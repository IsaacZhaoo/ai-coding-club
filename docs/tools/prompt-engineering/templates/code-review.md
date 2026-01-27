---
title: Code Review Prompts
description: Prompt templates for actionable code reviews and risk checks
---

import FAQSchema from '@site/src/components/FAQSchema';

# Code Review Prompt Templates

**Get actionable feedback: bugs, risks, and missing tests**

<FAQSchema
  items={[
    {
      question: 'What input produces the best reviews?',
      answer: 'A diff or the changed files, plus context: expected behavior, constraints, and how it was tested.',
    },
    {
      question: 'How do I get less generic feedback?',
      answer: 'Ask for concrete findings with file/line references and a prioritized list of risks.',
    },
    {
      question: 'What should a review always include?',
      answer: 'Behavioral risks, security concerns, and missing tests or validation gaps.',
    },
  ]}
/>

---

## 1) Review a PR diff (bugs + tests + risks)

```text
Act as a senior engineer doing a code review.

Input:
- PR goal: [GOAL]
- How tested: [COMMANDS]
- Diff (or changed files):
[PASTE DIFF]

Output:
- Findings ordered by severity
- Any missing tests
- Potential regressions
- Suggested follow-ups
```

## 2) Security-focused review

```text
Review this code for security issues.

Focus on:
- auth/authorization mistakes
- injection risks
- secrets handling
- data validation
- unsafe defaults

Code or diff:
[PASTE]
```

## 3) Performance review

```text
Review this change for performance risks.

Focus on:
- algorithmic complexity
- N+1 queries / repeated calls
- unnecessary re-renders (frontend)
- caching opportunities

Code or diff:
[PASTE]
```

## 4) Review for maintainability

```text
Review this module for maintainability.

Focus on:
- clarity and naming
- separation of concerns
- error handling and observability
- public API design

Code:
[PASTE]
```

## 5) Test gap review

```text
Given this feature change, list the test cases that should exist.

Feature:
[DESCRIBE]

Changed code/diff:
[PASTE]

Return:
- A prioritized list of tests to add
- Why each test matters
```

---

## FAQ

### What input produces the best reviews?

A diff or changed files, plus context about expected behavior and how it was tested.

### How do I get less generic feedback?

Ask for file/line references, severity ranking, and concrete follow-up steps.

### What should a review always include?

Behavioral risks, security concerns, and missing tests.

