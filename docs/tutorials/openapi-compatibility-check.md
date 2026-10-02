---
title: "Guard Your API: Check for Breaking OpenAPI Changes and Give an Agent a Targeted Repair Task"
sidebar_label: "OpenAPI Compatibility Checks"
description: "Use oasdiff to detect breaking OpenAPI changes, identify affected client requests, and give a coding agent a focused repair task."
keywords: ["OpenAPI", "oasdiff", "API compatibility", "AI coding agent"]
sidebar_position: 44
tags: ["tutorial", "agent-engineering"]
---

# Guard Your API: Check for Breaking OpenAPI Changes and Give an Agent a Targeted Repair Task

When you evolve your API, the invisible enemy isn’t just the new code; it’s the silent failure of existing clients that still send valid requests under the old contract. A single required field change can invalidate years of working integrations. This guide shows you how to:

- Detect whether an OpenAPI revision introduces a breaking change.
- Explain the exact operation, property, and client request affected.
- Give your coding agent precise context so it repairs with minimal risk.
- Verify contract compatibility alongside actual service and client behavior.

Let’s turn versioning from hopeful into deliberate.

## 1. Prerequisites

You’ll use `oasdiff` (version 1.33.0, the referenced release in this guide). Download the binary for your OS and architecture from the v1.33.0 release page, place it on your PATH, and verify the version:

Verify:

```bash
oasdiff --version
# Output should display the version string for 1.33.0
```

## 2. Set Up a Representative Example

We’ll use a tiny but realistic scenario that mirrors real-world API contracts.

### Base definition (`openapi-base.yaml`)

```yaml
openapi: 3.0.0
info:
  title: Sample API
  version: 1.0.0
paths:
  /products:
    post:
      operationId: addProduct
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
              required:
                - name
      responses:
        '200':
          description: OK
```

### Revision definition (`openapi-revision.yaml`)

```yaml
openapi: 3.0.0
info:
  title: Sample API
  version: 1.0.0
paths:
  /products:
    post:
      operationId: addProduct
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                description:
                  type: string
              required:
                - name
                - description
      responses:
        '200':
          description: OK
```

### Existing client request (still valid under the base)

```json
{
  "name": "Notebook"
}
```

Under the base contract, this request is valid. Under the revision contract, the request body no longer satisfies the schema because `description` is now required. That’s exactly the kind of schema-level incompatibility we want to detect early, before it propagates into runtime errors.

## 3. Run a Breaking-Change Detection

Use `oasdiff breaking` with the `--fail-on ERR` flag. This mirrors CI behavior: fail fast when you detect definite breaking changes.

```bash
oasdiff breaking --fail-on ERR openapi-base.yaml openapi-revision.yaml
```

Semantic finding summary:

- **Operation:** `/products POST` (`addProduct`)
- **Property change:** `description` is now a required property in the request body schema.
- **Implication:** Existing client payloads that omit this field no longer conform to the declared contract.

Key behaviors to remember:

- `breaking`: Reports ERR and WARN; INFO is excluded by default.
- `diff`: Broader view, including documentation-only differences.
- Exit code: 1 when ERR findings are present (useful in CI).  
  Note: Other non-zero exit codes exist (e.g., 101 on flag errors, 102 on spec-load issues, 103 on unmatched globs), but for this command a return of 1 specifically indicates ERR-level incompatibilities.

If you want to treat warnings as failures too (e.g., in a safety-first team), use:

```bash
oasdiff breaking --fail-on WARN openapi-base.yaml openapi-revision.yaml
```

## 4. Interpret the Report

Semantic breakdown of the finding:

- **Operation:** `/products POST` (`addProduct`)
- **Property:** `description` in the request body schema
- **Affected client behavior:** Any existing client sending `{ "name": "Notebook" }` will be declared incompatible with the new spec because it omits a required field. Whether the server returns 400, 422, or behaves differently depends on implementation details; the tool reports schema-level incompatibility, not HTTP status codes.

Important distinctions:

- The tool compares declared contracts, not runtime behavior.
- A permissive server accepting old requests does not prove compatibility from a spec perspective.
- Declaring `description` as required changes the contract; default values or optional server-side fills do not make omission valid under that schema.

## 5. Choose Your Compatibility Strategy

Once you know *what* broke, decide *how* to fix it.

### Option A: Keep the New Field Optional

If business rules permit the field being omitted, change the revision so `description` is not required. Then:

- Run `oasdiff breaking --fail-on ERR` again; it should report no ERRs.
- Verify that your service still validates and stores `description` when provided.

This is often sufficient for backward compatibility, but only if your domain truly tolerates missing descriptions.

### Option B: Add Versioning or Migration Rules

If the field must be mandatory (e.g., for compliance or product integrity), you cannot silently break clients. Choose an explicit plan:

- **Versioned endpoint:** `/products/v2/` with the new required field; keep `/products/` as-is for a deprecation window.
- **Deprecation header and timeline:** Announce breaking changes via `Deprecation` or custom headers, with a published sunset date.
- **Migration guide:** Document how clients should update their payloads.

Remember: changing one client’s code does not update all existing consumers. Your API contract is the shared truth that must evolve deliberately.

## 6. Give Your Coding Agent a Focused Repair Task

Now hand your AI agent the exact context it needs to repair cleanly. Structure your prompt like this:

```text
Context:
- We have an OpenAPI base and revision diff.
- Existing client still sends {"name": "Notebook"} and must continue to work.

Definitions:
- Base spec: openapi-base.yaml (provided)
- Revision spec: openapi-revision.yaml (provided)
- Old valid request: {"name": "Notebook"}
- Business requirement: We need 'description' in new payloads, but we do NOT want to break existing clients.

Files provided:
- api/openapi-base.yaml
- api/openapi-revision.yaml
- client/src/client.ts (uses the POST /products endpoint)
- service/routes/products.ts (handles addProduct)

Task:
1) Explain the cause of the breaking change in 2–3 sentences.
2) Propose a minimal change to the OpenAPI revision so that:
   - 'description' remains available for new clients.
   - Existing requests without 'description' are still valid according to the spec.
3) Update the corresponding code (client and/or service) if needed to handle both old and new payloads safely.
4) Provide verification steps:
   - Run oasdiff breaking --fail-on ERR on the revised specs.
   - Run existing service tests.
   - Run client integration tests with the old payload and confirm a successful response (e.g., 200).

Constraints:
- Keep changes minimal.
- Document any versioning or deprecation headers you recommend if we decide 'description' must be required later.
```

This prompt gives the agent:

- The baseline and revision specs.
- The comparison report and its implication.
- A concrete payload that currently fails schema validation under the new spec.
- Clear business rules and file locations.
- A step-by-step ask for cause, repair, and verification, including behavior assertions alongside spec checks.

## 7. Verify Compatibility End-to-End

A good repair is only as strong as the checks you run.

### Contract-level checks (CI)

Use the same `oasdiff` command in your CI pipeline:

```bash
# Compare baseline ref to proposed change
oasdiff breaking --fail-on ERR origin/main:openapi.yaml openapi.yaml
```

If you’re integrating with a Git-based workflow (like DependencyTrack’s public example), checkout the PR base SHA into a dedicated directory and compare its OpenAPI file against your proposed definition with `fail-on: ERR`.

### Service-level checks

Run your existing service tests:

- Test that new payloads including `description` are accepted.
- If you kept `description` optional, test that payloads missing it are still accepted.
- If you versioned the endpoint, verify routing between old and new paths works correctly.

### Client-level checks

Run client-side integration tests:

- Send the old request `{ "name": "Notebook" }` to `/products`.
  - Expect: 200 OK (no breaking change).
- Send a new request with `description`.
  - Expect: 200 OK and correct storage.

These three layers—contract, service, client—form a tight feedback loop that prevents “it works locally but breaks in production.”

## 8. Git Integration: Quick Reference

When you add this to your repo:

```bash
# Compare working directory against a remote branch (fetch if needed)
oasdiff breaking --fail-on ERR origin/main:openapi.yaml openapi.yaml

# Compare two local files
oasdiff breaking --fail-on ERR openapi-base.yaml openapi-revision.yaml
```

Git notes (v1.33.0 docs):

- The first argument must be an existing ref or file; fetch it first if it’s remote-only.
- Use `--fail-on ERR` in your pre-commit or CI hooks for strict compatibility enforcement.

## 9. Practical Workflow Summary

1. **Before merging a new OpenAPI:** run  
   `oasdiff breaking --fail-on ERR BASE REVISION`.
2. **If an ERR appears:**  
   - Identify the operation and property.  
   - Explain which existing client requests break.  
   - Decide: make it optional, version the endpoint, or deprecate with a plan.
3. **For your coding agent:** provide specs, report, sample payload, and business rules; ask for cause + minimal repair + verification steps.
4. **After changes:** run the same `oasdiff` command in CI plus your service/client tests.

## 10. Further Tools You Might Use

- **AI Coding Club OpenAPI Client Generator:**  
  https://tools.aicoding.club/openapi-client/  
  Generate starter TypeScript/JavaScript/Python client code from JSON definitions, then adapt to your project’s patterns.
- **oasdiff sources and docs:**  
  - Breaking rules: https://github.com/oasdiff/oasdiff/blob/v1.33.0/docs/BREAKING-CHANGES.md  
  - Official base/revision samples: https://raw.githubusercontent.com/oasdiff/oasdiff/v1.33.0/data/checker/request_property_added_base.yaml  
  - Releases: https://github.com/oasdiff/oasdiff/releases/tag/v1.33.0  
  - Git revision usage: https://github.com/oasdiff/oasdiff/blob/v1.33.0/docs/GIT-REVISION.md
- **DependencyTrack CI workflow example:**  
  https://github.com/DependencyTrack/dependency-track/blob/a26075bf4bd1b7665d464f2a08ecfd8a0f063c65/.github/workflows/ci-lint.yaml

---

The rule of thumb: an API contract is a promise, not just documentation. When you ship a new OpenAPI revision, verify it against your baseline with `oasdiff`, understand which real requests break, and then guide your agent to repair with surgical precision. That’s how you evolve APIs without surprising your users.