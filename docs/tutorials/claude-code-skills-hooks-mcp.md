---
title: "Claude Code Skills, Hooks, and MCP: When Should You Use Each?"
description: "Learn when to use Claude Code Skills, Hooks, or MCP by separating reusable procedures, lifecycle automation, and external tool connections."
keywords:
  - Claude Code Skills vs Hooks vs MCP
  - Claude Code Hooks vs Skills
  - Claude Code Skills vs MCP
  - Claude Code Hooks examples
  - Claude Code Skills examples
sidebar_position: 8
tags: [claude, tutorial, agent-engineering]
---
# Claude Code Skills, Hooks, and MCP: When Should You Use Each?

There is a moment in most Claude Code workflows where you catch yourself reaching for the same extension slot for three completely different needs. The release checklist that Claude should follow. The formatter that must run after every edit regardless of what Claude thinks. The GitHub issue that Claude needs to read before writing anything. All three feel like "making Claude do something." They are not the same kind of thing, and putting them in the wrong place produces failures that are genuinely hard to diagnose.

Here is the direct answer before anything else: **use a Skill when Claude needs reusable know-how, a Hook when an event must trigger a controlled action, and MCP when Claude needs a governed connection to an external tool or data source.** The rest of this article is about why that boundary matters and how to find it in your own setup.

If you are still learning the basic terminal-agent workflow, start with the [Claude Code beginner guide](/docs/tutorials/claude-code-guide/) before adding these extension layers.

---

## The Failure Mode of Treating All Three as "Extensions"

When I started building a pull-request workflow in Claude Code, I added everything to `CLAUDE.md`. The release procedure was there. The instruction to run the formatter was there. The instruction to "check the GitHub issue" was there. It worked until it didn't—and when it stopped working, I had no idea which part had broken or why. The procedure would sometimes be skipped. The formatter would sometimes run and sometimes not. The issue data would sometimes be hallucinated because there was no actual connection to GitHub, just an instruction to "look it up."

The vague label "extension" obscures three genuinely different requirements: know-how, event control, and connectivity. Each has a different trigger, a different trust model, and a different failure mode. Treating them as one kind of thing means you cannot reason about your workflow clearly.

Think of it as three parts of a workshop. The playbook explains the craft. The tripwire reacts at a defined boundary. The connector reaches another system. You need all three, but they do different jobs and break in different ways.

---

## Skills: Reusable Know-How That Loads When Relevant

A Skill packages reusable instructions and optional supporting resources around a `SKILL.md` file. In the pull-request workflow, the Skill is where the review and release procedure lives: what to check, in what order, what an acceptable output looks like, and how to interpret ambiguous results.

The key characteristic of a Skill is that its body loads when it is used rather than sitting in memory continuously the way always-loaded `CLAUDE.md` guidance does. Claude can select a Skill when it looks relevant to the current task, or you can invoke it directly by name. This is appropriate for a release checklist because the checklist is substantive, context-specific, and only needed during release operations—not during every file edit.

If the boundary between durable guidance and task-specific material is still unclear, first decide [what a coding agent should remember between sessions](/docs/tutorials/coding-agent-memory/).

A Skill can also carry supporting resources: a checklist template, an output contract describing what a completed review looks like, examples of edge cases. This is not just a prompt. It is a package of know-how that Claude can work with.

**What it owns:** reusable procedural knowledge and reference material<br />
**What triggers it:** relevance detection or direct user invocation<br />
**Model discretion:** substantial—Claude interprets and applies the Skill<br />
**External connectivity:** no inherent connectivity; the Skill supplies no standardized external connection by itself<br />
**Main risk:** the Skill may not be invoked when you expect it, or Claude may apply it differently than intended in edge cases

**Good example:** a release procedure Skill containing the checklist, output format requirements, and how to handle ambiguous test results.

**Clear misuse:** using a Skill to guarantee that a formatter runs after every edit. A Skill cannot guarantee execution at a lifecycle event. That requirement belongs to a Hook.

One note on custom commands: `.claude/commands/` files continue to work, but custom commands have been merged into the Skills model. If you have existing command files, they are not broken—but understanding Skills is now the better frame for building new reusable procedures.

---

## Hooks: Event-Triggered Control Without Model Discretion

A Hook runs at a defined Claude Code lifecycle event. The formatter that must run after every code edit is a Hook requirement. So is the gate that blocks a write to a protected configuration file. These are not procedures Claude should choose to follow—they are controls that must execute at a defined point in the lifecycle, independent of what Claude would select.

Claude Code provides several lifecycle events where Hooks can attach. A command Hook runs a shell command at that event and is the deterministic variant: the trigger fires, the command runs. Prompt-based and agent-based Hooks can involve model judgment and are not deterministic in the same way. The distinction matters when you are building a guardrail that cannot afford ambiguity.

For the pull-request workflow: a Hook runs the local formatter after a file-write event. Another Hook validates that no file in a protected directory has been touched before allowing a commit to proceed. These actions happen regardless of whether Claude thinks they are necessary. That is the point.

**What it owns:** event-triggered local actions and local validation gates<br />
**What triggers it:** a defined Claude Code lifecycle event<br />
**Model discretion:** minimal for command Hooks; variable for prompt/agent Hooks<br />
**External connectivity:** limited to what the local command can reach<br />
**Main risk:** the command itself

### Security boundary for Hooks

Hook commands run with your environment and your permissions. A Hook that silently deletes a file, modifies a file outside the intended scope, or calls a network endpoint with elevated credentials does those things with the same authority as you. A deterministic trigger does not make an unsafe command safe. Every Hook command deserves explicit review before it runs in a real workflow—not because Claude Code cannot manage Hooks, but because the consequences of a bad command at a lifecycle event can be significant.

Do not treat a Hook as a substitute for proper permissions design, code review, or safe command construction. The Hook guarantees execution; it does not guarantee that the command does the right thing.

**Good example:** a post-write Hook that runs `prettier --write` on changed files, or a pre-commit Hook that checks whether any file in `/config/protected/` has been modified and exits with an error if so.

**Clear misuse:** using a Hook to "remind Claude" about the release procedure. That is Skill territory. A command Hook should not own the release procedure itself—it is an event-triggered execution boundary.

---

## MCP: Governed Connectivity to External Systems

Model Context Protocol connects Claude Code to external tools, data sources, databases, and APIs through an open protocol. In the pull-request workflow, MCP is how Claude actually reads the GitHub issue, not just receives an instruction to do so. It is also how Claude would query a monitoring system for error rates, create a comment on a pull request, or look up a record in a database.

For a broader introduction to MCP setup and integration patterns, see the [MCP Server Guide](/docs/tools/mcps/).

The critical difference from a Skill is that MCP provides real connectivity. Claude is not synthesizing data from training or following an instruction to "check GitHub"—it is invoking a governed connection that returns actual current data and can perform authorized external actions.

On tool loading: the current Claude Code documentation indicates that tool search defers MCP tool definitions until they are needed by default in supported first-party configurations. This is a meaningful architectural detail if you are reasoning about what Claude sees at the start of a session, but the practical takeaway is that MCP tools are available when relevant, not that the entire server is loaded upfront regardless.

**What it owns:** external tool invocation and live data retrieval<br />
**What triggers it:** Claude's need for external data or an authorized external action<br />
**Model discretion:** substantial—Claude decides when to invoke which tool and how to use the result<br />
**External connectivity:** yes, by design<br />
**Main risk:** the external system itself, and the trust model around third-party servers

### Security boundary for MCP

Third-party MCP servers and external content require careful trust review. An MCP server that has read access to your issue tracker, write access to your pull requests, or query access to a production database is operating with real authority. Prompt injection through external content—a maliciously crafted issue title that instructs Claude to take an action via MCP—is a realistic risk, not a theoretical one. Review the permissions each MCP server requests, limit them to what the workflow actually needs, and treat external content that flows through MCP with the same skepticism you would apply to any user-controlled input.

Do not assume that a well-known third-party MCP server is automatically safe. The protocol is sound; the server's implementation and permissions scope are what need review.

**Good example:** an MCP connection to a GitHub server that allows Claude to read the linked issue and its labels before starting a review, and to post a structured comment when the review is complete.

**Clear misuse:** using MCP to load a static procedure that does not change and has no external state. That belongs in a Skill, which loads the procedure on demand without requiring an external connection.

---

## How the Three Work Together

The composition is cleaner once each mechanism has a clear owner.

In a complete pull-request workflow:

- The **Skill** contains the review procedure, the evidence checklist, and the output contract. It explains what to do, in what order, and what a completed review looks like. Claude invokes it when starting a review, or the user invokes it directly.

- **MCP** supplies the current issue, the pull request metadata, and any monitoring data Claude needs to make an informed judgment. If the review produces a structured comment that should be posted to the pull request, MCP performs that action through an authorized connection.

- A **Hook** guarantees that the local formatter runs after any file write, and that the protected configuration directory is validated before any commit proceeds. These actions are not Claude's to choose—they happen at the lifecycle event.

The Skill explains the craft. MCP connects to the external state. The Hook holds the local boundary. Each mechanism has a single owner, and each failure mode is isolatable.

Composition goes wrong when the boundaries blur. If the Skill includes raw shell commands meant to "guarantee" the formatter runs, you have moved execution logic into the wrong layer. If you try to use a Hook to deliver external data to Claude, you are working around MCP rather than using it. If you route everything through MCP because it feels like the most capable mechanism, you are paying for connectivity and trust review on problems that do not need them.

---

## Decision Matrix

| | Skill | Hook | MCP |
|---|---|---|---|
| **Owns** | Reusable procedures and knowledge | Event-triggered local execution | External connectivity and authorized actions |
| **Triggered by** | Relevance or direct invocation | Defined lifecycle event | Claude's need for external data or action |
| **Model discretion** | Substantial | Minimal (command Hook) | Substantial |
| **Needs external access** | No | Whatever its command can reach | Yes, by design |
| **Main risk** | Inconsistent application | Unsafe command execution | Untrusted server or prompt injection |
| **Good example** | Release checklist with output contract | Post-write formatter, pre-commit validator | GitHub issue retrieval, monitoring query |
| **Clear misuse** | Guaranteeing lifecycle execution | Delivering external data to Claude | Loading static procedures with no external state |

---

## The Smallest Mechanism That Actually Owns the Requirement

I have come to use this as a practical heuristic: reach for the smallest mechanism that actually owns the requirement. Not the most capable, not the most familiar—the one whose ownership model matches the problem.

A procedure that Claude should know and apply belongs in a Skill. An action that must happen at a defined event regardless of model judgment belongs in a Hook. A connection to external state that Claude needs to read or write belongs in MCP. When you are not sure which one to reach for, ask which failure mode is more tolerable: a Skill applied inconsistently, a Hook that did not run when you expected, or an MCP tool that could not reach its server. The answer usually clarifies the right layer.

The risk that drove my earlier concern about MCP—that it was being used too broadly, with too little review of what each server was actually permitted to do—has not gone away. The current tool-search behavior is better than the old eager-loading assumption, but the trust model for external servers still deserves explicit attention. That concern is a reason to be deliberate about when MCP is the right layer, not a reason to avoid it where it genuinely belongs.

---

## The Audit

Before you close this article, identify three things in your current Claude Code setup:

1. **A repeated procedure.** Is it in a Skill, in `CLAUDE.md`, or scattered across custom commands? If it is procedural knowledge that Claude should apply in specific situations, it belongs in a Skill. If it is always-applicable guidance, `CLAUDE.md` is correct. If it is neither, clarify what it actually is before deciding.

2. **An event guarantee.** Is there something that must happen at a lifecycle event—a formatter, a validator, a notification—regardless of what Claude would choose? If that guarantee is currently implemented as a Skill instruction or a `CLAUDE.md` reminder, it is in the wrong place. Move it to a Hook, and review the command carefully.

3. **An external connection.** Is Claude accessing live data from GitHub, a monitoring system, a database, or any external API? If that connection currently works through instructions to "check" a system, Claude is either hallucinating data or you have a gap in your workflow. If the connection is real and governed through MCP, audit what permissions each server holds and confirm they are scoped to what the workflow actually needs.

If each of those three things has a clear owner—the Skill, the Hook, or the MCP connection—your extension architecture is in reasonable shape. If any of them are in the wrong layer, you now have a cleaner model for where to move them.

For a wider progression from first agent task to durable repository workflow, continue with the [AI Coding Agent Beginner Route](/docs/tutorials/ai-coding-agent-beginner-guide/).

---

## References

- **Claude Code Skills**: https://code.claude.com/docs/en/skills
- **Claude Code Hooks Guide**: https://code.claude.com/docs/en/hooks-guide
- **Claude Code MCP**: https://code.claude.com/docs/en/mcp
