---
title: "最小修复前：检查你的“代码归属权”是否错配了"
sidebar_label: "Fable 5.2 的最小修复"
description: "在使用 Fable 5.2 做小修复前，检查继承的项目设计与维护授权，并用验收条件和实际 diff 核对改动范围。"
sidebar_position: 2
---

# 最小修复前：检查你的“代码归属权”是否错配了

你正要用 Claude Fable 5.2 做一个小修复吗？在运行模型之前，先花三分钟做一件事：**审视你继承下来的旧提示里，有没有把项目的设计决策和持续维护权“外包”给了模型。**

这不是玄学。Anthropic 官方文档已经明确给出了依据：在 Fable 5.2 的实验中，当提示中赋予模型“代码归属/角色与权限”时，小任务会出现结构性清理和额外改动；而另一处范围限制，并未能完全抵消这个效应。<br />
> 基于 Anthropic Claude [官方提示指南](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2#say-who-owns-the-code)

---

## 为什么这一点现在特别重要？

Fable 5.2 发布后，Anthropic 建议大多数编码与知识工作从 **Claude Opus 5.5** 开始尝试。但这不意味着你必须为所有日常任务立刻换模型。（官方公告见 https://www.anthropic.com/claude-fable-and-mythos-5-2 ）<br />
真正需要你立刻调整的是：**在同一个新会话里，旧提示的“权限语言”可能和新任务的“最小修复目标”打架了。**

如果旧提示里有类似这样的一段话（哪怕是你以前随手写的）：

> “You decide this project’s design and future direction.”<br />
> （你决定本项目的设计与未来方向。）

那么这段指令就是在做一件和“最小修复”完全冲突的事：**它把架构演进权交给了模型**。<br />
当模型发现当前任务恰好包含可重构空间，它的行为倾向就会偏向“顺便优化”，于是你看到的 diff 里多了不该动的逻辑、变了名字的函数、甚至新增依赖。

官方指南给出的直接建议是：<br />
> 对于需要**最小改动**的用户自有代码，**省略**那段“归属/授权”语句；保留所需的权限和具体行为/范围说明即可。<br />
> （来源同上）

注意：这里说的“ownership”，指的是**提示中的角色与权限设定（prompting behavior）**，不是法律意义上的知识产权归属。

---

## 那么，我到底该检查什么？

把当前会话的系统提示 / 早期指令 / 项目规则复制出来，只盯这三类句子：

1. **宽泛的设计委托型**<br />
   - “You decide the architecture.”<br />
   - “Feel free to refactor as needed.”<br />
   - “Optimize this for performance and clarity.”<br />
   → 如果当前任务只是修一个边界条件或回归 bug，这类句子大概率该删。

2. **范围模糊的“可改进”型**<br />
   - “Improve readability where obvious.”<br />
   - “Clean up dead code if you see it.”<br />
   - “Add comments and improve naming.”<br />
   → 这些不是错，但它们会诱发“顺便清理”的行为。在严格的最小修复任务里，建议把范围收紧到可验证的改点，或改为“仅在以下范围内改进”。

3. **明确的范围限制型**<br />
   - “Only change the function `filterByPrice` to fix exact-equal behavior.”<br />
   - “Preserve all existing tests and public APIs; only adjust the comparison operator.”<br />
   → 这类提示是保护你的，保留。

关键点：如果某个条款与“最小修复”冲突，**不要指望另一处的范围限制会自动抵消它**。Fable 5.2 的实验结论就是：**有归属授权时，清理效应会出现；再加一个范围限制，并不等于回归原状。**

---

## 用一个小修复来演示这个决策怎么落地

假设你现在的目标是：<br />
> “价格过滤器排除一个价格**恰好等于最大值**的商品。要求改为包含它：≤ max_price。保持原有顺序，只改必要逻辑。”

一个典型的输入输出：

- 输入：`[8, 10, 12]`，max_price = 10<br />
- 期望输出：`[8, 10]`（前两个保留，顺序不变）

在 Fable 5.2 会话中，你的提示结构应该像这样：

- **目标**：修复 `filterByPrice` 的边界比较逻辑，从 `<` 改为 `<=`。<br />
- **约束**：<br />
  - 仅修改比较条件；不改动参数名、返回值类型、测试用例或外部依赖。<br />
  - 必须通过所有现有测试（包括边缘值 max_price）。<br />
- **范围声明**：<br />
  - “Do not refactor, rename, or introduce new abstractions unless explicitly requested.”

如果你在这个提示里还带着旧系统指令：“Feel free to clean up and optimize the module as you see fit”，模型就有理由顺手把函数名改成 `filterByMax`，抽离出 `isWithinRange`，甚至改写调用链。这些改动对“≤ max_price”这个验收目标是多余的，但会在 diff 里制造噪音，让你误以为是一次“全面重构”。

官方指南的实操建议正是如此：**在最小修复场景下，把“归属授权”去掉，让模型的角色回归到“执行明确约束的技工”，而不是“架构顾问”。** 这是对当前小修复的做法。

---

## 做完之后，你还得做两件事

1. **看 diff，别只看测试通过**<br />
   - 绿色测试报告 + 一句“summary looks good” ≠ 范围合规。<br />
   - 对照你的约束清单：有没有不该动的函数被重命名？有没有新依赖被引入？有没有逻辑被挪到工具链里？<br />
   - 如果出现了设计改进，那应该是**单独评估的选项**，而不是模型在“顺手”塞进 diff 里的隐藏改动。

2. **把这次检查结果沉淀为一条规则**<br />
   - 如果旧提示里有宽泛授权：下次新会话直接删掉它。<br />
   - 如果发现模型在微小改动里主动重构：把“最小修复”的约束写得更硬，或拆分任务（先改逻辑 → 再问要不要重构）。

---

## 结论：这不关乎 Fable 是不是更强，只关乎你的提示有没有越界

- 你没有必要因为 Fable 5.2 发布就更换主力模型。<br />
- 你真正需要做的是：**在做每一个小修复前，确认当前会话的提示里没有把项目设计权“默认授予”模型。**<br />
- 如果存在冲突，**去掉授权条款**；保留必要的行为、边界和验收标准。

这是基于 Anthropic 官方披露的实验证据给出的最小可行配置策略：用更细的权限声明，换取更可控的改动范围，而不是指望模型自己“自觉收敛”。

---

### 想进一步把这种控制力变成习惯？

- 想深入理解如何用验收条件约束 AI 行为，读：[用价格过滤器写验收条件](/zh/docs/tutorials/acceptance-criteria-for-coding-agents/)<br />
- 想把这类改动真正“看得见、管得住”，读：[审查 AI 的实际代码改动](/zh/docs/tutorials/ai-code-review-workflow/)

这篇只聚焦新模型带来的**一个配置决定**。把这些决定变成你的标准流程，你会发现每次调用 Fable / Opus / Mythos 时，少的是意外重构，多的是对微小改动的清晰掌控。
