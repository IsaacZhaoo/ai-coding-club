---
title: "First Persistent Coding Task with the OpenAI Agents API"
description: "Run a coding task with the OpenAI Agents API, continue it in a persistent session, inspect execution output, download artifacts, and recover after a stream disconnects."
keywords:
  - OpenAI Agents API tutorial
  - persistent coding agent session
  - OpenAI hosted sandbox
  - Agents API Python
  - Agents API artifacts
sidebar_position: 39
tags: [tutorial, openai, agent-engineering]
---

# First Persistent Coding Task with the OpenAI Agents API

By AI Coding Club

This tutorial shows how to run a small coding task in an OpenAI-managed sandbox, keep that conversation alive across multiple turns, improve the code, and download the result. You’ll learn to:

- Create `tree.py` in a hosted Linux workspace
- Inspect its actual execution output
- Add a `--max-depth` option in the same session
- Download the updated script
- Recover your work if the live stream disconnects

No fancy infrastructure required—just Python, the OpenAI SDK, and an API key with the right scopes.

## Prerequisites

Make sure you have:

- A running environment that supports Python 3 (local terminal is fine).
- An OpenAI Platform project where a model `gpt-6-astra` is enabled for the Agents API.

### Install the SDK

```bash
pip install --upgrade openai
```

The new SDK exposes beta features under `client.beta`. It automatically adds the required header:

- `OpenAI-Beta: agents=v1`

You do not need to set that manually.

### Export your API key

Set an environment variable in your application terminal (not inside the agent’s sandbox):

```bash
export OPENAI_API_KEY="sk-your-application-key"
```

Required scopes for this tutorial:

- `api.agents.read`
- `api.agents.write`
- `api.responses.write`

If any of these are missing, create a dedicated key in your OpenAI project’s access settings.

## Environment and Concepts

Application code runs on your machine; the agent’s host runs Python in a Linux environment at `/workspace`. A session stores conversation history and agent settings across turns, while each turn is a self-contained unit of work—from receiving your input to completing a terminal lifecycle event. One turn can include multiple tool calls (writing, running, checking files). Files saved under `/workspace/outputs` are published as immutable artifacts once their turn finishes. Connected sandboxes receive periodic keepalives between turns; if neither activity nor keepalives occur for an hour, the sandbox may expire, but published artifacts remain and should be downloaded before session deletion. Model inference and hosted sandbox usage are billed separately. Note: Agents API public beta launched September 10, 2026.

## Task 1: Create and Run `tree.py`

We’ll start by telling the agent to create a script that prints a readable directory tree, run it, and report the actual output.

### Initialize the session

```python
from pathlib import Path
from openai import OpenAI

client = OpenAI()

def consume(events):
    """
    Consume stream events, raising on errors and returning when a turn completes.
    """
    for event in events:
        print(event.to_json(indent=None), flush=True)

        if event.type == "agent.session.created":
            # Persist session ID for later recovery
            Path("session-id.txt").write_text(event.session.id)

        if event.type == "error":
            raise RuntimeError(event.error.message)

        if event.type in {"agent.session.failed", "agent.session.environment.failed"}:
            raise RuntimeError(event.type)

        # We care about the main turn completion, not subagents
        if (
            event.type in {
                "agent.session.turn.failed",
                "agent.session.turn.cancelled",
                "agent.session.turn.completed",
            }
            and event.turn.subagent_id is None
        ):
            if event.type != "agent.session.turn.completed":
                raise RuntimeError(event.type)
            return event.turn.id

    raise RuntimeError("Stream ended early; retrieve the saved session and items.")

with client.beta.agents.sessions.create(
    agent={
        "model": "gpt-6-astra",
        "instructions": "Write clean code, run it, and report the actual output.",
    },
    environment={"type": "openai_hosted"},
    input="Create tree.py, a Python script that prints a readable tree of the files in the current directory. Run it and show me the output.",
    stream=True,
) as events:
    first_turn_id = consume(events)

session_id = Path("session-id.txt").read_text().strip()
```

What just happened:

- A new session was created with an OpenAI-hosted environment.
- The agent generated `tree.py`, ran it in `/workspace`, and streamed events back.
- Call `consume()` to read events and immediately raise explicit API errors, session/environment failures, and root-turn failures or cancellations. It won’t flag every tool call failure—a completed turn can still contain successful steps despite some failed tools. For detailed output inspection (messages, tool calls, results), see the section below.

- We store the session ID so we can recover or extend the session later.

### Inspect the output

Look at the printed events for this turn. You should see something like:

- The agent writing code to `/workspace/tree.py`
- Invoking `python tree.py`
- Printing its actual stdout/stderr back to you

If execution output is missing, open the saved session items in order. Reopening a stream only delivers new events and cannot replay missed output. The initial prompt may request a script or run but won’t automatically export artifacts, so command-line stdout isn’t guaranteed to appear under `/workspace/outputs`. When work looks incomplete, review the saved session state, wait for the session to become idle, then ask for the missing step.

## Task 2: Improve with `--max-depth`

Now we’ll open an event stream, verify the session is idle, send a new request to add an option, run the updated script, and download it.

> Note: Opening an event stream is separate from submitting input. You must ensure the first turn has fully ended and the session is in `idle` status before sending more work. If the idle guard stops execution, inspect the saved state and retry once that condition is met.

### Check session status

```python
if client.beta.agents.sessions.retrieve(session_id).status != "idle":
    raise RuntimeError(
        "Inspect the session and wait for idle before the follow-up."
    )
```

If this fails, either:

- The previous turn is still running (wait a moment), or
- Something unexpected happened; review the last events and retry after confirming `idle`.

### Submit the second turn

We’ll ask the agent to add a `--max-depth` flag, run it, and save the updated script so we can download it.

```python
text = (
    "Add a --max-depth option to tree.py. Run python tree.py --max-depth 2 "
    "and report the actual output. Copy the updated script to "
    "/workspace/outputs/tree.py so I can download it."
)

with client.beta.agents.sessions.events.stream(session_id) as events:
    # Send the new input via the Events API
    client.beta.agents.sessions.events.create(
        session_id,
        events=[{
            "type": "agent.session.input.message",
            "input": [{"role": "user", "content": [{"type": "input_text", "text": text}]}],
        }],
    )

    # Consume the turn events
    completed_turn_id = consume(events)
```

Key points:

- `client.beta.agents.sessions.events.stream(session_id)` establishes a streaming channel.
- `events.create(...)` injects your new user message into that session.
- `consume()` returns when the main turn completes, just like before.

### Inspect the results

Check:

1. The printed output for `python tree.py --max-depth 2`. It should show only up to depth 2.
2. Whether `/workspace/outputs/tree.py` was saved (see next section).

If output looks wrong, you can:

- Resubmit with a clarification via the same session.
- Inspect the agent’s code and execution steps from the events log.

## Task 3: Download the Updated Script

The improved `tree.py` is published as an artifact tied to the turn ID. Here’s how to download it:

```python
def download_artifact(client, session_id, turn_id, path, destination):
    for artifact in client.beta.agents.sessions.artifacts.list(session_id):
        if artifact.turn_id != turn_id or artifact.path != path:
            continue
        with client.beta.agents.sessions.artifacts.with_streaming_response.content(
            artifact.id, session_id=session_id
        ) as response:
            response.stream_to_file(destination)
        return
    raise FileNotFoundError(f"No artifact for {path!r} in turn {turn_id}")

download_artifact(
    client, session_id, completed_turn_id, "/workspace/outputs/tree.py", "tree.py"
)
```

After downloading artifacts, inspect `tree.py` for a `--max-depth` option. Running locally:
```bash
python tree.py --max-depth 2
```
confirms the depth rule against your local filesystem. Remember that hosted and local directory contents differ; literal directory-tree output may not match exactly.

If no artifact appears:

- Verify you’re using the correct `turn_id` (it should be `completed_turn_id`).
- Check all artifacts for that session; sometimes paths differ slightly.
- Review the events log for any “file write” or “artifact created” messages.

## Task 4: Recovery When Streams or Connections Drop

Real-world sessions disconnect. The pattern below is usable in a separate Python process to inspect what remains saved.

### Inspect session state and items

```python
from pathlib import Path
from openai import OpenAI

client = OpenAI()
session_id = Path("session-id.txt").read_text().strip()

print(client.beta.agents.sessions.retrieve(session_id).to_json())

for item in client.beta.agents.sessions.items.list(session_id, order="asc", limit=100):
    print(item.to_json())
```

The recovery snippet fetches session metadata/status plus conversation and tool items in order, letting you verify whether the agent actually produced output and if the session is now idle. Artifact IDs, turn IDs, and paths come from `client.beta.agents.sessions.artifacts.list(session_id)`, not from the item list; your local application keeps track of what’s already downloaded. Turn lifecycle status is available via separate resources, though this recovery code doesn’t query them directly. Reopening a stream never replays missed events.

### Stopping an active turn (without losing context)

If you need to pause execution but keep the conversation intact:

```python
client.beta.agents.sessions.events.create(
    session_id,
    events=[{"type": "agent.session.input.cancel"}],
)
```

This cancels the current turn. You can later resume from the same session once it’s idle.

### Cleanup

Once you’ve downloaded all required files:

```python
client.beta.agents.sessions.delete(session_id)
```

If deletion fails with HTTP 409 during setup or execution, wait briefly and retry up to three times. Other errors should be inspected; retain the session ID if cleanup remains incomplete. The API can delete metadata before the physical sandbox fully clears.

## Common Pitfalls and Best Practices

- Don’t trust `turn.completed` alone as proof of success. Always inspect the actual command output and artifacts.
- Idle or a closed stream alone is not enough; you must see concrete results for each step.
- Filesystem lives inside the sandbox. Only saved outputs under `/workspace/outputs` become durable artifacts.
- Published artifact copies survive sandbox expiry, but the live filesystem does not.
- Closing a stream does not cancel work, and starting a new stream does not replay missed events. Always read saved state before submitting more.
- Keep one observable execution result (stdout) and a known output path per task for easy recovery and verification.

## Quick Reference

- SDK base: `client.beta.agents`
- Create session: `client.beta.agents.sessions.create(..., stream=True)`
- Stream events: `client.beta.agents.sessions.events.stream(session_id)`
- Inject input: `client.beta.agents.sessions.events.create(session_id, events=[{"type": "agent.session.input.message", ...}])`
- List artifacts: `client.beta.agents.sessions.artifacts.list(session_id)`
- Download artifact: `client.beta.agents.sessions.artifacts.with_streaming_response.content(artifact.id, session_id=session_id)`
- Retrieve state: `client.beta.agents.sessions.retrieve(session_id)`
- List items: `client.beta.agents.sessions.items.list(session_id, order="asc")`
- Cancel turn: inject `{"type": "agent.session.input.cancel"}`
- Delete session: `client.beta.agents.sessions.delete(session_id)`

## Sources

For deeper details, refer to the official docs:

- [Quickstart](https://developers.openai.com/api/docs/guides/agents-api/quickstart)
- [Sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions)
- [Events and recovery](https://developers.openai.com/api/docs/guides/agents-api/sessions/events)
- [Files and artifacts](https://developers.openai.com/api/docs/guides/agents-api/environments/files)
- [Hosted sandbox lifetime](https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted)
- [Manage sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions/manage)
- [API changelog](https://developers.openai.com/api/docs/changelog)

This tutorial is built around those references and the concrete behavior you’ll see in the Agents API today.

## Related Guides

- [Coding Agent Harness Explained](/docs/tutorials/coding-agent-harness-explained/)
- [Coding Agent Evals: Turn Traces into a Quality Gate](/docs/tutorials/coding-agent-evals-guide/)
