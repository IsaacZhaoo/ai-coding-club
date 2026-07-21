---
title: "Spec-Driven Development with GitHub Spec Kit: From Requirement to Implementation"
description: "Learn a practical GitHub Spec Kit workflow from constitution and specification through plan, tasks, implementation, and human review gates."
keywords:
  - spec-driven development
  - GitHub Spec Kit
  - Spec Kit tutorial
  - specification driven development
  - AI coding workflow
sidebar_position: 14
tags: [tutorial, agent-engineering, workflow, spec-kit]
---

# Spec-Driven Development with GitHub Spec Kit: From Requirement to Implementation

*By Youguang · July 21, 2026*

---

## The Request That Sounds Done

A product manager sends a message: *"Add export to CSV."*

Three words. Feels clear. You assign it to the sprint, a coding agent picks it up, and forty minutes later a pull request arrives with a `toCsv()` function attached to the user table.

Then the review questions start.

Which users — all of them, or only the ones matching the current filter? Which fields — everything, or only what the export template shows? What happens when a field contains a comma, a newline, or a double quote? Is this a browser download, a server-generated file sent by email, or both? Does export respect row-level permissions? Does it appear in the audit log? Can a viewer role trigger it, or only admins? Is there a size limit before it becomes a background job?

None of those questions are hard. Every one of them has a right answer for your product. But the coding agent cannot find that answer in *"Add export to CSV."* It invents one — usually the locally-plausible one — and you discover the gap at review time, after the implementation is already written.

This is the real tension in agent-assisted development. It is not that agents write bad code. It is that implementation begins before the team has agreed what the code must *mean*. Spec-driven development addresses that gap by inserting a sequence of human-reviewed artifacts between the request and the first generated line.

GitHub Spec Kit is one concrete toolchain for that sequence.

---

## What Spec-Driven Development Actually Means

Spec-driven development is not a new idea. What changes with AI coding agents is the *cost asymmetry*: agents are very fast at producing code, but they have no way to surface ambiguity back to the human unless someone designs a process that forces the question. Without a gate, the path of least resistance is always to write something and see what breaks.

The core claim of spec-driven development is that durable artifacts — reviewed and approved before generation — are more valuable than iterated corrections after the fact. You do not have to agree with that claim for every task. A one-line bug fix probably does not need a specification document. But for anything involving an external interface, a permission model, an audit requirement, or a multi-step user journey, writing first and coding second tends to find problems earlier and cheaper.

GitHub Spec Kit operationalizes this as a layered artifact sequence: **constitution → specification → plan → tasks → implementation**. Each layer answers a different question at a different level of detail, and each is a review gate before the next one begins.

---

## The Artifact Layers

Understanding the layers is more important than any individual command, so it is worth being precise about what each one is for.

| Artifact | Question it answers | Who reviews it | When it changes |
|---|---|---|---|
| **Constitution** | What are our invariants and non-negotiable constraints for this project? | Technical lead, architect | Rarely; it is a project-level covenant |
| **Specification** | What exactly does this feature do, for whom, under what conditions? | Product + engineering | Before any implementation begins |
| **Plan** | How will we build it — which components, which approach, what are the trade-offs? | Engineering | After spec is approved |
| **Tasks** | What discrete, independently reviewable units of work exist? | Engineer or lead | After plan is approved |
| **Implementation** | The code that satisfies the tasks | Reviewer | After tasks are approved |

The key insight is that the constitution and specification are *product review objects*, not engineering documents. They use language a product manager or designer can audit. The plan and tasks are *engineering review objects*. Implementation is last, not first.

This ordering does not mean you must complete all five stages for every change. It means you decide up front which stages a given change requires, and you do not skip a stage silently.

---

## Installing Specify CLI

GitHub Spec Kit's CLI is called `specify`. The officially recommended installation route uses [`uv`](https://docs.astral.sh/uv/), the fast Python package manager:

```bash
# Official installation route (requires uv)
uv tool install specify-cli
```

If `uv` is available in your environment, this is the cleanest path — no virtual environment management, no pip, no version conflicts.

**Tested fallback:** In my environment, `uv` was not available, so I used a direct Python venv instead. This worked correctly and is a reasonable alternative if `uv` is absent:

```bash
python -m venv .venv
source .venv/bin/activate
pip install specify-cli==0.13.0
specify --version
```

At the time of testing (July 21, 2026), the latest observed release was **v0.13.0** (released 2026-07-17). Verify the current release at [github.com/github/spec-kit](https://github.com/github/spec-kit) before following these steps, since the version number in `pip install` may need to be updated.

Either route gives you the `specify` command. The rest of this tutorial applies identically regardless of which installation path you chose.

---

## Initializing a Project

Once `specify` is available, you initialize a new Spec Kit workspace with `specify init`. This command generates the project scaffold.

The command I tested:

```bash
specify init spec-kit-scratch-20260721 \
  --integration codex \
  --script sh \
  --ignore-agent-tools
```

**Flags explained:**

- `spec-kit-scratch-20260721` — the project name; used as a slug in generated file paths.
- `--integration codex` — configures the generated skill files for GitHub Codex rather than another agent runtime.
- `--script sh` — generates shell scripts (as opposed to PowerShell or other targets).
- `--ignore-agent-tools` — skips generation of tool manifests that some agent runtimes need; useful if you want a minimal scaffold first.

This command succeeded. I confirmed these generated categories:

```
spec-kit-scratch-20260721/
├── constitution, spec, plan, and tasks templates
├── generated shell workflow scripts
├── workflow registry metadata
└── Codex integration with ten generated Spec Kit skills
```

The ten generated Spec Kit skills are the most interesting part of the scaffold. Codex invokes them with `$speckit-*` names, but `$` is invocation syntax rather than part of the filesystem name. Their workflow instructions can be inspected as text.

I inspected the generated constitution, specification, plan, and tasks templates. They are distinct review artifacts rather than one generic planning document. Exact fields are version-sensitive, so inspect the generated version before adopting it as team policy.

---

## Walking the Workflow: A Small Feature Example

The following traces how the `$speckit-*` sequence is *documented* to work for a concrete feature. I am using the CSV export scenario from the opening as the running example. **This section describes the official workflow as specified in the project documentation, not a sequence I personally executed end-to-end.** My direct testing covered installation and initialization only.

### Step 1 — Constitution check

Before writing any feature spec, you open `constitution/CONSTITUTION.md` and confirm whether your feature touches any existing invariant. For CSV export, you are looking for clauses about data-handling, permission propagation, and audit logging. If a relevant invariant is not yet in the constitution, this is when you add and get it reviewed.

A constitution entry for this feature might look like:

```markdown
## Data Export
- All export operations must propagate the requesting user's row-level
  permission context. No export may surface rows the user could not
  see in the UI.
- Exports of more than 10,000 rows must be processed asynchronously
  and delivered via the notification system, not a synchronous response.
- All export events are audit-logged with: user_id, timestamp, filter
  state, row count, and export format.
```

Adding this to the constitution means that every future feature touching export — not just this one — inherits these constraints automatically.

### Step 2 — Specification (`$speckit-specify`)

The spec answers: *what does this feature do?* It is written before any architecture discussion.

```markdown
## Feature: Export filtered users to CSV

**User story**: As an admin, I can export the currently-filtered user
list to a CSV file so that I can perform offline analysis or import
the data into a third-party tool.

**Acceptance criteria**:
1. The export button appears only for users with role: admin or
   role: data-analyst.
2. The exported file contains only rows matching the active filter
   state at the time the button is clicked.
3. Exports of ≤ 10,000 rows are delivered as a browser download
   within 5 seconds.
4. Exports > 10,000 rows trigger a background job; the user receives
   a notification with a download link when ready.
5. CSV fields: user_id, email, display_name, role, created_at,
   last_active_at. No password hashes or internal keys.
6. Commas, double quotes, and newlines in field values are escaped
   per RFC 4180.
7. Every export event is written to the audit log before the
   response is returned.

**Out of scope**: Excel format, scheduled recurring exports, export
of non-user entities.
```

This document gets a product review. The product manager confirms the role list, the field set, the async threshold, and the out-of-scope boundary. The document does not mention any database tables, API routes, or code files. Those belong in the plan.

### Step 3 — Plan (`$speckit-plan`)

The plan answers: *how will we build it?* This is the first engineering document.

```markdown
## Implementation approach

**API**: Add `GET /api/users/export` accepting the same filter
parameters as `GET /api/users`. Returns a CSV stream for small
exports; returns 202 Accepted with a job_id for large ones.

**Permission check**: Middleware reads requesting user's role before
any data access. 403 if role is neither admin nor data-analyst.

**Row-level filter**: Re-uses `UserQueryBuilder` with the same
filter state serialization already in use for pagination.

**Async path**: Large exports enqueue a Sidekiq job. Job writes to
object storage, then calls `NotificationService.deliver`.

**Audit log**: `AuditEvent.record(:export, ...)` called inside a
DB transaction wrapping the data access.

**Trade-offs considered**: Streaming versus buffering for small
exports. Decision: buffer (simpler error handling, acceptable for
≤ 10 k rows). Revisit if threshold rises.
```

The plan goes to engineering review. The architect confirms the approach is compatible with the existing infrastructure, does not introduce new dependencies unexpectedly, and respects the constitution constraints.

### Step 4 — Tasks (`$speckit-tasks`)

Tasks slice the plan into independently reviewable units. The `$speckit-tasks` skill is documented to generate this slice given the approved plan.

```markdown
- [ ] T-01: Add permission middleware for /api/users/export
- [ ] T-02: Implement UserQueryBuilder.to_csv(filter_state)
- [ ] T-03: Implement synchronous export endpoint (≤ 10 k rows)
- [ ] T-04: Implement async export job and object storage write
- [ ] T-05: Wire 202 Accepted response and job_id return
- [ ] T-06: Implement NotificationService call on job completion
- [ ] T-07: Add AuditEvent.record to export path (sync + async)
- [ ] T-08: Write acceptance tests covering all 7 spec criteria
- [ ] T-09: Update API documentation
```

Each task is small enough that a reviewer can evaluate it without understanding the full feature. T-01 can be reviewed by someone who knows nothing about CSV formatting. T-07 can be reviewed by someone focused entirely on the audit requirement.

### Step 5 — Implementation (`$speckit-implement`)

Only now does the coding agent write code — one task at a time, with the constitution, spec, and plan available as context. The agent is not guessing what "export" means. It has a spec with seven numbered acceptance criteria, a plan with an explicit API contract, and a constitution clause about audit logging. The implementation decisions were made in review, not in generation.

Spec Kit provides analysis and checklist commands for reviewing consistency and requirements quality. The exact point at which a team runs them is a workflow decision; this article did not test post-task automation.

---

## Where to Put the Human Checks

The workflow has four natural points where a human review gate is necessary. These are not optional courtesies — they are the mechanism by which the process works.

**Gate 1: Constitution (before spec)** — Is the feature compatible with our existing invariants? Does it require a new invariant? This review prevents the spec from being written on a false premise.

**Gate 2: Spec (before plan)** — Does the product behavior described match what we actually want? Are the acceptance criteria testable? Is the out-of-scope list realistic? A spec that is approved here constrains everything downstream.

**Gate 3: Plan (before tasks)** — Is the engineering approach sound? Does it introduce unacceptable dependencies or violate the constitution? This is where architecture review happens.

**Gate 4: Task slice (before implementation)** — Are the tasks genuinely independent? Is anything missing? Can each task be reviewed in isolation? A poor task slice leads to reviewers who cannot evaluate individual PRs without holding the entire feature in their heads.

Optional Spec Kit skills can support clarification and cross-artifact analysis between these gates. Check the generated skill list for the installed version rather than assuming a fixed command set.

---

## When This Is Too Heavy

Spec-driven development at the full five-layer depth is not appropriate for every change. Applying it universally will produce bureaucratic friction without proportional benefit.

**Use the full sequence when:**
- The feature has an external API contract or a documented schema.
- Multiple roles or permission levels are involved.
- Audit or compliance requirements apply.
- The feature is large enough that it will be reviewed in parts.
- The product behavior is genuinely uncertain and product review is needed before engineering begins.

**Use a lighter subset when:**
- The fix is internally contained with no user-visible behavior change — a spec and tasks may be sufficient, skipping the plan.
- The feature is a pure visual change with no logic — a spec with acceptance criteria is probably enough.
- The change is a one-line bug fix with a clear reproduction case — a task and test are appropriate.

You can use `$speckit-specify` to create a specification without immediately completing the rest of the sequence. The value is in the disciplines the artifacts enforce — explicit acceptance criteria, out-of-scope declarations, and reviewable decisions — not in the number of documents you produce.

A practical middle path for small features: write a spec with acceptance criteria, get a single product review, skip the plan and go straight to tasks. You still catch the "which users, which fields, which permissions" questions before the agent starts writing.

---

## Failure Modes to Watch

**The spec that describes the implementation.** A spec should describe behavior, not code. If your spec mentions database tables, class names, or method signatures, it has crossed into plan territory and lost the ability to be reviewed by non-engineers.

**The constitution that is never updated.** A constitution that does not reflect your current architecture becomes a lie. Schedule a quarterly review or update it when a plan contradicts it.

**Tasks that are too large.** A task that takes three days to implement cannot be reviewed independently. If a reviewer needs to understand six other tasks to evaluate one, the slice is wrong.

**Spec drift.** Implementation details discovered during coding sometimes reveal that the spec was wrong. The correct response is to update the spec, get a re-review, and record the change. Use the analysis and review tools available in the installed version to surface drift.

**Using the scaffold without the reviews.** The templates and skills only work if humans actually read and approve the artifacts at each gate. If the process becomes "generate a spec, mark it approved, generate code," you have added ceremony without adding clarity.

---

## What I Verified, What I Did Not

For honesty about the evidence base: I installed `specify-cli==0.13.0` in a Python venv, ran `specify init` with the flags above, and examined the generated scaffold. The artifact structure, the ten skill files, and the template content are all based on direct observation.

The `$speckit-*` workflow sequence described in steps 1–5 is drawn from the official documentation in [github/spec-kit](https://github.com/github/spec-kit) and its `spec-driven.md`, plus the skill file content in the generated scaffold. I did not personally complete a full specify → plan → tasks → implement cycle on a real feature. The CSV export example is a hypothetical constructed to illustrate the workflow, not a record of an actual run.

Claims I am not making: that this toolchain has been validated in production at scale, that it eliminates rework, or that any team has measurably improved throughput using it. Those claims require evidence I do not have.

---

## References

- GitHub Spec Kit source and documentation: [github.com/github/spec-kit](https://github.com/github/spec-kit)
- Spec-driven development guide: `spec-driven.md` in the repository above
- `uv` installation: [docs.astral.sh/uv](https://docs.astral.sh/uv/)
- specify-cli on PyPI: [pypi.org/project/specify-cli](https://pypi.org/project/specify-cli)
- RFC 4180 (CSV format): [tools.ietf.org/html/rfc4180](https://tools.ietf.org/html/rfc4180)

---

*The gap between "what we requested" and "what we agreed on" is where most rework originates. Spec-driven development does not close that gap by generating better code. It closes it by making the agreement visible, reviewable, and persistent before the first line is written. GitHub Spec Kit gives that sequence a concrete scaffold. Whether the full five layers or a lighter subset is appropriate depends on what your feature actually touches — but the discipline of writing acceptance criteria before writing code is worth considering regardless of the toolchain.*

## Related Guides

- [AI Code Review Workflow](/docs/tutorials/ai-code-review-workflow/)
- [AGENTS.md Guide](/docs/tutorials/agents-md-guide/)
