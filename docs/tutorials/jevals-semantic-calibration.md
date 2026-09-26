---
title: "Choosing a Semantic Threshold: Using Jevals and Human Labels for Tool Results"
description: "Evaluate whether agents use tool results with jevals and Kev. Add human labels, compare threshold tradeoffs, and apply a chosen threshold to held-out traces."
keywords:
  - "jevals tutorial"
  - "UsedToolResult"
  - "agent evaluation"
  - "semantic evaluation threshold"
  - "human calibration"
sidebar_position: 34
tags: [tutorial, agent-engineering, evals]
---

# Choosing a Semantic Threshold: Using Jevals and Human Labels for Tool Results

If your agent is making tool calls but ignoring what it finds—or worse, contradicting it—substring matching won’t catch that. You need a semantic check and a threshold you can justify.

This tutorial shows how to:

- Use Jevals’ `UsedToolResult` evaluator on a real trace.
- Build a small labeled dataset of traces.
- Calibrate thresholds against human judgments with Kev as the backend.
- Pick and lock in a practical pass threshold for evaluation (not training).

By the end, you’ll be ready to run:  
`evaluate(sample, [UsedToolResult(threshold=0.80)], backend="kev://localhost:8009")`  
with a number you chose consciously.

Jevals 0.1.4 requires Python 3.10 or newer; Kev is already installed and serving requests at localhost:8009, with setup described at https://aicoding.club/docs/tutorials/kev-local-decision-model/.

```bash
python -m pip install "jevals==0.1.4"
```

## Why `UsedToolResult`?

Many agents rely on tool results and then forget them. You want to know:  
“Does the assistant’s final answer actually use the information returned by the tool?”

UsedToolResult evaluates whether a final answer properly incorporates tool-provided information instead of disregarding or contradicting it.

Key properties:

- Score and probability are the same value p (a continuous number in [0,1]).
- The run passes if `p >= threshold`.
- Default threshold: 0.5.
The `UsedToolResult.applicable` check is a lightweight gate that only verifies whether both the `messages` and `tool_results` lists are non-empty; if either is missing or empty, the evaluation is skipped. It does not perform deeper validation such as full trace-schema checks or tool-call pairing verification, serving solely to ensure there is actual content to evaluate before proceeding.

Think of this as your “semantic sanity check” beyond simple keyword overlap.

## A Sample Trace to Evaluate

Save the following as `trace.json`. It includes a realistic weather assistant scenario with one tool call and a final response that partly uses (and partly overreaches) the information:

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search",
        "description": "Web search for live information",
        "parameters": {
          "type": "object",
          "properties": {
            "q": {
              "type": "string"
            }
          }
        }
      }
    }
  ],
  "messages": [
    {
      "role": "system",
      "content": "You are a weather assistant."
    },
    {
      "role": "user",
      "content": "What's the weather in San Francisco today?"
    },
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [
        {
          "id": "c1",
          "type": "function",
          "function": {
            "name": "search",
            "arguments": "{\"q\": \"San Francisco weather today\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "tool_call_id": "c1",
      "content": "San Francisco, today: sunny, high 68F, low 54F, wind 12 mph from the west."
    },
    {
      "role": "assistant",
      "content": "It's sunny in San Francisco today with a high of 68F and a low of 54F. Winds are light from the west, and it will stay sunny all week."
    }
  ]
}
```

Run the evaluator against your local Kev backend:

```bash
jevals --backend kev://localhost:8009 check trace.json \
  --evals agent.used_tool_result --json
```

Important notes:

- `--backend` must appear before the subcommand (`check`).
- Use `kev://localhost:8009` explicitly so Jevals doesn’t fall back to an API-key–based hosted backend.
- `results.used_tool_result.score` and `.probability` should be identical.

In UsedToolResult, both score and probability are set to p, passed evaluates whether p meets or exceeds the default threshold of 0.5, and before interpreting passed you must verify that score is not null, skipped is false, and error is null.

The upstream jevals weather example recorded a UsedToolResult probability of 0.73 and a Grounded score of 0.50 from a Jev run. These figures are attributed results from that example, not expected local Kev values. Source: https://github.com/openlayer-ai/jevals#example-eval-an-agent-run

## Build a Labeled Dataset

Now we introduce human labels. We’ll create a small JSONL file where each line is:

- A full trace object (messages, tools, etc.).
- Plus a top-level field `human_used_tool`: true or false, based on your reading of the same semantic question Jevals asks.

Each completed saved trace receives a top-level human_used_tool boolean assigned by a human reviewer, where true indicates the agent’s answer incorporates tool information without contradiction and false signifies it ignores or contradicts that information.

```python
import json
from pathlib import Path

# Load a single trace from your saved file
sample = json.loads(Path("trace.json").read_text(encoding="utf-8"))

# Set the label based on your review of this conversation
sample["human_used_tool"] = True  # or False, depending on the content

# Append it as one record to your labeled dataset
with open("labeled.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(sample, ensure_ascii=False) + "\n")
```

Use this pattern for each unique trace. Review every conversation thoroughly before writing its label. One trace yields one row; repeatedly appending the same trace does not create a larger dataset. You can collect many traces over time and batch-label them using the same script.

Tips:

- Keep messages, tools, and tool responses exactly as they were generated. Jevals needs them intact.
- The label is your interpretation of “Did the assistant meaningfully use this information?” Not exact wording, not clever tricks—just substance.

## Calibrate with Kev and Jevals

```bash
jevals --backend kev://localhost:8009 calibrate labeled.jsonl \
  --eval agent.used_tool_result --label human_used_tool
```

JeVals prepares a calibration check that uses your saved traces instead of re-running the agent. Kev runs the model in inference only; it never sees the labels. JeVals strips the `human_used_tool` label before sending the prompt to Kev, then compares the returned scores with the original labels. This is an evaluation pass, not a training step.

The script counts only labeled results that have a score; skipped items and errors are excluded. If a trace is missing the `human_used_tool` label, it is also excluded from the calculation. By default it:

- checks thresholds from 0.50 to 0.95 in 0.05 steps,
- includes the currently selected threshold when testing.

## Interpreting the Threshold Table

The core of calibration is a small table that shows how different thresholds balance “passes” vs “misses” against your human labels.

| Field       | Formula    | Meaning                                      |
|-------------|------------|----------------------------------------------|
| auto-pass   | (TP+FP)/N  | fraction of all valid labeled cases passed   |
| wrong passes| FP/N       | fraction of all valid labeled cases incorrectly passed |
| missed passes| FN/N     | fraction of all valid labeled cases incorrectly failed |

N = all valid labeled scored cases; TP = correct passes, FP = wrong passes, FN = wrong failures.

Error shares like `FP / (TP + FP)` show the proportion of passed samples that are wrong.

Additional metrics (when applicable):

- Brier and ECE: how closely Jevals’ probabilities match your binary labels.
- AUROC: ranking quality across thresholds (omitted if only one class is present).

*   Raising the fixed score threshold narrows eligibility: it never adds to passing or falsely passing candidates, and it never reduces false failures.

You choose where to cut off based on how much you want to penalize each kind of mistake.

## Choosing and Applying a Threshold

Once you’ve inspected the table and the raw counts, pick a concrete threshold. Let’s say you decide on 0.80 because:

- It keeps wrong passes low (FP small).
- You can tolerate missing a few borderline examples in early development.
- Your agent runs frequently, so you want a clear pass/fail signal from evaluation time.

Now explicitly configure that threshold when evaluating any trace (or batch):

```python
import json
from pathlib import Path
from jevals import evaluate
from jevals.agent import UsedToolResult

sample = json.loads(Path("trace.json").read_text(encoding="utf-8"))
report = evaluate(
    sample,
    [UsedToolResult(threshold=0.80)],
    backend="kev://localhost:8009"
)
print(report.used_tool_result.score, report.used_tool_result.passed)
```

Evaluate different held-out traces using evaluate_dataset with UsedToolResult(threshold=0.80), where 0.80 is the value selected from the reader’s calibration. Compare these valid results against human judgments on those held-out traces to assess alignment and performance under strict operational criteria.

```python
from jevals import evaluate_dataset
from jevals.agent import UsedToolResult

report = evaluate_dataset(
    "review.jsonl",
    [UsedToolResult(threshold=0.80)],
    backend="kev://localhost:8009",
)
report.write_jsonl("review-results.jsonl")
```

Each line in `review-results.jsonl` contains:

- The original input index (preserving order),
- `results.used_tool_result.score`,
- `results.used_tool_result.passed`,
- `results.used_tool_result.skipped` and `results.used_tool_result.error` flags.

To assess quality, compare these scored results against independent human labels on the held-out traces. This reveals false passes/fails and lets you tune the threshold.

Note: The threshold configuration applies only to this evaluator instance. If you use the CLI’s built-in mode, it starts at the default `0.5` and does not inherit any Python-level setting. Changing backend, model, or labeling rule requires a fresh comparison run—and keep this threshold distinct from your model training logic.

Key points:

- The numeric threshold is an application choice derived from your own human labels and your Kev judge behavior.
- This step is purely for evaluation configuration, not training or model updates.
- Always double-check with held-out traces:
  - Confirm the distribution of false passes vs false failures.
  - Watch for edge cases where the assistant uses some data but not all, or paraphrases heavily.

If you change anything—Kev backend, model temperature, labeling rule—you should re-run calibration and potentially adjust the threshold.

## Best Practices and Common Pitfalls

- Use separate held-out traces: never evaluate your threshold on the same data you used to choose it without checking generalization.
- Inspect state and report: When a schema change or mismatched `tool_call_id` occurs, it isn’t guaranteed to cause a skip or error. It can silently alter the evaluator’s view of the conversation. Preserve all calls and results, then inspect the resulting state and include that in your report.
- Don’t trust skipped/error counts as failures: investigate before concluding a trace “failed.”
- Score independently:  
  - `UsedToolResult`: Did the solution meaningfully use the available tool information?  
  - Grounded evaluates whether answer claims are supported by evidence drawn from compact tool call results when available, or from supplied contexts otherwise.

## Wrapping Up

You now have an end-to-end workflow:

1. Inspect a trace with `UsedToolResult` to see baseline behavior.
2. Build a small labeled JSONL set reflecting your real-world notion of “tool use.”
3. Calibrate against Kev to see how thresholds map to your labels.
4. Pick a threshold that fits your tolerance for false positives and misses.
5. Apply that threshold explicitly in your evaluation pipeline.

This is a lightweight, offline evaluation configuration you can iterate on quickly as your agent and its tooling evolve.

## Related Guides

- [Run Kev Locally: A Choice Classification for Support Tickets (Apple Silicon Tutorial)](/docs/tutorials/kev-local-decision-model/)
- [Coding Agent Evals Guide: Turn Traces into Datasets and Quality Gates](/docs/tutorials/coding-agent-evals-guide/)
