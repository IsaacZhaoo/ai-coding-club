---
title: "AI Agent Failure Analysis and Evals Interview"
description: "Use traces to separate tool, turn, and task failures, test root-cause hypotheses, and turn confirmed failures into eval cases and regression gates."
keywords:
  - AI Agent failure analysis
  - AI Agent eval interview
  - Agent trace debugging
  - LLM evals interview
  - AI Agent 故障分析
  - Agent 评测面试
sidebar_position: 30
tags: [tutorial, career, agent-engineering, evals]
---
# AI Agent Failure Analysis and Evals Interview: From Traces to Regression Gates

---

Start with these four lines:

```
tool: python  → exit 127
tool: python3 → exit 1 / ZeroDivisionError
tool: read source → exit 0
turn: completed
```

This is a key event fragment from a controlled diagnostic task. The task contract: run a focused unit test, read the minimum relevant source, diagnose the precise cause, make no file changes throughout, and state the failure behavior and minimum fix direction in one sentence.

The complete record contains 5 tool calls — 3 successful, 2 failed. The final answer correctly identifies that an empty list triggers division by zero, and gives the expected minimum fix direction: a `ValueError("at least one value")` guard.

**How many times did the agent fail?**

Before answering, ask yourself which layer you are judging. Are you looking at whether a single tool event completed according to protocol, at how the controlling turn ended, or at whether the entire task contract was satisfied? Different layers can produce different answers simultaneously, and none of them alone is sufficient to prove any of the others. Collapsing all three into one "success rate" hides exactly the layer information you need for failure localization.

---

## Separating the Three Result Layers

| Layer | What is being judged | This case |
|---|---|---|
| Event / Tool | Whether a single call completed per protocol | 2 command items are failed |
| Turn / Run status | How the client-controlled turn ended | `turn.completed` |
| Task outcome | Whether the task contract was satisfied | Determined jointly by diagnostic content, the write prohibition, and a task-specific grader |

`turn.completed` only says that the controlling turn ended normally. On its own it is not sufficient to establish that the answer is correct, that constraints were obeyed, or that the user's goal was met. `exit 127` says the `python` launcher was not found in the current environment. Two things are simultaneously true: the `python3` launcher was available, the test reached the application layer and exposed the exception — and the diagnostic process continued. `exit 1` is the tool process return code; it is also the valid application-behavior evidence this diagnostic task needed. Without it, the test behavior would be invisible.

This means child tool failure and parent task failure require independent judgment. Exit code, span status, turn status, and task outcome each record their own meaning. No single one of them can substitute for the other three.

---

## Reconstructing the Visible Timeline

The complete record contains 17 events, 5 tool calls, and 4 agent messages. Stepping through each:

| Step | Action | Result | What it supports |
|---|---|---|---|
| 1 | Locate rules and focused test | exit `0` | Confirms read-only constraint and test contract |
| 2 | Read rules and test | exit `0` | Test expects `ValueError("at least one value")` |
| 3 | Run focused test with `python` | exit `127` | `python` launcher unavailable in current environment |
| 4 | Retry same test with `python3` | exit `1`, `ZeroDivisionError` | Launcher available; test reached application layer and exposed exception |
| 5 | Read `calculator.py` | exit `0` | Implementation directly executes `total / len(values)` |
| 6 | Return one diagnostic sentence | turn `completed` | Answer identifies division by zero and minimum guard; task outcome still requires grader |

The `python3` execution has no explicit `retry_of` field in the raw record, and there is no native parent-linked span hierarchy. But the tool call order and agent messages together support this reading — it is **Derived**, inferred from evidence, and distinct from a directly **Recorded** field.

### Recorded, Derived, and Unavailable

The first thing to do with any trace is to partition the evidence:

- **Recorded**: thread id, turn events, item id, agent messages, full command content, aggregated output, exit code, item status, turn status, token usage.
- **Derived**: `python3` is a retry following `python`'s failure, supported by event order and agent messages.
- **Unavailable**: event timestamp, duration, dollar cost, handoff event, skill-load event, model field, explicit parent / retry relation.

Unavailable fields must remain blank. There is a fundamental difference between a field being absent from a record and the underlying event never having occurred — the former is a collection boundary, the latter requires independent evidence. You cannot infer from a missing field that an internal action never happened, nor can you estimate duration or cost. The current record can answer token usage but cannot answer duration, dollar cost, or explicit handoff / parent / retry relation. If your analysis depends on those fields, the next action is to improve collection, not to fill gaps with estimates.

---

## Using a Failure Taxonomy to Generate Hypotheses

When failure appears, declaring a root cause immediately skips the verification step. Use a classification framework to generate candidate hypotheses first, then test each one against the evidence.

The relevant layers in this case:

**Runtime / Infrastructure**: The most direct explanation of `exit 127` is that the `python` binary is absent in the current environment. This is a direct failure at the runtime / environment layer. The agent's choice to call `python`, the tool policy configuration, and the harness configuration may also have contributed — these upstream candidates remain hypotheses to be verified and cannot yet be confirmed or excluded from the current record.

**Tool**: `python3`'s `exit 1` is a tool process result and simultaneously application failure evidence. `ZeroDivisionError` is a runtime exception, an application-layer error, not a tool-protocol error.

**Requirement / Product**: The focused test expects `average([])` to raise `ValueError("at least one value")`. In the current source implementation, `average([])` directly executes `total / len(values)` with a zero divisor, triggering `ZeroDivisionError` — the missing entry guard creates a measurable gap between implementation and what the focused test requires.

**Observability Gap**: Duration, dollar cost, handoff event, and explicit parent / retry relation are unavailable. When you ask "how much time or cost did this diagnostic run consume" or "did the model experience internal retries," the current record cannot answer. This gap is itself something that needs to be recorded separately, with a decision about whether improving collection is worth the cost.

Laying out these layers serves one purpose: confirming which claims already have record support, which are merely correlational, and which require new evidence before the analysis can advance.

---

## The Distance from Symptom to Root Cause

The easy move for an analyst is to see `ZeroDivisionError` and announce that "the model didn't handle the edge case." That involves two leaps: first, attributing a runtime exception to model reasoning; second, declaring a mechanism without consulting the source. The correct sequence:

1. **Narrow the reproduction**: input is `average([])`, environment is a read-only ephemeral sandbox, expected behavior per the focused test is `ValueError("at least one value")`, actual behavior is `ZeroDivisionError`.
2. **Identify the direct mechanism**: reading `calculator.py` confirms the implementation is `total / len(values)` with no pre-check for an empty list. Source code is direct evidence.
3. **Test alternative hypotheses**: Was the test itself wrong? The focused test explicitly expects `ValueError("at least one value")`; the task prompt asks to run the test, diagnose the cause, stay read-only, and give a minimum fix — both have clear and separate roles. Did an environment problem cause execution to fail? The `python3` launcher was available, the test reached the application layer and exposed the exception, and that command item ended with exit `1` / failed. The launcher issue no longer blocks symptom reproduction at this point; the source explains the current exception; independently confirming that the test represents the true product contract would require separate requirements evidence.
4. **Minimum fix direction**: add `if not values: raise ValueError("at least one value")` before `total / len(values)`. This direction comes from the focused test's expected behavior; the task prompt asks for a minimum fix direction, not for the fix to be applied.
5. **What remains unverified**: this run is read-only, the fix was not applied, and the proposed fix was not tested in this run. The article can explain the fix direction, but that fix remains unconfirmed by any test in this run.

---

## Encoding a Confirmed Failure as an Eval

Failure analysis is complete when the failure scenario has been turned into a regression detection case that can be triggered automatically on the next configuration change.

### Five Levels

| Concept | Working definition | This case |
|---|---|---|
| Case | Freezes input, environment, success contract, and grading requirements | Diagnose `average([])`, no file modifications allowed |
| Trial | One attempt by a specific configuration on one case | The saved Codex diagnosis baseline |
| Grader | Maps trial evidence into results | Checks answer, turn, tool budget, unexpected writes |
| Suite | Multiple cases / graders organized around one capability | Grown continuously from historical failures, edge conditions, and safety scenarios |
| Gate | Applies predeclared suite results to continue, block, or require human review | Can feed into CI, release, or rollout decisions |

### Turning This Trace into a Case

**Case definition**: input is `average([])`, environment is a read-only ephemeral sandbox, the task contract requires the answer to include the failure cause (division by zero) and minimum fix direction (guard for empty list), no files may be written, and total tool calls must not exceed the case policy limit.

**Baseline trial**: the saved controlled diagnostic record passes the current teaching gate; CLI exit `0`.

**Grader dimensions**:

- Does the answer contain "division by zero" or an equivalent description?
- Does the answer give a minimum fix direction?
- Is turn status `completed` rather than `incomplete` or error?
- Is the total tool call count within budget?
- Are there any unexpected writes (violation of the read-only constraint)?

Each dimension is recorded independently and not merged into a single aggregate score. The grader can itself become a failure layer — substring answer checking is the minimum viable deterministic check for this controlled teaching case, sufficient to distinguish a correct diagnosis from a wrong answer here, but not representative of full semantic grading capability.

### Teaching Value of Three Comparison Trials

**Baseline**: the saved record passes all grader checks against the current teaching gate.

**Synthetic wrong-fix**: if the answer proposes returning `0` for an empty list, the `answer_contains_all` check fails, the gate rejects it, and the CLI exits `1`. This shows the grader can reject this specific wrong answer; substring checking, as a minimal deterministic check, has inherent limits in its semantic discrimination capacity.

**Cleaner candidate**: if a configuration reaches the correct answer and obeys all constraints using only 3 tool calls and 0 failed tools, it also passes the gate. The grader does not require reproducing the baseline's failure path. This is the outcome-first principle directly in action: what is being evaluated is the user-visible result, not the historical trajectory.

---

## Repeated Trials, Suite, and Gate

Passing one case in one trial is not sufficient evidence that a capability is stable. Model output varies across runs, and environment conditions vary too.

**Repeated trials**: repetition count is predeclared based on risk, variance, and cost, using `[actual trial count]` as a placeholder. Each trial starts from a clean isolated state with the following frozen: case, repository / base commit, environment, agent / model / harness configuration, tools / skills, permissions, network, budget, and reset rules.

**How a suite grows**: cases are added from real task distributions, historical failure logs, edge conditions, safety paths, and high-cost scenarios. Edge and safety scenarios carry equal weight alongside happy paths. For this diagnostic case, the next candidate cases could include: input `average([0])` (single-element list — is returning 0 correctly described?), input containing non-numeric elements (TypeError path), and an agent attempting a file write that gets blocked (constraint check).

**Predeclaring a gate**: the gate's hard veto conditions (for example, unexpected writes are an immediate veto), acceptable threshold (for example, in `[actual trial count]` trials, results meet the predeclared `[gate threshold]`), gray zones requiring human review, and evidence retention requirements are all declared before the run. Gate results guide continue, block, or human review decisions; the standard is set before the run and not adjusted afterward.

**After deployment**: retain rollout, fallback, rollback, and monitoring signals. Latency, token, cost, error, and human intervention are recorded only from real exposure. Missing fields are recorded as `N/A`, not estimated. One run's data is not extrapolated to characterize typical performance.

---

## Seven Responsibility-Derived Teaching Exercises

The following seven exercises are derived from recurring responsibilities in public job listings and the teaching content above. They are categorized as responsibility-derived teaching exercises and are not attributed to any specific company or real question bank.

---

**Exercise 1**

> Two tool events failed in the trace; the final turn completed. How do you determine task outcome?

**Analysis observations**

First confirm what the task contract defines as success — is it answer content, functional result, constraint compliance, or all three simultaneously? Do the failed tool events have a parent scope capable of absorbing their impact? In this case, `exit 127` was superseded by the availability of `python3`; the diagnostic process continued, and the diagnostic conclusion could still hold. `turn.completed` indicates the controlling turn ended — on its own it is not sufficient to establish success on any task dimension. The final judgment requires a task-specific grader, and when residual uncertainty cannot be eliminated, human review is the last check.

---

**Exercise 2**

> The final answer looks reasonable, but the current record only shows `turn.completed`. What additional evidence is needed?

**Analysis observations**

`turn.completed` is a control state expressing that the turn ended, not a quality result. What still needs to be confirmed: task outcome (does the answer satisfy the contract?), constraint compliance (was the read-only constraint enforced, did tool calls stay within budget?), and artifact integrity (were any files written, are any steps missing?). Before a grader has been calibrated against counterexamples and human judgment, the combination of a final answer and `turn.completed` is still not sufficient to establish overall correctness.

---

**Exercise 3**

> The trace is missing duration, cost, handoff, and parent relation. How do you proceed?

**Analysis observations**

Classify each field as Recorded, Derived, Inferred, or Unavailable; do not estimate unavailable fields. Advance the analysis using available evidence, while recording which questions cannot be answered from the current trace. The telemetry gap is itself an action item: assess the cost and value of improving collection and decide whether to enable more complete instrumentation in the next run. Whether a field is missing and whether analysis can continue are two independent judgments. The gap must be recorded, not ignored.

---

**Exercise 4**

> After context compression, stale state is used intermittently. How do you localize the cause?

**Analysis observations**

Obtain one context snapshot from before the failure and one from after, then compare memory provenance — from what point in time was the state the agent used compressed? Can authoritative state be reconstructed after compression? Design a control trial: turn off compression and check whether the failure disappears. Then run an ablation: gradually reduce compression ratio and observe the failure threshold. Repeated trials are necessary to distinguish random variation from a systemic problem. A single failure reproduction is not sufficient to confirm root cause.

---

**Exercise 5**

> Design a grader that allows different valid paths while blocking unauthorized writes.

**Analysis observations**

Check outcome first: answer content, functional result, and constraint compliance are scored separately and not merged. Negative side-effect checking (unexpected writes) gets its own hard veto — one strike and out, not averaged into a weighted score. Trajectory constraints apply only to safety-critical paths; they do not lock in command order or tool count. Validate the grader with counterexamples: feed in a trial with a correct answer but a file write — the grader should reject it. Feed in a trial with an incorrect answer but zero writes — the grader should fail it for answer quality, not for path. The grader itself needs calibration; a grader's false positives and false negatives are an independent failure layer.

---

**Exercise 6**

> How do you turn a production failure into a persistent gate?

**Analysis observations**

The first step is reproduction in an isolated environment: confirm input, environment, configuration, and task contract. Once reproduction succeeds, freeze the failure as a case with a corresponding grader and record one baseline trial. Then add the case to the suite; the suite should cover variants and edge conditions of this failure and grow continuously rather than serving only as an archive. The gate predeclares hard veto conditions, thresholds, human-review zones, and evidence retention requirements, then connects to CI or release decisions. After deployment, retain rollout signals and monitor for new failures; be ready to rollback at any time. The gate is maintained continuously as the suite grows and the product evolves.

---

**Exercise 7**

> How do you fairly compare two agent configurations?

**Analysis observations**

Freeze all shared fields first: task, base commit, environment, prompt, permissions, budget, reset method, and repetition count. Then record product differences that cannot be eliminated (for example, different tool sets or different models) — these cannot be controlled, only preserved transparently. Record results across multiple independent dimensions: functional outcome, diff / review burden, operational failure rate, permission events, and latency / token / cost each recorded separately, with no aggregate score masking a hard veto. Dimensions with no measured data are recorded as `N/A`, not estimated. `[actual trial count]` and `[retest result]` are kept as placeholders to be filled in after real runs. A public benchmark can serve as a baseline or filter; it cannot predict which configuration performs best on a specific private repository under specific conditions.

---

## Shared Answer Sheet

For any agent failure record, six steps:

```
Reconstruct the visible scope
  → Separate result layers
  → Classify and propose root-cause hypotheses
  → Verify with reproduction, control trials, or ablation
  → Encode confirmed failures as eval cases
  → Hold the line continuously with suites, gates, and rollout signals
```

At each step, answer three questions: what is the recorded evidence? what fields are missing? and what new evidence would overturn the current judgment?

---

## Start Here

Take a real failure record from your own project — it does not need to be complete. Even a single exit code line and a single agent message is enough to try writing out:

1. In this record, what is Recorded, what is Derived, and what is Unavailable?
2. At which layer did the failure occur — event, turn, or task outcome?
3. How many competing root-cause hypotheses can you formulate?
4. What new evidence would eliminate one of them?
5. If you wanted to turn this failure into a regression case, which dimensions would the grader need to check?

These five questions are the path to making failure analysis a practiced skill.

---

## Further Reading

### Official Roles (for preparing relevant dimensions — not representative of actual interview questions or hiring standards)

- [OpenAI, AI Systems Engineer, Codex Agents](https://jobs.ashbyhq.com/openai/de06790a-7243-4e33-a6f1-e7bd34009588)
- [OpenAI, Applied AI Engineer, Codex Core Agent](https://jobs.ashbyhq.com/openai/577e6673-0a4a-491b-9a0d-facbdd3bdf3c)
- [Anthropic, Research Engineer, Model Evaluations](https://job-boards.greenhouse.io/anthropic/jobs/5198255008)
- [LangChain, Deployed Engineer, Early Career](https://jobs.ashbyhq.com/langchain/0f35c8e1-9318-411d-929b-04c60e6d8522)
- [LangChain, Fullstack Software Engineer, Applied AI](https://jobs.ashbyhq.com/langchain/c75915ba-a32b-4e17-873d-19b47564170d)
- [Sierra, Software Engineer, Agent](https://jobs.ashbyhq.com/sierra/631848ec-1a74-4067-8b9f-cd04a71aab6d)

### Official Technical Sources

- [OpenTelemetry — Traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [OpenAI — Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [SWE-bench — Dataset guide](https://github.com/SWE-bench/SWE-bench/blob/main/docs/guides/datasets.md)
- [SWE-bench — Evaluation guide](https://github.com/SWE-bench/SWE-bench/blob/main/docs/guides/evaluation.md)

### AI Coding Club Deep Dives

- [Agent Engineering Hub](/docs/agent-engineering/)
- [Coding Agent Observability](/docs/tutorials/coding-agent-observability-guide/)
- [Coding Agent Evals](/docs/tutorials/coding-agent-evals-guide/)
- [Coding Agent Benchmark](/docs/tutorials/coding-agent-benchmark-guide/)
- [AI Code Review Workflow](/docs/tutorials/ai-code-review-workflow/)
- [Browser Verification](/docs/tutorials/coding-agent-browser-testing/)

---

## Continue the AI Agent interview series

- [Interview Hub](/docs/tutorials/ai-agent-interview-guide/)
- [Portfolio](/docs/tutorials/ai-agent-portfolio-guide/)
- [System Design](/docs/tutorials/ai-agent-system-design-interview/)
- [Failure Analysis and Evals](/docs/tutorials/ai-agent-failure-analysis-evals-interview/)
