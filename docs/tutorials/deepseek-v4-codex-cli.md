---
title: "DeepSeek V4-Flash with Codex CLI: Setup, Compatibility, and Open Architecture"
description: "Set up DeepSeek V4-Flash in Codex CLI with a model catalog, named profile, API key, verification, rollback, and Responses API compatibility limits."
keywords:
  - DeepSeek V4 Codex
  - DeepSeek V4-Flash Codex CLI
  - use DeepSeek with Codex CLI
  - Codex custom provider
  - DeepSeek Responses API
  - DeepSeek Codex setup
sidebar_position: 31
tags: [tutorial, coding-assistant, agent-engineering, deepseek, codex]
---

# DeepSeek V4-Flash with Codex CLI: Setup, Compatibility, and Open Architecture

*By Youguang*

This tutorial has one concrete goal: build a verifiable, switchable, and reversible DeepSeek V4-Flash profile in Codex CLI without touching your existing default configuration. When you finish, you will have added exactly two new files—a model catalog JSON and a named profile TOML—and you will know how to switch back to your original provider at any point by running the ordinary `codex` command.

Once the configuration path is working, the tutorial covers the actual compatibility boundaries of the DeepSeek Responses API, then uses a five-layer architecture breakdown to clarify what you control, what DeepSeek controls, and where the lines are drawn across model weights, hosted inference, protocol, the Agent harness, and local execution.

---

## Prerequisites

Confirm the following before starting:

- **Codex CLI 0.144.0 or newer.** The DeepSeek model catalog integration requires this minimum version. Run `codex --version` to check.
- **A DeepSeek API key.** Obtain one from the [DeepSeek Open Platform](https://platform.deepseek.com/). The V4-Flash API entered public beta on 2026-07-31.
- **Bash on macOS, Linux, or WSL.** The shell commands in this tutorial are written for these environments.
- **Network access to `api.deepseek.com`.** The configuration uses DeepSeek's hosted inference endpoint. This is not a local deployment guide.

---

## Step 1: Confirm the Codex Configuration Directory

Codex reads its configuration from `~/.codex/` by default. If you have not configured Codex before, this directory may not exist yet:

```bash
mkdir -p ~/.codex
ls ~/.codex/
```

This tutorial adds two new files inside that directory. If you already have a `config.toml` there, that is your default Codex configuration. **This tutorial does not modify it.**

---

## Step 2: Fetch and Save the Complete DeepSeek Model Catalog

Codex uses the `model_catalog_json` field in a profile to load an external catalog file that describes the models a custom provider offers. You need to fetch the official catalog from DeepSeek's Codex integration documentation and save it locally.

Go to the DeepSeek Codex integration guide:

> **[https://api-docs.deepseek.com/quick_start/agent_integrations/codex](https://api-docs.deepseek.com/quick_start/agent_integrations/codex)**

The page provides the complete model catalog JSON. Copy the full content and save it as:

```bash
~/.codex/deepseek-models.json
```

**Do not trim or shorten the catalog content.** The `model_catalog_json` field in the profile points to this file, and Codex parses it at startup. An incomplete catalog will cause model-recognition failures.

After saving, verify that the file is present and the JSON is well-formed:

```bash
# Check that the file exists
ls -lh ~/.codex/deepseek-models.json

# Validate JSON structure without printing contents
python3 -m json.tool ~/.codex/deepseek-models.json > /dev/null && echo "JSON valid"
# Or with jq
jq empty ~/.codex/deepseek-models.json && echo "JSON valid"
```

If either command prints `JSON valid`, the catalog file is in place.

---

## Step 3: Create an Independent Named Profile

Codex supports named profiles for switching between different model and provider configurations. A named profile lives at:

```
$CODEX_HOME/<profile>.config.toml
```

`CODEX_HOME` defaults to `~/.codex/`. Create a dedicated profile file without touching anything that already exists:

```bash
touch ~/.codex/deepseek-v4.config.toml
```

Write the following content into that file:

```toml
# ~/.codex/deepseek-v4.config.toml
model = "deepseek-v4-flash"
model_provider = "deepseek"
model_reasoning_effort = "high"
model_catalog_json = "~/.codex/deepseek-models.json"

[model_providers.deepseek]
name = "DeepSeek"
base_url = "https://api.deepseek.com/"
wire_api = "responses"
env_key = "DEEPSEEK_API_KEY"
```

A few notes on these fields:

- `model = "deepseek-v4-flash"` is the API model identifier for DeepSeek V4-Flash.
- `wire_api = "responses"` tells Codex to use the Responses protocol when communicating with this provider. This is the compatibility path DeepSeek officially documents.
- `env_key = "DEEPSEEK_API_KEY"` tells Codex which environment variable to read the API key from. **The key itself does not go into the TOML file.**
- `model_catalog_json` points to the catalog file saved in Step 2.
- `model_reasoning_effort = "high"` follows DeepSeek's official Codex integration guide. Adjust it based on the task.

**This profile file only loads when you explicitly pass `--profile deepseek-v4` to Codex.** Running the ordinary `codex` command is entirely unaffected.

---

## Step 4: Inject the API Key in Shell Scope and Launch

**Do not write the key into any file, and do not export it in a global shell configuration file like `~/.bashrc` or `~/.zshrc`.** Use shell-scoped injection so the key only exists for the current shell session:

```bash
read -rsp "DeepSeek API Key: " DEEPSEEK_API_KEY
export DEEPSEEK_API_KEY
printf '\n'
codex --profile deepseek-v4
```

- `read -rsp` reads the key in silent mode without echoing it to the terminal.
- `export DEEPSEEK_API_KEY` makes the key available to child processes, but only within the current shell session.
- `codex --profile deepseek-v4` loads `~/.codex/deepseek-v4.config.toml` and starts Codex using that configuration.

---

## Step 5: Verification in Three Layers

Verification here has three levels with different scopes. Be precise about what each level actually confirms.

### Layer 1: Local files and environment are present

These checks do not contact the API. They only confirm that the configuration files are in place and the environment variable has been set:

```bash
# Confirm the profile file exists
ls -lh ~/.codex/deepseek-v4.config.toml

# Confirm the catalog file exists and parses
ls -lh ~/.codex/deepseek-models.json
python3 -m json.tool ~/.codex/deepseek-models.json > /dev/null && echo "Catalog OK"

# Confirm the environment variable is non-empty — never print the key value
[ -n "$DEEPSEEK_API_KEY" ] && echo "DEEPSEEK_API_KEY is set" || echo "DEEPSEEK_API_KEY is NOT set"
```

All three passing means the files are present, the catalog JSON is well-formed, and the key has been injected into the current shell. It does not confirm that Codex has parsed the profile or that the key is valid—those are later layers.

### Layer 2: API authentication via a live request

The first request Codex sends to the DeepSeek endpoint may return a normal response, an authentication error, or another API/network error. A `401 Unauthorized` or similar error points to either an incorrectly exported environment variable or an invalid key. A normal response confirms that authentication succeeded and that Codex can communicate with the DeepSeek API.

### Layer 3: End-to-end confirmation with a small task

A small, bounded task—asking Codex to read and describe an existing file, for example—is a good first step before working on anything complex. It lets you confirm that the full chain (profile → key → API → response → tool loop) is functional. Whether any given task succeeds depends on factors beyond configuration: the task itself, model capability, tool compatibility, and the local execution environment. Those are separate from the question of whether the setup is correctly configured.

---

## Step 6: Switching and Rollback

### Returning to your default Codex provider

After you exit the DeepSeek session, running the ordinary `codex` command brings you back to your original default configuration. The named profile has no effect on the default path:

```bash
# After exiting the DeepSeek session, clear the key
unset DEEPSEEK_API_KEY

# Start Codex with the default provider
codex
```

### Removing the added files

This tutorial added exactly two files: `~/.codex/deepseek-models.json` and `~/.codex/deepseek-v4.config.toml`. If you decide you no longer need them:

```bash
rm ~/.codex/deepseek-models.json
rm ~/.codex/deepseek-v4.config.toml
```

Before deleting, confirm that neither file is referenced by any other profile you may have created.

---

## DeepSeek Responses API Compatibility: A Gradient, Not a Binary

DeepSeek officially documents V4-Flash as natively supporting the Responses API and explicitly adapts it for Codex. The `wire_api = "responses"` field in the profile is the correct configuration path based on that documentation. But "compatible" is not a yes/no answer here—the Responses API support has a clear upper and lower bound.

Here is the actual scope of DeepSeek V4-Flash Responses API support:

| Feature / Field | Status | Notes |
|---|---|---|
| Function tools | ✅ Supported | Standard function calling; the core dependency of Codex's tool loop |
| Server-side web search | ✅ Supported | DeepSeek-hosted search capability |
| `apply_patch` | ✅ Supported | Codex-compatible patch tool; the key path for file modifications |
| `previous_response_id` | ❌ Not supported | Server-side response chaining unavailable; cross-request state links via the API are not possible |
| Conversation / store | ❌ Not supported | Server-side session management unavailable |
| Background mode | ❌ Not supported | Asynchronous background tasks unavailable |
| Built-in `file_search` | 🚫 Ignored | Field accepted in the request; not processed by the API |
| Built-in `code_interpreter` | 🚫 Ignored | Same as above |
| Built-in `computer_use` | 🚫 Ignored | Same as above |
| Built-in `mcp` tool type | 🚫 Ignored at API layer | Ignored by the API; whether Codex local MCP paths remain functional depends on whether the client translates MCP tools to ordinary function calls before sending the request |
| Unsupported parameter fields | ⚠️ Possibly silently ignored | Fields that the API does not support may be accepted without error but take no effect |

**On `apply_patch`:** This is the central compatibility point for the DeepSeek × Codex path. `apply_patch` is how Codex writes file changes, and DeepSeek explicitly documents support for it. That explicit alignment means both sides have agreed on a protocol contract for the most critical file-modification path.

**On the built-in `mcp` type being ignored:** DeepSeek's Responses API does not process the built-in `mcp` tool type. Whether Codex's local MCP configuration still produces useful behavior depends on whether the client-side tooling translates MCP tools into ordinary function calls before the request leaves your machine. That translation path is worth examining in your client's logs and documentation; it is not a question you can answer directly from the API reference.

**On silent ignore behavior:** Some unsupported Responses API fields do not trigger an error when included in a request. They are accepted and discarded. If a behavior you expect is not occurring and there is no obvious error, a silently ignored field is worth checking—especially when tracing why something that should have triggered did not.

---

## The Five-Layer Architecture of DeepSeek V4-Flash × Codex CLI

The setup you just built is one configuration of a composable Coding Agent system. Breaking it into five layers clarifies what is replaceable, where constraints exist, and who holds control at each boundary.

| Layer | Component in this setup | Open / replaceable | Constraints |
|---|---|---|---|
| **Model weights** | DeepSeek V4-Flash | Repository + weights MIT licensed | ~304B parameters; weight availability does not mean local runnability |
| **Inference** | DeepSeek hosted API | Provider is switchable via Codex profile | The documented path uses hosted inference; self-hosting involves separate engineering |
| **Protocol** | Responses subset + `apply_patch` | Connects across organizations | Compatibility is a gradient; some fields and tool types are ignored or unsupported |
| **Agent harness** | Codex CLI / `codex-core` | Apache-2.0; inspectable and modifiable | The harness defines the tool loop, context management, retries, sandbox, and approvals |
| **Execution** | Local repo + sandbox + approvals | User controls local actions | Input still crosses the inference boundary; local execution is not local inference |

There is something worth noticing about the two licenses here: one from a Chinese AI team, one from a large US technology company—both landing on permissive open licenses that allow inspection, modification, and commercial combination without copyleft obligations. Both licenses permit the combination this tutorial describes.

---

### Licenses establish the right to combine; technical compatibility is a separate question

MIT weights and an Apache-2.0 harness **permit this combination under those licenses**. They do not establish that the DeepSeek API is fully compatible with Codex at the protocol level, and they do not guarantee any particular task behavior. The licenses are a prerequisite, not a technical capability proof.

This distinction has practical consequences: the two open licenses tell you that you can freely build on both. But you still need the compatibility table to know which fields actually work, which are silently discarded, and which are entirely unsupported. Licenses and protocol specifications answer different questions.

---

### Protocol alignment means interoperability, not uniform behavior

Codex uses `wire_api = "responses"` to communicate with the provider. For this to work, DeepSeek needs to "speak Responses"—and explicitly documents Codex-compatible support for `apply_patch`, which represents an active protocol alignment effort on DeepSeek's part.

What the compatibility table also shows is where that alignment ends. The absence of `previous_response_id` support means cross-request state links cannot be maintained through the API. Ignored built-in tool types mean certain interaction paths that work with OpenAI's native tooling do not function on the DeepSeek side. **Compatibility is a gradient**, not full-spectrum support.

---

### Inference location determines runtime control

The configuration in this tutorial routes all requests to `https://api.deepseek.com/`, DeepSeek's hosted inference endpoint. That is the only inference path this tutorial covers.

The MIT license on the weights technically permits self-hosting. The official vLLM example uses a 4×GB300 node as a reference configuration—which gives you a sense of the scale of the official recipe. A local deployment of a 304B-parameter model is a substantial independent engineering project. It is not an extension of this tutorial.

The practical conclusion: open model weights do not mean inference runs locally. When you use the hosted API, inference happens on DeepSeek's servers. Your input crosses an inference boundary. What Codex controls locally is the tool loop, the sandbox, the approval flow, and file execution—not the model inference itself.

---

### The harness defines Agent behavior and determines the correct benchmark unit

`codex-core`'s README describes it as implementing the business logic used by Rust-based Codex UIs. `codex-protocol` defines the internal types used between the core and TUI, and the external types used by the app server. This means the scheduling of the tool loop, context management strategy, retry logic, sandbox policy, and approval workflow are all defined inside the Codex CLI harness—not inside the model.

This has a direct implication for how to read benchmark numbers: DeepSeek's public Agent benchmark runs with DeepSeek Harness in minimal mode, not Codex CLI. The benchmark score is a measurement of **model + DeepSeek harness + tools + test environment**. It cannot be mapped directly to expected Codex CLI performance.

The correct unit of measurement for any Agent benchmark is: **model + harness + tools + environment**. Swap the harness for Codex CLI—even with the same model weights—and the behavior may differ. This is both the key architectural insight and the reason not to use official benchmark figures to predict what you will see in Codex.

---

## Checklists: Configuration and Five-Layer Ownership

Use these after completing the tutorial to confirm your configuration state and your understanding of what you control at each layer.

### Configuration checklist

- [ ] `codex --version` reports 0.144.0 or newer
- [ ] `~/.codex/deepseek-models.json` exists, contains content copied from DeepSeek's official Codex documentation, and passes JSON validation
- [ ] `~/.codex/deepseek-v4.config.toml` exists and includes the complete `[model_providers.deepseek]` block
- [ ] The profile TOML contains no plaintext API key
- [ ] The API key was injected using `read -rsp` and is scoped to the current shell session only
- [ ] `[ -n "$DEEPSEEK_API_KEY" ] && echo "set"` returns `set` without printing the key value
- [ ] You have run `codex --profile deepseek-v4` and confirmed the profile loads
- [ ] Your existing `~/.codex/config.toml` (if any) has not been modified
- [ ] You know to run `unset DEEPSEEK_API_KEY` after exiting the session
- [ ] You know that running the ordinary `codex` command returns you to your default provider

### Five-layer ownership checklist

| Layer | What you control | What you do not control |
|---|---|---|
| **Model weights** | Right to inspect, reference, and modify weights (MIT) | Inference computation runs on the hosted side |
| **Inference** | Provider selection via profile switching | The inference service runs on DeepSeek's servers |
| **Protocol** | Configuring `wire_api`; choosing which Responses features to use | Some unsupported parameters may be silently ignored by the API |
| **Agent harness** | Ability to inspect and modify Codex source (Apache-2.0) | Harness logic determines tool loop scheduling and context behavior |
| **Execution** | Local sandbox, approvals, and repository files | Inference decisions upstream of execution happen beyond the inference boundary |

---

## Official Sources

- DeepSeek V4-Flash model repository and MIT license: [https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731)
- DeepSeek Codex integration guide (model catalog source): [https://api-docs.deepseek.com/quick_start/agent_integrations/codex](https://api-docs.deepseek.com/quick_start/agent_integrations/codex)
- DeepSeek Responses API documentation (compatibility scope): [https://api-docs.deepseek.com/guides/responses_api](https://api-docs.deepseek.com/guides/responses_api)
- Codex CLI repository and Apache-2.0 license: [https://github.com/openai/codex](https://github.com/openai/codex)
- Codex Core README (harness business logic): [https://github.com/openai/codex/blob/main/codex-rs/core/README.md](https://github.com/openai/codex/blob/main/codex-rs/core/README.md)
- Codex Protocol README (internal and external types): [https://github.com/openai/codex/blob/main/codex-rs/protocol/README.md](https://github.com/openai/codex/blob/main/codex-rs/protocol/README.md)
- Codex Advanced Configuration (named profiles and custom providers): [https://learn.chatgpt.com/docs/config-file/config-advanced](https://learn.chatgpt.com/docs/config-file/config-advanced)

---

## Related Guides

- [Codex Beginner Guide](/docs/tutorials/codex-guide/)
- [Coding Agent Harness Explained](/docs/tutorials/coding-agent-harness-explained/)
- [Coding Agent Sandbox Security](/docs/tutorials/coding-agent-sandbox-security/)
- [Coding Agent Engineering: From Prompt to Graph](/docs/agent-engineering/)
