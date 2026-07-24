---
title: "What Is Coding Agent Observability? Logs Aren't Enough"
slug: coding-agent-observability
description: "A real Codex turn completed after two failed tools. Learn why Coding Agent observability needs linked traces, explicit gaps, and tool-level evidence."
authors: [isaac]
tags: [perspective, future-of-coding]
keywords:
  - coding agent observability
  - agent observability
  - coding agent tracing
  - OpenTelemetry GenAI
  - Codex CLI observability
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline="What Is Coding Agent Observability? Logs Aren't Enough"
  description="A real Codex turn completed after two failed tools. Learn why Coding Agent observability needs linked traces, explicit gaps, and tool-level evidence."
  datePublished="2026-07-24"
  dateModified="2026-07-24"
  authorName="Isaac Zhao"
/>

# What Is Coding Agent Observability? Logs Aren't Enough

The diagnosis was correct. The turn completed. Codex CLI returned the smallest-fix explanation for a `ZeroDivisionError`, and the final status read `completed`. If I had stopped there — closed the terminal, pasted the answer, moved on — I would have called the run a success and never questioned what happened in between.

Then I read the event stream.

<!--truncate-->

---

## The Two Failures Inside a Green Result

That single read-only Codex CLI 0.145.0 run produced 17 events. Five of them were command executions. Two of those five failed. The first failure came when Codex called `python` to run the focused test: exit code `127`, the shell's command-not-found result in this ephemeral run environment. No `python`, only `python3`. The agent retried with `python3`. That invocation found the runtime, ran the test, and returned exit code `1` — the test failed, intentionally, exposing the `ZeroDivisionError` the diagnosis was supposed to explain. From there Codex read the source and produced the correct answer. The completed turn reported 201 reasoning output tokens, 749 output tokens, and 74,858 input tokens, of which 59,904 were cached.

Three out of five commands succeeded. Two failed. The final turn status was `completed`.

Both of those facts are true at the same time, and that is the whole problem.

If the event stream had retained only the final status and the answer text, I would have a correct output with no way to ask: did the agent path through a retry? Did it succeed on the first tool call or the third? Was the failure on `python` expected behavior or a gap in the environment? The successful output gives me none of that. The raw JSONL stream did include a thread id, event types, and item ids, but it did not include a parent-linked span hierarchy or an explicit machine-readable relation saying "this `python3` call retried that `python` exit-127."

A final green state looks sufficient until you notice the path that produced it.

---

## Why the Full Execution Story Disappears

The distinction I keep coming back to is causality, not verbosity. More log volume does not preserve causal structure on its own. In this run, two tool failures lived inside a successful agent turn. That is not a contradiction: the agent recovered and completed. But you can only inspect that recovery when the record connects events instead of leaving the relationship implicit.

OpenTelemetry's model for this is a trace: the complete path of one request through a system. Within that trace, each discrete unit of work is a span. Spans can carry a shared trace identifier and a parent identifier, so the structure is not flat. You can follow a failed tool operation to its parent operation and relate it to the work that followed. The hierarchy is encoded in the data, not reconstructed from timestamps by hand.

OpenTelemetry's GenAI agent semantic conventions — currently in Development status, not stable — extend this model with concepts for agent invocation, workflow invocation, planning, tool execution, and Token usage. The OpenAI Agents SDK, in its own tracing model, records generations, function tools, handoffs, guardrails, and custom events. That is evidence about that specific SDK, not a claim that every agent client does the same thing. But it demonstrates the direction: the community is trying to name the units of agent work the same way distributed systems named service calls.

A trace that names and relates its spans consistently is what lets you ask: "show me every run where a tool failed and the agent still completed." Without that correlation, the same question depends on client-specific event parsing.

---

## What the Run Did Not Emit

The 17-event stream from that Codex run is also useful for what it did not contain.

No timestamps. No duration. I cannot tell how long the `python3` test execution took, whether the retry was immediate, or whether the total turn was three seconds or thirty. That information may exist somewhere in the client internals, but it was not surfaced in the event data I could read.

No dollar cost. The token counts — 74,858 input, 59,904 cached input, 0 cache-write, 749 output, 201 reasoning output — are real fields from this specific run. They are not a billing claim or a typical-cost estimate; I do not know the rate applied to this model in this context. If I wanted to correlate retry behavior with cost impact across many runs, the capture path would need to expose cost at a useful level.

No handoff events. No Skill-load events.

Those gaps are not complaints about the client. They are evidence about the observability coverage of this event stream. The missing fields correspond to natural follow-up questions: Did the retry add latency? Did loading a Skill consume tokens I did not attribute? Did any handoff occur between agents? A trace contract designed to answer those questions would need to capture those operations. In this run, the record is partial — and partial records make it easy to mistake a green final status for a complete execution story.

I am not comfortable with dashboards that show total token counts and a success rate without a way to drill into individual execution paths. The totals are true and sometimes useful. But they collapse the path. When I see "17 events, completed, 74,858 input tokens," I have a summary. If instrumentation tied the two failed tool calls to the parent agent turn and explicitly linked the retry to the first attempt, I would have a story I could query and reason about.

---

## The Search Signal and the Project Layer

On 2026-07-23, a Google suggestion sweep across `agent observability`, `coding agent observability`, and adjacent seeds returned tools, platform, dashboard, standard, GitHub, open source, `coding agent observability`, `pi coding agent observability`, and `claude code agent observability`. A Bing sweep corroborated tools, platform, framework, monitoring, SDK, tracing, open source, and coding-agent-specific families. Suggestions reflect query intent, not search volume, and they are not a quality ranking. The appearance of named-client variants shows that the query family reaches beyond the general concept.

Hacker News and GitHub currently contain activity in observability, trace, replay, and runtime-evidence projects for agents. Stars and recency are not quality measurements. One project, `disler/pi-agent-observability`, publishes a direction toward a local coding-agent event stream with a dashboard. I mention it only as a direction marker: someone built a project-specific answer to the same gap this article is describing. The broader point is that the question is appearing in search suggestions, repositories, and HN discussions at the same time.

The OpenTelemetry GenAI semantic conventions being in Development status is consistent with that picture. The naming is not finished. The current development vocabulary covers agent, workflow, planning, tool, and usage concepts; Skill loads and any additional framework-specific operations still require explicit instrumentation choices. Instrumentation built against a Development convention may need updates as that vocabulary changes.

---

## The Minimal Contract the Tutorial Needs

What I took from the Codex run is a practical floor, not an ideal ceiling.

A minimal trace contract for a coding agent run needs at least: a shared execution identifier for the full turn, child spans for tool calls with their exit codes and outcome, a parent link to the containing agent operation, an explicit retry relation or link when one attempt follows another, and observed Token counts attached at a defined level. With those fields, the two failures in that run would have been findable by query, not only by reading raw event text line by line.

Beyond that floor, duration, cost, handoff events, and Skill-load events are each their own coverage question. Adding them makes the execution story more complete. Omitting them leaves specific questions unanswerable — but the floor is what makes the difference between a summary and a causal record.

That is the question the [*Coding Agent Observability Guide*](/docs/tutorials/coding-agent-observability-guide/) picks up directly: what does a practical trace implementation look like for a coding agent, what conventions apply today, and where does the Development status of the GenAI semantic conventions require you to make your own choices.

---

## Primary Sources

- [OpenTelemetry — Traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [OpenTelemetry GenAI Semantic Conventions](https://github.com/open-telemetry/semantic-conventions-genai) *(Development status)*
- [OpenAI Agents SDK — Tracing](https://openai.github.io/openai-agents-python/tracing/)
- [Pi Agent Observability](https://github.com/disler/pi-agent-observability)
- [Hacker News — agent observability](https://hn.algolia.com/?q=agent%20observability)
