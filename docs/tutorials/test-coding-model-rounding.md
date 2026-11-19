---
title: "Test Your Coding Assistant: Rounding the Right Way"
description: "Test a coding assistant on two Python rounding cases. Compare its patch, unchanged tests and actual output before deciding whether it fits your work."
tags: ["tutorial", "coding-assistant"]
---

# Test Your Coding Assistant: Rounding the Right Way

First, let’s set the stage. Google just announced Gemini 4 Neon, positioning it as their latest frontier model: [Google announcement](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/). That’s exciting—but does it actually get financial rounding right in a Python script? You’ll find out by testing several models, including Gemini 4 Neon, Claude Code, or whatever else you’re familiar with.

## Step 1: Prepare the Testing Lab
Download the practice material: <a href="/examples/test-coding-model-rounding/rounding-lab.zip" download="rounding-lab.zip">rounding-lab.zip</a>.  
Unzip it into a fresh folder. Inside, you’ll find:
- `amount.py` – The buggy function using `int(float(text)*100)`
- `test_amount.py` – Two unit tests expecting **round halves away from zero**

Run these initial tests to confirm the baseline failure:
```bash
python3 -m unittest -v
```
You should see both tests fail, producing outputs like `100` and `-100` instead of the correct `101` and `-101`.

## Step 2: Evaluate Candidate Models
For each AI model you want to test (e.g., Gemini 4 Neon, Claude, etc.):
1. Copy the folder contents into a new directory.
2. Paste this prompt verbatim into your chat interface:

> Coding exercise. Return only Python code defining cents(text). Change only amount.py. Current: def cents(text): return int(float(text)*100). Input decimal string. Output integer cents, halfway values round away from zero. Existing unmodified tests expect cents("1.005")==101 and cents("-1.005")==-101. No tools are available; do not claim to have run tests.

3. Apply **only** the model’s suggested changes to `amount.py`.
4. Run the unmodified tests again: `python3 -m unittest -v`

## Step 3: Document Everything
Track each model’s behavior using this simple scorecard. Leave one row blank for when you test Gemini 4 Neon.

| Model Tested | Prompt Used | Code Changes | Tests Passed? | Notes (actual outputs, unrequested edits) |
|--------------|-------------|--------------|----------------|-------------------------------------------|
| claude-opus-5[1m] | above | amount.py | 2/2 | Decimal, ROUND_HALF_UP |
| claude-sonnet-5 | above | amount.py | 2/2 | Decimal, ROUND_HALF_UP |
| Gemini 4 Neon|             |              |                |                                           |

## Step 4: Reflect on the Results
What did you learn? Did a model hallucinate tools? Did one silently edit tests? Did it correctly use `Decimal` and `ROUND_HALF_UP` without explanation? These details matter more than raw performance.
