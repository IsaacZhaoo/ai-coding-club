---
title: "什么是 Coding Agent Observability？只有日志还不够"
slug: coding-agent-observability
description: "一次真实 Codex 运行在两次工具失败后仍然完成。Coding Agent Observability 需要关联 Trace、明确缺口和工具级证据。"
authors: [isaac]
tags: [perspective, future-of-coding]
keywords:
  - Coding Agent Observability
  - Agent 可观测性
  - Coding Agent Trace
  - OpenTelemetry GenAI
  - Codex CLI 可观测性
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline="什么是 Coding Agent Observability？只有日志还不够"
  description="一次真实 Codex 运行在两次工具失败后仍然完成。Coding Agent Observability 需要关联 Trace、明确缺口和工具级证据。"
  datePublished="2026-07-24"
  dateModified="2026-07-24"
  authorName="Isaac Zhao"
/>

# 什么是 Coding Agent Observability？只有日志还不够

刚刚我用 Codex CLI 做了一次只读诊断，最终状态显示 `completed`，答案正确，Agent 给出了我期望中的最小修复判断。如果这是我唯一看到的东西，我会满意地关掉终端，认为一切如预期运行。

但事件流里还有另一层故事。

<!--truncate-->

---

## 绿灯之下

整个 turn 共触发了 17 个事件，其中 5 次命令执行，只有 3 次成功，2 次失败。先是环境里没有 `python`，退出码 `127`；Codex 随即改用 `python3` 重试，聚焦测试返回了退出码 `1`，把预设的 `ZeroDivisionError` 暴露出来；之后 Agent 才读取最小源码文件，给出了最终判断。

从 Token 维度来看：input tokens 74,858，其中 cached input tokens 59,904，output tokens 749，reasoning output tokens 201。

如果把这次运行只压缩成 `turn completed` 和一组 Token 汇总，两次失败会消失，重试路径会消失，从失败到判断的中间状态也会消失。留下的只有最终状态、几个总数，以及它们掩盖掉的过程。

这不是说日志没有用。准确地说：**没有关联关系的日志不能保留完整的因果路径。**

---

## 为什么"已完成"不够

Coding Agent 不是一次函数调用。它在一个 turn 里会做多件事：调用工具、解读输出、做出中间判断、决定是否重试，有时还会把任务转交给另一个 Agent。每一步都依赖上一步的结果，而这个依赖链就是执行的因果结构。

扁平、未关联的日志可以记录每个事件，但很难直接回答：这个重试是否由那次失败触发？最终答案在哪一步才真正确定？如果结构化日志已经携带 trace context，它也可以参与关联；关键不在文件名叫日志还是 Trace，而在记录里有没有身份、父子关系和状态。

这些问题在调试和审计时同样重要。Agent 最终正确，不代表我们已经理解了执行路径。一次结果正确与一条可以解释、回放的执行路径，是两个不同层次的证据。

---

## Trace 与 Span 是什么

OpenTelemetry 把 trace 描述为一次请求经过系统的路径，把 span 描述为一个工作单元。多个 span 可以通过共享的 trace id 和 parent id 组成执行层级。

放到 Coding Agent 场景里，一次 turn 可以对应一条 trace，工具调用、模型调用、handoff 等操作可以按需要建成 span。具体哪些对象是 span、哪些只是 event 或 attribute，取决于实际 instrumentation，不能假设每条 Agent 消息都必须是 span。

这个层级结构让我们能还原一个问题的因果链条——不是只靠把时间戳排序，而是靠执行关系本身。未关联日志行是孤立事件；带父子关系的 span 则保留了工作单元之间的结构。

OpenAI Agents SDK 目前在 trace 里记录 generation、function tool、handoff、guardrail 和自定义事件。这只代表该 SDK 的实现，不代表所有 Agent 客户端的行为。

OpenTelemetry 也有 GenAI Agent 的语义约定，现已迁移至 `open-telemetry/semantic-conventions-genai`，状态明确是 **Development**。当前开发中约定覆盖 Agent 调用、workflow、plan、工具执行与 usage 等概念。这意味着字段名称和结构仍在演进，依赖它构建数据管道需要接受后续调整的可能。

---

## 工具失败可以存在于成功的 Turn 里

这是一个值得单独说清楚的判断。

在这次运行里，退出码 `127` 和退出码 `1` 都是真实的失败，它们出现在 Agent 给出正确答案之前。最终状态 `completed` 没有消除它们。一个只看最终状态的看板，会把这次 turn 归为成功，却无法展示 Agent 是怎样从失败走到结果的。

如果观察很多次运行，我会进一步想知道：失败集中在哪些工具？同一类 fallback 是否重复出现？第二次尝试也失败时，Agent 会停在哪里？总数和最终状态都不能单独回答这些问题。

Observability 的价值在这里不是"更大的日志文件"，而是把工具失败、重试路径和最终结果连接起来的因果结构。没有这个结构，我对 Agent 行为的理解只停留在"大体上能用"的程度。

---

## 覆盖范围的边界

我在这次运行里能看到的是：事件数、命令执行结果、退出码、Agent 消息数、最终状态、Token 拆分。

我看不到的是：每个事件的时间戳和 duration、美元成本、handoff 事件、Skill 加载事件。

这次 Codex CLI 0.145.0 的 JSONL 事件流没有输出这些字段。我不知道它们缺失的内部原因，也不会自行补上。我可以知道"有 5 次命令执行，2 次失败"，但不能从现有事件推算"第一次失败到第二次尝试之间经过了多少毫秒"。这是观测覆盖范围的真实边界。

这个边界本身就是一种信号。一个 Coding Agent 的 Observability 方案能告诉我什么、告诉不了我什么，决定了我在调试时的能见度下限。

---

## 趋势在哪里

2026 年 7 月的一次 Google 与 Bing 搜索建议扫描里，出现了 `agent observability`、`coding agent observability`、trace、platform、open source 等查询族。搜索建议只能说明这类查询意图存在，不能代表精确搜索量、增长率或行业普及程度。

Hacker News 和 GitHub 上有 observability、trace、replay 和 runtime evidence 相关项目，其中 `disler/pi-agent-observability` 公开描述了一个本地 Coding Agent 事件流和看板的方向。活跃度和 Star 数不是质量证明，但方向本身值得注意：有人在认真思考如何把 Agent 执行变成可以回放的故事，而不只是可以总结的结果。

随着 Coding Agent 进入更长的工程工作流，只看结果会留下越来越多无法回答的问题。执行路径、失败模式和每一步判断怎样关联，正在成为独立的工程对象。

---

## 最小 Trace 合同

我在自己的工作里越来越依赖一个简单的问题来判断一次 Agent 运行是否"可观测"：如果我明天需要解释"这次 turn 为什么做了这个决定"，现有的记录够不够用？

这不是一个新奇的要求，这是严肃工程实践里的基本预期。带有关联上下文的 Trace，能把发生过的事件组织成一条可检查的因果路径；它不会自动解释所有语义上的"为什么"，但比一组未关联的结果更接近问题本身。

这次运行的 17 个事件、5 次命令、2 次失败和最终成功状态，构成了一条比最终答案丰富得多、但仍不完整的执行记录。如果想在下一次运行中可靠地看到同样的层级，需要定义一个最小 Trace 合同：每次 Agent turn 至少导出哪些 span，父子关系如何对齐，工具失败和重试如何标注。

如何定义和实现这个合同，是 [Coding Agent Observability 教程](/zh/docs/tutorials/coding-agent-observability-guide/)的起点。

---

## 一手来源

- [OpenTelemetry Traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [OpenTelemetry GenAI Semantic Conventions](https://github.com/open-telemetry/semantic-conventions-genai)
- [OpenAI Agents SDK Tracing](https://openai.github.io/openai-agents-python/tracing/)
- [Pi Agent Observability](https://github.com/disler/pi-agent-observability)
- [Hacker News: agent observability](https://hn.algolia.com/?q=agent%20observability)
