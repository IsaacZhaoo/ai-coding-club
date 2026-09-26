---
title: "Run Kev Locally: A Choice Classification for Support Tickets (Apple Silicon Tutorial)"
description: "Run Kev-0.8B locally on Apple Silicon, send a Choice request for support ticket routing, and understand model metadata, probabilities, and confidence."
keywords:
  - "Kev local deployment"
  - "Kev-0.8B"
  - "Apple Silicon"
  - "local decision model"
  - "Choice API"
sidebar_position: 33
tags: [tutorial, agent-engineering, local-models]
---

# Run Kev Locally: A Choice Classification for Support Tickets (Apple Silicon Tutorial)

If you’re an application or agent developer comfortable with the terminal and HTTP, and you want to move one text-classification decision into a local service on an Apple Silicon Mac, this tutorial will get you from zero to running Kev-0.8B in minutes.

We’ll:
- Install Kev locally
- Start its inference endpoint
- Submit a sample support ticket
- Inspect the model, read the Choice response, and understand the fields your app needs before routing tickets automatically

After reading, you should be able to:
- Launch the local server
- Confirm it’s loaded via `/v1/models`
- Send a single structured `POST /v1/systemone` request
- Decode the department assignment, option probabilities, and confidence

All examples use your local loopback address: `127.0.0.1:8009`. The server is unauthenticated by default for development; in production, add auth or network isolation as needed.

## Prerequisites

You need:
- An Apple Silicon Mac (M1/M2/M3 recommended)
- Git
- `uv` (modern Python/package manager)
- Python 3.12 or 3.13
- Basic terminal comfort with cloning repos, running scripts, and using `curl`
- Internet access for the initial model download

Kev’s Python constraint is `>=3.12,<3.14`; the project uses `.python-version` to select 3.13 when possible. `uv` handles the environment cleanly.

## What Is Kev?

Kev is a community-built family of locally runnable decision models, similar in spirit to Jev but tuned for structured outputs you can plug directly into workflows. 

- **Kev-0.8B** uses Qwen3.5-0.8B-Base and returns structured decisions (Choice, Scoring, etc.).
- The project generally recommends starting with **Kev-4B**, but this tutorial deliberately starts with 0.8B so you can get a working integration quickly on most Macs.
- On Apple Silicon, Kev uses MLX automatically; the backend is selected by the server based on your hardware.

Once the first request works, you can swap in your own categories, multi-intent tickets, and thresholds for automatic routing or human review.

## Step 1: Clone and Prepare Kev

Open your terminal and navigate to your projects directory (or create one):

```bash
mkdir -p ~/projects
cd ~/projects
```

Clone the repository:

```bash
git clone https://github.com/jaredpalmer/kev.git
cd kev
```

Install serving dependencies with `uv`:

```bash
uv sync --extra serve
```

For more direct instructions, see the official Kev run guide at [https://github.com/jaredpalmer/kev#run-it-locally](https://github.com/jaredpalmer/kev#run-it-locally).

This step:
- Installs all Python requirements
- Pulls MLX on Apple Silicon
- Prepares the server to load models

If you see a “resolving” or “downloading” prompt, let it finish. The first startup will then download both the adapter and base model weights.

## Step 2: Start the Local Server

In the same terminal (keep this window open), start Kev with the 0.8B model on port 8009:

```bash
uv run --extra serve python -m kev.serve \
  --run jaredpalmer/kev-0.8b \
  --port 8009
```

For detailed API and server hints, see [https://github.com/jaredpalmer/kev#api](https://github.com/jaredpalmer/kev#api).

You should see output similar to:

- Model loading messages
- A line indicating the backend (typically MLX on Apple Silicon)
- A binding message like `Running on http://127.0.0.1:8009`

Leave this terminal running. The server binds to `127.0.0.1` by default, so all examples below use that loopback address.

## Step 3: Inspect the Loaded Model

From a second terminal (or a new tab), verify the server is alive and inspect its model metadata:

```bash
curl http://127.0.0.1:8009/v1/models
```

You should see JSON similar to:

```json
{
  "models": [
    {
      "name": "kev-latest",
      "run": "jaredpalmer/kev-0.8b",
      "base": "Qwen/Qwen3.5-0.8B-Base",
      "device": "mps",
      "backend": "mlx",
      "dtype": "bfloat16"
    }
  ]
}
```

Key fields:
- `name`: logical model identifier used in requests (`kev-latest`)
- `run`: checkpoint being served
- `base`: underlying base model
- `device/backend/dtype`: tells you what hardware and precision are active

This is your control signal: if this call fails or returns an empty array, the server isn’t running correctly. Restart using Step 2 as needed.

## Step 4: Submit a Support Ticket for Classification

Kev’s core API endpoint for structured decisions is `POST /v1/systemone`. It accepts:
- A `model` identifier (`kev-latest` or `jev-latest`)
- A `state` string (the input text)
- A `questions` object keyed by question ID, each defining the type and criteria

The sample below classifies a billing ticket into one of three departments: Billing, Technical, or Sales. This is exactly what you’d send to a local routing service.

From your second terminal, run:

```bash
curl http://127.0.0.1:8009/v1/systemone \
  -H 'Content-Type: application/json' \
  --data-binary @- <<'JSON'
{
  "model": "kev-latest",
  "state": "Hi, I was charged twice for my March invoice (order #4471) and the refund I was promised last week still hasn't arrived. I've emailed three times. Please fix this today or I will dispute the charge with my bank.",
  "questions": {
    "team": {
      "type": "choice",
      "instructions": "Which team should handle this ticket?",
      "criteria": {
        "Billing": "Payments, invoices, refunds",
        "Technical": "Bugs, outages, integrations",
        "Sales": "Pricing questions, upgrades, new contracts"
      }
    }
  }
}
JSON
```

You should get a JSON response that includes an `answers` object with your chosen field populated. This JSON response, taken directly from mandu5’s independent publicly documented Kev-0.8B compatibility run, exemplifies the expected output format:

```json
{
  "answers": {
    "team": {
      "type": "choice",
      "choice": "Billing",
      "confidence": 0.9507,
      "probabilities": {
        "Billing": 0.9671,
        "Technical": 0.0142,
        "Sales": 0.0187
      }
    }
  }
}
```

These specific values (Billing=0.9671 / confidence=0.9507) come from mandu5's independent choice-basic test of Kev-0.8B on an M1 Pro with 16 GB RAM, running MLX in bfloat16 as documented in their September 24, 2026 run: [https://github.com/mandu5/jevcompat/blob/main/results/kev/RUN.md](https://github.com/mandu5/jevcompat/blob/main/results/kev/RUN.md) (full report at [https://github.com/mandu5/jevcompat/blob/main/results/kev/report.json](https://github.com/mandu5/jevcompat/blob/main/results/kev/report.json)). A new input or model configuration will change these numbers.

## Step 5: Understand the Response Fields

Your application will almost certainly read from `answers.team`. Here’s how to interpret each field in that object:

- `type`: Always `"choice"` for a multi-option classification.
- `choice`: The single selected option name (e.g., `"Billing"`). This is your routing key.
- `confidence`: A normalized measure of how strongly the model favors this choice over a uniform distribution.
  - For 3 options, confidence = (max_probability − 1/3) / (1 − 1/3).
  - With max_probability = 0.9671, confidence ≈ 0.9507.
- `probabilities`: A dictionary mapping each option to its likelihood:
  - `"Billing": 0.9671`
  - `"Technical": 0.0142`
  - `"Sales": 0.0187`

Important notes:
- The `confidence` and `probabilities` describe the output distribution, not a measured accuracy on your data.
- Real accuracy is task-specific; you’ll need labeled examples to calibrate thresholds and assess reliability.
- Different weights, input phrasing, or temperature/settings (if exposed) will change these numbers.

## Step 6: Wire Into an Application Flow

In your app (Python, Node, Go, etc.), the workflow is straightforward:

1. Normalize incoming support tickets into a `state` string and map your categories to `criteria`.
2. POST to `/v1/systemone` with your question ID and criteria.
3. On success:
   - Use `answers.<questionId>.choice` as your routing key (e.g., set department = “Billing”).
   - Optionally log or evaluate `probabilities` to decide whether to flag for review:
     - Example heuristic: if highest probability < 0.7, route to human triage.
4. On error:
   - Log the HTTP status and body
   - Provide a fallback (e.g., default queue, alert operator)

Because Kev returns structured JSON by design, you don’t need additional parsing libraries beyond standard JSON handling.

## Going Further

Once this works end-to-end, consider these next steps:

- **Swap in your own categories**: Replace the sample criteria with your real departments or tags.
- **Use multi-question routing**: Add questions like `priority`, `urgency`, or `requires_intervention` to build richer workflows.
- **Experiment with Kev-4B**: If you have a Mac with ~32 GB RAM, change:
  ```bash
  --run jaredpalmer/kev-0.8b
  ```
  to:
  ```bash
  --run jaredpalmer/kev-4b
  ```
  and repeat the tests. The same API; different model capacity.
- **Test on real data**: Run a batch of past tickets through Kev, compare its `choice` decisions with your historical labels, and adjust confidence thresholds accordingly.

## Final Notes

- This tutorial intentionally uses Kev-0.8B for an accessible first integration. The underlying API and response shape are stable across the model family.
- All examples use the local loopback address (`127.0.0.1:8009`). For production, consider HTTPS, authentication, and rate limiting.
- Kev is community-driven. Check the official repository for updates to models, API hints, or new capabilities.

You now have a working local Choice classifier for support tickets on an Apple Silicon Mac. Next, replace the sample ticket with your real data and let Kev start making routing decisions in your own infrastructure.

## Related Guides

- [Where Jev Fits in a Coding Agent Workflow](/blog/jev-coding-agent-workflow/)
- [Coding Agent Evals Guide](/docs/tutorials/coding-agent-evals-guide/)
