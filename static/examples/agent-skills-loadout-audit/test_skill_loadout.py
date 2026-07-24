from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from skill_loadout import (
    audit_catalog,
    load_activations,
    load_cases,
    load_skills,
    route_cases,
    score_activations,
    summarize_routes,
)


FIXTURE_ROOT = Path(__file__).resolve().parent


class SkillDiscoveryTests(unittest.TestCase):
    def test_loads_five_valid_skill_files(self) -> None:
        skills, diagnostics = load_skills(FIXTURE_ROOT / "skills")

        self.assertEqual(
            [
                "api-documentation",
                "database-query-review",
                "frontend-accessibility",
                "python-test-fixer",
                "release-notes",
            ],
            [skill.name for skill in skills],
        )
        self.assertEqual([], diagnostics)

    def test_missing_skills_directory_is_not_reported_as_a_clean_loadout(self) -> None:
        skills, diagnostics = load_skills(FIXTURE_ROOT / "missing-skills")

        self.assertEqual([], skills)
        self.assertEqual(["skills_dir_missing"], [item.code for item in diagnostics])


class CatalogAuditTests(unittest.TestCase):
    def test_reports_catalog_cost_without_false_overlap(self) -> None:
        skills, diagnostics = load_skills(FIXTURE_ROOT / "skills")
        self.assertEqual([], diagnostics)

        audit = audit_catalog(skills)

        self.assertEqual(5, audit["skill_count"])
        self.assertEqual(1065, audit["catalog_chars"])
        self.assertEqual(267, audit["estimated_catalog_tokens"])
        self.assertEqual([], audit["overlap_pairs"])

    def test_flags_descriptions_that_compete_for_the_same_prompts(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_skill(
                root,
                "code-review",
                "Use when reviewing code changes, tests, security, compatibility, and merge readiness.",
            )
            self._write_skill(
                root,
                "release-review",
                "Use when reviewing code changes, tests, security, compatibility, and release readiness.",
            )
            skills, diagnostics = load_skills(root)
            self.assertEqual([], diagnostics)

            audit = audit_catalog(skills, overlap_threshold=0.6)

            self.assertEqual(
                [("code-review", "release-review")],
                [(pair["left"], pair["right"]) for pair in audit["overlap_pairs"]],
            )

    @staticmethod
    def _write_skill(root: Path, name: str, description: str) -> None:
        skill_dir = root / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {description}\n---\n",
            encoding="utf-8",
        )


class LexicalRoutingTests(unittest.TestCase):
    def test_reports_the_known_limits_of_a_cheap_loadout_smoke_test(self) -> None:
        skills, diagnostics = load_skills(FIXTURE_ROOT / "skills")
        self.assertEqual([], diagnostics)
        cases = load_cases(FIXTURE_ROOT / "cases.jsonl")

        results = route_cases(skills, cases)
        summary = summarize_routes(results)

        self.assertEqual(20, len(cases))
        self.assertEqual(10, sum(case.expected_skill is not None for case in cases))
        self.assertEqual(10, sum(case.expected_skill is None for case in cases))
        self.assertEqual({"total": 20, "correct": 18, "accuracy": 0.9}, summary)
        self.assertEqual(
            {"near-api-implementation", "near-python-debug"},
            {result["case_id"] for result in results if not result["correct"]},
        )


class ActivationScoringTests(unittest.TestCase):
    def test_scores_repeated_real_agent_activation_records(self) -> None:
        cases = load_cases(FIXTURE_ROOT / "cases.jsonl")
        activations = load_activations(FIXTURE_ROOT / "activations.example.jsonl")

        summary = score_activations(cases, activations)

        self.assertEqual(12, summary["total_runs"])
        self.assertEqual(9, summary["exact_matches"])
        self.assertEqual(0.75, summary["accuracy"])
        self.assertAlmostEqual(5 / 7, summary["precision"])
        self.assertAlmostEqual(5 / 6, summary["recall"])
        self.assertEqual(2, summary["false_activations"])
        self.assertEqual(1, summary["missed_activations"])
        self.assertEqual(0, summary["wrong_skill"])

    def test_rejects_duplicate_run_records_that_would_inflate_metrics(self) -> None:
        cases = load_cases(FIXTURE_ROOT / "cases.jsonl")
        activations = load_activations(FIXTURE_ROOT / "activations.example.jsonl")

        with self.assertRaisesRegex(ValueError, "Duplicate activation record"):
            score_activations(cases, [*activations, activations[0]])


class CommandLineTests(unittest.TestCase):
    def test_audit_command_returns_machine_readable_loadout_report(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "skill_loadout.py",
                "audit",
                "--skills-dir",
                "skills",
                "--cases",
                "cases.jsonl",
                "--max-estimated-tokens",
                "300",
            ],
            cwd=FIXTURE_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(5, report["catalog"]["skill_count"])
        self.assertEqual(18, report["lexical_smoke_test"]["correct"])
        self.assertTrue(report["budget_passed"])

    def test_audit_command_fails_a_configured_catalog_budget(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "skill_loadout.py",
                "audit",
                "--skills-dir",
                "skills",
                "--max-estimated-tokens",
                "250",
            ],
            cwd=FIXTURE_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(2, completed.returncode)
        report = json.loads(completed.stdout)
        self.assertFalse(report["budget_passed"])

    def test_score_command_summarizes_recorded_agent_activations(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "skill_loadout.py",
                "score",
                "--cases",
                "cases.jsonl",
                "--activations",
                "activations.example.jsonl",
            ],
            cwd=FIXTURE_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(12, report["total_runs"])
        self.assertEqual(2, report["false_activations"])
        self.assertEqual(1, report["missed_activations"])


if __name__ == "__main__":
    unittest.main()
