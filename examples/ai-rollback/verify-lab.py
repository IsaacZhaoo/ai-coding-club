#!/usr/bin/env python3
"""Replay the exercise only in a newly created temporary repository."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists; preserve it and choose a new path")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    setup = Path(__file__).with_name("setup-lab.py")
    record = {"checks": [], "commands": [], "fixture_sha256": {
        "setup-lab.py": digest(setup), "verify-lab.py": digest(Path(__file__))}}
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_PAGER": "cat", "LC_ALL": "C"})

    with tempfile.TemporaryDirectory(prefix="ai-rollback-fixture-") as temporary:
        root = Path(temporary)
        project = root / "project"
        snapshot = root / "recovery-copy"
        record["temporary_root"] = str(root)

        def run(command, input_text=None, expected=0, cwd=None, env_override=None):
            result = subprocess.run(command, cwd=cwd or project, env={**env, **(env_override or {})},
                                    text=True, input=input_text, capture_output=True)
            record["commands"].append({"argv": command, "cwd": str(cwd or project),
                                       "input": input_text, "exit": result.returncode,
                                       "stdout": result.stdout, "stderr": result.stderr})
            if result.returncode != expected:
                raise AssertionError(record["commands"][-1])
            return result.stdout

        def check(name, condition):
            if not condition:
                raise AssertionError(name)
            record["checks"].append(name)

        try:
            run([sys.executable, str(setup), str(project)], cwd=root)
            git_version = run(["git", "--version"]).strip()
            record["environment"] = {"git": git_version, "python": sys.version.split()[0]}
            check("isolated .git directory exists", (project / ".git").is_dir())
            initial_head = run(["git", "rev-parse", "HEAD"]).strip()
            initial_index = digest(project / ".git/index")
            initial_notes = (project / "notes.txt").read_bytes()
            initial_source = (project / "expense_report.py").read_bytes()
            status = run(["git", "status", "--short"])
            check("mixed staged and unstaged edit plus untracked note", status ==
                  "MM expense_report.py\n?? notes.txt\n")
            check("bug is visible", run([sys.executable, "expense_report.py"]).strip() ==
                  "My trip | EUR 2500")
            full_diff = run(["git", "diff", "before-ai", "--", "expense_report.py"])
            check("two separate reviewable hunks", full_diff.count("\n@@ ") == 2)
            check("human and simulated AI edits both visible", '+CURRENCY = "EUR"' in
                  full_diff and "+    return sum(amounts) * 100" in full_diff)
            run(["git", "diff", "--cached", "--", "expense_report.py"])
            run(["git", "diff", "--", "expense_report.py"])
            # Whole-folder copy is bounded to this tiny, quiescent lab repository.
            shutil.copytree(project, snapshot)
            check("snapshot preserves original mixed file and untracked note",
                  (snapshot / "expense_report.py").read_bytes() == initial_source and
                  (snapshot / "notes.txt").read_bytes() == initial_notes)
            check("snapshot preserves index", digest(snapshot / ".git/index") == initial_index)
            response = run(["git", "-c", "color.ui=false", "restore", "--source=before-ai",
                            "--patch", "--worktree", "--", "expense_report.py"],
                           input_text="n\ny\n")
            check("exactly two hunk questions", response.count("Apply this hunk") == 2)
            check("human edit retained and incorrect total restored",
                  run([sys.executable, "expense_report.py"]).strip() == "My trip | EUR 25")
            check("untracked note byte-for-byte preserved", (project / "notes.txt").read_bytes()
                  == initial_notes)
            check("index byte-for-byte unchanged before further index reads",
                  digest(project / ".git/index") == initial_index)
            check("branch history unchanged", run(["git", "rev-parse", "HEAD"]).strip() ==
                  initial_head)
            check("no unstaged tracked changes remain", run(["git", "diff", "--exit-code"]) == "")
            final_status = run(["git", "status", "--short"])
            check("human edit remains staged and note remains untracked", final_status ==
                  "M  expense_report.py\n?? notes.txt\n")
            check("recovery copy remains intact", (snapshot / "expense_report.py").read_bytes() ==
                  initial_source and (snapshot / "notes.txt").read_bytes() == initial_notes)
            repeated = run([sys.executable, str(setup), str(project)], expected=2, cwd=root)
            check("existing destination rejected without changing source", repeated == "" and
                  run([sys.executable, "expense_report.py"]).strip() == "My trip | EUR 25")
            other = root / "second-project"
            final_index = digest(project / ".git/index")
            run([sys.executable, str(setup), str(other)], cwd=root, env_override={
                "GIT_DIR": str(project / ".git"), "GIT_WORK_TREE": str(project),
                "GIT_INDEX_FILE": str(project / ".git/index")})
            check("inherited Git paths cannot redirect setup to another repository",
                  (other / ".git").is_dir() and digest(project / ".git/index") == final_index
                  and run([sys.executable, "expense_report.py"]).strip() == "My trip | EUR 25")
            record["status"] = "passed"
        except Exception as error:
            record["status"] = "failed"
            record["error"] = repr(error)
            raise
        finally:
            record["temporary_cleanup"] = "TemporaryDirectory removes only this owned fixture root on exit"
            args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")

    print(f"{len(record['checks'])} checks passed; evidence: {args.output}")


if __name__ == "__main__":
    main()
