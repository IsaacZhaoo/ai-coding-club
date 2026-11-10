#!/usr/bin/env python3
"""Create a new, isolated Git exercise; refuse every existing destination."""

import argparse
import os
from pathlib import Path
import subprocess


BASELINE = '''TITLE = "My trip"
CURRENCY = "USD"


def report_label():
    return TITLE


def example_amounts():
    return [12, 8, 5]


def total_amount(amounts):
    return sum(amounts)


if __name__ == "__main__":
    print(f"{report_label()} | {CURRENCY} {total_amount(example_amounts())}")
'''
NOTE = "My own note: keep the train receipt.\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    destination = args.destination.absolute()
    if destination.exists() or destination.is_symlink():
        parser.error("destination already exists; choose a new directory")
    destination.mkdir(parents=False)
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    # These settings affect only this synthetic repository and its commands.
    def git(*parts):
        subprocess.run(
            ["git", "-c", "core.hooksPath=" + os.devnull,
             "-c", "commit.gpgsign=false", *parts],
            cwd=destination, env=env, check=True, capture_output=True, text=True,
        )

    git("init", "--initial-branch=main", "--template=")
    git("config", "user.name", "Exercise User")
    git("config", "user.email", "exercise@example.invalid")
    git("config", "core.autocrlf", "false")
    source = destination / "expense_report.py"
    source.write_text(BASELINE, encoding="utf-8")
    git("add", "--", "expense_report.py")
    git("commit", "-m", "Save working report before AI changes")
    git("tag", "before-ai")
    # A human edits and stages one part of the same file after the checkpoint.
    human_version = BASELINE.replace('CURRENCY = "USD"', 'CURRENCY = "EUR"')
    source.write_text(human_version, encoding="utf-8")
    git("add", "--", "expense_report.py")
    # A simulated AI edit introduces a bug in a separate hunk.
    source.write_text(
        human_version.replace("return sum(amounts)", "return sum(amounts) * 100"),
        encoding="utf-8",
    )
    (destination / "notes.txt").write_text(NOTE, encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    main()
