---
title: "Coding Agent Engineering: From Prompt to Graph"
description: "Follow the coding-agent engineering stack from prompts and context to memory, skills, harnesses, loops, graphs, security, and review."
slug: /agent-engineering
keywords:
  - coding agent engineering
  - agent engineering tutorial
  - prompt to graph
  - coding agent architecture
  - agent loop and graph
---

# Coding Agent Engineering: From Prompt to Graph

A useful Coding Agent starts with a prompt, but reliable repository work quickly becomes a larger engineering problem. The system must choose context, retain the right information, expose capabilities, control permissions, iterate against feedback, and coordinate work that no longer fits inside one local loop.

This page is the map for AI Coding Club's Agent Engineering tutorials. It is organized by responsibility, not by product and not as a mandatory course ladder.

If the Loop and Graph terminology brought you here, start with [Loop Engineering vs Graph Engineering](/blog/loop-engineering-vs-graph-engineering/). The article explains why Agent count, local feedback loops, and graph topology are different design dimensions.

## The main layers

| Layer | The question it owns | Start here |
|---|---|---|
| Prompt | What do I want the model to do now? | [Prompt Engineering 101](/docs/prompt-engineering-101/) |
| Context | What information should enter this task? | [The Power of Context](/docs/course/foundations/power-of-context/) — foundation lesson |
| Memory | What should persist, and what should expire? | [Coding Agent Memory](/docs/tutorials/coding-agent-memory/) |
| Instructions | Which repository rules should always apply here? | [AGENTS.md Guide](/docs/tutorials/agents-md-guide/) |
| Skills and tools | Which reusable procedures, event controls, and external connections are available? | [Claude Code Skills, Hooks, and MCP](/docs/tutorials/claude-code-skills-hooks-mcp/), then [Agent Skills Testing](/docs/tutorials/agent-skills-testing-guide/) |
| Harness | How are context, tools, permissions, memory, execution, and verification assembled around the model? | [Coding Agent Harness Explained](/docs/tutorials/coding-agent-harness-explained/) |
| Loop | How does one bounded unit of work improve through feedback and know when to stop or escalate? | [Loop Engineering Guide](/docs/tutorials/loop-engineering-guide/) |
| Graph | How do work units exchange state, run serially or concurrently, veto actions, and govern goal changes? | [Graph Engineering Guide](/docs/tutorials/graph-engineering-guide/) |
| Parallel execution | How do independent Agent tasks isolate checkout state, runtime resources, evidence, and merge authority? | [Parallel Coding Agents with Worktrees](/docs/tutorials/parallel-coding-agents-worktrees/) |

The layers are related, but they do not replace one another. Better context does not remove the need for a Harness. A Graph does not replace the Loops inside it. Adding more Agents does not automatically create a Graph.

## Assurance across every layer

Some responsibilities cut across the whole stack:

- [Coding Agent Sandbox Security](/docs/tutorials/coding-agent-sandbox-security/) explains what execution boundaries protect and where host trust can still escape them.
- [AI Code Review Workflow](/docs/tutorials/ai-code-review-workflow/) explains how to turn requirements, diffs, tests, and residual risks into an evidence-backed merge decision.
- [Coding Agent Observability](/docs/tutorials/coding-agent-observability-guide/) explains how to preserve tool failures, retries, Token usage, handoffs, and explicit telemetry gaps.
- [Coding Agent Evals](/docs/tutorials/coding-agent-evals-guide/) turns preserved traces into local cases, deterministic checks, and executable CI gates.

## Where to begin

- New to AI-assisted coding: begin with Prompt and Context.
- Already using terminal Agents: continue through Memory, Instructions, Skills, and Harness.
- Designing unattended or multi-step systems: continue with [Loop Engineering](/docs/tutorials/loop-engineering-guide/), then [Graph Engineering](/docs/tutorials/graph-engineering-guide/).
- Preparing for AI Agent roles: use the [AI Agent Engineer Interview Guide](/docs/tutorials/ai-agent-interview-guide/) to turn these layers into an interview capability map and a project-evidence plan.

The durable question is not which new label wins. It is which responsibility your system has made explicit—and which one is still hidden inside the Agent's behavior.
