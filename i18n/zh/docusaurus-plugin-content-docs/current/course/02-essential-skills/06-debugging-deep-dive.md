---
sidebar_position: 6
sidebar_label: '调试深潜：从错误到解决方案'
title: '调试深潜：从错误到解决方案'
description: '调试深潜：从错误到解决方案'
---

> TL;DR：更系统地排错：假设、证据与回归测试。

## 关键步骤
1. 列假设并按可能性排序。
2. 用日志/断点收集证据。
3. 修复后补回归测试。

## 练习
- 挑一个最近 bug，写一个能捕获它的回归测试。

这篇文章扩展了调试的基础，提供了一种系统性的方法来查找和修复代码中的错误。我们将涵盖使用AI作为调试伙伴、有效阅读文档以及使用常见的调试工具。

### 调试的系统方法

当你遇到bug时，诱惑是随意更改代码直到它工作。一个更好的方法是有一个系统。

1. **重现Bug**：持续地使bug出现。
2. **理解错误**：仔细阅读错误消息。
3. **形成假设**：猜测什么可能导致问题。
4. **测试假设**：使用print语句、调试器或要求AI验证你的猜测。
5. **修复和验证**：应用修复，并确保bug消失且没有引入新的bug。

### 使用AI作为调试伙伴

AI可以是一个强大的调试助手。与其只是说"它坏了"，不如提供背景。

**好的提示：**
> "我在我的JavaScript代码中得到`TypeError: cannot read properties of null`。这是它发生的函数：`[代码片段]`。我认为`user`对象有时为null。你能帮我添加检查吗？"

### 阅读文档

有时答案在官方文档中。学会阅读它是一种超能力。
- **MDN Web文档**：适用于网络开发（JavaScript、HTML、CSS）。
- **Stack Overflow**：搜索类似的错误消息。

### 调试工具

- **浏览器控制台**：对于前端JavaScript是必需的。使用`console.log()`来检查变量。
- **IDE调试器**：像VS Code中的工具让你暂停代码执行、检查变量并逐行执行代码。

### AI用于测试生成

你可以要求AI编写可能会reveal一个bug的测试。

**提示：**
> "为这个JavaScript函数编写一组测试来覆盖边界情况，特别是当`input`是空数组或包含非数值时会发生什么。`[代码片段]`"

### 实战：用运行时证据定位搜索与筛选冲突

在前文中，你已掌握了复现、假设、日志、断点和让 AI 生成测试的基本流程。这一节将把这套方法聚焦到一个具体的 React 场景：**商品搜索框与分类筛选器单独都能正常工作，但一旦组合使用，分类条件就“消失”了**。

我们并不先问“是不是 state 没更新？”或“是不是 debounce 太慢？”，而是让证据告诉我们：哪一步计算漏掉了仍然有效的约束。

---

#### 1. 从已知案例切入：一个可复现的抽象

[Nathan Onn 在一次公开调试笔记中](https://www.nathanonn.com/claude-code-debugging-visibility-methods/)记录了一个类似的 Products Browser：

- 输入搜索词 `apple`，并选择 `laptops` 分类；
- 单用搜索或单用分类都正确；
- 但组合使用时，显示结果却忽略了分类约束。

作者起初直接尝试修复代码，尚未引入额外的日志追踪。随后，他转而加入日志：在影响列表显示的各个 `useEffect` / 计算步骤中打印“触发原因、当前条件、计算结果”，然后把控制台输出交回给 Claude。这段证据链最终揭示了：**输入筛选的搜索计算，完全从完整商品列表中重新搜索，并覆盖了之前的分类结果**。

关键在于：当一项新计算“写入”显示列表时，它读取了哪些输入？又是否保留了仍然有效的筛选条件？

这篇文章会带你走完同一路径，但用更具体的数据、更可核对的回归条件，以及可直接交给 AI 的分析请求。

---

#### 2. 搭建最小可复现的数据与规则

为了清晰追踪每一步计算，我们先固定一套商品数据和筛选规则。读者在真实项目中可以按同样结构记录自己的数据。

##### 2.1 商品表（示例数据）

| ID | brand   | name          | category |
|----|---------|---------------|----------|
| P001 | Apple | iPhone 16     | phones   |
| P002 | Apple | MacBook Air   | laptops  |
| P003 | Apple | iPad Pro      | tablets  |
| P004 | Dell  | XPS           | laptops  |
| P005 | Samsung| S24          | phones   |

##### 2.2 筛选规则（用于预期结果核对）

- 搜索规则：
  - 对 `brand` 或 `name` 进行**不区分大小写的子串匹配**。
  - 若 `query` 为空字符串，则不过滤名字/品牌。
- 分类规则：
  - 若 `category === "all"`，则不过滤分类字段。
- 显示列表应同时满足所有生效条件。

##### 2.3 预期结果表（按组合条件）

| query    | category | 正确预期 ID     |
|----------|----------|-----------------|
| apple    | laptops  | P002            |
| （空字符串）| laptops  | P002、P004      |
| apple    | all      | P001、P002、P003|
| apple    | tablets  | P003            |
| dell     | tablets  | （空列表）      |
| apple    | phones   | P001            |

这些预期将作为回归检查的“锚点”。

---

#### 3. 复现步骤：让读者写出自己的“证据起点”

在动手写日志之前，请你在自己的环境中按以下步骤操作，并**精确记录每一步的输入状态与显示结果**：

1. 初始状态：
   - `query = ""`
   - `category = "all"`
2. 选择分类 `laptops`（不改变搜索词）。
3. 在搜索框中输入 `apple`。
4. 观察显示的商品列表 ID。
5. 清除搜索词，保持 `category = laptops`。
6. 输入搜索词 apple 并将分类改为 all，确认搜索结果中仍显示 P001/P002/P003。

记录你要的东西：

- 每一步的：
  - 当前 `query`
  - 当前 `category`
  - 显示列表中的商品 ID
- 如果可能，还记录：
  - 哪一步触发了界面刷新（例如：某个输入事件、某个选择事件）
  - 控制台或日志中提示“正在筛选”“正在搜索”等提示

这份“操作序列 + 结果快照”是后续交给 AI 分析时的最小上下文。

---

#### 4. 引入运行时证据：在关键计算处加日志

按照 Nathan 的思路，不要一开始就动筛选逻辑。先观察**是谁、在什么时候、基于哪些输入、算出什么结果**。

在典型的商品列表组件中，会有几个关键位置：

- 分类选择的 `useEffect`（或渲染时的推导）
- 搜索词变更的 `useEffect`（或渲染时的推导）
- 最终写入显示列表的位置（可能是另一个 `useEffect`、`useState` 更新，或直接返回给父组件）

为每个计算点添加结构化日志，例如：

```js
console.log('[FILTER] category changed:', {
  previous: oldCategory,
  current: newCategory,
  inputSet: allProducts.map(p => p.id),
  resultIds: computedIds,
});

console.log('[SEARCH] query changed:', {
  previous: oldQuery,
  current: newQuery,
  inputSet: allProducts.map(p => p.id),
  resultIds: computedIds,
});

console.log('[DISPLAY] list updated:', {
  reason: 'search',
  itemIds: displayedIds,
});
```

然后按“第 3 步”的复现顺序操作，把控制台输出完整复制下来。你看到的典型错误日志序列（对应本文示例数据）可能是：

- `[FILTER] category changed`：
  - `previous: "all"` → `current: "laptops"`
  - `inputSet: [P001..P005]`
  - `resultIds: [P002, P004]` ← 正确
- `[SEARCH] query changed`：
  - `previous: ""` → `current: "apple"`
  - `inputSet: [P001..P005]`
  - `resultIds: [P001, P002, P003]` ← 从全集重新计算
- `[DISPLAY] list updated`：
  - `reason: "search"`
  - `itemIds: [P001, P002, P003]` ← 覆盖了之前的分类结果

证据清晰：**搜索计算从完整商品集出发，只应用了搜索规则，却没有携带仍然有效的分类条件**。后续即使分类仍是 `laptops`，显示列表里却出现了不该在的 `P001` 和 `P003`。

> 注意：这里我们并不先断定“是旧 state 没更新”或“debounce 晚了”。证据表明的是：**某次结果计算漏用了仍然有效的约束**。

---

#### 5. 基于日志提出假设并让 AI 协助分析

拿到日志后，你可以用类似下面的方式与 AI 协作（保持上下文简洁、结构化）：

```text
任务：定位商品搜索与分类筛选冲突。

数据：
- 商品表：
  P001: Apple, iPhone 16, phones
  P002: Apple, MacBook Air, laptops
  P003: Apple, iPad Pro, tablets
  P004: Dell, XPS, laptops
  P005: Samsung, S24, phones

规则：
- query 为空时不过滤名字；category === "all"时不过滤分类。
- brand + name 不区分大小写子串匹配。

复现步骤与日志摘要：
1) category: "all" → "laptops", query: ""
   [FILTER] resultIds = [P002, P004]
2) query: "" → "apple"（category 仍为 "laptops"）
   [SEARCH] resultIds = [P001, P002, P003]
   [DISPLAY] itemIds = [P001, P002, P003]

现象：
- 单用搜索或单用分类都正确。
- 组合时出现 P001、P003，应被 category="laptops" 过滤掉。

问题：
哪一步计算漏用了仍然有效的分类条件？请给出：
1) 可能原因（至少两种）；
2) 建议的修正方向（代码结构层面，不直接给成品逻辑）。
```

AI 通常会给出类似结论：

- 搜索计算在“输入集”或“过滤函数”中没有传入当前 `category`。
- 显示列表的更新逻辑由单一事件驱动（如仅“搜索词变化”），导致分类变化后的状态没有参与新一轮计算。
- 推荐引入一个统一的筛选函数，统一接收 `query`、`category` 及其他条件，并在每次需要时调用。

这些判断是否成立，需要你在代码层面验证。但日志 + 预期表已经帮你把“可疑点”精确到了计算层。

---

#### 6. 修复方向：用统一的派生计算替代分散的 effect

[React 官方的建议](https://react.dev/learn/you-might-not-need-an-effect)很明确：**如果能由现有 props/state 算出，就尽量在渲染过程中派生；[`useMemo`](https://react.dev/reference/react/useMemo) 用于缓存计算结果、减少不必要的重算**。

在商品列表的场景中，一个更稳健的结构是：

1. 将筛选逻辑集中到一个纯函数（或 hook）：
   - 输入：
     - `allProducts`
     - `query`
     - `category`
     - 其他筛选/排序参数
   - 输出：
     - 符合所有条件的商品列表
2. 在组件中，用 `useMemo` 包裹这个计算：

```js
const filteredProducts = useMemo(() => {
  if (!query && category === 'all') return allProducts;

  const q = query.toLowerCase();
  const c = category || 'all';

  return allProducts.filter(p => {
    const matchQuery =
      !q ||
      p.brand.toLowerCase().includes(q) ||
      p.name.toLowerCase().includes(q);
    const matchCategory =
      c === 'all' || p.category === c;
    return matchQuery && matchCategory;
  });
}, [allProducts, query, category]);
```

3. 将 `filteredProducts` 作为显示列表的来源，而不是在多个 `useEffect` 中更新 state。

这种结构的好处：

- 每次 `query` 或 `category` 变化时，`useMemo` 都会重新计算，但**只基于传入的参数**。
- 没有任何“覆盖式”的副作用：谁提供条件，谁就决定结果。
- 日志不再分散在多个 effect 中，而是集中在一个计算块里，方便验证输入和输出。

你可以对照自己的日志，确认是否恰好是某个搜索 effect 独立调用了类似逻辑，而没有传入当前 `category`。如果是，那么统一计算就是针对性的修正。

---

#### 7. 修复后：制定可核对的回归条件

修复不是终点，可重复验证才是。用之前建立的“预期结果表”作为回归检查依据。

建议的回归检查清单（读者需将实际商品与 ID 替换为自己的数据）：

1. 基本组合路径：
   - `query = "apple"`, `category = "laptops"` → 显示 `[P002]`
   - `query = ""`, `category = "laptops"` → 显示 `[P002, P004]`
   - `query = "apple"`, `category = "all"` → 显示 `[P001, P002, P003]`
   - `query = "apple"`, `category = "tablets"` → 显示 `[P003]`
   - `query = "dell"`, `category = "tablets"` → 显示空列表
   - `query = "apple"`, `category = "phones"` → 显示 `[P001]`

2. 状态切换路径（重点）：
   - 先选分类再搜索：
     - 从 `category="all"` 切换到 `"laptops"`，观察列表；
     - 再输入 `query="apple"`，观察是否仍为 `[P002]`。
   - 先搜索再选分类：
     - 从 `query=""` 输入 `query="apple"`；
     - 再切换 `category="laptops"`，观察是否变为 `[P002]`。
   - 清空搜索词后保留分类约束：
     - 从 `query="apple"`, `category="laptops"` 改为 `query=""`, `category="laptops"` → `[P002, P004]`。
   - 清除分类后保留搜索约束：
     - 从 `category="laptops"` 改为 `"all"`，保持 `query="apple"` → `[P001, P002, P003]`。
   - 无匹配情况：
     - 例如 `query="xyz"`, `category="laptops"` → 空列表（不报错、不闪动）。

3. 工具层面的回归（可选）：
   - 使用 React Testing Library + Vitest：
     - 渲染组件，模拟输入事件和选择事件；
     - 断言查询结果（通过 `getByRole`、data-testid 或内部映射）与预期 ID 一致。
   - 将以上组合条件写进测试用例，作为持续集成的一部分。

回归检查表可以放在一个单独的文档或注释块中：

```text
[REGRESSION] Query / Category Matrix
- apple + laptops          → P002
- "" + laptops             → P002,P004
- apple + all              → P001,P002,P003
- apple + tablets          → P003
- dell + tablets           → []
- apple + phones           → P001

操作顺序要求：
- 选分类 → 搜词 → 结果仍符合两者
- 搜词 → 选分类 → 结果仍符合两者
- 清空 query → 保留 category
- 清空 category → 保留 query
- 无匹配 → 空列表（稳定）
```

---

#### 8. 小结：从日志到可验证的行为约定

这一节的完整闭环是：

1. **复现顺序**：按固定的输入变化路径操作，记录每一步的 `query`、`category` 与显示 ID。
2. **运行时证据**：在关键计算处加结构化日志，观察谁读取了哪些输入，谁最后写入了显示列表。
3. **AI 协作分析**：将“数据 + 规则 + 日志摘要”打包交给 AI，请求可能的原因与修正方向。
4. **统一计算修复**：用集中、可追踪的筛选逻辑（配合 `useMemo`）替代分散的效果式更新。
5. **回归检查**：用固定表格中的组合条件与预期 ID 反复核对，确保所有交互路径都稳定正确。

当你读完本节并动手完成上述练习时，你应当能够：

- 写出一段清晰、可复现的“操作序列 + 状态快照”；
- 从日志中识别出覆盖式计算或漏用条件的具体步骤；
- 提出一段给 AI 的具体调试请求，包含必要的数据与约束；
- 为同一组筛选逻辑制定一套可核对的回归条件。

这些能力不仅适用于商品搜索场景，也适用于任何“多个动态约束叠加却出现冲突”的交互系统。

#### 相关练习

- [审阅 AI 生成的测试](/zh/docs/tutorials/ai-generated-test-review/)
