---
title: "Audit and Maintain Project Instructions with claude-code Prompt Audit"
description: "Use Claude Code prompt-audit to check CLAUDE.md and project instructions, verify stale commands and paths, review edits, and confirm loading in a fresh session."
keywords:
  - "Claude Code prompt audit"
  - "doctor prompt-audit"
  - "CLAUDE.md audit"
  - "Claude Code project instructions"
sidebar_position: 37
tags: [tutorial, claude-code, agent-engineering]
---

# Audit and Maintain Project Instructions with `claude-code` Prompt Audit

You have been using Claude Code for a while now. Your repository is full of CLAUDE.md files, Skills, custom commands, and local rules. They started as helpful scaffolding but have drifted: stale paths, outdated package managers, and conflicting guidance clutter the context window.

This guide walks you through a concrete, small-scale maintenance task: using the `/doctor prompt-audit` command to locate and correct those inconsistencies. By the end, you’ll be able to:

- Locate which instructions are actually loaded into your session
- Run a focused audit that inspects paths, language, and behavior
- Judge findings against repository evidence
- Make informed edits while keeping necessary constraints
- Confirm changes didn’t break loading or behavior in a fresh session

We’ll stick to one well-scoped issue per example so you can inspect each change clearly.

## Prerequisites

Before running the audit:

- Ensure you’re running Claude Code v2.1.283 or later, which includes `/doctor prompt-audit`.

Check your version:

```bash
claude --version
```

If needed, update your installation:

```bash
claude update
```

- Open the repository you want to audit:

```bash
cd /path/to/project
```

- Launch Claude Code and enter `/doctor prompt-audit` in the interactive session.

That’s it. From here, we’ll treat this as a practical workflow rather than abstract theory.

## What `prompt-audit` Actually Checks

Running `/doctor prompt-audit` tells Claude Code to:

- Inspect CLAUDE.md, .claude/CLAUDE.md, and related rule files for outdated prompting patterns
- Prioritize stale file paths, deprecated package commands, and contradictory guidance across multiple instruction sources
- Preserve the thinking keywords that Claude Code still documents
- Present findings first; ask for your confirmation before applying any changes

This is not a generic “formatting” tool. It’s specifically tuned to how Claude Code reads project context at launch and during file operations.

A quick contrast:

- `claude doctor` (shell) – prints read-only diagnostics about your installation and settings; no session needed.
- `/doctor prompt-audit` (in-session) – scans your active configuration and prompts for edits.
- `/claude-api prompt-audit` – a separate workflow for API-level prompts and tool descriptions, not this project’s config.

For repository maintenance, you want the in-session version.

## Inspecting Loaded Instructions Before Auditing

Before auditing the first case study, inspect how Claude has loaded your project:

- Run `/context` in the interactive session. You will see the list of Memory files actually loaded for this context.
- Run `/memory` to view editable memory-file locations. Note that some listed paths may be nonexistent or irrelevant; these are placeholders, not guaranteed files.
- Run `/doctor prompt-audit`. The doctor will report findings and ask for confirmation before applying any changes.

A practical inspection step is to have the doctor display each affected file location, original instruction, reason for concern, and proposed edit.

## Case Study 1: Stale Package Manager Instructions

### The Problem

Your project uses pnpm as the package manager, but a rule file (likely in `.claude/rules/` or embedded in CLAUDE.md) still says:

> “Use npm to install dependencies.”

Over time, this drifts from reality. Developers install with `pnpm`, run scripts via `pnpm <command>`, and the instruction creates confusion when Claude Code suggests the wrong command.

### Audit Findings

Example prompt-audit snippet (abbreviated):

```
- Stale path/command pattern:
  - Instruction: "Run npm install"
  - Conflicts with: package.json scripts invoking pnpm
  - Suggested fix: Replace "npm install" with "pnpm install"
```

Before applying any suggested change, verify it against your project’s `package.json`, the committed lockfile, your actual scripts, and CI instructions to ensure it fits your environment.


### Evidence Check

Before editing, confirm the repo’s true behavior:

```bash
cat package.json
ls pnpm-lock.yaml
```

Look at a real script invocation in CI or Makefiles if you have them. You want to match reality, not guess.

### Proposed Edit

The safest change is minimal:

- Replace `"npm install"` with `"pnpm install"` in the flagged rule file.
- If other instructions suggest `npx` or `npm run`, update them consistently.

After `/doctor prompt-audit` proposes fixes in the package-manager case, don’t immediately say “apply”. Instead, ask in plain language to see the proposed changes first:

```
Please show me the proposed diff for each change and explain why each edit is suggested before applying any of them.
```

Review the proposed edits line by line. Ask for rationale if something feels ambiguous:

> “Why does this rule say npm instead of pnpm? Is there another script that needs updating?”

Once satisfied, confirm the change and then inspect the result:

```bash
git status --short
git diff -- CLAUDE.md .claude/
```

You’ll typically see changes only in the specific instruction file. If you spot an unexpected change, revert it before continuing.

## Case Study 2: Broken File Paths in Instructions

### The Problem

A Skill or command description references a script that has been moved:

> “Call ./scripts/deploy.sh to deploy the project.”

But the actual path is now `./deploy.sh` at the repo root, or perhaps it’s in `bin/`. This pattern often appears when scripts move but documentation stays put.

### Audit Findings

Example output:

```
- Stale path reference:
  - Instruction: "Run ./scripts/deploy.sh"
  - No matching file under scripts/ in current repository
  - Suggested fix: Update to ./deploy.sh or remove if obsolete
```

This is exactly the kind of drift that slows down autonomous agents and causes silent failures when Claude Code tries to execute commands.

### Evidence Check

Confirm what actually exists:

```bash
ls -R | grep deploy.sh
# or simply:
find . -name "deploy.sh" 2>/dev/null
```

If the file is at the repo root, the fix is straightforward. If it’s gone entirely, you may want to remove the instruction rather than patch it.

### Proposed Edit

Again, stay surgical:

- Update `./scripts/deploy.sh` to `./deploy.sh`.
- Or replace with a generic command that matches your actual workflow (e.g., “Run the deploy script from bin/”).

```
Show me the proposed change and its file location before applying it.
```


Ask Claude Code to trace where it found the path:

> “Which rule file mentions ./scripts/deploy.sh and why?”

That helps you decide whether to retain that instruction or move it into a more appropriate location (like a scoped rule or Skill).

## Case Study 3: Contradictory Planning Behavior

### The Problem

One instruction insists on long, multi-step planning for every change. Another permits straightforward fixes. Agents get confused: do they plan exhaustively or act directly?

Example:

- CLAUDE.md: “Always create a detailed plan before modifying any files.”
- .claude/rules/planning.md: “For trivial changes, apply edits immediately without planning.”

This contradiction is common as rules accumulate across projects and authors.

### Audit Findings

Prompt-audit might flag something like:

```
- Contradictory guidance:
  - CLAUDE.md: "Always plan before editing"
  - .claude/rules/planning.md: "Skip planning for trivial edits"
  - Suggestion: Reconcile or scope each rule clearly
```

This is less about paths and more about behavior. The audit doesn’t automatically rewrite these; it shows you where they conflict so you can decide.

### Evidence Check

Review your team’s actual workflow:

- Do trivial changes truly never need planning? (Often they do, in terms of impact checks.)
- Is long planning slowing down small tasks or causing unnecessary delays?

You might also check package.json scripts or CI behavior to understand what “trivial” means in practice.

### Proposed Edit

Reconcile the rules:

- Option A: Keep a single rule that is context-aware, e.g., “Plan for non-trivial changes; act directly for trivial edits.”
- Option B: Scope the long-planning rule to specific codebases or modules.

Prompt-audit can help draft wording, but you must validate it against real tasks. Ask for concrete examples:

> “Give me two examples where this rule would cause unnecessary delay and one where it prevents a mistake.”

Then edit accordingly. For instance, in CLAUDE.md:

```markdown
# Planning behavior

- For non-trivial changes (schema migrations, API contracts, multi-file refactorings): create a short plan before editing.
- For trivial changes (single-file edits, configuration tweaks): apply edits directly.
```

Preview the change and ask Claude Code to compare it with the existing rule set for clarity.

## Inspecting Memory and Rule Sources

Sometimes the confusing bits aren’t in CLAUDE.md at all but in memory files that aggregate rules across user and project scopes.

Run:

```text
/memory
```

This lists memory-file locations, some of which may point to non-existent or stale paths. To see what’s actually loaded in your session:

```text
/context
```

Notes:

- Project CLAUDE.md and `.claude/CLAUDE.md` load at launch.
- Nested CLAUDE.md files load when Claude reads files inside those directories.
- Files imported with `@path` still enter context; splitting them into imports helps organization but doesn’t remove their context cost.

Use `/memory` to choose an existing memory file, then ask Claude to correct one obsolete reference inside it. Do not try to rename that file; `/memory` is for selecting and editing content, not managing filenames.

Example workflow:
- Open a fresh session in the same project context.
- Run `/context` to confirm what Memory files are loaded after your edits.
- Update only the specific lines needed; remove any duplicated guidance unless it still serves as a reminder or example.


## Review Loop: Before and After Editing

A good maintenance cycle is simple but disciplined:

1. Run the audit: `/doctor prompt-audit`
2. Pick one clear issue (path, command, or behavior).
3. Check repository evidence (files, scripts, CI).
4. Ask Claude Code for a preview and rationale.
5. Edit confidently; confirm via `git diff`.
6. Open a fresh session.
7. Run `/context` to verify what’s loaded.
8. Compare the same small task: commands, paths, constraints, checks.

The key is “same small task.” If you can run a command that your developers actually use—say, installing dependencies or starting dev mode—and confirm it behaves as expected with the updated instructions, you have credible evidence the audit improved your setup.

## What to Keep and What to Discard

Not every flagged instruction should be removed:

- **Retain:**
  - Necessary safety rules (e.g., “Don’t commit secrets,” “Prefer linting before deploy”).
  - Test prerequisites that the code itself doesn’t reveal (environment variables, database state).
  - Project rationale that explains why certain tools or patterns are required.

- **Correct:**
  - Outdated commands or paths that no longer match the repo.
  - Ambiguous instructions that cause different behaviors across sessions.

- **Move to scoped rules or Skills:**
  - Task-specific procedures (e.g., “Deploy to staging” or “Run migrations for X schema”).
  - Patterns that should only apply when certain conditions are true.

The goal isn’t minimalism; it’s precision: context that is accurate, consistent, and aligned with your current workflow.

## Practical Tips While Auditing

- Start with one clear issue. Large batches make review noisy and error-prone.
- Ask Claude Code to request locations, rationale, and proposed edits before you commit changes.
- Use `git status --short` and `git diff -- CLAUDE.md .claude/` as your sanity checks.
- Always verify in a fresh session after editing; audit suggestions and observed task behavior are separate pieces of evidence.
- Keep the official docs handy for deeper reference:
  - Commands: https://code.claude.com/docs/en/commands
  - Memory: https://code.claude.com/docs/en/memory
  - Best practices: https://code.claude.com/docs/en/best-practices
  - CLI reference: https://code.claude.com/docs/en/cli-reference

## Final Checklist

Before you consider your instructions “maintained,” verify:

- [ ] Prompt-audit report shows no critical stale paths or commands.
- [ ] Loaded context (`/context`) matches the actual repo layout.
- [ ] A fresh session can execute your core workflow (install, dev, test) without ambiguity.
- [ ] Any remaining rules are intentional, scoped, and documented with rationale.

By treating instruction maintenance as a small, repeatable task—anchored by `/doctor prompt-audit` and backed by actual repository evidence—you keep your Claude Code setup accurate without burning cycles on speculative edits.

## Related Guides

- [Coding Agent Memory](/docs/tutorials/coding-agent-memory/)
- [Claude Code Skills, Hooks, and MCP](/docs/tutorials/claude-code-skills-hooks-mcp/)
