---
title: "Call a Web Page Function Directly from an AI Coding Agent"
description: "Expose a webpage action with WebMCP, connect it through Playwright MCP, and verify tool results against the page DOM with a pinned browser setup."
keywords:
  - "WebMCP tutorial"
  - "Playwright MCP"
  - "WebMCP registerTool"
  - "AI coding agent browser tools"
  - "WebMCP pizza demo"
sidebar_position: 38
tags: [tutorial, mcp, agent-engineering, browser-testing]
---

# Call a Web Page Function Directly from an AI Coding Agent

This tutorial shows you how to expose a small action on an existing webpage so that an AI coding agent (using Playwright MCP) can discover and call it like any other tool. We’ll use Google’s Pizza-Maker demo as the working example, walk through the browser + MCP setup, register the tool on the page, invoke it via JSON, and verify both the returned text and the actual DOM state.

By the end you’ll be able to:

- Pin Playwright MCP and its Chromium instance to a known build
- Configure the WebMCP flag and the MCP client configuration
- Register one real page function as an MCP tool (`toggle_layer`)
- Call it directly with concrete JSON arguments
- Confirm the result in the agent’s response and in the browser

## 1. Why this matters

WebMCP is a browser API that lets a page describe its own actions (like “add cheese” or “submit support request”) to an MCP client. Playwright MCP bridges those registered actions into the agent’s tool list.

This isn’t a backend endpoint; it’s something your JavaScript writes once, and then an AI can call it directly from within the browser context. The Pizza-Maker demo is perfect for illustrating that because:

- It has a real UI function (`toggleLayer`)
- It already registers its tool in Chrome’s imperative API guide style
- It works in full-page, visible mode so you can see exactly what changes

You don’t need a new framework or backend. You need one registration around an existing function.

## 2. Reproducible setup (Node + Playwright MCP)

We’ll use:

- Node.js 18+
- A graphical desktop (so the browser opens visibly)
- The pinned Playwright MCP version 0.0.82, which bundles a compatible Chromium for this walkthrough

### 2.1 Install Playwright MCP and its bundled Chromium

Run this once in your terminal:

```bash
npx -y playwright@1.64.0-alpha-1789764292000 install chromium
```

This installs the exact browser revision paired with 0.0.82 (Chromium/Chrome for Testing 154.0.8037.0, revision 1246). It’s important to keep them aligned because WebMCP is still experimental.

### 2.2 Create a WebMCP launch config

Create `webmcp.config.json` with:

```json
{
  "browser": {
    "browserName": "chromium",
    "isolated": true,
    "launchOptions": {
      "headless": false,
      "args": ["--enable-features=WebMCP"]
    }
  }
}
```

Notes:

- `browserName: "chromium"` tells Playwright to use the bundled Chromium instead of an installed Chrome.
- `isolated: true` gives a fresh context per run (good for demos).
- The `--enable-features=WebMCP` flag is what turns on the experimental WebMCP behavior in this pinned browser.

### 2.3 Add Playwright MCP to your MCP client config

In your existing MCP configuration, update the file at the project root — `.mcp.json` when using VS Code’s built‑in agent customization, or an equivalent JSON file in your repository for other clients. This is where the `mcpServers` block below belongs:


```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@0.0.82", "--config", "/absolute/path/webmcp.config.json"]
    }
  }
}
```

Replace `/absolute/path/webmcp.config.json` with your real path. Then:

- Restart or reconnect the MCP server.
- Confirm Playwright MCP is running in your client (you should see it listed among available servers).

Keep the exact pinned pair for this walkthrough. Playwright MCP 0.0.82 is bundled with Chromium 154.0.8037.0, and the configuration passes `--enable-features=WebMCP` via `launchOptions.args`. Although Chrome’s experimental toggle (chrome://flags/#enable-webmcp-testing) exists, it does not change the fact that MCP bridge 0.0.82 sends JSON strings to `executeTool`, while Chrome’s documented API expects objects; sticking with the verified Chromium 154 pair ensures reproducible behavior and avoids API mismatch errors.


Quick checklist:

- [ ] Node 18+ installed
- [ ] `playwright@1.64.0-alpha-1789764292000 install chromium` succeeded
- [ ] `webmcp.config.json` created with flags as shown
- [ ] `mcpServers.playwright` added to your MCP client config
- [ ] MCP server restarted and running

## 3. The demo page and the action it exposes

Use this URL with the `showButtons` query parameter so the human controls stay visible:

```text
https://googlechromelabs.github.io/webmcp-tools/demos/pizza-maker/?showButtons
```

The official pizza demo uses a simple layer stack where the initial cheese is hidden by `display: none`. The existing `toggleLayer` function switches that inline style between `block` (add) and `none` (remove). Both the on‑page human controls and your registered MCP tool ultimately call this same function, and the demo includes a fallback polyfill—so even if the demo appears to work on its own, you cannot assume native WebMCP support in that environment.

*   Initial cheese layer: hidden via CSS `display: none`.
*   Toggle behavior: `toggleLayer` sets inline `display` to `block` on add, `none` on remove.
*   Dual call sites: human UI buttons and the registered MCP tool both invoke `toggleLayer`.
*   Polyfill present: a working demo alone does not prove native WebMCP support.

Key point: WebMCP is a proposed browser API where a page describes its own actions. Playwright MCP exposes those registered actions into an MCP client’s tool list. An ordinary page gains these actions only when its author registers them.

## 4. Page-owned registration (one-time code)

This belongs in your page’s JavaScript, right next to the function it wraps. The official demo’s source confirms this pattern; here’s the canonical registration style from Chrome’s imperative API guide:

```js
await document.modelContext.registerTool({
  name: 'toggle_layer',
  description: 'Control pizza layers (sauce, cheese). Use "add", "remove", or "toggle".',
  inputSchema: {
    type: 'object',
    properties: {
      layer: { type: 'string', enum: ['sauce-layer', 'cheese-layer'] },
      action: { type: 'string', enum: ['add', 'remove', 'toggle'] },
    },
    required: ['layer'],
  },
  execute: async ({ layer, action }) => {
    await toggleLayer(layer, action);
    return `Performed ${action || 'toggle'} on layer: ${layer}`;
  },
});
```

What each part does:

- `name`: becomes the tool identifier in MCP (e.g., `webmcp_toggle_layer` once exposed).
- `description`: helps the agent understand what it can do.
- `inputSchema`: defines valid inputs and enums so the agent doesn’t guess.
- `execute`: calls your existing UI function, waits for any async updates if needed, then returns a human-readable result string.

For your own page:

1. Choose one real action (e.g., “open modal”, “calculate fee”, “submit support request”).
2. Wrap the existing application function in a registered tool.
3. Validate inputs and enforce permissions inside `execute` if required—this registration is just the bridge to the agent.

You don’t need multiple registrations. One well-chosen action shows the pattern clearly.

## 5. Discover, invoke, and check the result

### 5.1 Navigate and discover the tool

In your MCP client, ask it to navigate:

```text
browser_navigate("https://googlechromelabs.github.io/webmcp-tools/demos/pizza-maker/?showButtons")
```

After the page loads and runs its initialization script, it registers `toggle_layer`. Playwright MCP picks that up and adds it to the agent’s available tools.

In version 0.0.82:

- WebMCP collection is on by default.
- The old `browser_webmcp_list` / `browser_webmcp_call` tools are replaced by direct page tools.
- No extra capability switch is needed.

If you’re unsure whether the tool appeared:

- Ask for a snapshot of the tool list, or refresh the client’s view.
- Check the selected tab in your agent interface; tools are organized by the selected context.
- If discovery is missing, verify:
  - The page loaded without console errors.
  - The registration script ran (open DevTools and look at the Network / Sources panels).
  - The client handled dynamic tool lists (it should receive `tools/list_changed` events when the page updates its tools).

### 5.2 Call the action with concrete JSON

Ask your agent to call:

```json
{"layer":"cheese-layer","action":"add"}
```

In natural language, that’s:

- “Call tool `webmcp_toggle_layer` with layer: cheese-layer, action: add.”

What you should see:

- The handler returns something like: `Performed add on layer: cheese-layer`.
- Playwright MCP wraps this into its response.
- On the page, the cheese layer becomes visible (its inline style changes to `display: block`).

### 5.3 Verify both returned data and DOM state

A reliable test includes two checks:

1. Return value from the tool call:
   - Confirm the agent’s message contains the expected string (e.g., “Performed add on layer: cheese-layer”).
2. Actual page state:
   - Ask the agent to evaluate:
     ```js
     () => document.getElementById('cheese-layer').style.display
     ```
   - The result should be `"block"`.

Now remove it:

- Call the tool again with:
  ```json
  {"layer":"cheese-layer","action":"remove"}
  ```
- Expected return: `Performed remove on layer: cheese-layer`
- Expected DOM: `display` becomes `"none"` and the cheese visually disappears.

You can also toggle repeatedly; each toggle flips the state. Using explicit `add`/`remove` lets you set a known state reliably, which is ideal for tests.

For completeness, Microsoft’s published test demonstrates the same direct-call mechanism with `webmcp_add`, passing 2 and 40 and checking that the returned text equals 42. The pizza demo follows that exact model: page registers the tool → agent calls it → DOM + response both confirm success.

## 6. Forms, boundaries, and practical notes

### 6.1 Quick alternative for existing forms

If you have a real HTML form on your page, WebMCP supports a declarative shortcut:

```html
<form toolname="createSupportRequest" tooldescription="Submits a request for customer support.">
  <input name="email" required>
  <textarea name="message"></textarea>
</form>
```

Effects:

- Named fields become parameters in the agent’s tool schema.
- Invocation fills and focuses the visible form; the user submits unless `toolautosubmit` is added.
- This differs from the imperative registration style we used with the pizza demo.

Use declarative forms when your flow is “fill → submit” and you want the UI to stay natural for the human user. Use imperative registration when you need fine-grained control (e.g., conditional logic, async effects, or multiple possible actions).

### 6.2 Cross-origin and permissions

Native WebMCP requires an origin-isolated document—a document isolation prerequisite independent of browser extensions. Permissions Policy’s named `tools` defaults to `self`, so registering MCP tools in a cross-origin iframe needs `allow="tools"`. Keep two decisions separate: (1) registration and permission constraints, and (2) explicit cross-origin sharing via `exposedTo` and the caller’s `fromOrigins`. This walkthrough uses the main-frame demo to isolate those concerns.

### 6.3 Tool metadata and safety hints

When you register a tool, you’re responsible for:

- Accuracy: Provide clear `description`, correct `inputSchema`, and honest return values.
- Safety: For consequential actions (purchases, account changes), enforce application-level permissions and prompt users for confirmation before execution. Hints like `readOnlyHint` or `consequentialHint` communicate intent; they do not replace explicit confirmation or enforce security constraints.

- Validation: Even though the schema guides the agent, always validate inputs and permissions inside `execute`.

A DOM state change confirms that the page action worked; it does not prove a backend transaction succeeded. Treat the tool call as an HTTP-like request where the “response” lives in both the message and the UI.

## 7. Step-by-step checklist for your own page

To replicate this on your site:

1. Ensure you have Node.js 18+ and can run `npx`.
2. Install Playwright MCP with the pinned Chromium:
   ```bash
   npx -y playwright@1.64.0-alpha-1789764292000 install chromium
   ```
3. Create `webmcp.config.json` with the Chromium + WebMCP flags (Section 2.2).
4. Add the Playwright MCP server to your MCP client config (Section 2.3).
5. On your page, identify one function that changes visible state.
6. Register it using the imperative `registerTool` call from Section 4.
7. Navigate to your page via Playwright MCP.
8. Discover the tool name — registrations using `your_action_name` appear in the client as `webmcp_your_action_name`.

9. Call it with concrete JSON parameters.
10. Verify both the agent’s returned string and the actual DOM or visual result.

## 8. Useful public sources

- Chrome overview and setup: https://developer.chrome.com/docs/ai/webmcp
- Imperative API and the registration example: https://developer.chrome.com/docs/ai/webmcp/imperative-api
- Declarative forms: https://developer.chrome.com/docs/ai/webmcp/declarative-api
- Release behavior (Playwright MCP 0.0.82): https://github.com/microsoft/playwright-mcp/releases/tag/v0.0.82
- Configuration and requirements: https://github.com/microsoft/playwright-mcp/blob/v0.0.82/README.md
- Exact bundled browser info: https://github.com/microsoft/playwright/blob/78ff4260d79b924724bdcc4ccd89e463b8f43b0d/packages/playwright-core/browsers.json
- Microsoft direct-call test: https://github.com/microsoft/playwright/blob/78ff4260d79b924724bdcc4ccd89e463b8f43b0d/tests/mcp/webmcp-dynamic.spec.ts
- Pizza-Maker demo source: https://github.com/GoogleChromeLabs/webmcp-tools/blob/be5700df15ced221cfff862aaf5e6cf0c5f92b62/demos/pizza-maker/script.js

---

## Related Guides

- [Coding Agent Browser Testing: What to Check Before You Trust a UI Patch](/docs/tutorials/coding-agent-browser-testing/)
- [MCP Tool Design Guide: Boundaries, Schemas, and Errors for Agents](/docs/tutorials/mcp-tool-design-guide/)
