---
title: "Don’t Hand Fable 5.2 Ownership When You Want Minimal Repairs"
sidebar_label: "Minimal repairs with Fable 5.2"
description: "Before a small Fable 5.2 repair, audit inherited ownership instructions and check the resulting diff against explicit acceptance criteria."
sidebar_position: 2
---

# Don’t Hand Fable 5.2 Ownership When You Want Minimal Repairs

If you’ve been using Claude Fable 5.2 or Claude Mythos 5.2 in your daily coding workflow, you probably noticed something unusual: Anthropic’s new guidance explicitly warns against telling the model “you own this code” when you only want a small, precise fix. It sounds counterintuitive—usually, giving a model authority leads to better results. But for minimal repairs, that authority is exactly what can quietly corrupt your scope.

Before you run Fable 5.2 on an existing task, take 10 seconds to audit whether any inherited rules or system prompts are secretly delegating project design and future direction to the model itself. If you find a sentence like “You decide this project’s design and future direction,” remove it from your fresh task configuration. Keep everything else that’s actually needed: permissions, behavior, and scope constraints.

Here’s why, with a concrete example and a checklist you can use today.

## The core issue: ownership vs. minimal change

In Anthropic’s small coding-task tests, simply stating who “owns” the code nudges the model toward incidental or structural edits it wouldn’t otherwise make—even when you explicitly restrict its scope to specific changes. Another guardrail limiting the model’s actions didn’t erase that ownership effect; both factors played a role. As Anthropic notes, if your user already owns the code and you need only minimal edits, it’s worth dropping the ownership phrasing from your prompt to keep changes focused [Say Who Owns the Code](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2#say-who-owns-the-code). This guidance supports a practical configuration choice—trimming unnecessary directives—rather than implying any one strategy universally outperforms all others.

This doesn’t mean the model can’t act confidently; it means you’re preventing the model from rethinking the architecture or introducing “nice-to-have” changes while it’s supposed to just fix one thing. In practice, the same guidance applies to system prompts and earlier instructions that carry over into a resumed conversation—especially if you’re not starting in a fresh session. Anthropic specifically advises applying system/tool/earlier-instruction changes in a NEW conversation, rather than patching them later into an ongoing API session.

## What exactly is “code ownership” in this context?

Let’s be clear: this isn’t about intellectual property or legal rights. In prompting terms, “code ownership” means you’re assigning the model a role as the project architect and long-term maintainer. That role naturally bleeds into:

- Renaming functions or classes for consistency
- Refactoring adjacent logic while fixing a bug
- Introducing new abstractions or dependencies
- Adding defensive checks or logging
- Adjusting error handling strategies

All of these are valuable in a greenfield project, but they’re scope creep in a targeted repair. When your goal is “fix the maximum-price filter so it includes items at the boundary,” ownership authority is the last thing you want active under the hood.

## A concrete example: the maximum-price filter

Let’s use a simple task that already exists in our existing acceptance-criteria tutorial, but frame it as a Fable 5.2 repair scenario.

**Goal:** Ensure a product priced exactly at the maximum is included; exclude only items above the maximum; preserve original relative order.

- Input: `[8, 10, 12]` with `max = 10`
- Expected output: `[8, 10]`

A clean request for Fable might look like this:

> “Fix the maximum-price filter to include items priced exactly at max. For [8,10,12] with max=10, the output should be [8,10]. Preserve original order. Limit changes to the necessary logic and add a regression test.”

Key behaviors the model must keep:
- Items below max: included (unchanged)
- Items at max: now included (this is the fix)
- Items above max: excluded (unchanged)
- Original relative order preserved

What you want to avoid in this repair:
- Renaming the filter function or surrounding utilities
- Extracting the filter into a separate abstraction class
- Adding logging or analytics hooks
- Changing unrelated validation rules

## A practical checklist before running Fable 5.2

Before you hit “run,” run through this quick audit of your task setup.

1. **Fresh conversation?**<br />
   - Start a new chat or API session for the repair. Don’t try to patch earlier instructions into an ongoing thread if you can avoid it.

2. **Scan for broad delegation.**<br />
   - Look at any system prompts, project rules, or inherited instructions.
   - If they say anything like:
     - “You decide this project’s design and future direction.”
     - “You are the long-term owner of this codebase.”
     - “Feel free to refactor for maintainability.”
   - Remove those sentences for this specific task.

3. **Narrow the request.**<br />
   - State the exact bug or edge case.
   - Specify the expected input/output behavior.
   - Explicitly ask for a regression test.

4. **Ask for a diff, not just tests.**<br />
   - Require Fable to return the actual changed lines so you can verify scope compliance.
   - A green test or short summary alone doesn’t prove it stayed minimal.

5. **Inspect after the run.**<br />
   - Did the model change only what was needed?
   - Are there any unrelated improvements hidden in the diff?
   - If there are useful design changes, evaluate them as a separate task instead of silently bundling them into the repair.

## When ownership authority IS the right choice

This guidance is task-specific, not a global deletion policy. There are absolutely cases where you want Fable 5.2 to act like an owner:

- Greenfield projects where you’re iterating on architecture.
- Legacy codebases needing deliberate refactoring.
- Performance or safety improvements that inherently reshape the design.

In those scenarios, your request should explicitly include broader authority and mention new abstractions, renaming, or additional dependencies as acceptable outcomes. The important part is that this decision is conscious and scoped to the task—not a default behavior you inherit from old rules.

## How to interpret Anthropic’s evidence

Anthropic’s findings are from controlled coding experiments, not a full-scale production study. The guidance is:

- Practical heuristic based on observed behavior patterns
- Tied specifically to Fable 5.2 and Mythos 5.2
- Not a guarantee that every small task will stay in scope

Think of it like this: the data showed that ownership phrasing consistently nudged models toward structural changes, even when the prompt only asked for a tiny fix. So Anthropic’s recommendation is simply to turn that nudge off when you don’t want it. That’s why the advice is about wording and configuration rather than about which model you use.

## Next steps for your workflow

1. **Audit your current Fable tasks** for any inherited “ownership” or broad architectural language.
2. **Create a standard repair prompt template** that:
   - Starts with a fresh conversation
   - States the precise behavior change
   - Explicitly omits ownership phrasing
   - Requests a minimal diff plus regression tests
3. **After each run**, verify both test outcomes and the actual diff, not just the final summary.

This is a small configuration choice that can save you from silent scope creep. When your goal is surgical, stop treating the model like a co-owner and start treating it like a precise tool.

---

**Useful reading:**<br />
- Anthropic’s [prompting guide for Fable 5.2](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2#say-who-owns-the-code)<br />
- AI Coding Club: [acceptance criteria for coding agents](/docs/tutorials/acceptance-criteria-for-coding-agents/)<br />
- AI Coding Club: [AI code review workflow](/docs/tutorials/ai-code-review-workflow/)
