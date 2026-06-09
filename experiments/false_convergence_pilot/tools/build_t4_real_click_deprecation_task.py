#!/usr/bin/env python3
"""Build a real-repository closed-world audit task from Click."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_ROOT = ROOT / "T4_real_repo_click"
REPO = TASK_ROOT / "repo"

TARGET_FILES = {
    "src/click/__init__.py",
    "src/click/core.py",
    "src/click/parser.py",
    "tests/test_arguments.py",
    "tests/test_commands.py",
    "tests/test_options.py",
    "docs/commands-and-groups.md",
}

CHANGELOG_MAX_LINE = 420


def git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=True,
        )
    except Exception:
        return "unknown"
    return result.stdout.strip()


def classify(path: str, line: str) -> str:
    lower = line.lower()
    if path.startswith("tests/"):
        return "test_coverage"
    if path.startswith("docs/") or path == "CHANGES.md":
        return "documentation"
    if "warnings.warn" in line or "DeprecationWarning" in line:
        return "warning_emission"
    if "_format_deprecated" in line or "(DEPRECATED" in line:
        return "message_formatting"
    if "deprecated" in lower and ("param" in lower or "option" in lower or "argument" in lower):
        return "parameter_behavior"
    if "deprecated" in lower and ("command" in lower or "basecommand" in lower or "multicommand" in lower):
        return "command_behavior"
    return "implementation"


def is_target_line(rel_path: str, line_no: int, text: str) -> bool:
    lower = text.lower()
    if "deprecated" not in lower and "deprecationwarning" not in lower:
        return False
    if rel_path in TARGET_FILES:
        return True
    if rel_path == "CHANGES.md" and line_no <= CHANGELOG_MAX_LINE:
        return True
    return False


def build_oracle() -> dict[str, object]:
    items: list[dict[str, object]] = []
    for path in sorted(REPO.rglob("*")):
        if not path.is_file():
            continue
        rel_path = path.relative_to(REPO).as_posix()
        if rel_path not in TARGET_FILES and rel_path != "CHANGES.md":
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for index, line in enumerate(lines, start=1):
            if not is_target_line(rel_path, index, line):
                continue
            items.append({
                "file_path": f"repo/{rel_path}",
                "line": index,
                "bucket": classify(rel_path, line),
                "evidence_span": line.strip(),
                "difficulty_tag": (
                    "real_repo_cross_file"
                    if rel_path.startswith(("src/", "tests/"))
                    else "real_repo_documentation"
                ),
            })
    return {
        "task_id": "T4_real_repo_click_deprecation",
        "source_repo": "https://github.com/pallets/click",
        "source_commit": git_commit(),
        "oracle_policy": (
            "Line-level items in the real Click repository that are part of the "
            "current deprecated API surface audit. Include implementation, "
            "warning emission, formatting, validation guards, tests, and direct "
            "user documentation. Exclude incidental historical mentions outside "
            "the bounded changelog window and files outside the target audit set."
        ),
        "items": items,
    }


def write_task(oracle_size: int) -> None:
    task = f"""# T4 Real Repo Click Deprecation Audit

This is a real-repository closed-world discovery task.

Repository snapshot:

- local path: `repo/`
- upstream: https://github.com/pallets/click
- commit: `{git_commit()}`

## Goal

Find every line-level location in the repository snapshot that belongs to the
current deprecated API surface audit.

An item is in scope if the line is part of one of these categories:

1. implementation of deprecated command, argument, option, parser, or compatibility behavior;
2. warning emission for deprecated public APIs or deprecated parameter usage;
3. formatting of deprecated help labels or warning suffixes;
4. validation guards that reject invalid deprecated configurations;
5. tests that directly assert deprecated help text, warnings, or validation behavior;
6. direct user documentation for marking commands as deprecated;
7. relevant bounded changelog entries near the current deprecation feature notes.

The oracle has {oracle_size} line-level items.

## Boundaries

Inspect only this task directory. Do not inspect oracle, score, result, or
itemset files outside this task directory.

Include only concrete `file_path:line` items. The file path must be relative to
this task root and should start with `repo/`, for example:

```json
{{"file_path": "repo/src/click/core.py", "line": 1359}}
```

Do not include broad file-level answers. Do not include incidental uses of the
word "deprecated" outside the target audit set.

## Suggested audit strategy

1. Inspect source implementation in `repo/src/click/__init__.py`,
   `repo/src/click/core.py`, and `repo/src/click/parser.py`.
2. Inspect tests in `repo/tests/test_arguments.py`,
   `repo/tests/test_options.py`, and `repo/tests/test_commands.py`.
3. Inspect user documentation in `repo/docs/commands-and-groups.md`.
4. Inspect the bounded current changelog region in `repo/CHANGES.md`.
5. Return exact line-level items only.

## Output format

```json
{{
  "run_id": "T4_G3_seed01_agentXX",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [
    {{"file_path": "repo/src/click/core.py", "line": 1359}}
  ]
}}
```
"""
    (TASK_ROOT / "TASK.md").write_text(task, encoding="utf-8")


def write_manifest(oracle_size: int) -> None:
    manifest = {
        "task_id": "T4_real_repo_click_deprecation",
        "status": "task_ready_oracle_built",
        "source_repo": "https://github.com/pallets/click",
        "source_commit": git_commit(),
        "oracle_size": oracle_size,
        "needs_blind_runs": [
            "G3 seed01 agent01-agent03",
            "G6 holdout seed01",
            "optional standard summarizer",
            "optional union-preserving summarizer",
        ],
        "notes": [
            "This task family uses a real repository snapshot.",
            "The oracle is line-level and generated from an explicit audit policy.",
            "Do not count it as agent validation until blind G3/G6 runs are completed.",
        ],
    }
    (TASK_ROOT / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    if not REPO.exists():
        raise SystemExit(
            f"Missing repository at {REPO}. Clone https://github.com/pallets/click first."
        )
    oracle = build_oracle()
    oracle_size = len(oracle["items"])
    (ROOT / "results" / "T4_real_repo_click_deprecation_oracle.json").parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "results" / "T4_real_repo_click_deprecation_oracle.json").write_text(
        json.dumps(oracle, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_task(oracle_size)
    write_manifest(oracle_size)
    print(f"Built T4 oracle with {oracle_size} items")


if __name__ == "__main__":
    main()
