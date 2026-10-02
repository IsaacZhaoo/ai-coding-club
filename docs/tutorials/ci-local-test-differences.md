---
title: "Tests Pass Locally But Fail in CI: Use an AI Agent to Compare the Evidence from Two Runs"
sidebar_label: "Local Tests Pass, CI Fails"
description: "Compare local and CI test logs, source, dependencies, timezones, and event order to guide an AI agent toward a verifiable fix."
keywords: ["CI test failures", "AI debugging", "GitHub Actions", "flaky tests"]
sidebar_position: 43
tags: ["tutorial", "agent-engineering"]
---

# Tests Pass Locally But Fail in CI: Use an AI Agent to Compare the Evidence from Two Runs

If you’ve ever stared at a green checkmark on your laptop and a red X in your pipeline, you know the frustration. The same test passes when you run it locally but fails in continuous integration (CI), or worse, it intermittently fails in CI without a clear pattern.

This isn’t just about “it works on my machine.” It’s about systematically comparing the evidence from two runs—your local environment and the CI job—and using an AI coding agent to help you spot what actually changed.

Below is a practical, step-by-step guide. It assumes you have:

- An existing project
- A failed CI job log
- A working test command (e.g., `npm test`)
- Access to your repository and logs

After reading, you’ll be able to collect the right evidence, form an explanation, ask a focused question of an AI agent, and verify the fix in the original CI job plus related conditions.

---

## 1 Why This Problem Persists

The core issue isn’t usually “the test is wrong.” It’s that local and CI environments differ in subtle ways:

- Dependency versions (resolved, not declared)
- Install commands and lockfile usage
- OS, Node version, and runtime flags
- Timezone and date handling
- Environment variables and secrets
- Parallelism, workers, and test data setup/teardown
- Async timing and shared state

These differences are often invisible until a test fails. Developers tend to:

- Guess (“maybe it’s timezone?”)
- Change something randomly (“I’ll reinstall dependencies”)
- Ask an AI agent without context (“Why is this failing?”)

All of that wastes time. The more precise your evidence, the faster you get a correct diagnosis.

---

## 2 Collect Evidence from Both Runs

Start by gathering concrete data from both the local pass and the CI failure.

### From the CI Job

1. Locate the failed step in your GitHub Actions (or other CI) run:
   - Open the workflow run → Jobs → Steps.
   - Click the failing step to see its logs.
2. Extract:
   - Exact test name or assertion that failed.
   - Full error message and stack trace.
   - Surrounding log lines (setup, install, environment).
3. Record metadata:
   - Workflow file and job name.
   - Commit SHA that triggered the run.
   - Branch/tag used.
4. If your agent client supports GitHub MCP with proper permissions, you can pull logs directly. Otherwise, copy relevant sections and paste them into your chat.

### From Your Local Machine

1. Ensure you’re on the same commit:
   - `git rev-parse HEAD`
2. Confirm versions:
   - `node --version`
   - `npm --version` (or `yarn --version`, etc.)
3. Run the exact test command used in CI:
   - For npm projects, that’s usually `npm test`.
   - Capture stdout/stderr and any exit codes.
4. Note:
   - Install command (`npm ci`, `npm install`, `yarn install`, etc.).
   - Whether you’re using a lockfile and if it matches.

This baseline lets you compare apples to apples instead of guesses.

---

## 3 Compare Environment Conditions That Actually Matter

Not every environment detail is relevant. Focus on conditions that can change test behavior.

### Node/npm Projects: Key Checks

- **Lockfile presence and integrity**
  - CI often uses `npm ci`, which requires a valid lockfile (`package-lock.json` or `npm-shrinkwrap.json`).
  - If the manifest and lockfile mismatch, `npm ci` fails.
- **Install command**
  - Local: `npm install` (may read from registry, ignore lockfile if missing).
  - CI: `npm ci` (strict, deterministic).
- **Resolved dependency versions**
  - Run `npm ls` locally and compare with CI logs.
  - Pay attention to transitive dependencies that differ.
- **OS and Node flags**
  - OS differences can affect file paths, locale, and some libraries.
  - Check for runtime flags (e.g., `--max-old-space-size`).

### Environment Variables and Secrets

Record only task-relevant settings:

- Timezone (`TZ`)
- Locale-related variables
- Flags that affect test data or behavior
- Presence of secrets (e.g., API keys) – just note whether they’re set, don’t paste values.

Example:

| Condition          | Local        | CI           |
|--------------------|--------------|--------------|
| Node version       | 20.11.0      | 20.11.0      |
| npm version        | 10.2.4       | 10.2.4       |
| Lockfile present   | Yes          | Yes          |
| TZ                 | (unset)      | Europe/Paris |
| Parallel workers   | 1            | 4            |

---

## 4 Ask an AI Agent a Focused Question

Once you have evidence, craft a precise prompt. Avoid vague “fix this” requests.

### Good Prompt Structure

- Context: Project type, test framework, CI platform.
- Evidence: Exact failing assertion, key environment differences.
- Goal: What you suspect or want to confirm.

Example:

> I’m running Jest in an npm project. Locally `npm test` passes, but in GitHub Actions the same commit fails with:
> ```log
> [Local] 2024-10-09T12:34:56.789Z → "Oct 9, 2024 12:34:56 PM"
> [CI]    2024-10-09T12:34:56.789Z → "Oct 9, 2024 05:34:56 AM"
> ```
> Local timezone differs from CI environment.
> Suggest a minimal change that aligns snapshot generation and checking across environments, and tell me how to verify it in CI.

This gives the agent:

- The exact failure
- The environment contrast
- A clear, testable goal

---

## 5 Real-World Cases That Illustrate the Process

### date-fns #564 and Okami’s Date Snapshots (2017)

A classic example of timezone-driven flakiness:

- **Problem:** Okami’s Jest tests passed locally but failed on Travis CI.
- **Root cause:** Date snapshots were generated with one timezone and checked with another.
- **Fix:** The maintainer recommended setting `TZ` consistently for:
  - Snapshot generation
  - Snapshot checking
  - Regular test runs
- **Implementation:** A single commit added `TZ=Europe/Paris` to ordinary tests, snapshot updates, and watch commands, then removed a Travis-only `before_install TZ` setting.
- **Outcome:** The original author reported both local and CI passing after the change.

Key takeaway: When dates are involved, ensure the same timezone is used for generating and checking snapshots.

### DuckDB PR #8665 (2023) – Timezone Timestamp Roundtrip

Another real case involving version and environment interaction:

- **Problem:** A CI test failed with Python 3.7 / pandas 1.3.5 around timezone-aware timestamp roundtrips.
- **Initial idea:** Skip pandas < 2 to avoid complexity.
- **Final fix:** Retain compatibility by handling different dtype expectations:
  - **DuckDB PR #8665 (pandas ≥2 branch)**: Uses the specified `unit` with microsecond resolution (`us`) in `expected_dtype`.
  - For older pandas: construct input and expected dtype in nanoseconds (`ns`).
- **Lesson:** When date/time tests fail, check actual versions and their expected formats, not just the code.

---

## 6 Async Timing and Shared State

Many “pass locally / fail in CI” issues are timing or state-related.

### Jest and Promises

Jest waits for a Promise that a test returns or awaits. But:

- A promise can resolve after only dispatching background work.
- Your assertion may run before the real business event completes.

Example pattern:

- Background job is queued.
- Test resolves immediately.
- Assertion checks state that hasn’t updated yet.

**Solution:**

- Wait for an observable completion signal (callback, event, or final status).
- Or use bounded state polling with a timeout instead of a fixed `sleep`.

GitHub’s teaching logs illustrate this:

- Passing run: Background job completed → then check order status.
- Failing run: Check order status first → sees “pending” → test fails.

The difference is event ordering, not code correctness.

### pytest and Flaky Tests

pytest explicitly lists common flakiness sources:

- Test-order dependence
- Uncleaned global state
- Parallel execution interference
- Overly strict timing assertions

Compare:

- Are tests using shared fixtures or globals?
- Is cleanup running reliably in CI vs local?
- Are parallel workers causing race conditions?

---

## 7 A Minimal Verification Loop

After applying a fix, don’t just run the test once. Use a tight verification loop:

1. **Run the original failing CI configuration** with the fixed commit SHA.
2. **Confirm effective environment:**
   - Check actual `TZ` and other relevant variables in logs.
   - Ensure snapshot generation and checking use the same settings.
3. **Check related conditions:**
   - If the issue was async timing, verify completion before assertions.
   - If it was state, ensure isolation between tests.
   - If it was dependency-related, confirm the correct branches/versions are used.
4. **Run regression checks:**
   - Run the full test suite in CI.
   - Optionally run locally with identical flags (`TZ=... npm test`).

Passing observations under these conditions support your proposed fix. Unconfirmed causes remain candidates until proven otherwise.

---

## 8 Putting It All Together: Your Checklist

Use this as a quick reference when you face a local-pass / CI-fail scenario.

- [ ] Extract from CI:
  - Failed test name/assertion
  - Full error message and stack trace
  - Workflow, job, commit SHA
- [ ] Confirm both runs use the same source and test command.
- [ ] Record environment:
  - Node/npm/yarn versions
  - Install command (`npm ci` vs `npm install`)
  - Lockfile presence and integrity
  - OS and any runtime flags
  - Relevant environment variables (e.g., `TZ`)
  - Parallelism/workers settings
- [ ] Compare resolved dependency versions (`npm ls`, CI logs).
- [ ] Identify date/time or async patterns in the failing test.
- [ ] Form a hypothesis: “The failure is due to X because Y.”
- [ ] Ask an AI agent with:
  - Evidence
  - Hypothesis
  - Request for a minimal change and verification steps
- [ ] Apply the fix using the fixed commit SHA.
- [ ] Re-run the original failing CI job configuration.
- [ ] Verify effective environment and related conditions.
- [ ] Run regression tests to ensure no new failures.

---

## 9 Final Note

The goal isn’t to memorize every possible cause. It’s to build a repeatable process:

1. Collect precise evidence from both runs.
2. Compare only the conditions that can affect behavior.
3. Ask an AI agent with focused context, not vague complaints.
4. Verify the fix in the original CI job and related scenarios.

When you treat your local machine and CI as two experiments with different settings, the answers stop being mysterious and start being predictable.

**Further Reading**  
- [date-fns Issue #564](https://github.com/date-fns/date-fns/issues/564) – Timezone handling in formatting  
- [okami Commit 54c27c9](https://github.com/Kilix/okami/commit/54c27c96045b243a33e44cf3eb4bef2a06779e6c) – Snapshot generation with fixed TZ  
- [DuckDB PR #8665](https://github.com/duckdb/duckdb/pull/8665/files) – Timestamp unit and dtype alignment  
- [GitHub Copilot: Diagnose CI Test Failures](https://docs.github.com/en/copilot/tutorials/copilot-cookbook/debug-errors/diagnose-ci-test-failures)  
- [npm ci Documentation](https://docs.npmjs.com/cli/v11/commands/npm-ci)  
- [Jest Asynchronous Testing](https://jestjs.io/docs/asynchronous)  
- [Node.js CLI Timezone](https://nodejs.org/api/cli.html#tz)


## Related Guides

- [Review AI-Generated Tests](/docs/tutorials/ai-generated-test-review/)
- [Debugging Deep Dive](/docs/course/essential-skills/debugging-deep-dive/)
- [Migrate Jest 29 to 30 Without Losing Test Intent](/docs/tutorials/jest-major-version-migration/)
