# Branching Strategy

## Overview

This repository uses `main` as its only long-lived branch. `main` contains the
current production-ready content referenced by the AI Coding Club website.

Use a short-lived topic branch when a change needs isolated development or
review. Merge it into `main` after verification, then remove the topic branch.
Do not maintain `dev` or `develop` as parallel long-lived branches.

## Branch Structure

```text
main (production-ready content)
  ↑ verified integration
topic/*, fix/*, codex/*, or wip/* (short-lived when needed)
```

### `main`

- Holds the current content source.
- Is the only long-lived branch.
- Must remain synchronized with `origin/main` before new integration work.
- May receive a focused direct commit when isolation adds no value.

### Topic branches

- Start from the latest `main`.
- Contain one focused content or workflow change.
- Must be verified before integration.
- Are deleted after `main` contains all their commits.

## Normal Workflow

For an isolated change:

```bash
git switch main
git pull --ff-only origin main
git switch -c topic/short-description

# Edit and verify the content.
git add <paths>
git commit -m "Update: Short description"

git switch main
git pull --ff-only origin main
git merge --no-ff topic/short-description
git push origin main

git branch -d topic/short-description
git push origin --delete topic/short-description
```

For a small focused change made directly on `main`, confirm the worktree is
clean and `main` is synchronized with `origin/main` before editing. Run the
same content checks before committing and pushing.

## Verification

Before integrating or pushing content:

- review the changed English and Chinese source files;
- confirm frontmatter, routes, links, and static references;
- run the relevant checks from the parent website repository;
- verify that no draft-only or internal editorial material is entering a
  public page;
- confirm the final topic-branch tip is an ancestor of `main` before cleanup.

Never force-push `main`, hard-reset shared history, or delete a branch that has
commits not contained in `main`.

## Integration With the Website Repository

This repository is the `content/` submodule of the main `aiCodingClub`
repository. Updating this repository does not update the website repository's
submodule pointer automatically.

The release order is:

1. commit and push the content change to this repository's `main`;
2. verify the pushed content commit on `origin/main`;
3. update the `content/` submodule pointer in the parent website repository;
4. run the parent repository's required checks;
5. commit and push the parent repository change.

Cloudflare Pages deploys the website from the parent repository's `main`
branch. A content commit is not part of the deployed website until the parent
repository points to it.

## Branch Cleanup

Before deleting a local topic branch:

```bash
git merge-base --is-ancestor topic/short-description main
git branch -d topic/short-description
```

Before deleting its remote branch, fetch the latest refs and confirm both the
local and remote topic tips are ancestors of `origin/main`. Use normal deletion,
never a force delete, unless the user has explicitly authorized recovery from a
known exceptional state.
