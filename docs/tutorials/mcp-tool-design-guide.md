---
title: "MCP Tool Design Guide: Boundaries, Schemas, and Errors for Agents"
description: "Design MCP Tools that help Agents choose the right action through task-shaped boundaries, schemas, honest annotations, compact results, and actionable errors."
keywords:
  - MCP Tool design
  - MCP Tools for Agents
  - MCP inputSchema
  - MCP Tool annotations
  - MCP Agent evaluation
sidebar_position: 25
tags: [tutorial, mcp, agent-engineering, typescript]
---

# MCP Tool Design Guide: Boundaries, Schemas, and Errors for Agents

*By Youguang*

## When the Review Layer Is Missing

The pull request looked fine. A single handler, a clean dispatch pattern, two parameters:

```ts
project_api({ action, payload })
```

Backend engineers would read that and move on. The handler is correct. The HTTP response returns 200. Tests pass. From a server perspective, the work is done.

From an Agent's perspective, none of the hard questions have been answered.

Which action applies to this task? What belongs in `payload` for that action? Will this call change any stored state, or is it safe to retry? If the call fails, is that a recoverable business failure or a protocol fault? Which part of the response should drive the next call?

A human caller learns these things from documentation, Slack, or tribal knowledge. An Agent has none of that. It has the Tool definition. That definition is the entire negotiation surface, and `project_api(action, payload)` leaves all seven of those questions open.

This is the review layer that most backend-trained engineers skip: a Tool is an interface for a *non-deterministic* caller. The handler being correct is a necessary condition, not the end of the design. The MCP specification and Anthropic's Tool-design guidance make that layer visible. The rest of this article is about what filling it in actually looks like.

---

## Choosing Boundaries: Tasks, Not Endpoints

The most common mistake I see when teams first wrap a backend in MCP is a one-to-one copy of every endpoint. If the backend has `POST /issues`, `GET /issues`, `POST /issues/:id/close`, and `GET /issues/:id/comments`, the MCP server ends up with four corresponding Tools.

That structure makes sense if you are building a client-side SDK for a human developer. It does not make sense if you are building a decision surface for a reasoning Agent.

Anthropic's engineering guidance on Tool design frames this clearly: implement task-shaped Tools rather than mirroring every backend endpoint. The question to ask is not "what does my backend expose?" but "what decisions does the Agent need to make, and what state changes are consequential enough to require explicit selection?"

For an issue tracker, there are really two task categories:

1. **Finding things**: a read-only operation where the Agent needs to narrow down candidates before taking action.
2. **Changing state on a specific, selected item**: a destructive, user-sanctioned operation that should only run against a known ID.

Those two categories map naturally to two Tools: `issues.search` and `issues.close`. The backend might have six endpoints underneath. The Agent sees two decision nodes with clear, non-overlapping purposes.

Non-overlapping purposes matter. If two Tools could plausibly apply to the same situation, the Agent has to guess, and it will sometimes guess wrong. Ambiguity in Tool selection is not a model problem you can tune away — it is a design problem you can fix.

---

## Names and Descriptions as Context

The name `project_api` tells the Agent that this is related to a project and is an API. That is both obvious and useless. The name carries no signal about when to use the Tool or what it will do.

The MCP specification says Tool names SHOULD be 1–128 characters, use only ASCII letters, digits, underscores, hyphens, or dots, and SHOULD be unique within a server. That last point can break in aggregated environments where multiple servers are joined, which is why namespacing is useful in practice. A prefix like `issues.` scopes both Tools to a domain and makes collisions far less likely without losing readability.

Names are the shortest possible description. Descriptions are the rest of it. Here is what the description for `issues.search` in the synthetic server does:

```
Search the local issue index by words in the title.
Use this before issues.close when the exact issue ID is unknown.
This tool never changes issue state.
```

Three sentences. Each one answers a different question:

- **What does it do?** Searches by title words.
- **When should the Agent use it?** Before closing, when the ID is unknown.
- **Does it change state?** Explicitly no.

The third sentence is the one backend engineers most often omit because it seems obvious from the handler logic. It is not obvious to an Agent reading the description cold. If the description says nothing about side effects, the Agent has to infer from the name, the schema, or the annotations — and it might infer wrong.

The `issues.close` description does the same work from the other direction:

```
Close one issue by exact ID after the user has selected it.
This changes stored issue state.
Repeating the same call returns already_closed without another change.
```

"After the user has selected it" is a sequencing signal. The Agent learns it should only call this Tool once a human has confirmed the target — which aligns with the MCP specification's own note that applications SHOULD preserve human visibility and allow denial or confirmation before executing model-controlled Tool calls. The description reinforces the intended workflow without the Agent needing to reason it out from scratch.

"Repeating the same call returns `already_closed` without another change" tells the Agent exactly what to expect if it retries. That sentence prevents a whole class of unnecessary retries and clarification loops.

---

## Schemas That Remove Ambiguity

`payload: any` puts every decision back on the Agent. A well-constructed `inputSchema` takes those decisions off the table.

The MCP specification defines `inputSchema` as JSON Schema with an `object` at the root. Property descriptions are part of the Tool definition, meaning they are visible to the model at planning time — not just at validation time.

The `issues.search` schema in the synthetic example shows what this looks like in practice:

```ts
inputSchema: z.object({
  query: z.string().trim().min(2).max(80)
    .describe('Two or more characters to match in the issue title'),
  status: z.enum(['open', 'closed', 'any']).default('open')
    .describe('Which issue states to include'),
}),
```

`query` has a minimum length of 2 and a maximum of 80. The Agent cannot submit a single-character query or an unbounded dump. The description explains what the query matches against — the title, not the body or comments. An Agent that tries to search by assignee will know from that description that it is using the wrong field before the request fails.

`status` is an enum, not a free string. The Agent is not guessing between "Open", "OPEN", "active", or "pending". The enum closes that ambiguity entirely. The default of `'open'` means the Agent does not have to specify it for the common case, but the available options are explicit.

The `issues.close` schema is stricter:

```ts
inputSchema: z.object({
  issueId: z.string().regex(/^ISSUE-\d{3}$/),
  reason: z.string().trim().min(5).max(200),
}),
```

The regex `^ISSUE-\d{3}$` means only valid-format IDs will pass. An Agent that constructs an ID from incomplete information — or hallucinates one — will get a validation error before the handler runs. That validation error is actionable: it tells the Agent the ID format is wrong, which gives it something to correct rather than a silent bad state change.

`reason` has a minimum of 5 characters. This prevents the Agent from submitting an empty or trivially short reason to satisfy the required field. Minimum lengths on free-text fields are a lightweight way to push toward substantive inputs.

The principle is: every degree of freedom left in the schema is a decision the Agent must make at runtime without the context the schema designer had at design time. Enums, patterns, ranges, and clear property descriptions are not constraints on the Agent — they are information transferred to the Agent.

---

## Annotations: Honest Signals, Not Permission Checks

The MCP specification defines four behavioral hints: `readOnlyHint`, `destructiveHint`, `idempotentHint`, and `openWorldHint`. The defaults are deliberately conservative — read-only false, destructive true, idempotent false, open-world true — because the consequence of underestimating impact is worse than overestimating it.

For the synthetic `issues.search`:

```ts
annotations: { readOnlyHint: true, openWorldHint: false },
```

`readOnlyHint: true` tells clients that this Tool should not modify state. `openWorldHint: false` signals that the Tool operates on a known, bounded dataset rather than an open-ended external world. Together these two hints may inform client or application policy — for example, how a trusted server's Tools are presented or whether a confirmation step is included — but annotations do not themselves suppress or enforce confirmation behavior.

For `issues.close`:

```ts
annotations: {
  readOnlyHint: false,
  destructiveHint: true,
  idempotentHint: true,
  openWorldHint: false,
},
```

`destructiveHint: true` is honest — closing an issue changes stored state in a way that isn't trivially reversible. `idempotentHint: true` reflects the fact that calling `issues.close` with the same arguments a second time returns `already_closed` rather than changing anything further. That combination is accurate: the call is destructive on first use and idempotent on repetition.

Two cautions are worth stating plainly.

First, every annotation is a hint. The MCP specification is explicit: clients MUST treat annotations as untrusted unless they are received from a server that is trusted in that client's trust model. An annotation that says `readOnlyHint: true` does not sandbox the handler. An adversarial or misconfigured server can mark a state-changing Tool as read-only and clients have no way to verify otherwise from the annotation alone. Annotations inform client UI behavior and model planning — they do not enforce behavior.

Second, be honest. An annotation that claims `readOnlyHint: true` for a Tool that actually writes to a database is misleading to the model and the human reviewing the conversation. If your client uses annotations to decide whether to show a confirmation dialog, a dishonest annotation removes that check silently.

---

## Results: Compact, Actionable, Parseable

The most common output anti-pattern I see is returning an entire backend record when the calling Agent only needs a subset of its fields.

If `issues.search` returns every field on every matching issue — body, all comments, full audit log, nested assignee objects — the response volume grows with dataset size, and the Agent has to locate the relevant identifiers inside that noise. Anthropic's engineering guidance on this is direct: return high-signal context, not entire raw datasets; control large responses with filters, pagination, limits, or concise/detailed modes.

The synthetic example returns a compact `structuredContent` shape:

```ts
outputSchema: z.object({
  count: z.number().int().nonnegative(),
  issues: z.array(z.object({
    id: z.string(),
    title: z.string(),
    status: z.enum(['open', 'closed']),
  })),
}),
```

Three fields per issue: `id`, `title`, `status`. That is enough for the Agent to surface results to the user, enough for the user to select one, and enough for the Agent to pass the `id` into `issues.close`. Nothing more is needed for that workflow.

The `outputSchema` field is optional in MCP, but when provided, the server's `structuredContent` MUST conform to it. Clients SHOULD validate incoming structured content against the declared schema. For backward compatibility, a Tool that returns `structuredContent` SHOULD also return a human-readable summary in a `text` content block. The synthetic example does both:

```ts
return {
  content: [{ type: 'text', text: 'compact human-readable matches' }],
  structuredContent: { count, issues: matches },
};
```

The text block is for clients or models that cannot consume structured content natively. The structured content is for clients that can.

---

## Errors: Protocol Faults vs. Recoverable Failures

There are two kinds of failure in MCP Tool execution and they should not be mixed up.

**Protocol errors** — an unknown Tool name, a malformed request envelope, a server crash — are errors in the MCP transport layer. These are not Tool results. They propagate as protocol-level error responses.

**Tool execution errors** — a validation failure, a not-found ID, a business rule rejection — are outcomes of a Tool call. The call was received, and either schema/input validation failed before the business handler ran, or the handler ran and the outcome was negative. These should be returned as Tool results with `isError: true`.

The distinction matters because protocol errors are not returned as Tool results with `isError: true` and therefore do not provide the same model-facing recovery path; Tool execution errors can be exposed to the model so it can often adjust and retry.

In the synthetic server, if `issues.close` is called with an ID that does not exist, the handler returns:

```ts
{
  isError: true,
  content: [{
    type: 'text',
    text: 'Unknown issue ISSUE-999. Call issues.search to find a valid issue ID, then retry.',
  }],
}
```

That error message contains everything the Agent needs to recover: the unknown ID (so the Agent knows which call failed), and the recovery path (use `issues.search` first). A generic "not found" with no further instruction is technically correct and practically useless. Anthropic's guidance on error design captures this precisely: make errors specific and actionable.

---

## Verification: What the Local Tests Actually Prove

After building the synthetic server with Node.js v24.18.0, pnpm 11.10.0, `@modelcontextprotocol/server` 2.0.0, `@modelcontextprotocol/client` 2.0.0, and Zod 4.4.3, I ran it against an in-memory transport. The verification output was:

```json
{
  "toolOrder": ["issues.search", "issues.close"],
  "invalidSchemaInputIsError": true,
  "searchMatches": ["ISSUE-001", "ISSUE-002"],
  "missingIssueIsError": true,
  "firstClose": "closed",
  "repeatedClose": "already_closed"
}
```

What this confirms:

- The server returns Tools in deterministic order. The MCP specification says servers SHOULD return Tools in deterministic order when the set has not changed; this supports reliable client caching and prompt-cache reuse.
- Invalid schema inputs are caught and returned as `isError: true` results, not protocol errors.
- Search returns the expected IDs from the in-memory dataset.
- Calling `issues.close` on a missing ID returns `isError: true`.
- The first valid close returns `"closed"`. A repeated call with the same arguments returns `"already_closed"`.

What this does **not** confirm: that a live Agent will select the correct Tool, construct valid arguments, interpret results correctly, or successfully complete a realistic multi-step task. Handler tests and Agent evaluations answer different questions. Handler tests confirm that the Tool behaves correctly given a specific input. Agent evaluations confirm that a non-deterministic caller, reasoning from the Tool definition alone, can complete a realistic task reliably.

These are not the same question.

:::tip[Run the verified example]
<a href="/examples/mcp-tool-design-guide.zip" download>Download the verified TypeScript example</a>, install its pinned dependencies with pnpm, and run `pnpm verify` to reproduce the in-memory checks described above.
:::

---

## Running Realistic Evaluations

I did not run live-model evaluations for this tutorial, and I am not going to fabricate numbers. But here is the shape of an evaluation setup that would answer the questions handler tests cannot:

1. **Define realistic tasks with verifiable outcomes.** "Find all open issues containing the word 'timeout' and close the most recent one with a clear reason." Not "call issues.search."

2. **Include tasks that require multiple calls and ambiguous initial information.** Tasks where the Agent does not know the issue ID at the start, and has to search, present options, get confirmation, and then close. Single-call tasks test the handler; multi-call tasks test the Tool design.

3. **Run each task in a fresh Agent loop with only the intended Tool set.** Don't let evaluation sessions bleed into each other. Each run should start from the same state.

4. **Inspect the transcript, not just the final outcome.** Did the Agent call the right Tool first? Were the arguments valid on the first attempt? How many retries happened? Were any unnecessary calls made? Was the structured content consumed efficiently or ignored?

5. **Keep a held-out task set.** If you change a Tool description or schema in response to evaluation failures, rerun the full set. If you tune the description to pass held-out tasks, you have overfit to the held-out set — keep a second tier.

Anthropic's engineering guidance on this is to prototype quickly, then evaluate against realistic tasks, and to judge changes by task completion and transcripts rather than only by handler tests. That order matters. Build first, evaluate second, refine against outcomes.

---

## Before/After: The Refactor in One Table

| Dimension | `project_api({ action, payload })` | `issues.search` / `issues.close` |
|---|---|---|
| **Boundary** | One Tool for all operations | One Tool per task category |
| **Name** | Generic wrapper name | Namespaced, action-specific names |
| **Description** | None (implied by name) | When to use, when not to, side-effect statement |
| **Schema** | Freeform `payload` | Enums, regex, ranges, property descriptions |
| **Annotations** | Default (destructive true) | Honest per-Tool hints |
| **Output** | Whatever the backend returns | Compact, validated `structuredContent` + text block |
| **Errors** | HTTP error codes mixed with business failures | `isError: true` with actionable recovery message |

---

## Tool Review Checklist

Before registering a Tool in a server that Agents will use, I ask these questions:

**Boundary**
- [ ] Does this Tool map to one decision category or one consequential action, not a bundle of unrelated operations?
- [ ] Is the purpose non-overlapping with every other Tool in this server?

**Name**
- [ ] Is the name namespaced to a domain?
- [ ] Does the name describe what the Tool does, not just that it is an API?

**Description**
- [ ] Does the description say when to use this Tool?
- [ ] Does it say when *not* to use it, or which Tool to use instead?
- [ ] Does it explicitly state whether the Tool changes state?
- [ ] Does it say what to expect on retry if the Tool is idempotent?

**Schema**
- [ ] Are free strings replaced with enums wherever the valid set is bounded?
- [ ] Are patterns, minimums, and maximums in place for string and numeric fields?
- [ ] Does every property have a description that explains what it matches or accepts?
- [ ] Does the `outputSchema` capture only the fields the next call will need?

**Annotations**
- [ ] Do the annotations accurately reflect the Tool's actual behavior?
- [ ] Has `readOnlyHint` been set honestly — not just set to `true` to suppress confirmation prompts?
- [ ] Has `idempotentHint` been verified against the actual handler logic?

**Results**
- [ ] Does the `structuredContent` include identifiers needed for follow-up calls?
- [ ] Is a `text` content block also returned for backward compatibility?
- [ ] Is the response volume bounded — no entire backend records when a subset suffices?

**Errors**
- [ ] Are recoverable failures returned as `isError: true` Tool results, not protocol errors?
- [ ] Does the error message name the failing field or value and suggest a recovery path?

**Verification**
- [ ] Have handler tests confirmed the schema validation, error paths, and idempotency behavior?
- [ ] Is there a plan to run Agent evaluations on realistic tasks after the handler tests pass?

---

The handler tests will tell you when the Tool behaves correctly given a specific input. They will not tell you whether a reasoning Agent, reading only the Tool definition, can reliably complete a task that requires multiple calls and incomplete initial information.

That gap is what realistic Agent evaluations close. Build the Tool definitions until the checklist passes. Then build the evaluations.

---

## Official References

- [MCP Tools specification (2026-07-28)](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) — normative definitions of `inputSchema`, `outputSchema`, `structuredContent`, annotations, and error handling.
- [MCP schema reference (2026-07-28)](https://modelcontextprotocol.io/specification/2026-07-28/schema) — full JSON Schema definitions for Tool registration and result shapes.
- [MCP server quickstart (2026-07-28)](https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server) — getting a TypeScript MCP server running.
- [Anthropic: Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — Anthropic's engineering guidance on task-shaped Tools, description strategy, error design, and evaluation.
- [MCP Tool Annotations (2026-03-16)](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/) — MCP blog post on the four behavioral hints, their defaults, and their trust boundary.
- [TypeScript SDK Tool examples](https://github.com/modelcontextprotocol/typescript-sdk/blob/cc4b41617ce3601b1290d67216ea0b194a3cd9ac/examples/guides/servers/tools.examples.ts) — official SDK examples for Tool registration, schema definition, and result handling.

---

## Related Guides

- [MCP Server Guide](/docs/tools/mcps/)
- [MCP 2026-07-28 Stateless Migration Guide](/docs/tutorials/mcp-2026-07-28-stateless-migration/)
- [MCP Server Security Checklist](/docs/tutorials/mcp-server-security-checklist/)
- [Coding Agent Evals Guide](/docs/tutorials/coding-agent-evals-guide/)
