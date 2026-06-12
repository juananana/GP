#!/usr/bin/env python3
"""Build the T6 itsdangerous timestamp-signing audit task and oracle."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "false_convergence_pilot"
TASK_ROOT = BASE / "T6_real_repo_itsdangerous"
REPO = TASK_ROOT / "repo"
RESULTS = BASE / "results"

TASK_ID = "T6_real_repo_itsdangerous_timed_signing"
PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"TimestampSigner",
        r"TimedSerializer",
        r"URLSafeTimedSerializer",
        r"SignatureExpired",
        r"BadTimeSignature",
        r"max_age",
        r"return_timestamp",
        r"date_signed",
        r"timestamp",
        r"timestamp_to_datetime",
        r"get_timestamp",
        r"loads_unsafe",
        r"expired",
        r"expires",
        r"age",
    ]
]

FILES = [
    "repo/src/itsdangerous/timed.py",
    "repo/src/itsdangerous/exc.py",
    "repo/src/itsdangerous/url_safe.py",
    "repo/src/itsdangerous/__init__.py",
    "repo/tests/test_itsdangerous/test_timed.py",
    "repo/tests/test_itsdangerous/test_url_safe.py",
    "repo/docs/timed.rst",
    "repo/docs/exceptions.rst",
    "repo/docs/url_safe.rst",
    "repo/README.md",
    "repo/CHANGES.rst",
]

BUCKETS = {
    "repo/src/itsdangerous/timed.py": "implementation",
    "repo/src/itsdangerous/exc.py": "exception_types",
    "repo/src/itsdangerous/url_safe.py": "url_safe_timed_api",
    "repo/src/itsdangerous/__init__.py": "public_exports",
    "repo/tests/test_itsdangerous/test_timed.py": "test_coverage",
    "repo/tests/test_itsdangerous/test_url_safe.py": "test_coverage",
    "repo/docs/timed.rst": "documentation",
    "repo/docs/exceptions.rst": "documentation",
    "repo/docs/url_safe.rst": "documentation",
    "repo/README.md": "documentation",
    "repo/CHANGES.rst": "changelog",
}


def rel_to_disk(rel_path: str) -> Path:
    assert rel_path.startswith("repo/")
    return TASK_ROOT / rel_path


def include_line(rel_path: str, line_no: int, text: str) -> bool:
    if rel_path == "repo/CHANGES.rst":
        # Keep only bounded changelog notes that explicitly discuss timestamped
        # signing semantics, expiration, or timed unsign behavior.
        if line_no > 150:
            return False
    if rel_path == "repo/docs/url_safe.rst":
        return "URLSafeTimedSerializer" in text
    return any(pattern.search(text) for pattern in PATTERNS)


def build_oracle() -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for rel_path in FILES:
        path = rel_to_disk(rel_path)
        for line_no, text in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            if include_line(rel_path, line_no, text):
                items.append({
                    "file_path": rel_path,
                    "line": line_no,
                    "bucket": BUCKETS[rel_path],
                    "evidence": text.strip(),
                    "oracle_policy": "timestamp_signing_expiration_audit",
                })
    return items


def write_task(commit: str, oracle_size: int) -> None:
    task = f"""# T6 Real Repo itsdangerous Timestamp Signing Audit

This is a real-repository closed-world discovery task.

Repository snapshot:

- local path: `repo/`
- upstream: https://github.com/pallets/itsdangerous
- commit: `{commit}`

## Goal

Find every line-level location in the repository snapshot that belongs to the
timestamped signing and expiration audit.

An item is in scope if the line is part of one of these categories:

1. implementation of `TimestampSigner`, `TimedSerializer`, or
   `URLSafeTimedSerializer` timestamp signing behavior;
2. timestamp encoding, decoding, conversion to datetime, or current timestamp
   lookup;
3. `max_age`, expiration, future timestamp, `return_timestamp`, or
   `date_signed` behavior;
4. `SignatureExpired` or `BadTimeSignature` exception behavior directly tied to
   timestamped signatures;
5. tests that directly assert timestamp signing, expiration, malformed
   timestamp, returned timestamp, or URL-safe timed serializer behavior;
6. direct user documentation or bounded changelog notes about timestamped
   signing and expiration.

The oracle has {oracle_size} line-level items.

## Boundaries

Inspect only this task directory. Do not inspect oracle, score, result, or
itemset files outside this task directory.

Include only concrete `file_path:line` items. The file path must be relative to
this task root and should start with `repo/`, for example:

```json
{{"file_path": "repo/src/itsdangerous/timed.py", "line": 141}}
```

Do not include broad file-level answers. Do not include generic signing,
serializer, or URL-safe behavior unless the line directly concerns timestamped
signing or expiration.

## Suggested audit strategy

1. Inspect `repo/src/itsdangerous/timed.py`.
2. Inspect timestamp-related exceptions in `repo/src/itsdangerous/exc.py`.
3. Inspect timed URL-safe API and public exports.
4. Inspect `test_timed.py` and URL-safe timed tests.
5. Inspect `docs/timed.rst`, `docs/exceptions.rst`, `docs/url_safe.rst`,
   README, and bounded changelog notes.

## Output format

```json
{{
  "run_id": "T6_G3_seed04_agent01",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [
    {{"file_path": "repo/src/itsdangerous/timed.py", "line": 141}}
  ]
}}
```
"""
    (TASK_ROOT / "TASK.md").write_text(task, encoding="utf-8")


def main() -> None:
    commit = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    items = build_oracle()
    RESULTS.mkdir(parents=True, exist_ok=True)
    oracle = {
        "task_id": TASK_ID,
        "repository": "pallets/itsdangerous",
        "commit": commit,
        "oracle_policy": "timestamp_signing_expiration_audit",
        "items": items,
    }
    (RESULTS / "T6_real_repo_itsdangerous_timed_signing_oracle.json").write_text(
        json.dumps(oracle, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_task(commit, len(items))
    manifest = {
        "task_id": TASK_ID,
        "status": "task_ready_oracle_built",
        "source_repo": "https://github.com/pallets/itsdangerous",
        "source_commit": commit,
        "oracle_size": len(items),
        "oracle_builder": "tools/build_t6_real_itsdangerous_timed_task.py",
        "needs_independent_human_review": True,
        "notes": [
            "Initial oracle is regex/manual-policy constructed from bounded source files.",
            "Do not describe this as independent double annotation.",
        ],
    }
    (TASK_ROOT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{TASK_ID}: oracle_size={len(items)} commit={commit}")


if __name__ == "__main__":
    main()
