---
title: "Supervising Long Claude Code Tasks in tmux"
description: "Detach from a tmux session and reconnect to check a long Claude Code task. Practice with a checkpoint script, then verify the diff and test results."
tags: ["tutorial", "coding-assistant"]
---

# Supervising Long Claude Code Tasks in tmux

Open a terminal in an empty directory and place <a href="/examples/resume-claude-code-tmux/checkpoint.sh" download="checkpoint.sh">checkpoint.sh</a> there. Start the shell inside that folder, then launch tmux with an unused session name: `tmux new -s lesson`. Immediately run `bash checkpoint.sh` to create two files—progress.log and result.txt. Press Ctrl+b, release, then press d to detach cleanly.

From the same host and user, verify the session exists with `tmux ls`. Attach it back with `tmux attach -t lesson`. Let the shell complete; when ready, check outputs: `cat progress.log` should print start then ready; `cat result.txt` returns 42. This isolates completion proof from session presence—ideal for long tasks that finish independently of your terminal state.

## Interact with Claude Code

Inside the new tmux window, navigate to a disposable project folder.

```sh
claude
```

For demonstration, request Claude to:

- Inspect one existing source file
- Propose one small, safe change
- Run one existing test
- Summarize results and stop

Keep permissions normal; note that detaching alone never approves system prompts—only explicit input does so. After the task completes, inspect the transcript for context, review `git status --short`, and examine changes with `git diff`. If untracked files appear, inspect them separately to confirm they’re intentional. Re-run the real test to validate the modification. When done, return to your shell and type `exit` to close the practice session without leaving lingering tmux attachments.
