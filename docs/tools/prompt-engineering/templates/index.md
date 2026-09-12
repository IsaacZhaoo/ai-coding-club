---
title: Prompt Templates
description: Ready-to-use prompt templates for common coding tasks
---

import FAQSchema from '@site/src/components/FAQSchema';

# Prompt Templates

**50+ battle-tested templates for AI coding**

Ready-to-use prompt templates that get better results from AI assistants. Organized by task type for quick reference.

<FAQSchema
  items={[
    {
      question: 'Which prompt template should I use first?',
      answer: 'Start with debugging templates because they teach you to provide context, errors, and expected behavior.',
    },
    {
      question: 'How do I customize these templates?',
      answer: 'Replace the placeholders with your real code, constraints, and verification steps.',
    },
    {
      question: 'How do I know a prompt worked?',
      answer: 'The output should be testable and you should be able to verify it with lint, tests, or a reproducible example.',
    },
  ]}
/>

## Template Categories

### 🐛 [Debugging](/docs/tools/prompt-engineering/templates/debugging)
12 templates for finding and fixing bugs faster.

### 🔄 [Refactoring](/docs/tools/prompt-engineering/templates/refactoring)
Templates for safe refactors, migrations, and code cleanup.

### ✅ [Testing](/docs/tools/prompt-engineering/templates/testing)
Templates for unit/integration tests, edge cases, and regression coverage.

### 📝 [Documentation](/docs/tools/prompt-engineering/templates/documentation)
Templates for README, docstrings, API docs, and troubleshooting guides.

### 🔍 [Code Review](/docs/tools/prompt-engineering/templates/code-review)
Templates for review checklists, security review, and actionable feedback.

### 🧭 [Planning](/docs/tools/prompt-engineering/templates/planning)
Templates for plans, risk checks, and step-by-step execution.

---

## Read an unfamiliar codebase: trace one command {#read-codebase}

Pick one command in an unfamiliar repository. Before running it, read the source to locate its entry point, trace each call with file and line evidence, and predict its output. Then run it and compare. This exercise uses a small fixed fixture so every step can be checked against the source.

**Download the exercise:** <a href="/examples/codebase-reading-lab.zip">codebase-reading-lab.zip</a>

Unzip it and change into `codebase-reading-lab`. Python 3 must already be installed. The program uses the standard library only — no third-party packages, login, API key, network connection, or database.

The directory contains five files: `main.py`, `repository.py`, `query.py`, `tasks.json`, and `README.md`.

---

### Copyable prompt

Use this prompt with your own AI assistant. Fill `[COMMAND]` with the command you want to trace and `[directory tree / labeled relevant files]` with the file contents described in the supply instructions below. The prompt is reusable for any small command; the exercise-specific details are outside it.

```
I am supplying [COMMAND] and the relevant source files from a small repository.
[directory tree / labeled relevant files]

Before doing anything else, list every file you can actually read from what I have supplied. Do not assume any file exists based on an import or reference alone — an unsupplied file is not evidence it is absent at runtime or that it will cause an import error.

Then, for the supplied source:
- Identify the actual entry point and how arguments and defaults are handled.
- Trace one representative input through every call. Discover the actual call order from the source — including whether calls are sequential or nested — rather than assuming a fixed pattern. Do not infer what a function does from its name; read its body. If a file is missing, request it before predicting output that depends on it.
- For each step, cite file and line number with a short relevant code excerpt, and explain why that step runs.
- Separate what you can infer from the source from what would only be confirmed by execution. If you have not run the command, label the result a prediction.
- Do not edit, refactor, or review the code. Analysis only.
- State any files you cannot read and any uncertainty clearly, rather than inventing behavior.

If you are unable to inspect files or run commands in this session, tell me, and I will supply the directory tree and labeled file contents. Report a prediction only.
```

**For this exercise,** set `[COMMAND]` to `python3 main.py`.

**What to supply:** paste the complete contents of `main.py`, `repository.py`, `query.py`, and `tasks.json`, each labeled by filename, in one message or as attachments if your chat supports reading them. A ZIP or directory tree alone does not give the assistant access to source. `README.md` is for you to read; the assistant does not need it as input.

If your chat requires multiple messages, tell the assistant to wait for all files before analyzing, then signal when you have finished sending. Ask the assistant to confirm which files it can actually read; if attachments fail, paste labeled text instead.

Prompting cannot guarantee a correct answer. Check every cited line yourself. Without Python, you can inspect the source and compare predictions, but execution verification remains pending until you run the command.

---

### Compact answer key

`main.py:19–20` — `if __name__ == "__main__": main()` is the entry point.

`main.py:11–13` — `argparse` sets `--status` default to `"open"` and defaults `--data` to the path of `tasks.json` next to `main.py`, independent of your working directory. An unsupported `--status` value fails argparse validation.

`main.py:14` — `main` calls `load_tasks(args.data)` → `repository.py:4–6`, which opens the file and returns `json.load(source)`.

`main.py:15` — `main` then calls `select_tasks(tasks, args.status)` independently → `query.py:1–3`, which list-comprehends tasks whose `"status"` matches, then sorts by `"id"` lexicographically. `load_tasks` and `select_tasks` are called sequentially from `main`; neither calls the other.

`main.py:16` — `print(json.dumps(result, ensure_ascii=False))` prints the result. `json.dumps` is evaluated first; its return value is then passed to `print`.

**Why T2 is excluded by default:** its `"status"` is `"done"`; the default filter is `"open"`.

**Why T1 precedes T3:** `sorted(..., key=lambda task: task["id"])` sorts lexicographically; `"T1" < "T3"`.

---

### Expected output

**`python3 main.py`** (default `--status open`):

```json
[{"id": "T1", "title": "Find the entry point", "status": "open"}, {"id": "T3", "title": "Write a usage note", "status": "open"}]
```

**`python3 main.py --status done`**:

```json
[{"id": "T2", "title": "Run the example", "status": "done"}]
```

---

### Self-check

After running both commands, confirm:

- Your trace cites an actual file and line for each call, not just a function name.
- You explained why T2 is absent from the default output using a line from `query.py`.
- You explained why T1 appears before T3 using the sort key in `query.py`.
- Your terminal output matches both JSON blocks above exactly.
- You noted that changing `--status` changes selection only; `tasks.json` is never written.

---

### Applying this to your own project

When you want to trace one command in your own codebase, supply only the files directly involved in that command's path — entry point, any modules it imports for that path, and the relevant input file. Keep the scope small. This exercise covers one command in a five-file fixture; it is not a method for understanding a whole repository.

---

## Quick Start

1. Choose a template category above
2. Copy the template you need
3. Fill in your specific details
4. Paste into your AI assistant
5. Iterate based on results

---

## Pro Tips

- **Be Specific**: Add context and constraints
- **Provide Examples**: Show what you want
- **Iterate**: Refine based on first response
- **Save Winners**: Keep templates that work well

---

## FAQ

### Which prompt template should I use first?

Start with debugging templates because they teach you to provide context, errors, and expected behavior.

### How do I customize these templates?

Replace the placeholders with your real code, constraints, and verification steps.

### How do I know a prompt worked?

The output should be testable and you should be able to verify it with lint, tests, or a reproducible example.
