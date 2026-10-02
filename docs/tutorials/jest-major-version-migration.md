---
title: "Migrating Jest29 to Jest30 With an Agent: A Structured Approach Using NestJS as a Reference"
sidebar_label: "Jest 29 to 30 Migration"
description: "Upgrade Jest 29 to 30 with a coding agent: migrate matcher aliases and CLI flags while preserving assertion intent, using NestJS as a reference."
keywords: ["Jest 30", "Jest migration", "AI coding agent", "test migration"]
sidebar_position: 45
tags: ["tutorial", "agent-engineering"]
---

# Migrating Jest29 to Jest30 With an Agent: A Structured Approach Using NestJS as a Reference

> If you're upgrading from Jest 29 to 30, don't treat this as a blind bump. Treat it as a deliberate refactor of your test harness. Use your coding agent as a co-pilot: give it the guide, your project, and explicit intent. This article shows how to do that systematically, using the concrete NestJS sample migration as a worked example.

This guide is written for developers who already run their tests with Jest 29, know what those test commands are doing, and want to upgrade to Jest 30 without losing the "meaning" of their assertions. "Meaningful," here, means:

- Preserving exactly what each test is checking (business expectations, not just syntax).
- Keeping argument values, counts, and call patterns intact.
- Maintaining test file scope and environment assumptions.
- Avoiding silent failures due to deprecated APIs or typing mismatches.

We'll walk through:

1. What actually changes in Jest 30 that can affect tests.
2. How to translate the official upgrade guide into your repository.
3. A concrete diff you can expect (NestJS sample).
4. A repeatable agent prompt strategy that keeps test intent intact.
5. Verification steps that match your actual CI and type-checking workflow.

---

## 1. What Jest 30 Changes That Matter to Your Tests

Based on the official upgrade guide and observed changes in real projects (including the NestJS sample), these are the areas where Jest 29 → 30 can impact behavior:

- Matcher names removed or canonicalized  
  - `toBeCalledWith` → `toHaveBeenCalledWith` (alias removed).
- CLI argument naming for path patterns  
  - `--testPathPattern` → `--testPathPatterns` (plural, more flexible).
- Node and TypeScript environment requirements  
  - Minimum Node: ~18.x  
  - @types/jest: requires TypeScript ≥5.4
- Type inference strictness in matchers  
  - Argument types inferred more precisely; non-enumerable property handling can change in some built-in helpers.

For most NestJS-style projects using Node environment tests, the critical deltas are:

- A few matcher aliases.
- CLI syntax for path patterns.
- Version compatibility (Node/TS/@types/jest).

Your coding agent should focus on these first; everything else is typically configuration or environment hygiene.

---

## 2. Turn the Upgrade Guide Into Project Actions

Instead of reading "upgrade guide" as a wall of text, translate it into project-level actions:

- Identify test files that use removed/changed matchers.
- Confirm your test command and path patterns in package.json.
- Validate Node, TS, and @types/jest versions against Jest 30 requirements.
- Decide whether ts-jest is tied to a specific major version or can stay pinned independently.

Concrete steps:

1. Open your `package.json` scripts:

   - Jest 29 pattern:  
     ```json
     "test": "jest --coverage --testPathPattern=\"unit/.*\""
     ```
   - Jest 30 pattern (equivalent):  
     ```json
     "test": "jest --coverage --testPathPatterns \"unit/.*\""
     ```

2. Check the Node and TS ecosystem in package.json:

   - Confirm TypeScript ≥5.4 if you use @types/jest types.

3. Locate matchers used in test files:

   - Search for `toBeCalledWith`, `toBeCalledTimes`, etc.
   - Replace deprecated names with their canonical form before running tests.

Use this as your "checklist" when prompting an agent or doing the work manually.

---

## 3. Concrete Example: NestJS Sample (05-sql-typeorm) Migration

The real-world patch from merged PR #15268 upgrades Jest 29.7.0 → 30.2.0 and @types/jest 29.5.14 → 30.0.0. It keeps test scope, arguments, and intent intact while applying minimal supported changes.

### 3.1. What the Diff Actually Looks Like

The core of the change is very small:

```diff
-expect(repoSpy).toBeCalledWith({ id: 1 });
+expect(repoSpy).toHaveBeenCalledWith({ id: 1 });

-expect(removeSpy).toBeCalledWith('2');
+expect(removeSpy).toHaveBeenCalledWith('2');
```

Why this matters:

- `repoSpy` spies on `repository.findOneBy`. The test checks that the service calls it with `{ id: 1 }`.
- `removeSpy` spies on `repository.delete`. The test checks that it's called with `'2'`.
- Changing `toBeCalledWith` → `toHaveBeenCalledWith` updates to the canonical matcher without altering:
  - The arguments being checked.
  - The number of calls expected.
  - The identity of the spies or their targets.

This is exactly what "preserving meaning" looks like in practice: a one-word update that aligns with Jest 30's API while keeping business expectations intact.

### 3.2. CLI and Path Pattern Changes


- Jest 29 example pattern:
  ```bash
  jest --testPathPattern="unit/.*"
  ```
- Jest 30 equivalent:
  ```bash
  jest --testPathPatterns "unit/.*"
  ```

Notes:

- `--testPathPatterns` is pluralized to support multiple patterns more naturally.
- This flag selects file paths, not individual tests inside files. It doesn't change test names or scopes—only which files Jest runs.

If your project's test script already uses a pattern like this, simply swap the flag name and keep the regex. That's it.

### 3.3. Node, Types, and Runner Compatibility

Key points from the NestJS example:

- Jest version: 30.2.0 (target).
- @types/jest: 30.0.0.
- ts-jest: 29.4.5 stays pinned.
- Environment: node (no JSDOM complications).

The takeaway:

- Jest and @types/jest must be compatible; they are version-coupled.
- ts-jest can remain on its own major line as long as it supports the current Jest runner API (which it does for 30.x).

---

## 4. How to Use a Coding Agent Without Losing Test Intent

Your agent is powerful, but "upgrade my project to Jest 30" is too vague. It will hallucinate changes or over-refactor. Give it the context and constraints that mirror what you've done above.

### 4.1. Minimal Effective Prompt

Here's a prompt structure that consistently yields high-quality migration diffs:

```text
You are assisting with migrating a Jest29 project to Jest30.

Context:
- Current versions: Jest 29.7.x, @types/jest 29.5.14
- Target versions: Jest 30.2.0, @types/jest 30.0.0
- ts-jest is pinned at 29.4.5 and should not be changed.

Goal:
- Apply the minimal changes required to run tests with Jest30 while preserving:
  - Test scope (file patterns, environments)
  - Assertion intent (arguments, counts, call order)
  - Business expectations expressed in test names and comments

Known official changes:
- Matcher alias: toBeCalledWith -> toHaveBeenCalledWith
- CLI path pattern flag: --testPathPattern -> --testPathPatterns
- Ensure @types/jest, TypeScript, and Jest are compatible.

Please provide:
1) A short "change map" listing files/types of changes expected.
2) The minimal diffs for the known issues (matchers, CLI).
3) Any behavioral differences that require judgment (e.g., stricter types).
4) A verification plan: which commands to run and what results to expect.

Keep the test logic itself unchanged unless an API is removed. Only update hooks, matchers, CLI args, and configuration to be Jest 30 compatible.
```

This prompt gives the agent:

- Concrete source/target versions.
- A clear scope (matchers + CLI + compatibility).
- Constraints on what not to touch (test logic, ts-jest pin).
- Deliverables that match your actual workflow.

### 4.2. What to Expect in the Agent's Output

A good response will include:

- A file list or glob pattern (e.g., all `*.spec.ts`, plus `package.json` scripts).
- Explicit replacements like:
  - `.toBeCalledWith` → `.toHaveBeenCalledWith`
  - `--testPathPattern` → `--testPathPatterns` in scripts.
- Notes on:
  - Any stricter TypeScript errors appearing after the upgrade (and whether they reflect real issues or just type annotation tightening).
  - Environment-specific notes if your project uses jsdom (not the case in the NestJS sample).

It should avoid:

- Refactoring test bodies.
- Changing spy names, arguments, or expected call counts.
- Adding unrelated tests or altering test organization.

---

## 5. Verification: Proving You Didn't Break Anything

Upgrading is half done once Jest runs again. The second half is confirming that:

- The same tests are discovered.
- The same assertions pass.
- Types and environments still align with your toolchain.

Here's a focused verification plan.

### 5.1. File Discovery (No Execution)

Use `--listTests` to confirm Jest discovers the same files:

```bash
npm test -- --listTests
# Direct Jest CLI invocation:
npx jest --listTests
```

Compare output before and after migration:

- Same file paths.
- Same glob patterns applied.
- No new "no tests found" gaps.

This step isolates path pattern changes from assertion behavior.

### 5.2. Type Checks

Run your project's type-check command (often `tsc --noEmit` or similar). After upgrading @types/jest:

- Expect some new errors if you had loose typing in tests.
- Distinguish:
  - Real issues (mismatched argument types, strictness violations).
  - Cosmetic warnings that are acceptable for your style.

If the agent suggests stricter annotations, review them against your codebase's conventions before accepting.

### 5.3. Execute Tests

Run the standard test command exactly as it is used in CI:

```bash
npm test
# or
npx jest --coverage
```

Check that:

- Execution time is stable (no new OOM or timeout issues).
- The same tests pass and fail as before (if any were expected to fail).
- No flaky failures appear only after the upgrade.

### 5.4. CI Integration

Update your CI config file (GitHub Actions, GitLab CI, etc.) if it explicitly lists Jest versions:

- Keep `npm ci` or `pnpm install` behavior unchanged.

Then run your CI pipeline on a fork or branch. If the job passes, you've verified that:

- The CLI invocation from CI works.
- Your environment matrix remains valid.

---

## 6. What "Preserving Meaning" Actually Looks Like

To close with a concrete lens: here's how to judge whether your migration preserved test intent.

For each test, ask:

1. What is it asserting about the system?
   - Example: "findOneBy is called with a single ID and returns exactly one user."
2. Are the check conditions still identical?
   - Same arguments, same counts, same order of calls?
3. Did we accidentally change the target?
   - E.g., switching from `toHaveBeenCalledWith` to something else?
4. Is the test scope unchanged?
   - Same file pattern, same environment (node vs jsdom), same runner?

In the NestJS example:

- Intent: "Service calls `repository.findOneBy({ id: 1 })`."
- After migration: Still checking that `repoSpy` is called with `{ id: 1 }`.
- The only change: `toBeCalledWith` → `toHaveBeenCalledWith`.

That's the gold standard: semantic equivalence, syntactic alignment.

---

## 7. Quick Reference Summary

- Jest version: 29.7.x → 30.2.0
- @types/jest: 29.5.14 → 30.0.0
- ts-jest: keep pinned (e.g., 29.4.5) if compatible
- Node: minimum 18.x
- TypeScript: ≥5.4 for @types/jest compatibility

Key diffs:

- Matcher alias:  
  - `toBeCalledWith` → `toHaveBeenCalledWith`
- CLI pattern flag:  
  - `--testPathPattern="..."` → `--testPathPatterns "..."`
- Verification order:
  1) `--listTests` (discover files)
  2) Type check (`tsc --noEmit` or project's equivalent)
  3) Run tests (same CI command)
  4) Confirm CI pipeline passes

---

## 8. Final Note for Project Owners

When you migrate:

- Don't treat Jest 30 as a "black box update."
- Use your agent with precise constraints and the canonical upgrade guide as ground truth.
- Validate at each step with commands that separate discovery, typing, and execution.

Follow this structured approach and your migration will be predictable, minimal, and faithful to what your tests are actually trying to prove.

## Sources

- [Official Jest30 upgrade guide](https://jestjs.io/docs/upgrading-to-jest30)
- [Jest29.7 CLI](https://jestjs.io/docs/29.7/cli) / [Jest30.0 CLI](https://jestjs.io/docs/30.0/cli)
- [NestJS migration PR #15268](https://github.com/nestjs/nest/pull/15268/files)
- [Pinned sample configuration](https://raw.githubusercontent.com/nestjs/nest/22e2b8cc4e832895d436a09da9d7407f30d42e92/sample/05-sql-typeorm/package.json)
- [ts-jest29.4.5 peer compatibility](https://raw.githubusercontent.com/kulshekhar/ts-jest/v29.4.5/package.json)
