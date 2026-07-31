# UI Verification Lab

This is a synthetic, anonymous browser-verification fixture. It was created from scratch for a public tutorial and contains no production code, real user data, embedded Git history, remote URL, analytics, credentials, or external service dependency.

## What It Demonstrates

The same fake order page has two modes:

- `?mode=broken`: the Node/HTTP tests still pass, but the page overflows at a 390-pixel viewport and Retry calls a deliberately wrong local route.
- `?mode=fixed`: the long identifier wraps, Retry calls the valid local route, and the interaction finishes without a new console or page error.

The `role` query parameter writes one fake role to local storage. Reusing a browser session retains that state; separate browser sessions keep editor and viewer state isolated.

## Run It

Requirements: Node.js and pnpm. The recorded verification used Node.js `v24.18.0` and pnpm `11.10.0`; no third-party package is required.

```bash
pnpm test
pnpm build
pnpm start
```

Open:

- Broken baseline: <http://127.0.0.1:4173/?mode=broken&role=editor>
- Verified fix: <http://127.0.0.1:4173/?mode=fixed&role=editor>

## Expected Evidence

At a 390 × 844 viewport:

| Check | Broken baseline | Verified fix |
| --- | --- | --- |
| Document / viewport width | `632 / 390` | `390 / 390` |
| Retry request | Synthetic POST returns 404 | Synthetic POST returns 200 |
| UI result | `Synthetic retry failed.` | `Synthetic retry succeeded.` |
| Console | One controlled error | No new message |
| Page errors | Not used as a success claim | None recorded |

For session state, open the editor route in one disposable browser session and the viewer route in another. The recorded run retained `editor` only in the editor session and `viewer` only in the viewer session.

## Boundaries

- This fixture proves only the recorded local behaviors.
- It is not a production incident, accessibility certification, performance benchmark, security test, or cross-browser comparison.
- A 390-pixel check does not prove every responsive breakpoint.
- Empty console and page-error lists do not prove that the application is correct.
- Do not replace the fake identifiers, routes, or roles with real data when reproducing the example.

Sanitized evidence is recorded in `verification/browser-evidence-20260731.md`. The screenshots contain page content only and use synthetic values.
