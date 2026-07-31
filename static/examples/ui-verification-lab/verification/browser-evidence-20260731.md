# Browser Evidence — UI Verification Lab — 2026-07-31

> Scope: synthetic localhost fixture only
> Sensitive data: none used or recorded
> Publication claim boundary: direct results below, not a cross-tool or production benchmark

## Environment

- Node.js: `v24.18.0`
- pnpm: `11.10.0`
- agent-browser: `0.31.1`
- Browser sessions: disposable and separately named for the broken, fixed-editor, and fixed-viewer checks
- Fixture data: fake order `demo-001`, fake roles `editor` and `viewer`, local routes only

## Deterministic Baseline

Commands:

```bash
pnpm test
pnpm build
```

Result:

- 2/2 Node tests passed.
- The static fixture built into ignored `dist/` output.
- The known local Retry route returned the expected JSON with HTTP 200.
- The deliberately wrong local Retry route returned HTTP 404.

## Browser Red — Broken Baseline

Route pattern:

```text
http://127.0.0.1:4173/?mode=broken&role=editor
```

At a 390 × 844 viewport, the browser reported:

```json
{
  "innerWidth": 390,
  "scrollWidth": 632,
  "role": "Editor",
  "result": "Retry has not run."
}
```

After clicking `Retry status check`:

- UI result: `Synthetic retry failed.`
- Order status: `Needs attention`
- Network: one synthetic POST to the deliberately wrong local route, HTTP 404
- Console: one controlled synthetic retry error
- Page errors: none

The empty page-error result was confirmed in a fresh disposable session during the selected-draft fact gate on 2026-07-31. Console errors and page errors are separate evidence surfaces in this run.

Screenshot: `broken-390.png`.

## Browser Green — Verified Fix

Route pattern:

```text
http://127.0.0.1:4173/?mode=fixed&role=editor
```

At the same 390 × 844 viewport, after clicking Retry, the browser reported:

```json
{
  "h1Count": 1,
  "innerWidth": 390,
  "mainCount": 1,
  "result": "Synthetic retry succeeded.",
  "role": "Editor",
  "scrollWidth": 390,
  "status": "Ready"
}
```

Additional evidence:

- Network: one synthetic POST to the valid local route, HTTP 200
- Console messages after clearing before the interaction: none
- Page errors after the interaction: none
- Screenshot: `fixed-390.png`

The H1 and main counts are narrow structural observations, not a full accessibility audit.

## Session Isolation

The fixed editor session first stored the fake value `editor`. Reopening the fixed route without a `role` query parameter in that same session retained `editor`.

A separate fixed-viewer session stored and displayed `viewer` independently:

```json
{
  "editorSession": {
    "role": "Editor",
    "stored": "editor"
  },
  "viewerSession": {
    "role": "Viewer",
    "stored": "viewer"
  }
}
```

This demonstrates the recorded session boundary only. It does not test real authentication, authorization, cookies, or user accounts.

## Privacy Check

- No production repository code or history was copied.
- No remote Git URL or nested `.git` directory exists in the fixture.
- No real domain, account, user, order, credential, token, cookie, request header, analytics value, hostname, or business payload appears in the UI or screenshots.
- Screenshots contain the rendered synthetic page only; no browser chrome, tabs, profile names, extensions, bookmarks, or filesystem paths are visible.
