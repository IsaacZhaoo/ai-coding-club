---
title: "Agent Skills Testing Guide: Measure Trigger Precision, False Positives, and Context Cost"
description: "Audit an Agent Skills loadout with specification checks, catalog budgets, overlap detection, near-miss prompts, and real activation records."
keywords:
  - agent skills testing
  - skill trigger precision
  - agent skills false positives
  - skill description overlap
  - agent skills context cost
sidebar_position: 21
tags: [tutorial, coding-assistant, agent-engineering, agent-skills]
---

# Agent Skills Testing Guide: Measure Trigger Precision, False Positives, and Context Cost

*by Youguang*

---

[A previous post](/blog/too-many-agent-skills/) argued that a Skill catalog is a routing surface, not a trophy shelf. The argument stops there. It does not tell you how to know whether the routing actually works, how much metadata the catalog loads at Agent startup, or what happens when three descriptions compete for the same prompt.

This tutorial adds the loadout-level view. You will audit every Skill, measure the catalog, test positive and near-miss prompts across competing descriptions, and replace static guesses with activation records from the real Agent client.

> **Center:** The useful unit of Agent Skills quality is the whole loadout: validate every Skill, measure the catalog, test positive and near-miss prompts across competing descriptions, then replace static guesses with activation records from the real Agent client.

The companion fixture is published at <a href="/examples/agent-skills-loadout-audit.zip">/examples/agent-skills-loadout-audit.zip</a>. It contains five valid Skills and 20 JSONL cases. Its tests, audit, and scoring commands use only the Python standard library and make no external API calls.

---

## Four Layers, One Audit

Before running anything, name the four things you are actually measuring. Conflating them costs time.

| Layer | Question | Tool |
|---|---|---|
| **Specification validity** | Does each Skill satisfy the format contract? | `skills-ref validate` + fixture validator |
| **Catalog cost** | What local metadata-cost estimate does the whole catalog produce? | Character-count heuristic in the fixture |
| **Static description competition** | Do descriptions overlap enough to confuse a keyword router? | Pairwise overlap detector in the fixture |
| **Real Agent activation** | Which Skill did the Agent actually load, given a real prompt? | Client evidence recorded as activation JSONL + scorer |

The fixture implements the first three layers and scores records supplied for the fourth. It does not capture every Agent client's activation events for you. `skills-ref validate` is the official reference validator; the fixture complements it and does not replace it. The same split applies to the official description and output-evaluation guides: they teach you how to improve one Skill in isolation. This tutorial teaches the loadout view.

---

## Run First, Explain Later

I prefer to run the code before explaining it. Here is the test suite:

```bash
python3 -m unittest -v test_skill_loadout.py
```

All ten tests pass. Then the audit:

```bash
python3 skill_loadout.py audit \
  --skills-dir skills \
  --cases cases.jsonl \
  --max-estimated-tokens 300
```

Key values from the JSON report:

```text
catalog.skill_count = 5
catalog.catalog_chars = 1065
catalog.estimated_catalog_tokens = 267
catalog.overlap_pairs = []
budget_passed = true

lexical_smoke_test.total = 20
lexical_smoke_test.correct = 18
lexical_smoke_test.accuracy = 0.9
lexical_smoke_test.failures = [
  near-api-implementation → api-documentation
  near-python-debug → python-test-fixer
]
```

The budget passes. The smoke test mostly works. Two prompts are routed wrong. Keep those two failures in view — they are the point.

---

## Specification Validity

The official format contract is stricter than most people read it once:

- `SKILL.md` must exist as a direct child of the Skill directory.
- `name` in the YAML frontmatter must match the parent directory name.
- `name` is 1–64 characters, lowercase alphanumeric and hyphens, no leading, trailing, or consecutive hyphens.
- `description` is 1–1,024 characters and should explain what the Skill does and when to use it.

The fixture validator checks these boundaries and emits per-Skill diagnostics. This is the relevant code from `skill_loadout.py`:

```python
if len(name) > 64 or re.fullmatch(
    r"[a-z0-9]+(?:-[a-z0-9]+)*", name
) is None:
    diagnostics.append(Diagnostic("invalid_name", path, "..."))
if name != path.parent.name:
    diagnostics.append(Diagnostic("name_mismatch", path, "..."))
if len(description) > 1024:
    diagnostics.append(Diagnostic("description_too_long", path, "..."))
```

Missing names and descriptions are handled immediately before these checks. Nothing here is novel. What changes at loadout scale is that you run the checks across every Skill in one pass, so a single malformed entry does not hide behind a green result somewhere else in the suite.

---

## Catalog Cost

Progressive disclosure means the Agent loads catalog metadata — names and descriptions — at startup before it decides whether to load a full `SKILL.md`. That metadata is not free, but surrounding context management can differ between clients.

The fixture counts both names and descriptions, then applies a four-characters-per-token heuristic:

```python
catalog_chars = sum(
    len(skill.name) + len(skill.description)
    for skill in skills
)
estimated_catalog_tokens = math.ceil(catalog_chars / 4)
```

For the five-Skill fixture: `1065 / 4 = 266.25`, rounded up to 267. The budget passes at 300 tokens.

This is a local heuristic. It is not an exact tokenizer, not a billing value, and not a substitute for counting against the real model context. Its job is to provide a transparent catalog-budget signal that you can keep stable in CI while the loadout changes.

---

## The Case Set: Positive and Near-Miss Negative

The fixture ships 20 JSONL cases: 10 positive, 10 near-miss negative. Here is one of each:

```jsonl
{"id":"python-pytest-failure","prompt":"Fix the failing pytest assertions in tests/test_api.py and verify the focused test.","expected_skill":"python-test-fixer","split":"train"}
{"id":"near-api-implementation","prompt":"Implement a new API endpoint for creating invoices and add authentication.","expected_skill":null,"split":"train"}
```

The near-miss negatives are the more important half. The API implementation prompt shares several terms with `api-documentation`, but its intent is implementation rather than documentation. A lexical router fires. In the preserved real-client smoke run, Codex correctly decided that no listed Skill fit. Your test set needs to capture that gap.

The official description guide recommends about 20 realistic trigger queries, mixing 8–10 positive and 8–10 near-miss negative cases, repeated runs, and separate train and validation sets. The `split` field in each case is there precisely for that: you tune against `train` cases and evaluate against `validation` cases. Cross-contaminating them produces optimism.

---

## Pairwise Description Overlap

The overlap detector computes token-Jaccard similarity between every pair of descriptions. The fixture first normalizes terms and removes a small stop-word set:

```python
left_terms = _description_terms(left.description)
right_terms = _description_terms(right.description)
union = left_terms | right_terms
similarity = (
    len(left_terms & right_terms) / len(union)
    if union else 0.0
)
```

The audit command defaults to an overlap threshold of `0.45`, configurable with `--overlap-threshold`. If a pair meets or exceeds that threshold, the report includes both names and the rounded score. The bundled five-Skill catalog reports no overlap pairs at the default threshold.

This does not mean the Agent will route correctly — the Agent is not a Jaccard calculator. It means two descriptions share enough normalized vocabulary to deserve inspection and near-miss cases.

Pairwise overlap is O(n²). For large catalogs, treat it as an exploratory diagnostic rather than assuming one threshold is a universal gate.

---

## The Lexical Smoke Test Is Not the Agent

The audit's lexical smoke test routes each case using term intersection against all descriptions. It gets 18 of 20 right. Two fail:

1. **“Implement a new API endpoint for creating invoices and add authentication.”** routes to `api-documentation`. The expected answer is no Skill.
2. **“Debug this Python cache bug; there is no failing test yet.”** routes to `python-test-fixer`. The expected answer is no Skill.

For the first case, the smoke router finds four shared terms: `api`, `authentication`, `creating`, and `endpoint`. For the second, it finds `failing` and `python`. The simple score does not interpret the implementation intent in the first prompt or the negated test condition in the second.

These failures are features of the lesson, not bugs to fix. They show exactly where lexical matching diverges from the observed Agent decisions. Do not mistake a high smoke-test accuracy for evidence of correct Agent behavior. The smoke test is a fast static scan for obvious description competition and gross misroutes.

---

## Real Activation Records

The only way to know what the Agent actually does is to record what the Agent actually does. The fixture's portable JSONL contract uses the case id, run number, selected Skill, and client label:

```jsonl
{"case_id":"python-pytest-failure","run":1,"selected_skill":"python-test-fixer","agent":"codex-cli"}
{"case_id":"near-api-implementation","run":1,"selected_skill":null,"agent":"codex-cli"}
```

Use `null` when no Skill was activated. Evidence that a client actually read a `SKILL.md` belongs in the preserved client log or verification record; the compact activation row stores the scorable routing decision.

Score the records against the case set:

```bash
python3 skill_loadout.py score \
  --cases cases.jsonl \
  --activations activations.codex-smoke-20260723.jsonl
```

The preserved Codex smoke set has two runs: one positive pytest prompt where Codex stated it was using `python-test-fixer` and read that `SKILL.md`, and one near-miss API implementation prompt where Codex explicitly said no listed Skill fit and did not load `api-documentation`. The activation-log path and scoring mechanics work. Two runs are not a performance result.

The fixture also ships `activations.example.jsonl`. That file is synthetic data for testing the scorer itself. Do not present it as measured Agent behavior.

### The Metrics

The scorer returns three rates and five counts. The core routing metrics are:

| Metric | Definition |
|---|---|
| **Accuracy** | Exact routing decisions / total recorded runs |
| **Precision** | Correct Skill fires / total Skill fires |
| **Recall** | Correct Skill fires / total runs where a Skill was expected |
| **False activation** | A Skill fired when `expected_skill` was null |
| **Missed activation** | No Skill fired when `expected_skill` was not null |
| **Wrong Skill** | A Skill fired but it was not the expected one |

Precision answers: when a Skill fired, how often was it the expected Skill? Recall answers: when a Skill was expected, how often did it fire? You want both to be high, but a catalog tuned only for recall can acquire false activations. A catalog tuned only for precision can miss valid triggers. Near-miss negative cases are the main evidence for precision failures.

---

## Failing the Budget in CI

The `--max-estimated-tokens` flag sets a catalog budget. If `estimated_catalog_tokens` exceeds the limit, the JSON report sets `budget_passed` to `false`; for an otherwise valid loadout with no diagnostics, the command exits with code `2`.

The bundled catalog passes at 300 and fails at 250:

```bash
python3 skill_loadout.py audit \
  --skills-dir skills \
  --max-estimated-tokens 250
```

Put the flag in the CI command. If it is absent, no maximum is configured and the budget check passes by definition.

The heuristic remains local. Your actual model will tokenize differently. If real token cost matters for billing or context limits, measure it with the real tokenizer or provider instrumentation. The fixture's estimate is a stable warning signal, not a substitute for that measurement.

---

## Extension Exercise

Before moving on, add one Skill and one prompt to your local copy:

1. Create a new Skill whose description deliberately overlaps with `api-documentation`, for example a Skill focused on HTTP request examples.
2. Add one realistic case near the boundary between the two descriptions and set the `expected_skill` you actually want.
3. Re-run the audit and inspect both `catalog.overlap_pairs` and the lexical routing result.

Do not assume in advance that the new pair will cross the default `0.45` threshold or that the lexical router will choose a particular Skill. The exercise is to observe how description wording, the configured threshold, and the case text change the report.

The fixture is small by design. Five Skills are enough to learn the shape of the problem before applying the same contract to a real loadout.

---

## Sources

- [Agent Skills specification](https://agentskills.io/specification)
- [Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions)
- [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills)
- [`skills-ref` reference validator](https://github.com/agentskills/agentskills/tree/main/skills-ref)
- Companion fixture: <a href="/examples/agent-skills-loadout-audit.zip">/examples/agent-skills-loadout-audit.zip</a>

---

## What Comes Next: Observability

When activation logs are easy to capture, the audit above closes the routing-evidence loop. When they are not — when the Agent runs in a pipeline, uses multiple tools, hands off between Skills, or fails in a way that does not surface in the final output — the engineering problem is different. You need traces, not just activation records. You need to see which tool was called, which Skill was loaded, how many tokens each step consumed, and where the failure originated.

That is the [Coding Agent Observability](/docs/tutorials/coding-agent-observability-guide/) problem. The activation JSONL format here is a minimal starting point: structured, portable, scorable. The next step is connecting it to a trace that covers the full run — tools, Skills, handoffs, cost, and failures — so that a bad output has a causal chain you can follow rather than a mystery you have to reproduce.
