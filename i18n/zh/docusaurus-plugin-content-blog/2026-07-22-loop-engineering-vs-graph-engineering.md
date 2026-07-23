---
title: "Loop Engineering vs Graph Engineering：Loop 负责收敛，Graph 负责治理"
slug: loop-engineering-vs-graph-engineering
description: "Loop Engineering 负责局部收敛，Graph Engineering 把依赖、交接、否决、升级路径和目标修改权显式化。"
authors: [isaac]
tags: [perspective, future-of-coding, comparison]
keywords:
  - Loop Engineering
  - Graph Engineering
  - Loop Engineering vs Graph Engineering
  - Coding Agent 架构
  - 多 Agent 治理
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline="Loop Engineering vs Graph Engineering：Loop 负责收敛，Graph 负责治理"
  description="Loop Engineering 负责局部收敛，Graph Engineering 把依赖、交接、否决、升级路径和目标修改权显式化。"
  datePublished="2026-07-22"
  dateModified="2026-07-22"
  authorName="Isaac Zhao"
/>

# Loop Engineering vs Graph Engineering：Loop 负责收敛，Graph 负责治理

在我开始关注“Loop Engineering”和“Graph Engineering”这两个词之前，工作中已经出现了让我不舒服的信号：一个被拆分成多个子任务的总体目标，在运行一段时间后开始出现奇怪的漂移。不同的工作单元各自在收敛，但它们收敛的方向并不一致；某个单元完成了局部目标，却悄悄改变了另一个单元赖以决策的前提。我知道问题出在哪里，但当时没有好的词来说它。

后来在 X 和一些开发者文章里看到这两个词被拿来对比，感觉很像是找到了语言。不是术语帮我想清楚了，而是语言把已经想清楚的东西给了一个锚点。

<!--truncate-->

## 先把三个概念并排放一下

**Agent** 是行动者。它能够根据当前状态选择并执行行动。普通脚本、检索函数、格式转换工具不在这个定义里——它们可以是系统里的节点，但不是 Agent。Agent 的核心是“根据状态做选择”。

**Loop** 描述局部工作如何通过反馈收敛。一个可以被工程化的 Loop，包含这几样东西：局部目标、当前状态、可执行的行动、某种形式的反馈或评估器、执行预算和停止条件、允许做什么的权限范围、以及何时应该升级的条件。Addy Osmani 在他的 Loop Engineering 文章里把这个方向描述得很直接：把原来由人来重复操作的提示、检查和迭代，变成被设计的系统——同时正视它带来的无人值守错误和 token 成本。我认为这个方向是对的。Loop 是一个有边界的工作单元，目的是让局部目标通过反馈逐步收敛。

**Graph** 描述工作单元之间如何连接，以及目标、反馈和决策权如何在它们之间被组织。Graph 里可以有 Loop，可以有函数节点，可以有人工审批节点，可以有 evaluator，可以有 Agent——这些都可以是节点。边则携带着状态传递、依赖关系、handoff 条件、否决权和升级路径。

## 两个容易犯的混淆

**第一个：多个 Loop 不等于 Graph。**

几个 Loop 各自运行，互不知道对方的存在，这不是 Graph，这只是并发执行的孤立单元。让它们成为 Graph 的，是它们之间的关系——谁依赖谁的输出，谁有权修改谁的目标，谁的失败会触发另一个的升级，谁的结果需要被另一个否决或放行。这些关系在不少早期系统里是隐含的，藏在代码逻辑里，没有被显式设计。Graph Engineering 的动作是把这些关系显式化、类型化，并纳入治理。

**第二个：多个 Agent 也不等于 Graph。**

这一点更容易被忽视。拓扑结构（Graph 的形状和语义）和执行者数量（有几个 Agent 在跑）是两个独立的维度。同一个 Graph，可以由一个 Agent 串行执行所有节点，也可以由多个 Agent 并行执行不同节点。Graph 的意义不在于有多少个 Agent，而在于节点之间的关系是否被明确定义和治理。

反过来也成立：多个 Agent 在运行，但它们之间没有显式的依赖、状态传递和权限边界，只是在各自执行，那就只是多个执行者的集合，还不是有治理意义的 Graph。

顺带一提，线性的步骤顺序在数学上也可以是 Graph。我批评的不是线性结构，而是那种只有步骤顺序、没有明确状态传递和治理语义的薄弱工作流——节点之间的关系完全隐含在执行逻辑里，没有被显式地设计和管理。

## 全文的重心：谁拥有目标修改权

这是我认为最关键的一点，也是从工作经验里提炼出来的。

Loop 可以调整手段——在允许的范围内换一种行动策略，尝试不同的方法。Loop 也可以提出目标修改的请求——“我发现当前目标在这个约束下无法达成，建议修改”。但最终目标修改权不属于 Loop，属于相应的治理者。

这种治理机制可以是另一个 Agent，可以是人，也可以是被明确设计的治理规则。治理可以分散在多个领域，不同领域可以有自己的局部治理者。跨领域的冲突，再升级给更高层的所有者。

这就是 Graph 的职责所在。Graph 不只是拓扑，它是承载目标、反馈和决策权如何被组织的结构。当一个 Loop 提出升级，谁有资格响应，响应之后什么改变了，这些关系需要被设计，而不是靠运行时的随机碰撞来解决。

否决的形式也值得区分：硬否决是强制停止，软异议是标记问题但允许继续，建议是低优先级的意见。这三种形式携带不同的语义权重，在 Graph 里应该有不同的类型。不在这篇文章里展开实现，但区分它们的存在是必要的。

## Graph 没有替代 Loop

读过掘金上那篇“AI 又又造词，Graph 就又要替代 Loop 了”，我理解那种警惕感。行业确实有用新概念覆盖旧概念的惯性，好像每隔一段时间就要宣布上一代方法过时。

但这里不是替代关系。Loop 处理局部收敛，这个职责没有消失；Graph 处理工作单元之间的关系和治理，这是新增的层，不是覆盖。

变化是：以前工作系统里的依赖关系、状态传递、handoff 条件和权限边界，常常是隐含的，藏在执行逻辑里。随着 Agent 承担的工作变得更复杂、更长、更需要跨越不同的工作单元，这些隐含关系开始暴露问题。Graph Engineering 的方向，是把它们显式设计出来。

Josh Simmons 和 iii 的文章里都提到了类似的判断：不是 Loop 不够用，而是当多个 Loop 开始互相依赖时，需要一个层来承载这些关系。arXiv 上那篇从 Agent Loop 到结构化 Graph 的位置论文也在做类似的论证——尽管它是设计提案，不是生产效果的证明。

## 一张简洁的对照表

| 概念 | 关注点 | 典型问题 |
|---|---|---|
| **Agent** | 根据状态选择并执行行动 | 当前状态是什么？应该做什么？ |
| **Loop** | 局部目标通过反馈收敛 | 怎么知道做完了？预算用完怎么办？ |
| **Graph** | 工作单元之间的关系与治理 | 谁依赖谁？谁有权否决？升级给谁？ |
| **Governor（治理者）** | 持有目标修改权 | 局部目标和总体目标冲突时谁说了算？ |

## 一个简洁的工程地图

如果要给这些概念找一个位置关系，我会这样排列：

```text
Prompt → Context → Memory / Skills → Harness → Loop → Graph
```

Prompt 进来，经过 Context 和 Memory/Skills 的处理，进入 Harness（运行系统），在 Loop 里通过反馈收敛，多个 Loop 之间的关系由 Graph 来治理。

每一层都有自己的设计问题，不是只要设计好 Prompt 或者只要选对框架就能解决的。Coding Agent 工程系列会从这张地图的每个层展开，这篇文章是那个系列的引子，目的是把三个概念放到它们该在的位置上。

## 进入系列

如果你正在构建一个需要跨越多个工作单元的 Agent 系统，或者系统已经开始出现隐含依赖和冲突，可以先进入 [Loop Engineering 实战](/zh/docs/tutorials/loop-engineering-guide/)，再连续阅读 [Graph Engineering 实战](/zh/docs/tutorials/graph-engineering-guide/)。[Coding Agent 工程：从 Prompt 到 Graph](/zh/docs/agent-engineering/) 提供整个系列地图。

## 参考来源

- Addy Osmani, [Loop Engineering](https://addyosmani.com/blog/loop-engineering/) (2026-06-07)
- iii, [Loops, Graphs, and the Layer That Matters](https://iii.dev/blog/loops-graphs-and-the-layer-that-matters/) (2026)
- Josh C. Simmons, [We Are Entering the Graph Engineering Phase](https://www.drjoshcsimmons.com/writing/we-are-entering-the-graph-engineering-phase) (2026)
- arXiv 2604.11378, [From Agent Loops to Structured Graphs](https://arxiv.org/abs/2604.11378) (2026)（位置论文与设计提案）
- 掘金, [AI 又又造词，Graph 就又要替代 Loop 了？](https://juejin.cn/post/7664063148857442347) (2026)
