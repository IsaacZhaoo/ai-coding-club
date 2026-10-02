---
title: "How to Turn “Add a Filter” into Clear Acceptance Criteria for a Coding Agent"
description: "Turn a small feature request into acceptance criteria for a coding agent, with boundary cases, a copyable task brief, and a verification record."
keywords:
  - "acceptance criteria for coding agents"
  - "AI coding task brief"
  - "acceptance criteria examples"
  - "AI coding workflow"
sidebar_position: 14.1
tags: [tutorial, agent-engineering, workflow]
---

# How to Turn “Add a Filter” into Clear Acceptance Criteria for a Coding Agent

Imagine handing a coding agent this request:

> “Add a maximum-price filter to the product list.”

It sounds simple. In practice, it leaves too much room for assumptions about what “filter” means, how invalid input should be handled, and how to verify the result.

This guide shows you how to translate that vague feature request into precise, checkable acceptance criteria before you ask the agent to implement anything. By the end, you’ll have a copy-paste task brief you can adapt to your own project.

---

## 1. Why We Need Clear Criteria Before Coding

When working with an AI coding agent:

- Ambiguity quickly becomes bugs (or worse: “correct” code that doesn’t match intent).
- The agent can guess behavior, and guesses usually drift from what you actually want.
- You spend more time debugging expectations than writing code.

Good acceptance criteria solve this by defining:

- What the feature must do (behavior rules)
- What it must not do (constraints & error handling)
- How to verify it’s correct (tests/checks)

For a small, concrete feature like “add a maximum-price filter,” we can make this extremely explicit.

---

## 2. The Example We’ll Use

We’ll base the criteria on a clear, minimal example so you can see exactly how each rule maps to behavior.

Assumptions:
- Products are stored as a list with at least: `id`, `name`, and `price_cents`.
- Prices are integers representing cents (no currency symbols, no decimals).
- Original order in the input list is A/B/C/D:
  - A: price_cents = 0
  - B: price_cents = 1990
  - C: price_cents = 990
  - D: price_cents = 5000

Feature request (vague):  
> “Add a maximum-price filter to the product list.”

Our goal: define what that actually means in behavior and tests.

---

## 3. Core Behavior Rules

These are the rules that define “correct” filtering. Write them as non-negotiable requirements.

### 3.1 Optional Parameter with Default Behavior

- The filter uses an optional parameter, e.g. `max_price_cents`.
- When `max_price_cents` is omitted:
  - Return all products.
  - Preserve the original input order (A/B/C/D).

### 3.2 Valid Range and Comparison Logic

- `max_price_cents` must be a nonnegative integer.
- Condition for retention:
  - Keep product if `price_cents <= max_price_cents`.
- Zero is valid:
  - If `max_price_cents = 0`, include products priced at exactly 0.
- Preserve relative order:
  - The output list must contain only the retained products, in their original input order.

### 3.3 Explicit Expected Results

Use concrete test cases to lock down behavior. For our example:

| max_price_cents | Input (A/B/C/D) | Expected Output IDs |
|-----------------|-----------------|---------------------|
| omitted         | A/B/C/D         | A/B/C/D             |
| 0               | A/B/C/D         | A                   |
| 989             | A/B/C/D         | A                   |
| 990             | A/B/C/D         | A/C                 |
| 1990            | A/B/C/D         | A/B/C               |
| 10000           | A/B/C/D         | A/B/C/D             |

If your implementation matches these, you’ve nailed the core behavior.

---

## 4. Error Handling and Invalid Input

This is where most “simple” features go wrong: what happens when the input isn’t perfect?

Define rejection rules explicitly:

- If `max_price_cents` is:
  - negative (e.g., `-1`)
  - fractional/decimal (e.g., `1.5`)
  - any string value, numeric or otherwise (e.g., `"990"`, `"N/A"`)

Then:
- Reject the filtering request.
- Do not perform any filtering.
- Follow the project’s existing error convention (e.g., return an error object, throw an exception, or respond with a specific status).

Key point: distinguish between:

1. Invalid input → reject immediately.
2. Valid input that matches no products → return an empty list as normal, documented result.

---

## 5. Edge Cases You Must Cover

Mention these explicitly in your criteria. They’re easy to miss but very common in production code.

- Empty input list:
  - With any valid `max_price_cents`, return an empty list.
- No matches:
  - Example: input only B/C/D, limit = 0 → result must be an empty list.
  - This is a legitimate success case, not an error. Treat it separately from invalid input.
- Very large limit:
  - Ensure no overflow or type issues when using very large integers.
- Unit consistency:
  - All prices compared in cents. No mixing of dollars/cents or formatted strings unless explicitly parsed and validated.

---

## 6. How to Verify After Implementation

Once the agent implements the feature, use these checks:

### 6.1 Manual Spot Checks

Run through the table in Section 3.3 with your actual data:

- Omit the parameter → do you get all items in original order?
- Try `0`, `990`, `1990` → do the IDs match exactly?

### 6.2 Automated Tests (Minimal Set)

Create a small test suite that covers:

- Default behavior (no filter).
- Exact match at the boundary (`price_cents == max_price_cents`).
- Just below and just above the boundary.
- Zero limit.
- Empty input.
- Invalid inputs: negative, decimal, string.

Each test should:
- Call your filtering function with known input.
- Assert both:
  - The exact resulting list of products (or IDs).
  - That the order matches expectations.

---

## 7. Copy-Paste Task Brief Template

Here’s a ready-to-use brief you can hand directly to an AI coding agent. Replace bracketed parts with your project details.

```markdown
Implement a maximum-price filter for [product list / data set].

1) Input
- Data structure: [e.g., array of objects with {id, name, price_cents}]
- Price unit: integer cents (no decimals, no currency symbols).

2) Behavior
- Parameter: optional max_price_cents.
- If omitted: return all items in their original input order.
- If provided:
  - max_price_cents must be a nonnegative integer.
  - Keep item if and only if: item.price_cents <= max_price_cents.
  - Preserve the original relative order of retained items.
  - Do not modify the original data; return a new list.

3) Validation & Errors
- Reject (do not filter) if max_price_cents is:
  - negative
  - fractional/decimal
  - a string value for max_price_cents
- On rejection, follow our existing error convention:
  - [e.g., throw Error("Invalid max_price_cents") / return {error: true, message: "..."}]

4) Edge Cases
- Empty input list → return an empty list (valid success).
- No matching items → return an empty list (valid success).
- max_price_cents = 0 → include only items priced at exactly 0.
- Very large values → handle as integers without overflow issues.

5) Expected Behavior Examples
Given products A(0), B(1990), C(990), D(5000):
- no max_price_cents → [A, B, C, D]
- 0               → [A]
- 989             → [A]
- 990             → [A, C]
- 1990            → [A, B, C]
- 10000           → [A, B, C, D]

6) Verification
After implementation, these checks must hold:
- Compare outputs against the examples above.
- Ensure order is preserved.
- Confirm that invalid inputs are rejected and not silently ignored.
```

Use this as your specification. Replace examples with your own data shapes or adjust the error convention to match your stack.

---

## 8. After Coding: Record What’s Verified and What Isn’t

Even with great criteria, you should log a quick “verification record” once implementation is done. Keep it simple:

| Test ID | Description | Expected Result | Actual Result | Status | Notes / Follow-Up |
|---------|-------------|-----------------|---------------|--------|-------------------|
| 01 | Omitted limit (default) | A/B/C/D |           |        |                   |
| 02 | Limit = 0 with full set [A,B,C,D] | A only          |           |        |                   |
| 03 | Limit = 989                      | A only          |           |        |                   |
| 04 | Limit = 990                      | A, C            |           |        |                   |
| 05 | Limit = 1990                     | A, B, C         |           |        |                   |
| 06 | Limit = 10000                    | A/B/C/D         |           |        |                   |
| 07 | Limit = -1 (negative)            | request rejected      |           |        |                   |
| 08 | Limit = 1.5 (fractional)         | request rejected      |           |        |                   |
| 09 | Limit = "990" (string)           | request rejected      |           |        |                   |
| 10 | Input [B,C,D] with limit = 0     | Empty list      |           |        |                   |
| 11 | Verify relative order preserved  | Original order  |           |        |                   |
| 12 | Verify no mutation of input data | Unchanged       |           |        |                   |

- ⚠️ Needs verification:
  - [ ] Very large max_price_cents values
  - [ ] Integration with existing pagination or UI components

This short checklist ensures you separate “looks right” from “meets spec.”

---

## 9. Wrap-Up

Turning a small feature request like “add a filter” into clear acceptance criteria is mostly about:

- Pinning down the exact comparison rule (`<=`).
- Explicitly defining what counts as valid vs invalid input.
- Locking in concrete examples that anyone (including an AI agent) can test against.

Use the template above, adapt it to your domain, and you’ll spend significantly less time chasing ambiguity—and much more time shipping working features.

## Related Guides

- [Spec-Driven Development with GitHub Spec Kit](/docs/tutorials/spec-driven-development-guide/)
- [Testing Prompts](/docs/tools/prompt-engineering/templates/testing/)
- [AI Code Review Workflow](/docs/tutorials/ai-code-review-workflow/)
- [Add a Required PostgreSQL Field in Phases](/docs/tutorials/database-required-field-migration/)
