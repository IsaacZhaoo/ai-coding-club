---
title: "Codex CLI 是什么？OpenAI 的终端编程 Agent 适合谁用？"
slug: what-is-codex-cli
description: Codex CLI 是 OpenAI 推出的开源终端 coding agent，能读写文件、执行命令、自主完成多步骤编程任务。这篇说清楚它是什么、和 Claude Code / Cursor / ChatGPT 有什么区别、适合谁用。
authors: [isaac]
tags: [tools, ai, productivity]
keywords: [Codex CLI 是什么, OpenAI Codex CLI, Codex CLI 和 Claude Code 区别, Codex CLI 和 ChatGPT 区别]
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline="Codex CLI 是什么？OpenAI 的终端编程 Agent 适合谁用？"
  description="Codex CLI 是 OpenAI 推出的开源终端 coding agent，能读写文件、执行命令、自主完成多步骤编程任务。这篇说清楚它是什么、和 Claude Code / Cursor / ChatGPT 有什么区别、适合谁用。"
  datePublished="2026-05-10"
  dateModified="2026-05-10"
  authorName="Isaac Zhao"
/>

OpenAI 推出了 Codex CLI。

如果你听说过它但还不确定它是什么——这篇讲清楚。

<!--truncate-->

---

## Codex CLI 是什么

**Codex CLI 是 OpenAI 推出的开源终端 coding agent。** 它运行在你的本地机器上，通过自然语言接受指令，能自主完成一系列编程任务：读文件、改代码、运行测试、执行 shell 命令。

背后是 OpenAI 的 GPT-5 / Codex 模型体系，针对编程任务做了专项优化。

"终端 Agent"这个词值得停一下：不是代码补全，不是聊天问答，而是能自己推进任务的 Agent。你说"帮我找出这个 bug 并修复"，它去读代码、定位问题、改文件、跑测试，然后告诉你结果。

---

## 核心能力是什么

从日常使用看，Codex CLI 的核心能力主要有四类：

- **读写文件**：能访问你本地项目里的文件，也能修改它们
- **运行代码**：直接执行代码
- **浏览网页**：需要查文档或资料时能自己去搜
- **执行 shell 命令**：跑测试、构建、任意终端操作

任务执行上，Codex CLI 通过两类配置控制执行边界：

- **approval policy**：决定什么时候需要你确认——`on-request`（需要时确认）或 `never`（全自动不等待）
- **sandbox policy**：决定命令能访问和修改哪些范围——`read-only`、`workspace-write`（推荐）或 `danger-full-access`

日常本地开发推荐 `workspace-write` 搭配 `on-request`，保留效率的同时避免无边界执行。

---

## Codex CLI 和 ChatGPT 有什么区别

这是最常见的问题。

**ChatGPT** 是对话工具。你问它问题，它回答。就算你把代码贴给它，它也只是建议你改什么——真正改代码的还是你。

**Codex CLI** 是 Agent 工具。你下指令，它去做。读你的文件、改代码、跑命令——这些它自己执行，不需要你复制粘贴。

区别不在于谁更智能，而在于谁在"执行"。

Codex CLI 用的是 OpenAI 的 GPT-5 / Codex 模型体系，专门针对编程任务优化，但模型能力只是一部分——Agent 的价值更多在于它能直接操作你的项目，而不只是告诉你该怎么做。

---

## Codex CLI 和 Cursor 有什么区别

**Cursor** 是编辑器——一个在 VS Code 基础上改造的 AI 强化版编辑器。AI 嵌在编辑器里，你写代码，它帮你补全、解释、局部修改。你是主导，AI 是辅助。

**Codex CLI** 在终端运行，不依附于编辑器。你不需要打开 IDE，直接在终端里下指令。它的主场是多步骤任务自动执行，而不是你写代码时实时帮你补全。

两者不是替代关系，是分工：Cursor 在编辑器里配合你打字，Codex CLI 在终端里自己推进任务。

---

## Codex CLI 和 Claude Code 有什么区别

两个都是终端 Agent，但背后生态不同。

**Claude Code** 是 Anthropic 的产品，背后是 Claude 系列模型，适合已经在 Anthropic / Claude 生态里的开发者。

**Codex CLI** 是 OpenAI 的产品，背后是 GPT-5 / Codex 模型体系，是 OpenAI Codex 产品线的本地 CLI 入口。

如果你已经在用 ChatGPT 订阅，Codex CLI 是同一个账号体系。如果你已经在用 Claude，Claude Code 是同一个生态。

两个工具更详细的对比，可以看这篇：[Claude Code vs Codex CLI](/zh/blog/claude-code-vs-codex-cli/)

---

## 怎么接入 Codex CLI

两种方式：

**1. ChatGPT 账号登录**

有 ChatGPT 订阅（Plus、Pro、Business 等）的用户可以直接用账号登录，用量走订阅套餐。这是大多数个人用户最简单的接入方式。

**2. API Key**

通过 API Key 接入，走 OpenAI API 计费，按 token 实际用量付费。适合需要程序化调用、自动化流程或共享环境的场景。但 API Key 模式不包含 GitHub code review、Slack 等 cloud-based features，并且新模型访问可能有延迟。

安装方式：

```bash
npm i -g @openai/codex
# 或
brew install --cask codex
```

---

## 适合谁用

**适合 Codex CLI 的情况：**

- 已经在用 ChatGPT 订阅，想在终端里用同一个账号做编程任务
- 需要一个能自主推进多步骤任务的终端工具，不想手动复制粘贴
- 在 OpenAI 生态里工作，后续想用 Codex 的 Web、IDE、GitHub 集成等入口
- 想要开源工具，能看到源码、可以定制

**不太适合的情况：**

- 你的主要需求是编辑器内补全——那用 Cursor 或 Copilot 更直接
- 你已经在用 Claude Code 且满意——两个终端 Agent 叠用，边际收益不高
- 你需要离线工作——Codex CLI 需要联网调用 API

---

## 常见问题

### Codex CLI 需要付费吗？

有 ChatGPT 订阅（Plus、Pro 等）的用户可以直接用，用量走订阅。也可以用 API Key 按实际 token 消耗计费。具体额度和价格以 OpenAI 官方文档为准，会随产品迭代更新。

### Codex CLI 和 Claude Code 哪个更适合新手？

这个问题的关键不是谁更"新手友好"，而是你在哪个生态里——已经在用 ChatGPT 就用 Codex CLI，已经在用 Claude 就用 Claude Code。

两个工具的基本使用方式类似：在终端里用自然语言下指令。学习曲线不是主要差别。

### Codex CLI 能完全替代人工写代码吗？

不能，也不该这样期待。Codex CLI 在自动化重复任务、处理清晰定义的编程任务上效率很高，但复杂业务逻辑的判断、架构决策、代码质量审查仍然需要你参与。把它当效率工具，不要当完整替代品。

---

## 相关阅读

- [Claude Code vs Codex CLI：两个终端 Agent 怎么选](/zh/blog/claude-code-vs-codex-cli/)
- [Claude Code、Codex CLI、Cursor 怎么搭配？一个实用 AI 编程工作流](/zh/blog/claude-code-codex-cli-cursor-workflow/)
- [三款 AI 编程工具总对比](/zh/blog/ai-coding-tools-compared-2026/)
- [Claude Code 使用指南](/zh/docs/tutorials/claude-code-guide/)
- [AI 编程路线图](/zh/docs/ai-coding-roadmap/)
- [AI 编程工具列表](/zh/docs/tools/)
