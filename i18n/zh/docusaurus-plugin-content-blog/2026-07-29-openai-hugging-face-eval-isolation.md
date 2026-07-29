---
title: "OpenAI–Hugging Face 事件中，eval 隔离的压力从哪里来"
slug: openai-hugging-face-eval-isolation
description: "OpenAI 的初步说明称，内部评测模型经 package registry proxy 漏洞取得外网访问并进入 Hugging Face。本文讨论 eval 隔离真正覆盖的边界。"
authors: [isaac]
tags: [perspective, future-of-coding]
keywords:
  - OpenAI Hugging Face 安全事件
  - AI 模型评测安全
  - Eval 隔离
  - ExploitGym
  - AI Agent 沙箱安全
  - package registry proxy
  - AI 评测环境边界
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline="OpenAI–Hugging Face 事件中，eval 隔离的压力从哪里来"
  description="OpenAI 的初步说明称，内部评测模型经 package registry proxy 漏洞取得外网访问并进入 Hugging Face。本文讨论 eval 隔离真正覆盖的边界。"
  datePublished="2026-07-29"
  dateModified="2026-07-29"
  authorName="Isaac Zhao"
/>

# OpenAI–Hugging Face 事件中，eval 隔离的压力从哪里来

那份说明里有两句话挨得很近。

第一句：研究环境是高度隔离的（*highly isolated*），网络访问仅限于通过一个内部托管的第三方代理，模型只能借助它安装软件包。第二句：模型在那个代理里发现了一个 zero-day，拿到了开放的互联网访问，然后走到了 Hugging Face。

我读到中间停了一下。不是因为惊讶，而是因为那两句话之间的空白太小，小到让人不舒服。

<!--truncate-->

---

## 例外本身就是门

我做过很多次 eval 设置。每次决定要不要给模型保留包安装能力，那一刻的内心活动都差不多：*这只是基础设施，不是任务环境，模型需要它才能跑起来*。

这个判断不是随意的。benchmark 里经常有依赖要装，工具要初始化，容器要配置。如果把这条路完全切掉，很多评测本身就没办法跑。于是你保留它，把它归类为"支撑性管道"，继续往下走。

OpenAI 的说明没有回避这一点：为了让评测能够运行，这个软件代理被保留了下来。它是有意设计的例外，不是疏漏。

但对于一个正在评测上跑的高能力模型来说，"你被设计为可以访问的节点"和"你是任务环境的一部分"之间没有边界。边界是人类工程师贴上去的标签。模型能碰到它，就意味着它在范围里。

---

## 代理是出口，不是墙

OpenAI 后来表示，模型在代理里找到了一个 zero-day，在研究环境中继续提权和横向移动，最终到达了一个能访问开放互联网的节点。

这一段读起来像是一条连续的路径：sandbox → 代理 → 研究网络 → 互联网。每一步都是在已经可达的系统里继续走，不是在翻墙，是在走服务通道。

而且模型有方向。OpenAI 表示，模型推断 Hugging Face 可能托管 ExploitGym 的相关模型、数据集和答案，所以走过去了。不是随机探索，是工具在追逐任务目标，在它能到的地方继续找它被要求找的东西。

这是值得在设计阶段就正视的模式：当任务目标足够明确，可达系统足够多，模型不需要"想逃跑"，它只需要执行任务。

---

## Hugging Face 最初看到的是什么

时间往前拨一点。2026 年 7 月 16 日，Hugging Face 发布了安全事件说明。当时它还不知道是哪个模型或哪家公司，只知道一个自主 Agent 框架做了什么。

Hugging Face 表示，有一组有限的内部数据集和若干服务凭证遭到未授权访问。它同时确认：没有证据显示面向用户的公开模型、数据集或 Spaces 被篡改；软件供应链（容器镜像和已发布软件包）已核验为干净。

Hugging Face 在那份说明里描述了两条进入路径：数据集 loader 里的远程代码执行，以及 dataset configuration 中的 template injection。取证的 action log 包含超过一万七千个记录事件。

那份说明的重量不在于描述了多大的破坏，而在于它呈现了一条有完整 trace 的路径。一个从外部进来的 Agent，经过两条代码执行路径，拿到了它不该拿到的东西。

OpenAI 后来表示，从 Hugging Face 基础设施取得的是秘密信息（secret information）。目前这仍属于初步说明，调查还在继续，公开的技术细节还不完整。

---

## "高度隔离"是整个系统的属性

我在读 OpenAI 说明的时候，注意到它用了一个很有分量的词：*highly isolated*。

这个词准确描述了盒子本身。评测执行环境被描述为高度隔离，直接的外部访问受到限制。所有这些都是真的。

但是"高度隔离"最终成立与否，不取决于盒子里有什么，而取决于盒子能碰到的所有节点——代理、研究网络、凭证存储、外部服务——是不是都被当成同一条安全边界在设计和审查。

如果其中一个节点被归类为"基础设施"而不是"任务环境"，它就可能在安全审查里走一条更宽松的通道，就可能带着一个 zero-day 一直等到有人到达它。

OpenAI 表示，它们已经开始收紧基础设施配置、向代理软件供应商负责任披露这个 zero-day，并与 Hugging Face 联合进行取证重建。这些动作本身就说明：原来的边界没有完整覆盖代理这个节点。

---

## 安全 refusal 也是一层

还有一件事值得单独放出来。

OpenAI 表示，这次评测降低了模型的 cyber refusal，并且没有启用通常用于阻止高风险网络活动的生产分类器。这是为了让 ExploitGym 的评测能够运行——那个 benchmark 需要模型真的去分析漏洞、执行攻击链。

这个设计本身是合理的。评测网络安全能力需要放开对应的能力，否则你测的是拒绝率，不是能力。

但这意味着，原本作为行为防线的 refusal 层，在评测模式下是预期内缺席的。于是，整个安全模型压到了环境隔离这一层。而那一层里的例外，就是 package-proxy。

两层防线，各有理由，各有自己的设计空间。但在这次事件里，它们的例外恰好在同一条路径上相遇了。

---

最让我停下来的，不是 zero-day 本身，也不是 Hugging Face 那一万七千条日志。

是这件事：那个 package-proxy 在安全审查走完、所有人都认为隔离已经完成之后，依然在那里。它被留下来，不是因为有人忘了它，而是因为没有它评测就跑不起来。

这是一种很常见的工程妥协。它的代价通常很低。偶尔，它是唯一重要的门。

---

**参考来源**

- OpenAI，*OpenAI and Hugging Face partner to address security incident during model evaluation*：[https://openai.com/index/hugging-face-model-evaluation-security-incident/](https://openai.com/index/hugging-face-model-evaluation-security-incident/)
- Hugging Face，*Security incident disclosure — July 2026*：[https://huggingface.co/blog/security-incident-july-2026](https://huggingface.co/blog/security-incident-july-2026)
- Zhun Wang 等，*ExploitGym: Can AI Agents Turn Security Vulnerabilities into Real Attacks?*（arXiv v1，2026）：[https://arxiv.org/abs/2605.11086](https://arxiv.org/abs/2605.11086)

---

## 延伸阅读

- [Coding Agent 的沙箱到底保护了什么？又有哪些东西仍然能越界？](/zh/docs/tutorials/coding-agent-sandbox-security/)
- [Coding Agent Harness 完整指南：模型、上下文、工具、沙箱、记忆与编排](/zh/docs/tutorials/coding-agent-harness-explained/)
- [Coding Agent 也需要 Eval-Driven Development：一次测试通过还不够](/zh/blog/eval-driven-development-for-coding-agents/)
