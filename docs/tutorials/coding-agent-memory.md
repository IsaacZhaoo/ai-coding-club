---
title: "Coding Agent Memory: What Should Persist Between Sessions?"
description: "Learn how to separate coding-agent memory into durable project rules, active task state, retrievable history, and disposable working context."
keywords:
  - coding agent memory
  - AI coding agent memory
  - coding agent persistent memory
  - coding agent session memory
  - coding agent memory management
sidebar_position: 7
tags: [tutorial, coding-assistant, agent-engineering]
---
# Coding Agent Memory: What Should Persist Between Sessions?

When real repository work started moving between Claude Code, Codex, and Antigravity, "memory" stopped meaning one thing. The package-manager rule that Antigravity needed to know was the same rule Claude Code needed to know, and it would still be true in three months. The authentication regression I was chasing had a goal, a current hypothesis, and a blocker that would be irrelevant the moment it was resolved. The debugging session from four weeks ago might be relevant again if the same symptom came back, but loading it into every prompt would be noise. And the five exploratory prompts I wrote on a Wednesday afternoon trying to understand a JWT expiry edge case were useful for about two hours and then permanently in the way.

Putting all of that into one memory file—one giant `CLAUDE.md` or one ever-growing notes document—made the workflow harder, not easier. The file grew stale faster than I trusted it. I spent time cleaning it up instead of using it. And the agent started treating three-month-old decisions as active constraints.

The answer I arrived at is this: **a coding agent does not need one giant memory; it needs separate layers for durable project rules, current task state, retrievable history, and disposable working context, each with a clear owner and an expiry rule.** This is a storage hierarchy, not a notebook. Different information has different retention policies, and collapsing them into one place fails all of them.

This article explains the four layers, how to assign ownership and expiry to each, and how to run a quick audit on your own repository to see which layer your current information belongs in.

---

## Why Sessions Make the Problem Visible

Anthropic's Claude Code documentation states it plainly: each session begins with a fresh context window. There is no implicit carry-forward. Whatever an agent learned in yesterday's session is gone unless something explicit bridges the gap. Claude Code documents two mechanisms for that bridging: user-written `CLAUDE.md` instruction files that persist project guidance, and agent-written auto memory that the model can write for itself across sessions.

OpenAI's Codex takes a layered approach. It reads `AGENTS.md` files before starting work, from a global scope down through the active project path, so guidance can be scoped to the whole machine, the repository root, or a specific subdirectory.

Both of these mechanisms are primarily designed for one category of information: stable guidance that should always be in scope. They are not designed to handle the full spread of things a real project generates over time. When you try to use `CLAUDE.md` or `AGENTS.md` as a general-purpose memory dump, you get a file that is too long, partially stale, and difficult to trust.

The fresh-session boundary is not a bug to route around. It is the correct behavior that forces you to be explicit about what actually needs to persist—and what does not.

---

## The Four Layers

I will make these concrete with a continuing example: your team is investigating an authentication regression. A recent change broke session token validation for a subset of users. You need to fix it. Here is how that work touches each layer.

### Layer 1: Durable Project Rules

**What belongs here:** package manager choice, build commands, code style conventions, architectural constraints, "always/never" instructions that apply regardless of what task is running.

In the authentication example: the rule that all authentication changes must include integration tests. The rule that you use `pnpm` and never `npm`. The rule that JWT validation lives in `src/auth/` and not in middleware. The requirement to run `pnpm typecheck` before committing.

These rules do not change with the task. They are true before the authentication regression and they will be true after it. They have no expiry tied to any ticket or sprint.

**Who writes it:** the developer or team lead, not the agent. This is deliberate policy.

**Always loaded or on demand:** always loaded. This is what `CLAUDE.md` at the repository root and `AGENTS.md` files are designed for. Anthropic describes `CLAUDE.md` as persistent guidance for project conventions, workflows, architecture, and repeated instructions. Codex reads its layered `AGENTS.md` chain before every task.

**What updates it:** a project decision. A team agrees to change the linter, the test framework, or the module structure. Someone updates the file as a deliberate act.

**Main failure mode:** staleness combined with authority. If an architectural decision from eighteen months ago is still in `CLAUDE.md` but no longer reflects reality, the agent will treat it as a constraint. I have seen this cause more confusion than a missing rule would. Review durable rules periodically, the same way you review a `Makefile` or a `CI` configuration—not daily, but not never.

A short `CLAUDE.md` that is always accurate is worth more than a comprehensive one that cannot be trusted.

---

### Layer 2: Current Task State

**What belongs here:** the current goal, who owns it, active blockers, hypotheses under investigation, next concrete action, and evidence of completion.

In the authentication example: "Investigating session token validation regression introduced in commit `a7f3c2`. Token expiry check in `validateSession()` appears to skip the `iat` claim. Current blocker: cannot reproduce locally against the test token set. Next action: add fixture tokens from the affected environment. Completion: passing integration tests covering `iat` and `exp` validation paths."

This information is current and specific. It has a clear endpoint. It is irrelevant once the task closes.

**Who writes it:** ideally, either the developer or the agent at task start, then updated as the task progresses. The agent can add its current hypothesis if it is useful. The developer sets the goal and completion evidence.

**Always loaded or on demand:** always loaded for the duration of the active task, then archived or deleted. It does not belong in Layer 1 after the task closes.

**What updates it:** progress on the task. A blocker is resolved. A hypothesis is confirmed or eliminated. The task completes.

**Main failure mode:** forgetting to close it. Task state files that outlive their task become stale context. An agent reading last sprint's task state as if it were current will ask about blockers that were resolved weeks ago or avoid approaches that were already tried.

There are structured tools designed specifically for this layer. Beads, for example, describes itself as a dependency-aware graph issue tracker and structured persistent memory for coding agents. The project's self-description emphasizes tracking tasks, blockers, and dependencies in a way that is readable by agents. Whether or not you use Beads specifically, the principle is the same: task state needs structure, a clear owner, and a clear completion trigger.

---

### Layer 3: Retrievable History

**What belongs here:** past debugging sessions, old architectural decisions with rationale, patterns from resolved bugs that might recur, notes from a spike that informed a choice you made six months ago.

In the authentication example: you fixed a very similar token validation bug eight months ago. The root cause then was timezone handling in the expiry check. That information is not relevant to every session, but if you hit a similar symptom again, it is exactly what you want to find.

**Who writes it:** the developer, a summarizing agent step, or a combination. Raw session transcripts are not the goal. Distilled records of what was learned are.

**Always loaded or on demand:** on demand. This is the key distinction from Layer 1. You do not load all past debugging sessions into every prompt. You retrieve the relevant subset when a new task pattern suggests it.

**What updates it:** time and relevance. Old history does not get deleted; it gets indexed. It is available when the current task resembles the context of a past session.

**Main failure mode:** nothing retrieving it at all, so it might as well not exist. History stored in a directory of flat files that no agent or developer ever queries provides zero value. The retrieval mechanism matters as much as the storage.

deja-vu is an example of a project in this space. It describes itself as a local index over existing coding-agent session histories, with CLI and MCP recall—the idea being that you search or query past sessions rather than always loading them. The project's self-description emphasizes on-demand retrieval as the design goal. Whether or not that specific tool fits your setup, the category is real: you need some path from "I recognize this symptom" to "here is the relevant prior work."

---

### Layer 4: Disposable Working Context

**What belongs here:** raw logs, exploratory prompts you wrote to understand a problem, failed hypotheses you walked back, half-finished thoughts, temporary scaffolding that helped you navigate a session.

In the authentication example: the seventeen prompts you sent on Thursday trying to figure out whether the regression was in the middleware or the service layer. The log output you pasted. The failed approach where you tried to patch the expiry check in the wrong function.

This is not useless while you are in it. It is how thinking works. But it has no value the moment the session closes. Loading it into the next session would be actively harmful.

**Who writes it:** the agent and developer together, in real time.

**Always loaded or on demand:** loaded only for the current session. Discarded on close.

**What updates or expires it:** the session end. No explicit action required.

**Main failure mode:** accidentally promoting it to a higher layer. I have done this: pasted exploratory log output into a `CLAUDE.md` section because I thought I might need it later, then forgotten about it for four months. The agent treated it as active guidance.

If you find yourself thinking "I should save this just in case," pause and ask which layer it belongs to. If the answer is Layer 3 (retrievable history), write a short summary and put it there. If it is genuinely disposable, let it go.

---

## Retention Matrix

| Layer | What It Carries | Owner | Load Policy | Expires When |
|---|---|---|---|---|
| Durable rules | Package manager, conventions, architecture, "always/never" | Developer, deliberate policy | Always | Team decision changes it |
| Task state | Goal, blockers, hypotheses, next action, completion evidence | Developer or agent | Always (active task only) | Task closes |
| Retrievable history | Old debug sessions, architectural rationale, prior resolutions | Developer or summarizing step | On demand | Practically never (indexed, not injected) |
| Disposable context | Raw logs, exploratory prompts, failed paths, session scaffolding | Agent and developer, real time | Current session only | Session end |

---

## What This Looks Like in Practice

A mature project might have this structure at the repository root:

```
CLAUDE.md              # Layer 1: durable project rules
AGENTS.md              # Layer 1: Codex layered guidance (root scope)
.task/current.md       # Layer 2: active task state
.history/              # Layer 3: indexed past sessions and decisions
```

`CLAUDE.md` stays short. It covers the things that are true today and will be true next year: build commands, test requirements, module boundaries, coding conventions that the whole team enforces. It does not contain ticket references, sprint goals, or debugging notes.

`.task/current.md` covers the live task. It answers: what is the goal, what is blocked, what is the active hypothesis, what does completion look like. It is updated as work progresses and replaced or archived when the task closes.

`.history/` is an index of things that might matter again. You do not read it automatically. You query it when you recognize a pattern.

Session scaffolding never touches the repository. It lives in the conversation and disappears.

The exact tooling matters less than the layer separation. The structure above works with nothing more than a text editor and discipline. Tools like Beads or deja-vu can formalize Layers 2 and 3 respectively, but they are not required to start.

---

## The Bigger Mistake to Avoid

The failure pattern I see most often is treating memory accumulation as progress. An agent workflow where the context file grows over time feels like the agent is "learning." Usually what is happening is that stale task state, old hypotheses, and session scaffolding are accumulating in a place that looks like project rules.

More memory loaded into every prompt is not always better. It can degrade the signal-to-noise ratio in exactly the place where precision matters most. The goal of the four-layer model is not to remember everything—it is to ensure that the right information is available with the right retrieval policy, and that information from one layer does not contaminate another.

A durable rule that is accurate is worth more than fifty rules that are partially accurate. A task state file that reflects what is happening right now is worth more than one that has four merged tasks and resolved blockers in it.

---

## A Memory Audit You Can Run Now

Before you move on, spend ten minutes on your current repository:

**1. Open your `CLAUDE.md` or `AGENTS.md`.** Read each section. Ask: is this true today? Is it team policy, or was it written during one task? Does it reference a ticket, a temporary blocker, or a specific sprint? Anything that references a task or a moment in time belongs in Layer 2 or Layer 3, not Layer 1. Move it or delete it.

**2. Look for task state in the wrong place.** Do you have a section in your project instructions that reads like "we are currently fixing X" or "do not touch Y until Z is resolved"? That is task state. It should be in a task file with a completion condition attached, not in your durable rules.

**3. Check whether you have anything in Layer 3 at all.** If your project has no mechanism for retrieving past decisions or debugging notes, you are probably re-explaining the same context repeatedly. This is not a tool prescription—a single `decisions.md` file with dated entries is better than nothing.

**4. Ask what you would lose if your project instructions file were deleted and rewritten from scratch today.** Anything you would genuinely miss is a candidate for Layer 1. Anything you would not miss was probably Layer 4 that never got discarded.

This audit does not require any new tooling. It is a judgment exercise: look at what you have written down for agents to read, decide which retention policy actually applies to each piece, and move it accordingly.

---

## References

- Anthropic. *Claude Code: Memory*. Claude Code documentation. [https://code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)
- OpenAI. *AGENTS.md*. Codex developer documentation. [https://developers.openai.com/codex/guides/agents-md/](https://developers.openai.com/codex/guides/agents-md/)
- Beads. Dependency-aware graph issue tracker and persistent memory for coding agents. [https://github.com/gastownhall/beads](https://github.com/gastownhall/beads)
- deja-vu. Local index and retrieval for coding-agent session histories. [https://github.com/vshulcz/deja-vu](https://github.com/vshulcz/deja-vu)

*The four-layer taxonomy in this article is the author's proposed model. It is not an official taxonomy from Anthropic, OpenAI, Beads, or deja-vu.*
