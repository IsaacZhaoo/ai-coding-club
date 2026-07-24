---
title: "Coding Agent 工程：从 Prompt 到 Graph"
description: "沿着 Prompt、Context、Memory、Skills、Harness、Loop 和 Graph，理解 Coding Agent 工程的完整层级与验证边界。"
slug: /agent-engineering
keywords:
  - Coding Agent 工程
  - Agent Engineering 教程
  - Prompt 到 Graph
  - Coding Agent 架构
  - Agent Loop 和 Graph
---

# Coding Agent 工程：从 Prompt 到 Graph

一个有用的 Coding Agent 可以从 Prompt 开始，但进入真实仓库以后，问题很快就不只是“怎么提问”。系统还要选择上下文、保存正确的信息、提供工具、控制权限、根据反馈迭代，并协调那些已经无法装进一个局部 Loop 的工作。

这里是 AI Coding Club 的 Agent Engineering 教程地图。它按照责任边界组织，不按照某个产品组织，也不是必须逐关完成的课程。

如果你是从 Loop 和 Graph 的讨论来到这里，可以先看 [Loop Engineering vs Graph Engineering](/zh/blog/loop-engineering-vs-graph-engineering/)。那篇文章解释为什么 Agent 数量、局部反馈循环和 Graph 拓扑是三个不同的设计维度。

## 主线层级

| 层级 | 它负责回答的问题 | 从这里开始 |
|---|---|---|
| Prompt | 现在希望模型做什么？ | [提示工程 101](/zh/docs/prompt-engineering-101/) |
| Context | 当前任务应该获得哪些信息？ | [掌握上下文的艺术](/zh/docs/course/foundations/power-of-context/)——基础课程 |
| Memory | 什么应该长期保存，什么应该过期？ | [Coding Agent 的记忆应该保存什么？](/zh/docs/tutorials/coding-agent-memory/) |
| Instructions | 这个仓库始终应该遵守哪些规则？ | [AGENTS.md 完整指南](/zh/docs/tutorials/agents-md-guide/) |
| Skills 与工具 | 系统有哪些可复用流程、事件控制和外部连接？ | [Claude Code 的 Skills、Hooks 和 MCP](/zh/docs/tutorials/claude-code-skills-hooks-mcp/) |
| Harness | Context、工具、权限、记忆、执行和验证怎样围绕模型组装？ | [Coding Agent Harness 完整指南](/zh/docs/tutorials/coding-agent-harness-explained/) |
| Loop | 一个有边界的工作单元怎样通过反馈改进，并知道何时停止或升级？ | [Loop Engineering 实战](/zh/docs/tutorials/loop-engineering-guide/) |
| Graph | 工作单元怎样交换状态、串行或并行运行、否决行动并治理目标修改？ | [Graph Engineering 实战](/zh/docs/tutorials/graph-engineering-guide/) |

这些层级彼此相关，但不会互相取代。Context 变好以后仍然需要 Harness；Graph 也不会替代其中运行的 Loop；增加更多 Agent 更不会自动得到 Graph。

## 贯穿所有层级的保障

有些责任不是单独的一层，而是贯穿整个系统：

- [Coding Agent 的沙箱到底保护了什么？](/zh/docs/tutorials/coding-agent-sandbox-security/)解释执行边界保护了什么，以及 Host trust 仍可能从哪里越界。
- [AI Code Review 工作流](/zh/docs/tutorials/ai-code-review-workflow/)解释如何把需求、Diff、测试和残余风险变成有证据的合并判断。
- [Coding Agent Observability](/zh/docs/tutorials/coding-agent-observability-guide/)解释如何保存工具失败、重试、Token、Handoff 和明确的遥测缺口。
- [Coding Agent Evals](/zh/docs/tutorials/coding-agent-evals-guide/)把保存的 Trace 变成本地 case、确定性检查和可执行的 CI 门禁。

## 从哪里开始

- 刚开始使用 AI 编程：先看 Prompt 和 Context。
- 已经在使用终端 Agent：继续看 Memory、Instructions、Skills 和 Harness。
- 正在设计无人值守或多步骤系统：先看 [Loop Engineering](/zh/docs/tutorials/loop-engineering-guide/)，再进入 [Graph Engineering](/zh/docs/tutorials/graph-engineering-guide/)。

真正长期有效的问题，不是哪个新名词赢了，而是系统已经把哪些责任显式设计出来，还有哪些责任仍然藏在 Agent 的行为里。
