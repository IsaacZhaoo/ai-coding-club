---
title: "TypeScript SDK v2 and MCP 2026-07-28: Two Upgrades, One Often Missed"
description: "Migrate TypeScript MCP SDK v2 to protocol 2026-07-28 with explicit negotiation, stateless HTTP handling, state relocation, and legacy client checks."
keywords:
  - MCP 2026-07-28 migration
  - MCP stateless server
  - TypeScript MCP SDK v2
  - MCP version negotiation
  - MCP legacy client compatibility
sidebar_position: 24
tags: [tutorial, mcp, typescript, agent-engineering]
---

# TypeScript SDK v2 and MCP 2026-07-28: Two Upgrades, One Often Missed

*By Youguang*

---

The dependency audit passes. The lockfile is clean. You run `npm outdated`, see nothing alarming, and feel the quiet satisfaction of a codebase that looks current. Then a colleague asks whether your MCP server is on the 2026-07-28 protocol, and you realize you don't actually know. You know the *package* is v2. You don't know what the *wire* says.

That gap is the entire point of this guide.

---

## The Real Surprise: SDK Version ≠ Protocol Era

The official TypeScript migration guide is explicit about this, and it is easy to miss: constructing a `Client`, `Server`, or `McpServer` with the v2 SDK does not automatically adopt the MCP 2026-07-28 wire protocol. The SDK ships with backward-compatible defaults. Your server can carry a `v2` package version number and still negotiate the 2025-era protocol on every connection.

This matters because 2026-07-28 is not a minor addendum. It removes the `initialize` / `notifications/initialized` handshake, eliminates protocol-level sessions, drops the `Mcp-Session-Id` header, and changes where client identity and capabilities travel. A server that has not explicitly opted in will, on the legacy wire path, not use `server/discover` or the modern `_meta` capability flow; that path is incompatible with clients that support only the modern protocol and have dropped the old handshake sequence entirely.

The upgrade path therefore has two distinct phases. The mechanical phase rewrites imports and API calls. The architectural phase changes the wire behavior, entry points, and state model. You can finish the first phase and believe you are done. This guide is about not making that mistake.

---

## Know Where You Stand Before Touching Anything

Before running a codemod or bumping a version, answer four questions:

| Dimension | What to check | Why it matters |
|---|---|---|
| **SDK generation** | Is the project on SDK v1, an early v2 build, or already current? | Determines whether the codemod is needed and what it changes |
| **Protocol era** | Does the server negotiate 2025-era or 2026-07-28 on the wire? | A v2 package can still speak 2025-era by default |
| **Transport** | HTTP (Streamable or SSE), stdio, or both? | Entry points, header requirements, and deprecation timelines differ by transport |
| **State posture** | Is the server stateless, or does it rely on session-scoped state between calls? | Sessionful servers need an explicit compatibility branch, not just a handler swap |

Write these down. The answers control which steps below actually apply to you, and they prevent the common failure mode of treating an HTTP session migration as equivalent to a stdio one.

---

## Step 1: Run the Codemod If You Are on v1

If you are on SDK v1, the mechanical starting point is the official codemod:

```bash
npx @modelcontextprotocol/codemod@latest v1-to-v2 .
```

Run this at the package root. Review its output manifest. The codemod handles import paths, renamed APIs, and package reference changes. It does not adopt the modern protocol. Think of it as a prerequisite, not a migration. After it runs, you are in the same architectural position as someone who started on an early v2 build: the wire behavior is still 2025-era by default, and the work described in the rest of this guide still applies.

What the codemod does and does not do:

| Category | Codemod handles | Architectural work (you handle) |
|---|---|---|
| Package references | ✅ Rewrites `@modelcontextprotocol/sdk` imports | ❌ Does not change protocol defaults |
| API surface | ✅ Renames deprecated constructors and methods | ❌ Does not switch entry points |
| Transport wiring | ✅ Updates old transport instantiation patterns | ❌ Does not introduce `createMcpHandler` or `serveStdio` |
| Session model | ❌ Does not touch session state logic | ❌ You must route or replace it explicitly |
| Protocol handshake | ❌ Does not remove `initialize` negotiation | ❌ That is a wire-level decision you make in step 3 |

After reviewing the manifest and confirming the import changes are sane, commit. That gives you a clean baseline before the architectural steps.

---

## Step 2: Choose a Client Negotiation Mode Deliberately

The client side of a migration is often where "auto" hides a decision that should be explicit. The `versionNegotiation` option on `Client` accepts three meaningful postures:

**Legacy default.** If you omit `versionNegotiation`, the client speaks 2025-era. This is backward-compatible but not a migration.

**`mode: 'auto'`.** The client probes for modern protocol support and, where the SDK's documented transport, response-status, timeout, and configured-version conditions are met, falls back to legacy. This is the right posture during a bounded transition window where some servers in your environment have migrated and some have not:

```ts
const client = new Client(
  { name: 'my-client', version: '1.0.0' },
  { versionNegotiation: { mode: 'auto' } },
);
```

`auto` does not mean "always modern." It means the client will attempt modern negotiation and fall back when those conditions permit it. The selected era is inspectable with `client.getProtocolEra()`. During the transition, this posture is operationally safer than a hard pin. It also means you cannot use client behavior in this mode as proof that a specific server has actually migrated.

**Modern pin.** Pin the client to modern-only when legacy fallback is intentionally rejected. This is the right posture after you have confirmed all servers in scope are running 2026-07-28 and you want the client to fail loudly rather than fall back. If you pin early and have servers that have not migrated, you will get failures. That is the point.

Choose the mode based on your migration window, not on what sounds most current. `auto` during transition, pin when transition is complete.

---

## Step 3: Move HTTP Serving to `createMcpHandler`

The v2 HTTP entry for per-request modern behavior is `createMcpHandler`. It accepts a factory function and defaults to stateless legacy support from the same factory:

```ts
const handler = createMcpHandler(buildServer);
```

`buildServer` is called per request. The handler manages modern protocol negotiation, including the 2026-07-28 requirements for `Mcp-Method` and `Mcp-Name` request headers on Streamable HTTP. You wire this handler into your HTTP framework the same way you would any other route handler.

**If your existing server is sessionful**, this is the step where you cannot cut straight across. `createMcpHandler` assumes stateless, per-request behavior. A server that accumulated state in a session object over multiple calls cannot simply drop into this handler and preserve that behavior. You have two options:

1. **Explicit compatibility branch.** Route requests that carry legacy session signals to a separate handler that preserves the old session logic. Run the modern handler alongside it. Deprecate the legacy branch once clients have migrated.
2. **State model refactor first.** Move session-scoped state to explicit handles before switching the entry point. See step 4.

Do not assume the default handler preserves your session model. It does not. This is the step where unreflective migrations break things in production in ways that are hard to diagnose.

---

## Step 4: Move State to the Right Place

This step has two distinct sub-problems that are easy to conflate. Getting them confused leads to either security issues or architectural clutter.

**General cross-call application state** belongs in explicit server-minted handles that are passed as ordinary tool arguments. If your server currently stores user context, computed intermediate results, or resource references in a session object, move them to a handle that your server creates, manages, and passes explicitly. The client holds the handle identifier and includes it in subsequent calls. The server resolves the handle to the backing state. This is ordinary application architecture; the change is that the session boundary no longer provides it automatically.

**MRTR `requestState`** is narrower and distinct. It carries opaque retry state through the client for the purpose of resuming an interrupted request. It is not a general state store. It is attacker-controlled input. If `requestState` influences authorization decisions, resource access, or business logic, it must be integrity-protected on the server side before acting on it. Do not use `requestState` as a substitute for explicit handles, and do not treat explicit handles as equivalent to `requestState`. They solve different problems and have different trust properties.

The practical migration action is: audit every place your current server reads from session state. For each one, decide whether it belongs in an explicit handle (most cross-call state) or in protected `requestState` (only retry resumption). The default should be the explicit handle. Use `requestState` only when you are specifically implementing retry semantics.

---

## Step 5: Stdio Branch

If your server runs over stdio rather than HTTP, the entry point is:

```ts
serveStdio(() => buildServer());
```

The factory pattern is the same as `createMcpHandler`. The protocol negotiation semantics follow the same modern-versus-legacy distinction. The stateless-versus-session analysis is structurally simpler for stdio because stdio servers are typically single-connection and the session boundary coincides with the process lifetime. The state migration guidance from step 4 still applies, but the compatibility routing concern from step 3 is usually not present.

If your deployment runs both HTTP and stdio paths, handle them as separate branches with their own entry points. The factory function can be shared; the serving layer cannot.

---

## Step 6: Verify Both Modern and Legacy Before Removing the Fallback

This is the step most likely to be skipped under schedule pressure. Do not skip it.

Before removing legacy support from your server:

- Confirm that modern clients can connect, call `server/discover`, and execute tools without triggering any fallback path.
- Confirm that legacy clients still work against the compatibility branch you retained in step 3.
- Do not use a successful modern connection as proof that the legacy path still works. Test them independently.

Modern servers must implement `server/discover`. Clients may call it before other requests. If your server does not respond correctly to a discovery request, a modern client may fail in ways that are not immediately obvious from the error message.

---

## What I Actually Ran

On 2026-07-29, I cloned the official TypeScript SDK repository at commit `cc4b41617ce3601b1290d67216ea0b194a3cd9ac` and ran the official `examples/stateless-legacy` example with Node.js v24.18.0 and pnpm 10.26.1.

The example server listened on `http://127.0.0.1:32123/mcp`. The official example client looped through `legacy` and `auto` modes, found and called `greet`, asserted `Hello, world!` in both responses, and exited with code 0.

That is all this verifies. It does not verify a real v1 codemod, a sessionful production migration, authentication integration, MRTR with integrity protection, `requestState` in a real retry flow, caching with `ttlMs` and `cacheScope`, stdio serving, behavior behind a gateway or load balancer, or any performance characteristic. The official example is a useful sanity check that the SDK's dual-era plumbing works as advertised on a local socket. It is not a production readiness test.

The example is worth running before you start your own migration. It gives you a working reference point for what `auto` mode looks like. Then you close it and treat your own migration as its own problem.

---

## A Note on What Is Deprecated Versus Removed

Several features that you might have assumed are gone are still present but deprecated: Roots, Sampling, Logging, Dynamic Client Registration, and HTTP+SSE. Deprecated means they will be removed in a future revision; it does not mean they are gone today. Do not remove support for these from your server on a timeline driven by assuming they are already gone. Check whether your clients use them, and deprecate on a schedule driven by actual client migration, not by protocol aspiration.

---

## Migration Checklist

Use this checklist as a gate, not a formality. Each item should be verifiable, not assumed.

- [ ] **Inventory complete.** SDK generation, protocol era, transport, and state posture are documented before any changes.
- [ ] **Codemod run (v1 only).** `npx @modelcontextprotocol/codemod@latest v1-to-v2 .` executed, manifest reviewed, changes committed.
- [ ] **Client mode chosen deliberately.** `versionNegotiation` set to `auto` for a bounded transition or pinned for a completed one. Default (legacy) is a conscious choice, not an omission.
- [ ] **HTTP entry point updated.** `createMcpHandler(buildServer)` wired into the HTTP layer.
- [ ] **Sessionful compatibility branch handled.** Legacy session routing is either explicit or confirmed unnecessary.
- [ ] **State model migrated.** General cross-call state moved to explicit server-minted handles. `requestState` used only for retry flows, with integrity protection where it influences authorization or resources.
- [ ] **Stdio entry point updated (if applicable).** `serveStdio(() => buildServer())` in place of the old stdio serving pattern.
- [ ] **`server/discover` verified.** Modern clients can call it and receive a correct response.
- [ ] **Modern client path tested independently.** Not inferred from `auto` fallback success.
- [ ] **Legacy client path tested independently.** Not assumed to be preserved by the new handler.
- [ ] **Deprecated features audited.** Roots, Sampling, Logging, Dynamic Client Registration, HTTP+SSE: confirmed present or confirmed absent from all active clients before removal.
- [ ] **Fallback removed only after both paths pass.** Not on a calendar date.

---

## Official References

- [MCP 2026-07-28 release overview](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [Specification changelog for 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- [Server discovery specification](https://modelcontextprotocol.io/specification/2026-07-28/server/discover)
- [TypeScript SDK migration index](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/migration/index.md)
- [TypeScript SDK 2026-07-28 support guide](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/migration/support-2026-07-28.md)
- [Official stateless-legacy dual-era example](https://github.com/modelcontextprotocol/typescript-sdk/tree/main/examples/stateless-legacy)

---

## Related Guides

- [MCP Server Guide](/docs/tools/mcps/)
- [MCP Tool Design Guide](/docs/tutorials/mcp-tool-design-guide/)
- [MCP Server Security Checklist](/docs/tutorials/mcp-server-security-checklist/)
- [Claude Code Skills, Hooks, and MCP](/docs/tutorials/claude-code-skills-hooks-mcp/)
