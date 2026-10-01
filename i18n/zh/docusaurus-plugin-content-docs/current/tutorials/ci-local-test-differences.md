---
title: "本地测试通过，CI 却失败：让 AI 对照两次运行的证据定位问题"
sidebar_label: "本地通过、CI 失败排查"
description: "对照本地与 CI 的测试日志、源码、依赖、时区和事件顺序，让 AI Agent 提出并验证具体修复。"
keywords: ["CI test failures", "AI debugging", "GitHub Actions", "flaky tests"]
sidebar_position: 43
tags: ["tutorial", "agent-engineering"]
---

# 本地测试通过，CI 却失败：让 AI 对照两次运行的证据定位问题

> “同一个测试在本地通过、在 CI 失败，或同一 CI 测试偶尔成功、偶尔失败。”  
> 这往往不是“代码有问题”，而是“运行条件没对齐”。  
> 本文教你用编程 Agent 做一件事：**把两次运行的证据摆到桌面上，让 AI 对照差异，提出可验证的修复**。

---

## 一、从失败 Step 提取“实验样本”

一切始于一个失败的 CI Job。不要只看“红勾变红叉”，要把它当成一次**实验记录**。

### 1. 锁定关键信息

在 GitHub Actions 日志中，优先记录：

- Workflow / Run / Job ID（用于后续复现）
- Commit SHA（确保对比的是同一份源码）
- 失败的 Step 名称与完整命令
- 失败测试的名称、断言错误原文
- 失败前后几行日志（尤其是安装、环境初始化、数据加载阶段）

> 提示：  
> - 点击日志 → 搜索测试名 / 错误关键词 → 复制行链接或下载日志。  
> - 私有仓库需要相应权限；部分客户端可通过 GitHub MCP 自动拉取日志，但能力取决于配置。

### 2. 确认“同一份源码 + 同一个测试”

最容易踩的坑：你以为对比的是分支 A，其实 PR 合并时引入了额外提交。

- 用 `git rev-parse HEAD` 确认当前 Commit SHA
- 用 `node --version`、`npm --version` 记录运行时版本
- 核对测试命令是否真的对应失败日志中的命令（例如：`npm test` vs `npx jest`）

> 原则：  
> **比较的前提是“同一份源码 + 同一个测试入口”**。  
> 如果 PR 合并后代码变了，那就不是“本地 vs CI”，而是“版本漂移”。

---

## 二、构建对照表：让 AI 看到差异

AI 不会读散乱的日志，它需要一张**结构化差异表**。  
下面这张表是通用模板，按你的项目填充即可。

| 维度 | 本地运行（通过） | CI 运行（失败） | 备注 |
|------|------------------|----------------|------|
| Commit SHA | `abc123` | `abc123` | 必须相同 |
| Node 版本 | `v20.11.0` | `v20.11.0` | `node --version` |
| npm 版本 | `9.6.7` | `9.6.7` | `npm --version` |
| 测试命令 | `npm test` | `npm test` | 项目自有命令为准 |
| 时区 (TZ) | `UTC` / `Europe/Paris` | `UTC` / `Europe/Paris` | 进程启动前生效 |
| 并行 Worker | `maxWorkers: 4` | `auto` / `CPU_COUNT` | Jest/Vitest 等配置 |
| lockfile 状态 | 存在且匹配 | 存在且匹配 | `npm ci` 依赖此文件 |
| 关键环境变量 | `NODE_ENV=test`, `TZ=...` | 同上（记录存在性） | 凭证由安全存储管理 |
| 数据/清理策略 | 无 / 固定种子 | 无 / 固定种子 | 随机数据会引入 flaky |
| 浏览器模式 | 无 / 无头 | 无 / 无头 | 若涉及 E2E 需记录 |

> 表格作用：  
> - 让 AI 一眼看到“可能不同的变量”。  
> - 后续验证修复时，逐项回查这张表。

---

## 三、提出假设与候选原因

基于对照表 + 失败日志，你可以先列出**有证据的候选原因**。  
AI 的任务是：从候选中选出最可能的，并给出“最小修复”。

### 常见高概率原因（按优先级）

1. 时区候选原因：记录两次运行的实际 TZ，因为不同表示可能影响日期快照；Z 结尾的时间戳是 UTC，但捕获时间不同也会造成差异。因此应比对同一固定时刻的日期格式化、快照生成及检查条件，再将“时区不一致”列为候选原因，避免默认所有 CI 均使用 UTC。

2. **依赖解析 / lockfile 不匹配**  
   - `npm ci` 要求 lockfile 与 `package.json` 严格一致；版本微调也会改变依赖树。  
   - 证据：安装阶段报错，或运行时出现“模块未找到/版本冲突”。

3. **异步未完成就断言**  
   - Jest/Vitest 需要 `await Promise` 或返回 Promise；后台任务已派发但未等待完成。  
   - 证据：日志显示“Background job completed”在断言之后，或出现竞态日志。

4. **共享状态 / 未清理的全局变量**  
   - pytest/Jest 并行运行时，上一个测试残留数据影响当前测试。  
   - 证据：同一测试在单线程通过、多 worker 失败；或失败日志显示“previous test”相关错误。

5. **环境初始化差异（before_install / before_script）**  
   - Travis 的 `before_install` 与 GitHub Actions 的 `steps/run/env` 行为不同。  
   - 证据：CI 特有步骤在本地缺失，如安装全局工具、设置 PATH、注入凭证等。

> 关键判断：  
> **不要凭感觉猜“可能是时区”**，要用日志中的时间戳、环境变量、依赖版本作为锚点。

---

### 历史案例

- 2017 date-fns#564：Okami 作者报告本地 Jest 通过但 Travis 日期快照失败；维护者建议生成/检查快照时统一 TZ，作者选择 Europe/Paris。固定修复 54c27c 将 TZ 加入普通测试、更新快照并统一 watch 三入口，移除 Travis-only before_install TZ，作者随后报告两端通过。
  - 来源：https://github.com/date-fns/date-fns/issues/564
  - 修复提交：https://github.com/Kilix/okami/commit/54c27c96045b243a33e44cf3eb4bef2a06779e6c

- 2023 DuckDB PR8665：Python 3.7 / pandas 1.3.5 的 CI 时区 timestamp roundtrip 失败；最终保留旧 pandas 兼容方案，>=2 期望 us，旧版输入及期望 dtype 为 ns。证据来自 CI 失败与合并的兼容修复。
  - 来源：https://github.com/duckdb/duckdb/pull/8665/files

## 四、指令 AI Agent 执行“最小修复”

现在把**实验样本 + 对照表 + 候选原因**交给 AI Agent，并给出明确任务边界：

### 推荐 Prompt 结构（可微调）

```text
背景：
- 本地 npm test 通过，GitHub Actions CI 中同一测试失败。
- 两次运行 Commit: abc123, Node v20.11.0, npm 9.6.7。
- 失败 Step 命令: npm test
- 失败测试名: __tests__/date.spec.ts
- 关键错误片段: "日期快照文本不一致"

对照表（已整理）：
[此处粘贴上节表格]

候选原因（按证据强弱排序）：
1. 时区不一致导致日期快照错位
2. Jest 异步未完成就断言
3. lockfile 与 package.json 版本微调导致依赖树差异

任务：
- 基于上述证据，提出一个“最小修复”（改动行数最少、风险最低）。
- 说明修复如何对齐两次运行的关键条件。
- 给出验证方法：用原 CI job + 回归条件检查。

约束：
- 不要重写测试逻辑，只调整运行环境或断言时机。
- 若涉及时区，确保生成快照和检查快照使用同一 TZ。
```

### AI 应输出的典型结构

1. **观察到的差异**（例如：“本地 TZ=Europe/Paris，CI 默认 UTC”）
2. **最可能原因**（例如：“日期快照生成与检查时区不一致”）
3. **最小修复方案**（例如：在 `package.json` 的 `scripts.test` 前加 `TZ=Europe/Paris`）

> 原则：  
> - 修复要“可回滚”、“可观测”。  
> - 若 AI 提出多个方案，优先选改动最小、依赖最少的。

---

## 五、用原 CI job 和回归条件验证

在修复提交推送后，最直接的方式是通过项目原有的触发器启动同一 workflow/job 配置的新运行（run）。这一步的关键在于：准确记录新 run 实际 checkout 的 commit，并确认其中包含本次修复。由于 pull_request 默认 checkout 常为 refs/pull/.../merge，其 mergeSHA 可能与分支 headSHA 不一致，因此应核对实际测试所用源码，而非简单要求二者相等。若重新运行旧 run，它仍基于原 SHA，无法用于验证未包含的新修复。当 workflow 已配置 workflow_dispatch 且具备相应权限时，也可在网页上选择修复所在 branch 手动触发新 run，但同样需要仔细核对实际 checkout 的源码和配置。

对照原失败 step 与断言，安装文件与 flags 需保持一致；npmci 要求 package-lock 或 npm-shrinkwrap 与 manifest 一致，不匹配应报错。快照生成与检查应在同一时区（TZ）进行，测试进程内实际有效的 TZ 才是依据：内部脚本若固定 TZ 会覆盖父 shell 的设置，因此父 shell 的 echoTZ 不能单独证明子进程条件。固定 TZ 并不固定当前时刻，若要稳定日期需同时固定时钟或共享一次捕获时刻。

异步等待应基于实际业务完成事件或有界状态轮询后再断言；仅派发任务的 Promise 已完成仍不够。并发与资源隔离需按项目 runner 版本核验。通过支持观察条件下的修复，失败继续依据日志缩小候选。

---

## 六、小结

- 本地通过、CI 失败的本质是**运行条件未对齐**。  
- 用 AI 的关键不是让它“猜”，而是给它**结构化的实验样本**：两次运行的源码、命令、环境、日志。  
- 一张清晰的对照表 + 有证据的候选原因，能让 AI 提出可验证的最小修复。  
- 最终验证必须回到原 CI job，并用回归条件逐项确认。

> 下一步建议：  
> 将本文流程固化为你团队的“CI 失败排查模板”，每次遇到 flaky 测试时，先填表、再交 Agent，而不是直接改代码。