---
title: "Graph Engineering 实战：用依赖、并行与治理组织 Coding Agent 工作"
description: "设计一张包含显式依赖、串并行执行、带类型信号、合并规则、升级路径与治理权限的 Coding Agent Graph。"
keywords:
  - Graph Engineering
  - Coding Agent Graph
  - Agent 编排
  - 多 Agent 工作流架构
  - AI Agent 治理
sidebar_position: 18
tags: [tutorial, coding-assistant, agent-engineering, graph-engineering]
---

# Graph Engineering 实战：用依赖、并行与治理组织 Coding Agent 工作

**系列：** [Loop Engineering](/zh/docs/tutorials/loop-engineering-guide/) → **Graph Engineering**（本篇）

---

## 关系开始成为工程对象

做完 [Loop Engineering 教程](/zh/docs/tutorials/loop-engineering-guide/)之后，我以为剩下的事情是"多跑几个 Loop"。结果发现问题并不在 Loop 内部，而在 Loop 之间。

Context 准备需要一个 Loop，但它的局部目标是"把上下文收窄到足够精确"，而不是"实现功能"。实现需要一个 Loop，但它没有测试权限，也不应该自己决定什么时候算完。测试、Review、合并、审批——每一步都有不同的局部目标、不同的停止条件、不同的权限边界。当这些 Loop 开始传递状态、等待依赖、独立运行、提出异议、否决或升级时，一张隐藏的 Graph 才逐渐显现出来。

**Graph Engineering 是把这些关系显式化的实践。** 它不替代 Loop，它描述工作单元之间的拓扑、依赖、状态传递路径、并行机会和权限分配。同一套拓扑可以由一个 Agent 串行遍历，也可以由多个 worker 并行执行；带类型的信号和治理者共同决定哪些结果可以合并、停止、升级或修改目标。

"多个 Agent"不是架构。节点之间的关系才是。

---

## 一张 Graph 长什么样

我用 feature 变更流程作为例子，因为它足够具体，同时每一步的权限分离也足够典型：

```text
context
  -> implementation Loop
       -> tests -----\
       -> review -----> merge -> approval governor
```

[下载经过验证的 Loop / Graph 示例](/examples/loop-graph-engineering-example.zip)。压缩包包含 runner、拓扑、演示入口和全部 12 项行为测试。

这张图里，`context` 是准备节点；`implementation` 是核心实现 Loop；`tests` 和 `review` 是相互独立的验证节点，可以并行运行；`merge` 等待两者完成后合并状态；`approval` 是治理节点，拥有最终决策权，包括修改整个 Graph 的目标。

用代码定义这张 Graph：

```python
@dataclass(frozen=True)
class GraphDefinition:
    aim: str
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]
    governor_node: str | None = None
```

`aim` 是整体目标，不是某个节点的局部目标。`governor_node` 指向审批节点，该节点可以修改 `aim`，而普通 Loop 不能。

边是有类型的：

| 边类型 | 含义 |
|---|---|
| `dependency` | 目标节点等待源节点完成后才能启动 |
| `handoff` | 源节点将状态完整移交给目标节点 |
| `data_flow` | 源节点的输出成为目标节点的输入之一 |
| `veto` | 源节点可以阻断后续节点执行 |
| `approval` | 目标节点具有最终审批或目标修改权 |

这不是通用标准分类，而是我在这个拓扑里用来区分路由语义的一套标记。

---

## 串行与并行是两个独立维度

拓扑决定节点之间的关系。执行模式决定运行时谁在跑这些节点。两者是分开的。

```python
graph = build_feature_change_graph(approve_change)

serial   = run_graph(graph, ExecutionMode.SERIAL)
parallel = run_graph(graph, ExecutionMode.PARALLEL)
```

串行模式下，执行器按依赖顺序逐批运行：

```text
(('context',), ('implementation',), ('tests',), ('review',), ('merge',), ('approval',))
```

并行模式下，没有相互依赖的节点可以同时运行：

```text
(('context',), ('implementation',), ('tests', 'review'), ('merge',), ('approval',))
```

`tests` 和 `review` 都依赖 `implementation` 的输出，但彼此之间没有依赖关系，所以并行模式把它们放进同一批次。并行执行器使用 Python 标准库的线程；这里的 worker 是线程，不是 Agent。

在这个确定性示例里，两种模式产生完全相同的合并状态：

```python
{
    "retry_limit": 3,
    "validation_added": True,
    "tests_passed": True,
    "review_status": "ok",
}
```

这说明拓扑的正确性与执行模式无关。先把关系定义对，再决定用多少 worker 并行。如果拓扑本身有隐藏依赖，并行化会让它更早暴露，而不是掩盖它。

---

## 沿着流程追踪状态

### context

准备节点先运行。当前示例只返回两个约束：`compatibility_required=True` 和 `max_retry_limit=3`，没有读取项目文件或历史。它的输出进入共享 outputs，并让下游 implementation 节点变为可执行。这个节点可以是 Agent Loop，也可以是确定性函数——Graph 不在意。

### implementation

实现 Loop 等待 context 完成后启动，但当前处理器没有读取 context 输出，而是直接运行 retry-feature Loop contract。它有自己的预算和停止条件，但没有权限决定是否合并，也没有权限修改整体 Graph 目标。

当 implementation Loop 遇到超出自己权限的判断时——比如，它判断需要把兼容性要求改成迁移要求——它不能自行执行，只能发出 `escalation` 信号，把决定交给治理者。

### tests 和 review（并行）

`tests` 节点读取 implementation 的 `LoopResult`，记录它是否以 `success` 结束。`review` 节点返回预先配置的 signal 和 `reviewed` 标记；这个确定性示例并没有真正检查代码。`review_status` 由 merge 节点从 review signal 派生。两者在 `implementation` 完成后可以同时启动。

`review` 节点可以输出三种不同强度的信号：
- `ok`：无问题，按依赖继续。
- `soft_objection`：有异议，但不阻断合并，异议保留并交给治理者查看。
- `hard_veto`：严重问题，`merge` 和 `approval` 不得执行。

这三个信号的区分是关键。把所有反馈压缩成"通过/不通过"意味着丢失了"我有保留但允许继续"这个语义，而这恰恰是很多真实 Review 场景里最常见的状态。

### merge

`merge` 节点等待 `tests` 和 `review` 都完成后，把它们的输出合并进整体状态。如果上游有 `hard_veto`，`merge` 不会执行。如果有 `soft_objection`，`merge` 执行但保留异议记录。

### approval（治理者）

`approval` 节点是 governor，它有三种决定：

| 决定 | 行为 |
|---|---|
| `approve` | 保留当前 Graph 目标，以成功结果结束。 |
| `reject` | 以拒绝结果结束，不执行目标变更。 |
| `change_goal` | 应用由治理者提供的新 Graph `aim`，Graph 结果变为 `goal_changed`。 |

`change_goal` 是这里权限设计的核心。Loop 可以发现问题、提出建议、发出升级信号；但只有治理者可以批准并应用新的整体目标。普通节点，包括 implementation Loop，没有这个权限。

---

## escalation 的完整路径

以这个场景为例：`implementation` Loop 在执行过程中判断当前的兼容性约束不足，需要提供完整的迁移路径。这超出了它的局部目标权限——它不能自己决定修改整体 aim，而是发出 `escalation`。

注入的治理者收到升级信号，查看 Loop 的提案：把兼容性要求改成迁移要求。治理者返回 `CHANGE_GOAL`，新目标是：

```
Add bounded retries and provide a migration path.
```

Graph 结果变为 `goal_changed`。整个流程不是"Loop 决定了什么"，而是"Loop 提出了什么，治理者决定了什么"。

这个边界很重要。如果 implementation Loop 可以自行修改 Graph 目标，那么 approval 节点就失去了意义，整个权限设计就崩塌了。

---

## 信号是路由，不只是状态

把这些信号汇总在一起：

| 信号 | 来源 | 路由结果 |
|---|---|---|
| `ok` | 任意节点 | 按依赖继续执行 |
| `soft_objection` | review | 保留异议，允许 merge，交治理者查看 |
| `hard_veto` | review | 停止 merge 和 approval |
| `escalation` | implementation | 跳过剩余 Loop 迭代，直接交治理者 |
| `approve` | governor | 以成功结果结束 |
| `reject` | governor | 以拒绝结果结束 |
| `change_goal` | governor | 应用新 aim，结果为 `goal_changed` |

信号的价值在于它们把"发生了什么"和"接下来怎么走"都编码进了同一个对象。在当前实现里，边是否存在决定节点何时就绪，`EdgeRelation` 记录关系意图，`hard_veto` 和 `escalation` 等提前路由则由 `SignalKind` 处理。

---

## 读者操作

运行示例：

```bash
python3 graph_demo.py
python3 -m unittest discover . -p 'test_*.py'
```

**一个小练习：** 修改 `review` 节点的输出，把默认的 `OK` 改成 `SOFT_OBJECTION`，观察 `result.outputs` 里是否还出现 `merge` 和 `approval` 的输出，以及 `review_status` 如何被传递给治理者。再把 `SOFT_OBJECTION` 改成 `HARD_VETO`，观察 `merge` 和 `approval` 是否从输出中消失。

这个练习的目的是让你亲手感受三种信号强度的路由差异——不只是读到它，而是在输出里看到它。

---

## Graph 审计：一张清单

一个可用的 Graph 定义应该能够回答这些问题：

| 审计项 | 检查内容 |
|---|---|
| **节点** | 每个节点的局部目标是什么？它是 Agent Loop、确定性函数、evaluator 还是人工审批？ |
| **边** | 每条边的类型是什么？dependency、handoff、data_flow、veto 还是 approval？ |
| **就绪条件** | 每个节点启动前需要哪些前置输出？ |
| **状态** | 节点输出哪些键进入共享状态？下游节点消费哪些键？ |
| **信号** | 每个节点可以发出哪些信号？对应的路由行为是什么？ |
| **合并** | merge 节点如何处理冲突的上游输出？`soft_objection` 是否被保留？ |
| **权限** | 哪个节点是 governor？只有 governor 可以修改 `aim`。其余节点没有这个权限。 |

这张清单不是为了让你填表，而是为了让你在设计时不遗漏权限边界。遗漏权限边界是 Graph 设计里最常见的问题：节点和节点数量都对，但某个节点悄悄做了它不该做的决定，治理者形同虚设。

我对"只有步骤顺序、没有状态和决策权"的工作流没什么信任。步骤的顺序解决不了 Review 提出异议之后怎么办，解决不了 implementation 发现范围超限时谁来拍板，也解决不了测试通过但 Review 认为设计有根本问题时流程应该走向哪里。这些都需要信号、边类型和权限分配——也就是 Graph。

---

## 一手来源

- Anthropic, *Building effective agents*, 2024. 介绍了 orchestrator-worker 模式和 parallelization 场景，是本文并行执行讨论的背景参考。
- Kapoor et al., *AI Agents That Matter*, arXiv 2407.01502, 2024. 关于 Agent benchmark 与评估设计的研究，提示评估成本与控制变量的重要性。
- Wang et al., *A Survey on Large Language Model based Autonomous Agents*, arXiv 2308.11432, 2023. Agent 架构概览，涵盖规划、记忆与工具使用的分类框架。
- Qian et al., *Experiential Co-Learning of Software-Developing Agents*, arXiv 2312.17025, 2023. 多 Agent 协作开发场景，讨论角色分工与迭代机制。
- arXiv 2604.11378（立场论文与设计提案）。本文拓扑与治理合同是有光综合多篇来源后的独立判断，不以此论文作为生产效果证明。

---

*本文是 Loop Engineering 系列的直接延续。如果你还没有读过 Loop Engineering 教程，建议先建立局部收敛的基础概念，再回到这里理解 Graph 层的关系设计。*
