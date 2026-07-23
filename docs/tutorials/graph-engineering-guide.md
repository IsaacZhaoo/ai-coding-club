---
title: "Graph Engineering Guide: Coordinate Coding Agent Work with Dependencies and Governance"
description: "Design a Coding Agent Graph with explicit dependencies, serial and parallel execution, typed signals, merge rules, escalation, and governor authority."
keywords:
  - graph engineering
  - coding agent graph
  - agent orchestration
  - multi-agent workflow architecture
  - AI agent governance
sidebar_position: 18
tags: [tutorial, coding-assistant, agent-engineering, graph-engineering]
---

# Graph Engineering Guide: Coordinate Coding Agent Work with Dependencies and Governance

---

When I finished the [Loop Engineering Guide](/docs/tutorials/loop-engineering-guide/), I thought the hard part was over. A Loop gave me local convergence: a bounded work unit with its own aim, feedback, budget, stopping conditions, and escalation path. One Loop, one job.

Then I tried to apply the same thinking to something real. I was coordinating several work units inside Loops — context preparation, implementation, testing, review, and approval — and each unit had developed its own local aim, its own evaluator, its own sense of when it was done. But they were not independent. They depended on each other's outputs. They had opinions about each other's outputs. One unit could stop another entirely.

That structure is not a Loop. A Loop owns bounded local convergence. What I was looking at owns explicit **relationships among work units**: who waits on whom, what state passes between them, who can object, who can veto, and who has final authority. When those relationships become engineering objects — when you give them names, types, and rules — you have a Graph.

**Graph Engineering** is what you do when you make those relationships explicit.

> *Graph Engineering makes relationships between work units explicit: the same topology may be traversed serially by one Agent or executed concurrently by several workers, while typed signals and governors decide what may merge, stop, escalate, or change the goal.*

This tutorial picks up exactly where the Loop Engineering Guide left off.

---

## The Problem That Loops Cannot Solve

A Loop is good at one thing: converging on a local aim within budget. It takes an action, observes feedback, decides whether to continue or stop. That is the right abstraction for a single, bounded job.

It is the wrong abstraction for managing the relationships between jobs.

In my Loops work, I noticed a pattern. The implementation Loop finished its job, but the tests Loop needed the implementation's output before it could start. The review Loop needed both the implementation and the test results. The merge step needed the review to pass. The approval step needed the merge to succeed — but it also had broader authority to reject the whole thing or change the goal entirely.

I had five or six Loops, each internally coherent, and the coordination between them was living entirely in my head, in documentation, or in ad-hoc code that nobody had formally reasoned about. The step order was visible. The state transfers, the objection rules, and the authority boundaries were not.

More Agents do not solve this. Calling five independent Agents does not make a Graph. Several Agents can still share no formal dependency structure, still pass state as loose dictionaries, still have no typed signals for objection or veto, still have no governor with authority to change the goal. Agent count is not architecture.

A Graph is architecture. It makes the relationships the thing you design.

---

## Show the Topology First

Here is the topology I use in the working example. Read it before anything else:

```text
context
  -> implementation Loop
       -> tests -----\
       -> review -----> merge -> approval governor
```

[Download the verified Loop and Graph example](/examples/loop-graph-engineering-example.zip). It includes the runner, topology, demos, and all 12 behavior tests.

Six nodes. Some run in sequence. `tests` and `review` are independent of each other once implementation finishes — they can run in parallel. Both must complete before `merge`. `merge` feeds into an `approval` governor node that holds final authority.

The `GraphDefinition` captures this:

```python
@dataclass(frozen=True)
class GraphDefinition:
    aim: str
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]
    governor_node: str | None = None
```

Every edge carries a type. In this example the types are `dependency`, `handoff`, `data_flow`, `veto`, and `approval`. These are not universal categories — they are the types that emerged from this particular topology. Different graphs will need different edge types. In this runner, every edge contributes a readiness dependency. The relation label records why the connection exists, while signals implement veto and escalation behavior.

The `aim` is the Graph-level goal. The `governor_node` names the node that holds authority over decisions that exceed any individual Loop's scope.

---

## Run It Before You Explain It

The fastest way to understand the Graph is to run it in both modes and compare the results.

```python
graph = build_feature_change_graph(approve_change)

serial   = run_graph(graph, ExecutionMode.SERIAL)
parallel = run_graph(graph, ExecutionMode.PARALLEL)
```

Try this now:

```bash
python3 graph_demo.py
```

Serial execution processes nodes one batch at a time. The batches are:

```text
(('context',), ('implementation',), ('tests',), ('review',), ('merge',), ('approval',))
```

Parallel execution identifies independent nodes and runs them in the same batch. The batches become:

```text
(('context',), ('implementation',), ('tests', 'review'), ('merge',), ('approval',))
```

`tests` and `review` are now in the same batch. That is not a configuration choice — it is derived directly from the edge definitions. Neither `tests` nor `review` depends on the other, so the executor puts them together.

Both modes produce the same merged output state in this deterministic example:

```python
{
    "retry_limit": 3,
    "validation_added": True,
    "tests_passed": True,
    "review_status": "ok",
}
```

The topology and the worker count are **separate dimensions**. The topology is defined once in `GraphDefinition`. The mode is a runtime choice. You can change from serial to parallel — or back — without touching the Graph definition. The execution mode decides *how many things run at once*; the edge set determines readiness, while the relation labels document the intended relationship.

The parallel executor uses Python standard-library worker threads. They are workers, not Agents. An Agent selects and executes actions based on state. A worker thread in this executor just picks up a ready node and runs it. The distinction matters: calling threads Agents would suggest they have decision-making authority they do not have.

---

## Follow State Through the Graph

Walk through what each node does to the shared state.

**context** runs first, alone. In this example it records `compatibility_required: True` and `max_retry_limit: 3`. Its output is stored in the shared outputs before implementation becomes ready. Context is a deterministic function here, not a Loop, and this small handler does not inspect project files or history.

**implementation** is a Loop. It runs after context, although this demo handler does not read the context output. It executes the retry-feature contract, and its `LoopResult` carries the final state `retry_limit: 3` and `validation_added: True`. It also has the *ability* to propose a goal change if it encounters something that exceeds its authority — but it cannot apply that change itself. That matters; I will come back to it.

**tests** and **review** both become ready after implementation. The tests node reads the implementation `LoopResult` and records whether its outcome is `success`. Review emits the configured signal together with a `reviewed` marker; this deterministic demo does not inspect real code quality or compatibility. Neither knows what the other is doing while they run. When both complete, their outputs arrive at merge.

**merge** collects the state from both. In this example the merge logic is straightforward: it combines `tests_passed` from the tests node and `review_status` from the review node, and then decides whether to proceed. Merge is not a passive join; it is the place where you encode the merge rule. You can make merge conditional, weighted, or veto-sensitive.

**approval** is the governor node. It receives the merged state and makes a final decision. It has authority that none of the preceding nodes have.

---

## Signals: Feedback Strength and Routing

One of the things I found genuinely unsatisfying about earlier coordination code was that "feedback" was always binary: pass or fail. But real review is not binary. A reviewer might have a concern that is not a blocker. A test might fail in a way that should stop the pipeline entirely. An implementation Loop might encounter a constraint it cannot resolve on its own authority.

Typed signals make feedback strength and routing explicit.

| Signal | Behavior |
|---|---|
| `ok` | Continue through dependencies normally. |
| `soft_objection` | Preserve the concern, allow merge to proceed, surface it to the governor. |
| `hard_veto` | Stop before merge and approval. |
| `escalation` | Route directly to the governor when the Loop lacks authority. |
| `approve` | Keep the current Graph aim. |
| `reject` | End with a rejected outcome. |
| `change_goal` | Apply a new Graph aim supplied by the governor. |

**`ok`** is the silent path. Nothing special happens; dependencies run on schedule.

**`soft_objection`** is the most interesting signal in practice. The review node has a concern — maybe a style issue, maybe a compatibility note — but it does not believe the concern is severe enough to block the merge. It emits `soft_objection`. The merge proceeds. But the concern is preserved in state and presented to the governor at the approval step. The governor now has full information: the implementation succeeded, the tests passed, the merge completed, *and* there was a concern at review. The governor decides what to do with that.

This is a different design from blocking on every objection. It preserves reviewer judgment without giving the reviewer veto power they did not need for this concern.

**`hard_veto`** is the opposite. The review node finds something that must not merge: a security issue, a breaking change that violates a contract, a dependency that introduces an unacceptable risk. `hard_veto` stops the graph before merge. Approval never runs. The graph result records the veto.

**`escalation`** routes to the governor without going through merge at all. This is the signal for "I, as a Loop, have encountered something that exceeds my authority. I am not failing; I am forwarding this decision upward."

Run the full test suite to see all signals behave:

```bash
python3 -m unittest discover . -p 'test_*.py'
```

**Exercise:** In the demo, find where the review node emits its signal. Change it from `OK` to `SOFT_OBJECTION`. Run the demo again and inspect `result.outputs` — does `merge` appear? Does `approval`? Then change it to `HARD_VETO`. Does `merge` appear now?

This single change reveals whether your merge and approval logic correctly reads and respects the incoming signal. It is a minimal but real integration test of your signal routing.

---

## Why Loops Cannot Approve Their Own Goal Changes

This is the authority boundary that I kept tripping over before I formalized it.

A Loop has a local aim. It also has a feedback cycle, which means it observes results and can update its plan. But what happens when the feedback is not "try again differently" — what happens when the feedback is "the aim itself is wrong"?

In my working example, there is a verified scenario where the implementation Loop encounters a compatibility constraint during its work. It forms a proposal: *replace the compatibility requirement with a migration requirement instead*. That is a significant goal change. It is not an implementation detail.

The Loop does not apply this change. It cannot. A Loop that could unilaterally change the Graph aim would undermine the entire coordination structure. Other nodes were designed to pursue the current aim. Tests were written against it. The review node is evaluating work against it. If the implementation Loop changes the aim without authority, the rest of the graph is now running against an aim no one agreed to.

So the Loop emits an `escalation` signal and presents its proposal to the governor.

The injected governor in the test receives that proposal and returns `CHANGE_GOAL` with a new aim: `Add bounded retries and provide a migration path.` The graph records this, updates the aim, and produces the result `goal_changed`.

The governor applied the change. The Loop proposed it. That distinction is the authority boundary.

This matters because authority is not just about who runs the code. It is about who has the information and the mandate to make a particular class of decision. The implementation Loop has deep knowledge of the code. It does not have knowledge of the product roadmap, the compatibility contracts with other teams, or the release strategy. The governor has broader context. Goal changes belong to the governor.

---

## Graph Audit: What You Need Before You Ship

When I hand a Graph definition to someone else — or return to one after a few weeks — I run through a short checklist. These are the things that are most often underspecified.

**Nodes**

- Does every node have a name and a type? Is that type documented?
- Does every node have a clear output contract? What keys does it write to shared state?
- Is it clear whether each node is a Loop, a deterministic function, a tool, an evaluator, or a human approval step?

**Edges**

- Does every edge have a type? Do you know what that type means — what it allows, what it blocks?
- Is there a `governor_node` named if any node emits `escalation` or `change_goal`?
- Are all dependencies listed? Is there an implied dependency that is not in the edge list?

**Readiness**

- Can the topology executor compute a valid batch order from the edge definitions?
- Do serial batches and parallel batches produce the same final state on a deterministic example?

**State**

- Is the shared state schema defined? Do you know which nodes read which keys, and which nodes write which keys?
- Is there a merge function for nodes whose outputs overlap?

**Signals**

- Does every node that can emit `soft_objection`, `hard_veto`, or `escalation` have a test for each case?
- Does merge correctly read the incoming signal before deciding whether to proceed?
- Does the governor node cover `approve`, `reject`, and `change_goal`?

**Authority**

- Is there exactly one governor node (or none, for a fully deterministic graph)?
- Is it clear which decisions belong to individual Loops and which require governor authority?
- Can any node unilaterally change the Graph aim? If yes, that is a design error.

If you cannot answer one of these questions by reading the `GraphDefinition`, the `GraphNode` definitions, and the edge list, the Graph is underspecified. Add it there, not in documentation that lives somewhere else.

---

## What This Is and What It Is Not

Graph Engineering is a practitioner term for a recognizable practice: making relationships among work units explicit, giving them types, and building execution and governance on top of that definition. It is not a canonical standard or an established job title. Different teams will name their edge types differently. Different topologies will call for different governor designs.

What I found reliable across all the variations I worked through: the topology and the worker count are separate. The signals and the authority boundary have to be explicit. A Loop that proposes a goal change is functioning correctly. A Loop that applies a goal change has exceeded its authority.

The Graph becomes visible when the relationships become the engineering problem. Design the relationships first.

---

## Primary Sources

- Anthropic. *Building effective agents*. Anthropic Documentation, 2024. Covers orchestrator-worker patterns and parallelization strategies.
- Anthropic. *How we built our multi-agent research system*. Anthropic Engineering, 2025. Multi-agent coordination and delegation patterns.
- Masterman, T., Besen, S., Sawtell, M., & Chao, A. (2024). *The Landscape of Emerging AI Agent Architectures for Reasoning, Planning, and Tool Calling: A Survey*. arXiv:2404.11584.
- Wei, H. (2026). *From Agent Loops to Structured Graphs: A Scheduler-Theoretic Framework for LLM Agent Execution*. arXiv:2604.11378. (Position paper and design proposal; not production evidence.)
- The Loop Engineering Guide. *This series, preceding article.*
