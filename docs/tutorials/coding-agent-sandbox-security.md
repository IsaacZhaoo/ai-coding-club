---
title: "Coding Agent Sandbox Security: What the Boundary Protects—and What Can Still Escape"
description: "Understand coding agent sandbox boundaries, workspace-write risks, host trust, command allowlists, privileged daemons, and practical isolation checks."
keywords:
  - coding agent sandbox security
  - AI coding agent security
  - sandbox escape
  - Codex CLI security
  - workspace trust
sidebar_position: 11
tags: [tutorial, coding-assistant, agent-engineering, security]
---

# Coding Agent Sandbox Security: What the Boundary Protects—and What Can Still Escape

---

The pitch sounds clean: the agent runs in a sandbox. Your files are safe, your credentials are safe, your production systems are safe. The sandbox is the answer.

It is part of the answer. The part that matters, but that vendors understandably emphasize less, is what happens after the sandbox produces output.

On July 20, 2026, Pillar Research published a multi-product overview of sandbox escapes and boundary bypasses across Cursor, Codex, Gemini CLI, and Antigravity. BleepingComputer independently covered the story the same day. The research did not focus on brute-forcing kernel privilege or escaping container namespaces. What it described, repeatedly, was a simpler and more durable problem: the agent wrote or shaped something inside its allowed workspace, and a trusted component outside the sandbox later executed, loaded, scanned, or acted on it. The sandbox held. The boundary did not.

That distinction is the article. Not a CVE list, not a vendor ranking, not an assertion that every sandbox is broken—but a precise account of where the enforced boundary ends and where the implicit trust chain begins, and what you can do about it.

---

## The Boundary Is Real, and It Is Incomplete

When developers say "the agent runs in a sandbox," they usually mean one of several things: the agent process is constrained in what system calls it can make, it runs as a low-privilege user, it operates inside a container, or some approval mechanism intercepts dangerous-looking commands. All of those controls are legitimate. None of them are the whole story.

The Pillar Research taxonomy organizes the relevant surface into three layers, and that model is the most useful frame I've found for thinking about this problem:

**Layer 1 — Direct execution.** Commands and system calls the agent process can invoke on its own authority. This is the layer most people imagine when they think "sandbox." Allowlists, denylists, privilege restrictions, and approval gates live here.

**Layer 2 — Workspace writes.** Files, configuration, interpreter definitions, Git hooks, build scripts, lockfiles, and metadata the agent can create or modify inside its workspace. This layer may be broad because writing files is the primary job of a coding agent, and heavily restricting writes can break the core use case.

**Layer 3 — Host trust.** Unsandboxed tools, editor extensions, language environments, local daemons, and external helpers that later consume, execute, or act on what the agent wrote. This layer typically has no awareness that it is handling agent-produced content.

The vulnerability is not usually in Layer 1. It is in the handoff from Layer 2 to Layer 3: the agent produces something, and a trusted host component treats it as authoritative.

Think of the sandbox as a fenced workshop. The fence is real. But files leave the workbench constantly, and outside the fence there is machinery that runs whatever drawings it receives without checking where the drawings came from.

---

## Four Recurring Failure Modes

The Pillar Research overview identified four patterns that recur across the named products. They are not exotic. They follow directly from the three-layer model, and each one involves a control that is real but bounded in a way that leaves the host trust layer exposed.

| Failure mode | Where it lives | What it means in practice |
|---|---|---|
| Denylist gaps | Layer 1 → Layer 2 | A restricted capability is reached via an OS mechanism or alias not on the list |
| Executable workspace configuration | Layer 2 → Layer 3 | A project config the agent modifies is later treated as automation by the editor or runtime |
| Command-name allowlists | Layer 1 | A command is classified safe by name; arguments or side effects are not evaluated |
| Privileged local daemons | Layer 3 | A socket the agent can reach—such as the Docker socket—becomes a second execution environment |

### Denylist gaps

A denylist says: this command, this syscall, this resource is forbidden. The problem with denylists in complex environments is that the operating system offers many ways to accomplish similar things, and maintaining a complete list across platforms, shell variants, and language runtimes is operationally difficult. A capability that is blocked via one path may be reachable through a different mechanism that the list does not enumerate.

This is not a theoretical concern. Allowlists reduce dependence on enumerating every forbidden capability, but they still need invocation-, argument-, and side-effect-aware design to be effective—as the command-name allowlist pattern below illustrates. When an agent's execution policy is a denylist, the coverage of that list determines the actual boundary—and that coverage is harder to reason about than it appears.

### Executable workspace configuration

Many development tools treat certain files in the workspace as automation: Git hooks, editor configuration with build tasks, formatters with pre-commit integration, language environment files that affect interpreter behavior, or test runner configuration that specifies commands to execute. These are not unusual files. They are normal parts of a project.

If an agent can write or modify those files, and a host tool later interprets them as executable configuration, the agent has influenced execution outside Layer 1 without triggering any direct-execution control. The CVE-2026-48124 workspace-hook issue in Cursor reported fixed in 3.0.0 is a concrete instance of this pattern. The exact mechanism is not reproduced here, but the category is legible: workspace writes shaped something that the editor or surrounding toolchain later treated as trusted instructions.

This is where the fenced-workshop metaphor is most accurate. The fence did not move. The drawings left through the gate and went straight to the press.

### Command-name allowlists

Some agent policies evaluate commands by name rather than by full invocation. A policy that permits `git` does not automatically have a well-defined answer to `git show <attacker-controlled-ref>` or to the side effects of `git` subcommands that perform network operations or write to global configuration. A policy that permits `npm` may not anticipate the execution surface of `npm install` in a directory with a controlled `package.json`.

The Codex CLI `git show` allowlist issue, reported patched in 0.95.0 (CVE pending as of the checked sources), illustrates this pattern. When command policy is expressed at the name level rather than the invocation level, the gap between the permitted name and the actual behavior of a specific invocation is the attack surface.

This is not an argument against allowlists. It is an argument that allowlists belong at the level of full invocations, argument shapes, and anticipated side effects, not just command names.

### Privileged local daemons

If an agent process can reach the Docker socket, it can potentially start containers with elevated privileges, mount host paths, or otherwise use Docker as a second execution environment that is not subject to the same controls as the agent process itself. The agent does not need to escape the sandbox directly; it needs to make a request to a daemon that has the capabilities the sandbox restricts.

A Docker-socket issue affecting Codex, Cursor, and Gemini CLI was reported fixed. The pattern generalizes: any local daemon that the agent process can reach, and that has broader authority than the agent process itself, is a potential bypass of Layer 1 restrictions via a Layer 3 handoff.

---

## The Antigravity Case

The two Antigravity reports were described by Pillar Research as valid but downgraded by Google based on exploitability. I will not editorialize beyond that characterization, because I do not have the technical detail needed to evaluate the downgrade decision independently. What I will note is that "valid but low exploitability" is not the same as "not worth understanding." The boundary model applies regardless of how a specific vendor assesses severity, and the question of what an agent can write and what the host later trusts is worth auditing for any product.

---

## What "Patched" Means Here

The checked sources—Pillar Research and BleepingComputer—report that most named issues were patched or vendor-acknowledged. Patch statements throughout this article are attributed to those sources unless an official advisory is directly available in the Writer Packet, which it is not for most items. Public GitHub advisory endpoints did not provide structured advisory data during this research pass.

This is not an assertion that current versions remain exploitable. It is a statement that the article cannot confirm patch completeness from primary sources, and that you should verify current status through official vendor security channels before drawing conclusions about your specific deployment.

The more important point is that patches address the specific finding. The three-layer model and the four failure modes are structural patterns that will recur in different forms as agent capabilities expand. Patching a specific hook-execution issue does not eliminate the category of executable workspace configuration. The defensive audit below is written against the pattern, not the specific CVE.

---

## Why "It Runs in a Sandbox" Is Not a Complete Answer

I want to be careful here. I am not saying that sandboxes are ineffective, that all four products are currently vulnerable, or that vendors are acting in bad faith. The controls that sandboxes provide are real, and most agent deployments are more dangerous without them than with them.

The problem is a category error in how the question is framed. "Is the agent sandboxed?" asks about Layer 1. The more complete question is: "What can the agent write, which host components trust those writes, and what is the second-order execution surface of that trust?" That question spans all three layers, and the answer is not visible from the sandbox boundary alone.

A developer who grants an agent access to their local workspace, with their editor open, their Git hooks active, their Docker socket accessible, and their production credentials in the same session—that developer has a sandbox protecting one layer of a much larger trust surface. The sandbox is doing its job. The job description was too narrow.

This matters more as agents become more capable and as usage patterns shift toward longer autonomous runs with broader repository access. The risk surface at low autonomy and high approval granularity is manageable. The risk surface at high autonomy and low approval granularity in an untrusted repository is qualitatively different.

---

## The Defensive Audit

The following questions are not theoretical. They are the questions I work through when deploying a coding agent near anything I care about. They are structured around the three-layer model and they do not require security expertise to apply—they require honesty about your actual setup.

### Layer 1: What can the agent execute directly?

- What is the execution policy: allowlist or denylist?
- If it is a denylist, have you enumerated the OS-level and shell-level alternatives to each blocked capability?
- If it is an allowlist, is the allowlist expressed at the level of full invocations and argument shapes, or just command names?
- Which commands are permitted without approval, and do any of those commands have side effects that span outside the workspace?

### Layer 2: What can it write?

- Can the agent write to `.git/hooks/`, editor configuration directories, build tool config files, or language environment files in the workspace?
- Can it modify `package.json`, `pyproject.toml`, `.pre-commit-config.yaml`, `.vscode/tasks.json`, `.cursor/rules`, or equivalent automation-bearing files?
- If yes to any of the above: which host tools will later read those files, and what do those tools do with them?
- Are agent-created configuration changes surfaced in review before they take effect?

### Layer 3: Which host components trust those writes?

- Which editor extensions are active in sessions where the agent operates?
- Do any extensions auto-execute tasks based on workspace configuration?
- Which Git hooks are active in the repository?
- Which formatters, linters, or test runners run automatically on file events or commit events?
- Is there a language environment manager that reads configuration from the workspace?

### Sockets and daemons

- Is the Docker socket accessible from the agent's process?
- Are there other local daemons (language servers, build services, credential helpers) that the agent process can reach?
- What do those daemons have permission to do?

### Approval and review

- Which actions skip the approval flow?
- Is the approval flow based on command name or on full invocation and side effects?
- Can the agent batch multiple writes in a single approved action in a way that obscures individual file changes?
- Are configuration file changes reviewed with the same attention as code changes? The [AI code review workflow](/docs/tutorials/ai-code-review-workflow/) provides a practical evidence-based review sequence.

### Environment and isolation

- Are production credentials, deployment keys, or staging access present in the same user session where the agent operates?
- Are cloud provider credential files, SSH agent sockets, or browser cookie stores accessible from the workspace?
- Is the work being done in a disposable environment (ephemeral VM, remote development environment, clean container) or in a persistent local session?
- Could the task be scoped to a narrower directory rather than the full repository root?

---

## The Environment-Choice Rule

If you are still establishing the baseline approval workflow for a terminal agent, review the [Codex beginner guide](/docs/tutorials/codex-guide/) and [Claude Code beginner guide](/docs/tutorials/claude-code-guide/) before widening permissions.

The right environment for a coding agent depends on two variables: how much you trust the repository input the agent is working with, and how much autonomy the agent is exercising.

**Trusted work at controlled autonomy.** If you are running an agent against your own repository, with familiar input, in an interactive session with fine-grained approval, your local environment is a reasonable choice. Harden it by narrowing the workspace scope, auditing which host tools are active, and keeping production credentials out of the session. The standard sandboxing controls of your chosen product provide meaningful protection at this level.

**Untrusted input or high autonomy.** If the agent is processing repository content from an external source, cloning unfamiliar repositories, running extended autonomous tasks, or operating with broad permission to write and execute—use disposable isolation. An ephemeral cloud VM, a remote development environment, or a container configured without sensitive host mounts, privileged mode, host credentials, or Docker socket access—with no persistent credential storage and no production access. This is not paranoia. It is the appropriate engineering response to the trust model: the effective blast radius of a write in an agent workspace is determined by what the host trusts, and the safest way to bound that radius is to make the host disposable.

The two modes are not in competition. Most day-to-day agent work fits the first mode. The second mode is the right choice for the cases where it matters, which is precisely the case where many developers currently underprotect.

---

## A Note on How This Research Was Conducted

I did not reproduce the disclosed vulnerabilities for this article and I was not personally compromised. The findings are described conceptually and in the context of the three-layer model, not as exploit tutorials. Where patch status is uncertain based on available sources, the article says so. Where the research characterization requires further verification, the article attributes rather than asserts.

This is the appropriate posture for writing about active security research. The goal is not to raise fear or to provide capability to bad actors. It is to make the trust model legible so that developers can make better decisions about environment choice and permission scope.

---

## The Practical Summary

The sandbox is a real control. It is not the only control. The failure mode that Pillar Research documented across these products is not agents defeating sandboxes directly—it is agents writing files that trusted host components later executed or acted on. The three-layer model (direct execution, workspace writes, host trust) describes where those risks live. The four failure modes (denylist gaps, executable workspace configuration, command-name allowlists, privileged local daemons) describe how they manifest.

The defensive response is not to stop using coding agents. It is to:

1. Audit what your agent can write and which host tools trust those writes.
2. Tighten execution policy from name-level to invocation-level where possible.
3. Remove privileged sockets and production credentials from the agent's session.
4. Keep production-adjacent and untrusted-input work in disposable environments.
5. Treat configuration file changes from agent sessions with the same review discipline as code changes.

The boundary the sandbox enforces is meaningful. Know exactly where it ends.

---

## References

**Pillar Research** — Multi-product sandbox escape and boundary bypass overview, published 2026-07-20: [pillar.security/blog/the-week-of-sandbox-escapes](https://www.pillar.security/blog/the-week-of-sandbox-escapes). This is the primary source for all vulnerability characterizations, product-specific findings, patch status, and CVE references in this article.

**BleepingComputer** — Independent news coverage of the Pillar Research findings, published 2026-07-20: [bleepingcomputer.com/news/security/cursor-codex-gemini-cli-antigravity-hit-by-sandbox-escapes/](https://www.bleepingcomputer.com/news/security/cursor-codex-gemini-cli-antigravity-hit-by-sandbox-escapes/).

**Cursor Security** — Official security information and advisories: [cursor.com/security](https://cursor.com/security). Verify current patch status for CVE-2026-48124 and related workspace-hook issues through official Cursor security channels and the Pillar Research source above.

**OpenAI Codex CLI** — Repository and release notes at [github.com/openai/codex](https://github.com/openai/codex). Verify the 0.95.0 patch and pending CVE status for the `git show` allowlist issue directly through the repository's security advisories.

**Google Gemini CLI** — Security reporting and advisories through Google's Vulnerability Reward Program at [bughunters.google.com](https://bughunters.google.com). The Antigravity reports described as valid but downgraded by Google should be tracked through official Google security channels.

**Docker security hardening** — Docker's documentation on socket access and daemon privilege: [docs.docker.com/engine/security/](https://docs.docker.com/engine/security/). Relevant for the Docker-socket pattern regardless of specific product findings.

*Patch statements in this article reflect the Pillar Research and BleepingComputer sources. Readers should verify current advisory status through official vendor security channels before drawing conclusions about specific deployments.*
