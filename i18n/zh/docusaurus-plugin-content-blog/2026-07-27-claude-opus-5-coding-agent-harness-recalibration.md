---
title: "Claude Opus 5 发布后，Coding Agent 需要重新校准"
slug: claude-opus-5-coding-agent-harness-recalibration
description: "Claude Opus 5 在复杂 Agent 任务中表现强劲，但实际价值仍取决于 Harness、effort、工具、范围控制和验证环境是否同步校准。"
authors: [isaac]
tags: [perspective, future-of-coding]
keywords:
  - Claude Opus 5
  - Claude Opus 5 评测
  - Coding Agent Harness
  - Claude Code Opus 5
  - Agent Benchmark
  - AI 编程 Agent
image: /img/blog/claude-opus-5-harness/cover.jpg
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline="Claude Opus 5 发布后，Coding Agent 需要重新校准"
  description="Claude Opus 5 在复杂 Agent 任务中表现强劲，但实际价值仍取决于 Harness、effort、工具、范围控制和验证环境是否同步校准。"
  datePublished="2026-07-27"
  dateModified="2026-07-27"
  authorName="Isaac Zhao"
/>

# Claude Opus 5 发布后，Coding Agent 需要重新校准

用 Coding Agent 久了，我越来越不信单纯的模型排名。

不是说排名没有用，而是它能告诉我的事情有限。我同时跑 Claude Code 和 Codex 做真实项目，时间长了有个明显感受：同一个模型，在不同 Harness 下交出来的结果差距很大。上下文怎么进、工具开了哪些、验证跑在哪一层——这些东西会直接改变最终输出的质量，跟模型本身一样重要，有时候比模型本身更重要。

所以每次新模型发布，我第一反应不是刷榜单，而是想搞清楚：这个新数字，是在什么 Agent、什么 Harness、什么 effort 下测出来的？

Opus 5 发布在七月二十四日。这一次，公开材料提供的信息足够多，刚好可以把这个问题问得更清楚。

<!--truncate-->

---

## 评测里面的每一行数字

Frontier-Bench 七月二十六日的公共榜上，Opus 5 加 mini-SWE-agent、max effort，resolution rate 是 43.5%（±1.7%），排第一。Artificial Analysis 的 Intelligence Index 在 max effort 下得分 61，观察时同样排第一。Vals AI 把 Opus 5 列在 74.82%，排第二，同时报告它在 27 个已评榜单里拿了 14 个第一。

三个独立评测组织，方向一致：Opus 5 在复杂 Agent 任务里处于第一梯队。这是我目前能从公开材料里得出的最稳定的结论。

但每一行数字的背后都带着条件。Frontier-Bench 用的是 mini-SWE-agent，Anthropic 内部运行配了 GKE backend、每项任务跑五次取平均，安全分类器拒绝时还有 Opus 4.8 fallback。Artificial Analysis 的 GDPval-AA v2 用的是 Stirrup Agent Loop、Shell 和 Web。Vals 的主要运行是 max effort，Terminal-Bench 2.1 那一块用的是 high effort，同样配了 Opus 4.8 server-side fallback。Vals 自己也标注了：如果把 fallback 辅助的结果标记为失败，总分从 74.82% 变成 74.47%。

Benchmark 里的每一行，都是模型与 Agent、工具、effort 和验证环境共同形成的结果。跨行比较不能把 Agent 和 Harness 的差异剥掉，然后说某个模型"更强"。

![Benchmark 结果由模型、Agent、工具、effort、fallback 与验证环境共同形成](/img/blog/claude-opus-5-harness/benchmark-conditions-zh.png)

Artificial Analysis 的 GDPval-AA v2 提供了一个 effort 内部对比：同样是 Opus 5，max effort Elo 是 1861，medium effort 是 1632，而 Opus 4.8 的 max 是 1593。这个差距说明 effort 对特定任务分布有明显影响。但这个数字不支持"medium 普遍最优"，也不支持"max 永远最优"。哪种 effort 值得付，取决于任务。

---

## Anthropic 说的那几件事

发布材料里，Anthropic 对 Opus 5 的定位很清楚：困难编码、多文件功能、大型重构、端到端任务，提升更明显；简单的单轮修改与之前模型的差异较小。

这个区分对我来说是有用信息。它说明 Opus 5 的价值不是均匀分布的，重投入、复杂任务更能拿到回报。

更有意思的是迁移建议那一段。Anthropic 说 Opus 5 会主动验证和自我修正，然后提醒：如果你的 Prompt 里还留着"最终验证""双重检查"或"子代理复核"这类要求，可能会造成过度验证和额外 token 消耗。旧 Harness 里那些原本为了弥补较弱模型而加进去的独立验证脚手架，现在也应该重新评估。

我把这段话想了一下，理解是这样的：过去的旧脚手架是一种补偿性设计——你知道模型可能漏掉某个验证步骤，所以在外面再包一层。现在如果模型本身已经开始主动做这件事，外面那层脚手架不是变成双重保障，而是可能变成重复触发和 token 浪费。这是一个需要重新校准的具体工程点，不是普遍的正面消息。

![旧验证脚手架与重新校准后的 Coding Agent Harness](/img/blog/claude-opus-5-harness/harness-recalibration-zh.png)

Anthropic 还提了两条：对窄任务要明确范围，避免模型自行扩大；子代理更适合真正独立且规模较大的工作，小任务需要限制委派数量和成本。

这些建议我没有独立验证过，它们是 Anthropic 的迁移指导。但方向上说的是同一件事：模型能力提高之后，Harness 要同步调整，不是照搬过来用。

---

## 早期使用反馈里的摩擦

Claire Vo 做过一个七模型、六任务的盲式评测，结果对 Opus 5 的能力评价较高。但她同时记录了几个使用摩擦：输出 verbose、模型会主动扩张任务范围、在 merge conflict 场景遇到问题、还出现过指令冲突。

Zvi Mowshowitz 认为公开 Benchmark 很强，但保留担忧：无效自我验证、过度工程、过度自信、自我修正循环跑起来停不下来。

Hacker News 讨论里的反馈是混合的。积极的一面和过度工程、token 浪费、虚构引用、视觉验证不足这些问题同时存在。

这些不是发生率的估计，也不能说 Opus 5 比 4.8 退步，只是说明早期使用呈现混合状态。高分榜单和日常顺手之间有一段距离，这不是新问题，每次大模型发布都有这段距离。

---

## 我做的一次受限回放

七月十六日，我有个 CTA 修复已经部署并完成了生产验证。Opus 5 在七月二十四日发布。七月二十六日，我把部署前已经有的那批证据恢复成一个结果隐藏的审查任务，交给 Opus 5 跑一次。

运行环境：Claude Code `2.1.220`，`claude-opus-5`，标准模式，Fast 关闭，medium effort。工具、Web、MCP 和子代理全部关闭。一轮调用。

API 跑了 58.666 秒，成本约 0.1 美元，输出 3570 tokens。Verdict 是 `approve_with_followup`，没有 blocking finding。最有价值的 follow-up：补一次端到端或真实环境 smoke test。这个建议和七月十六日实际完成的生产验证类型一致。

有两件事同时成立。

第一，模型对证据缺口比较敏感。Prompt 里已经给了 bug 描述、目标行为、runtime facts、diff 和已有测试，模型没有独立调查仓库，也没有浏览器——但它识别出输入证据里缺少真实环境验证，并把它标成最重要的跟进项。这是有价值的判断。

第二，3570 tokens 对一个窄任务来说偏长。模型没有额外工具，能做的事情有限，但输出量超出了实际需要。这和 Claire Vo 记录的输出冗长，以及社区里的早期反馈，方向一致。

这次回放是单案例，没有对照组。它说明的是这次特定配置下的表现，不是跟旧模型、其他工具或人工审查的比较。Opus 5 也没有参与、批准或改变七月十六日的实际上线——时间线很清楚。

---

## Harness 的问题没有随着模型一起解决

Opus 5 在困难 Agent 任务上的能力，公开评测给出的方向是一致的。这个方向可信。

但能力本身不等于"接入就能用"。主动验证的模型搭配遗留验证脚手架，不一定更安全，可能更贵。对窄任务没有限制范围，模型自行扩张，成本就跑出去了。effort 没有校准，要么欠拟合，要么过度调用。

这些都是 Harness 层面的工作，不会因为模型更好而自动消失。Anthropic 的迁移建议指向的就是这一层。

我目前的判断是：Opus 5 可以承担更困难的工作，这一点我认为是真的。但确定性测试、真实环境验证和本地 Evals 的责任没有转移——它们仍然负责闭环，这部分不能交给模型的主动验证来替代。

模型能力和 Harness 是两个变量。新模型发布只更新了其中一个。

---

## 参考来源

1. [Anthropic：Claude Opus 5 发布](https://www.anthropic.com/news/claude-opus-5)，2026-07-24
2. [Anthropic：模型总览（Models Overview）](https://platform.claude.com/docs/en/about-claude/models/overview)
3. [Anthropic：Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)
4. [Frontier-Bench 公共榜](https://www.frontierbench.ai/)
5. [Artificial Analysis：Claude Opus 5 模型页与 GDPval-AA v2](https://artificialanalysis.ai/models/claude-opus-5)
6. [Vals AI：Vals Index](https://www.vals.ai/)
7. [Claire Vo：Claude Opus 5 评测](https://www.lennysnewsletter.com/p/claude-opus-5-review-this-model-is)
8. [Zvi Mowshowitz：Claude Opus 5 系统卡分析](https://thezvi.substack.com/p/claude-opus-5-the-system-card)
9. [Hacker News：Claude Opus 5 发布讨论](https://news.ycombinator.com/item?id=49038433)

---

如果你想先理解模型之外的那一层，可以从[什么是 Coding Agent Harness](/zh/docs/tutorials/coding-agent-harness-explained/)开始。关于为什么模型升级后仍然需要本地证据，可以继续阅读[面向 Coding Agent 的评测驱动开发](/zh/blog/eval-driven-development-for-coding-agents/)。
