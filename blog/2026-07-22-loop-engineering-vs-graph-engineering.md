---
title: "Loop Engineering vs Graph Engineering: Loops Converge, Graphs Govern"
slug: loop-engineering-vs-graph-engineering
description: "Loop Engineering governs local convergence. Graph Engineering makes dependencies, handoffs, vetoes, escalation, and goal authority explicit."
authors: [isaac]
tags: [perspective, future-of-coding, comparison]
keywords:
  - loop engineering
  - graph engineering
  - loop engineering vs graph engineering
  - coding agent architecture
  - multi-agent governance
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline="Loop Engineering vs Graph Engineering: Loops Converge, Graphs Govern"
  description="Loop Engineering governs local convergence. Graph Engineering makes dependencies, handoffs, vetoes, escalation, and goal authority explicit."
  datePublished="2026-07-22"
  dateModified="2026-07-22"
  authorName="Isaac Zhao"
/>

# Loop Engineering vs Graph Engineering: Loops Converge, Graphs Govern

The observation did not start with a term. It started with work.

I was building something with multiple Agents—or what I was calling Agents at the time—and a problem kept surfacing: one overall goal did not map cleanly onto one loop of action and feedback. Different units of work needed different local objectives. They needed different signals to know whether they were converging. They needed different stopping conditions and different answers to the question: *who is allowed to change the goal here?*

The loops were not independent. Some depended on what another produced. Some could block another from proceeding. One unit's partial result could make a previous unit's objective obsolete. What I was actually working with was a graph—I just had not made it explicit. When I later came across the terms **Loop Engineering** and **Graph Engineering** in developer discussion and on X, they named a structure I had already been trying to manage.

That is the order I want to keep: observation first, terminology second.

<!--truncate-->

## Three Things Worth Separating

A lot of confusion in this space comes from using Agent, Loop, and Graph as near-synonyms. They are not.

| Concept | What it describes |
|---|---|
| **Agent** | The actor. Selects and executes actions based on current state. Not a retrieval function or deterministic script—those are graph nodes. |
| **Loop** | How local work converges. A designed system with a local objective, state, actions, feedback or an evaluator, a budget, a stopping condition, an authority scope, and an escalation condition. |
| **Graph** | How work units connect. The structure of dependencies, handoffs, state transfer, vetoes, escalation paths, and authority relationships. |
| **Governor** | The authority that owns a goal or resolves cross-unit conflict. May be a human approval step, a domain owner, or a designated escalation target. |

Addy Osmani's [Loop Engineering](https://addyosmani.com/blog/loop-engineering/) (2026) describes the shift from manually prompting, checking, and iterating to designing that cycle deliberately—with real warnings about unattended errors and token cost. That framing is exactly right: a Loop is an engineering object, not a natural consequence of having an Agent. A work goal is not automatically a Loop, and not every task needs one.

Graph Engineering, as it appears in developer essays from mid-2026, takes the next step: making the relationships *between* loops explicit, typed, and governable. No single canonical definition exists yet, and that is fine—the concept is still being shaped in practice.

## Two Corrections Worth Making Early

### Several loops do not automatically make a Graph.

If you have three loops running sequentially, you have a chain. You know the order. But you do not necessarily know: what state moves between them, who can veto a handoff, what happens when one loop's output makes another's objective contradictory, or who decides when to restart a branch. A linear dependency chain is still a graph mathematically—but a sequence diagram that shows only step order while hiding state and governance semantics is not Graph Engineering. It is a flowchart with extra steps.

### Multiple Agents do not automatically make a Graph.

Agent count and graph topology are separate dimensions. One Agent can traverse a graph serially, moving through nodes one at a time. Several Agents can execute independent branches concurrently. The graph describes *what connects to what and how*—not how many actors are moving through it. Graph nodes can also be functions, scripts, tools, evaluators, or human approval gates. Treating "multi-Agent" and "graph-structured" as equivalent collapses a distinction that matters when things go wrong.

## Where Loops End and the Graph Takes Over

An engineered Loop has real authority within its scope: it can adjust its own actions, shift bounded tactics, and surface a proposed goal change. What it does not own is the final decision on that change. That belongs to the relevant governor.

This matters because it means the Loop is not a closed world. In this model, every Loop has an escalation condition—a threshold at which it stops trying to converge locally and hands the question upward. The Graph is the structure that carries those escalation paths. It holds the dependency edges, the veto relationships, the handoff contracts, and the authority scopes.

A few distinctions that are easy to blur in practice:

- **Hard veto** stops a downstream unit from proceeding until a condition is resolved.
- **Soft objection** flags a concern but does not block execution.
- **Suggestion** is advisory with no enforcement.

These are not the same. Treating them as equivalent when designing a multi-loop system tends to produce authority confusion at the worst possible moment—when two units produce contradictory outputs and something has to give.

Governance can be distributed. Different domains can own different goal-change authority. Cross-domain conflicts escalate to a designated owner. The Graph makes those escalation paths explicit rather than leaving them implicit in whoever happens to respond first.

## The Graph Does Not Replace the Loop

This is probably the most important thing to say clearly.

Graph Engineering is not a new iteration of Loop Engineering. The Graph does not replace the Loop. What Graph Engineering does is make the *relationships between loops* into engineering objects—things that can be typed, tested, versioned, and reasoned about.

Dependencies and conflicts between loops often get discovered during work rather than before it. You build the first loop, then the second, and then you notice that the second's feedback signal invalidates something the first was converging toward. Graph Engineering's argument is that those relationships should become explicit before they surprise you in production—not because you can always anticipate them, but because making them explicit gives you somewhere to put them when you do find them.

The emergence of this framing—and the fact that search suggestions now surface an explicit Loop vs. Graph comparison—reflects something real about where multi-Agent development practice is heading. The question is increasingly about what governs the loops.

## A Map for Orientation

If you are building with Coding Agents, the layers look roughly like this:

**Prompt → Context → Memory / Skills → Harness → Loop → Graph**

- **Prompt** is the immediate instruction.
- **Context** is what the Agent can see right now.
- **Memory and Skills** are what persist or can be loaded across invocations.
- **Harness** is the scaffolding that manages the Agent's execution environment.
- **Loop** is the designed feedback cycle that governs local convergence.
- **Graph** is the structure that connects loops, carries dependencies, and governs authority.

Each layer has its own engineering concerns. Collapsing them—treating a prompt as a loop, or treating a sequence of loops as a graph—makes it harder to reason about failures when they occur.

This article is an introduction. The full treatment of how to design Loops and Graphs, what governance structures look like in practice, and how to move from a prompt to a governed multi-loop system is in the [**Coding Agent Engineering Hub**](/docs/agent-engineering/).

## Sources

- Addy Osmani, [Loop Engineering](https://addyosmani.com/blog/loop-engineering/) (2026)
- iii, [Loops, Graphs, and the Layer That Matters](https://iii.dev/blog/loops-graphs-and-the-layer-that-matters/) (2026)
- Josh C. Simmons, [We Are Entering the Graph Engineering Phase](https://www.drjoshcsimmons.com/writing/we-are-entering-the-graph-engineering-phase) (2026)
- arXiv 2604.11378, [From Agent Loops to Structured Graphs](https://arxiv.org/abs/2604.11378) (2026)
- Juejin, [AI 又又造词，Graph 就又要替代 Loop 了？](https://juejin.cn/post/7664063148857442347) (2026)
