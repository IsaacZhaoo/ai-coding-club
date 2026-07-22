---
title: "Coding Agent Harness Explained: Model, Context, Tools, Sandbox, Memory, and Orchestration"
description: "Understand how a coding agent harness controls repository context, tools, orchestration, sandbox boundaries, memory, verification, and agent selection."
keywords:
  - coding agent harness
  - AI coding agent architecture
  - coding agent benchmark
  - agent harness engineering
  - coding agent comparison
sidebar_position: 16
tags: [tutorial, coding-assistant, agent-engineering, architecture]
---

# Coding Agent Harness Explained: Model, Context, Tools, Sandbox, Memory, and Orchestration

---

When [Grok Build's repository](/blog/grok-build-open-source/) went public, the first wave of takes treated it like a model drop. People skimmed the announcement, saw "open source," and assumed they were getting weights to poke at. That's not what was in the repo. What actually shipped was the Rust source for a CLI and TUI, an agent runtime, and a documented set of surrounding layers: tools, workspace integration, checkpoints, MCP support, skills, hooks, a headless mode, and sandbox-related plumbing. No model weights. The thing you could actually read and run was the *harness* — everything that sits between a language model and a working repository.

That misunderstanding is worth pausing on, because it's the same misunderstanding that shows up constantly in how people evaluate coding agents. You'll see someone say "I switched from Agent A to Agent B and it's so much better at finding the right file" or "it kept forgetting what we agreed on three turns ago," and the conversation drifts toward which model is "smarter." Often the model didn't change at all. What changed was retrieval, tool wiring, permission scope, or what got persisted between turns.

The day after the Grok Build release, JetBrains announced a repository-intelligence layer they're calling [JetBrains Context](https://blog.jetbrains.com/ai/2026/07/introducing-jetbrains-context-repository-intelligence-for-coding-agents/), explicitly pitched as infrastructure for coding agents rather than a model or an IDE feature in the traditional sense. Around the same window, search suggestions included agent benchmarks, leaderboards, and "harness" as a term of art — people comparing tools weren't asking "which model," they were asking "which setup." That's the right question. This piece is about how to ask it well.

A coding agent is not just a model in a terminal: the harness decides what the model can see, which tools it can use, how it acts and recovers, what persists, what it may touch, and how the result is verified — so agents should be compared at the system level, not by model name alone.

## Getting the vocabulary straight

These five words get used almost interchangeably in casual conversation, and that's where confusion starts.

**Model.** The trained network that turns a prompt into a completion — the thing with a name and a version number. [Anthropic's own framing of agentic systems](https://www.anthropic.com/research/building-effective-agents) is useful here: they describe the basic building block as an LLM augmented with retrieval, tools, and memory. The model is the "LLM" part of that sentence. Everything else is augmentation.

**Coding agent.** A model wired into a loop where it can read code, decide on an action, execute a tool, observe the result, and decide again. Anthropic draws a specific line between *workflows*, which follow predefined code paths, and *agents*, which dynamically direct their own process and tool usage. A script that always runs "lint, then test, then format" is a workflow. A system that decides for itself whether to run the linter again after seeing an error is acting like an agent.

**Harness.** The runtime and surrounding infrastructure that makes the agent loop possible in a specific product: how the repo is indexed, which tools are exposed and how they're sandboxed, what gets approved automatically versus flagged for a human, what state survives across sessions, and how the whole thing checks its own work. There is no single formal definition of "harness" that the industry has converged on — different teams draw the boundary differently, and this article doesn't claim otherwise. But practically, when people say "the harness matters more than the model," they mean this bundle of infrastructure decisions.

**Framework.** A reusable toolkit for building agent loops and harnesses — the kind of thing a team assembles a product on top of, rather than a finished product itself.

**Benchmark.** A fixed task set with a scoring method, used to compare systems on a defined slice of behavior. SWE-bench is a common reference point here: it evaluates systems on real repository issues by asking them to generate a patch, and it ships a Docker-based evaluation harness specifically so that results can be reproduced rather than taken on faith. Worth noting: SWE-bench itself needed a harness to be a fair benchmark. That's a good early signal that the harness is not a footnote — it's structural.

| Term | What it actually is | What it is not |
|---|---|---|
| Model | The trained network producing completions | The whole product experience |
| Coding agent | Model + tool loop + decision-making over actions | A fixed script of steps |
| Harness | Runtime, tools, sandboxing, memory, verification around the agent | A synonym for "the model's settings" |
| Framework | Reusable scaffolding for building agent loops | A finished, deployable product |
| Benchmark | A fixed task set with a scoring method | A guarantee of real-world performance |

## Six layers of a harness

Strip any coding agent product down and you'll find some version of these six layers. They're not always cleanly separated in a given product's architecture, but they're separable enough to reason about independently, and each one fails in a distinct, recognizable way.

### 1. Repository context and retrieval

Before the model can act, something has to decide what part of the repository it gets to see. That might be a full-text search over the working tree, an embedding index, a call graph, a language server integration, or some hybrid. This is the layer JetBrains Context is aimed at — treat any specific improvement numbers from that announcement as a vendor claim until someone outside JetBrains reproduces them, but the category of problem is real and worth naming on its own: retrieval quality is a distinct axis from model quality.

**Failure mode when weak:** the model writes plausible-looking code against a function signature that changed two refactors ago, because retrieval handed it a stale or irrelevant snippet instead of the current file. Or it "can't find" a helper that clearly exists in the repo, because the indexing missed it or the search query the model generated didn't match how the code is actually named.

### 2. Tools, editing, and command execution

This is the action surface: file read/write, shell execution, test runners, search, sometimes browser or API access. The interface matters as much as the coverage — a tool that returns raw diff noise is worse than one that returns a clean, reviewable patch; a shell tool with no output truncation will blow the model's context on a verbose build log.

**Failure mode when weak:** the agent can technically edit files but the diff it produces is a wall of unrelated whitespace changes, or it can run tests but the harness doesn't surface the failure output cleanly, so the model "fixes" the wrong thing based on a truncated error message.

### 3. Agent loop, planning, orchestration, and recovery

This is the decision-making core: how the system breaks a task into steps, when it re-plans, how it decides an action failed and needs a different approach, and whether it can hand off to a sub-task or another agent instance for scoped work. Recovery behavior is the part people notice most viscerally — does the agent double down on a broken approach, or does it recognize the failure and pivot?

**Failure mode when weak:** the agent hits an error, tweaks one parameter, hits the same error, tweaks another parameter, hits the same error again — the incremental-patch loop instead of a root-cause diagnosis. This is a harness-level failure as much as a model-level one: a harness that doesn't feed the model clear enough signal about *why* something failed, or that has no mechanism to say "you've tried this twice, stop and reconsider," will produce this behavior regardless of which model is underneath.

### 4. Permissions, approvals, sandboxing, and host trust

What can the agent touch without asking, what requires a human nod, and what's walled off entirely? Anthropic's guidance on this is blunt: test agents extensively in sandboxed environments with appropriate guardrails before trusting them with real systems. That's not a nice-to-have, it's the mechanism that makes an agent's mistakes cheap instead of expensive.

**Failure mode when weak:** an agent with full, unscoped shell access runs a command that has a side effect nobody reviewed — not because the model was reckless, but because the harness never asked it to check, or never gave a human the chance to see the command before it ran.

### 5. Session state, durable memory, and project instructions

What survives between messages, and what survives between sessions entirely? A running session has short-term context. Some harnesses layer durable memory on top — project instruction files, saved preferences, prior decisions — so the agent doesn't relearn the same constraints every time you open it. This is a distinct concern from context *retrieval* (layer 1): retrieval finds code, memory persists decisions and constraints.

**Failure mode when weak:** you tell the agent on Monday that the team doesn't use a particular library, and by Thursday it's suggesting that library again, because nothing about that instruction persisted anywhere durable. Or the opposite failure: stale project instructions from six months ago keep steering the agent toward a pattern the team has since abandoned, because nobody's pruning what's supposed to be durable.

### 6. Tests, evaluators, traces, checkpoints, and human review

The verification layer: does anything confirm the agent's output is actually correct before it's treated as done? This ranges from "the agent ran the test suite and it passed" to full trace logging that lets a human replay what happened, to checkpointing that lets you roll back to a known-good state if a multi-step task goes sideways.

**Failure mode when weak:** the agent reports success, the diff looks reasonable on a skim, and it ships — but nothing actually ran the tests, or the tests that ran didn't cover the changed path. The gap only surfaces later, and by then there's no trace to reconstruct what the agent actually did versus what it claimed.

| Layer | Core question | Weak-layer symptom |
|---|---|---|
| Context & retrieval | What can the model see? | Edits against stale or missing code |
| Tools & execution | What can it do, and how cleanly? | Noisy diffs, truncated feedback |
| Loop & recovery | How does it plan and recover? | Repeated failed patches, no pivot |
| Permissions & sandbox | What can it touch unsupervised? | Unreviewed side effects |
| State & memory | What persists across time? | Repeated mistakes or stale rules |
| Verification & review | How is output checked? | False confidence, no audit trail |

## The same model, a different feel

Here's a scene that's become routine for anyone testing more than one agent product: you point two different terminal agents at the same repository, same task, same underlying model family even. One of them finds the relevant config file in the first search and starts editing within a minute. The other spends several turns grepping in the wrong directory, because its retrieval layer indexes differently or its default search tool doesn't weight recently-modified files. One of them, hitting a failing test, reads the stack trace and changes the actual broken assumption. The other tweaks a type annotation, reruns, gets the same failure, tweaks a different annotation, reruns again — recognizable incremental patching, not because the model got dumber, but because the harness isn't feeding it a clean enough failure signal or isn't nudging it to step back.

None of that is a controlled comparison, and it shouldn't be reported as one — there's no shared benchmark score behind that description, and the point isn't that one tool is universally better. The point is narrower and more useful: the felt difference between two agent products using comparable models is frequently explained by harness layers 1, 3, and 6 — retrieval, recovery behavior, and verification — rather than by anything about the model itself. If you're evaluating tools by asking "which model is this running," you're asking a question that often doesn't predict the experience you're going to have.

## A repository-level selection checklist

Public leaderboards tell you how a system does on a fixed task set. They don't tell you how it'll behave on *your* repository, with *your* build tooling, *your* review culture, and *your* risk tolerance. Before adopting a coding agent product for real work, it's worth walking through these questions against your own codebase rather than against a benchmark's:

- **Context quality** — Does it find the actually-relevant files in a codebase with your real structure (monorepo, unusual naming conventions, generated code), not just in a clean sample repo?
- **Diff quality** — Are the changes it proposes scoped and reviewable, or do they sprawl into unrelated formatting and drive-by "improvements"?
- **Test feedback** — Does it run your actual test suite and act on real failure output, or does it declare success without running anything?
- **Recoverability** — When it's wrong, can you tell what it did and undo it cleanly? Checkpoints, clear diffs, and readable traces matter more here than raw capability.
- **Permission boundary** — Can you scope what it can touch without asking, and does it actually respect that scope, including for shell commands?
- **Reviewability** — Can a human on your team review its output in a normal PR flow, or does it produce changes that are hard to review because of noise or scale?
- **Cost visibility** — Do you have a clear sense of what a session costs before you commit to a long agentic run, especially for larger or looping tasks?
- **Portability** — If you switch tools next year, do your project instructions, memory, and configuration travel with you, or are they locked into one product's format?
- **Maintenance burden** — Does keeping it working require ongoing config upkeep, prompt tuning, or babysitting, or does it stay useful with minimal care?

None of these questions have a universal right answer. A solo developer on a small repo has different tolerance for permission friction than a team working in a regulated codebase. The point of the checklist is to make the comparison concrete and repository-specific instead of vibes-based.

## Why leaderboards aren't enough

Benchmarks like SWE-bench earn their usefulness by being reproducible — the Docker-based harness exists specifically so results can be checked, not just claimed. That reproducibility is valuable and rare in this space. But a benchmark score is still a score on someone else's repository issues, evaluated by someone else's harness, under someone else's task selection. It tells you the system can solve *those* problems under *those* conditions. It doesn't tell you how the retrieval layer handles your codebase's particular sprawl, whether the permission model fits your team's risk appetite, or whether the verification step would actually catch the kind of regression you're most worried about.

Public leaderboards are a reasonable first filter — they can rule out systems that clearly underperform on well-understood tasks. They are not a substitute for testing against your own repository, your own test suite, and your own review process. A follow-up guide will walk through building a small benchmark against your own codebase, so you can measure the layers that matter to you directly instead of inferring them from someone else's numbers.

## References

- Anthropic, ["Building Effective Agents"](https://www.anthropic.com/research/building-effective-agents) — framing of agentic systems as models augmented with retrieval, tools, and memory; the workflow-versus-agent distinction; guidance on sandboxed testing with guardrails.
- [SWE-bench project documentation](https://github.com/SWE-bench/SWE-bench) — task definition (generate a patch for a real repository issue) and the Docker-based evaluation harness for reproducible scoring.
- [Grok Build public repository](https://github.com/xai-org/grok-build) — CLI/TUI and agent runtime source, and documented tool, workspace, checkpoint, MCP, skill, hook, headless, and sandbox-related layers.
- JetBrains, [announcement of JetBrains Context](https://blog.jetbrains.com/ai/2026/07/introducing-jetbrains-context-repository-intelligence-for-coding-agents/) (2026-07-21) — repository-intelligence layer positioned for coding agents; treat specific performance claims as vendor-reported pending independent verification.

For the layers this piece deliberately didn't re-teach — [durable memory design](/docs/tutorials/coding-agent-memory/), [sandbox security postures](/docs/tutorials/coding-agent-sandbox-security/), [Skills/Hooks/MCP mechanics](/docs/tutorials/claude-code-skills-hooks-mcp/), [AGENTS.md conventions](/docs/tutorials/agents-md-guide/), and [AI-assisted code review](/docs/tutorials/ai-code-review-workflow/) — see the corresponding AI Coding Club guides. The natural next step from here is hands-on: building a small, repository-specific benchmark so you can evaluate these six layers against your own code instead of a public leaderboard. That's the subject of the next guide.
