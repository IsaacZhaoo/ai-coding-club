---
title: "Quick Guide: Checking cli/cli PR #14057 with gh"
description: "Inspect a real pull request with six passing checks and a request for changes. Connect the commit, CI results and a specific review comment with GitHub CLI."
tags: ["tutorial", "coding-assistant"]
---

# Quick Guide: Checking cli/cli PR #14057 with gh

`2026-11-19 · cli/cli#14057 · CLOSED · e0081cd`

I’ll show you how to inspect GitHub Actions and reviews for a specific public PR using the `gh` CLI in read-only mode. This uses the exact commit `e0081cd4f0e2c3c14237a2e7d9f6086a3a95bf91` from [PR #14057](https://github.com/cli/cli/pull/14057) in the `cli/cli` repository.

## 1. Pull up the PR metadata

```bash
gh pr view https://github.com/cli/cli/pull/14057 --json headRefOid,reviewDecision,reviews
```

This single command prints JSON containing:
- `headRefOid`: the exact SHA (e0081cd4f0e2c3c14237a2e7d9f6086a3a95bf91)
- `reviewDecision`: for this commit, `CHANGES_REQUESTED`
- `reviews`: array of individual reviewer notes

## 2. Read the build and check results

Builds and platform runs are exposed through GitHub’s standard checks interface:

```bash
gh pr checks https://github.com/cli/cli/pull/14057
```

You’ll see the three successful platform builds plus three integration tests. Note that some other checks are marked as skipped, and `reviewDecision` is tied to this exact commit. 

## 3. Look at the requested edits

Open files and conversation in your browser:
- Files changed: https://github.com/cli/cli/pull/14057/files
- Conversation: https://github.com/cli/cli/pull/14057#pullrequestreview-4985142387

Scroll to [discussion r3823478527](https://github.com/cli/cli/pull/14057#discussion_r3823478527) on docs/install_linux.md. You’ll find the reviewer’s note: “Why anchor to this channel number?”

## 4. (Optional) Watch new checks on your own PRs

If you maintain an active PR, you can poll its checks:

```bash
gh pr checks --watch
```

This runs while connected and updates as soon as new results appear. It does not track `reviewDecision` or comments; for those you must run `gh pr view` again or refresh the page. Event Streams (gh 2.105.0+) are optional and require preview access: see https://cli.github.com/manual/gh_event_listen.

## 5. Track state over time

Each push can change:
- Which checks pass or fail
- Who added new reviews
- Whether `reviewDecision` is updated

No merge actions are needed. The public PR state may evolve, so always re-run these read-only checks when you need current data.
