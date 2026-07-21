---
title: "Kimi Code CLI Guide: Install, Migrate from Kimi CLI, and Run Your First Safe Task"
description: "Install Kimi Code CLI, migrate safely from the legacy Kimi CLI, verify configuration, understand permission modes, and run a careful first task."
keywords:
  - Kimi Code CLI
  - Kimi CLI migration
  - Kimi Code install
  - Kimi Code tutorial
  - Kimi CLI replacement
sidebar_position: 10
tags: [tutorial, coding-assistant, kimi, agent-engineering]
---

# Kimi Code CLI Guide: Install, Migrate from Kimi CLI, and Run Your First Safe Task

---

If you found this because you searched for "Kimi CLI" and something felt off — the repository exists, the README is still there, but a bold notice at the top tells you the project is being phased out — you are in the right place. The product you want is **Kimi Code CLI**. The binary is different, the runtime is different, and the local data directory has moved. This guide covers how to install the new tool, migrate your existing state deliberately, verify the environment, and run a first task that does not immediately hand over the keys to the workshop.

---

## Why "Kimi CLI" Still Shows Up Everywhere

Search results are slow. GitHub Trending is not a changelog. Kimi CLI appeared on trending lists for long enough that it accumulated links, bookmarks, and word-of-mouth recommendations — and then its own maintainers announced that Kimi Code CLI is the successor. Both names coexist in search results today, and neither one obviously points at the other unless you already know which is current.

The useful thing to understand is that this is not a new model release dressed in a different name. It is a replacement product with a different codebase, a different runtime, different local state conventions, and an explicit migration path. If you are looking for the model and API rather than the terminal product, use the separate [Kimi K2 guide](/docs/tutorials/kimi-k2-guide/). The CLI project moved from Python (managed with `uv`) to TypeScript and Node.js. That is a meaningful difference in how you install it, how updates arrive, and how it behaves on a fresh machine. If your muscle memory reaches for a Python virtual environment, stop and read on.

---

## What Changed and What You Are Installing

| Dimension | Kimi CLI (legacy) | Kimi Code CLI (current) |
|---|---|---|
| Language / runtime | Python / uv | TypeScript / Node.js |
| Install method | Python package | Binary installer or npm |
| Default data directory | `~/.kimi/` | `~/.kimi-code/` |
| Command name | `kimi` | `kimi` |
| Migration path | — | `kimi migrate` |

The command name stays `kimi`, which is part of why the transition is confusing on a machine that had the old version. When you type `kimi --version` after installing Kimi Code CLI, you get the new tool's version — but if the old binary is still on your PATH, you might be talking to the wrong thing. We will check that explicitly.

---

## Installing Kimi Code CLI

### Recommended method: official installer script

For macOS and Linux, the official install script does not require Node.js to be preinstalled on your system:

```bash
curl -fsSL https://code.kimi.com/kimi-code/install.sh | bash
```

For Windows (PowerShell):

```powershell
irm https://code.kimi.com/kimi-code/install.ps1 | iex
```

These scripts download a self-contained binary. After they finish, open a new terminal session so your PATH is refreshed.

### Alternative: npm

If you prefer npm, you do need Node.js 22.19.0 or later installed before you begin:

```bash
npm install -g @moonshot-ai/kimi-code
```

This is the stricter option — the Node.js version requirement is exact and current tools like `nvm` or `fnm` make it manageable, but it is an extra step the binary installer avoids.

### Verify the binary

```bash
kimi --version
```

On 2026-07-21, version `0.28.1` returned successfully in an isolated environment with no login session. If you see an unexpected old version number, check `which kimi` and confirm you are not running the legacy Python binary.

```bash
which kimi
```

If that path points somewhere inside a Python virtual environment or a pip bin directory, the old tool is still winning. Remove it or adjust your PATH before continuing.

---

## Understanding Local State Before You Migrate

This is the part that deserves a pause. Moving workshops means understanding where things live before you pick up a box.

The old Kimi CLI stored configuration, input history, and any session data under `~/.kimi/`. Kimi Code CLI defaults to `~/.kimi-code/`. These directories are separate. Installing the new tool does not touch the old directory. Running `kimi migrate` copies specific data across — but not everything, and knowing what stays behind matters before you run it.

### The migration table

| Data | Behavior |
|---|---|
| CLI configuration | Copied |
| MCP server config | Copied |
| Input history | Copied |
| Selected sessions | Copied |
| **OAuth credentials** | **Not migrated** |
| **MCP service authorizations** | **Not migrated** |
| **Legacy plugins** | **Not migrated** |
| Old `~/.kimi/` directory | **Left intact** |

The workshop metaphor holds here: your notes and tool layouts can move, but the keys — credentials and trust relationships with external services — do not. You will need to authenticate fresh in the new environment regardless of what was in the old one. OAuth credentials are session-trust artifacts, not configuration files, and Kimi Code CLI treats them accordingly.

Migration can also be re-run. If you run `kimi migrate` and later realize you want to import a session you skipped, you can run it again. The old directory is never deleted.

---

## Running Migration

Before you run migrate, it is worth knowing where Kimi Code CLI will store its data. The default is `~/.kimi-code/`. If you want to change that, set the environment variable before anything else:

```bash
export KIMI_CODE_HOME=/path/to/your/preferred/location
```

Then run migration:

```bash
kimi migrate
```

The command will walk you through what it found in the old directory and what it proposes to copy. You can select which sessions to bring across. Review what it offers before confirming. This is not a one-way destructive action — your old directory survives — but being deliberate here is still worthwhile. If a session has sensitive context you do not want to move, do not move it.

---

## Running Doctor

After installation (and after migration, if you ran it), run the health check:

```bash
kimi doctor
```

This validates your `config.toml` and `tui.toml` configuration files. If default config files are missing, built-in defaults apply and the check is skipped for those files rather than failing. On 2026-07-21, `doctor` passed cleanly in an isolated environment using `KIMI_CODE_HOME` to separate state.

---

## First Login

First-run authentication has two supported paths:

1. **Kimi Code OAuth** — browser-based, links to your Moonshot account.
2. **Kimi Platform API key** — for headless environments or if you prefer key-based access.

```bash
kimi
```

Running the tool without arguments initiates the interactive session, which will prompt for login on first use. Follow the browser flow for OAuth, or supply your API key when prompted if you are using the key-based path. Other providers can be configured separately, but that is outside the scope of a first-run task.

---

## Understanding the Permission Ladder Before Your First Task

This is the other thing that deserves clear framing before you start. Kimi Code CLI has an explicit approval model, and the default is conservative — which is the right default for a new installation. For the wider boundary between an agent sandbox, workspace writes, and host trust, see the [coding agent sandbox security guide](/docs/tutorials/coding-agent-sandbox-security/).

| Mode | Behavior |
|---|---|
| **Default (normal)** | Read-only operations run automatically; modifying files and running shell commands require approval |
| **Plan mode** (`--plan`) | Agent plans and shows proposed changes before executing; you review the plan |
| **YOLO mode** | Skips regular approvals; the agent acts without pausing |
| **Auto mode** | Handles every approval automatically; fully autonomous execution |

For a first task on a new installation, default mode is what you want. You will see approval prompts when the agent proposes a file modification or a shell command, and you can read exactly what it intends to do before it happens.

Plan mode (`kimi --plan`, or `/plan` in an interactive session) is a useful middle ground: it costs you the time of reading the plan but gives you a structured view of what changes are coming before any of them execute. If you are working in a codebase you care about, this is a reasonable first-run habit.

YOLO and Auto both have their places, but not as first-run defaults on a freshly migrated environment. You do not yet know how this agent interprets your codebase, and skipping approvals before you do is trusting a stranger with your tools.

---

## Your First Safe Task

Here is one practical path through the first session. It does not require you to accept any autonomous changes.

### 1. Open a trusted, version-controlled repository

Do not start in a directory you cannot recover. Use a repository with uncommitted state you are willing to lose, or simply a scratch directory. `git status` before you begin. If the repository has untracked or modified files you care about, commit them first. The [AI coding agent beginner route](/docs/tutorials/ai-coding-agent-beginner-guide/) explains the same checkpoint-review-verify habit across terminal agents.

```bash
cd ~/projects/some-trusted-repo
git status
```

### 2. Start a session in read-only exploration mode

```bash
kimi
```

When prompted, type your instruction:

```text
Explain the structure of this directory. What are the main modules and how do they relate to each other? Do not create or modify any files.
```

Asking for a read-only directory explanation is a good first task because it exercises the agent's ability to understand your codebase without touching anything. The default approval mode means that even if it tried to modify something, it would stop and ask first.

Watch what it does. Notice which files it opens. Notice whether its summary is accurate. This tells you something about how the model reads your codebase before you let it write to it.

### 3. Ask a follow-up in the same session

You are already in the interactive prompt. Ask a follow-up question about what the agent just explained. Does it maintain context? Does it reference the right file? This is baseline model-behavior verification, not benchmarking — you are checking whether the tool is reading what you think it is reading.

### 4. Propose your first edit using Plan mode

When you are ready to make a change, switch to plan mode:

```bash
kimi --plan
```

When prompted, type your instruction:

```text
Rename the internal helper function `process_data` to `transform_input` and update all call sites.
```

Plan mode will describe the proposed changes — which files, which lines, what the diffs look like — without executing them. Review the plan. If it looks correct, confirm. If it missed a call site or reached into a file it should not touch, reject and refine the prompt.

This is the point at which you start building real trust in the agent's judgment for your codebase. Do not skip it by going straight to default-mode edits, and certainly do not jump to YOLO.

---

## What the No-Login Test Actually Confirmed

To be precise about what was directly tested: on 2026-07-21, `kimi --version` returned `0.28.1` and `kimi doctor` passed cleanly in an isolated environment using `pnpm dlx @moonshot-ai/kimi-code@0.28.1` with a dedicated `KIMI_CODE_HOME`. That confirmed package startup, version output, and config validation. The official binary installer endpoints were not separately verified in this test.

No live model response was verified. No coding task was completed in a logged-in session for this article. The downstream model behavior is well-documented but was not personally tested in this authoring context.

---

## The Compact Pre-Autonomy Checklist

Before you give Kimi Code CLI any approval to make autonomous changes — and before you consider YOLO or Auto mode — run through this:

- [ ] `kimi --version` returns the expected version (not the legacy Python binary)
- [ ] `which kimi` points to the correct installation path
- [ ] `kimi doctor` completes its configuration validation without unresolved config errors
- [ ] You have reviewed what `kimi migrate` will and will not move
- [ ] You have set `KIMI_CODE_HOME` if you want non-default state storage
- [ ] You have run at least one read-only task and reviewed what the agent examined
- [ ] You have reviewed one plan-mode proposal before accepting a file modification
- [ ] You understand that OAuth credentials and MCP authorizations must be reconfigured, not migrated
- [ ] You have committed or stashed anything in your working directory you are not willing to lose

Only after this checklist is comfortable should you consider widening the approval boundary. YOLO and Auto are not inherently dangerous, but they require that you already trust the agent's judgment in your specific environment. That trust is earned through the steps above, not granted at installation.

---

## A Word on the Naming Problem

This section exists because the naming situation is genuinely frustrating for developers trying to make good decisions. "Kimi CLI" and "Kimi Code CLI" are different tools that share a command name (`kimi`), coexist in search results, and use adjacent-sounding branding. The legacy project is still on GitHub. Its README now says it is being phased out, but that notice is easy to miss if you are following a link from a cached search result or an older blog post.

The honest recommendation is: if you are starting fresh, go directly to the Kimi Code CLI documentation. If you have an existing installation, run `which kimi` before you run anything else and confirm you know which tool you have. The migration path is clean and non-destructive, but it only helps if you realize you need it.

---

## Official References

- **Kimi Code CLI documentation**: [https://moonshotai.github.io/kimi-code/en/](https://moonshotai.github.io/kimi-code/en/)
- **Kimi Code CLI GitHub repository**: [https://github.com/MoonshotAI/kimi-code](https://github.com/MoonshotAI/kimi-code)
- **Official migration guide**: [https://moonshotai.github.io/kimi-code/en/guides/migration](https://moonshotai.github.io/kimi-code/en/guides/migration)
- **Command reference**: `kimi --help` and the official command reference cover `--continue`, `--prompt`, `--plan`, and permission-mode flags

---

*This guide was written on 2026-07-21. The version confirmed during testing was 0.28.1. Commands, paths, and migration behavior may change; verify against the official documentation for your current version before following install or migration steps.*
