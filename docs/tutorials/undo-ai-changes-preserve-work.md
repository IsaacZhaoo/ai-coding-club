---
title: "Undo an Unwanted AI Change Without Losing Your Own Edits"
sidebar_label: "Undo AI Changes, Keep Your Edits"
description: "Use Git patch restoration to remove an unwanted AI edit while preserving your staged changes and untracked notes in a small, reproducible exercise."
keywords: ["undo AI code changes", "git restore patch", "preserve staged changes", "selective rollback"]
sidebar_position: 50
tags: ["tutorial", "coding-assistant", "agent-engineering", "git"]
---

# Undo an Unwanted AI Change Without Losing Your Own Edits

You've discovered that an unwanted AI edit was merged with your own changes in the same file, leaving a mixed state you can't simply "undo" in one click. This scenario is common when external tools and human edits collide without clear boundaries or checkpoints.

In this tutorial, you will learn to inspect and selectively restore parts of a messy file. You'll run concrete commands that compare versions, isolate unwanted changes, and rebuild a clean state using only Git's built-in capabilities.

## The Problem: Mixed Changes, One File

Imagine this scenario:

- Your code was committed at tag `before-ai`.
- You changed the currency from `"USD"` to `"EUR"` (a deliberate edit). You staged this change but didn’t commit yet.
- The AI then overwrote your file and multiplied all amounts by 100. This new change is **unstaged**.

Now you see `My trip | EUR 2500` when running your script—completely wrong. But if you restore the file blindly, you also lose your EUR customization and possibly other personal tweaks.

You need to:

1. Keep your working directory safe
2. Inspect the exact differences
3. Apply only the undo for the unwanted change
4. Confirm your EUR edit and personal note remain intact

## Prerequisites
This exercise has been verified with Git 2.43 and Python 3 on Linux/WSL using Bash. Get <a href="https://raw.githubusercontent.com/IsaacZhaoo/ai-coding-club/efa81171466cc01774c91c3890ca169c50d92df9/examples/ai-rollback/setup-lab.py">setup-lab.py</a>, save it into a folder, and open the terminal in that same folder. That is the entire preparation.

## Step 1: Set Up the Lab Project

Run these commands to create a fresh, isolated repository for this exercise:

```bash
lab_dir=$(mktemp -d -t ai-rollback-XXXXXXXX)
python3 ./setup-lab.py "$lab_dir/project"
cd "$lab_dir/project"
```

Verify the initial state:

```bash
git status --short
python3 expense_report.py
```

Expected output:

```text
MM expense_report.py
?? notes.txt
My trip | EUR 2500
```

The `M` columns indicate staged (`cached`) and unstaged changes; the file’s current output is still wrong.

## Step 2: Save a Recovery Copy Before Doing Anything

Before making any changes, create a clean sibling copy of your repository to preserve the exact current state (including .git and untracked files) for comparison later. This is a bounded copy tailored to this exercise; do not assume it behaves as a full backup for arbitrary repositories.

```bash
test ! -e ../recovery-copy && cp -a . ../recovery-copy
```

Quickly verify that your key files are duplicated:

```bash
cmp expense_report.py ../recovery-copy/expense_report.py
cmp notes.txt ../recovery-copy/notes.txt
```

After running those comparisons, confirm that both show identical content and no differences. Continue only when the preceding copy and both comparisons succeed. The comparisons cover those two named files, not every file in the folder.

## Step 3: Inspect the Differences

Understand what Git sees in each storage layer:

### Working tree vs reference (both changes visible)

```bash
git diff before-ai -- expense_report.py
```

You’ll see two hunks:

1. The EUR currency change (your intentional edit)
2. The `* 100` multiplier (the unwanted AI edit)

These are separate, so we can treat them independently.

### Cached (staged) vs HEAD

```bash
git diff --cached -- expense_report.py
```

This shows only the EUR change relative to the commit at HEAD (`before-ai`). The unwanted multiplier is not in the index yet.

### Working tree vs index

```bash
git diff -- expense_report.py
```

This shows only the `* 100` multiplier, confirming it’s present in your working file but not staged.

## Step 4: Apply Only the Unwanted Undo Using `git restore --patch`

Use Git’s interactive patch restoration to select exactly which hunks to apply:

```bash
git restore --source=before-ai --patch --worktree -- expense_report.py
```

Git will present each hunk with a prompt like:

- Apply this hunk to worktree? [y/N]

**Read each change carefully before answering:**

- For the EUR currency hunk (if it appears), type `n` to keep your edit.
- For the calculation hunk that introduces `* 100`, type `y` to remove it.
- For any unrelated differences, decide based on what you expect.

Press `q` anytime to stop prompting without undoing choices already made. If Git ever shows a hunk that mixes changes you can’t confidently separate, pause and compare your saved versions instead of guessing.

> ⚠️ This method uses “hunks” as isolated patches. In practice, different repositories may order or combine hunks differently. Always review the displayed diff before answering.

## Step 5: Verify What Remains

After Git finishes prompting, confirm the results with these commands:

```bash
python3 expense_report.py
git diff --exit-code
git diff --cached -- expense_report.py
git status --short
cmp notes.txt ../recovery-copy/notes.txt
```

Expected behavior:

- `My trip | EUR 25` — only the correct total remains.
- `git diff --exit-code` exits with code 0 (no differences between index and working tree).
- `git diff --cached -- expense_report.py` still shows your staged USD→EUR change relative to HEAD.
- `git status --short` shows:
  ```text
  M  expense_report.py
  ?? notes.txt
  ```
  The `M` now reflects only the cached EUR edit; the unwanted multiplier is gone from the working tree.
- `cmp notes.txt ../recovery-copy/notes.txt` produces no output, confirming your personal note is unchanged.

You’ve successfully:

- Restored only the unwanted change
- Preserved your EUR customization and personal note
- Left Git’s index and history untouched (no new commits)

## When This Method Works Well

- You have a trustworthy reference state (like a recent commit or verified backup) to compare against.
- Your unwanted changes are clearly separable from the ones you want to keep.
- You control the local workspace and can safely run inspection and restoration commands.

A checkpoint does not label later changes by author, and Git cannot tell which uncommitted lines came from a human or an AI. This technique relies on your ability to inspect actual differences rather than guess origins.

## Limitations and Edge Cases

| Scenario | What Happens / What to Do |
|----------|---------------------------|
| Staged unwanted bytes remain in the index after a worktree-only restore | Inspect staged content separately before committing; this exercise does not fully resolve different starting states. |
| Overlapping edits or uncertain ownership | Use preserved copies and deliberate comparison or reconstruction; do not guess hunk answers. |
| Committed or shared changes | Inspect what the commit contains. A reviewed revert or follow-up change is a separate route; a mixed commit may hold wanted work. Cherry-picking an earlier commit does not undo a later change, so don't treat it as a recovery shortcut. |
| No trustworthy saved version exists | A missing tag alone doesn't guarantee no commits or editor/backup copies exist. Investigate those sources, but do not promise recovery of never-saved bytes. |
| Linked worktrees or submodules | They may point to metadata outside the copied folder. A small standalone-folder copy is not automatically a complete backup of those layouts. |

## Key Concepts at a Glance

- **Commit**: A snapshot in the Git history (the `before-ai` tag here).
- **Staging area / index**: The prepared changes ready for commit (`git diff --cached`).
- **Working tree**: Your actual files on disk; where `git restore --patch` edits.
- **Hunk**: A contiguous block of changed lines shown in diffs.
- **Checkpoint**: Any reference state (commit, tag, or external copy) you can compare against to isolate changes.

## Recommended Next Steps
Review the working-tree and staged diffs to ensure everything looks as expected, then keep the verified copy until you are satisfied. Remember that a commit records only staged content; creating a tag or branch merely names a commit and never saves uncommitted working-tree or index changes by itself. The saving step and naming a reference are different operations.

## Official References

- [git restore](https://git-scm.com/docs/git-restore): Source selection, worktree/index targets, interactive patch mode.
- [git diff](https://git-scm.com/docs/git-diff): Comparisons across working tree, index, and commits.
- [git revert](https://git-scm.com/docs/git-revert): Creating a new change that reverses an existing commit.

## Further Reading

- [Git basics](/docs/course/essential-skills/git-github/)
- [AI coding agent beginner guide](/docs/tutorials/ai-coding-agent-beginner-guide/)
- [Worktree isolation for parallel agents](/docs/tutorials/parallel-coding-agents-worktrees/)

---

Now you have a reliable, repeatable method to undo unwanted AI-assisted edits without losing your own work. The key is: always keep a reference checkpoint, inspect differences explicitly, and let Git’s hunk-level control guide your decisions rather than blindly trusting either the AI or any single diff output.