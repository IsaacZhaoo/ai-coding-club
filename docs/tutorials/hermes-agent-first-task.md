---
title: "Getting Started with Hermes Agent: Install, Connect, and Run a Local Code-Reading Task"
description: "Install Hermes Agent, connect a model provider, and read a local Python project with file references. Verify its predictions, resume sessions, and troubleshoot setup."
keywords:
  - "Hermes Agent tutorial"
  - "Hermes Agent install"
  - "Hermes CLI"
  - "local code reading"
  - "Hermes model setup"
sidebar_position: 36
tags: [tutorial, agent-engineering, hermes]
---

# Getting Started with Hermes Agent: Install, Connect, and Run a Local Code-Reading Task

This guide walks you through installing Hermes Agent CLI on Linux/macOS/WSL2, connecting it to a model provider, configuring it for local execution, and completing your first source-grounded reading task in an actual project directory.

By the end, you will be able to:

- Install and verify the Hermes CLI
- Configure a model provider and select an available model
- Set Hermes to use the local terminal backend in a specific project directory
- Complete a concrete file-reading task, cite file locations, and verify results manually
- Quit, resume, and troubleshoot common setup issues

Assumed environment: A Linux/macOS/WSL2 shell where Git, curl, tar, and `sha256sum` are available. You have an account with at least one supported model provider (e.g., OpenRouter or your choice). For this tutorial, we’ll assume you’ll use OpenRouter as a simple example; substitute your own provider if you prefer.

---

## 1. Install Hermes CLI

Hermes provides an official installer script that handles Python, Node, and related runtimes:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-browser --non-interactive
```

Key points:

- `--skip-browser` avoids downloading browser components (unnecessary for terminal-only work).
- `--non-interactive` lets the script proceed without prompts.
- After installation, verify:

  ```bash
  hermes --version
  ```

  You should see the version string printed.

Default POSIX paths (may vary slightly by system):

- Launcher binary: `~/.local/bin/hermes`
- Source directory: `~/.hermes/hermes-agent/`
- Data & config: `~/.hermes/`

Open a new terminal session, or reload your shell configuration:

```bash
source ~/.bashrc   # for Bash
# or
source ~/.zshrc    # for Zsh
```

If you still can’t find `hermes`, confirm that `~/.local/bin` is in your `PATH`.

---

## 2. Configure Your Model Provider

Run the model configuration command from an OS shell (not inside Hermes yet):

```bash
hermes model
```

This will:

- Prompt you to select or add a provider
- Guide you through authentication for that provider
- Let you choose a model to use

Notes:

- Run `hermes model` in your OS shell to configure (or change) provider, API key, and model; these settings persist across Hermes sessions, while `/model` inside Hermes lets you switch among already configured models quickly.
- Ensure the chosen model:
  - Supports tool calling
  - Supports at least ~64k tokens of context
- For this tutorial, we’ll assume you select OpenRouter and provide an API key. You may use any provider; follow its specific auth flow when prompted.

After successful setup, Hermes stores:

- General config in `~/.hermes/config.yaml`
- API secrets commonly in `~/.hermes/.env`
- OAuth state (if applicable) under `~/.hermes/`

---

## 3. Set Up the Local Terminal Backend

For this tutorial, we’ll run Hermes locally on your machine, with commands executing under your current user’s permissions.

In your shell:

```bash
hermes config set terminal.backend local
```

What this means:

- “Local” = agent commands run on this computer.
- No OS-level sandboxing or isolation is provided.
- A “project directory” simply defines where Hermes focuses its attention for file reads and tool execution.

---

## 4. Choose a Project Directory

You can work with any small project of your choice. For this tutorial, use AI Coding Club’s five-file code-reading exercise: <a href="https://aicoding.club/examples/codebase-reading-lab.zip">Download the code-reading exercise</a>.

1. Extract the ZIP to a location you can navigate via your shell.
2. Change into the folder that contains `main.py` (and the other four files: `repository.py`, `query.py`, `tasks.json`, `README.md`). For example, if you extracted it to `/Users/you/code/reading-lab`:

   ```bash
   cd /path/to/extracted/project
   ```

   Replace the path above with your actual project directory.

The exercise runs with standard Python 3 and the Python standard library; Hermes simply talks to the model service you configured. When you’re ready, start Hermes from this exercise directory. If you’re using a different project, adjust the filenames and paths accordingly in later steps. No source clone is required—this ZIP is hosted by AI Coding Club for the lab itself.

---

## 5. Start Hermes in the Project Directory

Now launch Hermes from within the project directory:

```bash
hermes
```

You should see a welcome screen showing:

- Your selected model
- Terminal backend: local
- Working directory: the project directory you’re in
- Enabled tools (file reading, terminal, etc.)

Inside Hermes:

- In-session commands start with `/` (e.g., `/tools`, `/quit`, `/model`).
- Shell commands like `hermes` and `hermes model` run outside Hermes.
- `/quit` exits the Hermes session; Ctrl+C may interrupt an ongoing operation but doesn’t always exit cleanly.

---

## 6. Verify Tools and Directory Context

Let’s confirm that Hermes sees the right environment:

```text
/tools
```

You should see tools such as:

- File reading (e.g., `read_file`)
- Terminal execution (e.g., `terminal`)

If file-reading or terminal tools are missing, exit with `/quit`, then reconfigure with:

```bash
hermes tools
```

---

## 7. Complete a Source-Grounded Reading Task

Now we’ll ask Hermes to analyze the actual project files and make predictions you can independently verify.

Inside Hermes, paste this request (you can copy-paste as-is):

> You are working in: /path/to/project (replace with your real path). Confirm your working directory, then do the following without editing any files:
> 
> 1. Read main.py, repository.py, query.py, tasks.json, and README.md.
> 2. Cite file paths and line ranges where you see evidence for each point.
> 3. Explain how the program runs: describe what python3 main.py does by default, including argument handling and the --status option behavior.
> 4. Predict the exact output (task IDs) produced by these two shell commands:
>    - python3 main.py
>    - python3 main.py --status done
> 
> Return your analysis in a concise report format with clear file references.

After Hermes responds, verify its claims:

### 7.1. Check File Locations and Paths

Ask Hermes to confirm it’s using the right directory:

```text
What is your current working directory?
```

It should match the path you navigated into earlier.

### 7.2. Spot-Check File References

For each file Hermes mentions, quickly scan the cited lines:

- `main.py`: Look for `argparse` or similar argument parsing; confirm default `--status=open`.
- `repository.py`: Confirm UTF-8 JSON loading of `tasks.json`.
- `query.py`: Look for status filtering and sorting by ID.
- `tasks.json`: Verify the structure Hermes describes (task IDs, statuses).
- `README.md`: Check for brief usage notes that match Hermes’s explanation.

### 7.3. Run the Commands Independently

Open a new terminal window (not inside Hermes), stay in the project directory:

```bash
python3 main.py
```

You should see output listing task IDs, e.g.:

- T1, T3

Then run:

```bash
python3 main.py --status done
```

You should see only:

- T2

Compare these results with Hermes’s predictions. If they match, your environment and configuration are correct.

### 7.4. Ask Hermes to Align Its Explanation

If there’s a mismatch, you can ask:

> Re-check main.py’s argument parsing and repository.py’s JSON loading. Did I misread any status values or default behavior? Update your explanation accordingly.

Hermes will re-read the files and refine its analysis, which is the core value of a file-grounded agent session.

---

## 8. Quit, Resume, and Session Management

When done:

```text
/quit
```

To return later to the same project:

1. Close or exit Hermes.
2. From your shell, navigate back into the project directory:

   ```bash
   cd /path/to/project
   ```

3. Start a new session with continuation awareness:

   ```bash
   hermes --continue
   ```

If Hermes doesn’t pick up your session automatically:

- List available sessions:

  ```bash
  hermes sessions list
  ```

- Resume a specific one by ID:

  ```bash
  hermes --resume <session_id>
  ```

Use `hermes --continue` to resume work in your current terminal/workspace, which takes precedence over the globally newest conversation. To restore a specific earlier session, use `hermes --resume <session_id>`; this brings back that session and can restore the working directory that was saved with it—inspect the resulting directory to verify.

---

## 9. Common Troubleshooting Patterns

Symptom → Action:

- Command `hermes` not found
  - Ensure PATH includes `~/.local/bin`.
  - Run `source ~/.bashrc` or `source ~/.zshrc`, then try again.

- Authentication errors or no model response
  - From shell, run `hermes model` to re-check provider and API key.

- Hermes chats but doesn’t read files
  - Confirm you launched Hermes from within the correct project directory.
  - Check terminal backend: `hermes config get terminal.backend`. Should be `local`.
  - List tools: `/tools`; if missing, exit and run `hermes tools` to reconfigure.

- Custom endpoint or model issues
  - Verify base URL, model ID, tool calling support, and context limits in your provider’s settings.
  - Run `hermes doctor` to inspect configuration and dependency status.

- Stale or out-of-date Hermes version
  - Update: `hermes update`
  - Check-only: `hermes update --check`

---

## 10. Summary Checklist

After reading this page, you should be able to:

- [ ] Install Hermes CLI with the official installer and verify version.
- [ ] Connect a model provider and select an available model via `hermes model`.
- [ ] Set `terminal.backend` to local and navigate into a project directory.
- [ ] Start Hermes from the shell (`hermes`) inside the project directory.
- [ ] Confirm tools are enabled with `/tools` and directory context.
- [ ] Complete a file-reading task, cite paths/lines, and verify outputs manually.
- [ ] Quit with `/quit`, then resume later with `--continue` or `--resume <session_id>`.
- [ ] Diagnose basic setup issues using `hermes model`, `hermes doctor`, and PATH checks.

The next step: try a slightly more advanced task—ask Hermes to propose a small change to one of the project files (e.g., add a new status value), cite where it would fail, and explain how you’d test that change. Then let us know what results you get.

## Related Guides

- [AI Coding Agent Beginner Route](/docs/tutorials/ai-coding-agent-beginner-guide/)
- [Read an Unfamiliar Codebase with a Concrete Exercise](/docs/tools/prompt-engineering/templates/#read-codebase)
- [Find Code by Behavior with Jevgrep](/docs/tutorials/jevgrep-code-discovery/)
