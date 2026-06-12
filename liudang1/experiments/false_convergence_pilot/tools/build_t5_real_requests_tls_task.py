#!/usr/bin/env python3
"""Build a real-repository closed-world audit task from Requests."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_ROOT = ROOT / "T5_real_repo_requests_tls"
REPO = TASK_ROOT / "repo"

TARGET_FILES = {
    "README.md",
    "src/requests/adapters.py",
    "src/requests/api.py",
    "src/requests/certs.py",
    "src/requests/exceptions.py",
    "src/requests/sessions.py",
    "src/requests/utils.py",
    "tests/conftest.py",
    "tests/test_requests.py",
    "tests/testserver/server.py",
    "tests/certs/README.md",
    "docs/user/advanced.rst",
    "docs/community/faq.rst",
    "docs/community/recommended.rst",
}

TLS_TERMS = (
    "tls",
    "ssl",
    "certificate",
    "certificates",
    "certifi",
    "ca bundle",
    "ca_bundle",
    "ca_cert",
    "cacert",
    "requests_ca_bundle",
    "curl_ca_bundle",
    "default_ca_bundle_path",
    "client cert",
    "client certificate",
    "cert_file",
    "key_file",
    "cert_reqs",
    "cert_none",
    "cert_required",
    "sslerror",
    "verify",
)


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


def normalized(text: str) -> str:
    return re.sub(r"[^a-z0-9_]+", " ", text.lower())


def in_scope(rel_path: str, line: str) -> bool:
    text = normalized(line)
    if rel_path not in TARGET_FILES:
        return False
    if rel_path == "README.md":
        return "tls ssl verification" in text
    if rel_path.startswith("docs/"):
        return any(term.replace("_", " ") in text for term in TLS_TERMS)
    if rel_path.startswith("tests/certs/"):
        return "certificate" in text or "certificates" in text or "mtls" in text
    return any(term in text for term in TLS_TERMS)


def classify(rel_path: str, line: str) -> str:
    text = normalized(line)
    if rel_path.startswith("docs/") or rel_path == "README.md":
        return "documentation"
    if rel_path.startswith("tests/certs/") or rel_path.startswith("tests/testserver/"):
        return "test_infrastructure"
    if rel_path.startswith("tests/"):
        return "test_coverage"
    if "requests_ca_bundle" in text or "curl_ca_bundle" in text or "default_ca_bundle_path" in text or "ca bundle" in text:
        return "ca_bundle_resolution"
    if "cert_file" in text or "key_file" in text or "client cert" in text or "client certificate" in text:
        return "client_certificate"
    if "cert_reqs" in text or "cert_required" in text or "cert_none" in text or "verify is false" in text:
        return "verification_mode"
    if "sslerror" in text or "ssl error" in text or "certificate failure" in text:
        return "error_handling"
    return "implementation"


def build_oracle() -> dict[str, object]:
    items: list[dict[str, object]] = []
    for rel_path in sorted(TARGET_FILES):
        path = REPO / rel_path
        if not path.exists() or not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for index, line in enumerate(lines, start=1):
            if not in_scope(rel_path, line):
                continue
            items.append({
                "file_path": f"repo/{rel_path}",
                "line": index,
                "bucket": classify(rel_path, line),
                "evidence_span": line.strip(),
                "difficulty_tag": (
                    "real_repo_cross_file_tls"
                    if rel_path.startswith(("src/", "tests/"))
                    else "real_repo_tls_docs"
                ),
            })
    return {
        "task_id": "T5_real_repo_requests_tls_audit",
        "source_repo": "https://github.com/psf/requests",
        "source_commit": git_commit(),
        "oracle_policy": (
            "Line-level items in the real Requests repository that belong to a "
            "TLS certificate verification and certificate handling audit. Include "
            "verify parameter behavior, CA bundle resolution, client certificate "
            "handling, TLS/SSL error handling, test infrastructure, tests, and "
            "direct user documentation. Exclude unrelated uses of 'verify' that "
            "do not concern TLS/certificates."
        ),
        "items": items,
    }


def write_task(oracle_size: int) -> None:
    task = f"""# T5 Real Repo Requests TLS Certificate Audit

This is a real-repository closed-world discovery task.

Repository snapshot:

- local path: `repo/`
- upstream: https://github.com/psf/requests
- commit: `{git_commit()}`

## Goal

Find every line-level location in the repository snapshot that belongs to the
TLS certificate verification and certificate handling audit.

An item is in scope if the line is part of one of these categories:

1. implementation of TLS verification mode or `verify` behavior;
2. CA bundle resolution, including default certifi bundle and environment variables;
3. client certificate or key-file handling;
4. TLS/SSL certificate error handling;
5. tests and test infrastructure for TLS, certificate verification, CA bundles, or mTLS;
6. direct user documentation about SSL/TLS verification, CA bundles, or client certificates.

The oracle has {oracle_size} line-level items.

## Boundaries

Inspect only this task directory. Do not inspect oracle, score, result, or
itemset files outside this task directory.

Include only concrete `file_path:line` items. The file path must be relative to
this task root and should start with `repo/`, for example:

```json
{{"file_path": "repo/src/requests/adapters.py", "line": 321}}
```

Do not include broad file-level answers. Do not include unrelated occurrences of
the word `verify` that do not concern TLS certificates or certificate handling.

## Suggested audit strategy

1. Inspect source implementation in `repo/src/requests/adapters.py`,
   `repo/src/requests/sessions.py`, `repo/src/requests/certs.py`, and
   `repo/src/requests/utils.py`.
2. Inspect tests in `repo/tests/test_requests.py`, `repo/tests/conftest.py`,
   and `repo/tests/testserver/server.py`.
3. Inspect certificate fixture documentation in `repo/tests/certs/README.md`.
4. Inspect user documentation in `repo/docs/user/advanced.rst` and related
   community docs.
5. Return exact line-level items only.

## Output format

```json
{{
  "run_id": "T5_G3_seed01_agentXX",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [
    {{"file_path": "repo/src/requests/adapters.py", "line": 321}}
  ]
}}
```
"""
    (TASK_ROOT / "TASK.md").write_text(task, encoding="utf-8")


def write_manifest(oracle_size: int) -> None:
    manifest = {
        "task_id": "T5_real_repo_requests_tls_audit",
        "status": "task_ready_oracle_built",
        "source_repo": "https://github.com/psf/requests",
        "source_commit": git_commit(),
        "oracle_size": oracle_size,
        "needs_blind_runs": [
            "G3 seed01 agent01-agent03",
            "G6 holdout seed01",
            "standard summarizer",
            "union-preserving summarizer",
        ],
        "notes": [
            "This task family uses a real repository snapshot.",
            "The task is TLS/certificate verification audit, not deprecation audit.",
            "Blind agents may inspect only T5_real_repo_requests_tls/.",
        ],
    }
    (TASK_ROOT / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    if not REPO.exists():
        raise SystemExit(
            f"Missing repository at {REPO}. Clone https://github.com/psf/requests first."
        )
    oracle = build_oracle()
    oracle_size = len(oracle["items"])
    out = ROOT / "results" / "T5_real_repo_requests_tls_oracle.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(oracle, indent=2, ensure_ascii=False), encoding="utf-8")
    write_task(oracle_size)
    write_manifest(oracle_size)
    print(f"Built T5 oracle with {oracle_size} items")


if __name__ == "__main__":
    main()
