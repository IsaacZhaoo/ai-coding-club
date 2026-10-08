---
title: "Don’t Send Haiku 5.5 a Whole Migration Project"
slug: haiku-55-bounded-subtasks
description: "Use Claude Haiku 5.5 for bounded coding subtasks with verifiable outputs, and compare prompt-length pricing with the cost of completing a task."
authors: [isaac]
tags: [ai, tools, perspective]
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline={"Don’t Send Haiku 5.5 a Whole Migration Project"}
  description={"Use Claude Haiku 5.5 for bounded coding subtasks with verifiable outputs, and compare prompt-length pricing with the cost of completing a task."}
  datePublished="2026-10-08"
  dateModified="2026-10-08"
  authorName="Isaac Zhao"
/>

There’s a new model that costs about as much as your morning coffee per million tokens. Anthropic just released Claude Haiku 5.5 on October 7, 2026, and the pricing is genuinely game-changing for high-volume work: summaries, compaction, database queries, classification, and yes—narrow coding subtasks. But if you’re using this to rethink how you assign work across your agent team, here’s the real insight: cheaper tokens don’t mean you should give Haiku 5.5 everything. They mean you can afford to ask it for *many more tiny requests*.

Think about how you want models to fit into your workflow; what tends to change is very specific: Haiku 5.5 is now cheap enough that you can literally call it back-to-back for micro-tasks without it hurting your budget. But a vague subtask will still produce output you end up rewriting yourself—which is the same trap many fall into with earlier models. The difference here is not that Haiku 5.5 magically understands better; it’s that the price now lets you run many small calls instead of just one big one, and you’re better off doing that only when your subtask is well-bounded.

Let’s make this concrete with something we could run today.

<!--truncate-->

## A potential task: “Add a cache layer to our config loader”

Suppose you’re updating an existing config-loading library in TypeScript. You need to:

1. Read the current module structure.
2. Add an in-memory cache that reuses results for identical environment strings.
3. Ensure the cache invalidates when certain config flags change.

You have three models in your mental stack:

- **Opus 5.5**: Complex architecture, cross-file design decisions.
- **Sonnet 5.5**: Heavy lifting across a moderate codebase.
- **Haiku 5.5**: Narrow tasks you can verify quickly and cheaply.

If you ask Opus 5.5 to “add caching to the config loader,” it will draft how the interfaces change, where files live, and how edge cases like concurrent reads fit in. That’s valuable, but it’s also a lot of responsibility for one prompt.

Then comes the moment where Haiku 5.5 becomes interesting. Instead of one huge “do everything” prompt, you might break it into:

- “Here is the current config loader function. Generate a cache wrapper that accepts environment strings and returns memoized results.”
- “Now write a single unit test that validates cache invalidation when `CACHE_FORCE_RELOAD` is set to true.”
- “Summarize this diff in one paragraph for my changelog.”

Each of those is narrow, self-contained, and easy to verify. And each costs pennies, depending on your actual token usage.

## Why narrow matters more than speed or price

The public positioning from Anthropic is clear: Opus 5.5 and Sonnet 5.5 are better suited for complex agentic coding tasks; Haiku 5.5 fits narrower tasks like compaction, summarization, and subagent work. That’s not a marketing abstraction—it maps directly to how you should assign responsibilities.

Here’s the pattern that works:

- Delegate when:
  - The task is bounded by clear inputs and outputs.
  - You can check correctness mechanically or quickly via tests.
  - The scope doesn’t depend on understanding your full system.

- Keep to yourself (or give to a larger model) when:
  - You’re making architecture decisions that span multiple modules.
  - Requirements are fuzzy, and you need strong reasoning or negotiation across constraints.
  - A wrong choice breaks downstream systems in subtle ways.

You might see teams accidentally move their entire workflow onto Haiku because of the price. This can lead to:

- Too many calls to keep “alive” a partial understanding of the codebase.
- Responses that are superficially correct but structurally off.
- A lot of time spent reworking outputs instead of shipping.

The problem isn’t Haiku 5.5’s intelligence; it’s the assumption that price alone justifies handing over responsibility. You still need to decide which work you can describe narrowly and verify cheaply. The model doesn’t change that requirement.

## What a good “Haiku subtask” actually returns

In practice, when I delegate a small piece to Haiku 5.5, I expect something concrete:

- A single coherent function or data structure with no dangling references.
- One test case or one verification script, not a vague “I added tests.”
- A short diff summary you can paste into a PR description if needed.

And when it returns that, I still run two quick checks:

1. **Sanity check**: Does this compile/type-check without context?
2. **Integration check**: Do I need to edit 3 other files to make this work, or is it ready-to-merge?

If the second check fails, the task wasn’t narrow enough, and it’s not Haiku’s fault—it’s a boundary problem.

## The economics: why this actually changes allocation

Let’s be precise about the numbers. Anthropic’s pricing for prompts up to 100K tokens (and higher tiers) is:

- **Input:** $0.10 per 1M tokens (&lt;=100k) vs $0.50 per 1M tokens (>100k)
- **Output:** $0.50 per 1M tokens (&lt;=100k) vs $2.50 per 1M tokens (>100k)
- **Cache reads:** $0.01 per 1M tokens (&lt;=100k) vs $0.05 per 1M tokens (>100k)

Compare this to Haiku 4.5: input $1, output $5, cache read $0.10 per 1M tokens. For Sonnet 5.5, cache reads are now $0.10 instead of $0.20 per 1M tokens; Opus 5.5 remains $0.20 for cache reads. Source: https://www.anthropic.com/claude-haiku-5-5

That’s a massive gap when you’re running hundreds of short prompts per day. But the catch is that tokenization and actual usage differ across models, so per-token savings don’t automatically translate to equal dollar savings for identical tasks. Still, the effect is real: if Haiku 5.5 can do something Sonnet 5.5 could also do at a fraction of the cost, you’re incentivized to use it more often—for the right things.

And here’s where the “adjustable effort” feature becomes interesting. You can now choose a tradeoff between compute and intelligence, not merely tweak prompts. It’s about capability within the model versus workflow structure. One-shot vs multi-turn or context size are your design choices; Haiku 5.5 simply lets you tune cost/compute/quality within that flow. For example:

- Generate a snippet once (“produce this function”).
- Refine iteratively over multiple turns (“review and suggest improvements only where needed”).
- Use lighter context windows when boundaries are already known.

That flexibility lets you design micro-flows cheap enough to be “fire-and-forget.” You can, for example:

- Offload database query generation and validation.
- Let it summarize large logs into structured snippets.
- Use it to draft boilerplate tests you then lightly adjust.

But none of this justifies moving a whole migration or a complex refactoring entirely to Haiku 5.5 without a strong reason. Even if you’re on a generous API credit plan, the opportunity cost of architectural mistakes is far higher than token savings.

## So what should I try first?

If you’re reading this and thinking, “I need to decide which subtask to shift,” here’s a proposed experiment:

Take a task you normally send to Sonnet 5.5 or Opus 5.5 that is already well-scoped. Examples:

- Summarizing a large diff into bullet points for a PR.
- Extracting and formatting all environment variable usages from one module.
- Turning a long list of requirements into a single validation schema.

Keep the acceptance requirement exactly the same. For instance, “Output must be a valid JSON schema I can drop into `zod`” or “Output must fit in a one-paragraph changelog.” Then run Haiku 5.5 with that exact same prompt ten times over a week and measure:

- How many outputs meet the requirement without revision?
- How much time you spend fixing or reworking the output?
- Your actual token cost compared to using a larger model once.

If you find yourself with >70% acceptable outputs and zero architecture decisions made, you’re in the sweet spot. That’s what Haiku 5.5 is for: repeatable, checkable micro-tasks.

## The practical takeaway

Cheaper tokens are an opportunity to change task allocation, not a reason to move a whole complex migration to the smallest model. Your job as a developer and architect is still to decide which work you can describe narrowly and verify cheaply. Haiku 5.5 just makes it safe to try many more of those narrow slices.

Use it for:

- Bounded code snippets and utilities.
- Summaries, diffs, and compaction of known content.
- Fast, repeatable checks where wrong answers are easy to spot.

Keep your larger models for:

- Cross-file architecture and design trade-offs.
- Tasks where requirements are fluid and need strong reasoning.
- Anything where a single mistake cascades across modules.

The new prices mean you can afford to be granular, but being granular only helps if each subtask is well-defined and verifiable. Use Haiku 5.5 as your swarm of tiny specialists, not as the general contractor for your entire system.