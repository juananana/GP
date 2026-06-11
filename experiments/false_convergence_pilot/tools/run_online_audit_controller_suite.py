#!/usr/bin/env python3
"""Run or stage the Requests TLS online audit-controller discovery suite.

This script expands the previous seed04-only blind validation into the P0
experiment grid recommended by docs/repair1.md. It deliberately separates
discovery from audit-policy evaluation: the current implementation runs blind
discovery agents and writes a manifest for the audit policies that still require
online verifier/holdout agents. Oracle files are never read here.
"""

from __future__ import annotations

import argparse
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
OUT_ROOT = BASE / "online_audit_controller" / "T5_requests_tls"
MODEL = "gpt-5.3-codex"
SEARCH_BUDGET = 180
MAX_LINES_PER_FILE = 1200
TASK_ID = "T5_real_repo_requests_tls_online_audit_controller"
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

PARTITIONS = {
    "src": [
        "repo/src/requests/adapters.py",
        "repo/src/requests/sessions.py",
        "repo/src/requests/certs.py",
        "repo/src/requests/utils.py",
        "repo/src/requests/exceptions.py",
    ],
    "tests": [
        "repo/tests/test_requests.py",
        "repo/tests/conftest.py",
        "repo/tests/testserver/server.py",
        "repo/tests/certs/README.md",
    ],
    "docs": [
        "repo/docs/user/advanced.rst",
        "repo/docs/community/faq.rst",
        "repo/docs/community/recommended.rst",
        "repo/README.md",
    ],
}

AUDIT_POLICIES = [
    "no_audit",
    "random_holdout",
    "singleton_audit",
    "boundary_focused_holdout",
    "source_partitioned_review",
    "always_holdout",
    "risk_triggered_audit",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def condition_specs(seed: str) -> dict[str, list[dict[str, Any]]]:
    seed_note = f"Fixed evaluation seed label: {seed}. Do not use any previous run output."
    return {
        "homogeneous": [
            {
                "agent": f"agent{i:02d}",
                "files": COMMON_FILES,
                "prompt_variant": "standard_high_recall",
                "prompt_addon": (
                    f"{seed_note} Prioritize complete line-level coverage across "
                    "implementation, tests, fixtures, and documentation."
                ),
            }
            for i in range(1, 4)
        ],
        "prompt_diverse": [
            {
                "agent": "agent01",
                "files": COMMON_FILES,
                "prompt_variant": "implementation_focus",
                "prompt_addon": (
                    f"{seed_note} Focus first on implementation lines that control "
                    "verify behavior, CA bundle selection, client certificates, and SSL errors."
                ),
            },
            {
                "agent": "agent02",
                "files": COMMON_FILES,
                "prompt_variant": "test_fixture_focus",
                "prompt_addon": (
                    f"{seed_note} Focus first on tests, fixtures, certificate "
                    "infrastructure, and testserver behavior."
                ),
            },
            {
                "agent": "agent03",
                "files": COMMON_FILES,
                "prompt_variant": "docs_boundary_focus",
                "prompt_addon": (
                    f"{seed_note} Focus first on documentation and boundary cases "
                    "involving certificate verification, CA bundles, and environment variables."
                ),
            },
        ],
        "source_partitioned": [
            {
                "agent": "agent01",
                "files": PARTITIONS["src"],
                "prompt_variant": "source_partition_src",
                "prompt_addon": f"{seed_note} Inspect only the implementation partition.",
            },
            {
                "agent": "agent02",
                "files": PARTITIONS["tests"],
                "prompt_variant": "source_partition_tests",
                "prompt_addon": f"{seed_note} Inspect only the test and fixture partition.",
            },
            {
                "agent": "agent03",
                "files": PARTITIONS["docs"],
                "prompt_variant": "source_partition_docs",
                "prompt_addon": f"{seed_note} Inspect only the documentation partition.",
            },
        ],
        "independent_context": [
            {
                "agent": "agent01",
                "files": PARTITIONS["src"] + PARTITIONS["tests"],
                "prompt_variant": "independent_src_tests",
                "prompt_addon": (
                    f"{seed_note} Use an independent source order. Start from source "
                    "and tests; include docs only when directly cited in the provided context."
                ),
            },
            {
                "agent": "agent02",
                "files": PARTITIONS["tests"] + PARTITIONS["docs"],
                "prompt_variant": "independent_tests_docs",
                "prompt_addon": (
                    f"{seed_note} Use an independent source order. Start from tests "
                    "and docs; include implementation only when directly justified."
                ),
            },
            {
                "agent": "agent03",
                "files": PARTITIONS["docs"] + PARTITIONS["src"],
                "prompt_variant": "independent_docs_src",
                "prompt_addon": (
                    f"{seed_note} Use an independent source order. Start from docs "
                    "and implementation; include tests only when directly justified."
                ),
            },
        ],
    }


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT.parent, check=True)


def run_agent(seed: str, condition: str, spec: dict[str, Any], dry_run: bool) -> Path:
    run_id = f"T5_online_{seed}_{condition}_G3_{spec['agent']}"
    condition_dir = OUT_ROOT / seed / condition
    run_out = condition_dir / "runs" / f"{run_id}.json"
    if run_out.exists() or dry_run:
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


def merge_and_score(seed: str, condition: str, run_files: list[Path], dry_run: bool) -> None:
    if dry_run or not all(path.exists() for path in run_files):
        return
    condition_dir = OUT_ROOT / seed / condition
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


def write_manifest(seeds: list[str], dry_run: bool, status: str, error: str | None = None) -> None:
    manifest = {
        "suite": "online_audit_controller_requests_tls",
        "status": status,
        "dry_run": dry_run,
        "created_or_updated_at": utc_now(),
        "task": "T5 Requests TLS certificate audit",
        "repository": "psf/requests",
        "commit": "1190afd14fca74292946d62c4c8169880a47ff67",
        "model": MODEL,
        "seeds": seeds,
        "discovery_conditions": list(condition_specs(seeds[0]).keys()) if seeds else [],
        "audit_policies_planned": AUDIT_POLICIES,
        "api_key_env": "AUTODL_ART_API_KEY",
        "api_key_present": bool(os.environ.get("AUTODL_ART_API_KEY")),
        "outputs": {
            "root": str(OUT_ROOT),
            "per_seed": {seed: str(OUT_ROOT / seed) for seed in seeds},
        },
        "online_audit_status": "not_implemented_yet_verifier_and_holdout_agents_required",
        "error": error,
    }
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", default=["seed04", "seed05", "seed06", "seed07", "seed08"])
    parser.add_argument("--conditions", nargs="+", default=["homogeneous", "prompt_diverse", "source_partitioned", "independent_context"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not os.environ.get("AUTODL_ART_API_KEY"):
        write_manifest(args.seeds, args.dry_run, "blocked_missing_api_key", "AUTODL_ART_API_KEY is not set")
        raise SystemExit("Missing AUTODL_ART_API_KEY")

    write_manifest(args.seeds, args.dry_run, "running")
    try:
        for seed in args.seeds:
            specs_by_condition = condition_specs(seed)
            for condition in args.conditions:
                specs = specs_by_condition[condition]
                run_files = [run_agent(seed, condition, spec, args.dry_run) for spec in specs]
                merge_and_score(seed, condition, run_files, args.dry_run)
        write_manifest(args.seeds, args.dry_run, "dry_run_completed" if args.dry_run else "discovery_completed")
    except Exception as exc:
        write_manifest(args.seeds, args.dry_run, "failed", repr(exc))
        raise


if __name__ == "__main__":
    main()
