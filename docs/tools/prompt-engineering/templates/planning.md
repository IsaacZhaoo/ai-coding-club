---
title: Planning Prompts
description: Prompt templates for planning, risk checks, and step-by-step execution
---

import FAQSchema from '@site/src/components/FAQSchema';

# Planning Prompt Templates

**Turn a vague task into a safe, executable plan**

<FAQSchema
  items={[
    {
      question: 'What makes a plan executable?',
      answer: 'Clear scope, file list, steps, and a verification plan for each step.',
    },
    {
      question: 'How do I reduce risk?',
      answer: 'Ask for incremental steps, rollback options, and a minimal-change approach.',
    },
    {
      question: 'What should I do when context is missing?',
      answer: 'Ask clarifying questions and request the exact files needed before changing anything.',
    },
  ]}
/>

---

## 1) Implementation plan (with files and DoD)

```text
Create an implementation plan for this task:
[TASK]

Constraints:
- Keep diffs small
- List exact files to change
- Define \"Definition of Done\" with verification commands

Output format:
1) Assumptions/questions
2) Step-by-step plan
3) Files to change
4) Risks + mitigations
5) Verification checklist
```

## 2) Debug investigation plan

```text
I have a bug. Create an investigation plan.

Bug:
- Symptom: [SYMPTOM]
- Error/logs: [LOGS]
- Recent changes: [CHANGES]

Output:
- Hypotheses ranked by likelihood
- What evidence to gather
- Commands to run
- How to confirm the fix
```

## 3) Migration plan (backwards compatible)

```text
Plan a migration from [OLD] to [NEW].

Constraints:
- Backwards compatible rollout
- No downtime if possible
- Include rollback steps

Return:
- Phased migration steps
- Data/schema considerations
- Monitoring/alerts to watch
```

## 4) Risk review before merging

```text
Before we merge, do a risk review.

Context:
- Goal: [GOAL]
- Changed files: [FILES]
- Diff: [PASTE DIFF]

Output:
- Top risks
- Worst-case failure modes
- Mitigations
- Extra tests or checks to run
```

## 5) Release checklist

```text
Create a release checklist for this change.

Include:
- Pre-release checks
- Deploy steps
- Post-deploy validation
- Rollback plan

Change summary:
[SUMMARY]
```

---

## FAQ

### What makes a plan executable?

Clear scope, file list, step-by-step tasks, and verification for each step.

### How do I reduce risk?

Use incremental steps, keep diffs small, and include rollback options.

### What should I do when context is missing?

Ask clarifying questions and request the exact files before changing anything.

