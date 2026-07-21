---
title: "AGENTS.md Guide: Repository Instructions That Coding Agents Can Actually Use"
description: "Write useful AGENTS.md files with correct Codex discovery and precedence, root and nested scopes, practical templates, and maintenance checks."
keywords:
  - AGENTS.md guide
  - AGENTS.md Codex
  - coding agent instructions
  - Codex project instructions
  - nested AGENTS.md
sidebar_position: 15
tags: [tutorial, codex, agent-engineering, workflow]
---

# AGENTS.md Guide: Repository Instructions That Coding Agents Can Actually Use

---

The agent ran the tests, opened a pull request, and the CI pipeline immediately failed. Not because the logic was wrong—the logic was fine. It had run `npm test` in the `packages/api` directory instead of `pnpm test --filter=api` from the monorepo root, generated a client SDK file directly into `src/generated/` without regenerating the index barrel, and left the build in a broken state that any human contributor would have caught in thirty seconds.

Nobody had told it not to. There was a `CONTRIBUTING.md` explaining the pnpm workspace setup, a `Makefile` with the correct targets, and three pages of onboarding notes—all written for human readers who would read them top-to-bottom, once, before touching anything. The agent had a task and a working directory. It made locally reasonable choices. The repository-wide conventions existed nowhere it could discover them.

That is the problem `AGENTS.md` is designed to solve.

---

## What AGENTS.md Is

[agents.md](https://agents.md) presents `AGENTS.md` as a plain Markdown file with no mandatory fields, no schema to validate, and no runtime to install. As of the time this guide was written, the site reports more than 60,000 open-source repositories using the convention—verify the current figure at [agents.md](https://agents.md) before quoting it. The format is intentionally minimal: a Markdown file placed where a coding agent will find it, containing the instructions that agent needs to work correctly in that codebase.

The core insight is placement. Instructions close to the code they govern are more likely to be discovered, more likely to stay current, and easier for contributors to audit than instructions buried in onboarding wikis or scattered across comments. `AGENTS.md` is not a new spec; it is a convention for where to put information the agent needs.

---

## What Belongs in the Root File

For Codex, the root `AGENTS.md` is the broad repository instruction file discovered for work in that tree. Keep it short enough to fit comfortably within context and accurate enough that a stale line does not misdirect the agent.

**Commands and invocation.** State the exact commands for building, testing, linting, and formatting. Do not describe them—write them. If your project uses a wrapper script, name it:

```
Build:   pnpm build --filter=...
Test:    pnpm test --filter=<package>
Lint:    pnpm lint
Format:  pnpm format
```

A vague instruction like "use the monorepo test runner" produces the same guessing that caused the opening failure. An agent cannot look up intent; it can only act on text.

**Directory structure.** Give a brief map of the top-level layout so an agent working in `packages/api` understands where shared utilities live, where generated files land, and which directories it should not touch:

```
packages/api/      — Express service, owns its own schema
packages/web/      — React app, consumes generated client
shared/            — shared TypeScript types, do not modify without migration
infra/             — Terraform, no agent edits without explicit task
src/generated/     — GENERATED: do not edit by hand, run `pnpm gen` to regenerate
```

**Invariants.** State the rules that must hold after every change: no direct edits to generated files, no new dependencies added to the root `package.json`, test coverage must not drop below threshold, all public API changes need a changelog entry. These are not aspirational guidelines; they are constraints the agent should treat as hard stops.

**Verification steps.** Tell the agent what to run before considering a task complete. This matters more than it sounds. An agent that runs only the tests relevant to the file it changed may pass local checks while breaking an integration the CI pipeline catches twenty minutes later. Specify the minimum verification surface:

```
Before opening a PR:
  1. pnpm build (from root)
  2. pnpm test --filter=<affected package>
  3. pnpm lint
```

**Scope boundaries.** State which parts of the repository are off-limits for autonomous changes, which require human review, and which directories an agent should not even read without an explicit task. This is especially important in repositories that mix application code with infrastructure definitions, secrets management, or compliance-sensitive data.

**Generated-file rules.** Generated files are a persistent source of agent mistakes. The agent sees a `.ts` file with a bug; it edits the `.ts` file; the bug returns on the next generation run because the real source is a `.graphql` schema. Be explicit: list generated directories, name the generation command, and state that edits go to the source, not the output.

---

## File Structure and Codex Precedence

> **Note:** The following precedence rules describe **Codex-specific behavior**. Other agents and tools that adopt the `AGENTS.md` convention may implement discovery differently. Always verify against the documentation for the agent you are using.

### A Small Tree

```
my-repo/
├── AGENTS.md                    ← root, repository-wide rules
├── packages/
│   ├── api/
│   │   ├── AGENTS.md            ← api-subtree rules; closer conflicts override root
│   │   └── src/
│   └── web/
│       ├── AGENTS.override.md   ← takes precedence over AGENTS.md at this level
│       └── src/
└── infra/
    └── AGENTS.md                ← infra-subtree rules
```

### How Codex Discovers Files

Codex walks from the **repository root to the current working directory**. For each directory in that path, it selects exactly one file, evaluated in this order:

| Priority | File | Notes |
|----------|------|-------|
| 1 (highest) | `AGENTS.override.md` | Selected if present; `AGENTS.md` ignored at this level |
| 2 | `AGENTS.md` | Selected if no override file present |
| 3 | Configured fallback names | Agent-level configuration; consult Codex docs |

At the global (user-level) scope, `AGENTS.override.md` wins over `AGENTS.md` by the same rule.

**Closer instructions override broader instructions.** If the root `AGENTS.md` says "use `pnpm test`" and `packages/api/AGENTS.md` says "use `jest --config jest.api.config.js`", an agent working in `packages/api/` applies the closer instruction for tests. The root instruction still applies for everything not addressed by the nested file.

The combined size of all discovered instruction files is capped at **32 KiB** by default. This is a current implementation detail, not a permanent specification; check the OpenAI Codex documentation for the current value before designing around it. If your instruction chain approaches this limit, you are probably including too much.

### The Override File Pattern

`AGENTS.override.md` replaces `AGENTS.md` only at the same directory level. If `packages/web/AGENTS.override.md` exists, Codex ignores `packages/web/AGENTS.md` there, but broader root instructions remain in the chain unless a closer rule conflicts. Use overrides deliberately so contributors do not add rules to the same-level file that is being skipped.

### Session Lifecycle

The instruction chain is rebuilt at the start of each run or session. Codex does not persist discovered instructions between sessions; `/init` can scaffold the file, but the discovery walk happens fresh each time. This means changes to `AGENTS.md` take effect immediately on the next run—a useful property for fixing bad instructions, and a risk if an accidental commit lands a breaking change.

---

## When Nested Files Help—and When They Hurt

### When Nesting Is Justified

Add a nested `AGENTS.md` when a subtree has genuinely different conventions that would be wrong to apply globally:

- **Different test commands.** A Python service in a JavaScript monorepo might need `pytest -x` instead of `pnpm test`.
- **Different generated-file rules.** A protobuf service generates its client differently from a GraphQL service in the same repo.
- **Explicit scope containment.** An `infra/AGENTS.md` that says "do not create or destroy resources without an approved plan" adds a hard stop at the subtree level that is more visible than a root-level note.
- **Package-specific invariants.** A payments package may require that every change touches the audit log; the web package does not.

The test: if a developer working exclusively in that subtree for a week would encounter different conventions than a developer working in the root, a nested file is justified.

### When Nesting Creates Problems

**Contradiction without coverage.** If the root file says "all tests must pass" and a nested file changes the test command but not the verification requirement, an agent may pass the wrong tests and believe the invariant is satisfied.

**Invisible same-level policy.** When `AGENTS.override.md` suppresses `AGENTS.md` in a directory, rules that exist only in that same-level regular file are skipped. Root instructions remain in the chain, subject to closer conflicting rules.

**Duplication drift.** Copy-pasting the root build command into five nested files means five places to update when the command changes. Put repository-wide commands only in the root; nest only what genuinely differs.

**Scope creep.** A nested file that re-explains the entire repository structure is not a nested file—it is a second root file competing with the first. Nested files should address the delta, not the whole.

---

## How AGENTS.md Relates to Other Instruction Types

These distinctions matter because confusion between them is a common cause of duplicated or misplaced content.

| Type | Location | Purpose | Audience |
|------|----------|---------|---------|
| **AGENTS.md** | Repository | Repository-wide commands, constraints, conventions | Coding agents |
| **Memory** | Agent/project context | Learned preferences, project-specific facts accumulated over sessions | Agent's own persistence layer |
| **Skills** | Agent configuration | Invoked, reusable workflow steps (e.g., a "run deploy" skill) | Agent runtime |
| **README / docs** | Repository | Human-facing explanation of what the project does and how to use it | Human contributors and users |
| **Prompts** | Task input | Task-specific intent for a single run ("refactor this function") | Single task context |

`AGENTS.md` is not documentation. It does not explain why the project exists, how the architecture evolved, or what the roadmap looks like. An agent reading `AGENTS.md` is not trying to understand your product—it is trying to know what to run, what not to touch, and what a correct outcome looks like.

`AGENTS.md` is not memory. Memory may accumulate across sessions; `AGENTS.md` is typically maintained with the repository by contributors. Putting personal or ephemeral session notes into it is usually wrong because they become shared instructions.

`AGENTS.md` is not a prompt. A prompt specifies what to do in a particular task. `AGENTS.md` specifies the constraints that govern how any task in this repository should be done. The difference is scope and durability.

---

## Mistakes That Make AGENTS.md Harmful

### Vague Prose

*"Make sure to follow our testing conventions."*

This instructs nothing. An agent cannot infer which conventions apply or where they are documented. Either state the convention or link to a machine-readable source. If you cannot state it concisely, it may not be ready to be an agent instruction.

### Stale Commands

A build command that worked eight months ago and now points to a script that was renamed is worse than no instruction—it produces a confident failure instead of a recoverable guess. Treat `AGENTS.md` entries as code: they break when the codebase changes and must be updated in the same commit.

### Giant Context Dumps

Pasting the entire `CONTRIBUTING.md` into `AGENTS.md` consumes context budget, buries the actionable rules in prose, and creates a second document to keep synchronized. Write what an agent needs to act; link to human documentation for everything else.

### Duplicated Rules

A rule stated in the root file and re-stated in three nested files will eventually diverge. When they diverge, the agent's behavior depends on which file it discovered last—a confusing, hard-to-debug inconsistency. Keep each rule in exactly one place.

### Contradictions

A root file that says "never commit to main directly" and a nested file that says "you may push hotfixes directly to main" creates a contradiction that the agent cannot resolve. Closer instructions win in Codex, but the agent has no way to know whether the contradiction was intentional. Write nested files to extend, not to silently negate.

### Secrets and Credentials

`AGENTS.md` is typically committed to the repository. Treat anything placed there as potentially version-controlled and public. Never put API keys, tokens, passwords, or secret values in it.

### Instructions That Cannot Be Verified

*"Be careful with the database migrations."*

An agent cannot verify whether it was careful. Write verifiable instructions: "Run `pnpm db:validate` after any migration change; it should exit 0." If a constraint cannot be expressed as something the agent can check, reconsider whether it belongs in this file at all.

---

## Starter Template

```markdown
# AGENTS.md

## Commands

- Build:   pnpm build (from repo root)
- Test:    pnpm test --filter=<package>  (run only affected packages)
- Lint:    pnpm lint
- Format:  pnpm format
- Gen:     pnpm gen  (regenerates all generated files)

## Directory Overview

- packages/api/     — Express API service
- packages/web/     — React frontend
- shared/           — Shared TypeScript types; coordinate changes
- src/generated/    — GENERATED. Do not edit. Run `pnpm gen` to update.
- infra/            — Terraform. Do not modify without an explicit task.

## Invariants (must hold after every change)

1. `src/generated/` is never edited by hand.
2. No new root-level dependencies without package.json review.
3. All exported functions have JSDoc type annotations.
4. `pnpm build` exits 0 before any PR.

## Verification Before PR

1. pnpm build
2. pnpm test --filter=<affected>
3. pnpm lint

## Off-Limits Without Explicit Task

- infra/
- .github/workflows/
- shared/ (requires migration coordination)

## Notes

- This file is authoritative for agent behavior in this repository.
- Nested AGENTS.md files apply to their subtree only.
- Do not add secrets, credentials, or environment variable values here.
```

Adjust section names to match your project. Keep the total character count well under the 32 KiB combined limit—this template is intentionally short.

---

## Debugging Instruction Discovery

When an agent ignores a rule or applies the wrong command, the likely causes are:

1. **Wrong working directory.** Codex walks root to CWD. If the agent's working directory was set to a subdirectory that skips a relevant `AGENTS.md`, that file is never read. Check what CWD the agent session used.

2. **Override file suppression.** If an `AGENTS.override.md` exists at any level in the discovery path, the corresponding `AGENTS.md` at that level is not read. Audit override files to confirm they contain everything you intended the regular file to provide.

3. **Size limit reached.** If the total discovered instruction chain exceeds the 32 KiB limit, later content is truncated. Keep instruction files concise and check the combined size of your discovery path.

4. **Stale session.** The chain is rebuilt per run or session, so start a fresh run after changing instructions. The file does not need to be committed for Codex to read the current filesystem.

5. **Contradiction from nested file.** A closer file overrode a rule you expected to apply. Print the discovery path mentally: root → intermediate directories → CWD, and identify which file wins at each level for the rule in question.

---

## Maintenance Checklist

Run through this list whenever you change a build command, add a generated directory, rename a script, or restructure the repository:

- [ ] **Commands are current.** Every command in every `AGENTS.md` was tested after the last structural change.
- [ ] **Generated directories are listed.** Every directory that should not be edited by hand is marked as generated.
- [ ] **No duplicated rules.** Each rule appears in exactly one file; nested files address only the delta.
- [ ] **No contradictions.** Nested file rules extend root rules; they do not silently negate them.
- [ ] **No secrets.** Grep for tokens, passwords, and environment variable values.
- [ ] **Verification steps are runnable.** Every command in the "before PR" section exits cleanly from a fresh checkout.
- [ ] **Off-limits scope is current.** Directories that were added or reorganized are reflected in scope boundaries.
- [ ] **Size is within budget.** Combined instruction chain for common working directories is well under 32 KiB.
- [ ] **Override files are intentional.** Every `AGENTS.override.md` has a documented reason for suppressing the regular file.

---

## References

- [agents.md](https://agents.md) — community convention site; check for current adoption numbers and tooling compatibility notes
- [OpenAI Codex AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md) — Codex-specific discovery, precedence, size limits, and `/init` behavior

Precedence rules, size limits, and file selection behavior described in this guide reflect the Codex implementation at time of writing. The agents.md convention is adopted by other tools with varying implementations—verify behavior for the agent you are deploying.

---

The agent in the opening scenario did not fail because it was wrong. It failed because the repository never told it what right looked like in this specific codebase. A well-maintained `AGENTS.md` is not a constraint on what agents can do—it is the information that lets them do the right thing without a human watching over every decision.

Keep the root file short, accurate, and verifiable. Add nested files only where the subtree genuinely differs. Treat every line as code that will break when the codebase changes. The payoff is not a smarter agent; it is a repository where the agent's locally reasonable choices are also the repository-correct ones.

## Related Guides

- [Coding Agent Memory](/docs/tutorials/coding-agent-memory/)
- [Spec-Driven Development with GitHub Spec Kit](/docs/tutorials/spec-driven-development-guide/)
