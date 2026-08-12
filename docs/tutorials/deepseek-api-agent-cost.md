---
title: "DeepSeek API Cost Calculation: Budgeting Cache, Output, and Agent Retries"
description: "Build recalculable DeepSeek API cost records from cache-hit input, cache-miss input, output, retries, and human review time."
keywords:
  - DeepSeek API cost
  - DeepSeek API pricing
  - Coding Agent cost tracking
  - AI Agent token cost
  - DeepSeek cache pricing
  - Agent retry budget
sidebar_position: 32
tags: [tutorial, agent-engineering, deepseek, api-cost]
---


# DeepSeek API Cost Calculation: Budgeting Cache, Output, and Agent Retries

On August 6, 2026, the DeepSeek English pricing page stated that overall API pricing is planned to increase in the near future, with the increase expected to be significant. The final prices, effective date, and mechanism have not been published. Until an official notice lands, no reliable "cost after the increase" can be calculated.

What you can do right now is make your existing agent logs recalculable. That means preserving raw usage per call, associating every call with a task, and applying a dated price table. If you do that today, you can apply any new price table to historical records the moment the official notice is published—without re-running anything.

By the end of this article you will have a minimum task-level record containing: task type and task ID; model; raw `usage` JSON; normalized cache-hit input, cache-miss input, and output token counts; call index, success state, retry state, and failure reason; price-table version and calculation timestamp; and separately recorded human review or rework time.

---

## Step 1 — Preserve a Recalculable Raw Record

Many cost investigations fail because the logs discard the data needed to explain individual calls. If your database stores only a monthly total or a formatted dollar string, you cannot break the cost down by task, model, or cache behavior, and you cannot recalculate when a price changes.

The minimum fields to log for every API call are:

| Field | Notes |
|---|---|
| `task_type` | e.g. `code_review`, `doc_gen` |
| `task_id` | groups calls that belong to the same user task |
| `call_id` | response ID from the API, or a caller-generated UUID |
| `call_index` | 0-based position within the task (0 = first attempt) |
| `model` | exact model string from the response |
| `timestamp_utc` | when the request completed |
| `success` | boolean |
| `retry` | boolean |
| `failure_reason` | null or a short string |
| `usage_raw` | the full `usage` object from the response, stored as JSON |

### Chat Completions field names

The Chat Completions API returns a `usage` object with:

```json
{
  "prompt_tokens": 1000000,
  "prompt_cache_hit_tokens": 800000,
  "prompt_cache_miss_tokens": 200000,
  "completion_tokens": 100000
}
```

Here `prompt_tokens = prompt_cache_hit_tokens + prompt_cache_miss_tokens`. The breakdown is already in the response; you just have to save it.

### Responses API field names

The Responses API uses a different structure:

```json
{
  "input_tokens": 1000000,
  "input_tokens_details": {
    "cached_tokens": 800000
  },
  "output_tokens": 100000
}
```

Cache-miss input is derived: `input_tokens − input_tokens_details.cached_tokens`. The Responses API does not surface a `cache_miss_tokens` field directly.

### Normalize to internal fields

Because the two APIs use different field names, map both to three internal fields before you store anything:

```
hit_input_tokens  = chat: prompt_cache_hit_tokens
                    responses: input_tokens_details.cached_tokens

miss_input_tokens = chat: prompt_cache_miss_tokens
                    responses: input_tokens − cached_tokens

output_tokens     = chat: completion_tokens
                    responses: output_tokens
```

Store the raw `usage` object alongside these normalized fields. The raw object is your audit trail; the normalized fields are for calculation. Do not guess or infer one from the other.

---

## Step 2 — Apply a Versioned Three-Path Price Table

The following table is the current DeepSeek [pricing page](https://api-docs.deepseek.com/quick_start/pricing) as of **2026-08-06**, in USD per 1 million tokens. Label it with that date.

| Model | Cache-hit input | Cache-miss input | Output |
|---|---:|---:|---:|
| `deepseek-v4-flash` | $0.0028 | $0.14 | $0.28 |
| `deepseek-v4-pro` | $0.003625 | $0.435 | $0.87 |

Think of these three columns as separate utility meters on the same call. Hit input, miss input, and output each tick at a different rate. A retry that sends the same long system prompt through the pipeline runs all three meters again—possibly at the miss rate if the cache was not warm.

For `deepseek-v4-flash`, the miss/hit input price ratio is **50×**. For `deepseek-v4-pro` it is **120×**. That ratio is why the cache state matters when calculating a single call. It is not a claim about which cost component dominates your workload; that depends on your actual call patterns.

### Cost formula for one call

```
cost = (hit_input_tokens / 1_000_000) × hit_price
     + (miss_input_tokens / 1_000_000) × miss_price
     + (output_tokens / 1_000_000) × output_price
```

Calculate the three terms separately, then sum. Never blend hit and miss tokens into a single "input" line before applying a price; you will get an incorrect result.

### Worked example — price-table arithmetic only

This is not a real API run or a typical workload. It is arithmetic applied to the 2026-08-06 price table so the formula is visible.

**Scenario A — `deepseek-v4-flash`, warm cache**

- 0.8M cache-hit input tokens
- 0.2M cache-miss input tokens
- 0.1M output tokens

```
0.8 × $0.0028  =  $0.00224
0.2 × $0.14    =  $0.02800
0.1 × $0.28    =  $0.02800
                  ─────────
Total            $0.05824
```

**Scenario B — same 1M total input and 0.1M output, all misses**

```
1.0 × $0.14    =  $0.14000
0.1 × $0.28    =  $0.02800
                  ─────────
Total            $0.16800
```

With the same output quantity, Scenario B is approximately **2.88×** Scenario A. The output volume is identical in both scenarios; the difference is entirely in cache state.

---

## Step 3 — Aggregate Calls into a Task

A task is a unit of work that may require several API calls: the first attempt, a retry on parse failure, a follow-up call to fix an incomplete output. Each of those calls has its own `usage`, and each one has a real cost.

Rules for aggregation:

1. **Group by model and price-table version before summing.** If a task started before a price change and finished after, the two segments must stay in separate rows. Blending them produces numbers that can be reproduced only if you remember when the price changed.

2. **Keep failed and retried calls.** A failed call that received tokens still costs money. A retry is a separate call with its own usage. If you discard them, your task-level total is wrong and you cannot identify which task types are expensive because of high retry rates.

3. **Do not invent an average retry count.** Your logs have the actual call index for each call. Use that; it is more useful than any assumed average.

The task-level record is the sum of individual call records that share the same `task_id`, filtered to the same `model` and `price_table_version`. A task may have entries for multiple models if it switched mid-run; keep them separate.

---

## Step 4 — Record Human Review and Rework Separately

An API bill measures tokens sent and received. It does not measure whether the output was useful, whether a human had to read it carefully, or whether the human had to rewrite part of it. Those are real delivery costs and they belong in a separate record.

Recommended fields for a human review record:

| Field | Notes |
|---|---|
| `task_id` | links back to the API call records |
| `review_minutes` | actual minutes spent reading the output |
| `rework_reason` | short string if output required changes, null otherwise |
| `reviewer` | role or ID, not personal data |
| `timestamp_utc` | when the review happened |

Two things not to do:

- **Do not invent an hourly rate** and multiply it by review minutes to get a dollar figure. You do not have a single agreed rate, and the result would create false precision that obscures the underlying data.
- **Do not merge human time into the API cost total.** They are different units. Keep them adjacent in your reporting schema, not combined into a single column.

The reason this matters at budget time: an agent task with a very low API cost but a high review-minute count is not actually cheap. A task with a high API cost but zero rework might be. You cannot tell without the separate record.

---

## Step 5 — Recalculate When the Official Price Changes

When the official price change is announced:

1. **Add a new price-table version.** Give it a version label and the effective date. Never overwrite the existing `2026-08-06` version. Historical records must remain recalculable at the price that was in effect when they were created.

2. **Apply old and new versions to the same historical task records.** Run the cost formula for each record under both versions. The difference is the actual impact on your workload—not a theoretical one based on estimated token counts.

3. **Compare by task type, not only by monthly total.** A price change may affect `code_review` tasks differently from `doc_gen` tasks if they have different cache-hit rates or different output lengths. A monthly total hides that variation.

4. **If you switch provider, map fields before comparing prices.** Different providers use different usage field names and different billing boundaries. Map each provider's fields to your internal `hit_input_tokens`, `miss_input_tokens`, and `output_tokens` before applying any price table. Comparing raw field values across providers without mapping first produces numbers that look precise but are not comparable.

---

## Cache Boundaries

DeepSeek [context disk caching](https://api-docs.deepseek.com/guides/kv_cache) is enabled by default for all users; there is nothing to turn on. When it works, it can substantially reduce cost on long system prompts that repeat across calls.

Understanding what it actually guarantees:

- **Prefix matching, not full-text matching.** A cache hit requires a complete match with a persisted cache-prefix unit. A small change early in the prompt can stop a later request from fully matching that prefix unit.
- **Best effort, not guaranteed.** The documentation is explicit that the cache does not guarantee a 100% hit rate. Treat cache hits as observed outcomes from your usage logs, not as a baseline to assume.
- **Construction takes seconds.** The official guide says cache construction takes seconds. Do not assume an immediate retry will hit; verify the returned usage.
- **Cleanup after hours to days.** Unused cache is normally cleared within hours to days. A long idle period between tasks on the same prefix may result in a miss.

The implication for logging: never pre-compute an "expected cache hit" percentage and apply it to your token estimates. Record the actual `prompt_cache_hit_tokens` or `cached_tokens` from each response and use those numbers.

---

## Five Common Mistakes

### 1. Estimating tokens from character counts

A character-based token estimate might be useful for quick planning. It is not useful for a cost record. Actual token counts come from the API response. Save them. If you need to estimate before a call completes, label it explicitly as an estimate and replace it with the actual figure once the response arrives.

### 2. Treating default caching as a guaranteed hit

"Caching is on by default" does not mean every call will hit. Prefix changes, construction lag, and cleanup all reduce hit rates below 100%. An agent that calculates expected cost assuming 80% cache hits without checking actual usage is not doing cost accounting; it is guessing.

### 3. Saving only the final successful call

Agents retry. Each model retry that returns usage consumes tokens. If your logging fires only on success, you are missing intermediate model calls that returned usage.

### 4. Equating a low API bill with low delivery cost

API cost is one input. Review minutes, rework, and blocked downstream work are others. A workflow with a low API cost but a high review burden is not inexpensive. Log them separately so the full picture is visible.

### 5. Hard-coding prices without historical versions

Any system that stores the current price in a constant and applies it to every record—past and future—will produce wrong historical numbers the moment the price changes. Version the table. Associate every calculation with the version used.

---

## Minimum Action Checklist

Start with one existing real task from your current logs. Do not spend money to run a new experiment for this article.

- [ ] Find a task with a known `task_id` and retrieve its API call records.
- [ ] Confirm that raw `usage` was preserved. If it was not, note the gap—that is the first thing to fix in your logging layer.
- [ ] Create a price-table entry labeled `2026-08-06` with the values from the table in Step 2.
- [ ] Calculate the cost of that task using the three-path formula: hit input + miss input + output.
- [ ] Store the result alongside the price-table version label and the calculation timestamp.
- [ ] Preserve the formula, not just the dollar figure. The formula is what makes the record recalculable.
- [ ] After the official price notice is published, add a new price-table version entry with the announced date and rerun the same historical task record. The comparison is your actual impact, not a projected one.

Logging systems differ in structure and tooling. This checklist does not estimate how long any step will take.

---

## A Note on Open Weights

The [DeepSeek V4-Flash model weights](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731) are released under the MIT license. That is a fact about intellectual property, not a cost guarantee. The MIT license does not set hosted API prices and does not establish that self-hosting is less expensive than the API. If you are evaluating self-hosting, the relevant inputs are infrastructure cost, operational overhead, and throughput requirements—none of which are derivable from the model license.

---

## Quick Reference

**Current price table — version `2026-08-06`**

| Model | Cache-hit input | Cache-miss input | Output |
|---|---:|---:|---:|
| `deepseek-v4-flash` | $0.0028 / 1M | $0.14 / 1M | $0.28 / 1M |
| `deepseek-v4-pro` | $0.003625 / 1M | $0.435 / 1M | $0.87 / 1M |

**Formula**

```
cost = (hit / 1M × hit_price)
     + (miss / 1M × miss_price)
     + (out / 1M × out_price)
```

**Minimum task record fields**

`task_type` · `task_id` · `call_id` · `call_index` · `model` · `timestamp_utc` · `success` · `retry` · `failure_reason` · `usage_raw` · `hit_input_tokens` · `miss_input_tokens` · `output_tokens` · `price_table_version` · `calculated_cost` · `calculation_timestamp`

**Separate human review fields**

`task_id` · `review_minutes` · `rework_reason` · `reviewer` · `timestamp_utc`

---

If you are setting up the DeepSeek API for the first time and need to configure authentication and a client, the [AI Coding Club DeepSeek × Codex Tutorial](https://aicoding.club/docs/tutorials/deepseek-v4-codex-cli/) covers installation and configuration. This article picks up after the client is running and focuses on what to log and how to calculate cost from those logs.

**Official references**

- [DeepSeek API Pricing](https://api-docs.deepseek.com/quick_start/pricing)
- [KV Cache Guide](https://api-docs.deepseek.com/guides/kv_cache)
- [Token Usage](https://api-docs.deepseek.com/quick_start/token_usage)
- [Chat Completions API](https://api-docs.deepseek.com/api/create-chat-completion)
- [Responses API](https://api-docs.deepseek.com/guides/responses_api)
