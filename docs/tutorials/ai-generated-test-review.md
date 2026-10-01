---
title: "Green Tests, Dead Behavior: How to Validate AI-Generated Test Quality"
sidebar_label: "Review AI-Generated Tests"
description: "Review AI-generated tests against requirements, inspect assertions and boundaries, and use meaningful mutations to identify missing tests."
keywords: ["AI-generated tests", "test review", "mutation testing", "test assertions"]
sidebar_position: 40
tags: [tutorial, testing, agent-engineering]
---

# Green Tests, Dead Behavior: How to Validate AI-Generated Test Quality

Your task in this review is simple but critical: evaluate the suite of green AI-generated tests for `isUserOldEnough` and determine whether they effectively catch two failure modes—accepting an underage user (age &lt; 18) or rejecting a legitimate adult (age ≥ 18). Look closely at the test data, the mutant outcomes, and any gaps between expected behavior and what’s actually verified.

When you lean on AI to generate or extend your test suite, it’s tempting to trust that “if it passes, it’s good.” But passing is cheap. Meaningful assertions are expensive—and worth paying for. This guide walks you through a concrete review process using a simple age-check function and mutation testing. You’ll walk away with:

- A clear framework for reviewing any AI-generated test set.
- A hands-on mutation-testing example using one tiny edge case that breaks many real tests.
- Precise prompts you can give your AI assistant to close gaps without rewriting everything from scratch.

Let’s start.

---

## 1. The Core Problem: Coverage vs. Behavior

Coverage metrics tell you **which lines ran**. They do not tell you **whether the function behaves as required**. A test suite can be 100% covered and still miss a subtle bug if its assertions are too lenient or poorly chosen.

Key distinction:

- Coverage says: “This code path was executed.”
- Behavior testing says: “When this input arrives, we get the right result for the right reason.”

In your daily work with AI-generated tests, you often see:

- Many green tests.
- High coverage bars.
- A silent gap between what the function actually does and what it should do under edge conditions.

This guide focuses on closing that gap, using a tiny but representative example.

---

## 2. Example: A Deceptively Simple Function

Consider this function, typical of everyday business logic:

```javascript
function isUserOldEnough(user) {
  return user.age >= 18;
}
```

Requirements are straightforward:

- Users aged 17 or younger → `false`.
- Users aged 18 or older → `true`.

The boundary is at 18. That single number matters. Many failing implementations slip by unnoticed because the tests don’t probe that edge.

---

## 3. A Naive AI-Generated Test Suite

AI might generate something like:

```javascript
// test-old-enough.test.js

import { expect } from "chai"; // or your framework of choice

describe("isUserOldEnough", () => {
  it("returns true for an adult", () => {
    expect(isUserOldEnough({ age: 19 })).to.be.true;
  });

  it("returns true for a young adult", () => {
    expect(isUserOldEnough({ age: 25 })).to.be.true;
  });

  it("returns false for a child", () => {
    expect(isUserOldEnough({ age: 10 })).to.be.false;
  });
});
```

At first glance, this looks fine. All tests pass. Coverage is high. But let’s stress-test it with mutation analysis.

---

## 4. Mutation Testing: Stress-Testing Your Tests

Mutation testing intentionally breaks your code and checks whether your tests catch it. If a mutated version runs all tests green, that mutant “survived,” which usually means your tests are too weak for that behavior.

Stryker (https://stryker-mutator.io/docs/) is a popular tool. The core idea:

1. Establish a passing baseline with your current implementation.
2. Introduce small, meaningful mutations.
3. Run the tests against each mutation.
4. Check which tests fail and why.
5. Restore the original implementation afterward.

Let’s manually simulate this on our example.

### 4.1 Baseline: Verify Everything Passes

Before mutating anything, confirm your current setup:

- Implementation: `user.age >= 18`
- Tests: as above
- Result: All green ✅

Note each assertion in terms of input → expected output:

| Input age | Expected result |
|-----------|-----------------|
| 10        | false           |
| 19        | true            |
| 25        | true            |

---

### 4.2 Mutation 1: Change `>=` to `>`

Mutation:

```javascript
function isUserOldEnough(user) {
  return user.age > 18; // MUTATED
}
```

Behavioral change:

- Age 17 → false (same as before)
- Age 18 → **now false** (was true before!)
- Age 19 → true (same)

Run the tests:

- The test with `age: 19` still passes ✅
- The tests with `age: 10` and `age: 25` still pass ✅
- No test failed. Mutant survives ❌

Interpretation:

The original test suite never exercised the critical boundary of exactly 18. The mutation changed behavior at that boundary, but no assertion checked it.

---

### 4.3 Mutation 2: Return true unconditionally

```javascript
function isUserOldEnough(user) {
  return true;
}
```

With this mutant in place, every user is accepted regardless of age. The existing test suite contains three cases: `age=10` (expected false), `age=19` (expected true), and `age=25` (expected true). Against the mutant, the results become actual values `true, true, true`, so the test at age 10 fails (actual true vs expected false) and the suite kills the mutant. The tests at ages 19 and 25 continue to pass.

---

### 4.4 Mutation 3: Change >= to &lt;=

```javascript
function isUserOldEnough(user) {
  return user.age <= 18;
}
```

This mutant reverses the direction of the comparison. Running the existing tests yields actual values `true, false, false` for ages 10, 19, and 25, respectively—directly contradicting the expected `false, true, true`. All three tests fail, so this mutant is also killed. However, if an explicit test for `age=18` existed, both the original rule (`>= 18`) and this mutant (`<= 18`) would return true for that specific input, making the 18-year-old case unable to distinguish between them. This highlights why a single boundary point does not guarantee detection of logic-flipped mutants in surrounding areas.

---

## 5. Designing a Better Test Set

The core rule is: a user is considered old enough if their age is greater than or equal to 18. To verify this cleanly with Chai, use the following minimal test block that covers the key boundary and surrounding values:

```javascript
describe('isUserOldEnough', () => {
  it('rejects an underage user at 17', () => {
    expect(isUserOldEnough({ age: 17 })).to.be.false;
  });

  it('accepts a user exactly at the boundary (18)', () => {
    expect(isUserOldEnough({ age: 18 })).to.be.true;
  });

  it('accepts an adult at 19', () => {
    expect(isUserOldEnough({ age: 19 })).to.be.true;
  });
});
```

With this set in place, the mutants behave as expected: the `>18`-only mutant fails on the 18-year-old test; the constant-true mutant fails on the 17-year-old test; and the `<=18` mutant fails on both the 17 and 19 cases. 

For missing or invalid ages (e.g., `undefined`, null, or an empty object), you must first define the intended behavior—whether to coerce, throw, or default—before writing assertions. As it stands, the current comparison returns false for an empty object, which means a throwing expectation cannot be added without changing the implementation or wrapping the logic in a safer guard.

---

## 6. How to Review Any AI-Generated Test Set

Use this checklist when reviewing tests AI has written for you:

### 6.1 Are the assertions tied to requirements?

- Each assertion should reflect a clear requirement or contract rule.
- Avoid “testing implementation details” like exact property names unless those are part of the API contract.

Example of weak test:

```javascript
it("checks user property", () => {
  expect(isUserOldEnough({ age: 19 })).to.be.true; // okay
  expect(typeof isUserOldEnough).to.equal("function"); // unnecessary detail
});
```

### 6.2 Are boundary values explicitly tested?

- Identify the critical thresholds (e.g., 0, 1, 10, 18, 1000).
- Ensure at least one test uses each threshold as input.

### 6.3 Is there a mix of positive and negative cases?

- Every rule that says “return true for X” should have an equivalent “return false for NOT X.”
- A single positive test does not validate correctness; it just validates alignment with one data point.

### 6.4 Are inputs diverse enough to expose mutations?

- Include:
  - Exact thresholds.
  - Immediate neighbors (threshold ± 1).
  - Typical values.
  - Edge cases defined by your contract (null, empty string, negative, etc.).

### 6.5 Are tests independent of the implementation?

- Use values and expectations that would fail if the function changed logic, not just internal state or property names.
- Ask: “If I refactor this function completely but keep the same behavior, do these tests still make sense?”

### 6.6 Have mocks replaced real behavior?

- If your system calls external services, ensure you’re testing what matters.
- Don’t mock away the very logic you’re supposed to validate unless you’re isolating side effects intentionally.

---

## 7. Practical Workflow: Using Mutation Testing in Your Project

You don’t need a full mutation suite to get value. A lightweight manual process works well, especially when reviewing AI-generated tests.

### Step 1: Run Your Tests Baseline

```bash
npm test        # or your framework command
```

Ensure they pass and note key assertions.

### Step 2: Make One Small, Meaningful Change to the Implementation

Example changes:

- `>= 18` → `> 18` (boundary shift)
- `>= 18` → `true` (logic collapse)
- `age >= 18` → `user.name.length > 2` (completely different logic, same signature)

Do not refactor; mutate. The goal is to see if your tests “scream” when the behavior changes.

### Step 3: Run Tests Again

Watch for:

- Failing assertions that directly relate to the change → good sign.
- Silent failures (e.g., import errors, syntax issues) → stop and fix execution first; don’t interpret them as test quality.

### Step 4: Restore and Re-Verify

Once you’ve gathered insights, restore the correct implementation and confirm tests pass again.

---

## 8. Prompts to Give AI for Focused Improvements

AI can be powerful—but it needs precise context. Instead of “make my tests better,” try prompts like:

### Prompt A: Add Boundary Tests

> Given:
> - Requirement: Users aged 18 or older are considered old enough.
> - Current implementation: `return user.age >= 18;`
> - Existing test: only checks ages 10 and 19.
> 
> Generate three new tests that specifically validate the exact boundary at age 18 and its immediate neighbors, using the same framework (Mocha/Chai/Vitest/etc.).

### Prompt B: Add the Missing Boundary Cases

> “Current test suite covers ages 10 (false), 19 (true), and 25 (true) against the rule age ≥ 18. Write two additional tests using the existing framework that add ages 17 (false) and 18 (true). Then briefly explain which mutation each new test helps detect.”

### Prompt C: Connect Tests to Contract

> Here is my interface contract:
> - Input: `{ age: number }`
> - Output: `boolean`
> - Rule: true if and only if `age >= 18`, otherwise false.
> 
> Review this test set I have (paste it).
> Identify which assertions directly validate the rule and which are incidental. Then add missing tests that would catch a change from `>=` to `>` or to `true`.

When you provide the requirement, current test, and the specific gap (e.g., “boundary at 18 not covered”), AI gives you far more actionable output than with generic requests.

---

## 9. Surviving Mutants ≠ Perfect Tests

If a mutation survives, it doesn’t automatically mean “my tests are useless.” Two important nuances:

### 9.1 Equivalent Mutants

Some mutants are equivalent in behavior for all valid inputs. Different source code, same observable results. No amount of tests can kill them because they’re mathematically indistinguishable within your test domain.

Reference: Stryker’s documentation on equivalent mutants (https://stryker-mutator.io/docs/mutation-testing-elements/equivalent-mutants/).

In practice:
- A surviving equivalent mutant is an artifact of the language and tooling, not a test defect.
- Focus on “non-equivalent” survivors that represent real behavioral differences.

### 9.2 Survivors vs. Blind Spots

A survivor might indicate:
- A missing edge case in tests.
- An assertion that’s too generic.
- Or it might just be an equivalent mutant.

Your job is to:
- Inspect the failing assertions when a mutant is killed (those are your strongest evidence).
- Recognize when a survivor reflects a genuine behavioral gap you care about.
- Avoid treating “all survivors” as a single verdict on test quality.

---

## 10. Common Pitfalls with AI-Generated Tests

Here are specific issues Mark Seemann and others highlight that often show up in AI-generated tests:

- **Ceremonial testing**: Tests that pass but don’t challenge the implementation meaningfully. They read like a ritual rather than a safeguard.
- **Tautological assertions**: Asserting what the function already calculates directly, without validating against an external requirement.
- **Overly narrow input sets**: Only typical values; no boundary exploration.
- **Implementation-leaked assertions**: Checking internal properties or formatting that could change without affecting behavior.

These patterns often emerge when AI is asked to “write tests” without context about domain rules, boundaries, or failure modes.

---

## 11. A Red-Green Mindset for AI-Assisted Testing

https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/ attributes this sequence to Simon Willison: first run a test and watch it fail, then write just enough code to make it pass. For practical development, treat your tests as a living contract—keep them green after each refactor, but ensure the assertions collectively cover the decision boundary and at least one value beyond it. When you trim or move logic, re-run the same failing-test-first cycle rather than relying on intuition alone.

You can adapt this pattern for AI-assisted test generation:

1. See a requirement or a mutation survivor that implies missing behavior.
2. Ask AI to generate a test that would specifically fail if that behavior is wrong.
3. Verify that when the implementation is correct, the test is green; when mutated or buggy, it’s red.

This keeps tests tightly coupled to real, observable behavior instead of drifting into “tests that just run.”

---

## 12. Quick Summary: Your Review Checklist

Use this as a practical cheat sheet the next time you’re reviewing AI-generated tests:

- [ ] Is each assertion tied to a clear requirement or contract rule?
- [ ] Are boundary values (thresholds) explicitly tested?
- [ ] Do we have both positive and negative cases for each rule?
- [ ] Are inputs near critical thresholds included (threshold ± 1)?
- [ ] Is every meaningful wrong behavior (underage acceptance, adult rejection, boundary misclassification) caught by at least one relevant assertion in the suite?
- [ ] Are mocks or stubs used intentionally, not to hide behavior under test?
- [ ] If I run mutation testing mentally (one small change at a time), would any key tests turn red?

If most answers are yes, your test suite is likely doing its job. If several are no, those are your next prompts for AI.

---

## 13. Final Thought: Tests Are Cheap, Wrong Tests Are Expensive

Green tests give false comfort. Mutation testing gives you a concrete stress-test: “If the behavior changes slightly, will someone notice?” Use that insight to guide AI—not to replace human judgment.

Review your tests with an eye on behavior, not coverage. Validate boundaries. Challenge your implementation, not your assumptions. And remember: the goal isn’t perfect test coverage; it’s catching real defects before they reach users.

Happy coding—and testing.

## Related Guides

- [Testing Prompt Templates](/docs/tools/prompt-engineering/templates/testing/)
- [AI Code Review Workflow](/docs/tutorials/ai-code-review-workflow/)
- [Debugging Deep Dive](/docs/course/essential-skills/debugging-deep-dive/)
- [Local Tests Pass, CI Fails](/docs/tutorials/ci-local-test-differences/)
