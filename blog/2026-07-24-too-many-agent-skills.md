---
title: "When More Agent Skills Make a Coding Agent Worse"
slug: too-many-agent-skills
description: "A larger Agent Skills catalog can create trigger ambiguity and context cost. Learn why a Skill loadout needs routing evidence, not collection counts."
authors: [isaac]
tags: [perspective, future-of-coding]
keywords:
  - agent skills
  - too many agent skills
  - agent skills testing
  - skill trigger precision
  - coding agent context cost
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline="When More Agent Skills Make a Coding Agent Worse"
  description="A larger Agent Skills catalog can create trigger ambiguity and context cost. Learn why a Skill loadout needs routing evidence, not collection counts."
  datePublished="2026-07-24"
  dateModified="2026-07-24"
  authorName="Isaac Zhao"
/>

# When More Agent Skills Make a Coding Agent Worse

Something happened on Juejin on July 23 that is worth paying attention to, not because any single post broke new ground, but because of what the posts, taken together, reveal about where the conversation has moved.

A Juejin hot list checked on July 23 included a Top 10 Skills roundup, a guide to designing better Skills, and a piece asking, plainly, why installing more Skills can make an AI feel slower and less reliable. On Hacker News in the same window, projects surfaced for diagnosing loadout health, gating Skill changes with real usage evidence, and mapping which installed capabilities rarely fire. I am not citing these as verified market signals. Autocomplete suggestions and hot-list rankings show *intent*, not volume. But the intent itself is the signal: developers are no longer asking mainly "where can I get more Skills?" They are asking which Skills actually trigger, which ones collide, which ones sit unused, and whether any of them are worth their context cost.

That shift is worth understanding from first principles.

<!--truncate-->

---

## A Skill catalog is a routing surface

The [Agent Skills specification](https://agentskills.io/specification) defines a Skill as a directory containing a `SKILL.md` file. The required metadata is a `name` and a `description`. The description should explain what the Skill does *and* when to use it. Under progressive disclosure, the Agent sees catalog metadata first, loads the full `SKILL.md` only after activation, and pulls supporting resources only as needed.

This design is sensible. Loading every instruction at once would be wasteful. But it also means the `name` and `description` are not decorative labels; they are the entire routing mechanism at the point of selection. Before the Agent reads a single line of actual instructions, it must distinguish one description from every other description in your catalog and decide whether this prompt belongs here.

Think of it as a crowded control panel where every button is labeled in natural language. If you have four buttons and they cover clearly different territory, the Agent finds the right one without friction. If you have forty buttons and several of them describe overlapping territory in slightly different words, the routing problem becomes harder—not because the underlying model has become less intelligent, but because there are more labels to disambiguate.

---

## Installed capability is not the same as reliable capability

This is the distinction that most Skills-as-features thinking misses.

A Skill that never fires is not "more capability." It is overhead: catalog metadata loaded at agent startup, context it does not use, and a description you are presumably maintaining. A Skill that fires on a near miss—activating for a prompt that resembles its description but does not actually need its instructions—is not "more capability" either. It is a routing error that may suppress the correct Skill, add irrelevant instructions to the active context, or simply confuse the completion.

The [optimizing-descriptions guide](https://agentskills.io/skill-creation/optimizing-descriptions) says this directly: an under-specified description can fail to trigger when it should, while an over-broad description can trigger when it should not. The guidance recommends realistic positive prompts *and* near-miss negative prompts, repeated runs, and separation between training and validation sets. This is not optional polish for perfectionist developers. It is the acknowledgment that trigger failure is a routine engineering failure mode, not an edge case.

A compact way to see the difference:

| State | What it means |
|---|---|
| **Fires correctly** | Reliable capability |
| **Never fires** | Installed overhead |
| **Fires on near miss** | Routing error, possible context pollution |
| **Competes with a sibling description** | Ambiguous routing, degraded confidence |

Catalog size determines how crowded the panel is. Description quality determines how legibly each button is labeled. You need both dimensions; count alone is not a proxy for either.

---

## Why adding Skills can make things feel worse

If you have hit a point where your Coding Agent feels slower to reach the right behavior, or where it seems to activate instructions that don't quite fit, three inspectable culprits are:

**Trigger ambiguity.** Two or more descriptions that overlap enough for the Agent to hesitate or choose incorrectly. This does not announce itself loudly. You get subtly wrong activations that are hard to attribute without deliberate testing.

**Accumulated context cost.** Even with progressive disclosure, catalog metadata accumulates as your loadout grows. Context is not free, and the cost is not just tokens—it is attention the model is distributing across more material before generating a word of useful output. The gap between a local context estimate and what your provider actually accounts for can make this hard to see clearly until you measure it.

**Maintenance debt on descriptions.** A description you wrote six months ago for a Skill you rarely use may have drifted from the current task landscape. It is now either under-specified, mis-specified, or competing with a newer Skill you added without auditing the overlap.

None of this means Skills are the wrong mechanism. It means that the mechanism requires the same engineering discipline you would apply to any other routing system: specification, testing, evidence, and periodic review.

---

## The ecosystem is moving toward diagnosis

The projects that surfaced in that window are evidence of an ecosystem response to exactly this problem. `drskill` approaches loadout health through overlap detection. `Ingot` requires held-out evidence and human promotion before optimizer-generated challengers replace live instructions. `Agent Atlas` reads local session histories to map installed capabilities and count what actually fires. I am describing their published intent, not benchmarking them; every project-specific observation belongs to that project's own context.

What they share is a diagnostic orientation. They treat the installed catalog as a system to be measured, not a collection to be grown. That orientation is the right one.

The [Anthropic Skills repository](https://github.com/anthropics/skills) is explicit about this: test Skills thoroughly in your own environment. That is not a disclaimer; it is a statement that a Skill's behavior is a function of its description *in your context*, not just its instructions in isolation. A Skill that works well in a minimal loadout may trigger ambiguously once you have added ten neighbors with overlapping scopes.

The [evaluating skill output quality guide](https://agentskills.io/skill-creation/evaluating-skills) addresses the other half: once a Skill fires correctly, does it produce outputs worth the invocation? Both failure modes—not firing and firing incorrectly—are first-class concerns.

---

## The useful question is not count

I have watched Skills acquisition turn into a collection contest in more than one team I know, and I find it genuinely uncomfortable, not because Skills are bad but because count is such a poor proxy for what actually matters.

The useful question is: does this catalog route real work to the right instructions at an acceptable cost?

That question has three parts. *Real work* means prompts that actually occur in your development practice, not prompts you constructed to make the Skill demo correctly. *Right instructions* means the correct Skill fires with high reliability and near-miss prompts are handled cleanly. *Acceptable cost* means you have some idea of what the catalog contributes to context on a typical invocation, and you have decided that it is worth it.

A smaller loadout that you can explain, test, and defend prompt-by-prompt is more valuable than a larger one you cannot. This is not a philosophical preference; it is what makes a Skill catalog useful rather than decorative.

If you are not sure whether your current loadout meets that standard, the first step is not to remove Skills arbitrarily. It is to measure. What fires? What does not? Where do descriptions overlap? Which activations do you actually want?

---

## Where this goes next

If you are new to how Skills relate to Hooks and MCP, start with the [existing guide on those boundaries](/docs/tutorials/claude-code-skills-hooks-mcp/) before continuing here—the distinctions matter and the comparison is already written.

The [next page in this sequence](/docs/tutorials/agent-skills-testing-guide/) is a practical audit Tutorial. It will walk through specification health checks, catalog size decisions, description overlap analysis, positive and near-miss prompt testing, and reading real activation records. The goal is to give you a concrete procedure for answering the routing question with evidence rather than intuition.

The short version of everything above: install what you can explain and test. Audit what you have before adding more. Treat trigger failures as engineering problems with known mitigations, not as signs that Skills don't work. The mechanism is sound; the discipline around it is what makes the difference.

---

## Primary Sources

- [Agent Skills specification](https://agentskills.io/specification)
- [Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions)
- [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills)
- [Anthropic Skills repository](https://github.com/anthropics/skills)
- [drskill](https://github.com/dbreunig/drskill)
- [Ingot](https://github.com/SlanchaAI/ingot)
- [Agent Atlas](https://github.com/Pycomet/agent-atlas)
