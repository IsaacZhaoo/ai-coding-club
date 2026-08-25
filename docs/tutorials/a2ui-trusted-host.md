---
title: "Build a Trusted A2UI Host for Agent-Generated Interfaces"
description: "Build a trusted A2UI Host that validates messages, admits known components, stages batches, and blocks unapproved actions before side effects."
keywords:
  - A2UI tutorial
  - trusted A2UI Host
  - Agent-generated UI security
  - A2UI component allowlist
  - A2UI action allowlist
sidebar_position: 25.5
tags: [tutorial, a2ui, agent-engineering, security, javascript]
---

# Build a Trusted A2UI Host for Agent-Generated Interfaces

You want an Agent to assemble a release-approval card: a title field, a status indicator and an approve button. Those component types are known ahead of time. A later saved payload requests a `ShellCommand`. The processor you are about to build retains that unknown type as surface data; it does not execute a shell command. The practical question is therefore: where should the application refuse an unknown request before it enters live state?

That question is not answered by the A2UI protocol alone. A2UI gives the application structured UI messages. A trustworthy host still has to validate each message, admit the component, preflight the batch and gate the action before any side effect occurs. This tutorial walks those four responsibilities in order, using a saved fixture that needs no model or API key.

---

## The card you are building

The release-approval card lives at surface ID `release-approval`. Its initial `createSurface` message declares a `Column` containing a `Text` for the title, a `Button` for the approval action and a second `Text` that shows the current status value. There is no `Title` or `Heading` component in the fixture; both the card heading and the status label are plain `Text` nodes.

A subsequent `updateComponents` message introduces a `ShellCommand` type. A later `updateDataModel` message patches the status path:

```json
{
  "version": "v0.9.1",
  "updateDataModel": {
    "surfaceId": "release-approval",
    "path": "/status",
    "value": "approved"
  }
}
```

These are the two cases that separate processor behavior from host policy.

The verified source lives in the [A2UI trusted-host fixture on GitHub](https://github.com/IsaacZhaoo/ai-coding-club/tree/8bfe91f3b6ee0938bd286f077476340b75fb1ab2/examples/a2ui-trusted-host). Clone the repository and check out the tested revision before running it:

```bash
git clone https://github.com/IsaacZhaoo/ai-coding-club.git
cd ai-coding-club
git checkout 8bfe91f3b6ee0938bd286f077476340b75fb1ab2
cd examples/a2ui-trusted-host
npm ci
npm test
```

Package version `0.10.6` and protocol version `v0.9.1` are different facts. The package ships multiple protocol generations; the import path selects the one this tutorial uses. Keep both version strings in your code exactly as they appear — they are not interchangeable.

---

## Creating the processor and walking the accepted path

A2UI represents surface changes with four message types: `createSurface`, `updateComponents`, `updateDataModel` and `deleteSurface`. The processor tracks a model of active surfaces and fires your `onAction` callback when the Agent triggers a user-initiated event.

```js
import {A2uiMessageSchema, Catalog, MessageProcessor} from '@a2ui/web_core/v0_9';
import {BASIC_COMPONENTS} from '@a2ui/web_core/v0_9/basic_catalog';

const BASIC_CATALOG_ID = 'https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json';
const catalog = new Catalog(BASIC_CATALOG_ID, BASIC_COMPONENTS);
const processor = new MessageProcessor([catalog], onAction, {version: 'v0.9.1'});
```

`BASIC_COMPONENTS` contains `Column`, `Text` and `Button`. The processor accepts any component the catalog recognizes. At this point the fixture runs cleanly for the `createSurface` and the `updateDataModel` messages. The accepted update changes `/status` from `pending` to `approved`; the fixture inspects the in-memory surface model and does not render a visual card.

What the processor does with `ShellCommand` depends on your host code. In direct processor use — feeding messages straight to `processMessages` without any preflight — the tested processor retained `ShellCommand` as surface data. It did not execute code. That behavior is reassuring, but it means the decision to refuse an unknown type landed nowhere explicit in the application. The tutorial adds that explicit boundary next.

---

## Adding schema ingress and component admission

Demos that stop the trust discussion at "declarative JSON" leave the application in a position where unexpected component types accumulate silently. The host loop below makes ingress and admission explicit before any message touches live state.

```js
for (const [index, message] of messages.entries()) {
  if (!A2uiMessageSchema.safeParse(message).success) {
    throw new Error(`Invalid A2UI message at index ${index}`);
  }
  for (const component of message.updateComponents?.components ?? []) {
    if (component.component && !catalog.components.has(component.component)) {
      throw new Error(`Untrusted component type: ${component.component}`);
    }
  }
}
```

Two checks, two distinct refusal cases:

**Schema validation** (`A2uiMessageSchema.safeParse`) catches structurally invalid messages. `executeScript` is not a valid top-level A2UI message type. The schema parse fails immediately; nothing downstream processes it.

**Component admission** (`catalog.components.has`) catches component types that are structurally valid A2UI update payloads but reference a type your host does not recognize. `ShellCommand` passes the schema check — it arrives inside a well-formed `updateComponents` message — but it is not in `BASIC_COMPONENTS`, so the catalog membership test fails here.

These two checks finish before staging begins. A schema error or an unknown component type throws in this preflight loop, not inside `stagingProcessor.processMessages`. That ordering matters: staging assumes the message shapes and component types are already approved.

---

## Gating action names

The `onAction` callback receives the event the Agent declared on the component. Before the application dispatches it, the host checks the action name against an explicit allowlist:

```js
const actionName = action?.event?.name;
if (!actionAllowlist.has(actionName)) {
  throw new Error(`Untrusted action: ${actionName ?? '<missing>'}`);
}
const surface = processor.model.getSurface(surfaceId);
if (!surface) throw new Error(`Surface not found: ${surfaceId}`);
await surface.dispatchAction(action, sourceComponentId);
```

`delete_everything` is an action name that should appear in a refusal test. It is not in the allowlist, so the callback throws before `dispatchAction` is reached.

Be clear about what this check is and is not. An action-name allowlist is not authentication, not a permission check, not payload validation and not server-side authorization. It is a narrow gate: the application asserts that only named, expected events can be dispatched from the surface. An Agent that learns to name its events correctly will pass this gate, so the allowlist works as a first refusal layer, not as a complete security boundary.

---

## Staging replay and the partial-mutation case

Schema and component checks protect individual messages. The staging pattern below protects against a batch where early messages succeed and a later message in the same batch would corrupt the surface:

```js
const stagingProcessor = new MessageProcessor([catalog], undefined, {version: 'v0.9.1'});
stagingProcessor.processMessages(structuredClone(acceptedMessages));
const candidateMessages = structuredClone(messages);
stagingProcessor.processMessages(candidateMessages);

const committedMessages = structuredClone(messages);
processor.processMessages(committedMessages);
acceptedMessages.push(...structuredClone(committedMessages));
```

The staging processor replays the already-accepted history onto a clone, then tries the candidate batch against that clone. The committed processor only runs if staging completes without throwing. `acceptedMessages` grows only after a successful commit.

The partial-mutation test exercises this boundary directly. The batch contains two messages: a valid `updateDataModel` that patches `/status`, followed by an `updateComponents` message that carries a known type — `Text` — but in a malformed shape. The staging processor applies the data update to the clone successfully, then reaches the malformed `Text` component. At that point the processor throws. Neither message has reached committed state because the staging run never completed.

The important limitation to name before connecting a live Agent: this staging boundary is synchronous and in-process. It is not an A2UI rollback guarantee — the protocol does not define transaction rollback. The batch atomicity here belongs to the fixture's own design. Any host that relies on it must implement the same staging pattern itself.

---

## Replacing the defaults and testing refusals

The fixture uses `BASIC_COMPONENTS` and a small `actionAllowlist`. For a real approval workflow the application has its own policy about which component types it owns and which action names its backend expects. Replace both before connecting a live Agent:

```js
// Replace BASIC_COMPONENTS with your application's component registry
const catalog = new Catalog(APP_CATALOG_ID, APP_COMPONENTS);

// Replace with the exact action names your backend handles
const actionAllowlist = new Set(['submit_approval', 'request_revision']);
```

Before that connection, write at least these three refusal cases as tests:

1. **Invalid top-level message** — send a message that is not a valid A2UI envelope (for example, `{ "executeScript": "..." }`). Expect the schema check to throw at the preflight loop before staging.

2. **Unknown component type** — send a well-formed `updateComponents` message that carries a type your catalog does not contain (`ShellCommand` in the fixture). Expect the component admission check to throw before staging.

3. **Blocked action name** — trigger the `onAction` callback with an event whose name is not in your allowlist (`delete_everything` in the fixture). Expect the allowlist gate to throw before `dispatchAction`.

The tests do not require a visual renderer. The fixture's in-memory surface model is enough to confirm that the processor's surface state did not change after a rejected message.

---

## Where each check belongs

The article's central claim is worth restating precisely because it determines which code lives in which layer.

The A2UI schema (`A2uiMessageSchema`) and the `MessageProcessor` belong to the protocol implementation. They define what a valid message looks like and how surface state evolves. The processor in the fixture retained `ShellCommand` as data rather than executing it — that is correct processor behavior, not application policy.

The component catalog admission, the staging replay, the action-name gate and the decision to throw rather than silently drop belong to the host application. They are explicit decisions that the application has to make and test. The protocol does not make them for you.

That boundary is the thing to carry forward. A2UI is a channel for structured UI intent. Whether that intent is trusted enough to enter live state is a question the host has to answer with its own catalog, its own allowlist and its own staging strategy — and those answers need to exist in code that is tested before a live Agent sends its first message.

---

**Before you connect a live Agent:** replace `BASIC_COMPONENTS` with your application's component registry, narrow `actionAllowlist` to the exact names your backend handles, and confirm that the three refusal cases above fail loudly rather than silently. The [GitHub fixture](https://github.com/IsaacZhaoo/ai-coding-club/tree/8bfe91f3b6ee0938bd286f077476340b75fb1ab2/examples/a2ui-trusted-host) is the starting point; the policy it contains is a placeholder, not a recommendation.
