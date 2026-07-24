---
title: "Skills 越多，Coding Agent 反而越笨吗？"
slug: too-many-agent-skills
description: "Skills 越多不等于能力越强。本文解释 Agent Skills 目录为什么会出现误触、漏触、描述冲突和上下文成本，以及为什么应该先审计再扩容。"
authors: [isaac]
tags: [perspective, future-of-coding]
keywords:
  - Agent Skills 测试
  - Skills 越多越笨
  - Coding Agent Skills
  - Skill 误触
  - Skills 上下文成本
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline="Skills 越多，Coding Agent 反而越笨吗？"
  description="Skills 越多不等于能力越强。本文解释 Agent Skills 目录为什么会出现误触、漏触、描述冲突和上下文成本，以及为什么应该先审计再扩容。"
  datePublished="2026-07-24"
  dateModified="2026-07-24"
  authorName="Isaac Zhao"
/>

# Skills 越多，Coding Agent 反而越笨吗？

7 月 23 日的热榜有点意思。

7 月 23 日的一次 NewsNow／掘金热榜抓取里，同时出现了三种内容：怎么挑选值得装的 Skills、怎么写出好的 Skill、以及"为什么装得越多，Agent 越笨"。同一时间窗口，Hacker News 上也出现了检查 Skills 负载、用使用证据治理 Skill 修改、统计哪些能力长期没有触发过的项目。

这个并列本身就说明了问题正在发生变化。

大家的提问，已经从"还能装什么"，悄悄转向了"哪些真的会触发、哪些会误触、哪些互相抢任务、哪些只是在占上下文"。这是一个方向性的转变，值得认真想一想。

<!--truncate-->

---

## Skills 目录，其实是一个路由界面

在展开"多了会不会更笨"之前，先要想清楚一件事：Agent 在真正执行一个 Skill 之前，需要先决定用哪个。

根据 [Agent Skills 规范](https://agentskills.io/specification)，每个 Skill 是一个包含 `SKILL.md` 的目录，`name` 和 `description` 是必需的元数据。规范里有一个叫做 **progressive disclosure** 的机制：Agent 会先暴露目录层的元数据，只有 Skill 被激活之后，才加载完整的 `SKILL.md`，其他资源也按需加载。

这个设计是合理的。如果每次请求都把所有 Skill 的完整指令一口气塞进上下文，成本会非常难看。progressive disclosure 让大多数 Skill 在"待机"状态只占极少量的空间。

官方规范描述的是：Agent 启动时加载所有可用 Skill 的 `name` 和 `description`，用它们决定该激活谁——或者不激活谁。具体客户端是否在每轮请求重新加载，由各自实现决定。

这是一个路由决策。它依赖的不是 Skill 的实际内容，而是那两行元数据写得准不准。

想象一下，你有一个拥挤的控制台，上面有几十个按钮，每个按钮只有一个简短的标签。你需要在很短的时间内判断按哪个。如果有三个标签都写着"处理代码"，你会怎么选？Agent 面对的是类似的问题，而且没有人类的直觉兜底。

---

## "已经安装"和"可靠能力"之间的距离

我对"Skills 越多越强"这个直觉一直有点不适。

不是说安装更多 Skills 会让底层模型变笨——那是另一回事。问题在于，一个 Skill 装进目录，不等于它已经成为能力。它至少要过三关：

1. **能被发现**：在路由阶段，description 要能让 Agent 识别这是对的 Skill。
2. **边界清晰**：近似的请求不会误触另一个 Skill，也不会在两个 Skill 之间产生歧义。
3. **结果可验证**：真实任务跑完之后，知道它做对了还是做偏了。

官方的 [description 优化指南](https://agentskills.io/skill-creation/optimizing-descriptions) 把这个问题说得很直接：描述过窄，正经请求触发不到；描述过宽，不该触发的时候反而触发。指南建议用真实的正例、近似负例、重复运行，以及训练和验证的拆分来打磨触发描述。

这意味着，漏触和误触是**可以测试和修正的工程问题**，不是 Skills 机制本身的原罪。但也正因为是工程问题，它需要工程投入来解决——而大多数人安装 Skill 的速度，远快于他们做这件事的速度。

一个没有被验证的 Skill，在目录里的真实状态，可能是以下几种之一：
- 从未被触发过（发现失败）
- 被触发了，但偶尔会去做它不该做的事（边界失效）
- 被触发了，但结果是对是错从来没人测过（评测缺失）

这三种情况都不能算成"能力增加"。而且每一个这样的 Skill 留在目录里，都可能在路由层增加一点歧义的成本。数量累积，歧义累积，路由代价累积。

---

## 生态正在从收集转向诊断

这也是为什么同一时间窗口的 Hacker News 讨论有点不一样。

[`drskill`](https://github.com/dbreunig/drskill) 的角度是检查 Skills 之间的重叠，识别 description 语义相近、可能会争抢同类请求的 Skill 对。[`Ingot`](https://github.com/SlanchaAI/ingot) 对优化器生成的 Skill 修改引入证据门禁：候选修改要携带留出任务证据，并由人决定是否替换当前指令。[`Agent Atlas`](https://github.com/Pycomet/agent-atlas) 则尝试用使用地图的形式，让人能看清哪些 Skill 实际被调用、哪些长期沉默。

这三个项目的方向，都不是教你再多装一个 Skill。它们都在问：你现在有什么，它们真的工作吗，你是怎么知道的？

需要说清楚的是：这些都是独立的早期项目，它们的探索方向有参考价值，但各自的结论不能等同于普遍规律。[Anthropic 公开的 Skills 仓库](https://github.com/anthropics/skills)也明确提醒，在关键任务前应该在自己的环境中充分测试，而不是拿来即用。

观察一下搜索端：Google 的搜索建议里已经出现 `agent skills testing` 查询族，Bing 也出现了 `agent skill testing`。搜索建议只能说明这类意图存在，不能代表规模，但它至少证明有人开始主动找工具来做这件事了。

生态的重心，正在从"收集"向"诊断和治理"移动。

---

## 明确说一件事

我的判断是：**Skill 数量不应该再被当成结果。**

真正值得看的，是：一个真实任务，能不能被送到正确的指令；这件事付出了多少可解释的成本。

如果你的目录里有 30 个 Skills，但其中 15 个从来没有被激活过，另外 8 个偶尔会在不该触发的地方出现，你其实不是拥有 30 个能力，你是在用 30 个 Skill 的路由负担换来 7 个不确定质量的能力。

一个较小但能够解释和测试的 Skills 目录，比一个充满未经验证条目的大目录更值得信任。这不是反 Skills，这是工程上的基本诚实。

[Skills 评测质量](https://agentskills.io/skill-creation/evaluating-skills)的官方文档里有一套评测思路，值得看一遍。不一定要照搬，但对着它想想自己的 Skills 目录，往往会发现一些没想到的盲区。

---

## 下一步

如果你想动手检查自己的 Skills 负载，[下一篇教程](/zh/docs/tutorials/agent-skills-testing-guide/)会用一个小夹具走完这个流程：检查规范合规性、目录大小、description 语义重叠、正例与近似负例，以及从真实激活记录里回头看哪些 Skill 在工作、哪些没有。

不需要大工程，一个小工具跑一遍，就能让你的目录从"感觉很强"变成"知道为什么能用"。

---

## 来源

- [Agent Skills Specification](https://agentskills.io/specification)
- [Optimizing Skill Descriptions](https://agentskills.io/skill-creation/optimizing-descriptions)
- [Evaluating Skill Output Quality](https://agentskills.io/skill-creation/evaluating-skills)
- [Anthropic Skills（官方仓库）](https://github.com/anthropics/skills)
- [drskill](https://github.com/dbreunig/drskill)
- [Ingot](https://github.com/SlanchaAI/ingot)
- [Agent Atlas](https://github.com/Pycomet/agent-atlas)
