---
title: Testing Prompts
description: Prompt templates for writing tests and verifying behavior
---

import FAQSchema from '@site/src/components/FAQSchema';

# Testing Prompt Templates

**Turn requirements into tests that prevent regressions**

<FAQSchema
  items={[
    {
      question: 'What should I include to get good tests?',
      answer: 'The function/module under test, expected behavior, edge cases, and the test framework used in the repo.',
    },
    {
      question: 'How do I avoid flaky tests?',
      answer: 'Ask for deterministic tests, explicit timeouts, and stable test data fixtures.',
    },
    {
      question: 'What is a good minimum?',
      answer: 'Happy path + at least 2 edge cases + one regression case for the bug you saw.',
    },
  ]}
/>

---

## 1) Unit tests (happy path + edge cases)

```text
Write unit tests for the following code.

Repo details:
- Language: [LANG]
- Test framework: [Jest/Vitest/Pytest/etc]

Requirements:
- Cover happy path
- Cover at least 3 edge cases
- Use descriptive test names
- No network calls

Code:
[PASTE CODE]
```

## 2) Regression test for a specific bug

```text
I fixed a bug. Write a regression test that would fail before the fix and pass after.

Bug:
- Expected: [EXPECTED]
- Actual before fix: [ACTUAL]
- Reproduction steps: [STEPS]

Code under test:
[PASTE CODE]

Return:
- The test file path you would add
- The exact test cases
```

## 3) Test plan before implementing

```text
Before I implement this feature, write a test plan.

Feature:
[DESCRIBE FEATURE]

Constraints:
- Include unit + integration tests where relevant
- List key edge cases
- Note any mocking/stubbing needed
```

## 4) Integration test for API or workflow

```text
Write an integration test for this workflow:
[WORKFLOW DESCRIPTION]

Constraints:
- Use the repo's existing test tooling
- Prefer testing behavior over implementation details
- Include cleanup/teardown
```

## 5) Improve coverage with meaningful cases (not filler)

```text
Given these existing tests, propose improvements to increase coverage meaningfully.

Existing tests:
[PASTE OR DESCRIBE]

Code under test:
[PASTE OR LINK PATH]

Output:
- 5-10 additional test cases that add real value
- Why each case matters
```

---

## FAQ

### What should I include to get good tests?

Include the code, expected behavior, edge cases, and the test framework used in the repo.

### How do I avoid flaky tests?

Ask for deterministic tests, stable fixtures, and no real network/time dependencies.

### What is a good minimum?

Happy path + multiple edge cases + a regression case for the bug you saw.

