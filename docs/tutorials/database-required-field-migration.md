---
title: "Using an AI Coding Agent for Safe, Phased Column Migration in Production PostgreSQL 18"
sidebar_label: "PostgreSQL Required-Field Migration"
description: "Plan a phased PostgreSQL 18 required-field migration with an AI coding agent, covering existing rows, older application versions, validation, and rollback."
keywords: ["PostgreSQL 18", "database migration", "NOT NULL", "AI coding agent"]
sidebar_position: 46
tags: ["tutorial", "agent-engineering"]
---

# Using an AI Coding Agent for Safe, Phased Column Migration in Production PostgreSQL 18

When you add a required field to an existing table in production—especially while older application versions are still deployed—the danger isn’t just locking the database. It’s letting some write path slip through with incomplete data, or tightening a constraint before every writer has been upgraded and the old data is corrected.

This guide shows you how to instruct an AI coding agent (or yourself) to plan and execute this migration as a coherent, phased workflow: add the column, preserve existing data, backfill in bounded batches, tighten the constraint safely, and embed explicit rollback paths. You’ll get a concrete task package you can paste into a coding assistant and immediately turn into production-ready SQL and checks.

---

## TL;DR

- Add `billing_email` as nullable first, so old deployments don’t break.
- Backfill in small, idempotent batches using `WHERE billing_email IS NULL` plus `FOR UPDATE`.
- Keep a compatibility read path (`COALESCE(billing_email, email)`) until every writer is migrated.
- Give your agent: current schema, all write entry points, business rules, deployment order, and acceptance criteria.

---

## The Problem (in One Sentence)

You need to enforce a new `billing_email` field on an existing `customers` table while some application versions still omit it during inserts/updates.

If you rush this with naive DDL or blanket updates, you risk:
- Data loss from incorrect mass updates.
- Deployment failures from premature `NOT NULL` constraints.
- Silent corruption where one write path updates a row without the new field.

The solution is to treat schema evolution as a multi-phase deployment artifact, not a single SQL command.

---

## 1. Schema and Business Rules (For the Agent)

### Existing table (PostgreSQL 18)

```sql
CREATE TABLE customers (
    id       BIGINT PRIMARY KEY,
    email    TEXT NOT NULL
);
```

### New column

- Name: `billing_email`
- Type: `TEXT`
- Nullable initially.
- After migration, it must be `NOT NULL`.

### Business rule

- For existing rows where `billing_email IS NULL`, the initial value will be set to that row’s `email` during backfill.
- After that:
  - New inserts must provide `billing_email`.
  - Existing non-NULL values are preserved unless explicitly updated.
- The mapping “initial billing_email = email” is a business decision; the agent should document it clearly and treat it as a one-time initialization rule, not a permanent schema identity.

---

## 2. Phase Overview

Think of this as a deployment plan your AI agent can propose and you can review step-by-step:

1. Add nullable column (no data change).
2. Preserve backward compatibility in code and reads.
3. Identify and kill all “hidden” write paths that bypass normal validation.
4. Backfill in bounded batches.
5. Tighten the constraint via NOT VALID → VALIDATE → SET NOT NULL.
6. Remove nullable safety nets and finalize cleanup.

Each phase has:
- Preconditions (what must be true before starting).
- Operations (SQL/code changes).
- Acceptance criteria (how to verify success).
- Rollback / pause criteria.

---

If every old row and every new INSERT truly should share a single non-NULL business default, you can take a simpler path: add the column with NOT NULL and a constant DEFAULT. For example, to `ALTER TABLE support_tickets ADD COLUMN status text NOT NULL DEFAULT 'open';`, assuming all tickets should be open by default. Explicit NULL never triggers that DEFAULT; omitting the column in an UPDATE leaves it unchanged, not reset to the default. A constant DEFAULT avoids physically updating every existing row when the column is added, though DDL locks still apply. This pattern does not work for billing_email without a staged migration because each row must be initialized with its own email value—DEFAULT expressions cannot reference other columns in the same row.

## 3. Phase 1: Add the Nullable Column

### Goal

Introduce `billing_email` without breaking existing inserts/updates. This ensures deployments running old code still succeed.

### DDL

```sql
ALTER TABLE customers ADD COLUMN billing_email TEXT;
```

During the nullable expansion phase, write compatibility is preserved through careful use of NULL. Old INSERT statements may omit billing_email; PostgreSQL stores NULL for those rows without error. Similarly, if an UPDATE does not specify that column, its current value remains unchanged. However, before you backfill data and tighten constraints, every existing writer—whether application code, background workers, import scripts, or external feeds—must be upgraded or retired in practice, not just documented or scheduled for later. New writers should always provide billing_email on INSERTs, and preserve any existing non-NULL value unless deliberately changed.

### Compatibility for old code

Until every writer is upgraded:
- Keep `billing_email` nullable.
- Do not add foreign keys, CHECK constraints, or `NOT NULL` yet.
- Consider adding a view or accessor that normalizes reads:

```sql
-- Example compatibility read helper (application-level logic, not schema)
-- SELECT COALESCE(billing_email, email) AS billing_address FROM customers;
```

### Acceptance criteria

- Existing application deployments can still insert/update `customers` without error.
- New inserts that omit `billing_email` store NULL (allowed temporarily).
- No DDL locks block long enough to cause deployment stalls (verify with `pg_locks`).

---

## 4. Phase 2: Identify All Write Paths

Before any backfill or constraint tightening, your agent must map every place that writes to `customers`.

### Why this matters

- A single overlooked script, cron job, import tool, or batch API can:
  - Fail catastrophically when constraints are enforced.
- This phase is about inventory and kill-switching, not schema changes.

### Things to ask the agent (or your team)

- List all components that ever INSERT/UPDATE `customers`:
  - Application services and background workers.
  - Import/EAV tools, migration scripts, data pipelines.
  - External services via API (webhooks, nightly loaders).
- For each:
  - Does it currently supply `billing_email`?
  - Can it be temporarily disabled or patched?
  - Is there a “bypass” path (e.g., bulk load, direct SQL)?

### Practical tactics

- Run queries to spot recent writes outside of the main app:
  - Check `pg_stat_activity` for long-running transactions touching `customers`.
  - Audit logs for direct connection usage.
- Temporarily enforce logging at the DB level:
  - Use triggers or audit tables (if not already present) to flag unexpected NULLs after Phase 3.

### Acceptance criteria

- A clear inventory list is produced and reviewed.
every existing writer—whether application code, background workers, import scripts, or external feeds—must be upgraded or retired in practice, not just documented or scheduled for later.

---

## 5. Phase 3: Bounded Backfill of Existing Rows

During the nullable expansion phase, write compatibility is preserved through careful use of NULL. Old INSERT statements may omit billing_email; PostgreSQL stores NULL for those rows without error. Similarly, if an UPDATE does not specify that column, its current value remains unchanged. However, before you backfill data and tighten constraints, every existing writer—whether application code, background workers, import scripts, or external feeds—must be upgraded or retired in practice, not just documented or scheduled for later. New writers should always provide billing_email on INSERTs, and preserve any existing non-NULL value unless deliberately changed.

### Design principles

- Idempotent: running the batch multiple times never corrupts data.
- Bounded: fixed LIMIT per batch to avoid runaway CPU/locks.
- Protected: only update rows where `billing_email IS NULL`.
- Lock-aware: use `FOR UPDATE` within short-lived transactions.

### Batch backfill SQL

Run this repeatedly until no rows remain:

```sql
WITH batch AS (
  SELECT id
  FROM customers
  WHERE billing_email IS NULL
  ORDER BY id
  LIMIT 1000
  FOR UPDATE
)
UPDATE customers AS c
SET billing_email = c.email
FROM batch AS b
WHERE c.id = b.id AND c.billing_email IS NULL;
```

Notes:
- `FOR UPDATE` locks selected rows for that transaction only.
- The predicate `c.billing_email IS NULL` ensures existing values are untouched.
- Batch size (1000) is a tuning knob; reduce it under heavy load, increase if throughput stalls.

### Monitoring progress

After each batch:

```sql
SELECT count(*) AS remaining
FROM customers
WHERE billing_email IS NULL;
```

- When this reaches 0, backfill is complete.
- Log timestamps and counts for audit and rollback readiness.

### Lock timeout guidance

Use a short lock timeout on the migration connection to avoid indefinite waits:

```sql
SET lock_timeout = '2s';
-- run backfill batch here
RESET lock_timeout;
```

Behavior:
- If a row is locked by another long transaction, the query fails after 2 seconds.
- This forces you to:
  - Investigate straggling transactions.
  - Implement retry logic with exponential backoff.
- It does not limit how long a single batch executes, only lock contention.

### Acceptance criteria

- `billing_email` is non-NULL for every row.
- No existing non-NULL values were altered.
- No long-lived transactions are holding locks on `customers`.

If new NULLs appear after this phase, pause and investigate the source before proceeding.

---

## 6. Phase 4: Enforce NOT NULL Safely (NOT VALID → VALIDATE → SET NOT NULL)

At this point, you want to prevent future inserts/updates from leaving `billing_email` as NULL.

### Step 1: Add a CHECK with NOT VALID

```sql
ALTER TABLE customers
  ADD CONSTRAINT customers_billing_email_present
  CHECK (billing_email IS NOT NULL) NOT VALID;
```

The CHECK (billing_email IS NOT NULL) NOT VALID constraint enforces that all new writes satisfy the condition immediately after ADD CONSTRAINT succeeds. An unrelated UPDATE that modifies an existing row will still fail if the updated row retains a NULL billing_email. Using NOT VALID allows the database to skip checking existing rows initially; later, when you run VALIDATE, those old rows are examined. Importantly, enforcement of new inserts and updates does not wait for validation to complete.



### Step 2: Validate the Constraint

Run this after backfill completes and all writers are synchronized:

```sql
ALTER TABLE customers
  VALIDATE CONSTRAINT customers_billing_email_present;
```

Notes:
- Uses `SHARE UPDATE EXCLUSIVE`, which allows normal reads and writes.
- It will scan existing rows; if any violate `billing_email IS NOT NULL`, the command fails.
- If it succeeds, all existing rows satisfy the rule.

### Step 3: Convert to NOT NULL

```sql
ALTER TABLE customers ALTER COLUMN billing_email SET NOT NULL;
```

Key behavior:
- This statement enforces `NOT NULL` for all future changes.
- Because the previous CHECK was validated and found clean, this conversion is efficient.

### Step 4: Drop the Redundant CHECK

```sql
ALTER TABLE customers DROP CONSTRAINT customers_billing_email_present;
```

This cleans up metadata; the `NOT NULL` attribute now fully encodes the rule.

Locking behavior changes with each step. Adding a CHECK, setting NOT NULL, or dropping a CHECK uses ACCESS EXCLUSIVE locks, which block normal SELECTs and all data-modifying operations. VALIDATE uses SHARE UPDATE EXCLUSIVE locks instead: these are compatible with ordinary reads and writes but may conflict with certain maintenance tasks or concurrent DDL. If a validated CHECK guarantees that billing_email is never NULL, SET NOT NULL can skip scanning existing rows to enforce the rule—provided that CHECK is not dropped in the same ALTER TABLE command. Always commit DDL changes separately from your backfill batches, and commit each batch individually so you can isolate any data issues. Remember that lock_timeout limits how long a single lock acquisition may wait, not the total time your query runs.

### Alternative: Native NOT NULL + VALIDATE

PostgreSQL 18 also allows:

```sql
ALTER TABLE customers
  ADD CONSTRAINT customers_billing_email_nn
  NOT NULL billing_email NOT VALID;

ALTER TABLE customers
  VALIDATE CONSTRAINT customers_billing_email_nn;
```



This is shorter and avoids a separate CHECK object, but the semantics are similar. Choose one consistent path for your team.

### Acceptance criteria

- Any attempt to INSERT or UPDATE with `billing_email = NULL` fails.
- Reads of existing non-NULL rows succeed without error.
- No long transactions remain blocking writes.

---

## 7. Phase 5: Clean Up Compatibility Layers

Now that constraints are enforced and writers are aligned, you can remove transitional logic.

### Application-level cleanup

- Remove:
  - Compatibility reads using `COALESCE(billing_email, email)` unless they’re still needed for legacy reporting.
  - Temporary flags or columns introduced to support the migration.

### Database-level cleanup

- If your design no longer requires backward-compatible reads, you may consider removing helper views, but:
  - Do not drop the column yet; data is still valuable.
  - Keep the `NOT NULL` attribute as your primary safeguard.

### Acceptance criteria

- The schema and application code both reflect the “billing_email is required” invariant.
- No legacy fallback paths are documented as active.

---

## 8. Rollback and Pause Strategy

Keep the added column and its data throughout the process. If the application change must be reverted, you can roll back the application code while leaving the database compatible with NULL values for now. After tightening constraints (SET NOT NULL and VALIDATE), restore full compatibility by removing any remaining helper CHECKs and dropping the NOT NULL restriction if needed—again as separate, reviewed changes. Always preserve billing_email data; never delete it during the migration. Pause the process if you encounter unknown writers, recurring NULL values before enforcement, constraint violations after enforcement, or prolonged lock waits. Successful constraint enforcement prevents NULL rows from persisting, rather than relying solely on catching rogue writers afterward.

---

## 9. Practical Task Package for an AI Coding Agent

Give your agent this concise prompt to generate a concrete plan and SQL:

```text
Context:
- PostgreSQL 18.
- Table: customers(id BIGINT PRIMARY KEY, email TEXT NOT NULL).
- Business rule: Add billing_email TEXT (initially nullable). For existing rows where billing_email IS NULL, set it to email during backfill. After migration, billing_email must be NOT NULL.

Deliverables:
1) A phased migration plan covering:
   - DDL for adding the column (nullable first).
   - Idempotent batch backfill SQL with bounded LIMIT and FOR UPDATE.
   - Progress-checking queries.
   - Constraint tightening steps using NOT VALID → VALIDATE → SET NOT NULL (or native NOT NULL + VALIDATE).
2) Notes on:
   - Required app-level changes to supply billing_email on new rows.
   - Compatibility reads during the transition.
   - Rollback commands for constraint.
3) Acceptance criteria for each phase.

Constraints:
- Preserve existing non-NULL billing_email values (if any).
- Use lock_timeout guidance and explain why.
```

The agent should return:
- Reviewed SQL scripts (you keep final authority).
- A short checklist for deployment order.
- Clear “stop if” conditions.

---

## 10. Final Checklist for the Team

Before executing the migration in production, verify:

- [ ] New `billing_email` column exists and is nullable.
- [ ] All write paths (app, workers, imports) are upgraded.
- [ ] Backfill completed with zero remaining NULLs.
- [ ] Constraint validated successfully (no violations found).
- [ ] `billing_email` is now `NOT NULL`.
- [ ] Rollback commands are tested in staging and documented.

Follow this plan and your AI agent becomes a force multiplier: turning a risky schema change into an auditable, reversible deployment step that respects both data integrity and production realities.

## References

- [PostgreSQL 18: ALTER TABLE](https://www.postgresql.org/docs/18/sql-altertable.html)
- [PostgreSQL 18: Modifying Tables](https://www.postgresql.org/docs/18/ddl-alter.html)
- [PostgreSQL 18: CREATE TABLE](https://www.postgresql.org/docs/18/sql-createtable.html)
- [PostgreSQL 18: Explicit Locking](https://www.postgresql.org/docs/18/explicit-locking.html)
- [PostgreSQL 18: UPDATE](https://www.postgresql.org/docs/18/sql-update.html)
- [PostgreSQL 18: Client Connection Defaults](https://www.postgresql.org/docs/18/runtime-config-client.html)
- [GitLab: NOT NULL constraints](https://docs.gitlab.com/development/database/not_null_constraints/)
