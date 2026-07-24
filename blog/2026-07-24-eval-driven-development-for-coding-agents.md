---
title: "Eval-Driven Development for Coding Agents: One Passing Test Is Not Enough"
slug: eval-driven-development-for-coding-agents
description: "One passing Agent run is one trial, not reliability. Turn real failures into cases, graders, repeated trials, and executable quality gates."
authors: [isaac]
tags: [perspective, future-of-coding]
keywords:
  - eval-driven development
  - coding agent evals
  - agent evaluation framework
  - coding agent quality gate
  - agent evals
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline="Eval-Driven Development for Coding Agents: One Passing Test Is Not Enough"
  description="One passing Agent run is one trial, not reliability. Turn real failures into cases, graders, repeated trials, and executable quality gates."
  datePublished="2026-07-24"
  dateModified="2026-07-24"
  authorName="Isaac Zhao"
/>

# Eval-Driven Development for Coding Agents: One Passing Test Is Not Enough

On 2026-07-23 I watched a Codex CLI 0.145.0 turn complete correctly. Five tool calls, the right diagnosis, a final status of `completed`. I had preserved the bounded JSONL event stream from the observability work I'd been doing — the recorded tool calls, their results, and the two failed attempts along the way before the Agent reached the correct diagnosis. It was a satisfying run to look at.

And then I realized I had exactly zero evidence about tomorrow.

That trace explains one path through one turn on one day. It cannot tell me whether swapping the model version will regress that behavior, whether adding a new Skill to the loadout will cause a misfired tool, whether a prompt tweak to the harness will change how the agent approaches similar tasks. One successful run is not a regression test. It is evidence from one trial.

That gap is where Eval-Driven Development begins.

<!--truncate-->

---

## What a Passing Test Actually Covers

I am not arguing that unit tests are obsolete. That would be absurd. A deterministic test that asserts a function returns the correct value is still doing exactly what it was written to do. It covers the outcome it was written to check, and it will keep covering that outcome reliably every time you run it.

The problem with coding agents is that the thing you're trying to verify isn't a function. It's a behavior-under-construction that calls tools in sequences that can vary, produces outputs that can be semantically correct but structurally different, and can succeed or fail for reasons that have nothing to do with your code. Your unit test checks whether the final patch compiles and passes assertions. It doesn't check whether the agent touched files it shouldn't have. It doesn't check whether it completed the task in twelve tool calls when three would have been correct. It doesn't check whether the Skill it loaded gave it misleading context that happened to not matter on this particular input.

The event stream from my Codex turn contained two failed tool calls inside a run that ultimately succeeded. Those failures did not prevent the Agent from completing correctly. But they made the next question obvious: if I change anything upstream, how do I know whether that recovery behavior is preserved, degraded, or accidentally improved? I have no executable contract for it.

A passing test tells me the outcome was acceptable once. An eval tells me whether a change is acceptable now.

---

## From One Run to a Case

The vocabulary shift matters here, not because I'm asserting a universal standard but because the distinctions are actually useful engineering concepts once you're building with agents.

Anthropic's January 2026 agent eval guide draws a clear line between several things I had been conflating. A **task** defines inputs and success criteria. A **trial** is one attempt at that task. A **grader** checks one aspect of outcome or behavior. A **trace** is the preserved execution record. An **Eval Harness** runs tasks, collects trials, invokes graders, and aggregates results. A **suite** is a collection of tasks that defines what "working" means for a capability.

What I had from the observability work was a trace. It was valuable for understanding what happened. But a trace plus a judgment contract becomes an eval case. That's the step I hadn't taken.

The case I extracted from that read-only diagnosis looks like this: given the task, the Agent should identify `ZeroDivisionError`, mention the `ValueError("at least one value")` guard, modify no files, and stay within local tool-call ceilings. Those are separately gradeable criteria. The Agent might identify the error and still violate the tool-call budget. Or it might stay within budget but touch a file during a read-only task. Those are different failures with different causes, and a single pass/fail outcome hides which one you're dealing with.

---

## The Specific Failures That Become Cases

Let me be concrete about the kinds of behaviors that should become eval cases in a coding agent workflow, because "eval your agent" is useless advice without examples of what you're actually grading.

**Correct patch, unauthorized files.** The agent produces a patch that fixes the bug and passes all assertions, but it also modified a config file that was out of scope for the task. Your existing test suite passes. Your eval case catches this because the grader checks the file-change manifest, not just the test results.

**Correct answer, excessive tools.** The agent solves the problem but makes nine tool calls when the task is tractable in three. This is a latency and cost signal on top of being a behavior signal. If a Skill or prompt change causes this to regress, you want to catch it before it hits production workloads.

**Skill misfire.** You added a new Skill to the loadout that's relevant to one class of tasks. On a different class of tasks, the agent loads that Skill anyway and the retrieved context misleads it into attempting an irrelevant approach. This failure mode doesn't show up if you're only running the tasks the Skill was designed for.

**Regression on trial two.** The agent succeeds on the first trial. You feel good. You run it again and it fails on a slightly different phrasing of the same instruction. Agent behavior varies. One trial is not a reliability claim. The multi-trial requirement isn't pessimism — it's just how non-determinism works. Anthropic explicitly recommends multiple trials for Agent variability, while OpenAI's current evaluation guidance recommends comparing runs and continuously expanding evals.

---

## The Outcome-First Rule

One mistake I made early was treating the specific sequence of tool calls in a successful trace as the thing I was trying to preserve. If the agent used `read_file` then `grep_search` then `write_to_file` in that order, I felt like a different order was a regression.

It isn't. The outcome is what matters.

When you write a grader for an agent task, you check whether the patch is correct, whether the files are in scope, whether the task is complete. You don't force the agent to replay one historical command sequence when another valid path exists and produces the same result. Locking the eval to a specific tool order turns it into a brittle implementation test that will fail every time the model updates its internal reasoning, even when the outcome is fine.

This is the outcome-first rule: define success at the level of what was accomplished, not how it was accomplished. Build in behavioral graders — tool-call budget, file-change scope, forbidden-action checks — as separate graders layered on top of the outcome grader. Keep them distinct so you know which one fired when a trial fails.

---

## The Failure-to-Case Loop

The practical workflow for Eval-Driven Development isn't a one-time setup. It's a loop that you run continuously as the agent changes.

**Observe.** Something fails in a way you didn't expect, or a trace shows a behavior you want to preserve. You have a candidate case.

**Curate.** Not every failure is worth an eval case. You're looking for failures that are reproducible, that represent a real capability you need, and that have success criteria you can actually specify. The two failed tool calls in my Codex trace weren't worth curating — they were recovery steps inside a successful run. A case where the agent produced an incorrect patch on a specific class of refactoring task would be worth curating.

**Grade.** Write the grader. Code-based graders are fast, deterministic, and cheap. Model-based graders can handle semantic correctness checks that are hard to express as code but introduce their own variability and cost. Human graders are authoritative but don't scale. Pick the right tool for each criterion.

**Run candidates.** When you have a proposed change — new model, new Skill, new prompt, new harness configuration — run the suite against it. Multiple trials per task. Compare against the baseline.

**Gate.** Turn the result into a decision. A quality gate doesn't require every trial to pass; it requires the suite to meet whatever reliability threshold you've defined for that capability. If it doesn't, the change is blocked. This is where the eval stops being a dashboard metric and becomes an actual enforcement mechanism.

**Add new failures.** When something fails in production or in testing in a way you didn't have a case for, add it. The suite grows from real failures. That's the part that makes it useful over time.

---

## What This Is Not

Eval-Driven Development for coding agents is not the same as four adjacent things that often get conflated with it.

**Observability** preserves execution evidence for debugging and understanding. It is a valuable source of real eval cases, but a trace without a grader is not an eval. The Codex turn I preserved was observability. This article is about the next step.

**Agent Skills testing** verifies that a Skill retrieves relevant context or formats instructions correctly. That's a unit concern for the Skill itself. EDD operates at the task level, where the Skill is one component of a larger behavior.

**AI Code Review** checks the output of agent-generated code for correctness, style, and security. It's downstream of the agent run and doesn't assess the agent's behavior during the run. EDD includes output graders but also grades process behaviors that code review doesn't see.

**Public model benchmarks** measure model capabilities on standardized tasks using standardized evaluation protocols. They're useful for model selection but they don't tell you how a model behaves on your tasks, in your harness, with your Skill loadout, against your success criteria. A benchmark score is not a substitute for testing that specific system.

---

## The Local Tutorial: Keep It Executable

The most useful thing I can point you toward is a local implementation that avoids vendor lock-in and stays executable. OpenAI deprecated its Evals platform on 2026-06-03; existing evals become read-only on 2026-10-31, and the dashboard and API are scheduled to shut down on 2026-11-30. This is a product-surface decision, not a judgment on eval methodology. But it does make a strong argument for owning your eval infrastructure rather than depending on a hosted dashboard.

The local tutorial I'm building toward for the Coding Agent Evals Guide uses three things:

**Plain JSONL for cases.** In the local teaching fixture, each line has a `case_id`, a `task`, and an `expect` object containing the outcome checks and local policy ceilings. It is a project-local schema, not an official standard. You can open it with ordinary tools, version-control it alongside your code, and diff it when cases change.

**Deterministic graders where possible.** A grader that checks whether a file path is in a permitted set doesn't need a model. It needs a set membership test and a boolean return. Write that in whatever language your harness runs in. Reserve model-based graders for the criteria that genuinely require semantic judgment — and document that they introduce variability.

**Process exit codes for the gate.** The local script evaluates supplied normalized trials and exits `0` if all pass, `1` if any evaluated trial fails, and `2` if the input is invalid. Your CI system doesn't need to understand evals — it just needs to see a non-zero exit code. Repeated-trial thresholds can be added later, once enough trials exist to justify them.

AWS published an attributed production Agent evaluation blueprint on 2026-07-23 using Strands and AgentCore that shows how these pieces can compose at a larger scale. I'm not going to generalize their thresholds or cost figures to your situation — those are specific to their workload. The local tutorial implements only the narrower dataset-and-gate seam.

---

## Where This Leaves Me

The preserved Codex turn is still useful. It's evidence that the agent can complete that specific task correctly. The two failed tool calls inside it are interesting behavioral data. The trace is a good starting point for a case.

But it's one trial. It cannot answer whether tomorrow's agent — different model version, different Skill loadout, different harness configuration — produces the same outcome. It cannot block a regression. It cannot tell me whether the recovery behavior I observed is reliable or lucky.

Eval-Driven Development begins when I extract the case from that trace, write the grader, run it across multiple trials, and build a gate that enforces the result. It continues every time a new failure becomes a new case.

The practical implementation — JSONL cases, deterministic checks, exit-code gates, and a path toward repeated trials — is what the [Coding Agent Evals Guide](/docs/tutorials/coding-agent-evals-guide/) covers next. One article explains why. The next one shows how.
