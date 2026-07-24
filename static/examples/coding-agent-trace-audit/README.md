# Coding Agent Trace Audit Fixture

This Python standard-library fixture keeps two evidence classes separate:

1. `portable-trace.example.jsonl` is synthetic data used to teach and test a small client-neutral span contract.
2. `codex-diagnosis-20260723.jsonl` is a preserved real Codex CLI `--json` event stream from one ephemeral, read-only diagnosis run.

The synthetic trace can include timing, dollar cost, a Skill load, a retry, a handoff, and an evaluation because those fields are explicitly marked synthetic. The real Codex record includes only what the client emitted: ordered events, five command executions, two failed commands, four agent messages, final turn status, and token usage. It does not expose span timestamps, duration, dollar cost, a handoff, or a Skill-load event.

## Run the tests

```bash
python3 -m unittest -v test_trace_audit.py
```

## Audit the synthetic portable trace

```bash
python3 trace_audit.py portable \
  --trace portable-trace.example.jsonl
```

## Summarize the real Codex event stream

```bash
python3 trace_audit.py codex \
  --events codex-diagnosis-20260723.jsonl
```

## Capture a new Codex event stream

```bash
codex exec --json --ephemeral \
  --skip-git-repo-check \
  --sandbox read-only \
  -C /path/to/controlled-fixture \
  "Run the focused test, inspect the smallest relevant source file, and diagnose the cause."
```

Redirect standard output to a JSONL file in your own environment. Keep standard error separate because client or MCP diagnostics are not part of the JSON event stream.

## Boundaries

- The portable schema is a tutorial contract, not an official standard.
- OpenTelemetry GenAI semantic conventions are development-stage and are used only to align selected operation names and attributes.
- Do not infer a field that the client did not emit.
- Cost availability requires an explicit numeric `cost`, `cost_usd`, `estimated_cost_usd`, or `total_cost_usd` field; merely mentioning the word “cost” in text does not count as telemetry.
- One Codex run is enough to verify the capture and parser path, not enough for a performance, reliability, or cost comparison.
