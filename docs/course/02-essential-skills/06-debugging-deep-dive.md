---
sidebar_position: 6
sidebar_label: 'Debugging Deep Dive: From Error to Solution'
title: 'Debugging Deep Dive: From Error to Solution'
description: 'Debugging Deep Dive: From Error to Solution'
---

> TL;DR: Go deeper on debugging: hypotheses, instrumentation, and iteration.

## Key steps
1. Form hypotheses and rank by likelihood.
2. Add logs or breakpoints to gather evidence.
3. Fix and add a regression test.

## Practice
- Pick a recent bug and write a regression test that would have caught it.

This post expands on the basics of debugging, providing a systematic approach to finding and fixing errors in your code. We'll cover using AI as a debugging partner, reading documentation effectively, and using common debugging tools.

### A Systematic Approach to Debugging

When you encounter a bug, it's tempting to randomly change code until it works. A better way is to have a system.

1.  **Reproduce the Bug:** Consistently make the bug appear.
2.  **Understand the Error:** Read the error message carefully.
3.  **Form a Hypothesis:** Guess what might be causing the issue.
4.  **Test Your Hypothesis:** Use print statements, a debugger, or ask an AI to verify your guess.
5.  **Fix and Verify:** Apply the fix and ensure the bug is gone and no new bugs were introduced.

### Using AI as Your Debugging Partner

AI can be a powerful debugging assistant. Instead of just saying "it's broken," provide context.

**Good Prompt:**
> "I'm getting a `TypeError: cannot read properties of null` in my JavaScript code. Here is the function where it happens: `[code snippet]`. I think the `user` object is sometimes null. Can you help me add a check for this?"

### Reading Documentation

Sometimes the answer is in the official documentation. Learning to read it is a superpower.
- **MDN Web Docs:** For web development (JavaScript, HTML, CSS).
- **Stack Overflow:** Search for similar error messages.

### Debugging Tools

- **Browser Console:** Essential for frontend JavaScript. Use `console.log()` to inspect variables.
- **IDE Debuggers:** Tools like the one in VS Code let you pause code execution, inspect variables, and step through your code line-by-line.

### AI for Test Generation

You can ask an AI to write tests that might reveal a bug.

**Prompt:**
> "Write a set of tests for this JavaScript function to cover edge cases, especially what happens when `input` is an empty array or contains non-numeric values. `[code snippet]`"

### Your Turn: Debug These Issues (Hands-On Evidence & Checks)

Nathan Onn illustrates the same core issue in an account from https://www.nathanonn.com/claude-code-debugging-visibility-methods/: when a combined search-and-filter query runs, the component often selects the laptops filter first, then runs “search apple” and lets that search result overwrite the correct category display. Readers can apply this evidence-record exercise to their own comparable component and data.

#### 1. Reproduction Sequence (The Minimal Story)

Use your existing product-filter page for a simple reproduction:

- Select the laptops category and record all displayed product IDs.
- Change the filter to search “apple” (keeping the category selected) and record the new list.
- For a search-only comparison, clear the category first, enter “apple,” and record the resulting IDs; you cannot get a search-only result by toggling the category off and on in sequence because that re-enables the category and changes the behavior.

Compare the three ID lists against your dataset’s matching rules to locate mismatches.

Tip: If you’re using the browser DevTools Console, keep it open and ready to paste logs into an AI assistant later. A short annotated screenshot of the filtered list plus your console output is stronger evidence than a long block of raw logs.

#### 2. Evidence Record to Capture

Before asking your AI assistant for a fix, fill out this compact record. It’s designed to be pasted directly into a chat with an AI or into your own debug notes:

- Interaction:
  - Step 1: Selected category `laptops`.
  - Step 2: Typed search term `apple`.
- Inputs observed (from console/log):
  - Product list length before filtering: N
  - Category value used: “laptops”
  - Search query value used: “apple”
- Computation outputs observed:
  - Category-filtered result IDs: [list or first few items]
  - Search-only result IDs after interaction: [list or first few items]
  - Combined result (what you expected): [list or first few items]

##### Anomaly

When multiple conditions apply simultaneously, the final list must represent the intersection of all active constraints, not a union or a “merged set.” Equality to a search-only result alone cannot prove a bug because sometimes all search matches already belong in the selected category. The useful symptom is displayed IDs that violate a still-active category.

**Labeled example:**
- Category output: [A, B]
- Search output: [B, C]
- Expected intersection: [B]
- Actual display: [B, C]
- Item C violates the active category constraint.

Since these snapshots alone cannot tell you which computation read the wrong list or which effect overwrote the display last, log every step in execution order: record each computation’s name, the category or search query it was given, the exact collection IDs it consumed, the IDs it returned, and every write it performed to the displayed list. With that timeline plus your current code, you can definitively verify whether the search routine starts from the full list and silently replaces the filtered category result—the exact flaw observed in Nathan Onn’s account.

#### 3. Focused Debugging Request for an AI Assistant

When you paste your evidence record into an AI assistant, keep the request tight. A good prompt looks like this:

- “Given this product list with name/category fields, a search query string, and an active category (or empty string for none), compute the single derived list of products that satisfies both constraints as an intersection. Preserve existing behavior: clear the category to reset the constraint while keeping the query active, and clear the query to reset the text filter while keeping the category active. Optional memoization may be considered for performance; it is not a correctness requirement.”

Be specific about:
- What each effect currently reads (category, query, product list).
- When they run relative to UI interactions.
- The exact behavior you expect versus what you’re seeing.

Avoid vague language like “it breaks when I combine filters.” Replace it with “after selecting category and then typing a search term, the displayed list equals the search-only result.” Concrete statements lead to concrete suggestions.

#### 4. Proposed Fix Pattern (to Validate After Changes)

Implement a single combined calculation during rendering using inputs and active constraints; avoid side effects from searches or filters that mutate state outside this block. React links: https://react.dev/learn/you-might-not-need-an-effect and https://react.dev/reference/react/useMemo . useMemo is optional caching, not what makes the logic correct.

Inputs and all active constraints establish correctness. Products have string name/category; query is a string; activeCategory is an empty string when no category is selected. Empty query matches all names.

```jsx
const displayedProducts = useMemo(() => {
  const search = query.toLowerCase();
  return products.filter(product =>
    (!activeCategory || product.category === activeCategory) &&
    product.name.toLowerCase().includes(search)
  );
}, [products, query, activeCategory]);
```

This is a small integration fragment for the reader's existing component; actual query matching can include their real search fields. Clearing category with the empty-string convention preserves search, clearing query preserves category.

After implementing, compare actual IDs with expected ones and run these regression checks: one matched result alone does not establish that all scenarios are fixed.

#### 5. Regression Checks (Behavior-Based)

Don’t just test one happy path. Validate all combinations where constraints can be added or removed:

| Scenario | Action | Expected Outcome |
| --- | --- | --- |
| Category → Search | Select a category, then type a search term. | Display shows items in that category AND matching the query. |
| Search → Category | Type a search term, then select a category. | Display updates to show items in that category AND matching the query. |
| Clear Query (search → none) | Type a search term, then clear it. | All products in the selected category appear; query constraint removed. |
| Clear Category (category → none) | Select a category, then deselect/clear it. | Items matching the current query appear across all categories; category constraint removed. |
| No Matches | Combine filters (e.g., search "zoo" + category "laptops"). | Empty list is shown cleanly; no errors or stale items. |

To make this repeatable:
- Save a snapshot of one “good” combination (category + query).
- For each row above, verify that the displayed product IDs align with your expectations.
- If using Jest/Testing Library, assert at least two of these scenarios per build to catch regressions quickly.

#### 6. Quick Checklist Before You Ship

- [ ] Reproduction sequence documented and reproducible by another developer.
- [ ] Evidence record includes effect names, inputs, outputs, and the specific mismatch observed.
- [ ] The AI request includes specific evidence (IDs or outputs) and asks for one derived calculation that preserves all active conditions, without requiring useMemo or side effects.
- [ ] Fix implemented as a single filtering transformation derived from props/state during render.
- [ ] All five regression scenarios pass visually and via automated tests where applicable.

Follow this structure and you’ll turn a stubborn filter bug into a concrete change with measurable validation—exactly the kind of outcome that makes debugging feel like solving a puzzle instead of guessing.

#### Related Practice

- [Review AI-Generated Tests](/docs/tutorials/ai-generated-test-review/)
