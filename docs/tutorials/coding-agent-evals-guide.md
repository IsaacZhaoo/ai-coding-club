---
title: "Coding Agent Evals Guide: Turn Traces into Datasets and Quality Gates"
description: "Turn a preserved Coding Agent trace into a local JSONL dataset, deterministic graders, machine-readable reports, and a CI quality gate."
keywords:
  - coding agent evals guide
  - coding agent evaluation framework
  - agent evals tools
  - eval-driven development
  - coding agent quality gate
sidebar_position: 20
tags: [tutorial, coding-assistant, agent-engineering, evals]
---

# Coding Agent Evals Guide: Turn Traces into Datasets and Quality Gates

*by Youguang*

---

The [Observability Tutorial](/docs/tutorials/coding-agent-observability-guide/) showed how to capture a Codex CLI event stream and preserve a real diagnosis record. This guide picks up exactly there. It will not re-explain trace capture or log shipping. What it will do is take that preserved record, state what must remain true about its outcome, normalize it into a small structured trial, and make a deliberately wrong candidate fail with a non-zero process exit code that CI can act on.

By the end you will have a local, replayable gate with visible inputs and a clear exit code. No hosted scoring service, no remote API key, no model call in the verification path.

> **Download:** <a href="/examples/coding-agent-eval-gate.zip">/examples/coding-agent-eval-gate.zip</a> — contains the five core files discussed here, plus a README.

---

## Why I Build This Locally First

I have a strong preference for auditability. A hosted eval score I cannot step through is less useful to me than a script I can read in an afternoon. The gate in this guide uses only Python's standard library. Every input is a JSONL file I can open in a text editor. The verdict is a JSON object printed to standard output, and the process exit code is the CI seam.

This is not the only way to evaluate Agents. OpenAI's current evaluation guidance describes a pipeline of objective → dataset → metrics → compare runs → continuous evaluation and explicitly recommends mining logs for cases. Anthropic has published a detailed vocabulary for Agent evals—*task*, *trial*, *grader*, *transcript/trace*, *outcome*, *Harness*, and *suite*—and recommends deterministic graders where possible. Anthropic also warns that rigid trajectory matching can reject a valid path the eval author did not anticipate. This guide is built around that advice.

One housekeeping note: OpenAI's old Evals platform is deprecated and scheduled to shut down on 2026-11-30. I will not teach its API as a durable path. Everything here runs on the standard library and will still work after that date.

---

## Run First, Read Later

Before touching implementation detail, run the tests and both gate commands so you can see what you are working toward.

**Tests:**

```bash
python3 -m unittest -v test_eval_gate.py
```

All 20 test methods pass. I will summarize their covered behaviors later in this guide.

**Preserved baseline (the real Codex trace, normalized):**

```bash
python3 eval_gate.py \
  --cases eval-cases.example.jsonl \
  --trials baseline-trials.example.jsonl
```

```json
{
  "case_count": 1,
  "trial_count": 1,
  "passed_trials": 1,
  "failed_trials": 0,
  "gate_passed": true,
  "results": [
    {
      "case_id": "average-empty-diagnosis",
      "trial_id": "codex-diagnosis-20260723",
      "passed": true,
      "failed_checks": []
    }
  ]
}
```

Process exit code: `0`.

**Deliberately wrong synthetic regression:**

```bash
python3 eval_gate.py \
  --cases eval-cases.example.jsonl \
  --trials regression-trials.synthetic.jsonl
```

```json
{
  "case_count": 1,
  "trial_count": 1,
  "passed_trials": 0,
  "failed_trials": 1,
  "gate_passed": false,
  "results": [
    {
      "case_id": "average-empty-diagnosis",
      "trial_id": "synthetic-wrong-fix",
      "passed": false,
      "failed_checks": ["answer_contains_all"]
    }
  ]
}
```

Process exit code: `1`. The regression record is synthetic and carries `"synthetic": true`.

Now let us look at what is inside those files.

---

## The Case Record: What Must Remain True

A *case* captures everything you know about what a correct outcome looks like, independent of any specific run. It does not record how the Agent got there.

Here is the single case in `eval-cases.example.jsonl`:

```jsonl
{
  "case_id": "average-empty-diagnosis",
  "task": "Diagnose why average([]) violates the focused test without modifying files.",
  "expect": {
    "turn_status": "completed",
    "answer_contains_all": [
      "ZeroDivisionError",
      "ValueError(\"at least one value\")"
    ],
    "max_tool_calls": 5,
    "max_failed_tool_calls": 2,
    "modified_files": []
  }
}
```

Each field is a check, not a log replay:

| Field | What it enforces |
|---|---|
| `expect.turn_status` | The Agent's turn must complete with the expected status |
| `expect.answer_contains_all` | The final answer must contain every listed substring |
| `expect.max_tool_calls` | A policy ceiling on tool use, not a required exact count |
| `expect.max_failed_tool_calls` | A policy ceiling on failed tool calls |
| `expect.modified_files` | Exact expected modified-file list |

The tool-call ceilings are local teaching policy derived from this case. They are not industry benchmarks. A cleaner Agent that reaches the same correct diagnosis in three tool calls and zero failures passes this gate just as legitimately—and one of the 20 tests verifies exactly that.

The expected `modified_files` list is empty here because the Codex task was read-only: diagnose, do not fix. Any trial that writes a source file will fail the `modified_files` check.

---

## The Trial Record: One Run's Evidence

A *trial* is a normalized snapshot of one Agent run against one case. It does not need to be a full trace replay. It only needs the fields the gate checks.

Here is the entry from `baseline-trials.example.jsonl`:

```jsonl
{
  "case_id": "average-empty-diagnosis",
  "trial_id": "codex-diagnosis-20260723",
  "turn_status": "completed",
  "answer": "average([]) divides by zero and raises ZeroDivisionError; the smallest fix is an empty-input guard that raises ValueError(\"at least one value\") before division.",
  "tool_calls": 5,
  "failed_tool_calls": 2,
  "modified_files": [],
  "synthetic": false,
  "source": "preserved Codex CLI 0.145.0 event stream from 2026-07-23"
}
```

And here is the synthetic regression in `regression-trials.synthetic.jsonl`:

```jsonl
{
  "case_id": "average-empty-diagnosis",
  "trial_id": "synthetic-wrong-fix",
  "turn_status": "completed",
  "answer": "Return 0 when the list is empty.",
  "tool_calls": 3,
  "failed_tool_calls": 0,
  "modified_files": [],
  "synthetic": true,
  "source": "synthetic regression used to exercise the failing gate"
}
```

The synthetic trial has the expected status, stays within tool budgets, and writes no files, but its answer contains neither `ZeroDivisionError` nor the `ValueError` guard. That is why it fails only the `answer_contains_all` check and exits `1`.

This fixture labels every fabricated record with `synthetic: true`. You should never mix real and synthetic data silently.

---

## The Adapter Boundary: Trace to Trial

Between the raw event stream and the trial record there is a normalization step I call the adapter. The Observability Tutorial preserved the original Codex CLI 0.145.0 event stream. From that stream I extracted:

- **Final turn status:** `completed`
- **Answer text:** the Agent's last prose response, which identifies both `ZeroDivisionError` and the `ValueError("at least one value")` guard
- **Tool call count:** five tool calls across the session
- **Failed tool call count:** two tool calls that returned non-zero or error results
- **Modified files:** none (read-only diagnostic task)

Those are facts from one trial only. I do not claim they are typical for this class of task. The adapter produces a JSONL record with those five fields plus the `case_id`, `trial_id`, `synthetic`, and `source` labels.

The adapter is not in the eval gate itself. The gate is deliberately ignorant of Codex's event format, OpenTelemetry spans, or any specific trace schema. The JSONL contract is a local teaching format, not OTLP or any official eval standard. If you switch your tracing backend, you update the adapter, not the gate.

This is the most important architectural boundary in the whole setup. Keep it explicit and keep it testable.

---

## The Gate: Deterministic Checks, Machine-Readable Report

`eval_gate.py` (see the download for the full source) does the following:

1. **Validates both input files.** If either file contains invalid JSON, a non-standard JSON constant (`NaN`, `Infinity`, `-Infinity`), duplicate case IDs, duplicate trial IDs, an unknown `case_id` in a trial, an empty case set, an empty trial set, a case with no corresponding trial, a scoring field with the wrong type, a counter or limit that is not a non-negative integer, or `failed_tool_calls` greater than `tool_calls`—it writes a JSON error object to standard error and exits `2`. Exit code `2` is distinct from a passed gate (`0`) and a failed gate (`1`), so CI can distinguish bad input from a genuine regression.

2. **Runs five checks per trial** against its case definition:
   - `turn_status` matches `expect.turn_status`
   - Every string in `answer_contains_all` appears as a substring in `answer`
   - `tool_calls` ≤ `max_tool_calls`
   - `failed_tool_calls` ≤ `max_failed_tool_calls`
   - `modified_files` exactly matches `expect.modified_files`

3. **Builds a report** with case count, trial count, passed/failed counts, `gate_passed`, and per-trial `failed_checks`.

4. **Exits `0`** if `gate_passed` is true, **`1`** if false.

A short excerpt showing the core check loop:

```python
expected = cases_by_id[case_id]["expect"]
failed_checks = []

if trial["turn_status"] != expected["turn_status"]:
    failed_checks.append("turn_status")
if not all(
    fragment in trial["answer"]
    for fragment in expected["answer_contains_all"]
):
    failed_checks.append("answer_contains_all")
if trial["tool_calls"] > expected["max_tool_calls"]:
    failed_checks.append("max_tool_calls")
if trial["failed_tool_calls"] > expected["max_failed_tool_calls"]:
    failed_checks.append("max_failed_tool_calls")
if trial["modified_files"] != expected["modified_files"]:
    failed_checks.append("modified_files")
```

That is the entire grading logic. No model call, no remote request, no randomness.

---

## The Preserved Baseline: Real Evidence Holds

When you run the gate against `baseline-trials.example.jsonl`, you are asking: does the normalized evidence from the preserved Codex run still satisfy the case definition?

```bash
python3 eval_gate.py \
  --cases eval-cases.example.jsonl \
  --trials baseline-trials.example.jsonl
```

It does. `gate_passed: true`, exit code `0`. This is the sanity check that your case definition is not so strict that it rejects the real observed behavior you were trying to codify.

If the preserved baseline ever fails, investigate the fixture, gate, and case contract before comparing a new Agent run; the failure is in that local verification path, not evidence about a candidate by itself.

---

## The Synthetic Regression: Exit Code 1 as the CI Seam

The synthetic regression trial in `regression-trials.synthetic.jsonl` is fabricated to represent a wrong fix: returning `0` for an empty list instead of identifying the `ZeroDivisionError` and required guard. It is explicitly labeled `"synthetic": true`. Do not treat it as evidence about real Agent behavior.

```bash
python3 eval_gate.py \
  --cases eval-cases.example.jsonl \
  --trials regression-trials.synthetic.jsonl
```

Exit code `1`. The failed check is `answer_contains_all`.

This exit code is the only thing CI needs to see. The gate does not require CI to parse the JSON report. A shell pipeline or YAML step blocks on non-zero exit by default. The JSON report is available if a human or downstream tool needs the detail.

The design principle here matches what Anthropic describes for outcome-based graders: you check whether the Agent achieved the right result, not whether it followed a particular sequence. The synthetic trial finishes with `completed` status, three tool calls, zero failures, no file writes—it would pass every check except the one that asks whether the answer actually addresses the diagnosed root cause.

---

## Outcome-First Grading: Why Trajectory Matching Is Brittle

The Codex baseline used five tool calls and two failed ones. I could have written the case to require exactly those counts. I did not.

Anthropic's published guidance explicitly warns against overly rigid trajectory grading because a capable Agent may find a valid path the eval author did not anticipate. This is not abstract advice. If you require exactly five tool calls:

- A faster Agent that reads the relevant file in one shot and answers correctly fails.
- A refactored Agent with better retry logic that succeeds on first attempt fails.
- Any future Agent running on improved infrastructure that produces fewer intermediate steps fails.

The case sets ceilings (`max_tool_calls: 5`, `max_failed_tool_calls: 2`). A trial that uses three tool calls and zero failures satisfies both ceilings. One of the 20 tests—the "cleaner path pass"—verifies this explicitly.

The `answer_contains_all` check is a substring gate, not a semantic judgment. It catches the synthetic wrong-fix trial because both required fragments are absent. It can also reject a correct paraphrase that omits those exact strings. The gate uses this deterministic check as a transparent teaching minimum, not as sufficient production semantic grading. If you later add a model-based grader, calibrate it against human judgment before trusting its verdicts.

---

## Twenty Tests: What They Cover

The 20 test methods in `test_eval_gate.py` cover the following behavior groups. Some methods exercise more than one related boundary, so this is a coverage map rather than the file's literal method order:

1. **Real baseline pass** — the preserved Codex trial passes all checks
2. **Synthetic wrong-fix failure** — the synthetic regression fails `answer_contains_all`
3. **Cleaner path pass** — three tool calls, zero failures, same correct answer still passes
4. **Tool-budget failure** — exceeding `max_tool_calls` fails the gate
5. **Failed-status failure** — a trial with a non-matching status fails `turn_status`
6. **Failed-tool-budget failure** — exceeding `max_failed_tool_calls` fails the gate
7. **Unexpected file write failure** — a `modified_files` list that differs from the case expectation fails
8. **CLI pass exit 0** — running the gate CLI returns exit code `0` on the baseline
9. **CLI fail exit 1** — running the gate CLI returns exit code `1` on the regression
10. **Invalid-input CLI exit 2** — malformed input returns exit code `2` with a JSON error on stderr
11. **Duplicate case rejection** — two records sharing a `case_id` are rejected at input validation
12. **Duplicate trial rejection** — two records sharing a `trial_id` are rejected at input validation
13. **Unknown case rejection** — a trial referencing a nonexistent `case_id` is rejected
14. **Empty case-set rejection** — an empty cases file is rejected
15. **Empty trial-set rejection** — an empty trials file is rejected
16. **Case-without-trials rejection** — a case with no matching trial is rejected
17. **Non-negative integer validation** — negative and non-integer counter or limit examples are rejected
18. **Impossible failed-tool count rejection** — `failed_tool_calls > tool_calls` is rejected
19. **Non-standard JSON constant rejection** — the parser rejects `NaN`, `Infinity`, and `-Infinity`; the test places `NaN` in an otherwise ungraded field
20. **Invalid JSON error reporting** — the error object includes the source file name, line number, and column of the parse failure

Tests 11–20 cover input validation only. They do not run grading logic. Separating validation tests from grading tests is important: if validation breaks, grading results are meaningless.

---

## CI Integration: Block on Non-Zero Exit

The verified gate command is three lines. Wrapping it in CI is equally short.

**Shell snippet:**

```bash
#!/usr/bin/env bash
set -euo pipefail
python3 eval_gate.py \
  --cases eval-cases.example.jsonl \
  --trials baseline-trials.example.jsonl
```

`set -e` exits the script on any non-zero exit code. No parsing needed.

**GitHub Actions fragment:**

```yaml
- name: Run eval gate
  run: |
    python3 eval_gate.py \
      --cases eval-cases.example.jsonl \
      --trials baseline-trials.example.jsonl
```

GitHub Actions marks a step failed when its command exits non-zero. This is the entire CI integration. The merge-blocking step should evaluate new candidate trials against the case contract. Keep a known failing trial as a negative test fixture that explicitly asserts exit `1`; do not feed it into the all-trials-must-pass invocation and make CI permanently red.

One practical note: keep the gate command in CI deterministic. The bundled gate validates the scoring fields before grading and exits `2` on malformed input. If another CI step generates trial files dynamically, preserve that validation boundary instead of letting malformed data skip grading.

---

## Growing the Fixture: A Practical Expansion Path

The fixture in the download is intentionally minimal: one case, one baseline trial, one synthetic regression. That is enough to prove the gate works and to anchor CI. Here is how to grow it without losing auditability.

**Start with real failures.** When an Agent produces a wrong answer, use that trace to create or sharpen a case contract, then run future candidate trials against that case. Preserve the original failure as negative evidence and a test of the gate's failure path, not as an input to the merge-blocking all-pass run. A synthetic failure is a placeholder until you have a real one.

**Balance your cases.** Cases should cover distinct task types, not just variations of the same diagnosis prompt. If all your cases look like `average-empty-diagnosis`, your gate covers one narrow slice of Agent behavior. Additional real traces can become candidates after human review and normalization.

**Isolate environments.** If your trials touch real files or real network endpoints, introduce a sandbox wrapper at the adapter layer, not inside the gate. The gate must remain stateless and reproducible. A trial record should contain the normalized evidence, not a live Agent session.

**Run multiple trials per case.** Agents are not fully deterministic. Anthropic recommends multiple trials per case specifically because of run-to-run variability. If you run a case ten times and six pass, the case is not reliably verified. The gate in this guide counts passed and failed trials separately; you can extend the `gate_passed` logic to require a minimum pass rate once you have enough trials to make that meaningful.

**Add model-based graders only after calibration.** When substring checking is genuinely insufficient—open-ended code review, explanation quality, architectural judgment—add a model-based grader. But do not add it until you have human-reviewed a sample of its outputs against your own verdicts and the agreement rate is high enough that you trust it to block CI. Calibration is not optional for model-based graders; it is the evidence that the grader is measuring what you think it is measuring.

**Use the OpenAI guidance pipeline as a forcing function.** OpenAI's current evaluation best practices describe: define objective → build dataset → pick metrics → compare runs → set up continuous evaluation. The gate in this guide covers the first two steps and the continuous evaluation seam. Metrics beyond pass/fail—latency, token count, cost—belong in a separate reporting layer that reads the same JSONL trials, not inside the gate itself.

---

## What This Gate Does Not Do

To be precise about scope:

- It does not claim the JSONL format is OTLP or any official eval standard. It is a local teaching contract.
- It does not call a model or use an LLM as a judge anywhere in the verified code path.
- It does not report pass rates, pass@k, speed, cost, or rankings derived from a single trial.
- It does not infer fields from the raw trace or invent Agent runs.
- It does not compare vendors or recommend hosted scoring services.

Substring checking—`answer_contains_all`—is not sufficient for production semantic quality assessment. The gate uses it because it is deterministic, auditable, and honest about its limitations. Graduating to richer graders is the expansion path described above, not a shortcut available on day one.

---

## Summary

The core loop is:

1. Preserve a real trace with the observability setup from the previous tutorial.
2. Extract the five outcome facts: turn status, answer evidence, tool counts, modified files.
3. Write a case that encodes what must remain true, with policy ceilings rather than exact counts.
4. Write a trial with the normalized evidence.
5. Run `eval_gate.py`. Exit `0` means the case is satisfied. Exit `1` means it is not. Exit `2` means the input is malformed.
6. Let CI block on non-zero exit.

That is a machine-readable quality gate. It is local, replayable, and auditable. It does not require an internet connection, a vendor account, or a model inference call. It will still run after the old Evals platform goes dark on 2026-11-30.

The expansion path—more cases, more trials per case, model-based graders with human calibration—is real work. But it starts here, with one preserved trace and five checks that tell you whether a candidate Agent identified `ZeroDivisionError` and the `ValueError` guard. That is a concrete, verifiable starting point, and concrete and verifiable is where I always want to begin.

---

*Download the complete fixture: <a href="/examples/coding-agent-eval-gate.zip">/examples/coding-agent-eval-gate.zip</a>*
