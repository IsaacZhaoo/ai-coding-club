# Agent Skills Loadout Audit Fixture

This standard-library fixture audits a directory of Agent Skills as one competing catalog rather than testing one Skill in isolation.

It provides three deliberately separate layers:

1. specification checks for `SKILL.md` discovery, required metadata, naming, and description length;
2. a cheap lexical smoke test for description overlap and obvious routing ambiguity;
3. scoring for activation records captured from a real Agent client.

The lexical smoke test is not a model benchmark. It cannot reliably interpret every boundary or negation. Its two known false activations in the bundled cases are preserved because they demonstrate why static matching cannot replace real Agent traces.

## Run the tests

```bash
python3 -m unittest -v test_skill_loadout.py
```

## Audit the bundled five-Skill loadout

```bash
python3 skill_loadout.py audit \
  --skills-dir skills \
  --cases cases.jsonl \
  --max-estimated-tokens 300
```

The catalog estimate uses a transparent four-characters-per-token heuristic. It is a local budget signal, not a provider tokenizer or a universal billing measurement.

## Audit a real repository loadout

```bash
python3 skill_loadout.py audit \
  --skills-dir /path/to/project/.agents/skills \
  --overlap-threshold 0.55
```

## Score real activation records

Capture one JSON object per run:

```json
{"case_id":"python-pytest-failure","run":1,"selected_skill":"python-test-fixer","agent":"codex-cli"}
```

Use `null` when no Skill was activated, then run:

```bash
python3 skill_loadout.py score \
  --cases cases.jsonl \
  --activations activations.codex-smoke-20260723.jsonl
```

`activations.example.jsonl` is synthetic test data used to verify scoring math. It must not be presented as measured Agent performance.

## Publication boundary

Before publishing benchmark-like claims, expand the real activation set, repeat prompts, keep train and validation cases separate, and preserve the client logs that prove which `SKILL.md` files were loaded. The current Codex smoke test only verifies one positive activation and one near-miss non-activation.
