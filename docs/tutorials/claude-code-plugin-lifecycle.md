---
title: "Managing Claude Code Plugins: Install, Verify, Update, and Troubleshoot"
description: "Install, verify, update, and remove Claude Code plugins with commit-commands. Understand local, project, and user scopes, reload sessions, and troubleshoot loading."
keywords:
  - "Claude Code plugins"
  - "Claude Code plugin install"
  - "commit-commands"
  - "Claude Code marketplace"
  - "reload-plugins"
sidebar_position: 35
tags: [tutorial, claude, plugins]
---

# Managing Claude Code Plugins: Install, Verify, Update, and Troubleshoot

Claude Code plugins can package sophisticated capabilities—skills, custom agents, lifecycle hooks, and even full MCP or LSP servers—directly into your terminal workflow. Think of the marketplace as a curated catalog where each plugin is identified by a clear source and a stable install ID (`plugin-name@marketplace-name`).

This guide walks you through:
- Installing an official plugin for local use
- Verifying it loaded correctly and exposing usable skills
- Managing updates, scopes, and removals via the shell or interactive panel
- Troubleshooting when commands don’t appear or sessions behave unexpectedly

We’ll focus on practical commands with `commit-commands` as a running example. It’s small, well-documented, and demonstrates everything from scope settings to command execution within Git workflows.

---

## Quick Start: Install the Official Commit Plugin

Assume you’re in a project directory with Git initialized. Run these commands in your OS shell (bash, zsh, etc.) to register and install the plugin locally:

```bash
# Register the official marketplace (skip if already present)
claude plugin marketplace add anthropics/claude-plugins-official --scope local

# Install the plugin in local scope
claude plugin install commit-commands@claude-plugins-official --scope local

# Confirm installation and enabled status
claude plugin list
```

The `--scope local` flag is key here. It tells Claude Code that this plugin applies only to this specific project directory, keeping your personal settings clean and respecting collaborators’ environments.

Shell installation takes effect in your next Claude Code session. To apply it immediately inside an already running session, type:

```text
/reload-plugins
```

Inside that same session, `/plugin install commit-commands@claude-plugins-official` opens the plugin’s details page where you can inspect components and choose its scope.

---

## Verifying Installation and Capabilities

### 1. Check Installed Status via CLI

Run:

```bash
claude plugin list
```

Each entry shows `Version`, `Scope`, and `Status`. A `Status` of `enabled` means the plugin is enabled in your settings; whether it has loaded in the current session is a separate runtime state.

### 2. Inspect Interactive Panel

Inside your running Claude Code TERMINAL SESSION, type `/plugin`:

- **Installed** — Lists every plugin, showing both those actively enabled and those present but disabled.
- **Errors** — reports loading problems if any occurred.
- **Marketplaces** — manages sources and repository registrations.

The plugin’s **DETAILS** page includes a Will install section that previews components such as subagents, commands, and servers before or after activation.

### 3. Locate Exposed Skills

In the running session, type `/` to open command search, then locate:

```
/commit-commands:commit
```

Finding this command confirms the plugin is wired into your session. When invoked later for real Git work, it stages relevant files and creates a commit. Note that hook or server-only plugins may expose no skill-menu entry at all.

---

## Understanding Scopes and Configuration

Claude Code supports three scope levels, each targeting different areas of your environment:

| Scope     | Location                                      | Behavior                                                            |
|-----------|-----------------------------------------------|----------------------------------------------------------------------|
| `user`    | `~/.claude/settings.json`                      | Applies globally for this user on this machine.                      |
| `project` | `<repo>/.claude/settings.json` (Git-tracked)  | Shared across collaborators; can be committed safely.                |
| `local`   | `<repo>/.claude/settings.local.json`           | Private to your machine and repo; overrides project/user settings.   |

**Important notes:**
- Overrides apply vertically: local > project > user.
- A shared project enable entry does *not* download the plugin onto collaborators’ machines. Each collaborator must still run `claude plugin install` in their environment.
- Local scope is ideal for testing or experimenting without affecting other projects.

---

## Interactive Installation and Review

Use `/plugin` to open Discover; `/marketplace` is a convenient alias. When you run `/plugin install commit-commands@claude-plugins-official`, you’ll see details plus scope choices. For more control, find the plugin’s community catalog repository containing `.claude-plugin/marketplace.json` (even if it defines only one plugin). A plugin’s `.claude-plugin/plugin.json` describes that single plugin; it does not describe a marketplace.

From your shell:
```text
claude plugin marketplace add OWNER/REPO --scope local
```
Replace `OWNER/REPO` with the actual repository path and confirm the registered catalog name. Then install from it:
```text
claude plugin install PLUGIN@MARKETPLACE --scope local
```
Swap `PLUGIN` for the install ID (e.g., `commit-commands`) and `MARKETPLACE` for the registered name you just saw.

To verify, run:
```text
claude plugin marketplace list  # checks registered sources
claude plugin list             # checks installed plugins
```

---

## Updating Plugins and Marketplaces

Claude Code manages two layers of updates:

### Marketplace Update
Refreshes the catalog metadata for a registered marketplace (e.g., `anthropics/claude-plugins-official`). Use this when new plugins appear or existing ones change their IDs:

```bash
claude plugin marketplace update claude-plugins-official
```

### Plugin Update

In the shell, run:

```bash
claude plugin update commit-commands@claude-plugins-official --scope local
```

Your running session retains the previously loaded version. To load the updated plugin:

- Start a new session, or
- Type this INSIDE the existing session:

```text
/reload-plugins
```

---

## Troubleshooting: When Commands Don’t Appear or Installation Fails

1) Ensure the source is registered: run `claude plugin marketplace list`.
2) Use the full `PLUGIN@MARKETPLACE` form to avoid ambiguity; bare names are legal but less reliable.
3) Confirm Scope and Status enabled with `claude plugin list`. Remember local > project > user configuration priority. If disabled, enable via Installed or:
   ```text
   claude plugin enable commit-commands@claude-plugins-official --scope local
   ```
4) Check the Errors panel for the exact loading/configuration message and fix its cause.
5) Inside the running session, `/reload-plugins` applies changes. If it asks to accept prompt-cache invalidation from changing MCP/LSP tools, use `/reload-plugins --force`; starting a new session is an alternative.
6) If project settings enable a plugin missing locally, follow the scope-specific installation command reported by Claude Code.

---

## Lifecycle Management: Disable, Uninstall, and Clean Up

### Toggle Enable/Disable
Use these opposite commands to control whether a plugin runs:
```text
claude plugin disable commit-commands@claude-plugins-official --scope local
claude plugin enable commit-commands@claude-plugins-official --scope local
```
Disabling changes the enabled setting while preserving installation and data.

### Uninstall a Plugin
Remove an install for a specific scope:
```text
claude plugin uninstall commit-commands@claude-plugins-official --scope local
```
Persistent data lives at `~/.claude/plugins/data/<id>/` and is shared by plugin ID across scopes. Data is deleted only when the LAST installation scope for that plugin is removed. You can optionally keep it with `--keep-data`, though uninstall still clears the enabled setting.

### Remove a Marketplace Catalog
Delete a registered catalog source:
```text
claude plugin marketplace remove claude-plugins-official
```
Without `--scope`, this removes catalog declarations across scopes; when the last declaration is gone, the catalog’s plugins are uninstalled. This action is broader than uninstalling a single plugin, so treat it carefully.

---

## Security and Execution Privileges

Plugins run with user privileges on your machine. Before installing any plugin—especially those exposing hooks or MCP servers:

- **Inspect the source**: Check `.claude-plugin/plugin.json`, `skills/`, `hooks/hooks.json`, and `.mcp.json` in the official repo.
- **Understand execution**: Hooks and MCP processes can execute local code or connect to external services.
- **Scope controls settings, not sandboxing**: Local scope defines where settings apply; it doesn’t isolate filesystem access or limit permissions.

The practical question is always: *What code runs? What network/service does it reach?*

---

## Best Practices Summary

- Use `--scope local` for personal experimentation in a project.
- Prefer the official marketplace (`anthropics/claude-plugins-official`) for trusted plugins.
- Verify installation with `claude plugin list`, then `/plugin` → Installed and Errors.
- Locate skills via `/` or `/commit-commands:commit`.
- Apply changes with `/reload-plugins` before expecting updated tooling.
- Keep settings organized by scope to avoid unexpected overrides in collaboration.

---

## Further Reading

- Installation & management docs: https://code.claude.com/docs/en/discover-plugins
- CLI reference: https://code.claude.com/docs/en/plugins/cli-reference
- Troubleshooting guide: https://code.claude.com/docs/en/plugins/troubleshooting
- Security and execution privileges: https://code.claude.com/docs/en/plugins/security
- Example source: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/commit-commands

Now you have a complete, repeatable workflow for installing, verifying, updating, and managing Claude Code plugins in your development environment.

## Related Guides

- [Claude Code Beginner Guide](/docs/tutorials/claude-code-guide/)
- [Claude Code Skills, Hooks, and MCP](/docs/tutorials/claude-code-skills-hooks-mcp/)
