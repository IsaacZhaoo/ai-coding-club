# Local Coding Agent Eval Gate

This standard-library fixture turns one normalized Coding Agent trial into an executable quality gate.

## Files

- `eval_gate.py`: validates and evaluates cases and trials.
- `test_eval_gate.py`: 20 behavioral tests.
- `eval-cases.example.jsonl`: one task and its explicit success contract.
- `baseline-trials.example.jsonl`: one normalized record from the preserved real Codex diagnosis run.
- `regression-trials.synthetic.jsonl`: one deliberately wrong synthetic trial.

## Run

```bash
python3 -m unittest -v test_eval_gate.py

python3 eval_gate.py \
  --cases eval-cases.example.jsonl \
  --trials baseline-trials.example.jsonl

python3 eval_gate.py \
  --cases eval-cases.example.jsonl \
  --trials regression-trials.synthetic.jsonl
```

The baseline exits `0`. The synthetic regression exits `1` and reports `answer_contains_all`.

## Contract

The example case checks:

- final turn status;
- required answer evidence;
- maximum tool calls;
- maximum failed tool calls;
- expected modified-file list.

Tool counts and case limits must be non-negative integers, and failed tool calls cannot exceed total tool calls. The gate also validates the types of the status, answer, required-fragment, and modified-file fields before grading. Non-standard JSON constants are rejected even in fields the grader does not inspect. Invalid inputs return JSON on standard error and exit `2`, distinct from an evaluated regression at exit `1`.

The maximums are local policy for this teaching case. They are not industry benchmarks.

## Boundary

This fixture consumes normalized trial records. It does not parse OTLP, call an Agent, score with another model, or establish reliability from repeated trials. In a real workflow, an adapter would convert preserved traces into this small trial schema, and the dataset would grow from real failures, edge cases, and human-reviewed outcomes.
