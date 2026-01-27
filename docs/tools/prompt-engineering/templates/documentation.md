---
title: Documentation Prompts
description: Prompt templates for writing and improving technical documentation
---

import FAQSchema from '@site/src/components/FAQSchema';

# Documentation Prompt Templates

**Get clear docs that match the code and reduce support load**

<FAQSchema
  items={[
    {
      question: 'How do I prevent inaccurate docs?',
      answer: 'Give the real code or interfaces and ask the AI to cite the exact symbols it is documenting.',
    },
    {
      question: 'What is the best doc structure?',
      answer: 'Start with a TL;DR, then usage examples, configuration, common pitfalls, and troubleshooting.',
    },
    {
      question: 'What should I always request in docs?',
      answer: 'At least one runnable example and a short troubleshooting section.',
    },
  ]}
/>

---

## 1) README section (install + usage)

```text
Write a README section for this module.

Include:
- TL;DR (1-2 sentences)
- Installation
- Basic usage with a runnable example
- Configuration options
- Common pitfalls

Module context:
[PASTE CODE OR API]
```

## 2) Docstring / JSDoc generation

```text
Add docstrings/JSDoc to the following code.

Rules:
- Explain inputs/outputs
- Mention important edge cases
- Provide one usage example

Code:
[PASTE CODE]
```

## 3) Troubleshooting guide

```text
Create a troubleshooting section for this feature.

Include:
- Top 5 failure modes
- Symptoms
- Likely causes
- Fix steps

Feature description:
[DESCRIBE FEATURE]
```

## 4) API docs (endpoints or functions)

```text
Write concise API docs for the following interface.

Include:
- Endpoint/function summary
- Parameters and types
- Example request/response or usage
- Error cases

API:
[PASTE API]
```

## 5) Change log / release notes

```text
Given this diff summary, write release notes.

Include:
- What changed
- Why
- How to upgrade
- Breaking changes (if any)

Diff summary:
[PASTE SUMMARY]
```

---

## FAQ

### How do I prevent inaccurate docs?

Give the real code or interfaces and ask the AI to cite the exact symbols it is documenting.

### What is the best doc structure?

Start with a TL;DR, then usage examples, configuration, pitfalls, and troubleshooting.

### What should I always request in docs?

At least one runnable example and a short troubleshooting section.

