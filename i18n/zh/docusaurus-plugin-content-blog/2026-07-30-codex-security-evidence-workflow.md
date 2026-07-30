---
title: "Codex Security Plugin 0.1.14：scan history、稳定 identity 与 review-before-tracking"
slug: codex-security-evidence-workflow
description: "Codex Security Plugin 0.1.14 增加 scan history 与 scoped SECURITY.md policy。本文讨论为什么 finding 消失仍不能证明修复。"
authors: [isaac]
tags: [tools]
keywords:
  - Codex Security
  - Codex Security Plugin 0.1.14
  - AI 安全代码审查
  - SECURITY.md 安全策略
  - 安全扫描历史
  - 漏洞验证
  - 安全扫描 coverage
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline="Codex Security Plugin 0.1.14：scan history、稳定 identity 与 review-before-tracking"
  description="Codex Security Plugin 0.1.14 增加 scan history 与 scoped SECURITY.md policy。本文讨论为什么 finding 消失仍不能证明修复。"
  datePublished="2026-07-30"
  dateModified="2026-07-30"
  authorName="Isaac Zhao"
/>

# Codex Security Plugin 0.1.14：scan history、稳定 identity 与 review-before-tracking

一条 FAQ 里有句话，我停了一下。

不是那种会让人截图转发的句子。措辞很克制，意思大概是：后一次扫描没有再报出原来的 finding，不能单独证明问题已经修好。必须检查覆盖范围是否真的涵盖了原目标和受影响路径，重要的 finding 还要回到当前代码上直接复查。

我大概读了两遍。不是因为难懂，而是因为这句话说的，其实是 AI 安全审查这件事里最容易被跳过的部分。

<!--truncate-->

---

## 消失的 finding 告诉我们什么

绿色状态很容易交付。一次扫描没有出现上次的警告，视觉上看是"问题解决了"。

但这个判断要成立，需要确认不少前提：这次扫描真的覆盖了原来那条路径吗？代码改动有没有改变可达性，让原来的问题换了位置？还是说这次只是没有报出来，coverage 停在了 `partial` 甚至 `unknown`？

Codex Security 官方 FAQ 明确说，同一份配置重复运行 AI-assisted scan，结果可能变化。matching 机制能识别两次结果是否指向同一个 root cause，但没有办法让扫描本身变成确定性过程。这是 AI-assisted 审查的结构性特点，不是某个版本的 bug。

所以"不见了"这件事，实际上只有三种可能：真的修好了，扫描这次没有覆盖到，或者模型这次没有输出这条。要区分这三种，必须看 coverage 状态，必须回到那条路径上做直接复查。

这不是苛求，这是理解自己看到的结果的最低条件。

---

## 一个仓库没有写出来的安全假设

让我觉得更值得聊的，是 `SECURITY.md` 这件事。

很多仓库有这个文件，大多数是告诉外部研究者怎么提交漏洞报告。Codex Security 把它用来放另一类内容：trust boundary 在哪里，哪些 invariant 是安全前提，哪些 finding 被接受为 accepted risk，severity 如何判断，什么路径是明确排除的。

这个设计背后有一个很实际的问题：同一个 pattern，在某些仓库是漏洞，在另一个仓库可能是经过评估的权衡。Agent 在没有上下文的情况下，没办法区分这两种。如果仓库自己的安全假设没有被写出来，扫描工具只能用自己的通用判断来填这个空白。

更接近目标路径的策略文件会被优先使用，这个设计方向是对的。但这也意味着，如果仓库本来就没有明确这些边界，工具能给的就只是通用意见，不是针对这个仓库的判断。

写 `SECURITY.md` 不是为了满足工具的输入格式。它更像是逼自己把团队心里默认的安全假设真正落到文字上。这件事本身就有价值，不管用什么工具扫描。

---

## 证据积累，不是一次性结论

Codex Security 最近更新（plugin 0.1.14，发布于 2026-07-28）里有几个方向值得注意，不是功能罗列的意义，而是它们合在一起指向哪里：保存扫描结果、支持 rerun 和 compare、finding 和 repository 有了稳定的 identity 标识、可以基于安全策略跟踪 finding 的前期复核。

这些能力合在一起，是在做一件事：让安全审查从"运行一次，看报告，关掉"，变成有历史可以回溯的东西。

我做代码审查有一个习惯：同一个问题，如果在两次 review 之间消失了，我不认为它自动解决了。我会看 git log，看这个部分有没有人动过，或者问一句"这块是怎么处理的"。不是不相信同事，是因为我需要知道它是因为什么不在了。

这个习惯放到 Agent 安全审查里，道理是一样的。工具最终能给的是一份可以被人复查的证据：这次看了哪里，发现了什么，为什么这样判断，哪些已经在代码上验证过。如果这份证据是完整的，人来复查才有意义；如果它不完整，一个绿色状态反而是在降低警惕。

---

## 入口不同，能得到的也不同

有一点需要说清楚，因为文档本身也容易让人混淆。

Codex Security Plugin、独立的 `codex-security` CLI 和 SDK、以及 Cloud 工作流，同属一个产品名，但不是同一个发布入口，权限和版本也不相同。

本地 Plugin 是目前最容易入手的路径，在 Codex 里对本地仓库运行只读扫描，提供可见的 finding 和 remediation guidance；独立 CLI 和 TypeScript SDK 仍在 limited beta，只向获批的客户和合作伙伴开放；Cloud 工作流处于 research preview，通过已连接的 GitHub 仓库运行扫描，会结合仓库的 threat model 分析，在隔离环境里验证高信号 finding，再把结果和建议修复交给人审阅。

最新的 hosted catalog 版本是 0.1.14，公开 Plugin marketplace 上是 0.1.11，这个版本差是真实存在的。我在这里写出来，不是为了对比，而是说：你现在能拿到的，和文档描述的不一定完全对齐，这是 beta 阶段正常的状态，需要自己核实当前能用到什么。

Cloud 给出的 patch 是供人审阅的建议，不会自动改动生产仓库。这一点官方也明确写了。

---

## Agent 安全审查能信到哪里

官方对 Codex Security 的定位说得很清楚：是对 SAST 的补充，不替代人工安全审查、代码级验证、可利用性检查或人的威胁评估。

这个边界不是谦虚，是 AI-assisted 审查的实际范围。它能做的是：帮助在代码库里找到值得关注的 pattern，提供可以被人验证的证据，在有 threat model 上下文的情况下过滤出高信号的 finding，并且把这个过程保存下来让它可以追溯。

它不能做的是：给出"这个仓库现在安全"的确定性结论，替代对 finding 的代码级判断，或者在没有人复查的情况下自行决定什么是已经修好的。

我读到"把某个 finding 标记为 false positive，会把理由作为以后扫描的上下文，但不会永久屏蔽某个 rule、路径或漏洞类型"这句话时，觉得这个设计是对的。它在保留记忆的同时，没有让过去的判断取代下次对当前代码的直接检查。这是一种对自己上一次结论的适当不信任。

---

那个消失的 finding，如果重新出现了，我们大概会说"好，还是有问题"。但如果它没有再出现，我们知道的是：这次扫描运行了，coverage 是这个状态，当前代码没有再产生这个输出。这不是坏事。只是它和"已经修好"之间，还隔着一步需要人去走的复查。

Agent 安全审查最重要的交付，不是一次绿色结果。是一份人可以坐下来、拿出原来的 finding，对照当前代码，一行一行说清楚为什么不在了的记录。

---

**参考来源**

- OpenAI，*Codex Security*：[https://learn.chatgpt.com/docs/security](https://learn.chatgpt.com/docs/security)
- OpenAI，*Codex Security plugin changelog*：[https://learn.chatgpt.com/docs/security/plugin/changelog](https://learn.chatgpt.com/docs/security/plugin/changelog)
- OpenAI，*Codex Security plugin quickstart*：[https://learn.chatgpt.com/docs/security/plugin](https://learn.chatgpt.com/docs/security/plugin)
- OpenAI，*Codex Security CLI FAQ*：[https://learn.chatgpt.com/docs/security/cli/faq](https://learn.chatgpt.com/docs/security/cli/faq)
- OpenAI，*Codex Security cloud FAQ*：[https://learn.chatgpt.com/docs/security/faq](https://learn.chatgpt.com/docs/security/faq)
---

## 延伸阅读

- [AI Code Review 工作流：合并之前，Agent 到底该检查什么？](/zh/docs/tutorials/ai-code-review-workflow/)
- [Coding Agent 的沙箱到底保护了什么？又有哪些东西仍然能越界？](/zh/docs/tutorials/coding-agent-sandbox-security/)
- [连接 MCP Server 之前，我会检查这 12 件事](/zh/docs/tutorials/mcp-server-security-checklist/)
