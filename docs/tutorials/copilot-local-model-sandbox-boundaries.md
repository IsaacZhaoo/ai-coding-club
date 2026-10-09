---
title: "Copilot CLI 1.0.94: Local Provider, Offline Mode, and Sandbox Policy Primer"
sidebar_label: "Copilot CLI Sandbox Boundary Lab"
description: "Run a reproducible Copilot CLI 1.0.94 lab to compare local sandbox policies, offline mode, file access, and tool-network access."
keywords: ["Copilot CLI", "local sandbox", "offline mode", "local model", "sandbox policy"]
sidebar_position: 48
tags: ["tutorial", "coding-assistant", "agent-engineering"]
---

# Copilot CLI 1.0.94: Local Provider, Offline Mode, and Sandbox Policy Primer

This tutorial walks you through running the Copilot boundary lab end-to-end. You’ll execute a deterministic protocol fixture against the real Copilot CLI (1.0.94), read its results, and understand which settings to inspect before switching to an actual local model. It assumes you’re comfortable in a terminal on Linux or WSL.

## What this lab proves

The fixture demonstrates three distinct controls:

- **Offline mode** (`COPILOT_OFFLINE=true`): disables GitHub authentication, telemetry, web tools, built-in GitHub MCP, and updates. It still calls your configured provider; it does not stop code/prompts from flowing there.  
- **Local sandboxing**: In Copilot product defaults, local sandboxing is OFF by design; it does not block outbound calls or DevTool usage. When enabled in a real deployment, outbound traffic and bypass requests are allowed per policy. This lab explicitly tightens the boundary: it denies the specific network path and tool-network access we test for.
- **Provider behavior under constraints**: the CLI continues to send model protocol requests even when a shell-level network attempt is blocked by sandbox policy.

Importantly:

- This lab uses a fixed `provider.py` shim; it is not an LLM and does not test “model quality.”
- It does not test all network traffic, only the probe patterns defined in the fixture.
- Results are deterministic and machine-checkable so you can compare them reliably.

For deeper context:  
- [About Cloud and Local Sandboxes](https://docs.github.com/en/copilot/concepts/security-governance-and-network-settings/about-cloud-and-local-sandboxes)  
- [Using Local Sandboxing](https://docs.github.com/en/copilot/how-tos/cloud-and-local-sandboxes/using-local-sandboxing)  
- [Configuring Local Sandbox Settings](https://docs.github.com/en/copilot/how-tos/cloud-and-local-sandboxes/configuring-local-sandbox-settings)

## Prerequisites

Run this lab on Linux or Windows Subsystem for Linux (WSL), using your ordinary user account. You do **not** need sudo or root permissions to execute the sandbox; they are tested under a normal non-privileged user.

## Step 1: Environment and Files

Your environment must meet these requirements:

- Python 3 is installed and runnable as `python3`.
- Node.js, npm, and bubblewrap >= 0.5.0 are available.
- The slirp4netns tools are installed.
- util-linux >= 2.35 is present with `unshare` and `nsenter`.
- iptables and ip6tables (and their restore variants: `iptables-restore` and `ip6tables-restore`) are installed.
- The current user can read and write `/dev/net/tun`.
- A free TCP port 18761 is available.

Having bubblewrap alone does not guarantee successful sandbox startup; all tools listed above are required together.

To obtain the lab files:

Download <a href="/examples/copilot-boundary-lab.zip">the boundary lab</a>.

The ZIP archive contains exactly three Python files inside `copilot-boundary-lab/`:

- provider.py
- probe.py
- run_lab.py


Unpack the archive and enter the directory `copilot-boundary-lab/`. The next step installs CLI 1.0.94 into `./runtime` and invokes that exact executable. No prior Copilot installation needs to be changed.

## Step 2: Run the lab sequence (execute ONCE)

Run these three commands in order. They share the same directory context and produce a single `lab-output` folder with all artifacts.

```sh
npm install --prefix runtime @github/copilot@1.0.94 --no-audit --no-fund
python3 run_lab.py --copilot ./runtime/node_modules/.bin/copilot
python3 -m json.tool lab-output/results.json
```

Notes:

- `run_lab.py` creates one new `lab-output/` directory containing `work`, `outside`, `config`, and `results.json`.
- It starts a single localhost provider process, then runs two CLI sessions sequentially:
  - First with `--no-sandbox` (baseline)
  - Then with `--sandbox` (policy enforced)
- Both CLI runs use `COPILOT_OFFLINE=true` and isolated `COPILOT_HOME`.
- The driver stops its provider after completion; existing output directories are never overwritten. A later repeat must specify a fresh `--output` directory.

## Step 3: Understand what the fixture does under the hood

The fixture keeps things simple but precise:

- `provider.py` returns a fixed “bash tool-call” request and streams back a deterministic response.
- The real Copilot CLI runs `probe.py` inside the workspace. `probe.py`:
  - Reads `work/hello.txt`.
  - Tries to read `outside/sentinel.txt`.
  - Attempts a GET request to `http://127.0.0.1:18761/ping`.

File contents are dummy markers, not secrets. The provider records only the model-protocol request metadata; incoming prompts still contain code/text as usual.

## Step 4: Read the baseline and sandbox results

Both runs use `sandbox.enabled=true` in `settings.json`. The difference is how we invoke the runtime:

- **Baseline run**: Overrides the config with `--no-sandbox`, allowing normal network behavior for this session.
- **Sandbox run**: Uses `--sandbox`, which enforces the lab-specific restrictions defined in `settings.json`.

Here’s what each session reports under the test scope (by construction, using dummy markers):

| Field                  | Baseline (`--no-sandbox`) | Sandbox (`--sandbox`) |
|------------------------|---------------------------|-----------------------|
| `sandboxed`            | `false`                   | `true`                |
| `workspace_read`       | `LOCAL_BOUNDARY_OK`       | `LOCAL_BOUNDARY_OK`   |
| `outside_read`         | `OUTSIDE_SENTINEL_NOT_SECRET` | `FileNotFoundError` |
| `tool_network`         | `LOCAL_PROVIDER_REACHED`  | `URLError`            |

Key points to read correctly:
- The marker files contain only dummy labels. Being able to read a file does not prove it lacks secrets; we are testing access patterns, not content inspection.
- Only **reading** was tested. No write-attempts or file-modification checks are included in this lab.
- The top-level `provider_requests=4` aggregates exactly four POST requests received by the fixture provider across BOTH sessions combined. It is not:
  - A count of probe GETs (one per session, and only baseline reaches the loopback).
  - A per-session total.
  - Inclusive of GET /ping.
- The top-level `passed=true` check validates that probe values, sandboxed markers, and receipt counts match expectations. If you see a mismatch, it indicates something in your environment deviated from the lab’s controlled conditions and warrants investigation.
- This probe is narrow: it targets specific file/loopback destinations and network paths. It does not claim to cover all outbound traffic or all possible routes the tool might take.

## Step 5: Inspect the sandbox configuration used

The lab’s policies are stored in `lab-output/config/settings.json`. Open it to see exactly what was enforced:

```json
{
  "sandbox": {
    "enabled": true,
    "allowBypass": false,
    "allowDevToolAccess": false,
    "auth": {
      "git": false,
      "gh": false
    },
    "userPolicy": {
      "filesystem": {
        "deniedPaths": [
          "/absolute/path/to/lab-output/outside"
        ]
      },
      "network": {
        "allowOutbound": false,
        "allowLocalNetwork": false
      }
    }
  }
}
```

Key points:

- `sandbox.enabled=true` activates policy enforcement.
- `deniedPaths` controls which directories are blocked (the “outside” directory in the fixture).
- `allowOutbound=false` and `allowLocalNetwork=false` deny typical shell network attempts.
- `allowBypass`, `allowDevToolAccess=false`, and authentication flags tighten the policy further.

These match Copilot’s documented sandbox controls:  
[Configuring Local Sandbox Settings](https://docs.github.com/en/copilot/how-tos/cloud-and-local-sandboxes/configuring-local-sandbox-settings)

## Step 6: What NOT to interpret from this lab

- The provider is a fixed shim; there is no “intelligence” or LLM evaluation here.
- Only four POST requests are made to the fixture provider, representing model-protocol calls received during the two sessions; no external destinations are contacted and no file-writing behavior is tested, so the scope is limited to read access and the specified network paths.
- Offline mode (`COPILOT_OFFLINE=true`) disables GitHub telemetry and web tools, but you still send prompts to the configured provider. That separation is intentional and normal.
- The OS sandbox constrains shell processes and supported local subprocesses; the CLI host process itself runs without an OS-level sandbox in this fixture. Built-in file tools follow policy best-effort, not strict OS enforcement.

## Step 7: Moving from the lab to a real local model

Before using the real local model provider, ensure it is already running, confirm that the selected model is installed, and verify that it supports both tool calling and streaming. These capabilities must be checked independently of the deterministic fixture behavior.

In your real workflow you likely have a provider already running locally—say an Ollama instance or similar. In that environment, `COPILOT_PROVIDER_BASE_URL` points to its API endpoint (for example `http://127.0.0.1:11434/v1`), and `COPILOT_MODEL` is the actual model name you want to use.

Set `COPILOT_OFFLINE=true` explicitly. This disables GitHub authentication, telemetry, and web-based tooling—including any built-in GitHub MCP or update checks. Note that the provider still receives prompts locally; “offline” only affects connectivity to GitHub services, not local API calls.

When you start an interactive Copilot CLI session, the `/model` command can discover existing supported Ollama models (as documented since 1.0.94-0). Selecting a model requires your confirmation and does not download, enable offline mode, or toggle telemetry—those are controlled by environment variables and provider configuration.

You can inspect your current sandbox behavior with:
- `/sandbox status` to see the effective sandbox configuration.
- `/sandbox policy` to review what restrictions are active. The `policy` command is informational; it does not execute a tool.

If you begin a new session using plain `--sandbox`, remember that the lab-specific restrictions do not apply by default—you’ll need deliberate policy configuration for those tighter constraints.

This fixture proves access-control behavior, not compatibility with any real model. Always verify that your chosen provider and model support the operations you expect. For more on BYOK and custom providers, see https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models, and for local model discovery guidance: https://github.blog/changelog/2026-10-07-discover-local-models-in-github-copilot-cli/.

## Step 8: Quick reference checklist

Before you switch to a real local model, confirm:

- [ ] `lab-output/results.json` shows `passed: true` with expected baseline and sandbox values.
- [ ] `provider_requests` is at least 4, confirming the fixture’s protocol path works end-to-end.
- [ ] `settings.json` policies match your security requirements (e.g., deny outbound if required).
- [ ] Your local provider supports tool calling + streaming.
- [ ] You know how to inspect `/sandbox status` and `/sandbox policy` in interactive sessions.

## What you now know

- How to run a deterministic Copilot CLI fixture against the real CLI 1.0.94.
- Which output fields map directly to sandbox and offline-mode behavior.
- That `COPILOT_OFFLINE` controls connectivity/telemetry, while the sandbox config controls filesystem and network policy.
- Where to look (`settings.json`, `/sandbox` commands) before trusting a local model setup in production.
