from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

from trace_audit import (
    load_jsonl,
    summarize_codex,
    summarize_portable,
    validate_spans,
)


FIXTURE_ROOT = Path(__file__).resolve().parent


class PortableTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spans = load_jsonl(FIXTURE_ROOT / "portable-trace.example.jsonl")
        cls.report = summarize_portable(cls.spans)

    def test_loads_nine_portable_spans(self) -> None:
        self.assertEqual(9, len(self.spans))

    def test_reports_span_kinds(self) -> None:
        self.assertEqual(
            {
                "agent": 1,
                "evaluation": 1,
                "handoff": 1,
                "model": 2,
                "skill": 1,
                "tool": 3,
            },
            self.report["kind_counts"],
        )

    def test_reports_errors_retry_and_handoff(self) -> None:
        self.assertEqual(2, self.report["error_spans"])
        self.assertEqual(1, self.report["retry_spans"])
        self.assertEqual(1, self.report["handoff_spans"])

    def test_sums_synthetic_usage_and_cost(self) -> None:
        self.assertEqual(1000.0, self.report["input_tokens"])
        self.assertEqual(150.0, self.report["output_tokens"])
        self.assertEqual(0.016, self.report["cost_usd"])

    def test_reports_root_duration_and_timing_coverage(self) -> None:
        self.assertEqual(8000, self.report["root_duration_ms"])
        self.assertEqual(9, self.report["timed_spans"])

    def test_rejects_unknown_parent(self) -> None:
        broken = [dict(span) for span in self.spans]
        broken[1] = {**broken[1], "parent_span_id": "missing"}
        with self.assertRaisesRegex(ValueError, "Unknown parent_span_id"):
            validate_spans(broken)


class CodexEventTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = load_jsonl(FIXTURE_ROOT / "codex-diagnosis-20260723.jsonl")
        cls.report = summarize_codex(cls.events)

    def test_counts_real_tool_calls_and_failures(self) -> None:
        self.assertEqual(5, self.report["tool_calls"])
        self.assertEqual(3, self.report["successful_tool_calls"])
        self.assertEqual(2, self.report["failed_tool_calls"])
        self.assertEqual([127, 1], self.report["failed_tool_exit_codes"])

    def test_run_completed_despite_failed_tool_calls(self) -> None:
        self.assertEqual("completed", self.report["turn_status"])

    def test_preserves_observed_token_usage(self) -> None:
        self.assertEqual(
            {
                "input_tokens": 74858,
                "cached_input_tokens": 59904,
                "cache_write_input_tokens": 0,
                "output_tokens": 749,
                "reasoning_output_tokens": 201,
            },
            self.report["usage"],
        )

    def test_reports_missing_duration_cost_and_handoffs(self) -> None:
        self.assertFalse(self.report["duration_available"])
        self.assertFalse(self.report["cost_available"])
        self.assertEqual(0, self.report["handoff_events"])

        text_only = [
            *self.events,
            {
                "type": "item.completed",
                "item": {
                    "type": "agent_message",
                    "text": "No cost data was emitted.",
                },
            },
        ]
        self.assertFalse(summarize_codex(text_only)["cost_available"])

        explicit_cost = [*self.events, {"type": "metric", "cost_usd": 0.01}]
        self.assertTrue(summarize_codex(explicit_cost)["cost_available"])

    def test_cli_emits_machine_readable_json(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "trace_audit.py",
                "codex",
                "--events",
                "codex-diagnosis-20260723.jsonl",
            ],
            cwd=FIXTURE_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(5, json.loads(completed.stdout)["tool_calls"])


if __name__ == "__main__":
    unittest.main()
