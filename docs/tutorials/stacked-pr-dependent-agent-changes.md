---
title: "Layered Git Workflows: Stacked Changes, Rebasing, Squash-Merging, and Verification"
sidebar_label: "Stacked PRs for Dependent Agent Changes"
description: "Review dependent coding-agent changes with a local Git and Python lab: isolate layer diffs, catch semantic regressions after rebase, and repair squash-merge baselines."
keywords: ["stacked pull requests", "coding agent code review", "dependent changes", "git rebase", "squash merge"]
sidebar_position: 49
tags: ["tutorial", "coding-assistant", "agent-engineering", "git"]
---

# Layered Git Workflows: Stacked Changes, Rebasing, Squash-Merging, and Verification

If you’re comfortable with Git branches and basic Python, but occasionally feel “magic” when an upstream contract changes and your downstream tests suddenly fail, this tutorial is for you. We’ll walk through a realistic local workflow where two coding-agent changes sit in stacked branches, one depends on the other, and an upstream semantic change breaks a clean rebase. You’ll see exactly how to isolate the failure, repair only what’s necessary, and integrate everything using a squash merge that leaves your final review diff focused on the consumer code.

We keep this entirely local—no GitHub account required. The only dependencies are Git and Python 3. We treat the examples as instructional; adapt them to your team’s ownership model.

## Quick Outcomes

By the end of this walkthrough, you will be able to:

- Name the base/head of both pricing and checkout layers
- Reproduce the classic semantic regression (99.8 vs 80) after a clean rebase
- Repair only the consumer layer where the API contract changed
- Verify that only downstream files appear in the final review diff
- Confirm the combined test suite still passes on main

## Setup: The Small Two-Layer Project

We’ll build a tiny Python project with two layers:

1. `pricing` (A): exposes how discounts are calculated.
2. `checkout` (B): consumes pricing to compute a final checkout total.

All in a single local repository using one worktree. This simplifies tracking; in a real repo, you’d coordinate branch ownership and avoid mutating shared branches from unrelated worktrees.

### 1. Initialize the Repository

Run these commands in an empty directory:

```bash
mkdir ai-coding-club-lab && cd ai-coding-club-lab
git init -b main
git config user.name "Lab Author"
git config user.email "lab@example.com"
```

Add `.gitignore` immediately:

```bash
echo "__pycache__/" > .gitignore
git add .gitignore
git commit -m "chore: add .gitignore as initial main commit"
```

### 2. Create the Initial Pricing Layer (A)

Create `pricing.py` with fraction-based discounts:

```python
# pricing.py
def discounted_total(subtotal, discount):
    if not 0 <= discount <= 1:
        raise ValueError('discount out of range')
    return round(subtotal * (1 - discount), 2)
```

Create `test_pricing.py`:

```python
# test_pricing.py
import unittest
from pricing import discounted_total

class PricingTests(unittest.TestCase):
    def test_twenty_percent(self):
        self.assertEqual(discounted_total(100, 0.2), 80)
    def test_no_discount(self):
        self.assertEqual(discounted_total(100, 0), 100)
    def test_full_discount(self):
        self.assertEqual(discounted_total(100, 1), 0)
    def test_invalid_discount(self):
        for value in (-1, 1.1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                discounted_total(100, value)
```

Switch to the feature branch and commit A’s files:

```bash
git switch -c feature/pricing
git add pricing.py test_pricing.py
git commit -m "feat(pricing): initial fraction-based discount calculation"
```

Create a tag to mark this as the pricing-layer checkpoint (before any checkout changes exist):

```bash
git tag lab/parent-v1 feature/pricing
```

### 3. Create the Checkout Layer (B)

Create a new branch for checkout changes:

```bash
git switch -c feature/checkout
```

Add `checkout.py`:

```python
# checkout.py
from pricing import discounted_total

def checkout_total(subtotal):
    return discounted_total(subtotal, 0.2)
```

Add `test_checkout.py`:

```python
# test_checkout.py
import unittest
from checkout import checkout_total

class CheckoutTests(unittest.TestCase):
    def test_twenty_percent_checkout(self):
        self.assertEqual(checkout_total(100), 80)
    def test_zero_subtotal(self):
        self.assertEqual(checkout_total(0), 0)
```

Commit B’s files:

```bash
git add checkout.py test_checkout.py
git commit -m "feat(checkout): apply fixed 20% discount via pricing"
```

### 4. Verify the Starting State

Run tests:

```bash
python3 -m unittest discover -v
```

You should see 6 passing tests (4 from `pricing`, 2 from `checkout`).

Check the diff boundaries:

```bash
git diff --name-only feature/pricing...feature/checkout
# Lists: checkout.py, test_checkout.py

git diff --name-only main feature/checkout
# Lists: pricing.py, test_pricing.py, checkout.py, test_checkout.py
```

This confirms that `pricing` files are part of the ancestry required to run B’s tests.

## The Problem: Upstream Contract Change

Now imagine you run a coding agent on the pricing layer (A) to refactor how discounts are represented. It should still behave identically from an end-user’s perspective, but internally:

- Discounts switch from fractions (0.0–1.0) to percent units (0–100).
- The `discounted_total` function implementation changes accordingly.

Note: this pricing example is our lab, not an official Git example.

### 1. Record Pricing-Layer A Before Changes
Switch to your pricing feature branch:
```bash
git switch feature/pricing
```
This moves you onto the work-in-progress pricing changes. No tag is created yet—only the parent checkpoint `lab/parent-v1` exists. The new checkpoint for the updated A tip will be recorded after you commit your refactor.

### 2. Apply the Pricing Change

Modify the two files (`pricing.py` and `test_pricing.py`) as described in this lab example.

`pricing.py`:

```python
def discounted_total(subtotal, discount):
    # discount is now a percent (0–100)
    if not 0 <= discount <= 100:
        raise ValueError('discount out of range')
    return round(subtotal * (1 - discount / 100), 2)
```

`test_pricing.py`:

```python
import unittest
from pricing import discounted_total

class PricingTests(unittest.TestCase):
    def test_twenty_percent(self):
        self.assertEqual(discounted_total(100, 20), 80)
    def test_no_discount(self):
        self.assertEqual(discounted_total(100, 0), 100)
    def test_full_discount(self):
        self.assertEqual(discounted_total(100, 100), 0)
    def test_invalid_discount(self):
        for value in (-1, 101):
            with self.subTest(value=value), self.assertRaises(ValueError):
                discounted_total(100, value)
```

Commit this pricing change:

```bash
git add pricing.py test_pricing.py
git commit -m "refactor(pricing): switch discount to percent units"
```

Now record the updated pricing tip:
```bash
git tag lab/parent-v2 feature/pricing
```
This tag captures the new percent-based contract boundary that will later be excluded while replaying layer B.

At this point, A’s four tests still pass. But note that the API contract changed: callers must now pass 20 instead of 0.2.

### 3. What Happens If You Naively Rebase Checkout?

On `feature/checkout`, attempt a clean rebase onto the updated pricing branch:

```bash
git switch feature/checkout
git rebase --onto feature/pricing lab/parent-v1
```

Git replays only ONE consumer commit onto the new pricing head. There are no text conflicts here, and the patch content remains byte-for-byte identical until the final fix arrives.

Now run tests:

```bash
python3 -m unittest discover -v
```

You’ll see a failure in `test_twenty_percent_checkout`:

- Computed value: `99.8`
- Expected: `80`

Why? Because `checkout_total` still calls:

```python
discounted_total(subtotal, 0.2)
```

But the pricing layer now interprets `0.2` as “0.2%”, not “20%”. The contract changed semantically; B’s unchanged consumer code no longer matches the new API.

This is expected. It’s the core problem we’ll solve: preserve patch identity while accounting for upstream semantic changes.

### 4. Repair Only the Consumer Layer (B)

The smallest repair is to adjust B’s call to pass `20` instead of `0.2`:

```python
# checkout.py (edited)
from pricing import discounted_total

def checkout_total(subtotal):
    return discounted_total(subtotal, 20)
```

Commit:

```bash
git add checkout.py
git commit -m "fix(checkout): align discount call with percent-based pricing API"
```

Run tests again:

```bash
python3 -m unittest discover -v
```

All six tests pass. Note:

- The upstream tests changed with the contract.
- The consumer test still expects 80, because the math (`100 * (1 - 20/100) = 80`) is unchanged from the user’s perspective.
- You repaired only what was necessary; B’s original patch remains intact in ancestry.

## Rebasing onto a Squashed Main: Clean Integration

Now we simulate an upstream team that squashed A into `main` and then merges your checkout branch. We’ll do this locally in a clean repository to keep the graph visible.

### 1. Return to main and Squash Pricing

```bash
git switch main
git merge --squash feature/pricing
git commit -m "chore(pricing): incorporate percent-based discount logic"
```

This gives you a squash commit that contains A’s files without preserving the original A commit ancestry as merged history.

### 2. Verify Diff Boundaries After Squash

From `main`, check which files look “new”:

```bash
git diff --name-only main feature/checkout
# Lists: checkout.py, test_checkout.py

git diff --name-only main...feature/checkout
# Lists: pricing.py, test_pricing.py, checkout.py, test_checkout.py
```

This is a comparison-boundary issue: `main...feature/checkout` includes A’s ancestry via the merge base, so it lists four files. But `git diff --name-only main feature/checkout` (endpoint trees) shows only B’s two files—exactly what you want to see in a final review diff once integration is done.

### 3. Rebase Checkout Onto Squashed Main

Still on `feature/checkout`, rebase onto the squash commit:

```bash
git switch feature/checkout
# Optional but recommended for safety (creates backup ref without switching):
git branch feature/checkout-backup

git rebase --onto main lab/parent-v2
```

Git replays B’s two commits (original consumer + fix) onto `main`. There are no conflicts.

Run tests again:

```bash
python3 -m unittest discover -v
```

All six tests pass. Now the checkout layer is cleanly built on top of the squashed pricing logic.

If you accidentally hit a conflict, inspect it and abort to restore your branch:

```bash
git rebase --abort
```

### 4. Pre-Merge Review
With B safely checked out after the successful post-squash restack, review the exact files changed:
```bash
git diff --name-only main...feature/checkout
# Lists exactly: checkout.py, test_checkout.py
```
Confirm base and head commits using:
```bash
git rev-parse main feature/checkout
```
Six tests have just passed on this tip. Now return to main:
```bash
git switch main
git merge --ff-only feature/checkout
```
The resulting graph contains one A squash commit plus two replayed B commits. Main and the merged branch now point to the same commit—no new features or extra branches introduced.

## Final Verification Checklist

After the fast-forward merge, verify state with:
```bash
git rev-parse main feature/checkout
# Both refs resolve to the identical commit hash
```
Confirm there are no local differences between main and the merged branch:
```bash
git diff --name-only main feature/checkout
# Output is empty—tree equality confirmed
```
Run your test suite to ensure example behavior holds:
```bash
python3 -m unittest discover -v
# All six tests pass
```
Remember, the two-file layer review was performed before merge (see Pre-Merge Review), and its recorded base/head pair serves as concrete evidence of what was integrated. An empty diff after merge verifies the trees match; passing tests verify the specific example behavior remains correct.

## Key Takeaways

- A layer’s approval is tied to both its diff and the upstream contract on which it was checked. An unchanged patch and a conflict-free rebase do not preserve that evidence if the upstream API changes semantically.
- Rebasing cleanly replays your changes but doesn’t automatically adjust them for an evolved interface. You must retest after any upstream contract change.
- Use `git diff --name-only A B` vs `A...B` carefully: they describe different comparison boundaries and will show different file lists in PR tools or reviews.
- For stacked changes, merge from the lowest unmerged layer upward (as GitHub’s native stacked-PR docs recommend). In this local example, that’s pricing → checkout.
- When integrating after a squash merge, your final review diff should focus only on downstream files once ancestry is properly accounted for.

## Next Steps

You now have a reusable mental model for layered changes:

- Record stable parent boundaries (`lab/parent-v1`, `lab/parent-v2`) before rewriting or rebasing.
- Treat each layer’s tests as evidence of its contract; when upstream semantics change, update downstream calls minimally.
- Use local worktrees and controlled branch ownership to run these mutations safely in shared repositories.

To continue exploring parallel agent workflows, checkout the next tutorial: [Parallel coding agents with worktrees](https://aicoding.club/docs/tutorials/parallel-coding-agents-worktrees/). For review evidence patterns, see: [AI code review workflow](https://aicoding.club/docs/tutorials/ai-code-review-workflow/).

For deeper reference on the commands used here:
- Git diff: https://git-scm.com/docs/git-diff
- Git rebase: https://git-scm.com/docs/git-rebase
- Git merge: https://git-scm.com/docs/git-merge

To understand GitHub’s native stacked-PR mechanics (outside of this local lab), see: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests