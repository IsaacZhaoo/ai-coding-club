---
title: "Loop Engineering 实战：构建一个有预算、会停止、能升级的 Coding Agent Loop"
description: "用局部目标、Evaluator、预算、停止条件、权限范围和升级路径，构建一个有边界、可验证的 Coding Agent Loop。"
keywords:
  - Loop Engineering
  - Coding Agent Loop
  - Agent 循环
  - Agent Evaluator
  - Agent 治理
sidebar_position: 17
tags: [tutorial, coding-assistant, agent-engineering, loop-engineering]
---

# Loop Engineering 实战：构建一个有预算、会停止、能升级的 Coding Agent Loop

---

我最初对 Agent Loop 的理解，和大多数开发者一样：任务没完成就继续跑，直到成功或者我手动叫停。这个理解没有错，但它把 Loop 理解成了一种执行态度，而不是工程对象。

态度不能被测试，不能被预算，也不能在出错时给你一份结构化的失败报告。

这篇文章要说清楚的，是 Loop 怎样从"反复尝试"变成一份可以设计、测试、治理的合同。

---

## 一句话先说清楚

**一个有用的 Coding Agent Loop，是一份有边界的局部控制合同。**

它只能在明确权限内调整手段，每次行动后接受评价，在成功或预算耗尽时停止，遇到目标修改则升级——而不是自己悄悄改目标。

这一句话里有四个关键词：局部、评价、停止、升级。接下来我会围绕同一个运行例子，把这四件事说完整。

---

## 先运行一次，看清楚 Loop 在做什么

示例场景：在不改变现有兼容性要求的前提下，为一个模块增加一个有上限的重试设置。

[下载经过验证的 Loop / Graph 示例](/examples/loop-graph-engineering-example.zip)。示例只使用 Python 标准库。

运行入口：

```python
contract = retry_feature_contract()
result = run_loop(contract)

print(result.outcome.value)
print(result.attempts)
print(result.final_state)
```

输出：

```text
success
2
RetryFeatureState(retry_limit=3, validation_added=True)
```

两次行动，Loop 停止，结果是 `success`。

这里发生了什么：

- **第一次行动**：action policy 把 `retry_limit` 设为 5，但没有增加校验逻辑。evaluator 检查状态，认为不满足接受条件，返回 `continue`。
- **第二次行动**：action policy 把 `retry_limit` 改为 3，并增加了校验。evaluator 重新检查，接受当前状态，返回 `success`。停止条件被触发，Loop 退出。

两次行动都在同一份合同的权限范围内完成。没有偷偷改目标，没有无限滚动，也没有对外声称"已完成"但状态仍然残缺。

运行测试：

```bash
python3 demo.py
python3 -m unittest discover . -p 'test_*.py'
```

---

## 合同结构

示例里的 `LoopContract` 长这样：

```python
@dataclass(frozen=True)
class LoopContract(Generic[StateT]):
    local_aim: str
    initial_state: StateT
    action_policy: Callable[[LoopContext[StateT]], ActionDecision[StateT]]
    evaluator: Callable[[StateT], Evaluation]
    budget: int
    stopping_condition: Callable[[Evaluation], bool]
    authority_scope: AuthorityScope
```

`LoopContract` 里有七个存储字段，runner 返回的 `EscalationResult` 是第八个概念性合同要素。这不是 Addy Osmani 的分类，也不是 Anthropic 的官方 API，而是我认为缺一个就会让 Loop 失控的八项。

下面按照它们在运行时的依赖顺序，而不是平均长度，说清楚每一项。

---

### 局部目标（local\_aim）

这是 Loop 被允许收敛的问题范围。

"局部"两个字很重要。一个完整任务往往包含多个子问题，每个子问题需要不同的停止条件和不同的权限边界。把整个任务塞进一个 Loop，要么停止条件变得模糊，要么权限边界变得危险。

示例里的局部目标是：

```
"Add a bounded retry setting without changing compatibility requirements."
```

这个目标在整个 Loop 生命周期内不会改变。evaluator 的判断、action policy 的行动选择、停止条件的触发，都围绕它展开。

一旦 action policy 发现要实现这个目标必须改动超出当前权限的内容——目标本身需要被修改，而不是手段——Loop 就应该升级，而不是自己悄悄扩大范围。

### 状态（initial\_state）

状态是 Loop 的信息载体。每次行动后，状态会被更新，evaluator 会读取状态来判断是否接受。

示例中的状态结构：

```python
@dataclass(frozen=True)
class RetryFeatureState:
    retry_limit: int | None = None
    validation_added: bool = False
```

状态里没有历史日志，没有完整上下文——只有 evaluator 做判断所需要的最小信息。这让 evaluator 的逻辑保持简单，也让测试保持可重复。

### 行动策略（action\_policy）

action policy 是 Loop 里变化最大的部分，也是最安全的修改点。

它的职责是：给定当前状态和上下文，决定下一步做什么。在示例里，action policy 是一个确定性函数。在真实的 Coding Agent 里，这个位置可以由 LLM、工具调用链、或者函数组合来履行——但合同结构不变。

**最重要的一点：action policy 只能决定手段，不能修改目标。**

如果 action policy 发现当前手段空间无法满足 `local_aim`，它可以返回一个升级信号，把决定权交出去。自己扩大目标，是 Loop 最危险的越权行为。

### Evaluator

Evaluator 是 Loop 唯一有资格宣布"成功"的角色。

我对"没有证据却宣布完成"的 Loop 有一种根本性的不信任。一个不经过 evaluator 就自己结束的 Loop，它的成功是没有意义的——我不知道它究竟收敛到了什么状态。

示例里的 evaluator 检查两件事：`retry_limit` 是否在合法范围内，以及 `validation_added` 是否为 `True`。两者都满足，才返回 `success`。

Evaluator 还有另一个权力：即使当前行动完全合法，如果它在检查状态的过程中发现需求本身存在冲突——比如两个约束互相矛盾——它也可以触发升级。升级不是错误，是 Loop 诚实面对自身局限的机制。

这也是 evaluator 成为第二个最安全修改点的原因：它的逻辑改变不会影响 runner，也不会影响合同结构，但会直接决定 Loop 收敛到哪里。

### 预算（budget）

预算是 Loop 的硬性上限，不是软性建议。

示例的默认预算是 3 次。两次行动成功，Loop 提前停止。如果三次都没有收敛，Loop 不会继续——它会返回 `budget_exhausted`，并附上当前状态作为结构化 handoff。

**预算耗尽是有效信息，不是无限重试的许可证。**

预算耗尽告诉你：在当前的行动策略和当前的评价标准下，这个局部目标在给定次数内没有收敛。这可能意味着 action policy 需要调整，可能意味着目标边界需要重新定义，也可能意味着问题本身比预想的复杂。但不管是哪种原因，Loop 不应该自己猜测并继续滚动。

Addy Osmani 在讨论 Loop Engineering 时提到无人值守错误和 Token 成本的风险——一个没有预算边界的 Loop 是最直接的来源。

**一个小练习**：把示例里的 `budget` 改为 1，然后重新运行。你会看到结果从 `success` 变成 `budget_exhausted`，因为第一次行动无法满足 evaluator 的接受条件。这是预期行为，不是 bug。

### 停止条件（stopping\_condition）

停止条件是评价到行动之间的桥梁。它读取 evaluator 的输出，决定 Loop 是否应该终止。

示例里的停止条件非常简单：如果 evaluator 返回 `success`，就停止。这个设计有意保持简单，是因为停止条件越复杂，它和 evaluator 的职责就越容易重叠。

Anthropic 在 `Building effective agents` 里建议设置最大迭代次数，并强调 ground truth 来自环境而不是 agent 自身——这两点在合同里分别对应 `budget` 和 `evaluator`。

### 权限范围（authority\_scope）

权限范围定义了 Loop 被允许触碰的边界。

示例里的 `AuthorityScope` 包含 `allowed_actions`：Loop 可以修改 implementation，可以修改 tests，但不能修改兼容性要求，也不能修改局部目标本身。

如果 action policy 产生的行动越过了 `allowed_actions`，Loop 不会执行那个行动，而是返回 `EscalationResult`，附上越权原因、需要的权限级别、以及可选的修改提案。

这份提案交给对应的 Graph 治理者决定，而不是由 Loop 自己执行。

### 升级结果（escalation）

这是合同里最容易被忽视的一项，也是让 Loop 保持诚实的最后一道机制。

三种结果的示例含义：

| 结果 | 含义 |
| --- | --- |
| `success` | evaluator 接受当前状态，停止条件触发 |
| `budget_exhausted` | 尝试次数用完，局部目标不变，返回结构化 handoff |
| `escalated` | 行动或需求越过 Loop 权限，交给 Graph 治理者决定 |

`budget_exhausted` 和 `escalated` 都不是失败，它们是 Loop 在能力边界处诚实停止的信号。

---

## 关于确定性函数和 Agent

示例里的 action policy 和 evaluator 都是确定性 Python 函数。它们不是 Agent。

我不想把普通函数包装成 Agent 来让示例看起来更高级——这会掩盖合同结构本身的价值。合同结构的意义在于：**无论节点由函数、工具调用还是 LLM 来履行，runner 的逻辑和停止机制都保持不变。**

当你把 action policy 换成一个调用 LLM 的函数，合同依然成立。evaluator 该在哪里拦截，就在哪里拦截。预算该在哪里耗尽，就在哪里耗尽。升级该在哪里触发，就在哪里触发。

这是合同设计带来的最大好处：可测试性和可替换性是独立的。

**另一个小练习**：把 evaluator 里可接受的 `retry_limit` 上限从 3 改为更严格的 2，保持 action policy 不变，重新运行。观察结果是否从 `success` 变成 `budget_exhausted`，以及 `final_state` 里的 `retry_limit` 值是什么。不需要改动 runner 的任何代码。

---

## Loop 到 Graph 的边界

Loop 负责局部收敛。它不知道，也不应该知道，它的输出会进入哪条下游路径。

当 Loop 结束时，无论是 `success`、`budget_exhausted` 还是 `escalated`，它都返回一份结构化结果。这份结果由更高层的 [Graph Engineering](/zh/docs/tutorials/graph-engineering-guide/) 结构来路由：下一个 Loop 接着运行，还是交给人工审查，还是整个任务目标需要修正。

这个更高层的角色，我在示例里叫做 `graph_governor`。它不是一个框架 API，是一个设计角色——在不同的实现里可以是调度函数、Orchestrator，或者人工节点。

跨 Loop 的依赖、全局目标的修改、多个 Loop 之间的状态同步，都不是单个 Loop 应该处理的。Loop 的局部性正是它的价值来源：它在一个被明确定义的范围内做到最好，然后把边界问题交出去。

无限重试往往是在掩盖一个设计失败：没有人决定这个 Loop 应该管什么，于是它只好一直管下去，直到开发者手动叫停。

把手段、评价、边界和停止分开设计，是让 Loop 从执行态度变成工程对象的核心转变。

---

## 参考来源

- Addy Osmani, *Loop Engineering* (2026)
- Anthropic, *Building effective agents* — [https://www.anthropic.com/research/building-effective-agents](https://www.anthropic.com/research/building-effective-agents)
