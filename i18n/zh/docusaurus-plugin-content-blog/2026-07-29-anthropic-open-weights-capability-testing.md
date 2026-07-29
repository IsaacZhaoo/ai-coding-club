---
title: 'Anthropic 说所有"足够强大"的模型都该测试，但"足够"由谁来定义？'
slug: anthropic-open-weights-capability-testing
description: "Anthropic 主张“足够强大”的开放和封闭模型都应接受安全测试。真正未解决的问题，是如何定义并公开能力阈值。"
authors: [isaac]
tags: [perspective, future-of-coding]
keywords:
  - Anthropic 开放权重
  - 开放权重安全测试
  - 能力阈值
  - 模型发布测试
  - frontier 模型安全
  - sufficiently capable
  - 不可逆权重发布
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline={'Anthropic 说所有"足够强大"的模型都该测试，但"足够"由谁来定义？'}
  description="Anthropic 主张“足够强大”的开放和封闭模型都应接受安全测试。真正未解决的问题，是如何定义并公开能力阈值。"
  datePublished="2026-07-29"
  dateModified="2026-07-29"
  authorName="Isaac Zhao"
/>

# Anthropic 说所有"足够强大"的模型都该测试，但"足够"由谁来定义？

打开 Anthropic 那篇说明的时候，我读到了一个让我停下来的短语。

文章说，所有 *sufficiently capable* 的模型——无论开放还是封闭权重——都应在发布前接受强制安全测试。这句话读起来像一个精确的限定词。但我做产品的习惯让我本能地去找后面那个字段：什么叫 sufficiently？能力怎么测？阈值画在哪里？谁来画？

如果这是一段代码，我会说：校验规则还没写。

<!--truncate-->

---

Anthropic 主张，不具有危险能力的开放权重模型是一种公共产品（public good）。这部分我读得很顺——它承认了开放权重的真实价值，也没有把所有开放模型一刀切地归入高风险。

但同一份说明里有另一条逻辑，让我觉得"open / closed"这个二元开关承载不了它被要求承载的东西。

Anthropic 说，权重一旦发布，就很难再统一施加使用阶段的 guardrail、监控、访问控制，也无法撤回。这条观察是准确的。权重不是 API 调用，它不会在你发完之后等你去改配置。

开放权重联名信也承认这一点：权重发布后会脱离原始开发者的控制，被修改的版本很难追踪或逆转。这封信同时主张，开放权重可以扩大访问、竞争、用户控制、可适配性、透明度和防御能力，并建议用定向的法律和商业框架来处理问题，而不是广泛限制。

我认同这些好处是真实的。我也认同不可逆是真实的。

问题恰恰在这里：如果"open"和"closed"都不是一个整齐的安全类别，那用这个开关来决定是否触发发布前测试，就是在用错误的粒度做判断。

---

英国 AI Security Institute（AISI）在它的 cyber 评测中发现了一些具体的东西。在设定明确范围的 cyber 测试里，GLM-5.2 和 DeepSeek V4-Pro 落后于指定封闭权重对照模型约 4 到 7 个月——比 AISI 在 2025 年大部分时间内部测到的 6 到 10 个月差距更窄。

AISI 明确说明：这个结果只适用于被命名的模型、cyber 测试，以及当前的评测方法。测试设置还可能稍微低估了开放权重模型的最高能力。

我没有运行这些评测，也没有看到背后的私有数据。但这个结果让我注意到的不是具体的月份数字，而是"差距在缩小"这件事本身所暗示的速率问题——如果一个基于静态月份差距的判断框架，它的刷新频率跟不上模型演进的速度，那个框架就会开始对现实撒谎。

并且，生物风险或其他高风险领域的能力评测，不能从这份 cyber 结果里直接外推。范围必须写清楚，才不会让一个领域的结论变成另一个领域的护身符。

---

Demis Hassabis 提议了一个框架：通过能力阈值定义"Frontier-class"，在 cyber、生物风险等高风险领域做发布前测试，不区分 open / closed，并豁免非 frontier 模型。

这个框架还是一个提案，不是已生效的政策，也不是 Google DeepMind 已经强制执行的标准。但我注意到，它和 Anthropic 说明的逻辑方向有一个共同点：测试应该由能力触发，而不是由发布形式触发。

这个共享方向对我来说是有意义的。如果发布门的传感器感应的是能力，那它就在测量值得测量的东西；如果传感器感应的只是权重格式，那它只是在为决策过程制造一种精确感。

---

对低能力的开放模型来说，低摩擦通道必须保留。初创公司的研究模型、学界的实验权重，如果被拖进一个为 frontier 危险能力设计的发布流程，不是安全提升了，而是创新路径变窄了，而真正应该被拦下来的东西依然在别处。

真正需要发布前测试触发的，是已被证明的危险能力——在发布之后就无法再收回的那种不可逆性，要求在发布之前完成判断。这一点在各份来源里有足够共识，足以作为判断的起点。

但目前，"危险能力"在这些文件里仍然是一个定性描述。Anthropic 说明没有给出本文可以直接引用的完整、已定案阈值。联名信要求用定向框架替代广泛限制，但没有写出那个框架的刻度。Hassabis 提案是目前我看到结构最接近可操作定义的方向，但它还在提案阶段。

发布门已经被谈论，但传感器的校准规则还没有公开写下来。

---

这让我回到那个短语：*sufficiently capable*。

如果没有人公开说明它指向哪些能力、用什么评测方法测量、阈值画在哪里——那它就只是一个占位符，暂时填充了一个真正的判定条件应该在的位置。

作为产品开发者，我有一个不太优雅的习惯：当我在一个校验字段里看到模糊条件，我会把这条路推迟，直到规则写清楚。但在发布前安全测试这件事上，推迟本身就是一个选择，而这个选择的后果会附在那份权重文件里一起发出去，收不回来。

*Sufficiently capable* 只有在某个人必须定义它、为它辩护、公开它的测量方式时，才开始真正承担责任。

---

**参考来源**

- Dario Amodei / Anthropic，*Our position on open-weights models*（2026-07-27）：[https://www.anthropic.com/news/position-open-weights-models](https://www.anthropic.com/news/position-open-weights-models)
- *Open Weights and American AI Leadership* 联名信：[https://images.nvidia.com/pdf/Open-Weights-and-American-AI-Leadership.pdf](https://images.nvidia.com/pdf/Open-Weights-and-American-AI-Leadership.pdf)
- 英国 AI Security Institute，*How Far Behind the Frontier are Leading Open Weight Models on Cyber?*：[https://www.aisi.gov.uk/blog/how-far-behind-the-frontier-are-leading-open-weight-models-on-cyber](https://www.aisi.gov.uk/blog/how-far-behind-the-frontier-are-leading-open-weight-models-on-cyber)
- Demis Hassabis，*A Framework for Frontier AI and the Dawning of a New Age*：[https://demishassabis.substack.com/p/a-framework-for-frontier-ai-and-the-dawning-of-a-new-age](https://demishassabis.substack.com/p/a-framework-for-frontier-ai-and-the-dawning-of-a-new-age)

## 延伸阅读

- [Kimi K3 权重开放，算力门槛也跟着公开了](/zh/blog/kimi-k3-open-weights-compute-barrier/)
- [OpenAI–Hugging Face 事件中，eval 隔离的压力从哪里来](/zh/blog/openai-hugging-face-eval-isolation/)
- [Coding Agent Evals 教程：把 Trace 变成数据集和质量门禁](/zh/docs/tutorials/coding-agent-evals-guide/)
