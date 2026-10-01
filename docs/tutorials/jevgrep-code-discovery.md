---
title: "Find Code by Behavior: A Jevgrep Tutorial for AI-Coding Clubs"
sidebar_label: "Jevgrep Code Discovery"
description: "Find code by behavior with Jevgrep, inspect source evidence, and give your coding agent a focused implementation task."
keywords: ["Jevgrep", "semantic code search", "AI coding agent", "code discovery"]
sidebar_position: 42
tags: ["tutorial", "agent-engineering"]
---

# Find Code by Behavior: A Jevgrep Tutorial for AI-Coding Clubs

You’ve landed in a new repository. You know what you need—maybe it’s a retry handler that kicks in after a timeout, or a telemetry recorder that buffers events before flushing—but you don’t know which files implement it. Instead of guessing, searching with `grep`, or asking a coding agent to “search the whole repo” (and then hoping it doesn’t hallucinate), you can give your agent high-quality evidence: exact file paths, quoted source, and line references.

That evidence comes from **Jevgrep**.

This tutorial walks through:
- Installing Jevgrep and configuring an LLM provider
- Turning a natural-language behavior description into a search query
- Reading the outputs (paths, verbatim code, call relationships)
- Handing that evidence to your coding agent for implementation or verification

No deep theory—just actionable steps you can use in a real project today.

## 1. What Jevgrep Does and Why It Matters

Jevgrep is a relevance-based source retrieval CLI (short: `jg`). Instead of just matching keywords, it uses Jev—a lightweight model layer—to score:
- Directories
- Files
- Declarations (functions, classes, etc.)

It then returns reading leads sorted by relevance. That means you (and your coding agent) can quickly zero in on the exact places where a behavior lives.

**Who is this for?**
Developers comfortable with the terminal and using an AI coding agent who:
- Work in unfamiliar codebases
- Need to locate specific behaviors (e.g., “auth before handler”, “telemetry recording”, “retry on timeout”)
- Want to send a focused, well-scoped source set to their provider

## 2. Prerequisites

Before we begin, make sure you have:

- Node.js 22 or newer (`node --version`)
- npm (comes with Node)
- A macOS or Linux environment
- Your preferred LLM provider API key (Vercel AI Gateway, OpenRouter, TypeSafe, etc.)

Jevgrep bundles everything it needs. No separate Python, Bun, or ripgrep installation required.

## 3. Installation and First Checks

From your project root (or anywhere you like), run:

```sh
npm install --global @dzhng/jevgrep@0.7.1
jg --version
```

If `--version` prints something like `0.7.1`, you’re ready to configure a provider.

### 3.1 Authenticate with an LLM Provider

Jevgrep needs a provider to judge relevance. Run:

```sh
jg auth
```

The interactive flow will ask you to choose from presets such as:
- `vercel` (Vercel AI Gateway)
- `typesafe`
- `openrouter`
- `opencode`

Or you can enter a custom TypeSafe-compatible endpoint. Once selected, your credentials are saved to:
- `$XDG_CONFIG_HOME/jevgrep/credentials.json`, or
- `~/.config/jevgrep/credentials.json` (if XDG is not in use)

When you run `jg auth` and select a provider, the client saves your chosen credentials locally so that all subsequent searches use this configuration automatically. Notably, the CLI ignores any environment variables for API keys, endpoints, or model overrides; these values are read only from your saved auth state. If you need to switch providers later, simply run `jg auth` again with the new selection.

### 3.2 Verify Your Setup

Before searching, confirm Jevgrep can talk to your provider:

```sh
jg doctor
```

It runs a synthetic query against your saved configuration and reports success or failure. If it fails:
- Check your provider’s rate limits or billing status
- Rerun `jg auth` to switch providers if needed

## 4. Understanding the Search Scope

Jevgrep doesn’t search everything blindly. It respects common ignore patterns (build dirs, hidden files, credential files, binaries) but you can refine the scope with explicit arguments and flags.

### 4.1 Inspect What Will Be Searched

Before running a query, use `jg files` to see Jevgrep’s plan:

```sh
jg files ./my-project --exclude 'src/generated/'
```

You’ll get something like:

- File counts and total bytes grouped by top-level directory
- Skip counts for excluded patterns or ignored files

`jg files` scans your project locally and returns a preview of eligible file counts, total bytes, top-level directory groups, and filter skip counts. This scan requires no provider key and sends no data to any external service. These metrics help you decide the search scope, while project constraints then determine which specific sources are uploaded to your selected provider. The default filtering excludes obvious sensitive files and build or dependency content, though this is not a strict guarantee of completely secret-free input.

### 4.2 Choosing the Root and Exclusions

For unfamiliar repos, it’s best to:
- Start narrow: `./src` or a known subsystem
- Add exclusions for generated code or test scaffolding

Example:

```sh
jg files ./src --exclude 'generated/' --exclude '__snapshots__/'
```

Use the exact root and flags you intend to search in your actual query—consistency matters.

## 5. Writing Effective Behavior Queries

Jevgrep thrives on natural-language descriptions of behavior, conditions, and context. Avoid vague keywords; be specific about flow and boundaries.

### 5.1 Good vs. Vague Queries

❌ Vague:
- “Where is authentication used?” (too broad, many false positives)

✅ Better:
- “Where is authentication checked before a request reaches a handler?”
- “Which tests cover retry behavior when a request times out after 3 seconds?”
- “How are telemetry events recorded and sent to the endpoint?”

The examples above illustrate three common patterns you might need: pre-handler validation, timeout/retry handling, and telemetry pipelines.
1. Pre-handler validation (auth, rate limiting)
2. Error handling with backoff/retry
3. Observation/logging pipelines

### 5.2 Running a Search

Basic search syntax:

```sh
jg "<your behavior query>" <root> [flags]
```

Examples:

```sh
jg "How are telemetry events recorded and sent?" ./my-project --exclude 'src/generated/'

jg "Where is authentication checked before a request reaches a handler?" .

jg "Which tests cover retry behavior when a request times out?" .
```

Replace `./my-project` with your actual directory. Using the repo root (`.`) is fine for small projects or well-structured repositories.

## 6. Reading the Output: From Summary to Evidence

Jevgrep prints several layers of information, each useful at different stages.

### 6.1 Top-Level Structure

The output typically has three sections:
1. **Summary & Compact File List**
   - High-level overview and top candidates
2. **Verbatim Source with Line References**
   - Exact code excerpts with file paths and line numbers
3. **Declaration and Call Locations**
   - Jevgrep provides declaration positions and possible local call sites from static structure.

### 6.2 What to Look For

- **File paths**: These are your primary handoff to a coding agent.
- **Line references**: Crucial when asking an agent to modify or add tests.
- **Quoted source**: Shows context without requiring you to open every file immediately.
- **Call relationships**: Helps confirm whether a candidate is truly the implementation, not just a caller.

## 7. Interpreting Example Telemetry Results

To make this concrete, here’s what Jevgrep might return for a telemetry-style query in a typical Node/TypeScript service, based on its actual recorded behavior.

**Query:**
```sh
jg "How are telemetry events recorded and sent?" ./my-project --exclude 'src/generated/'
```

**Actual output highlights (from recorded runs):**

- Files matched:
  - `src/telemetry.ts`
  - `src/backend/events.ts`
  - `tests/telemetry.test.ts`

- Verbatim excerpts from the source:

  From `src/telemetry.ts`:

  ```typescript
  // Events preserve the caller's name.
  export class Telemetry {
    recordEvent(name: string) {
      return { name, recorded: true };
    }
  }
  ```

  From `src/backend/events.ts`:

  ```typescript
  import { Telemetry } from '../telemetry';
  // Backends preserve the same event contract.
  export class BackendTelemetry extends Telemetry {
    recordEvent(name: string) {
      return super.recordEvent(name);
    }
  }
  ```

- Test evidence of behavior:

  From `tests/telemetry.test.ts`:

  ```typescript
  import { Telemetry } from '../src/telemetry';
  // Regression example: do not rename the caller's event.
  export function testEventName() {
    return new Telemetry().recordEvent('opened').name === 'opened';
  }
  ```

This tells you:
- There’s a base `Telemetry` class whose `recordEvent(name)` returns an object preserving the caller’s event name.
- `BackendTelemetry` extends it and forwards the call, maintaining the same contract.
- The test explicitly verifies that the returned object’s `name` matches the input `'opened'`.

You can now hand this exact set to your coding agent with confidence.

## 8. Handing Evidence to Your Coding Agent

Once you’ve identified the files, lines, and relationships:

1. **Copy the relevant paths** into your chat/agent prompt.
2. **Paste the quoted excerpts** that matter (shorter is better; keep context).
3. **Reference line numbers** when asking for changes or tests.

Example agent prompt fragment:

> Here is the telemetry recording implementation and behavior evidence:
> - `src/telemetry.ts`: base implementation returning `{ name, recorded: true }`
> - `src/backend/events.ts`: subclass that forwards to preserve the contract
> - Test at `tests/telemetry.test.ts`: confirms caller’s name is preserved in output
>
> Task: Extend `BackendTelemetry.recordEvent` to include an `eventId` field in the returned object when available. Ensure the base behavior (preserving `name` and `recorded`) remains unchanged, and update the test so it still passes while also verifying the new `eventId` is attached correctly.

You’ve now replaced vague requests (“add telemetry ID logging”) with a focused, evidence-backed task your agent can solve quickly.

## 9. Practical Tips for Reliable Searches

### 9.1 Output Handling

Jevgrep prints to stdout; it doesn’t create report files automatically. You can save outputs when needed:

```sh
jg "How are telemetry events recorded and sent?" ./my-project --exclude 'src/generated/' > telemetry-search.txt
```

This is useful for:
- Audit trails of what you asked
- Sharing context with a team member or agent in one file

### 9.2 Concurrency and Slow Connections

On unstable or rate-limited connections, limit parallel API calls:

```sh
jg "Where is authentication checked before a request reaches a handler?" . --concurrency 4
```

- Default concurrency: 32
- Recommended for slow networks: 4 or lower
- For serial execution (very unstable): `--concurrency 1`

Inspect the reported reason: a narrower scope helps budget-related gaps, and connection recovery helps transport-related gaps. You can:
- Rerun the search after connection recovery
- Use `--no-cache` to force a fresh evaluation if needed

### 9.3 Exit Codes

- `0`: Complete success
- `1`: Failed (e.g., auth or network issue)
- `2`: Incomplete results (some queries didn’t resolve)
- `130`: Interrupted (Ctrl+C)

If you get exit code `2`, rerun the search or try a narrower root or query.

### 9.4 Caching Behavior

Jevgrep caches valid answers locally by default:
- Provider errors and final results are not cached.
- Rerunning after recovery reuses cached evaluations where possible and retries failed work.

To bypass everything for one run (useful during debugging):

```sh
jg --no-cache "query" .
```

### 9.5 Exact Symbols vs. Behavioral Queries

If you know the exact symbol or path:
- Use a direct file read or ripgrep (`rg`) for speed.
- Use Jevgrep when your goal is behavioral discovery across an unfamiliar codebase.

## 10. Integrating with Your Coding Agent Workflow

There’s a small but important ecosystem step around agents and Jevgrep.

### 10.1 Install the Usage Skill

Run this from your project root:

```sh
jg skill
```

This delegates to `npx skills`, which:
- Requires npm/npx and network access
- Installs a usage skill into the agent’s toolset

The workflow:
1. Install CLI: `npm install --global @dzhng/jevgrep@0.7.1`
2. Authenticate provider: `jg auth`
3. Install skill: `jg skill`
4. Upgrade CLI later with `npm install --global @dzhng/jevgrep@latest`
5. Re-run `jg skill` separately to update the installed skill

The skill allows your agent to:
- Run Jevgrep directly inside its context
- Receive relevance-ranked evidence, not just a raw file dump

Even if you don’t use the skill in every session, having it available gives your agent first-class access to high-quality search when needed.

### 10.2 A Minimal Agent Prompt Template

When using your agent with Jevgrep evidence:

> Project root: `./my-project`
> Search context (generated by jg): [paste summary and key excerpts]
> Behavior identified: “Events are recorded via `recordEvent(name)` in `src/telemetry.ts` and subclassed in `src/backend/events.ts`.”
> Task: Implement X using this pattern, and add tests that cover edge cases.

The clearer your context, the fewer iterations you’ll need.

## 11. Troubleshooting Common Issues

- **No matches found?**
  - Try a broader root (e.g., `.`) or a simpler query.
  - Confirm your exclude patterns aren’t too aggressive.
- **“Unrecovered provider error”**
  - Check your API key, billing status, and rate limits.
  - Switch providers with `jg auth` if needed.
- **Inconsistent results between runs**
  - Use `--no-cache` to force a fresh evaluation.
  - Ensure you’re using the same root and exclude flags each time.
- **Huge output from large repos**
  - Narrow the root to `./src` or a specific domain folder.
  - Add more exclusions for vendor/build artifacts.

## 12. Summary: Your Evidence-Based Workflow

Here’s the end-to-end loop you’ll use repeatedly:

1. **Define the behavior** you need (“auth before handler”, “retry on timeout”, etc.).
2. **Inspect scope** with `jg files` to avoid surprises.
3. **Run Jevgrep**: `jg "<behavior>" ./root --exclude 'generated/'`.
4. **Read outputs**: note paths, quoted code, and line references.
5. **Validate quickly**: open one or two files at cited lines to confirm relevance.
6. **Hand evidence to your agent**: attach paths, excerpts, and specific tasks.
7. **Iterate if needed**: refine the query or root based on the agent’s results.

You now have a repeatable method for turning “I need to find where X happens” into “Here is exactly where X happens, with proof.” That’s the difference between guessing and engineering with AI.

—

**Further Reading:**
- Official overview: https://github.com/dzhng/jevgrep
- CLI operation and authentication: https://github.com/dzhng/jevgrep/blob/c9c70c448842297093e9f1187c493cdf9fa69d7b/apps/cli/README.md
- Example stdout output: https://github.com/dzhng/jevgrep/blob/c9c70c448842297093e9f1187c493cdf9fa69d7b/specs/done/jevgrep/assets/stdout-example.txt

Keep this page handy. The next time you face an unfamiliar codebase and a well-defined behavior you need, run Jevgrep first—then let your agent do the rest.

## Related Guides

- [Read a Repository with Hermes Agent](/docs/tutorials/hermes-agent-first-task/)
- [Local Tests Pass, CI Fails](/docs/tutorials/ci-local-test-differences/)
- [AI Code Review Workflow](/docs/tutorials/ai-code-review-workflow/)
