from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import combinations
import json
import math
from pathlib import Path
import re
import sys


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    path: Path


@dataclass(frozen=True)
class Diagnostic:
    code: str
    path: Path
    message: str


@dataclass(frozen=True)
class Case:
    id: str
    prompt: str
    expected_skill: str | None
    split: str


@dataclass(frozen=True)
class Activation:
    case_id: str
    run: int
    selected_skill: str | None
    agent: str | None = None


def load_skills(skills_dir: Path) -> tuple[list[Skill], list[Diagnostic]]:
    skills: list[Skill] = []
    diagnostics: list[Diagnostic] = []

    if not skills_dir.is_dir():
        return [], [
            Diagnostic(
                "skills_dir_missing",
                skills_dir,
                "Skills directory does not exist or is not a directory",
            )
        ]

    for path in sorted(skills_dir.glob("*/SKILL.md")):
        metadata, parse_error = _parse_frontmatter(path)
        if parse_error is not None:
            diagnostics.append(parse_error)
            continue

        name = metadata.get("name", "").strip()
        description = metadata.get("description", "").strip()
        if not name:
            diagnostics.append(Diagnostic("missing_name", path, "Missing required name"))
            continue
        if not description:
            diagnostics.append(
                Diagnostic("missing_description", path, "Missing required description")
            )
            continue

        if len(name) > 64 or re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) is None:
            diagnostics.append(
                Diagnostic("invalid_name", path, "Name does not match the Agent Skills format")
            )
        if name != path.parent.name:
            diagnostics.append(
                Diagnostic("name_mismatch", path, "Name does not match the parent directory")
            )
        if len(description) > 1024:
            diagnostics.append(
                Diagnostic("description_too_long", path, "Description exceeds 1024 characters")
            )

        skills.append(Skill(name=name, description=description, path=path))

    return sorted(skills, key=lambda skill: skill.name), diagnostics


def audit_catalog(skills: list[Skill], overlap_threshold: float = 0.45) -> dict[str, object]:
    catalog_chars = sum(len(skill.name) + len(skill.description) for skill in skills)
    overlap_pairs: list[dict[str, object]] = []

    for left, right in combinations(skills, 2):
        left_terms = _description_terms(left.description)
        right_terms = _description_terms(right.description)
        union = left_terms | right_terms
        similarity = len(left_terms & right_terms) / len(union) if union else 0.0
        if similarity >= overlap_threshold:
            overlap_pairs.append(
                {
                    "left": left.name,
                    "right": right.name,
                    "similarity": round(similarity, 3),
                }
            )

    return {
        "skill_count": len(skills),
        "catalog_chars": catalog_chars,
        "estimated_catalog_tokens": math.ceil(catalog_chars / 4),
        "overlap_pairs": overlap_pairs,
    }


def load_cases(path: Path) -> list[Case]:
    cases: list[Case] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        data = json.loads(line)
        try:
            cases.append(
                Case(
                    id=str(data["id"]),
                    prompt=str(data["prompt"]),
                    expected_skill=data.get("expected_skill"),
                    split=str(data["split"]),
                )
            )
        except KeyError as error:
            raise ValueError(f"Missing {error.args[0]} on line {line_number}") from error
    return cases


def route_cases(
    skills: list[Skill], cases: list[Case], minimum_score: int = 2
) -> list[dict[str, object]]:
    skill_terms = {
        skill.name: _description_terms(
            re.split(r"\bdo not use\b", skill.description, maxsplit=1, flags=re.IGNORECASE)[0]
        )
        for skill in skills
    }
    results: list[dict[str, object]] = []

    for case in cases:
        prompt_terms = _description_terms(case.prompt)
        scored: list[tuple[int, str]] = []
        for skill in skills:
            score = len(prompt_terms & skill_terms[skill.name])
            scored.append((score, skill.name))

        scored.sort(reverse=True)
        top_score = scored[0][0] if scored else 0
        top_names = [name for score, name in scored if score == top_score]
        selected = top_names[0] if top_score >= minimum_score and len(top_names) == 1 else None
        results.append(
            {
                "case_id": case.id,
                "split": case.split,
                "expected_skill": case.expected_skill,
                "selected_skill": selected,
                "score": top_score,
                "correct": selected == case.expected_skill,
            }
        )

    return results


def summarize_routes(results: list[dict[str, object]]) -> dict[str, object]:
    total = len(results)
    correct = sum(bool(result["correct"]) for result in results)
    return {
        "total": total,
        "correct": correct,
        "accuracy": correct / total if total else 0.0,
    }


def load_activations(path: Path) -> list[Activation]:
    activations: list[Activation] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        data = json.loads(line)
        try:
            activations.append(
                Activation(
                    case_id=str(data["case_id"]),
                    run=int(data["run"]),
                    selected_skill=data.get("selected_skill"),
                    agent=data.get("agent"),
                )
            )
        except KeyError as error:
            raise ValueError(f"Missing {error.args[0]} on line {line_number}") from error
    return activations


def score_activations(
    cases: list[Case], activations: list[Activation]
) -> dict[str, object]:
    expected_by_id = {case.id: case.expected_skill for case in cases}
    exact_matches = 0
    true_positive = 0
    selected_positive = 0
    expected_positive = 0
    false_activations = 0
    missed_activations = 0
    wrong_skill = 0
    seen_records: set[tuple[str | None, str, int]] = set()

    for activation in activations:
        record_key = (activation.agent, activation.case_id, activation.run)
        if record_key in seen_records:
            raise ValueError(
                "Duplicate activation record: "
                f"agent={activation.agent!r}, case_id={activation.case_id!r}, run={activation.run}"
            )
        seen_records.add(record_key)
        if activation.case_id not in expected_by_id:
            raise ValueError(f"Unknown case_id: {activation.case_id}")

        expected = expected_by_id[activation.case_id]
        selected = activation.selected_skill
        if selected == expected:
            exact_matches += 1
        if selected is not None:
            selected_positive += 1
        if expected is not None:
            expected_positive += 1
        if expected is not None and selected == expected:
            true_positive += 1
        elif expected is None and selected is not None:
            false_activations += 1
        elif expected is not None and selected is None:
            missed_activations += 1
        elif expected is not None and selected is not None and selected != expected:
            wrong_skill += 1

    total_runs = len(activations)
    return {
        "total_runs": total_runs,
        "exact_matches": exact_matches,
        "accuracy": exact_matches / total_runs if total_runs else 0.0,
        "precision": true_positive / selected_positive if selected_positive else 0.0,
        "recall": true_positive / expected_positive if expected_positive else 0.0,
        "false_activations": false_activations,
        "missed_activations": missed_activations,
        "wrong_skill": wrong_skill,
    }


def _description_terms(description: str) -> set[str]:
    stop_words = {
        "a",
        "an",
        "and",
        "do",
        "for",
        "from",
        "general",
        "in",
        "including",
        "it",
        "not",
        "of",
        "or",
        "the",
        "to",
        "use",
        "when",
        "without",
    }
    return {
        token
        for token in re.findall(r"[a-z0-9]+", description.lower())
        if token not in stop_words
    }


def _parse_frontmatter(path: Path) -> tuple[dict[str, str], Diagnostic | None]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, Diagnostic("missing_frontmatter", path, "SKILL.md must start with ---")

    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return {}, Diagnostic("unclosed_frontmatter", path, "YAML frontmatter is not closed")

    metadata: dict[str, str] = {}
    index = 1
    while index < end:
        line = lines[index]
        match = re.fullmatch(r"([A-Za-z0-9_-]+):\s*(.*)", line)
        if match is None:
            index += 1
            continue

        key, value = match.groups()
        if value in {">", "|"}:
            block: list[str] = []
            index += 1
            while index < end and (not lines[index].strip() or lines[index].startswith((" ", "\t"))):
                block.append(lines[index].strip())
                index += 1
            metadata[key] = " ".join(part for part in block if part)
            continue

        metadata[key] = _strip_yaml_quotes(value)
        index += 1

    return metadata, None


def _strip_yaml_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit an Agent Skills loadout")
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser("audit", help="Run static loadout checks")
    audit_parser.add_argument("--skills-dir", type=Path, required=True)
    audit_parser.add_argument("--cases", type=Path)
    audit_parser.add_argument("--max-estimated-tokens", type=int)
    audit_parser.add_argument("--overlap-threshold", type=float, default=0.45)
    audit_parser.add_argument("--minimum-score", type=int, default=2)

    score_parser = subparsers.add_parser(
        "score", help="Score activation records captured from a real agent"
    )
    score_parser.add_argument("--cases", type=Path, required=True)
    score_parser.add_argument("--activations", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "audit":
        skills, diagnostics = load_skills(args.skills_dir)
        catalog = audit_catalog(skills, overlap_threshold=args.overlap_threshold)
        max_tokens = args.max_estimated_tokens
        budget_passed = (
            max_tokens is None
            or int(catalog["estimated_catalog_tokens"]) <= max_tokens
        )
        report: dict[str, object] = {
            "catalog": catalog,
            "diagnostics": [
                {
                    "code": diagnostic.code,
                    "path": str(diagnostic.path),
                    "message": diagnostic.message,
                }
                for diagnostic in diagnostics
            ],
            "max_estimated_tokens": max_tokens,
            "budget_passed": budget_passed,
        }

        if args.cases is not None:
            cases = load_cases(args.cases)
            routes = route_cases(skills, cases, minimum_score=args.minimum_score)
            route_summary = summarize_routes(routes)
            route_summary["failures"] = [
                result for result in routes if not result["correct"]
            ]
            report["lexical_smoke_test"] = route_summary

        print(json.dumps(report, indent=2, ensure_ascii=False))
        if diagnostics:
            return 1
        return 0 if budget_passed else 2

    if args.command == "score":
        cases = load_cases(args.cases)
        activations = load_activations(args.activations)
        print(
            json.dumps(
                score_activations(cases, activations),
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
