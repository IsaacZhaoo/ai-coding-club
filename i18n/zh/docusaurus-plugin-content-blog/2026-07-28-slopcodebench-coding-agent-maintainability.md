---
title: "通过测试只是截面，下一个需求才是真正的压力"
slug: slopcodebench-coding-agent-maintainability
description: "SlopCodeBench 用连续需求观察 Coding Agent 留下的代码，解释为什么一次测试通过还不能证明下一次需求容易继续修改。"
authors: [isaac]
tags: [perspective, future-of-coding]
keywords:
  - SlopCodeBench
  - Coding Agent 可维护性
  - AI 生成代码质量
  - Coding Agent Benchmark
  - 代码退化
  - 连续需求测试
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline="通过测试只是截面，下一个需求才是真正的压力"
  description="SlopCodeBench 用连续需求观察 Coding Agent 留下的代码，解释为什么一次测试通过还不能证明下一次需求容易继续修改。"
  datePublished="2026-07-28"
  dateModified="2026-07-28"
  authorName="Isaac Zhao"
/>

# 通过测试只是截面，下一个需求才是真正的压力

看到 `4/17` 的那一刻，我的第一反应和大多数人一样：又一个模型跑分。

HumanLayer 选了三道题，共 17 个 checkpoint，拿 Opus 5 去跑，严格通过 4 个。这个数字很容易被放进"模型评测"的心理框架里，然后滑过去，像一条新闻标题。我也几乎这样做了。

后来我打开了 SlopCodeBench 的论文。

<!--truncate-->

---

## 不是跑一次，是每步继承上一步的 workspace

Gabriel Orlanski 和研究团队在论文里描述了一件我没有预期的事：每道题从空 workspace 开始，然后不断向 Agent 发出新需求。每到下一个 checkpoint，Agent 收到的不是一个干净的问题，而是它自己上一步留下的 workspace，加上一条新的需求。之前的对话上下文不会带过去。

也就是说，Agent 不停地在自己上一次的决策上继续盖楼。

论文的规模是 36 道题、196 个连续 checkpoint。HumanLayer 的小实验是其中的 3 道题、17 个 checkpoint：`circuit_eval` 8 个、`database_migration` 5 个、`dynamic_config_service_api` 4 个。三组模型使用相同的 Prompt 和 Claude Code Harness，每个 checkpoint 都是 fresh context。

这个设计让我停下来。不是因为 Opus 5 通过了 4 个，而是因为我开始想：前面通过的 checkpoint，会在后面的任务里以回归测试的形式重新出现。早期的架构选择，不管好不好，都会成为下一个 checkpoint 的前提。

---

## 终端绿了，但那不是终点

做过真实仓库的开发者都有这种感受：功能上线，测试通过，看起来像是结束了。但下一个需求进来，才会暴露上一次留下的结构。那些当时为了快速通过测试而压缩的逻辑，那些没有认真拆分的函数，那些"这里先 hardcode 一下"的选择，会在新需求里以更高的摩擦成本浮出来。

SlopCodeBench 试图把这件事量化。题目只规定 CLI 或 API 对外可观察的行为，不管内部架构怎么组织。这给了 Agent 足够的自由度，也留出了足够的空间让结构问题慢慢积累。

论文对 15 个 Coding Agent（来自 6 家提供方）的轨迹做了分析，得出两个量化信号：

**structural erosion**：复杂度向高复杂度函数集中的趋势。**verbosity**：由指定 AST 规则命中的代码行和结构重复组成的指标。

77% 的轨迹出现 erosion 上升，75.5% 出现 verbosity 上升。论文用 473 个 Python 仓库作为比较基准，报告 Agent checkpoint 在 verbosity 上为基准的 2.3 倍、在 structural erosion 上为基准的 2.0 倍。

这两个数字需要原样保留它们的方法边界，不能读成"AI 写的代码比人差两倍"。它们是论文在自己定义的指标下、在自己的样本范围内观察到的信号，不是可维护性的完整定义，更不是最终判决。但它们指向了一件真实的事：Agent 的代码在连续迭代后，在这些维度上会朝某个方向漂移。

论文明确说明，在它给定的设置中，没有一个被测 Agent 从头到尾通过任何一道题的全部 checkpoint。

---

## 排行榜能告诉你什么，不能告诉你什么

我对排行榜有一种职业性的警惕。不是因为数字不真实，而是因为分数是截面，使用是过程。

HumanLayer 的 Opus 5 通过 4/17、Opus 4.8 和 Sonnet 5 各通过 1/17，是一个有边界的小样本，用于当前讨论是合适的，但不是"哪个模型最能维护"的普遍答案。SlopCodeBench 官方网站有一个持续更新的 live leaderboard，那是不同时间范围、更多模型的结果，和论文评测的 15 个 Agent 不是同一组数据，不能混在一起读。

官方仓库把 SlopCodeBench 称为开放、社区驱动的 evaluation primitive，而不是已经定型的最终 benchmark。这个定位本身很诚实，也值得记住。

---

## 那份代码，下一次需求还要继承

真正让我在意的问题，不是 Opus 5 的分数。

我现在用 Coding Agent 处理的工作，不会在一个任务后结束。下一个需求会进来，Agent 会看到上一次的代码，然后在上面继续。如果我不检查它上一次留下了什么，我接受的不只是一次功能，而是一份结构遗产。

这份遗产可能很好用，也可能在第三个 checkpoint 开始把维护成本悄悄推后。绿灯不会告诉我是哪种。

SlopCodeBench 的价值，在我看来，不是给出哪个 Agent 最好的答案，而是把"继续改"这件事变成了可以观察的对象。它不是唯一的观察方式，它的指标也不是可维护性的全部。但它把那道我原本需要自己去问的问题，嵌进了 benchmark 的结构里：

**通过这次需求之后，下一次需求会继承什么？**

我没有答案，只知道这个问题值得在每次接受 Agent 代码之前，认真停一下。

---

**参考来源**

- Gabriel Orlanski 等，*SlopCodeBench: Benchmarking How Coding Agents Degrade Over Long-Horizon Iterative Tasks*，arXiv v2，2026-05-07：[https://arxiv.org/abs/2603.24755](https://arxiv.org/abs/2603.24755)
- SlopCodeBench 官网：[https://www.scbench.ai/](https://www.scbench.ai/)
- 官方 runner：[https://github.com/SprocketLab/slop-code-bench](https://github.com/SprocketLab/slop-code-bench)
- HumanLayer，*Benchmarking Opus 5 on SlopCodeBench*：[https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/benchmarking-opus-5-on-slop-code-bench.md](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/benchmarking-opus-5-on-slop-code-bench.md)


---

## 延伸阅读

- [Coding Agent Benchmark 实操：怎样在自己的仓库比较不同 Agent](/zh/docs/tutorials/coding-agent-benchmark-guide/)
- [Coding Agent 也需要 Eval-Driven Development：一次测试通过还不够](/zh/blog/eval-driven-development-for-coding-agents/)
- [Coding Agent Evals 教程：把 Trace 变成数据集和质量门禁](/zh/docs/tutorials/coding-agent-evals-guide/)
