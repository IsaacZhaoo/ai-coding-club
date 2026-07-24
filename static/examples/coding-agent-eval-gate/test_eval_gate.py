from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from eval_gate import evaluate_files


FIXTURE_ROOT = Path(__file__).resolve().parent


class EvalGateTests(unittest.TestCase):
    def test_preserved_real_baseline_passes_the_quality_gate(self) -> None:
        report = evaluate_files(
            FIXTURE_ROOT / "eval-cases.example.jsonl",
            FIXTURE_ROOT / "baseline-trials.example.jsonl",
        )

        self.assertEqual(
            {
                "case_count": 1,
                "trial_count": 1,
                "passed_trials": 1,
                "failed_trials": 0,
                "gate_passed": True,
                "results": [
                    {
                        "case_id": "average-empty-diagnosis",
                        "trial_id": "codex-diagnosis-20260723",
                        "passed": True,
                        "failed_checks": [],
                    }
                ],
            },
            report,
        )

    def test_synthetic_wrong_fix_fails_the_answer_check(self) -> None:
        report = evaluate_files(
            FIXTURE_ROOT / "eval-cases.example.jsonl",
            FIXTURE_ROOT / "regression-trials.synthetic.jsonl",
        )

        self.assertEqual(
            {
                "case_count": 1,
                "trial_count": 1,
                "passed_trials": 0,
                "failed_trials": 1,
                "gate_passed": False,
                "results": [
                    {
                        "case_id": "average-empty-diagnosis",
                        "trial_id": "synthetic-wrong-fix",
                        "passed": False,
                        "failed_checks": ["answer_contains_all"],
                    }
                ],
            },
            report,
        )

    def test_cli_returns_nonzero_and_json_for_a_failed_gate(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "eval_gate.py",
                "--cases",
                "eval-cases.example.jsonl",
                "--trials",
                "regression-trials.synthetic.jsonl",
            ],
            cwd=FIXTURE_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(1, completed.returncode, completed.stderr)
        self.assertFalse(json.loads(completed.stdout)["gate_passed"])

    def test_cli_returns_zero_and_json_for_a_passing_gate(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "eval_gate.py",
                "--cases",
                "eval-cases.example.jsonl",
                "--trials",
                "baseline-trials.example.jsonl",
            ],
            cwd=FIXTURE_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["gate_passed"])

    def test_cli_returns_exit_two_and_json_for_invalid_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trials_path = Path(temp_dir) / "trials.jsonl"
            trials_path.write_text("", encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "eval_gate.py",
                    "--cases",
                    "eval-cases.example.jsonl",
                    "--trials",
                    str(trials_path),
                ],
                cwd=FIXTURE_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(2, completed.returncode, completed.stderr)
        self.assertEqual("", completed.stdout)
        self.assertEqual(
            {"error": "No trials found", "gate_passed": False},
            json.loads(completed.stderr),
        )

    def test_better_path_does_not_have_to_repeat_baseline_failures(self) -> None:
        report = self._evaluate_trial(
            {
                "case_id": "average-empty-diagnosis",
                "trial_id": "cleaner-candidate",
                "answer": "average([]) raises ZeroDivisionError; add a guard that raises ValueError(\"at least one value\").",
                "turn_status": "completed",
                "tool_calls": 3,
                "failed_tool_calls": 0,
                "modified_files": [],
                "synthetic": True,
            }
        )

        self.assertTrue(report["gate_passed"])

    def test_tool_budget_regression_fails(self) -> None:
        report = self._evaluate_trial(
            {
                "case_id": "average-empty-diagnosis",
                "trial_id": "tool-budget-regression",
                "answer": "average([]) raises ZeroDivisionError; add a guard that raises ValueError(\"at least one value\").",
                "turn_status": "completed",
                "tool_calls": 6,
                "failed_tool_calls": 0,
                "modified_files": [],
                "synthetic": True,
            }
        )

        self.assertEqual(["max_tool_calls"], report["results"][0]["failed_checks"])

    def test_failed_status_and_failed_tool_budget_regressions_fail(self) -> None:
        report = self._evaluate_trial(
            {
                "case_id": "average-empty-diagnosis",
                "trial_id": "incomplete-with-failed-tools",
                "answer": "average([]) raises ZeroDivisionError; add a guard that raises ValueError(\"at least one value\").",
                "turn_status": "failed",
                "tool_calls": 4,
                "failed_tool_calls": 3,
                "modified_files": [],
                "synthetic": True,
            }
        )

        self.assertEqual(
            ["turn_status", "max_failed_tool_calls"],
            report["results"][0]["failed_checks"],
        )

    def test_unexpected_file_modification_fails(self) -> None:
        report = self._evaluate_trial(
            {
                "case_id": "average-empty-diagnosis",
                "trial_id": "write-regression",
                "answer": "average([]) raises ZeroDivisionError; add a guard that raises ValueError(\"at least one value\").",
                "turn_status": "completed",
                "tool_calls": 4,
                "failed_tool_calls": 0,
                "modified_files": ["calculator.py"],
                "synthetic": True,
            }
        )

        self.assertEqual(["modified_files"], report["results"][0]["failed_checks"])

    def test_trial_scoring_fields_are_validated(self) -> None:
        for field, value, error_message in (
            ("tool_calls", -1, "tool_calls must be a non-negative integer"),
            (
                "failed_tool_calls",
                1.5,
                "failed_tool_calls must be a non-negative integer",
            ),
            ("answer", 123, "answer must be a string"),
            ("turn_status", [], "turn_status must be a string"),
            (
                "modified_files",
                "none",
                "modified_files must be a list of strings",
            ),
        ):
            with self.subTest(field=field, value=value):
                trial = {
                    "case_id": "average-empty-diagnosis",
                    "trial_id": f"invalid-{field}",
                    "answer": "average([]) raises ZeroDivisionError; add a guard that raises ValueError(\"at least one value\").",
                    "turn_status": "completed",
                    "tool_calls": 3,
                    "failed_tool_calls": 0,
                    "modified_files": [],
                    "synthetic": True,
                }
                trial[field] = value

                with self.assertRaisesRegex(
                    ValueError,
                    error_message,
                ):
                    self._evaluate_trial(trial)

    def test_failed_tool_calls_cannot_exceed_total_tool_calls(self) -> None:
        trial = {
            "case_id": "average-empty-diagnosis",
            "trial_id": "impossible-tool-counts",
            "answer": "average([]) raises ZeroDivisionError; add a guard that raises ValueError(\"at least one value\").",
            "turn_status": "completed",
            "tool_calls": 0,
            "failed_tool_calls": 2,
            "modified_files": [],
            "synthetic": True,
        }

        with self.assertRaisesRegex(
            ValueError,
            "failed_tool_calls cannot exceed tool_calls",
        ):
            self._evaluate_trial(trial)

    def test_case_scoring_fields_are_validated(self) -> None:
        original_case = json.loads(
            (FIXTURE_ROOT / "eval-cases.example.jsonl").read_text(encoding="utf-8")
        )
        trial = json.loads(
            (FIXTURE_ROOT / "baseline-trials.example.jsonl").read_text(
                encoding="utf-8"
            )
        )

        for field, value, error_message in (
            (
                "max_tool_calls",
                1.5,
                "max_tool_calls must be a non-negative integer",
            ),
            (
                "max_failed_tool_calls",
                -1,
                "max_failed_tool_calls must be a non-negative integer",
            ),
            ("turn_status", 1, "turn_status must be a string"),
            (
                "answer_contains_all",
                "ok",
                "answer_contains_all must be a non-empty list of non-empty strings",
            ),
            (
                "answer_contains_all",
                [],
                "answer_contains_all must be a non-empty list of non-empty strings",
            ),
            (
                "answer_contains_all",
                [""],
                "answer_contains_all must be a non-empty list of non-empty strings",
            ),
            (
                "modified_files",
                "none",
                "modified_files must be a list of strings",
            ),
        ):
            with self.subTest(field=field, value=value):
                case = {**original_case, "expect": {**original_case["expect"]}}
                case["expect"][field] = value
                with tempfile.TemporaryDirectory() as temp_dir:
                    cases_path = Path(temp_dir) / "cases.jsonl"
                    trials_path = Path(temp_dir) / "trials.jsonl"
                    self._write_jsonl(cases_path, [case])
                    self._write_jsonl(trials_path, [trial])

                    with self.assertRaisesRegex(
                        ValueError,
                        error_message,
                    ):
                        evaluate_files(cases_path, trials_path)

    def test_duplicate_case_ids_are_rejected(self) -> None:
        case = json.loads(
            (FIXTURE_ROOT / "eval-cases.example.jsonl").read_text(encoding="utf-8")
        )
        trial = json.loads(
            (FIXTURE_ROOT / "baseline-trials.example.jsonl").read_text(
                encoding="utf-8"
            )
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            cases_path = Path(temp_dir) / "cases.jsonl"
            trials_path = Path(temp_dir) / "trials.jsonl"
            self._write_jsonl(cases_path, [case, case])
            self._write_jsonl(trials_path, [trial])

            with self.assertRaisesRegex(ValueError, "Duplicate case_id"):
                evaluate_files(cases_path, trials_path)

    def test_trial_for_an_unknown_case_is_rejected(self) -> None:
        trial = {
            "case_id": "unknown-case",
            "trial_id": "orphan-trial",
            "answer": "No matching case.",
            "turn_status": "completed",
            "tool_calls": 0,
            "failed_tool_calls": 0,
            "modified_files": [],
            "synthetic": True,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            trials_path = Path(temp_dir) / "trials.jsonl"
            self._write_jsonl(trials_path, [trial])
            with self.assertRaisesRegex(ValueError, "Unknown case_id"):
                evaluate_files(
                    FIXTURE_ROOT / "eval-cases.example.jsonl",
                    trials_path,
                )

    def test_empty_trial_set_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trials_path = Path(temp_dir) / "trials.jsonl"
            trials_path.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "No trials"):
                evaluate_files(
                    FIXTURE_ROOT / "eval-cases.example.jsonl",
                    trials_path,
                )

    def test_empty_case_set_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cases_path = Path(temp_dir) / "cases.jsonl"
            cases_path.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "No eval cases"):
                evaluate_files(
                    cases_path,
                    FIXTURE_ROOT / "baseline-trials.example.jsonl",
                )

    def test_duplicate_trial_ids_are_rejected(self) -> None:
        trial = json.loads(
            (FIXTURE_ROOT / "baseline-trials.example.jsonl").read_text(
                encoding="utf-8"
            )
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            trials_path = Path(temp_dir) / "trials.jsonl"
            self._write_jsonl(trials_path, [trial, trial])
            with self.assertRaisesRegex(ValueError, "Duplicate trial_id"):
                evaluate_files(
                    FIXTURE_ROOT / "eval-cases.example.jsonl",
                    trials_path,
                )

    def test_invalid_json_reports_the_source_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            trials_path = Path(temp_dir) / "trials.jsonl"
            trials_path.write_text("{}\nnot-json\n", encoding="utf-8")
            with self.assertRaisesRegex(
                ValueError,
                r"Invalid JSON in .+trials\.jsonl on line 2, column 1",
            ):
                evaluate_files(
                    FIXTURE_ROOT / "eval-cases.example.jsonl",
                    trials_path,
                )

    def test_nonstandard_json_constants_are_rejected(self) -> None:
        trial_text = (
            FIXTURE_ROOT / "baseline-trials.example.jsonl"
        ).read_text(encoding="utf-8")
        trial_text = trial_text.replace('"synthetic":false', '"synthetic":NaN')

        with tempfile.TemporaryDirectory() as temp_dir:
            trials_path = Path(temp_dir) / "trials.jsonl"
            trials_path.write_text(trial_text, encoding="utf-8")
            with self.assertRaisesRegex(
                ValueError,
                r"Invalid JSON constant in .+trials\.jsonl on line 1: NaN",
            ):
                evaluate_files(
                    FIXTURE_ROOT / "eval-cases.example.jsonl",
                    trials_path,
                )

    def test_every_case_requires_at_least_one_trial(self) -> None:
        case = json.loads(
            (FIXTURE_ROOT / "eval-cases.example.jsonl").read_text(encoding="utf-8")
        )
        second_case = {**case, "case_id": "second-case"}
        trial = json.loads(
            (FIXTURE_ROOT / "baseline-trials.example.jsonl").read_text(
                encoding="utf-8"
            )
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            cases_path = Path(temp_dir) / "cases.jsonl"
            trials_path = Path(temp_dir) / "trials.jsonl"
            self._write_jsonl(cases_path, [case, second_case])
            self._write_jsonl(trials_path, [trial])
            with self.assertRaisesRegex(ValueError, "No trials for case_id: second-case"):
                evaluate_files(cases_path, trials_path)

    def _evaluate_trial(self, trial: dict[str, object]) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temp_dir:
            trials_path = Path(temp_dir) / "trials.jsonl"
            self._write_jsonl(trials_path, [trial])
            return evaluate_files(
                FIXTURE_ROOT / "eval-cases.example.jsonl",
                trials_path,
            )

    @staticmethod
    def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
        path.write_text(
            "".join(json.dumps(record) + "\n" for record in records),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
