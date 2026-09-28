---
title: "Practical Security Audit with Cloudflare's Skill"
sidebar_label: "Cloudflare Security Audit Skill"
description: "Run a scoped audit with Cloudflare Security Audit Skill, read confirmed and unresolved findings, and turn evidence into a focused repair task."
keywords: ["Cloudflare Security Audit Skill", "AI security audit", "coding agent security", "security audit reports"]
sidebar_position: 41
tags: [tutorial, security, agent-engineering]
---

# Practical Security Audit with Cloudflare's Skill

This tutorial guides you through a scoped security audit using the `cloudflare/security-audit-skill`. It explains how to invoke the workflow, interpret the verdicts, and turn confirmed findings into repair tasks. It assumes you have:

- A local project in version control
- A coding agent with tool use and parallel sub-agent support
- Node.js runtime installed (required by the included validators)

## Why Use This Skill

You want a structured security review that:

- Scopes cleanly (paths, subsystems, or commit ranges)
- Distinguishes confirmed vulnerabilities from speculative leads
- Produces artifacts you can inspect without digging through raw agent chatter

This skill orchestrates isolated agents through reconnaissance → hunting → validation → reporting, and provides clear verdicts instead of vague “possible issues.”

## Installation and Setup

### Install the Skill

From your target project directory:

```bash
npx skills add https://github.com/cloudflare/security-audit-skill --skill security-audit
```

Use `--global` if you want it available across projects:

```bash
npx skills add https://github.com/cloudflare/security-audit-skill --skill security-audit --global
```

### Requirements

- A coding agent that supports:
  - Natural-language task understanding
  - Tool use
  - Parallel sub-agents
- Node.js runtime (used by the two zero-dependency validators in the workflow)

The skill installs a workflow. It does not bundle a full deployment environment, nor a sandbox; it assumes you can run agents locally or via an existing host setup.

## Modes and Profiles

Cloudflare Security Audit Skill operates in two primary modes, chosen by how explicitly you phrase your request to the coding agent:

**Guidance Mode**  
Focused advice on a security question or specific vulnerability. If you ask “How might an attacker bypass rate limiting in this middleware?” or “What’s the risk of this config?”, the skill responds with targeted reasoning and code suggestions. Guidance mode does not automatically create an audit output directory or a formal report suite.

**Full Audit Mode**  
Full audit applies only to explicit codebase audits, comprehensive reviews, or requests for audit report artifacts; merely mentioning review scope does not automatically select full mode. A focused security question remains guidance unless a full audit is explicitly requested.

Three audit profiles are available. Scoping, profile, and output location are all specified in the natural-language task to the agent; there is no separate CLI command beyond installation.

- **Quick** – A shallow but structured scan: one hunter wave, one final coverage critic, one fresh verifier per candidate for both validation and record checking. Suitable for fast triage or when you need a baseline signal. It remains partial coverage.
- **Standard (default)** – Balanced depth across reconnaissance, hunting, verification, and reporting without heavy redundancy. Good for most routine audits of small to medium repositories.
- **Deep** – More thorough candidate validation and final record checks, with stronger redundancy and cross-checking. Use when the repository is higher-risk or has complex auth/streaming paths.

Profile choice adjusts breadth and redundancy; it does not change the core evidence standard or the sandbox behavior.

## Running a Scoped Audit: A Natural-Language Example

To get a concrete result without extra setup, write your audit request as a single clear prompt inside your agent session. The skill is already installed via `npx skills add` in the previous section; no additional CLI run command is needed.

Copy this example, adapt repo and path names, and paste it directly into your agent:

```text
Run a scoped security audit on my Node.js repository.

Scope:
  - Focus areas: access control logic in src/auth and API routing/validation in src/api.
  - Include dependency and middleware chains that touch these modules.

Profile:
  - Use the "quick" profile for speed, but ensure all standard report artifacts are generated.

Output location:
  - Write results to a fresh external directory: ~/audits/my-project-auth
  - Ensure the directory is new and not tracked by version control.

Execution details:
  - Record the current commit hash and working-tree changes at audit start.
  - Verify that the audit scope (src/auth, src/api) was actually examined in the output.
  - Note any unfinished or conditional checks (e.g., build-time flags, environment-dependent code).

Assume I'm using an agent with tool use and parallel sub-agents. Provide a clear summary plus all standard artifacts.
```

When executed, the agent will:

- Create `~/audits/my-project-auth` as the run directory.
- Record metadata (commit, tree state, scope).
- Produce standard artifacts (see next section).
- Return structured findings with enough detail for immediate remediation in your small repo.

## Phases and How They Fit Together

The six phases involve coding agents performing source analysis, hunting, and factual verification, while scripts handle mechanical format and ledger checks.

1. **Reconnaissance**  
   Maps code structure: key modules, trust boundaries, input surfaces (CLI, HTTP, API routes), and existing coverage. Produces an initial layout of where to hunt.

2. **Coverage-Led Hunting**  
   Uses the reconnaissance map to drive targeted checks: auth flows, data validation, crypto usage, environment config, event loop issues, etc. Candidates are formed here based on patterns or known risks.

3. **Fresh Candidate Verification**  
   Each candidate claim is attempted to be disproven with concrete tests and static/code-path checks. This phase validates evidence before it reaches reports.

4. **Structured Records and Mechanical Validation**  
   Audit findings are normalized into machine-checkable records. Node.js scripts validate format and ledger consistency; they do not decide whether a vulnerability is true, only that the documentation matches the rules.

5. **Fresh Independent Checking**  
   A second pass of independent verification over final source observations, impact assessment, and proposed remediation steps. Ensures no hallucinated or stale conclusions slip through.

6. **Reports Derived from Records**  
   Human-readable artifacts are generated from validated records: high-level summaries, detailed findings, architecture notes, and validation status.

Quick combines phase 3 and 5 responsibilities under one fresh independent verifier while phase 4 remains distinct. Target-controlled execution requires sandbox controls, but the parent/agent reporting process does not run inside that sandbox.

## Understanding Verdicts: The Most Important Part

When you finish a Cloudflare security audit, don’t panic at the number of statuses in your reports. They’re just labels for how much we know about a claim. Think of each status as a decision point on a checklist:

- **confirmed**
  - We have a complete trace from source to observed behavior.
  - We see a clear condition and a bounded result that matches the rule being tested.
  - This is your repairable finding.

- **needs_validation**
  - A solid, source-grounded lead exists: we know what we’re missing and how to check it.
  - There is an exact, actionable validation plan.
  - No severity is implied; treat it as a “do more work” flag until the piece is pinned down.

- **rejected**
  - A claim that was disproved by looking at the source, actual behavior, or an existing control.
  - Rejected records remain in findings.json; the main report may reference their fingerprints only to explain prior disagreements or coverage decisions.
  - This is not a bug; this is evidence that your current design already handles the concern (or the claim was wrong).

A file location alone, a static dependency graph, or even a plausible code snippet do not prove a confirmed boundary failure. Only when you can say “given X, the system does Y” with evidence tied to source and conditions do you move a record into confirmed.

## Reading the Reports: What to Inspect

Begin with the three human-readable reports (REPORT.md, FINDINGS-DETAIL.md, NEEDS-VALIDATION.md) while using findings.json and coverage-ledger.json as the underlying records and coverage source.

1. **REPORT.md**
   - The executive summary: profile used (quick/standard/deep), scope, and coverage notes.
   - REPORT.md identifies run-level source reference/completion status and presents confirmed findings in its own section.
   - A separate table for needs_validation items with their blockers and plans.
   - Hardening notes that describe recommended improvements not tied to a specific rejected claim.
   - Coverage summary: what was covered and what remains unresolved or out-of-scope.

2. **FINDINGS-DETAIL.md**
   - Expands only the confirmed medium/high/critical records.
   - For each, you’ll find deeper evidence tied to its source and observed behavior.
   - Low-severity confirmed records don’t always have a detail entry; they live in REPORT.md/findings.json.

3. **NEEDS-VALIDATION.md**
   - The unresolved backlog: each record lists the evidence you have, the precise blocker, and an applicable validation plan (often local or owner-observed).
   - This is your roadmap for turning “needs_validation” into “confirmed” or “rejected”.

Use REPORT.md as your navigation map. Start there to see what’s confirmed, what needs work, and what you can safely close. Use FINDINGS-DETAIL.md when a confirmed item will drive a repair task. Use NEEDS-VALIDATION.md to plan the next verification runs.

## From Finding to Repair Task

A repair task is not just “fix this line.” It’s a closed loop that ties source, conditions, observed behavior, and regression cases together. Here’s how to construct one:

- Start with a confirmed record in REPORT.md or findings.json.
- If it’s medium/high/critical, open its detail entry in FINDINGS-DETAIL.md for the full evidence chain.
- Extract the five core elements that define the repair:
  - **Source path** where the logic lives (e.g., a handler, middleware, or config).
  - **Actual conditions** under which the failure is reproduced.
  - **Bounded observed result**: precisely what happens when those conditions are met.
  - **Smallest effective source change**: the minimal code/config tweak that prevents the result while preserving expected behavior.
  - **Regression case**: a concrete test scenario that must continue to pass after the fix.

Example of the repair loop:

1. Pick one confirmed finding.
2. Read its source path and conditions; ensure you can run the same bounded scenario in your environment.
3. Propose the smallest change that enforces or corrects the expected rule on that exact path.
4. Define a regression test (or checklist) that proves the fix holds when the original conditions reappear.

If the finding is low severity, you may skip a detailed entry but still apply this loop. If you’re unsure whether a record should be confirmed, check NEEDS-VALIDATION.md first: there may already be a validation plan that converts it cleanly.

## Practical Example: Tracing an Access-Control Claim

Imagine a simple rule: “Objects owned by user B must be hidden from any user who is not B.”

Scenario:

- Dummy user A has a valid authenticated session.
- Object “obj-99” is owned by B and marked private under the application’s access rule.
- The read handler accepts an object_id, fetches the object, and passes it downstream without re-checking ownership against the current principal.
- A bounded local execution shows A successfully reading obj-99’s full content.

How this becomes a confirmed finding:

- We identify the read handler (source path).
- We define conditions: authenticated as A, reading obj-99 owned by B.
- We observe: A receives private content without being blocked or prompted.
- Together, these trace and result support confirmation that access control is not enforced on this path.

What doesn’t count as confirmation:

- Just seeing A read a public profile.
- Just knowing the rule exists in a config file.
- Just reviewing code that “looks” like it checks ownership, without running the bounded scenario.

The repair task:

- For objects that may be read only by the owner, enforce that the authenticated principal is the object's owner on that same read path before private content is returned.
- Make sure the check happens at the point where the object is selected or before it’s returned to the user.
- Add a regression case that verifies:
  - A can read their own objects.
  - A is denied B’s private objects.
  - Unauthenticated requests are handled according to the access rule (blocked or redirected).

Note what’s irrelevant to authorization:

- Checking whether the user exists or is active.
- Validating that the object_id falls within a known range.
- These are sound identity and data-quality checks, but they do not establish ownership authorization on their own.

## Handling Execution and Reproduction Limits

Before executing target-controlled builds, tests, or reproductions, the host must supply an OS-enforced sandbox with external networking disabled, allowing only isolated loopback for local client/server checks. Installing the skill alone does not configure these controls.

### Host-Controlled Sandbox Entry

- **Clean environment:** Populated from an explicit allowlist of safe variables; no random env pollution.
- Target and toolchain run in read-only mode; target-controlled processes write only to their assigned scratch directory, never to shared reports or retained artifacts.
- Explicit limits apply to CPU, memory, concurrent processes, file size, disk usage, and wall-clock time per target session.
- Use dummy principals, resources, and non-secret fixture data throughout all checks.
- **Disposable copies:** If a build step requires adjacent writes (e.g., caching or temporary compilation artifacts), a disposable source copy can be created in scratch.

Output organization:

- Full audit default output: `~/security-audit-skill/<repo-name>/run-<N>`, where `<N>` is the next unused integer.
- An internal directory is allowed only when explicitly selected and verified to be fully ignored by version control (e.g., added to `.gitignore`).
- Using a named external directory (like `~/audits/my-project-auth`) creates a fresh, isolated run directory that does not interfere with your repo.

Shared artifacts produced by the audit:

- `run-metadata.json`: run metadata
- `architecture.md`: architecture snapshot
- `coverage-ledger.json`: checks and coverage
- `findings.json`: verdict-specific records
- `REPORT.md`: scope, confirmed findings, needs validation, and coverage summary
- `FINDINGS-DETAIL.md`: confirmed medium/high/critical details
- `NEEDS-VALIDATION.md`
  - The unresolved backlog: each record lists the evidence you have, the precise blocker, and an applicable validation plan (often local or owner-observed).

If required sandbox controls are unavailable, do not execute the target code. Retain a source-grounded lead with its exact needs_validation blocker and a safe validation plan for owner inspection, avoiding live audit probes.

## Deciding What to Fix vs. What to Keep Open

Not every finding demands an immediate fix. Use these rules:

**Fix now:**

- Confirmed medium/high/critical findings that directly enable unauthorized access, data leakage, or unsafe operations.
- Any confirmed item with a clear, low-effort source change and a well-defined regression case.

**Keep as needs_validation:**

- Preserve a source-grounded lead with a precise missing runtime or deployment fact.
- Ask the owner to inspect the relevant configuration, identity, or route.
- Apply an applicable bounded local plan once controls are available; keep unresolved records without a severity field and avoid new live traffic experiments.

**Reject safely:**

- A downstream function already enforces the correct ownership rule on the same unavoidable path; your evidence shows the data flows through that enforcement point.
- The behavior you saw matches an expected control (e.g., a rate limiter or header policy) and your claim was misstated.
- Use source and bounded behavior to close the loop: “Given X, the system does Y via Z.”

**Rerun hygiene:**

- If you change source code or configuration, revalidate any affected confirmed records; do not assume prior evidence still holds.
- Unchanged confirmed records can reuse eligible evidence after current source and conditions checks, but each carried record still follows the current independent verification path. Prior unresolved records remain active work items.
- Blocked/deferred/out-of-scope items in coverage-ledger.json remain on your backlog; a past clean pass is never proof of complete or ongoing coverage.

## When to Run This vs. Broader Harnesses

Cloudflare’s blog describes an evolution from single-repository skills into an enterprise vulnerability harness that connects cross-repository pipelines and policy checks. That cross-repository orchestration belongs in the later harness, not this skill.

For most individual projects and teams:

- This audit skill is the right granularity: scoped, artifact-rich, and lightweight.
- You can layer it on top of policy engines, CI gates, or a larger harness once you’re ready.

## Bottom Line

Treat the audit as a set of evidence-driven decisions:

- **confirmed** = repairable, bounded failure supported by source and observed result.
- **needs_validation** = credible lead with an exact missing fact and a concrete validation plan.
- **rejected** = disproved claim; often useful to reference its fingerprint when explaining coverage choices or past disagreements.

Use REPORT.md to pick your next target, FINDINGS-DETAIL.md to understand the mechanics, NEEDS-VALIDATION.md to plan your next verification step, and then turn one supported issue into a tight repair task: source path, conditions, observed result, minimal fix, and regression case.

---

- [Official Repository](https://github.com/cloudflare/security-audit-skill)
- [Workflow Definition](https://github.com/cloudflare/security-audit-skill/blob/main/skills/security-audit/SKILL.md)
- [Validation & Reporting](https://github.com/cloudflare/security-audit-skill/blob/main/skills/security-audit/VALIDATION-AND-REPORTING.md)

## Related Tutorials

- [Coding Agent Sandbox Security](/docs/tutorials/coding-agent-sandbox-security/)
- [AI Code Review Workflow](/docs/tutorials/ai-code-review-workflow/)
