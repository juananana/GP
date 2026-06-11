#!/usr/bin/env python3
"""Run a minimal online blind validation suite.

The suite is deliberately small because it calls a paid model endpoint. It does
not read oracles during agent generation. Oracles are used only after all runs
finish, during merge/score postprocessing.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "false_convergence_pilot"
TASK_ROOT = BASE / "T5_real_repo_requests_tls"
OUT = BASE / "online_blind_validation" / "T5_requests_tls_seed04"
MODEL = "gpt-5.3-codex"
SEED = "seed04"
SEARCH_BUDGET = 180
MAX_LINES_PER_FILE = 1200
TASK_ID = "T5_real_repo_requests_tls_online_minimal"
ORACLE_SIZE = 304


COMMON_FILES = [
    "repo/src/requests/adapters.py",
    "repo/src/requests/sessions.py",
    "repo/src/requests/certs.py",
    "repo/src/requests/utils.py",
    "repo/src/requests/exceptions.py",
    "repo/tests/test_requests.py",
    "repo/tests/conftest.py",
    "repo/tests/testserver/server.py",
    "repo/tests/certs/README.md",
    "repo/docs/user/advanced.rst",
    "repo/docs/community/faq.rst",
    "repo/docs/community/recommended.rst",
    "repo/README.md",
]

CONDITIONS: dict[str, list[dict[str, Any]]] = {
    "homogeneous": [
        {
            "agent": "agent01",
            "files": COMMON_FILES,
            "prompt_variant": "standard_high_recall",
            "prompt_addon": "Use the task instructions as written. Prioritize complete line-level coverage across implementation, tests, fixtures, and documentation.",
        },
        {
            "agent": "agent02",
            "files": COMMON_FILES,
            "prompt_variant": "standard_high_recall",
            "prompt_addon": "Use the task instructions as written. Prioritize complete line-level coverage across implementation, tests, fixtures, and documentation.",
        },
        {
            "agent": "agent03",
            "files": COMMON_FILES,
            "prompt_variant": "standard_high_recall",
            "prompt_addon": "Use the task instructions as written. Prioritize complete line-level coverage across implementation, tests, fixtures, and documentation.",
        },
    ],
    "prompt_diverse": [
        {
            "agent": "agent01",
            "files": COMMON_FILES,
            "prompt_variant": "implementation_focus",
            "prompt_addon": "Focus first on implementation lines that control verify behavior, CA bundle selection, client certificates, and SSL errors. Include tests/docs only when directly tied to these implementation paths.",
        },
        {
            "agent": "agent02",
            "files": COMMON_FILES,
            "prompt_variant": "test_fixture_focus",
            "prompt_addon": "Focus first on tests, fixtures, certificate infrastructure, and testserver behavior. Include implementation/docs only when needed to justify exact TLS/certificate items.",
        },
        {
            "agent": "agent03",
            "files": COMMON_FILES,
            "prompt_variant": "docs_boundary_focus",
            "prompt_addon": "Focus first on user documentation and boundary cases involving certificate verification, CA bundles, client certificates, and environment variables. Include source/test lines when directly connected.",
        },
    ],
    "source_partitioned": [
        {
            "agent": "agent01",
            "files": [
                "repo/src/requests/adapters.py",
                "repo/src/requests/sessions.py",
                "repo/src/requests/certs.py",
                "repo/src/requests/utils.py",
                "repo/src/requests/exceptions.py",
            ],
            "prompt_variant": "source_partition_src",
            "prompt_addon": "Inspect only the implementation partition. Return exact implementation lines for TLS verification, CA bundle resolution, client certificates, and SSL errors.",
        },
        {
            "agent": "agent02",
            "files": [
                "repo/tests/test_requests.py",
                "repo/tests/conftest.py",
                "repo/tests/testserver/server.py",
                "repo/tests/certs/README.md",
            ],
            "prompt_variant": "source_partition_tests",
            "prompt_addon": "Inspect only the test and fixture partition. Return exact test, fixture, and certificate infrastructure lines related to TLS/certificate behavior.",
        },
        {
            "agent": "agent03",
            "files": [
                "repo/docs/user/advanced.rst",
                "repo/docs/community/faq.rst",
                "repo/docs/community/recommended.rst",
                "repo/README.md",
            ],
            "prompt_variant": "source_partition_docs",
            "prompt_addon": "Inspect only the documentation partition. Return exact documentation lines about TLS verification, CA bundles, client certificates, SSL errors, and environment variables.",
        },
    ],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT.parent, check=True)


def run_agent(condition: str, spec: dict[str, Any]) -> Path:
    run_id = f"T5_online_{SEED}_{condition}_G3_{spec['agent']}"
    condition_dir = OUT / condition
    run_out = condition_dir / "runs" / f"{run_id}.json"
    if run_out.exists():
        return run_out
    run([
        sys.executable,
        str(BASE / "tools" / "run_autodl_blind_agent.py"),
        "--task-root",
        str(TASK_ROOT),
        "--task-root-label",
        "experiments/false_convergence_pilot/T5_real_repo_requests_tls/",
        "--run-id",
        run_id,
        "--files",
        *spec["files"],
        "--out",
        str(run_out),
        "--raw-out",
        str(condition_dir / "raw" / f"{run_id}_raw_response.json"),
        "--cost-out",
        str(condition_dir / "cost" / f"{run_id}_cost.json"),
        "--search-budget",
        str(SEARCH_BUDGET),
        "--max-lines-per-file",
        str(MAX_LINES_PER_FILE),
        "--prompt-variant",
        spec["prompt_variant"],
        "--prompt-addon",
        spec["prompt_addon"],
        "--model",
        MODEL,
    ])
    return run_out


def merge_and_score(condition: str, run_files: list[Path]) -> None:
    condition_dir = OUT / condition
    merged = condition_dir / "merged_itemsets.json"
    score_json = condition_dir / "score_summary.json"
    score_md = condition_dir / "score_summary.md"
    run([
        sys.executable,
        str(BASE / "tools" / "merge_blind_itemsets.py"),
        "--task-id",
        TASK_ID,
        "--oracle-size",
        str(ORACLE_SIZE),
        "--inputs",
        *[str(path) for path in run_files],
        "--out",
        str(merged),
    ])
    run([
        sys.executable,
        str(BASE / "tools" / "score_itemsets.py"),
        "--oracle",
        str(BASE / "results" / "T5_real_repo_requests_tls_oracle.json"),
        "--runs",
        str(merged),
        "--out-json",
        str(score_json),
        "--out-md",
        str(score_md),
    ])


def write_manifest(status: str, error: str | None = None) -> None:
    manifest = {
        "suite": "online_blind_validation_minimal",
        "status": status,
        "created_or_updated_at": utc_now(),
        "task": "T5 Requests TLS certificate audit",
        "repository": "psf/requests",
        "commit": "1190afd14fca74292946d62c4c8169880a47ff67",
        "seed": SEED,
        "model": MODEL,
        "search_budget": SEARCH_BUDGET,
        "max_lines_per_file": MAX_LINES_PER_FILE,
        "api_key_env": "AUTODL_ART_API_KEY",
        "api_key_present": bool(os.environ.get("AUTODL_ART_API_KEY")),
        "conditions": CONDITIONS,
        "outputs": {
            "root": str(OUT),
            "per_condition": {
                condition: {
                    "runs": str(OUT / condition / "runs"),
                    "raw": str(OUT / condition / "raw"),
                    "cost": str(OUT / condition / "cost"),
                    "merged_itemsets": str(OUT / condition / "merged_itemsets.json"),
                    "score_summary_json": str(OUT / condition / "score_summary.json"),
                    "score_summary_md": str(OUT / condition / "score_summary.md"),
                }
                for condition in CONDITIONS
            },
        },
        "error": error,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    if not os.environ.get("AUTODL_ART_API_KEY"):
        write_manifest("blocked_missing_api_key", "AUTODL_ART_API_KEY is not set")
        raise SystemExit("Missing AUTODL_ART_API_KEY")
    write_manifest("running")
    try:
        for condition, specs in CONDITIONS.items():
            run_files = [run_agent(condition, spec) for spec in specs]
            merge_and_score(condition, run_files)
        write_manifest("completed")
    except Exception as exc:
        write_manifest("failed", repr(exc))
        raise


if __name__ == "__main__":
    main()
