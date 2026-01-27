---
title: Refactoring Prompts
description: Prompt templates for safe refactors, migrations, and code cleanup
---

import FAQSchema from '@site/src/components/FAQSchema';

# Refactoring Prompt Templates

**Make changes safely, with minimal diffs and clear verification**

<FAQSchema
  items={[
    {
      question: 'What makes a refactoring prompt effective?',
      answer: 'A clear goal, constraints, and a verification plan (tests/typecheck) so the output is reviewable and safe.',
    },
    {
      question: 'How do I keep diffs small?',
      answer: 'Ask for one change at a time and request a minimal diff with file-by-file steps.',
    },
    {
      question: 'What should I always request?',
      answer: 'Ask for edge cases and concrete verification commands after the refactor.',
    },
  ]}
/>

---

## 1) Safe refactor with a verification loop

```text
You are editing a production repo.

Goal:
- Refactor [MODULE/FUNCTION] to improve [readability/performance/maintainability]

Constraints:
- Do NOT change behavior
- Do NOT add new dependencies
- Keep diffs small and reviewable

Context:
- File: [PATH]
- Related files: [PATHS]
- Current code:
[PASTE CODE]

Output:
1) Propose a short plan
2) Show the minimal diff (or describe exact edits)
3) List verification steps (tests/typecheck/lint)
```

## 2) Extract function/class with stable API

```text
Extract a helper from this code without changing behavior.

Constraints:
- Keep the public API the same
- Prefer pure functions where possible
- Add/adjust unit tests if needed

Code:
[PASTE CODE]

Return:
- New helper signature
- Updated call sites
- Tests to add or update
```

## 3) Rename symbol safely across the repo

```text
I need to rename:
- Old name: [OLD]
- New name: [NEW]

Constraints:
- Update imports/exports consistently
- Avoid breaking public API if possible (if not, propose a migration path)
- Update docs/comments where relevant

Repo context:
- Entry file: [PATH]
- Related modules: [PATHS]

Give:
- The exact files to change
- The order of changes
- Verification commands
```

## 4) API migration (old -> new)

```text
Migrate from [OLD API] to [NEW API] in this codebase.

Constraints:
- Keep behavior identical
- If needed, add a compatibility layer with a deprecation note
- Update tests to cover both typical and edge cases

Provide:
- Step-by-step migration plan
- Minimal diffs per step
- Rollback strategy
```

## 5) Reduce complexity (split module)

```text
This module is too large and hard to maintain.

Goal:
- Split it into smaller modules with clear responsibilities

Constraints:
- Preserve behavior
- Keep exports stable
- Avoid circular dependencies

Current file:
[PASTE CODE OR LINK PATH]

Return:
- Proposed file structure
- New module responsibilities
- A checklist to verify nothing broke
```

---

## FAQ

### What makes a refactoring prompt effective?

A clear goal, constraints, and a verification plan so the output is reviewable and safe.

### How do I keep diffs small?

Ask for one change at a time and request a minimal diff with file-by-file steps.

### What should I always request?

Ask for edge cases and concrete verification commands after the refactor.

