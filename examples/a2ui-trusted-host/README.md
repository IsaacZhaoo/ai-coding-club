# A2UI Trusted Host Fixture

This no-model fixture separates A2UI protocol processing from host-owned trust decisions.

## Version Boundary

- `@a2ui/web_core`: `0.10.6`
- A2UI message protocol: `v0.9.1`
- Runtime: Node.js with the built-in test runner

Package version and protocol version are independent. The exact dependency is preserved in `package-lock.json`.

## Run

```bash
npm ci
npm test
npm run demo
```

The demo creates one release-approval surface, applies an incremental data update, accepts one allowlisted action, and records three rejected inputs:

- unknown component `ShellCommand`;
- non-A2UI `executeScript` message;
- non-allowlisted action `delete_everything`.

## Trust Boundary

```text
saved JSON messages
  -> official A2uiMessageSchema
  -> host component allowlist
  -> temporary MessageProcessor replay and whole-batch preflight
  -> official MessageProcessor
  -> host action allowlist
  -> application handler
```

The official processor validates properties for component types present in its catalog. In the tested package version it does not itself reject an unknown component type, and an unrecognized message type is ignored. The wrapper makes those two host policies explicit and replays accepted history plus the candidate batch through a temporary processor before committing the batch to the live surface.

This fixture does not prove that every catalog implementation, custom wrapper, renderer, data binding, URL, or side effect is safe. It demonstrates one narrow ingress and action-dispatch boundary.
