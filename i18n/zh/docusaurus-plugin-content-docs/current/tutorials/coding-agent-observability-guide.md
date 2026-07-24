---
title: "Coding Agent Observability 教程：追踪工具、重试、Token、Handoff 和失败"
description: "构建本地 Coding Agent Trace 审计，保留工具失败、重试、Token、Handoff 和明确的遥测缺口。"
keywords:
  - Coding Agent Observability 教程
  - Coding Agent Trace
  - Agent 可观测性工具
  - OpenTelemetry GenAI
  - Codex CLI JSONL
sidebar_position: 19
tags: [tutorial, coding-assistant, agent-engineering, observability]
---

# Coding Agent Observability 教程：追踪工具、重试、Token、Handoff 和失败

> **夹具下载**：<a href="/examples/coding-agent-trace-audit.zip">/examples/coding-agent-trace-audit.zip</a>

---

上一篇 [Coding Agent Observability 文章](/zh/blog/coding-agent-observability/)展示了一个最终状态为 `completed` 的 Codex turn。但如果你仔细看那个 turn 的内部路径，会发现它先后经历了两次工具失败，才到达正确的诊断。

这正是我想谈的问题：**一个 "成功" 的 turn 完全可以包含失败**。如果你的观测系统只记录最终状态，那些中间失败就永远消失了——你就失去了能够回放、审计和改进 Agent 的最有价值的那条路径。

## 一条有用的 Trace 必须保留什么

先回答最核心的问题，再解释实现。

一条有用的 Coding Agent Trace 必须保留：

- **身份**：每个 span 的 `trace_id`、`span_id`、`parent_span_id`，让层级关系可以重建；
- **状态**：每个 span 自己的 `status`（`ok` 或 `error`），不能用 root 成功覆盖 child 失败；
- **真实观测到的 usage**：实际发生的 token 数，不估算；
- **明确的覆盖缺口**：duration、美元成本、handoff、Skill load 如果没有观测到，就保持 `false` 或 `null`，不猜一个数字；
- **工具的退出码和失败原因**：让重试路径可以被还原。

> **一句话中心**：有用的 Coding Agent Trace 必须保留身份、父子关系、状态、真实观测到的 usage，以及明确的覆盖缺口，让工具、重试、handoff 和失败可以被重建，而不是用猜测填补缺失遥测。

---

## 先跑起来，再解释

夹具包含四个核心文件：`trace_audit.py`、`test_trace_audit.py`、`portable-trace.example.jsonl`，以及一次真实的 Codex 事件流 `codex-diagnosis-20260723.jsonl`。

### 第一步：运行测试套件

```bash
python3 -m unittest -v test_trace_audit.py
```

**已验证结果：11 个测试全部通过。** 当前测试覆盖确定性汇总、CLI JSON 输出和部分校验行为；validator 本身会检查必需字段、span id 唯一性、parent 存在、parent-child trace id 一致、status 合法、结束时间顺序和循环 parent 链，但测试套件没有逐一触发每条拒绝分支。

先让测试通过，你才能信任后续的审计输出。

### 第二步：审计合成 Portable Trace

```bash
python3 trace_audit.py portable \
  --trace portable-trace.example.jsonl
```

**已验证的确定性输出：**

| 字段 | 值 |
|---|---|
| trace 数 | 1 |
| span 数 | 9 |
| root span | 1 |
| kind: agent | 1 |
| kind: evaluation | 1 |
| kind: handoff | 1 |
| kind: model | 2 |
| kind: skill | 1 |
| kind: tool | 3 |
| error span 数 | 2 |
| error span id | `tool-python`、`tool-python3` |
| retry span 数 | 1 |
| handoff span 数 | 1 |
| 有时间字段的 span | 9 |
| root duration | 8,000 ms |
| 合成 input tokens | 1,000 |
| 合成 output tokens | 150 |
| 合成成本 | USD 0.016 |

> ⚠️ **重要**：这个文件里的每条记录都有 `synthetic: true`。这些数字是教学仪器，不是真实 Agent 运行，不是服务商账单，不代表任何性能基准。

### 第三步：汇总真实 Codex 事件流

```bash
python3 trace_audit.py codex \
  --events codex-diagnosis-20260723.jsonl
```

**已验证的真实运行事实：**

| 字段 | 值 |
|---|---|
| 事件数 | 17 |
| 工具调用 | 5 |
| 成功工具调用 | 3 |
| 失败工具调用 | 2 |
| 失败退出码 | `127`、`1` |
| Agent 消息 | 4 |
| handoff 事件 | 0 |
| 最终 turn 状态 | `completed` |
| input tokens | 74,858 |
| cached input tokens | 59,904 |
| cache-write input tokens | 0 |
| output tokens | 749 |
| reasoning output tokens | 201 |
| duration available | false |
| cost available | false |

这是 Codex CLI 0.145.0 的一次本地 `codex exec --json` 运行输出，只证明采集与解析链路，不代表任何其他版本或客户端的行为。

---

## Portable Trace 合同：span 的最小结构

Portable Trace 是本教程设计的本地教学 schema，**不是 OTLP，不是官方标准**。设计它的出发点是：用最少的字段，让执行路径可以被重建。

OpenTelemetry 将 trace 描述为一次请求经过系统的路径，将 span 描述为一个工作单元。span 可以包含 trace id、span id、parent id、开始／结束时间、attributes、events、links 与 status。通过 parent 连接的 spans 可以重建端到端操作层级。

基于这个思路，合同要求每个 portable span **必须**包含：

```jsonc
{
  "trace_id":      "t-diag-001",
  "span_id":       "tool-python",
  "parent_span_id":"model-first",
  "kind":          "tool",
  "name":          "run_python",
  "status":        "error",
  "attributes": {
    "tool.exit_code": 127,
    "tool.command":   "python test_calculator.py -k test_average_empty"
  }
}
```

**必需字段解释：**

- `trace_id`：同一次完整运行共享同一个 trace id。如果 parent 和 child 的 trace id 不同，审计立刻报错。
- `span_id`：在本次输入文件内唯一。重复的 span id 意味着你的数据管道出了问题。
- `parent_span_id`：根 span 的 parent 为 `null`；其余 span 必须指向一个已存在的 span id。本地合同用它还原层级。
- `kind`：合成示例使用 `agent`、`skill`、`model`、`tool`、`handoff`、`evaluation` 六种本地分类。这是教程分类，不是任何官方 taxonomy。
- `status`：只接受 `ok` 或 `error`，合同明确拒绝模糊值。

`started_at` 和 `ended_at` 是**可选字段**，因为并非每个来源都输出时间戳。合同会验证"如果两者都存在，结束时间不能早于开始时间"，但不强制要求它们出现。

---

## 合成 Trace 能教什么

合成 trace 有 9 个 span，覆盖一次完整的 Agent 运行从 agent 根 span 到 evaluation 的全链路。我们用它来教学，而不是用它来描述真实性能。

### Timing 与 Duration

root span 的 `started_at` 和 `ended_at` 之差是 8,000 ms。所有 9 个 span 都有时间字段，所以你可以看到每个 tool call 耗时多少、model span 占了多长时间窗口。在真实 Codex 事件流里，这个字段是 `false`——客户端没有输出 duration，所以保持不可用，而不是猜一个数字。

### Retry 路径

合成 trace 里有 1 个 retry span。`tool-python` 以 status `error` 结束，`tool-python3` 通过 `retry_of` 指向它，同样以 `error` 结束。这让你看到：**同一测试命令的两次尝试都失败了**，而 root span 的 status 可以依然是 `ok`。

这正是子 span 状态与根 span 状态必须分别保留的原因：如果你只看 root `ok`，你永远不知道 Agent 在路上踩了多少坑。

### Handoff

合成 trace 包含 1 个 `kind: handoff` span。这是 Agent 把控制权移交给另一个 Agent 或子流程的时刻。在真实 Codex 事件流里，parser 报告 handoff 事件数为 0，不会补写一个没有出现的事件。

### Token 与可选 Cost

合成 trace 记录了 input tokens 1,000、output tokens 150，以及一个合成成本 USD 0.016。**这三个数字都标注了 `synthetic: true`**，是教学用途。真实 Codex 运行提供了 input tokens 74,858、cached input tokens 59,904、output tokens 749、reasoning output tokens 201，但 cost available 是 `false`，因为这次本地事件流没有输出成本字段。保持 `false`，比猜一个数字更诚实。

### Evaluation Span

合成 trace 的最后一个 span 的 kind 是 `evaluation`，它记录一次针对诊断结果的检查，`verdict` 为 `pass`。这是从 Trace 通往 Eval-Driven Development 的接口——后面会讲。

---

## 真实运行：一个 completed turn 里的两次工具失败

这是整个教程里我认为最有价值的结果。

受控代码要求 `average([])` 抛出 `ValueError("at least one value")`，但实际实现会除以零。Agent 的路径是这样的：

1. **找到聚焦测试**：定位 `test_average_empty` 测试用例；
2. **读取测试**：读取测试文件内容；
3. **尝试 `python`**：以退出码 `127` 失败（命令不存在）；
4. **改用 `python3` 重试**：测试以退出码 `1` 失败，暴露 `ZeroDivisionError`；
5. **读取 `calculator.py`**：读取实现文件；
6. **返回正确诊断**：准确指出 bug 位置；
7. **turn 以 `completed` 结束**。

没有修改任何文件。整个 turn 的最终状态是 `completed`。

这条路径在 Codex CLI 的 JSONL 事件流里是这样呈现的：17 个事件，5 个工具调用，2 个失败，3 个成功，4 条 Agent 消息。如果你只看最终 turn 状态 `completed`，你看不到 `127` 和 `1` 这两个退出码，你看不到 Agent 自己做了 python → python3 的回退决策。

**这两个失败工具，才是最有信息量的数据点。**

---

## 两种数据的覆盖对比

下面这张表直接对比合成全字段 Portable Trace 与真实 Codex 事件流的字段覆盖范围。

| 字段 | 合成 Portable Trace | 真实 Codex 事件流 |
|---|---|---|
| trace_id | ✅ 有（合成） | ❌ 无 portable `trace_id`（但有 `thread_id`） |
| span_id / parent_span_id | ✅ 有（合成） | ❌ 无 |
| kind | ✅ 有（本地分类） | ❌ 无 portable `kind`（但有事件类型） |
| status per span | ✅ 有 | ⚠️ 有 command item status 和 turn status，但无 span 层级 |
| tool exit_code | ✅ 有 | ✅ 有（真实） |
| tool 成功 / 失败数 | ✅ 有 | ✅ 有（真实） |
| Agent 消息数 | ✅ 有 | ✅ 有（真实） |
| handoff | ✅ 有（合成） | ❌ 0（真实） |
| started_at / ended_at | ✅ 有（合成） | ❌ duration available: false |
| root duration | ✅ 8,000 ms（合成） | ❌ 不可用 |
| input tokens | ✅ 1,000（合成） | ✅ 74,858（真实） |
| cached input tokens | ❌ 无 | ✅ 59,904（真实） |
| output tokens | ✅ 150（合成） | ✅ 749（真实） |
| reasoning tokens | ❌ 无 | ✅ 201（真实） |
| 美元成本 | ✅ USD 0.016（合成） | ❌ cost available: false |
| Skill load | ✅ 有 skill span（合成） | ❌ 无 |
| evaluation span | ✅ 有（合成） | ❌ 无 |
| synthetic 标注 | ✅ 每条记录 | — |

这张表本身就是一个设计决策：**哪些字段你能真实观测到，哪些只能靠合成教学**。不要把合成列的数字用到真实列里。

---

## 覆盖缺口：保持不可用，不要猜

真实 Codex 事件流里，`duration available: false`，`cost available: false`。

这不是 bug，这是诚实的观测结果。此次 Codex CLI 0.145.0 本地 JSONL 事件流没有输出这两个字段。你的审计工具应该把它们标注为不可用，而不是从 token 数反推一个估算成本，也不是从墙钟时间推断一个 duration。

原因很简单：一旦你开始猜，你的 Trace 就从记录变成了假设。当你用这条 Trace 来调试一个月后的问题，你不会记得哪个数字是真实的，哪个是推断的。

> 我更信任一个诚实写着 `false` 的覆盖字段，而不是一个能看起来很完整的 Dashboard。

同样，handoff 事件数为 0 是真实观测，不代表这个 Agent 永远不会产生 handoff。Skill load 不在这份真实事件流里，不代表不存在 Skill 概念——只能说明这次保存的事件没有暴露它。

---

## 隐私提醒

Trace 里会包含你可能没有意识到的敏感内容：

- **prompt 和 output**：用户输入和模型输出可能出现在 span attributes 里；不同客户端也可能记录 reasoning 相关数据；
- **command 和 tool result**：工具执行的命令行、标准输出、标准错误；
- **secret**：如果命令里包含 API key 或密码，它可能出现在 `tool.command` 字段里。

OpenAI Agents SDK 的文档明确提醒：Trace payload 可能包含敏感数据。

本教程的夹具都是本地文件，不发送任何数据。如果你要把 Trace 发送到远程收集器，请先确认：哪些字段需要脱敏，谁有权限访问 Trace 存储，数据保留周期是多长。

---

## 小练习

用你自己的客户端或另一个 Codex 版本，采集一次受控的**只读**运行（不修改任何文件），然后对比以下问题：

1. 你的事件流里有没有 `exit_code` 字段？
2. 有没有时间戳？格式是 ISO 8601 还是 Unix 毫秒？
3. token 字段的键名叫什么？是 `input_tokens` 还是 `prompt_tokens` 还是其他？
4. 有没有 cached token 的区分？
5. 最终 turn 状态字段叫什么？

**只比较哪些字段存在，不做性能横评。**

这个练习的目的是让你知道你的采集链路实际输出了什么，而不是假设它输出了完整字段。

---

## 交给 Eval-Driven Development

Trace 的终点不是存档，而是回放和质量门禁。

合成 trace 里有一个 `kind: evaluation` span。这个设计的意图是：当 instrumentation 支持时，Agent 运行可以产生 evaluation span，记录外部评估器或既定检查对输出质量的判断。

当你积累了足够多的 Trace，你就拥有了一个可以回放的数据集：每一次工具失败、每一次重试、每一次 handoff，都成为可以写成测试用例的证据。你可以：

- 把这次 `ZeroDivisionError` 的诊断路径写成一个 eval 用例；
- 在下一个 Agent 版本跑过同样场景后，比较 evaluation span 的结果；
- 把通过率作为发布的质量门禁。

这就是 Eval-Driven Development for Agents 的起点：**Trace 不只是调试工具，它是可以被回放的证据，也是质量数据集的原材料。**

---

## 一手来源

| 来源 | 内容 |
|---|---|
| [OpenTelemetry 官方文档：Traces](https://opentelemetry.io/docs/concepts/signals/traces/) | Trace、span、parent id 定义 |
| [OpenTelemetry GenAI Agent 语义约定](https://opentelemetry.io/docs/specs/semconv/gen-ai/) | 当前状态 Development，包含 Agent 调用、workflow、工具执行、Token usage 概念 |
| [OpenAI Agents SDK Tracing 文档](https://openai.github.io/openai-agents-python/tracing/) | generation、tool、handoff、guardrail span；敏感数据提醒 |
| `codex exec --help`（Codex CLI 0.145.0） | `--json` 向标准输出写 JSONL 事件 |
| `python3 -m unittest -v test_trace_audit.py` | 本地已验证：11 个测试通过 |
| `python3 trace_audit.py portable --trace portable-trace.example.jsonl` | 本地已验证：9 span，2 error，1 retry |
| `python3 trace_audit.py codex --events codex-diagnosis-20260723.jsonl` | 本地已验证：17 事件，5 工具调用，2 失败 |

---

*如果你想把这个小框架扩展到可以回放的 eval 数据集，下一步就是 [Coding Agent 的 Eval-Driven Development](/zh/blog/eval-driven-development-for-coding-agents/)。*
