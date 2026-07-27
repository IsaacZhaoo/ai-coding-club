---
title: "Coding Agent 并行指南：任务契约、证据回传与合并权限"
description: "用 worktree、任务契约、运行时隔离、证据回传和单一合并权限，让多个 Coding Agent 并行工作不把省下的时间耗在集成阶段。"
keywords:
  - Coding Agent 并行
  - Git worktree
  - 并行 Coding Agent
  - 多 Agent 编程工作流
  - Agent 合并冲突
sidebar_position: 23
tags: [tutorial, coding-assistant, agent-engineering, git]
---

# Coding Agent 并行指南：任务契约、证据回传与合并权限

*作者：有光*

并行跑两个 Coding Agent 很容易。真正难的是让这两个 Agent 最后还能合到一起。

我踩过很多次一模一样的坑。两个窗口同时滚动输出，看起来进展惊人，等两边都停下来，才发现各自修改了同一组类型定义，或者一边改了 migration、另一边的数据层还在用旧 schema，或者更简单：两边都在端口 3000 上起了 dev server，互相把对方踹掉了。节省的时间一分都没少——它只是搬到了后面的冲突处理和审查阶段。

这件事反复发生几次之后，我不再把它归结为偶发倒霉，开始把并行工作本身当作一个隔离问题来处理。

---

## worktree 能解决的范围其实很窄

Git 官方支持在同一个仓库上附加多个 working tree，每个 linked worktree 有各自独立的 `HEAD` 和 index，同时共享仓库的其他 Git 数据。命令形式稳定、官方维护：

```bash
git worktree add -b <branch> <path> <commit-ish>
```

Anthropic 在 Claude Code 的公开文档里也建议为并行会话使用 worktree，以避免并发编辑直接碰撞。这个建议是真实有效的——在文件系统层面，两个 Agent 操作的是不同目录，不会在同一个文件上同时写入，也不会踩对方未暂存的修改。

但 worktree 管理的只是 Git checkout 状态。它不会自动帮你分配独立端口、独立数据库、独立缓存、独立临时目录、独立测试账号或凭据。文件路径分开，不等于行为独立。两个任务仍然可能共享同一套 API、同一份 schema、同一组 migration 顺序、同一个 lockfile，或者彼此依赖某个隐含假设——而这些完全在 worktree 的视野之外。

所以我把 worktree 当成必要条件，而不是充分条件。它处理的是最浅的那一层冲突，后面还有更多东西要想清楚。

---

## 启动之前先判断任务是否真的独立

这是我花时间最长、也觉得最值的一步：在创建任何 worktree 之前，把两个任务并排放，问自己几个问题。

**写入路径有没有交叉？** 两个 Agent 各自要改哪些文件？如果答案里有重叠，要么拆得更细，要么接受串行。类型定义文件、全局配置、共享工具函数，这几类特别容易出问题。

**有没有共享契约？** Schema 定义、接口类型、API 响应格式、数据库表结构——这些如果有一方要改，另一方的代码很可能同步失效。依赖同一份契约的任务不应该并行；应该先把契约改好、确认、再启动后续任务。

**生成产物有没有依赖关系？** 代码生成、类型生成、lockfile 更新——如果两个 Agent 都会触发同一个生成步骤，最后合并时的产物可能发生冲突或不一致。

**运行时状态有没有共享？** 开发数据库、消息队列、缓存服务、浏览器 profile——这些需要在任务级别手动拆分，不是给 worktree 目录加个前缀就能解决的。

只要其中一项答案让我不确定，我会先把不确定的部分固定下来再并行，或者干脆把任务改成串行。

---

## 一个任务对应一个 branch 和一个 worktree

确认任务确实独立之后，操作本身并不复杂。

```bash
# 从同一个 base commit 分别创建两个 worktree
git worktree add -b <branch-a> <path-a> <base-commit>
git worktree add -b <branch-b> <path-b> <base-commit>

# 查看当前所有 worktree
git worktree list
```

用同一个 `<base-commit>` 是刻意的。两个 Agent 从同一个已知状态出发，后面合并时至少有一个确定的对比基准。如果 base 不固定，你在 review diff 的时候会不知道哪些变化是预期内的、哪些是意外带进来的。

在启动 Agent 之前，我会写一份简短的任务契约，内容不多，但必须说清楚：

- 可以写哪些路径
- 可以只读哪些路径（不能改）
- 绝对不能碰哪些路径
- 验收条件是什么
- 返回时需要提供什么证据

最后一项值得单独展开。

---

## 要求 Agent 带着证据回来

两个 Agent 同时运行时，我没办法一直盯着两个窗口。等它们停下来，我需要能快速判断："这个任务做完了，而且做对了。" 如果只有一句 "done"，我仍然不知道发生了什么。

我现在要求每个 Agent 完成任务后返回以下内容：

- 工作的 branch 名称
- 最终 commit hash
- 从哪个 base commit 出发
- 改动了哪些文件（简要列表）
- 用哪条命令验证了结果，以及命令输出是什么
- 做了哪些假设
- 有哪些风险没有解决

这是我个人推荐的返回契约，不是 Git 官方要求，也不是 Claude Code 的要求。但没有这份证据，合并阶段就是在盲操作。

---

## 运行时资源需要手动隔离

这部分是我觉得最容易被忽视的。

每个任务需要各自独立的：

- **开发端口**（别让两个 dev server 抢同一个端口）
- **数据库或 schema**（用独立的测试库，或者至少独立的 schema prefix）
- **缓存目录**（尤其是会根据路径生成 key 的工具）
- **临时目录**（生成文件、fixture、截图）
- **测试账号和凭据**（如果任务会创建数据或修改账号状态）

这些东西不在 worktree 的管辖范围内，需要在任务契约里明确写出来，然后在环境变量、配置文件或启动脚本里实际落地。一个常见的做法是在任务路径里维护一份 `.env.local`，专属于这个 worktree 的环境配置。

忽略这一步的代价是：两个 Agent 在文件层面互不干扰，但共享数据库的状态以某种难以追踪的方式彼此污染，等你发现的时候已经很难区分哪个任务的代码是对的、哪个只是因为数据库状态刚好对而通过了测试。

---

## 合并权限只给一个人

两个 worktree 都做完之后，决定合并顺序、处理冲突、做联合验证——这三件事我不交给任何一个 Agent 自己决定。

只有一个 controller 来主导集成阶段，通常是我自己。如果任务之间真的没有依赖，顺序理论上无所谓；但实际操作中，先合进去的那个可能会影响后面的 diff，哪怕只是改了格式。更重要的是，两个分支各自通过了自己的验证，不等于合并后的结果也通过——这是我踩过的最贵的一个假设。

合并完成之后，我会跑一次联合验证：统一运行两个任务涉及的所有测试，在合并后的代码上。如果有 E2E，也在这里跑。不是因为我不信任 Agent，而是因为合并本身可能引入新的行为，而这些行为不在任何一个分支的测试视野里。

---

## 这几类工作应该停止并行

worktree 用熟了之后，有一个反直觉的收获：我开始更清楚什么东西不适合并行，而不是更冲动地多开几个 Agent。

**有依赖顺序的 migration。** 两个 Agent 各自生成一个 migration，合并后的执行顺序可能语义上是错的，或者互相之间有前置条件没满足。Migration 要串行，要审查，不要并行。

**共享 schema 的设计决策。** 如果一个任务的结论会改变另一个任务的前提，先把结论做出来，确认，再开后续的 Agent。

**根因尚未确认的调试。** 两个 Agent 同时追同一个 bug，路径不同，最后各自给出了一个"修复"，两个修复都有可能掩盖根因而非真正解决问题。这不是在解决问题，这是在争着先提交一个看起来对的答案。

这三类场景我现在都保持串行，宁可慢一些。

---

## 收尾：删除 worktree 之前

任务完成、证据回传、代码已经合并之后，可以清理 worktree：

```bash
git worktree remove <path>
git worktree prune
```

但在执行 `remove` 之前，确认有用的 commit 和证据已经保存好。linked worktree 删除之后，对应目录消失，如果 branch 也一起删了，且对应 commit 没有被其他 branch、tag 或合并历史保留，那个阶段的工作记录才可能需要借助 reflog，不方便。我的习惯是先确认 branch 已经 merge 或者已经 push 到远端，再执行清理。

---

最后说一句我觉得最核心的东西：worktree 给两个 Agent 各自一块干净的工作区，这是真实有效的隔离，但只是隔离的一层。把任务依赖、运行时状态、证据回传和合并权限也同样认真对待，多个 Agent 并行才真的能缩短墙上时间。不然的话，并发只是把等待从"我在跑任务"搬到了"我在处理冲突"——而后者往往更耗时，也更难解释。

---

## 参考资料

- [Git worktree 官方文档](https://git-scm.com/docs/git-worktree) — Git project

- [Claude Code Common Workflows: Run parallel sessions with worktrees](https://code.claude.com/docs/en/common-workflows#run-parallel-sessions-with-worktrees) — Anthropic

---

## 相关阅读

- [Coding Agent 工程：从 Prompt 到 Graph](/zh/docs/agent-engineering/)
- [Graph Engineering 指南](/zh/docs/tutorials/graph-engineering-guide/)
- [AI Code Review 工作流](/zh/docs/tutorials/ai-code-review-workflow/)
- [Coding Agent 沙箱安全](/zh/docs/tutorials/coding-agent-sandbox-security/)
