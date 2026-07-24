from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


def evaluate_files(cases_path: Path, trials_path: Path) -> dict[str, Any]:
    """Evaluate normalized Coding Agent trials against an eval dataset."""
    cases = _load_jsonl(cases_path)
    trials = _load_jsonl(trials_path)
    if not cases:
        raise ValueError("No eval cases found")
    if not trials:
        raise ValueError("No trials found")

    cases_by_id = {}
    for case in cases:
        case_id = str(case["case_id"])
        if case_id in cases_by_id:
            raise ValueError(f"Duplicate case_id: {case_id}")
        expected = case["expect"]
        for field in ("max_tool_calls", "max_failed_tool_calls"):
            value = expected[field]
            if type(value) is not int or value < 0:
                raise ValueError(f"{field} must be a non-negative integer")
        if not isinstance(expected["turn_status"], str):
            raise ValueError("turn_status must be a string")
        answer_fragments = expected["answer_contains_all"]
        if (
            not isinstance(answer_fragments, list)
            or not answer_fragments
            or not all(
                isinstance(fragment, str) and fragment
                for fragment in answer_fragments
            )
        ):
            raise ValueError(
                "answer_contains_all must be a non-empty list of non-empty strings"
            )
        modified_files = expected["modified_files"]
        if not isinstance(modified_files, list) or not all(
            isinstance(path, str) for path in modified_files
        ):
            raise ValueError("modified_files must be a list of strings")
        cases_by_id[case_id] = case
    results = []
    seen_trial_ids = set()
    tested_case_ids = set()

    for trial in trials:
        trial_id = str(trial["trial_id"])
        if trial_id in seen_trial_ids:
            raise ValueError(f"Duplicate trial_id: {trial_id}")
        seen_trial_ids.add(trial_id)
        case_id = str(trial["case_id"])
        if case_id not in cases_by_id:
            raise ValueError(f"Unknown case_id: {case_id}")
        for field in ("tool_calls", "failed_tool_calls"):
            value = trial[field]
            if type(value) is not int or value < 0:
                raise ValueError(f"{field} must be a non-negative integer")
        if not isinstance(trial["turn_status"], str):
            raise ValueError("turn_status must be a string")
        if not isinstance(trial["answer"], str):
            raise ValueError("answer must be a string")
        modified_files = trial["modified_files"]
        if not isinstance(modified_files, list) or not all(
            isinstance(path, str) for path in modified_files
        ):
            raise ValueError("modified_files must be a list of strings")
        if trial["failed_tool_calls"] > trial["tool_calls"]:
            raise ValueError("failed_tool_calls cannot exceed tool_calls")
        tested_case_ids.add(case_id)
        expected = cases_by_id[case_id]["expect"]
        failed_checks = []

        if trial["turn_status"] != expected["turn_status"]:
            failed_checks.append("turn_status")
        if not all(
            fragment in trial["answer"]
            for fragment in expected["answer_contains_all"]
        ):
            failed_checks.append("answer_contains_all")
        if trial["tool_calls"] > expected["max_tool_calls"]:
            failed_checks.append("max_tool_calls")
        if trial["failed_tool_calls"] > expected["max_failed_tool_calls"]:
            failed_checks.append("max_failed_tool_calls")
        if trial["modified_files"] != expected["modified_files"]:
            failed_checks.append("modified_files")

        results.append(
            {
                "case_id": case_id,
                "trial_id": trial_id,
                "passed": not failed_checks,
                "failed_checks": failed_checks,
            }
        )

    for case_id in cases_by_id:
        if case_id not in tested_case_ids:
            raise ValueError(f"No trials for case_id: {case_id}")

    passed_trials = sum(result["passed"] for result in results)
    return {
        "case_count": len(cases),
        "trial_count": len(trials),
        "passed_trials": passed_trials,
        "failed_trials": len(trials) - passed_trials,
        "gate_passed": passed_trials == len(trials),
        "results": results,
    }


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if line.strip():
            def reject_constant(constant: str) -> None:
                raise ValueError(
                    f"Invalid JSON constant in {path} "
                    f"on line {line_number}: {constant}"
                )

            try:
                records.append(json.loads(line, parse_constant=reject_constant))
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON in {path} on line {line_number}, "
                    f"column {error.colno}"
                ) from error
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a local Coding Agent eval gate")
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--trials", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        report = evaluate_files(args.cases, args.trials)
    except (KeyError, OSError, TypeError, ValueError) as error:
        print(
            json.dumps(
                {"error": str(error), "gate_passed": False},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if report["gate_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
