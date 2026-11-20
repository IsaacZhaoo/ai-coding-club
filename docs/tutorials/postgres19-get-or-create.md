---
title: "Test Your Signup: Make PostgreSQL Return the Saved ID on Success and Retry"
description: "Use PostgreSQL 19 to return the original signup ID after a duplicate email submission. Compare DO SELECT RETURNING with DO NOTHING in a runnable SQL exercise."
tags: ["tutorial", "postgresql", "sql"]
---

# Test Your Signup: Make PostgreSQL Return the Saved ID on Success and Retry

Hi there! If you’re testing a signup form that talks to PostgreSQL, you probably want one clear signal: “Row saved. Here’s its ID.” You also want that same email address to be safe to retry—no crashes, no double saves, and definitely no accidental overwrites of the original data.

This tutorial walks you through a tiny, self-contained exercise you can run in a single `psql` session (PostgreSQL 19). It shows:

- How to capture the inserted row’s ID on first submission
- What happens if the client resubmits with the same email
- The practical difference between `DO SELECT RETURNING` and `DO NOTHING RETURNING`
- A simple way to verify no overwrite occurs

## The Setup (Run This as One Session)

Open your terminal, start `psql`, connect to any database (even `postgres`), and paste this block. It uses a temporary table scoped to the current connection and wrapped in a transaction so everything cleans up automatically.

```sql
BEGIN;

-- Fresh, temporary table for this test only
CREATE TEMP TABLE signup (
  id      integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email   text UNIQUE NOT NULL,
  display_name text NOT NULL
);

-- First submission: new row should be inserted, return its id
INSERT INTO signup (email, display_name)
VALUES ('reader@example.test', 'First')
ON CONFLICT (email)
DO SELECT RETURNING id, display_name;

-- Retry with the same email: conflict happens. We want to preserve "First".
INSERT INTO signup (email, display_name)
VALUES ('reader@example.test', 'Retry')
ON CONFLICT (email)
DO SELECT RETURNING id, display_name;

-- Another retry demonstrating DO NOTHING:
INSERT INTO signup (email, display_name)
VALUES ('reader@example.test', 'Retry')
ON CONFLICT (email)
DO NOTHING RETURNING id, display_name;

-- Confirm how many rows are actually stored
SELECT count(*) AS stored_rows FROM signup;

ROLLBACK;
```

## What You Should See (And Why It Matters)

Run the script in a single transactional block like above. The output will look roughly like this:

- **First `INSERT`:**
  - Returns one row: `id = 1, display_name = 'First'`

- **Second `INSERT` (`DO SELECT`):**
  - Also returns one row: `id = 1, display_name = 'First'`
  - No new row is created; the conflict target `(email)` triggered the `DO SELECT` branch.

- **Third `INSERT` (`DO NOTHING`):**
  - Returns zero rows
  - The row remains unchanged, confirming idempotency without data mutation

- **Final `SELECT count(*)`:**
  - Returns `1`

Key takeaways:

- `ON CONFLICT ... DO SELECT RETURNING` fetches the existing conflicting row’s columns. That’s perfect for your backend to read “what is actually stored” without assuming a single value. It does not mutate the row; it only selects it.
*   When ON CONFLICT DO NOTHING triggers, PostgreSQL returns an empty `RETURNING` set because no row was actually modified or inserted; this leaves the original signup row untouched and causes the identity sequence to potentially advance on the conflicting statement, meaning the backend cannot retrieve the existing signup ID from that empty result.
- Because the email column is unique and the conflict target matches your form input, any retry with the same email will hit the conflict handler instead of inserting again.

## How to Wire This Into Your Signup Flow

For a real signup endpoint:

1. Use an `ON CONFLICT (email) DO SELECT RETURNING id, display_name` clause for the insert.
2. Treat the returned ID and `display_name` as your canonical values.
3. If the client resends the same email, your code receives the same ID—your application logic can safely treat this as “already registered, here’s the existing record.”
4. Keep side effects (sending emails, creating tokens, webhooks) idempotent on application code; the database conflict clause only guarantees one row in the table.

That’s it: a crisp, testable pattern that ensures your signup form always gets back the saved row ID, regardless of whether it’s first or retry, without letting duplicates or overwrites slip in.