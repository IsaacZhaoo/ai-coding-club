---
title: "After the Terminal Goes Green: Hidden Costs in Sequential Agent Tasks"
slug: slopcodebench-coding-agent-maintainability
description: "SlopCodeBench tests Coding Agents across sequential requirements. A green test shows today's behavior, not whether the code can support tomorrow's change."
authors: [isaac]
tags: [perspective, future-of-coding]
keywords:
  - SlopCodeBench
  - coding agent maintainability
  - iterative coding benchmark
  - AI generated code quality
  - coding agent benchmark
  - code erosion
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline="After the Terminal Goes Green: Hidden Costs in Sequential Agent Tasks"
  description="SlopCodeBench tests Coding Agents across sequential requirements. A green test shows today's behavior, not whether the code can support tomorrow's change."
  datePublished="2026-07-28"
  dateModified="2026-07-28"
  authorName="Isaac Zhao"
/>

# After the Terminal Goes Green: Hidden Costs in Sequential Agent Tasks

When I saw the Hacker News post titled *Benchmarking Opus 5 on SlopCodeBench*, the number that caught my eye was `4/17`. My first instinct was the usual one: scan the score, file the model somewhere in my mental ranking, move on. Four passes out of seventeen checkpoints. Not great. Not catastrophic. Just another data point on the leaderboard treadmill.

Then I made the mistake of opening the paper.

<!--truncate-->

---

Gabriel Orlanski and the SlopCodeBench team describe 36 problems containing 196 sequential checkpoints, published in arXiv v2 revised May 7, 2026. The surface looks like a typical coding benchmark until you notice the architecture underneath. Each problem starts from an empty workspace. At later checkpoints, the Agent receives the new specification and the workspace it built for the previous checkpoints. The prior conversation is not carried forward. The Agent meets its own earlier decisions cold, with only its own code as context, and a new requirement on top.

That detail changed what I was reading. The score isn't just a count of problems solved — it's a record of how well an Agent's code survived its own future.

The specifications describe observable CLI or API behavior. They don't prescribe internal architecture. The Agent decides how to structure the code. What it builds becomes the foundation the next checkpoint must extend. Tests from earlier checkpoints return as regression tests at later checkpoints, so the Agent can't quietly break the past to satisfy the present. And under the paper's setup, across 15 Coding Agents evaluated across six providers, not a single agent completed any of the 36 problems with every checkpoint passing end to end.

That is what `4/17` actually means when you hold the full context. Not a ranking. A record of how far the code held together before it didn't.

---

There's a feeling I recognize from working with Coding Agents on real repositories. The terminal goes green. The declared behavior matches the test. Everything looks resolved. It's easy to close the loop there, because the test itself certifies that the requirement was met. What it can't certify is the shape of the code left behind — whether it bent to accommodate this one task in a way that will cost the next task more.

The SlopCodeBench paper makes that cost measurable, with caveats I'll get to. Across its evaluated trajectories, the researchers report structural erosion increasing in 77% of cases and verbosity increasing in 75.5%. Structural erosion, as the paper defines it, means complexity concentrating in high-complexity functions — the code grows heavier in the places that are already hardest to change. Verbosity combines selected AST-pattern flags with structural duplication.

These are two deterministic signals. The paper is careful about this, and so should the reader be. They don't constitute a complete theory of maintainability, and they don't prove that Agent-written code is unworkable. What they do is give you a specific, trackable pattern to watch across a sequential task structure that most benchmarks don't test at all.

The comparison the paper draws is precise: Agent checkpoints measured at 2.3× the verbosity metric and 2.0× the erosion metric against a panel of 473 Python repositories. The methodology boundary matters here. This is not a claim that Agents produce code twice as bad as human engineers. It's a report of where two selected signals landed for this evaluation's sample, against this reference panel, in this benchmark's Python track. That specificity is the thing worth carrying away — not the multiplier stripped of its context.

---

The HumanLayer post that surfaced on Hacker News ran a subset: three problems from SlopCodeBench, totaling 17 checkpoints across `circuit_eval`, `database_migration`, and `dynamic_config_service_api`. They used the Claude Code Harness with fresh context per checkpoint and tested Opus 4.8, Sonnet 5, and Opus 5. Opus 5 passed 4 of the 17 strictly. The other two models each passed 1.

I find this run more interesting as a window into the benchmark's design than as a ranking of the three models. A run of three problems, with one team's harness and prompts, on one day, is not enough to say much about any model's general capability. What it does do is show the benchmark working as advertised: checkpoints accumulating, regressions returning, the inherited workspace becoming either an asset or a liability as the requirements continue arriving.

The SlopCodeBench team calls their project an open, community-driven evaluation primitive rather than a finalized benchmark. That framing feels honest. The living site has expanded since the paper. Different runs will produce different numbers. What remains stable is the structural insight: put a Coding Agent in a room with its own earlier decisions, hand it a new requirement, and see what it does with what it left itself.

---

Most of the benchmarks I've seen ask whether the Agent can build the thing. SlopCodeBench adds a question I've been waiting for someone to ask formally: can the Agent build things sequentially, such that the next thing isn't fighting the last thing?

Green tests are not nothing. They mean what they say — the declared behavior was met at that moment. But a test describes a contract with the current requirement. It says very little about the architecture the next requirement must inherit. That architecture is what the Agent actually leaves in the room when the terminal goes quiet.

The number I came away from this thinking about isn't 4. It's 196 — the total checkpoints across 36 problems where evolving workspaces are evaluated. A score per checkpoint is a measure of whether the Agent solved today's problem. Whether the code enables solving tomorrow's is a different question, and it's the one that determines whether Coding Agents are useful for repositories that keep changing, which is every repository I've worked with.

That's the question I'll be thinking about the next time a terminal goes green.

---

**Sources**

- Gabriel Orlanski et al., *SlopCodeBench: Benchmarking How Coding Agents Degrade Over Long-Horizon Iterative Tasks* (arXiv v2, 2026): [https://arxiv.org/abs/2603.24755](https://arxiv.org/abs/2603.24755)
- Official SlopCodeBench site: [https://www.scbench.ai/](https://www.scbench.ai/)
- Official runner: [https://github.com/SprocketLab/slop-code-bench](https://github.com/SprocketLab/slop-code-bench)
- HumanLayer, *Benchmarking Opus 5 on SlopCodeBench*: [https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/benchmarking-opus-5-on-slop-code-bench.md](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/benchmarking-opus-5-on-slop-code-bench.md)


---

## Related Reading

- [Coding Agent Benchmark Guide: How to Compare Agents on Your Own Repository](/docs/tutorials/coding-agent-benchmark-guide/)
- [Eval-Driven Development for Coding Agents: One Passing Test Is Not Enough](/blog/eval-driven-development-for-coding-agents/)
- [Coding Agent Evals Guide: Turn Traces into Datasets and Quality Gates](/docs/tutorials/coding-agent-evals-guide/)
