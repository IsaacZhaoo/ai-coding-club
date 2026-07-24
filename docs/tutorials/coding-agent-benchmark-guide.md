---
title: "Coding Agent Benchmark Guide: How to Compare Agents on Your Own Repository"
description: "Build a fair 3–5-task pilot to compare Coding Agents on your repository with fixed commits, tests, permissions, budgets, repeated trials, and review burden."
keywords:
  - coding agent benchmark
  - coding agent comparison
  - coding agent leaderboard
  - AI coding agent evaluation
  - coding agent scorecard
sidebar_position: 22
tags: [tutorial, coding-assistant, agent-engineering, benchmarks]
---

# Coding Agent Benchmark Guide: How to Compare Agents on Your Own Repository

*by Youguang*

---

There is a moment I recognize immediately when a team is shopping for a Coding Agent. Someone pulls up a leaderboard, points near the top, and says something like: *"This one performed well on SWE-bench Verified. Shouldn't we just use that?"*

It is a reasonable instinct. Public benchmarks are not noise; they represent real engineering effort to define tasks uniformly and make results comparable across systems. The problem is the gap between *"performed well on a defined benchmark"* and *"will work well in our repository, under our constraints, on the work we actually do."* Those are different questions. A leaderboard answers the first. It cannot answer the second, because it was not designed to.

This guide is for the developer or small engineering team standing at that second question. It is a method for building a small, reproducible task set from your own repository so that you can compare candidates on controlled evidence rather than borrowed scores.

---

## What a Public Benchmark Answers — and What It Cannot

Think of a public benchmark as a standardized test track. Everyone who runs on it faces the same course: the same benchmark tasks and grading target, the same obstacles, the same finish line. That uniformity is precisely what makes the results comparable. When SWE-bench defines a coding task, it anchors to a specific repository, a `base_commit`, a problem statement, a test patch, and documented test transitions — the set of tests that must go from failing to passing, and the set that must continue to pass. Each attempt produces a patch. Patches are graded by running the repository's tests in a Docker-based environment. The result is a number you can compare across systems, because the benchmark fixes the tasks and grading target.

That is genuinely valuable. It makes a public benchmark useful for building a shortlist.

But the track was not built from your repository. It does not know that your team enforces a strict import boundary between modules, that your CI pipeline fails on any touched migration file outside a migration PR, that you have a permission policy that prevents tool calls to external hosts during review, or that some of your most important tasks are repository-specific maintenance work that no public benchmark includes. The track cannot tell you how much human review and correction time an Agent will cost you per task — and that number has a way of dominating the decision once you are in production.

The next question after understanding the leaderboard is therefore not "which name is number one?" but "what controlled evidence would let me choose for *this* repository?"

---

## Define the Candidate Before You Define the Tasks

One of the easiest ways to run a meaningless comparison is to compare vague things. "Agent A versus Agent B" is not a comparison. A comparison requires fixing what you are actually comparing.

A candidate is a complete configuration:

| Configuration axis | What to record |
|--------------------|----------------|
| Agent / client name and version | The exact release or build identifier |
| Model name and version | Not just the family — the specific version |
| Harness or runner and its config | The framework, version, and configuration file or flags used |
| Context files loaded | System prompt, rules files, repository summaries, etc. |
| Tools and skills available | Which tools are enabled; which external calls are allowed |
| Permission and network policy | What file paths, shell commands, and network hosts are permitted |

If two candidates differ on any of these axes, you are measuring the combination, not just the model. That is fine — the combination is what you will deploy. But record it precisely so that you know what you chose and can reproduce the comparison later.

This also means that comparing "the same model" via two different client applications is a legitimate and sometimes important comparison. The [Harness](/docs/tutorials/coding-agent-harness-explained/) and permissions are product differences, not noise to erase.

---

## Write the Decision and Disqualifiers Before Selecting Tasks

Before you build a single task, write down what you are actually deciding and what would end the evaluation early.

**The decision question** should be narrow and repository-specific. Not "which Agent is best?" but something like: "Which configuration should we introduce as the default suggestion for engineers working in this service, given our current CI, review process, and permission policy?"

**Disqualifiers** are must-pass conditions that no dimension weighting can override. Common ones include:

- Modifies files outside the declared scope without flagging
- Breaks any currently-passing test in the regression suite
- Requires permissions beyond the declared policy to complete any task
- Cannot operate within the declared token or cost budget per task
- Introduces a security-relevant change without explicit direction

Write these down before running anything. If you decide disqualifiers mid-run, you will be tempted to calibrate them around the results you have already seen.

---

## Build a 3–5-Task Pilot from Real Repository Work

A pilot of three to five tasks is not a statistically conclusive study. I want to say that plainly. You will not be able to rank candidates with confidence after five tasks, and any framing that implies otherwise should make you skeptical.

What a small pilot *can* do is reveal fit and failure modes: a candidate that repeatedly escapes its declared scope, a candidate that cannot handle your import style, a candidate whose diffs require significant cleanup, or a candidate that escalates permissions on maintenance tasks. These are useful signals even without a rigorous sample size. They can support a provisional decision and identify what a maintained evaluation gate should monitor over time.

Choose tasks that are representative of the work your team actually does. Some useful task shapes to draw from:

- **A localized bug with a regression test.** A well-scoped defect with a failing test already written or straightforward to write. Tests functional correctness directly.
- **A small cross-module feature.** Something that requires understanding relationships between at least two modules. Tests whether the candidate reads context correctly and respects existing patterns.
- **A behavior-preserving refactor.** A cleanup or restructuring task where the tests must all continue to pass and no behavior should change. Good at revealing whether a candidate stays inside its brief.
- **A diagnosis task.** Ask the candidate to identify the cause of a defect or a failing test without necessarily fixing it. Tests analytical quality without conflating it with patch quality.
- **A repository-specific maintenance task.** A changelog update, a schema migration entry, a dependency version bump following your conventions. Tests whether the candidate understands your repository's administrative conventions, not just its code.

Do not pick tasks that are too easy (every candidate will pass, revealing nothing) or tasks that are far outside the work your team does (revealing nothing about fit). Pick tasks where you expect some variation in outcome.

---

## Write Each Task Card Before Testing

Every task needs a card written before any candidate runs it. This is not bureaucracy; it is what makes the results reviewable and the comparison fair. A card written after the run will unconsciously reflect what you observed.

A task card records:

- **Task ID, source, and type** — a stable identifier, where the task came from (issue number, commit, conversation), and which shape it is.
- **Exact prompt** — the full text the candidate will receive. Not a paraphrase. The exact string.
- **Frozen commit** — the `git` SHA the candidate starts from. Every trial starts from the same commit.
- **Setup instructions** — any environment preparation needed before the run.
- **Allowed scope** — which files and directories the candidate is expected to modify. Everything else is out of scope.
- **Must-pass checks** — the specific tests or behaviors that must succeed.
- **Regression checks** — the full set of tests that must continue to pass.
- **Forbidden changes** — specific files or patterns that must not be touched (e.g., migration files, generated files).
- **Reset method** — the exact sequence to recreate a clean state between trials, preferably with a disposable worktree or container rebuilt from the frozen commit rather than destructive cleanup in a working directory.
- **Budgets** — declared per-trial limits on elapsed time and, where measurable, tokens and cost.
- **Permissions and network policy** — what the candidate is allowed to do.
- **Repetition count** — how many trials you will run per candidate per task.

Writing this card forces you to notice ambiguities before they corrupt your data. If you cannot write the exact prompt, you are not ready to run the task.

---

## Protocol Fairness: What It Means and What It Does Not

Fair comparison does not mean erasing real product differences. It means making all differences visible.

Every candidate receives the same starting commit, the same exact prompt, and the same budget declaration. Every trial begins from a clean reset. Every run is preserved with its version information. Differences you cannot control — a model version that changed mid-study, a network latency spike during one run — are logged as caveats, not silently absorbed into the results.

Some real product differences should remain in the comparison: if one candidate supports a tool that another does not, that is a capability difference worth knowing about. If one candidate's Harness enforces a strict file-scope policy and another does not, that is a permission difference that affects your deployment decision. Do not standardize these away.

A note on prompted context: if you give one candidate a system prompt, repository summary, or rules file, and another candidate nothing, you are not comparing models — you are comparing configurations. That might be your intended comparison ("what does our default setup versus a minimal setup look like?"), but name it clearly.

---

## Protocol Overview

| Phase | What to fix | What to record |
|-------|-------------|----------------|
| Before any run | Decision question, disqualifiers, candidate configurations, task cards, reset method, budgets | Protocol document with all fields populated |
| At each trial start | Frozen commit verified, clean environment confirmed, prompt delivered exactly | Trial start timestamp, candidate version snapshot |
| During the trial | No intervention unless the candidate hits a declared blocker | Logs, tool traces |
| After each trial | Reset immediately; do not carry over artifacts | Trial record: results, diff, artifacts, timing, token/cost if available |
| After all trials | Grade, review, correct, log review time | Per-trial record completed |
| Decision | Apply must-pass gates, then matrix | Decision document with failures and caveats preserved |

---

## Grading the Outcome

Grade in two stages.

**Stage one: functional outcome.** Did the required behavior tests pass? Did the regression suite pass? For the must-pass gate, record whether both conditions were met. Keep any partial result as diagnostic evidence, not as a substitute for the declared gate.

**Stage two: everything else, kept separate.** Do not collapse these into a weighted score — a composite score can hide a repeated failure mode behind strong scores on other dimensions. Keep them as separate columns:

- **Diff scope** — were changes confined to the declared allowed scope? Were there unrelated edits?
- **Tool behavior** — did the candidate use only its declared tools? Were there tool failures or retries?
- **Permission escalations** — did the candidate request or attempt capabilities outside the declared policy?
- **Artifacts** — what did the candidate produce? Are traces, diffs, and test results preserved and readable?
- **Timing and resources** — elapsed time per trial. Tokens and cost per trial if the client exposes them; write `N/A` if not. Do not estimate from text length.
- **Human review and correction burden** — minutes spent reading and validating the diff, minutes spent correcting it, number of interventions required. This is often the most consequential column and the one most frequently omitted.

On human burden: a candidate that produces a cheap token run but generates a diff that requires a costly audit and partial rewrite is not an inexpensive candidate. Record the correction time.

Grading should assess what the candidate produced, not whether it followed a specific path. If the task allows multiple valid approaches and a candidate took a valid approach you did not anticipate, that is not a failure. Grade the outcome against the must-pass checks and the regression suite, then inspect the diff for scope and quality.

---

## Repeated Trials

Model outputs vary between runs. A single trial per task per candidate is not sufficient to understand reliability. Anthropic's evaluation guidance makes this point explicitly: multiple trials are needed, and the environment must be stable and cleanly isolated between trials, because leftover files, caches, or state can distort results.

How many repetitions to run is a budget question. The blank scorecard below has a field for repetition count — your protocol chooses the number before any run begins. Whatever you choose, apply it uniformly across all candidates and all tasks.

One practical note: if your budget allows only one trial per task per candidate, record that as a constraint on the conclusions you can draw. A single pass on a single trial says almost nothing about reliability.

---

## Making the Decision

Apply disqualifiers first. A candidate that triggered a disqualifier during any trial — escaped scope, broke regression, required forbidden permissions — is disqualified. No dimension score compensates for a must-pass failure.

For candidates that clear all disqualifiers, review the dimension columns:

- Where is functional reliability high across tasks and trials? Where does it drop, and why?
- Which diffs are clean and reviewable? Which require significant correction effort?
- Which candidates stay inside their permission policy consistently?
- Where token and cost data is available, does it fall within budget?
- What is the total human burden per task?

If one candidate is clearly better on every dimension, the choice is easy. Usually it is not. Record the tradeoffs honestly, including the tasks or dimensions where each candidate performed worse. The decision should be repository-specific: "for this repository, this team, and this use case, configuration X is preferred because of Y, with the caveat that it performed worse on Z." That caveat is part of the record.

Do not crown a universal winner. The team on the other side of a different repository, with different conventions and different permission policies, should run their own pilot.

---

## Reusable Blank Scorecard

Copy this template before any run. Fill in the protocol and task-card fields before beginning the first trial. Leave result cells blank until the run completes.

````markdown
## Coding Agent Evaluation Scorecard

---

### Part 1 — Protocol Header

| Field | Value |
|-------|-------|
| Experiment ID | |
| Date | |
| Owner | |
| Decision question | |
| Repository | |
| Frozen commit (SHA) | |
| Shared context files | |
| Permissions / network policy | |
| Declared token / cost budget per trial | |
| Repetitions per task per candidate | |
| Reset rule | |

#### Candidate Configurations

| Axis | Candidate A | Candidate B | Candidate C |
|------|-------------|-------------|-------------|
| Agent / client name | | | |
| Agent / client version | | | |
| Model name | | | |
| Model version | | | |
| Harness / runner | | | |
| Harness version / config | | | |
| Context files loaded | | | |
| Tools / skills enabled | | | |
| Permission policy | | | |
| Network policy | | | |
| Notes | | | |

---

### Part 2 — Task Cards

*(Copy this block for each task in the pilot. Complete before any run.)*

#### Task [ID]

| Field | Value |
|-------|-------|
| Task ID | |
| Source | |
| Type | |
| Exact prompt | |
| Starting commit (SHA) | |
| Setup instructions | |
| Allowed scope (files / directories) | |
| Must-pass checks | |
| Regression checks | |
| Forbidden changes | |
| Artifacts to retain | |
| Reset sequence | |
| Elapsed time budget | |
| Token / cost budget (or N/A) | |
| Repetitions | |

---

### Part 3 — Per-Trial Record

*(Copy this block for each trial: one candidate × one task × one repetition.)*

#### Trial [ID] — Candidate [ ] — Task [ ] — Rep [ ]

| Field | Value |
|-------|-------|
| Trial start timestamp | |
| Trial end timestamp | |
| Elapsed time | |
| Tokens used (or N/A) | |
| Cost (or N/A) | |
| Functional result (pass / fail) | |
| Regression result (pass / fail) | |
| Timeout / error (Y / N; describe) | |
| Files changed | |
| Unrelated edits (Y / N; describe) | |
| Tool failures (Y / N; describe) | |
| Permission escalations (Y / N; describe) | |
| Trace artifact link | |
| Diff artifact link | |
| Test log artifact link | |
| Review minutes | |
| Correction minutes | |
| Interventions (count and description) | |
| Accept / reject | |
| Blocking reason (if rejected) | |
| Notes | |

---

### Part 4 — Decision Matrix

#### Must-Pass Gate Status

| Disqualifier | Candidate A | Candidate B | Candidate C |
|--------------|-------------|-------------|-------------|
| [Disqualifier 1] | | | |
| [Disqualifier 2] | | | |
| [Disqualifier 3] | | | |
| **Cleared all gates?** | | | |

*(Candidates that did not clear all gates are excluded from the matrix below.)*

#### Dimension-by-Dimension Summary

| Dimension | Candidate A | Candidate B | Candidate C |
|-----------|-------------|-------------|-------------|
| Functional reliability (task / trial breakdown) | | | |
| Diff quality and scope | | | |
| Unrelated edits | | | |
| Permission fit | | | |
| Operational fit (errors, escalations, tool failures) | | | |
| Resource visibility (tokens / cost, or N/A) | | | |
| Human review burden (minutes per task) | | | |
| Human correction burden (minutes per task) | | | |

#### Repository-Specific Decision

| Field | Value |
|-------|-------|
| Selected configuration | |
| Decision rationale | |
| Known weaknesses / caveats | |
| Tasks / dimensions where non-selected candidates performed better | |
| Conditions that would prompt re-evaluation | |
| Date of next scheduled review | |

````

---

## Where This Fits in a Maintained Evaluation Practice

A one-time pilot answers the question "which candidate should we start with?" It does not answer "is this candidate still performing well three months from now, after model updates and repository drift?"

If the pilot reveals tasks worth monitoring over time — a regression check you want to run on every model update, a scope-escape pattern you want to detect automatically — those are candidates for a maintained quality gate. The [Coding Agent Evals Guide](/docs/tutorials/coding-agent-evals-guide/) covers how to turn a selected task set into a repeatable gate with versioned fixtures and automated grading. The two documents are designed to be read together: this guide for the initial selection decision, and the Evals Guide for the ongoing monitoring practice.

The judgment I hold most firmly, and the one I think survives most discussions about which agent to use: the final diff and the cleanup work matter more than any badge. A system that produces a clean, scoped, reviewable patch on tasks drawn from your repository is more useful to your team than one that scores well on a track you did not build. Build your track. Run it carefully. Keep the failures in the record.

---

## Source References

- SWE-bench repository: https://github.com/SWE-bench/SWE-bench
- SWE-bench dataset documentation: https://github.com/SWE-bench/SWE-bench/blob/main/docs/guides/datasets.md
- SWE-bench evaluation documentation: https://github.com/SWE-bench/SWE-bench/blob/main/docs/guides/evaluation.md
- Anthropic — Demystifying Evals for AI Agents: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- OpenAI — Evaluation Best Practices: https://developers.openai.com/api/docs/guides/evaluation-best-practices
- Harbor framework — Tasks documentation: https://www.harborframework.com/docs/tasks
- Harbor framework — Run Evals documentation: https://www.harborframework.com/docs/run-jobs/run-evals
