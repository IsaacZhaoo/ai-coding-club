---
title: "Coding Agent 也需要 Eval-Driven Development：一次测试通过还不够"
slug: eval-driven-development-for-coding-agents
description: "一次通过只是一条 trial 证据。把真实失败变成 case、grader、重复 trial 和可执行的质量门禁。"
authors: [isaac]
tags: [perspective, future-of-coding]
keywords:
  - Eval-Driven Development
  - Coding Agent Evals
  - Agent 评测框架
  - Coding Agent 质量门禁
  - 智能体评测
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline="Coding Agent 也需要 Eval-Driven Development：一次测试通过还不够"
  description="一次通过只是一条 trial 证据。把真实失败变成 case、grader、重复 trial 和可执行的质量门禁。"
  datePublished="2026-07-24"
  dateModified="2026-07-24"
  authorName="Isaac Zhao"
/>

# Coding Agent 也需要 Eval-Driven Development：一次测试通过还不够

上一篇 Observability 教程里保存了一次真实的 Codex CLI 0.145.0 运行。最终判断是正确的，turn 状态是 `completed`，5 次工具调用里有 2 次失败——Agent 自己绕过去了，结果还是对的。保存的事件流记录了这条路径里可见的工具调用、失败结果和恢复过程。

但它回答不了一个更重要的问题：**明天我换了 Agent 版本、换了模型、调整了 Prompt、改了 Skill loadout，甚至只是升级了 Harness——新行为究竟是更好、更差，还是只是不一样？**

一次成功运行不是回归测试。

<!--truncate-->

---

## 普通测试仍然重要，但它只覆盖它明确检查的东西

我不是要说单元测试已经过时。`assert output == expected` 的那类检查永远有价值：它们快、确定性强、CI 能直接跑。对于 Coding Agent 的确定性部分——代码生成的语法合法性、函数签名是否被保留、依赖文件是否存在——这类测试应该继续写，而且应该先写。

问题在于：Coding Agent 的行为不是一条确定性路径。同样的任务，下一次运行可能经过不同的工具调用顺序，可能消耗不同数量的 token，可能触发不同的 Skill，也可能在第 3 次 trial 才出现第 1 次没有出现的回归。

单元测试检查的是**结果是否符合规格**，它没有能力检查"这 5 次运行里有多少次通过"，也没有能力检查"Agent 这次改了它不该改的文件"。

---

## 从一次 trial 推不出可靠性

回到那次真实运行：2 次工具失败，Agent 自己绕过去了，turn 完成。我不会把这个写成"Agent 具备容错能力"——那是一次 trial 的观察，不是可靠性数据。

Anthropic 在 2026 年 1 月发布的 Agent Eval 指南里对这一点做了明确区分（我在下文会反复用这套术语，因为它对工程思考有用，不是因为它是统一标准）：

- **task / case**：一个具体的输入加上明确的成功标准。
- **trial**：对同一个 task 的一次尝试。Agent 行为会波动，一次 trial 只是一条路径证据。
- **grader**：检查 outcome 或行为某一个维度的判断器。可以是代码检查、正则匹配、模型打分，也可以是人工审核——每种都有边界。
- **suite**：多个 case 的集合，覆盖你关心的场景分布。
- **Eval Harness**：运行任务、保存 trials、调用 graders 并汇总结果的机器设施。

单次 trial 的证明力是有限的。即使 pass rate 同为 80%，它是 5 次里的 4 次，还是 100 次里的 80 次？这两个数字在做变更决策时的意义也不同。

---

## 四个让我停下来的 Coding Agent 场景

让我换一种方式讲清楚为什么一次通过不够。这四个场景都是真实 Coding Agent 使用里会碰到的：

### 场景一：测试通过，但它改了不该改的文件

Agent 被要求修复 `auth.py` 里的一个 bug。单元测试通过了。但它顺手修改了 `config.py` 里一个变量的默认值，而这个修改在测试覆盖范围之外。

普通测试发现不了这个问题，因为你没有对 `config.py` 写断言。你需要一个 grader 检查"本次运行涉及的文件改动范围是否在预期集合以内"。

### 场景二：结果正确，但工具消耗异常

Agent 完成了重构，函数签名正确，测试全绿。但这一次调用了 14 次工具，上一个版本只用了 6 次。

如果你不测量工具调用次数，你不会知道模型升级之后 Agent 的行为模式发生了漂移。成本和延迟是可以被 grader 检查的维度，不只是精度。

### 场景三：Skill 误触发

你给 Agent 配置了一个 Git commit Skill。某次任务里它在没有被要求的情况下触发了 commit。行为上是"完成了任务"，但它做了一件你没有要求的事。

这是一个需要行为级 grader 的场景：不只检查 outcome，还检查执行路径里有没有出现不该出现的工具调用。

### 场景四：第二次 trial 才出现的回归

第一次运行通过了。你提交变更，上了 CI，打包。第二天有人报告说相同的 task 有时会失败。你拉了 5 次运行的 trace，发现其中 1 次在某个边界输入上走了一条没有被覆盖的路径。

一次通过给了你信心，但信心和可靠性不是同一件事。

---

## Trace 是记录，Eval 增加判断合同

Observability 工具保存的是执行记录，例如工具调用顺序、已捕获的输入输出和失败点；只有采集到时间字段时才能分析延迟。这些数据可以成为 Eval 的原材料，但 Trace 本身不做判断。

Eval 增加的是一个**判断合同**：这次运行的哪些维度需要通过，通过的标准是什么，由谁来判断。

这个区分在实践中很重要。一次 trace 显示"Agent 调用了 write_file"——这是事实。Eval 的 grader 需要判断"这次 write_file 调用的目标路径是否合法"——这是判断。你必须把判断标准写下来，它才能被自动执行，才能在下一次变更时被重新运行。

OpenAI 的 Evaluation best practices 建议"尽早编写任务相关测试，从日志提取 case，自动评分、比较运行并持续扩充"——这个建议的核心逻辑和我说的是一样的：观察到的失败要变成 case，case 要配上可执行的 grader，然后反复运行。

---

## Eval-Driven Development 的循环

我理解的 EDD 不是某种新方法论，它是一个朴素的工程循环：

```
观察到失败
    ↓
把失败变成一个明确的 case（定义输入 + 定义成功标准）
    ↓
写一个可以执行的 grader（代码检查 / 模型判断 / 正则匹配）
    ↓
在候选变更上跑这个 case（多次 trial）
    ↓
设置 quality gate（通过率阈值 → 是否接受这次变更）
    ↓
新的失败出现 → 收入 suite → 循环重启
```

"一次通过才真正开始"这句话的意思是：当真实失败变成了明确 case、成功标准变成了可执行 grader、非确定性通过重复 trial 处理、而且回归能够阻止一次变更的时候，EDD 才算建立起来了。在这之前，你只是在积累一次次的 trial 证据。

---

## Outcome-First，不要强迫 Agent 重演历史路径

这里有一个容易踩的坑：把 Grader 写成"Agent 必须按照我上次成功时的顺序调用工具"。

那条成功路径是一次 trial 的证据，不是唯一合法的路径。Agent 可能用两步完成三步能完成的事，也可能用不同的工具顺序得到相同的结果。如果你把 grader 写成路径匹配，你实际上是在用历史的成功路径约束未来的所有可能性。

更健壮的做法是 **outcome-first**：定义任务完成的标准是什么，而不是完成的方式是什么。

- 目标文件是否被正确修改？
- 测试是否通过？
- 改动范围是否在预期以内？
- 关键工具调用是否在允许集合里？

这些是 outcome 层面的检查。只有当某个具体的行为本身就是问题时（比如 Skill 误触发），你才需要路径级的 grader。

---

## 简单区分四个容易混淆的概念

这四个概念在讨论里经常被混用，我做一个简洁的区分，不是为了咬文嚼字，而是因为混用之后工程决策容易跑偏：

| 概念 | 它做什么 | 它不做什么 |
|---|---|---|
| **Observability / Trace** | 记录一次执行中被采集到的路径和证据 | 不自动给出质量判断 |
| **Skill 测试** | 验证某个 Skill 在已知输入上的行为 | 不覆盖 Agent 在真实任务里的调度判断 |
| **AI Code Review** | 对代码变更做语义审查 | 不替代多 trial 下的可靠性评估 |
| **公开模型 Benchmark** | 在标准化任务集上比较模型能力 | 不反映你的任务分布、你的 Harness、你的 Skill loadout |

这四件事都有价值，也可能共享同一批证据，但承担的责任不同。Trace 可以提供真实 case 的来源；Skill 测试通过，只能说明被测试的触发与行为符合预期；公开 Benchmark 的数字可以帮助模型选型，但不能替代你在自己任务上的实测。

---

## 关于平台变化：方法不随产品消失

OpenAI 在 2026 年 6 月 3 日宣布弃用其 Evals platform，现有 evals 将于 2026 年 10 月 31 日变为只读，Dashboard 和 API 计划于 2026 年 11 月 30 日关闭。这是一次产品层面的变化，不代表 Eval 方法本身消失。

Eval 的核心——把真实失败变成可执行 case，反复运行，设置 gate——不依赖任何托管平台。一个 JSONL 文件加一个能退出非零码的脚本，就可以构成一个本地 gate。

---

## 我偏好的起点：本地小型 gate

我不打算在这里做托管 Eval 平台的教程，也不打算推荐某个框架排名。生产环境的 Agent 评测规模因项目而异，AWS 在 2026 年 7 月发布的 Strands + AgentCore 评测案例里提到了具体的阈值和成本数字，但那是他们的任务分布、他们的 Harness 配置产出的结果，不是通用基准。

我更愿意从最小可用的本地机制开始讲：

1. **JSONL case 文件**：当前教学夹具每行一个 case，包含 `case_id`、`task` 与保存检查合同的 `expect`。
2. **确定性 grader**：先从能写成代码检查的维度开始——文件改动范围、测试通过与否、工具调用白名单。
3. **多次 trial**：同一个 case 可以积累多条 trial。要做可靠性判断时，一次运行不够；当前教程只演示如何评估已经归一的记录。
4. **进程退出码**：当前 gate 在全部 trial 通过时退出 `0`，有评测失败时退出 `1`，输入无效时退出 `2`；以后有足够样本时再增加通过率阈值。

这是一个能在本地运行、不依赖外部服务、不需要花钱调用评分模型的最小 Eval 闭环。它不完美，但它是可以真正执行的。

---

## 结尾：交给实战教程

这篇文章到这里只是搭了框架：为什么一次通过不够，核心区分是什么，循环是什么形状，坑在哪里。

真正要把这些落地，你需要：

- 一个真实的 Coding Agent task 作为第一个 case
- 一个能检查 outcome 的 grader 脚本
- 一个保存并归一 trial 记录的 adapter 边界
- 一个带退出码的 gate 脚本，能接入 CI

这些内容会在下一篇**[《Coding Agent Evals 实战教程》](/zh/docs/tutorials/coding-agent-evals-guide/)**里逐步给出：从一条 JSONL case 开始，运行确定性 gate，把退出码挂进本地 CI，再展示一条真实 baseline 通过和一条明确标注的合成错误记录失败。

那里的所有代码都是能跑的，而不只是示意。

---

*当前产品事实参考来源：Anthropic Agent Eval 指南（2026-01-09）、OpenAI Evaluation best practices、OpenAI Evals platform 弃用公告（2026-06-03）、AWS 生产 Agent 评测案例（2026-07-23）。搜索趋势证据只说明查询意图存在，不代表搜索量或普及率。*
