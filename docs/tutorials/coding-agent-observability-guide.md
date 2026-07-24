---
title: "Coding Agent Observability Guide: Trace Tools, Retries, Tokens, Handoffs, and Failures"
description: "Build a local Coding Agent trace audit that preserves tool failures, retries, Token usage, handoffs, and explicit telemetry gaps."
keywords:
  - coding agent observability guide
  - coding agent trace
  - agent observability tools
  - OpenTelemetry GenAI
  - Codex CLI JSONL
sidebar_position: 19
tags: [tutorial, coding-assistant, agent-engineering, observability]
---

# Coding Agent Observability Guide: Trace Tools, Retries, Tokens, Handoffs, and Failures

*By Youguang*

---

## What a Useful Trace Must Preserve

In the preceding [Coding Agent Observability article](/blog/coding-agent-observability/) I showed a completed Codex turn that contained two failed tools. The turn finished as `completed`, the diagnosis was correct, and the agent never modified a file. Useful result. But the moment I close the terminal, I lose all of that unless I preserved the path.

That is the observability question this guide answers: **what must a Coding Agent trace preserve so that tools, retries, handoffs, and failures can be reconstructed later without turning missing telemetry into invented data?**

My answer, stated once and enforced throughout:

> A useful Coding Agent trace preserves identity, parent relationships, status, observed usage, and explicit coverage gaps, so tools, retries, handoffs, and failures can be reconstructed without turning missing telemetry into invented data.

A trace that omits a field should say so. A trace that cannot compute cost should record `cost_available: false`. Honest gaps are a coverage result. Invented numbers are a lie.

The downloadable fixture at <a href="/examples/coding-agent-trace-audit.zip">/examples/coding-agent-trace-audit.zip</a> contains everything referenced below: the portable schema, the synthetic full-field example, the real Codex event stream, the audit script, and the test suite.

---

## Run the Tests First

Before I explain any implementation, here are the commands and their verified results. Run them against the downloaded fixture so you can see exactly what passes before reading the explanations.

### Eleven unit tests

```bash
python3 -m unittest -v test_trace_audit.py
```

All eleven tests pass. The suite checks the deterministic summaries, CLI JSON output, and selected validation behavior. The validator itself enforces required fields, unique span ids, known parents, matching trace ids, allowed status values, end time ordering, and cycle detection; the current suite does not exercise every rejection branch separately.

### Synthetic portable trace audit

```bash
python3 trace_audit.py portable \
  --trace portable-trace.example.jsonl
```

Verified output:

| Field | Value |
|---|---|
| Trace count | 1 |
| Span count | 9 |
| Root spans | 1 |
| Kind: agent | 1 |
| Kind: evaluation | 1 |
| Kind: handoff | 1 |
| Kind: model | 2 |
| Kind: skill | 1 |
| Kind: tool | 3 |
| Error spans | 2 |
| Error span ids | `tool-python`, `tool-python3` |
| Retry spans | 1 |
| Handoff spans | 1 |
| Timed spans | 9 |
| Root duration | 8,000 ms |
| Synthetic input tokens | 1,000 |
| Synthetic output tokens | 150 |
| Synthetic cost | USD 0.016 |

Every record in `portable-trace.example.jsonl` carries `"synthetic": true`. These numbers are a teaching instrument. Do not read them as a measured agent run or a provider bill.

### Real Codex event stream audit

```bash
python3 trace_audit.py codex \
  --events codex-diagnosis-20260723.jsonl
```

Verified output:

| Field | Value |
|---|---|
| Event count | 17 |
| Tool calls | 5 |
| Successful tool calls | 3 |
| Failed tool calls | 2 |
| Failed exit codes | `127`, `1` |
| Agent messages | 4 |
| Handoff events | 0 |
| Final turn status | `completed` |
| Input tokens | 74,858 |
| Cached input tokens | 59,904 |
| Cache-write input tokens | 0 |
| Output tokens | 749 |
| Reasoning output tokens | 201 |
| Duration available | `false` |
| Cost available | `false` |

This is one Codex CLI 0.145.0 event stream captured with `codex exec --json`. It proves the capture path and the parser. It proves nothing else.

---

## Trace Concepts: Identity, Parents, Status, Attributes

OpenTelemetry defines a **trace** as the path of a request through a system, and a **span** as a named unit of work within that trace. Each span can carry a trace id, a span id, a parent span id, start and end timestamps, attributes, events, links, and a status. Parent-linked spans reconstruct the full hierarchy of an end-to-end operation.

The local portable schema is not OTLP. It does not claim to be. It borrows the structural ideas—trace id, span id, parent id, status, attributes—and applies them to Coding Agent execution. Here is the minimum a portable span must include:

```jsonc
{
  "trace_id":      "trace-diagnosis-001",
  "span_id":       "tool-python",
  "parent_span_id":"agent-root",
  "kind":          "tool",
  "name":          "shell: python test_calculator.py",
  "status":        "error",
  "attributes": {
    "exit_code": 127,
    "error_message": "python: command not found"
  }
}
```

`started_at` and `ended_at` are optional because not every source emits timing. The validator checks that when both are present, the end time is not before the start time. It also checks that no span is its own ancestor—the cycle check.

The `status` field accepts two values: `ok` and `error`. That binary is intentional. I do not want a third value that a parser has to guess. Child failure and root status are kept **separate** by design, which I return to shortly.

The local `kind` values in the synthetic example are `agent`, `skill`, `model`, `tool`, `handoff`, and `evaluation`. These are tutorial categories chosen to cover common Coding Agent concepts. They are not an official universal taxonomy.

The OpenTelemetry GenAI agent semantic conventions that cover agent invocation, workflow invocation, planning, tool execution, and token-usage attributes are currently at **Development** status. I follow the structural pattern without claiming the portable schema implements the spec.

---

## Teaching with the Synthetic Trace

The synthetic trace exists to demonstrate what a fully-populated Coding Agent span record looks like. Because it is synthetic, I can include fields that the real Codex stream does not emit: timing on every span, token counts, a dollar cost, a handoff, a Skill load, and an evaluation span.

### Timing and root duration

All nine spans in the synthetic trace include `started_at` and `ended_at`. The audit computes root duration as the elapsed time on the single root span: 8,000 ms. That number is fabricated. Its purpose is to show the calculation path so that when a real source emits timestamps you know where the number comes from.

### Retries

The two error spans—`tool-python` and `tool-python3`—appear as siblings under the same parent. The audit counts a retry when a span's attributes include `retry_of`. One retry span is found: `tool-python3` points to `tool-python`. Both synthetic tool spans have `status: error`; the root span still ends `ok` after the later diagnosis work. In the real Codex stream, the same two commands return exit `127` and exit `1`, but the stream has no explicit `retry_of` field; the retry relationship is reconstructed from the sequence and the Agent message.

### Handoffs

One span carries `kind: handoff`. The audit finds it and reports handoff count as 1. The synthetic span includes attributes that name the source and target. The real Codex stream reports zero handoff events, which is accurate and expected for a single-agent single-turn run.

### Skills

One span carries `kind: skill`. It represents a loaded Skill document that scoped the agent's behavior. The synthetic trace includes it to demonstrate the concept. The real event stream contains no Skill-load event, and the current Codex summary has no Skill-load availability field; the gap therefore remains unavailable rather than being counted as zero.

### Evaluations

One span carries `kind: evaluation`. In an Eval-Driven workflow an evaluator can run assertions against the agent's output and record pass or fail. The synthetic trace demonstrates a passing evaluation. The current audit counts evaluation spans among kind totals and counts any error-status evaluation among error spans; it does not yet emit an evaluation-specific quality-gate result.

### Tokens and cost

The synthetic trace records `1,000` input tokens, `150` output tokens, and a synthetic cost of `USD 0.016`. These numbers were chosen to demonstrate the schema fields. They are labeled `synthetic: true` in every record. The audit adds them up and reports them. The real Codex stream reports token counts from the actual run; those counts are real. The real stream does not report a dollar cost. The audit reports `cost_available: false`.

---

## The Real Codex Stream: A Successful Turn with Two Failed Tools

The blog post showed the completed turn. Here is what the event stream contains when the audit reads it.

### Narrative of the run

The controlled test expected `average([])` to raise `ValueError("at least one value")`. The implementation divided by zero instead.

The agent took this path:

1. **Discover** the focused test file.
2. **Read** the test to understand the assertion.
3. **Try `python`** — shell exits `127` because `python` is not on the path.
4. **Retry with `python3`** — the test runs, the suite exits `1`, the output contains `ZeroDivisionError`.
5. **Read `calculator.py`** — confirm the bug location.
6. **Return the diagnosis** — correct, specific, no guessing.
7. **Finish** — final turn status is `completed`.

No files were modified. The agent read, diagnosed, and reported. Five tool calls total: three succeeded (`discover`, `read test`, `read calculator.py`), two failed (`shell: python`, `shell: python3`).

### Why this is the most useful result in the fixture

A completed turn with two embedded failures is more informative than a clean run. It proves that the capture path records non-zero exit codes. It proves that the audit distinguishes tool-level failure from turn-level status. It proves that you can reconstruct the retry sequence from the event stream alone.

The two failed tool calls inside a single `completed` turn are not a problem to suppress. They are the signal.

### What the event stream contains

17 events. Token fields are real: 74,858 input tokens, of which 59,904 were served from the cache, plus 749 output tokens and 201 reasoning output tokens. Cache-write input tokens: 0.

What it does not contain: wall-clock duration for the turn, a dollar cost, handoff events, Skill load events, or model identity fields. The audit explicitly reports duration and cost as `false` and the handoff count as zero; the remaining omissions are verified by inspecting the preserved stream.

---

## Child Failure and Root Status Are Separate

This deserves its own section because it is the most common mistake I see when people first look at agent traces.

A span's `status` field records **that span's outcome**. A tool span with `status: error` means that tool call failed. It says nothing about the turn's final status. A turn that contains two failing tool calls and ends as `completed` is not a contradiction. It means the agent handled the failures and still produced a valid result.

If you collapse child failures into a root error you lose the distinction between:

- a turn that recovered from failure and succeeded;
- a turn that could not recover and failed.

The portable schema keeps them separate by design. The root span carries its own `status`. Each child span carries its own. The audit reports both. You reconstruct the story by reading the full hierarchy, not by inheriting status downward.

---

## Coverage Gaps Are Data

The preserved event stream from one Codex CLI 0.145.0 run does not contain:

- **Wall-clock duration.** The `codex exec --json` JSONL output does not include a turn duration field. `duration_available: false`.
- **Dollar cost.** No pricing field appears in the event stream. `cost_available: false`.
- **Handoff events.** This was a single-agent run. `handoff_events: 0`. If it had been a multi-agent run and the stream still showed zero, I would still report zero rather than infer one.
- **Skill load events.** The stream does not record which Skill documents were loaded. The current summary has no Skill-load availability key, so this remains an explicit coverage gap rather than a zero count.

None of these gaps are filled by estimation. The audit script's job is to report what it found and name what it did not find. An honest `false` is a coverage result. A guessed number is a different kind of error than the one you were looking for.

When you run a different client or a newer version of the same client, the set of available fields will change. That is the right comparison to make: which fields are present in this stream versus that stream. Not which agent is faster or cheaper—you do not have the data for that comparison.

---

## A Short Privacy Warning

Coding Agent traces can contain prompts, command outputs, tool results, file contents, and reasoning tokens. Any of these may include secrets, personal data, API keys, or sensitive business logic.

Before storing or transmitting a trace:

- Scrub environment variables and tokens from command attributes.
- Review tool result payloads for file contents that should not leave the machine.
- Treat reasoning token text with the same care as prompt text.
- Do not log trace payloads to a shared system without knowing what the agent was doing.

The OpenAI Agents SDK documentation includes a warning about sensitive trace payloads. The same concern applies to any client that records tool inputs and outputs.

The fixture contains a synthetic portable trace and one bounded real Codex stream. The real stream came from a controlled read-only task and contains no secrets in the preserved commands or outputs. Before you capture a trace from your own work, decide where it will be stored and who can read it.

---

## Synthetic vs. Real: A Direct Comparison

| Field | Synthetic portable trace | Real Codex stream |
|---|---|---|
| Spans / events | 9 spans | 17 events |
| Timing on all records | ✓ (synthetic) | ✗ (`duration_available: false`) |
| Token counts | ✓ (synthetic) | ✓ (real) |
| Dollar cost | ✓ (synthetic, USD 0.016) | ✗ (`cost_available: false`) |
| Handoff records | ✓ (1, synthetic) | ✗ (0 observed) |
| Skill load records | ✓ (1, synthetic) | ✗ (not emitted; no availability key) |
| Error spans | 2 (`tool-python`, `tool-python3`) | 2 (exit 127, exit 1) |
| Root status | `ok` | `completed` |
| `synthetic: true` on every record | ✓ | not applicable |

The synthetic trace teaches the contract. The real stream proves the capture path. Neither replaces the other.

---

## Exercise: Compare Fields, Not Performance

The right first exercise with this fixture is not benchmarking. It is field mapping.

1. Pick one other Coding Agent client or a different version of Codex CLI.
2. Set up a controlled read-only task—something that reads a file, runs an existing test, and returns a diagnosis. No writes.
3. Capture the event stream using whatever the client offers (`--json`, SDK hooks, log files).
4. Run your parser against it and record which fields from the portable schema are present and which are absent.
5. Compare your field map to the Codex field map above.

The result is a coverage table, not a leaderboard. You now know exactly what observability you have with each client before you build anything that depends on it. That knowledge is worth more than a performance comparison computed from incomplete data.

---

## Toward Eval-Driven Development

A trace that preserves identity, parent relationships, status, observed usage, and explicit coverage gaps is not just a debugging artifact. It is replayable evidence.

When you capture the same controlled task across multiple runs, the traces become a dataset. You can write assertions against that dataset:

- Did the turn complete?
- Were there more than zero failed tool calls?
- Did the retry sequence resolve within two attempts?
- Did token usage stay below a threshold?
- Did an evaluation span record a pass?

These assertions are quality gates. When a code change causes a regression—the turn fails, the retry count grows, an evaluation span records a failure—the trace shows where the path changed and which recorded evidence preceded it, not just that something broke.

The synthetic trace in the fixture includes an evaluation span for exactly this reason: to show what the signal looks like when you promote traces from observation to evidence. The eleven tests in the fixture are a small version of the same idea applied to the schema itself.

Traces become datasets. Datasets enable quality gates. Quality gates make the development loop replayable. That is Eval-Driven Development for Coding Agents, and it starts with a trace that tells the truth about what it knows and what it does not.

---

## Primary Sources

- OpenTelemetry. "Traces." — request paths, trace hierarchy, and span fields. [https://opentelemetry.io/docs/concepts/signals/traces/](https://opentelemetry.io/docs/concepts/signals/traces/)
- OpenTelemetry. "Spans." — span fields including trace id, span id, parent id, timestamps, attributes, events, links, and status. [https://opentelemetry.io/docs/concepts/signals/traces/#spans](https://opentelemetry.io/docs/concepts/signals/traces/#spans)
- OpenTelemetry. "Semantic Conventions for GenAI systems." — agent invocation, workflow invocation, planning, tool execution, token-usage attributes; current status: **Development**. [https://opentelemetry.io/docs/specs/semconv/gen-ai/](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- OpenAI. "OpenAI Agents SDK — Tracing." — traces for generations, tools, handoffs, guardrails, custom spans; sensitive payload warning. [https://openai.github.io/openai-agents-python/tracing/](https://openai.github.io/openai-agents-python/tracing/)
- OpenAI. "Codex CLI." — project source; local Codex CLI 0.145.0 help was used to verify that `codex exec --json` writes JSONL events to stdout. [https://github.com/openai/codex](https://github.com/openai/codex)

---

*Download the fixture at <a href="/examples/coding-agent-trace-audit.zip">/examples/coding-agent-trace-audit.zip</a>. Continue with [Eval-Driven Development for Coding Agents](/blog/eval-driven-development-for-coding-agents/): how to promote trace records into assertion datasets and run quality gates as part of a Coding Agent workflow.*
