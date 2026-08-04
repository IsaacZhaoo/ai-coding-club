---
title: "AI Agent System Design Interview Guide"
description: "Practice AI Agent system design through evolving constraints across context, tools, state, loops, graphs, permissions, and verification."
keywords:
  - AI Agent system design interview
  - Agent architecture interview
  - LLM system design
  - AI Agent 系统设计面试
  - Agent 架构
sidebar_position: 29
tags: [tutorial, career, agent-engineering, architecture]
---
# AI Agent System Design Interview: Context, Tools, Loops, Graphs, and Permission Boundaries

---

## Exercise

> **Teaching exercise (synthetic prompt — not attributed to any company)**
>
> Design an agent that can accept a repository task, read code, call tools, and return verifiable evidence of its actions.

Before you reach for components, read the prompt again. It's missing almost everything that matters: who initiates the task, whether the input is ambiguous, how success, refusal, and escalation are each defined, which tools are available, which actions are read-only, which carry write side effects, which require approval or can be rolled back, which events must be reconstructable after a failure, and what verification would be sufficient to accept a release.

When faced with an open-ended prompt like this, jumping straight to components — "LangGraph plus memory plus an MCP server" — tends to unravel under follow-up questions. The components are present, but there's no explanation of how they handle specific failure modes.

The approach here is: **first complete the prompt into a constraint contract, then derive the architecture layer by layer**. Every component introduced must answer which constraint it addresses, who owns it, how failures surface, and how behavior is verified.

---

## The Decision Chain: The Core Model Running Through Every Round

A persuasive system design answer lets every engineering decision be traced to a chain:

```text
Constraint
  → Decision
  → Owner / Component
  → Failure Mode
  → Evidence
  → Trade-off / Known Limit
```

This chain transforms "we need memory" into: **what constraint drives the memory decision? who manages retrieval and retention policy? how does a stale memory failure surface? what evidence verifies it? what does introducing memory cost?**

Component names are useful as handles for discussion, but the answer also needs responsibility boundaries, failure paths, and verifiable evidence. Listing names alone has no design value.

Here is a reusable answer template that runs through all seven rounds:

| Constraint | Decision | Owner | Failure Mode | Evidence | Trade-off |
|---|---|---|---|---|---|
| `[real constraint from the prompt]` | `[design decision]` | `[model / harness / tool / state / runtime / human]` | `[reachable failure]` | `[trace / eval / audit / diff / runtime signal]` | `[cost and residual risk]` |

---

## Step One: Complete the Constraint Contract First

Before designing anything, clarify the questions that actually shape architecture:

**User and task layer**: who initiates the task, is the input format fixed, how are success, refusal, and escalation each defined? Is partial completion allowed?

**Time, scale, and quality layer**: single-turn or long-horizon? Is the primary pressure on request volume, task length, tool calls, concurrency, or state? What are the budgets for latency, cost, failure, and human intervention?

**Environment, data, and side-effect layer**: where do code, private data, external services, network, and credentials live? Which actions are read-only, which carry write side effects, which require approval, and which can be rolled back?

**Evidence layer**: which events must be reconstructable when something goes wrong? What eval, audit, or runtime signal is required before a release is acceptable?

When the prompt is under-specified, the right move is to state reasonable assumptions and explain how the design would shift if those assumptions change. For example: "If the task is read-only diagnosis, the architecture can stay small, with focus on task contract, context selection, source references, completion criteria, and trace. Write access is the trigger for extending tool enforcement, rollback, and approval paths."

The seven rounds below apply progressively tighter constraints to the same synthetic exercise system.

---

## Reference Architecture (Working Model)

```text
Task Contract
  → Harness / Orchestrator
      ├─ Context Builder ← Memory / Durable Instructions
      ├─ Task State / Checkpoint Store
      ├─ Model / Action Policy ← Provider Boundary
      ├─ Tool Gateway → Sandbox / External Services
      ├─ Evaluator / Stop Guard / Retry Policy
      └─ Approval / Governor / Handoff
  → Structured Result

Trace / Audit covering critical paths
Eval / Rollout checking outcome, critical trajectory, and regression
```

This is the article's teaching working model; implementation terminology varies across teams. Every node in the diagram requires a decision chain. Listing names without describing responsibility boundaries has no design value.

---

## Four Technical Boundary Groups: Getting These Right Matters

### 1. Model / Provider / Harness / Framework

These four terms are frequently conflated, but their responsibilities are distinct:

- **Model**: produces judgments, plans, or candidate actions from the current context. What's in context shapes what the model can reason about; the tool gateway, runtime policy, and authority scope determine what the system is actually allowed to execute. Model visibility and execution authority are separate things.
- **Provider**: supplies model access and inference-service capabilities and limits. The provider boundary determines which API features are available and which limits the harness must handle.
- **Harness**: in this article's working model, the harness owns the organization of context, tools, state, control flow, permissions, and verification.
- **Framework** (LangGraph, AutoGen, and so on): an implementation choice. Naming a framework does not allocate responsibility for any of the above.

Saying "I'd use LangGraph to manage this flow" and stopping there is roughly equivalent to saying "I'd use Python to solve this problem." It describes a tool; it doesn't describe an engineering decision.

### 2. Context / Memory / State

- **Context**: the information actually visible in a single model call. The window is finite, and what you select is a core engineering judgment.
- **Memory**: information retained and retrieved across calls or sessions. It requires explicit scope (who can see it), provenance (source and trustworthiness), retention (how long it persists), and staleness policy (what happens when it expires).
- **State**: the authoritative record of task progress, executed actions, results, checkpoints, and control decisions. State is the basis for recovery; a stale memory is not the same failure as a lost state.
- **Durable Instructions**: stores relatively stable rules and policies; when loaded, they become a source of rules in context.

*These are the article's working definitions, not a universal industry taxonomy.*

### 3. Tool / MCP / Runtime Enforcement

A tool contract covers more than its schema: it also needs to specify semantics, error behavior, idempotency (whether an action is safe to retry), and side-effect scope (write boundaries). Runtime enforcement is carried out by authorization checks, approval flows, policy guards, and sandboxing. Fixtures and evals test tool implementation and behavior, but they cannot replace runtime execution interception.

MCP standardizes tool interaction protocols and description formats. It does not automatically provide authorization control, containment, business-semantic validation, or side-effect governance. Tool annotations in the current MCP specification — such as `readOnlyHint` — are hints. Permissions are enforced by runtime enforcement; the two responsibilities are different, and relying on hints as a security boundary is a mistake worth actively checking for.

### 4. Loop / Graph / Parallelism

This article describes a loop with eight fields: **aim** (what problem this loop is solving), **state** (the record of current task status, executed actions, evaluation results, and remaining budget), **action policy** (selects the next action based on current state and evaluator or environment feedback), **evaluator** (holds an evaluation contract separate from the executor — it can be implemented as a deterministic check, a rule, another model, or a human review), **budget** (the maximum number of iterations or cost), **stopping condition** (the specific conditions that trigger termination), **authority scope** (limits the actions, resources, and goals the loop is allowed to touch), and **escalation** (the handoff path when budget or authority scope is exceeded). The runner executes the control contract: it invokes the action policy, applies the evaluator and stopping condition, consumes budget, checks authority and escalation, and returns a structured outcome. The next action is proposed or selected by the action policy.

The graph working model in this article manages dependency, routing, merge, veto, approval, and governor relationships between units of work. Nodes in the graph can be agents, functions, tools, evaluators, or approval steps. Parallelism is justified by branches the dependency graph shows can run independently. Increasing agent count alone does not establish isolation or merge authority — it expands the risk surface. Git worktrees isolate the linked working tree's Git state. Ports, databases, caches, temporary files, credentials, and external resources still require separate isolation.

---

## Seven Rounds of Constraint Evolution: How One System Grows

### Round 1: Read-Only Diagnosis

**Constraint added**: the agent may only read repository contents, return a structured diagnostic report, and must not modify any files.

| Constraint | Decision | Owner | Failure Mode | Evidence | Trade-off |
|---|---|---|---|---|---|
| Read-only; output is a diagnostic report | Define task contract with explicit success / refusal / escalation criteria | harness | Task goal is ambiguous; agent returns an unverifiable "complete" | Structured outcome, source references, basic trace | Stricter contract reduces flexibility in handling edge-case input |
| Model cannot see the full codebase | Context builder selects only relevant file fragments; completion criteria determine whether output satisfies the task contract | harness | Missing context, incorrect references, missing completion criteria so task completion cannot be judged | Source reference compared against outcome; completion-condition check records | More context improves coverage and raises token cost and noise |
| Need to distinguish model judgment from harness control | Explicitly separate model, provider, and harness responsibilities | harness / provider adapter | Framework name is treated as the answer; responsibility boundaries are lost | Harness logs are independent of model output | Layering adds implementation complexity but reduces debugging blind spots |

At this round the architecture can stay small. Focus belongs on a clearly defined task contract, traceable context selection, source references that can be compared against the structured outcome, and trace coverage of call paths. Tool enforcement, rollback, and approval paths are only needed after write access is introduced.

---

### Round 2: Small Code Changes

**Constraint added**: the agent may make small changes to files within a designated scope, but must provide a diff and validation results.

The moment write access is introduced, three things must be in place simultaneously: **allow scope** (explicitly specifying which paths may be modified, enforced by the harness before tool execution), **idempotency** (the tool contract declares whether an action is safe to retry, and a rollback point is saved before any write), and **runtime validation** (after a write, the harness runs lint, compile, or tests, and saves the results as a diff and tool event).

These three layers — allow-scope boundary definition, runtime authorization checks, and fixture-and-eval behavior verification — have different responsibilities and cannot substitute for one another. Writing outside the allow scope, or performing an automatic retry on a non-idempotent action after a partial side effect, are the most direct failure paths in this round. The trade-off: a narrower allow scope is safer but reduces flexibility at boundaries; rollback points add storage and state complexity; more complete runtime validation costs more time.

---

### Round 3: Multi-Turn Task Approaching the Context Limit

**Constraint added**: the task requires multiple turns to complete, and a single context window cannot hold all historical information.

This round exposes the cost of conflating context, memory, and state.

**Context selection** (Constraint: window is finite; Owner: harness): load only the information the current decision actually needs; excess history does not enter context. The failure path is that critical information is truncated and the model proceeds on wrong premises. Evidence is the context diff compared against the trace and outcome. Trade-off: tighter selection lowers cost but may drop needed historical fragments.

**Memory** (Constraint: historical information is needed across turns; Owner: harness): stores retrievable history and long-term information, with provenance and staleness policy. The failure path is stale memory causing incorrect recovery, or expired information corrupting new decisions. Evidence is memory provenance records and staleness checks. Trade-off: memory retrieval adds latency and complexity; without provenance, historical information is difficult to audit.

**State** (Constraint: task must be recoverable after interruption; Owner: harness): stores the authoritative task progress and checkpoints, maintained separately from memory. The failure path is that lost state prevents resumption from a checkpoint, and restarts repeat side effects. Evidence is state transition logs and resume records. Trade-off: the state store requires its own persistence and consistency guarantees.

Key engineering judgment: treating conversation history as the authoritative task state (the conversation-as-state anti-pattern) causes inconsistent state on recovery after interruption. Stale memory and lost state are two distinct failures and need separate detection and recovery paths.

---

### Round 4: Automatic Correction After Failed Validation

**Constraint added**: the agent may automatically attempt correction after a validation failure, but there must be a limit and an exit path.

This round introduces a bounded loop. All eight fields must be defined for the loop to remain controllable. **Aim** is fixed to correcting a specific class of validation failure; broadening it to "make the task complete" loses the local boundary. **State** records the current task status, executed correction actions, evaluation results, and remaining budget — the basis for recovery and audit. **Action policy** selects the next correction action based on current state and evaluator or environment feedback. **Evaluator** holds an evaluation contract independent of the executor — completion judgment cannot rely solely on the executor's self-report. The evaluator can be implemented as a deterministic check (lint passes, tests pass), a rule, another model, or a human review. Only when an additional model or service is used does the corresponding inference cost apply; a deterministic evaluator carries implementation and maintenance cost but no additional inference overhead.

**Budget** and **stopping condition** together determine when to exit: budget is the hard ceiling (maximum attempts or cost); stopping condition is the specific trigger (evaluator passes, budget exhausted, a particular error state reached). **Authority scope** limits the actions, resources, and goals the loop is allowed to touch. Modifying the task goal under retry pressure — changing the aim definition so the evaluator will pass — is a scope violation. **Escalation** fires when budget is exhausted or authority scope is breached, producing a structured handoff that prevents silent task failure. The runner executes the control contract: invokes the action policy, applies the evaluator and stopping condition, consumes budget, checks authority and escalation, and returns a structured outcome.

Retry preconditions check whether an action is idempotent and whether its side effects can safely be redone. Automatically retrying a non-idempotent action creates duplicate side effects and state inconsistency; the loop must exit into an approval or escalation path. Evidence includes attempt traces, evaluation records, and budget and escalation outcomes.

---

### Round 5: Independent Subtasks That Need to Run in Parallel

**Constraint added**: the repository contains several mutually independent modules that need to be examined or modified at the same time.

Draw the dependency graph first; decide on parallelism after. Schema-migration ordering, hard dependencies, a debugging scenario where the root cause is unknown, or an undefined merge authority are all reasons to default to serial execution.

Once independent branches are confirmed, isolation has two requirements: git worktrees isolate the linked working tree's Git state, but ports, databases, caches, credentials, and external resources still require separate isolation. Using only worktrees without handling runtime resources leaves real gaps in isolation.

The merge phase requires an explicit governance policy. For this exercise scenario, the working model specifies one: a designated merge authority holds the final decision; nodes may issue a hard veto (blocks the merge) or a soft objection (recorded but does not block); the governor triggers escalation on veto or abnormality. This is the article's example policy — teams may use different names — but any policy must answer: who has merge decision authority, what conditions block the merge, and what triggers escalation.

The core trade-off of this round: greater parallelism may reduce wait time while also expanding the scope of side effects, isolation cost, merge complexity, and the burden of combined verification. Parallelism is justified by branches the dependency graph shows can run independently; adding agents without dependency analysis, isolation, merge authority, and combined verification expands the risk surface rather than managing it. Evidence includes dependency records, branch contracts, base commits, handoff records, and the combined merge and verification result.

---

### Round 6: High-Risk External Tools

**Constraint added**: certain tools need to access external services, execute system commands, or handle sensitive credentials.

Least authority is the starting point: each tool receives only the minimum permission needed to fulfill its declared responsibility. Credential scope follows the tool contract and task responsibility — it is not granted wholesale to an agent identity. The failure path is credential leakage or permission scope that exceeds the actual need; evidence is permission check records and audit logs.

High-risk actions trigger an approval flow before execution (Owner: harness and human). The approval being bypassed, or the agent executing an action that was never approved, are the direct failure forms here; evidence is approval records and denied-action traces.

Allowlist validation must check the full invocation — arguments, cwd, configuration, and side effects — not just the command name. Checking only the command name permits argument-driven or cwd-driven scope violations. The effective boundary of a sandbox depends on the actual isolation mechanism, workspace-write controls, host trust boundaries, credential handling, and reachable resources. The name alone cannot prove the boundary is effective; missing these checks leave security blind spots. Evidence is security eval cases and host access logs.

Trade-off: fine-grained permission control adds configuration complexity; complete allowlist validation has higher maintenance cost; approval adds latency, and which actions require approval must be defined in advance so the approval path does not become a production bottleneck.

---

### Round 7: Preparing for Real-User Delivery

**Constraint added**: the system must run in a real-user environment with latency, cost, and reliability requirements, and must support rollback.

**Observability** (Constraint: events must be reconstructable at failure time; Owner: harness and infra): deploy trace and telemetry covering critical paths, and actively identify telemetry gaps — paths with insufficient instrumentation. A failure with no information to locate the root cause makes debugging depend on guesswork. Evidence is a trace coverage report and a telemetry gap list. Trade-off: more complete tracing adds storage cost and data-processing load.

**Eval system** (Constraint: quality regressions must be detected; Owner: harness and eval pipeline): design the eval suite outcome-first; trajectory constraints should cover only safety- and quality-critical paths. Overly granular trajectory constraints lock in accidental execution paths and flatten real differences between models and APIs into the lowest common denominator. The evaluation contract is separate from the execution policy and can provide check evidence beyond the executor's self-report; an evaluator can be deterministic checks, rules, another model, human review, or a combination. Evidence uses case and trial results, suite results, gate decisions, and regression records. All success-rate targets use `[target]` placeholders — no values are assumed.

**Rollout and rollback** (Constraint: budget overruns and quality regressions must be controllable; Owner: harness and infra): design rollout (gradual staged release), fallback (degraded path), and rollback signal (the conditions and thresholds that trigger rollback). SLO, cost, and baseline all use `[target]` / `[budget]` / `[actual record]` placeholders. Without real measurement data, establish the measurement mechanism first, then make budget decisions. Trade-off: excessive provider abstraction provides replaceability at the cost of flattening real model and API differences into the lowest common denominator; excessive trajectory constraints have the same flattening effect.

---

## Trade-offs Must Be Specific

Three core trade-offs running through all seven rounds, with the conditions that would change each decision:

**Context and Memory**: both provide information coverage and cross-turn continuity, while also introducing noise cost, provenance management, retention policy, and staleness risk. **Condition for change**: if the task is single-turn and input is already well-structured, reducing memory layers lowers complexity. If the task spans multiple sessions, the memory staleness policy becomes a critical design decision.

**Autonomy and Parallelism**: greater autonomy and more parallelism may reduce wait time while expanding the scope of side effects, isolation cost, merge complexity, and combined verification burden. **Condition for change**: schema-migration ordering, hard dependencies, a debugging scenario where the root cause is unknown, or an undefined merge authority all favor serial execution.

**Trajectory Constraints and Provider Abstraction**: both provide control or replaceability; overuse can lock in accidental execution paths or flatten real model and API differences into the lowest common denominator. **Condition for change**: with only one provider, the abstraction layer adds cost and reduces benefit. Trajectory constraints have a clear basis only when a safety-critical path has an explicit pass/fail definition.

---

## Design Traps Worth Checking While You Answer

These traps have appeared across the seven rounds. They're listed here as a checklist:

**Framework-first**: picking a framework before requirements are clear, letting the framework name substitute for an explanation of harness responsibilities. Frameworks are implementation choices; architecture questions come first.

**Conversation-as-state**: using conversation history as the authoritative task state. Conversation history may be incomplete, inconsistent, and unable to support checkpoint recovery. State requires separate maintenance.

**Schema-as-permission**: treating a tool schema or MCP annotation (such as `readOnlyHint`) as an authorization mechanism. Schema describes structure; permissions are enforced by runtime enforcement. The two responsibilities are different and cannot substitute for each other.

**Executor self-grading**: relying entirely on the executor's own report of whether the task is complete. An evaluation contract separate from the execution policy can provide evidence beyond self-report; the evaluator can be deterministic checks, rules, another model, human review, or a combination.

**Unbounded retry**: no budget, no stopping condition, no escalation path. The loop continues consuming resources without progress, or modifies its aim under pressure to make the evaluator pass.

**Parallel-everything**: treating agent count as the source of parallelism, without dependency analysis, isolation mechanisms, merge authority, or combined verification.

**Sandbox-without-checks**: claiming isolation based on the component name alone, without workspace-write controls, host trust verification, or reachable-resource auditing. The blind spots remain.

**Final-answer-only**: returning only a conclusion without saving trace, audit, diff, or eval records. When something goes wrong, there is no way to reconstruct the event sequence.

---

## Relevant Role Responsibilities (Preparation Reference)

The following role responsibilities are drawn from public job descriptions and are included to show which preparation dimensions this article covers. They reflect only the relevance of public responsibilities and do not represent real interview questions, processes, or scoring criteria.

- **OpenAI AI Systems Engineer, Codex Agents**: focuses on harness, execution loop, sandbox, orchestration, evals, observability, and production reliability.
- **OpenAI Applied AI Engineer, Codex Core Agent**: focuses on real-world tasks, prompt and tool and context experimentation, failure analysis, and feedback loops.
- **Anthropic Research Engineer, Model Evaluations**: focuses on designing evaluations of agentic behavior, hardening the distributed eval execution platform, debugging anomalous eval results to distinguish model changes from harness/data/infrastructure issues, and improving eval tooling.
- **LangChain Deployed Engineer, Early Career / LangChain Fullstack Software Engineer, Applied AI**: focuses on multi-step workflow, orchestration, failure handling, monitoring, evaluation pipeline, and communicating architectural decisions.
- **Cognition Applied AI Engineer / Sierra Software Engineer, Agent**: focuses on MCP integration, production agent workflow, agent lifecycle, and continuous iteration.

---

## Further Reading

### Official Job Postings

- [OpenAI, AI Systems Engineer, Codex Agents](https://jobs.ashbyhq.com/openai/de06790a-7243-4e33-a6f1-e7bd34009588)
- [OpenAI, Applied AI Engineer, Codex Core Agent](https://jobs.ashbyhq.com/openai/577e6673-0a4a-491b-9a0d-facbdd3bdf3c)
- [Anthropic, Research Engineer, Model Evaluations](https://job-boards.greenhouse.io/anthropic/jobs/5198255008)
- [LangChain, Deployed Engineer, Early Career](https://jobs.ashbyhq.com/langchain/0f35c8e1-9318-411d-929b-04c60e6d8522)
- [LangChain, Fullstack Software Engineer, Applied AI](https://jobs.ashbyhq.com/langchain/c75915ba-a32b-4e17-873d-19b47564170d)
- [Cognition, Applied AI Engineer](https://jobs.ashbyhq.com/cognition/811c3f5a-b26d-4162-b49b-93890a91794d)
- [Sierra, Software Engineer, Agent](https://jobs.ashbyhq.com/sierra/631848ec-1a74-4067-8b9f-cd04a71aab6d)

### Official Technical Sources

- [Anthropic, Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [Anthropic, Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [MCP, Tools specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)
- [Git, git-worktree documentation](https://git-scm.com/docs/git-worktree)
- [OpenTelemetry, Traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [OpenAI, Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)

### AI Coding Club Learning

- [Agent Engineering Hub](/docs/agent-engineering/)
- [Coding Agent Harness](/docs/tutorials/coding-agent-harness-explained/)
- [Coding Agent Memory](/docs/tutorials/coding-agent-memory/)
- [MCP Tool Design](/docs/tutorials/mcp-tool-design-guide/)
- [Loop Engineering](/docs/tutorials/loop-engineering-guide/)
- [Graph Engineering](/docs/tutorials/graph-engineering-guide/)
- [Parallel Agents With Worktrees](/docs/tutorials/parallel-coding-agents-worktrees/)
- [Coding Agent Sandbox Security](/docs/tutorials/coding-agent-sandbox-security/)

---

## Continue the AI Agent interview series

- [Interview Hub](/docs/tutorials/ai-agent-interview-guide/)
- [Portfolio](/docs/tutorials/ai-agent-portfolio-guide/)
- [System Design](/docs/tutorials/ai-agent-system-design-interview/)
- [Failure Analysis and Evals](/docs/tutorials/ai-agent-failure-analysis-evals-interview/)
