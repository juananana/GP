#!/usr/bin/env python3
"""Run T6 itsdangerous external validation for the frozen staged controller."""

from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any

import run_click_heldout_staged_controller as base
from run_autodl_blind_agent import call_api, extract_output_text, parse_json_text


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "false_convergence_pilot"
TASK_ROOT = BASE / "T6_real_repo_itsdangerous"
OUT_ROOT = BASE / "online_external_itsdangerous_staged_controller"
ORACLE = BASE / "results" / "T6_real_repo_itsdangerous_timed_signing_oracle.json"
TASK_ID = "T6_real_repo_itsdangerous_timed_signing_external"
ORACLE_SIZE = 160
MODEL = "gpt-5.3-codex"
SEEDS = ["seed04", "seed05", "seed06"]
CONDITIONS = ["homogeneous", "source_partitioned", "independent_context"]

COMMON_FILES = [
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

PARTITIONS = {
    "src": [
        "repo/src/itsdangerous/timed.py",
        "repo/src/itsdangerous/exc.py",
        "repo/src/itsdangerous/url_safe.py",
        "repo/src/itsdangerous/__init__.py",
    ],
    "tests": [
        "repo/tests/test_itsdangerous/test_timed.py",
        "repo/tests/test_itsdangerous/test_url_safe.py",
    ],
    "docs_changelog": [
        "repo/docs/timed.rst",
        "repo/docs/exceptions.rst",
        "repo/docs/url_safe.rst",
        "repo/README.md",
        "repo/CHANGES.rst",
    ],
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def source_family(key: str) -> str:
    path = key.rsplit(":", 1)[0]
    if path.startswith("repo/src/"):
        return "src"
    if path.startswith("repo/tests/"):
        return "tests"
    if path.startswith("repo/docs/") or path in {"repo/README.md", "repo/CHANGES.rst"}:
        return "docs_changelog"
    return "other"


def condition_specs(seed: str) -> dict[str, list[dict[str, Any]]]:
    seed_note = f"Fixed external itsdangerous seed label: {seed}. Do not use previous run outputs."
    return {
        "homogeneous": [
            {
                "agent": f"agent{i:02d}",
                "files": COMMON_FILES,
                "variant": "itsdangerous_standard_high_recall",
                "addon": (
                    f"{seed_note} Prioritize complete line-level coverage across "
                    "timestamp signing implementation, exceptions, tests, docs, and changelog."
                ),
            }
            for i in range(1, 4)
        ],
        "source_partitioned": [
            {
                "agent": "agent01",
                "files": PARTITIONS["src"],
                "variant": "itsdangerous_partition_src",
                "addon": f"{seed_note} Inspect only source implementation and public exports.",
            },
            {
                "agent": "agent02",
                "files": PARTITIONS["tests"],
                "variant": "itsdangerous_partition_tests",
                "addon": f"{seed_note} Inspect only tests.",
            },
            {
                "agent": "agent03",
                "files": PARTITIONS["docs_changelog"],
                "variant": "itsdangerous_partition_docs_changelog",
                "addon": f"{seed_note} Inspect only docs, README, and changelog.",
            },
        ],
        "independent_context": [
            {
                "agent": "agent01",
                "files": PARTITIONS["src"] + PARTITIONS["tests"],
                "variant": "itsdangerous_independent_src_tests",
                "addon": f"{seed_note} Start from source and tests.",
            },
            {
                "agent": "agent02",
                "files": PARTITIONS["tests"] + PARTITIONS["docs_changelog"],
                "variant": "itsdangerous_independent_tests_docs",
                "addon": f"{seed_note} Start from tests, docs, and changelog.",
            },
            {
                "agent": "agent03",
                "files": PARTITIONS["docs_changelog"] + PARTITIONS["src"],
                "variant": "itsdangerous_independent_docs_src",
                "addon": f"{seed_note} Start from docs/changelog and source.",
            },
        ],
    }


def run_agent(seed: str, condition: str, spec: dict[str, Any], dry_run: bool) -> Path:
    run_id = f"T6_itsdangerous_{seed}_{condition}_G3_{spec['agent']}"
    condition_dir = OUT_ROOT / seed / condition
    out = condition_dir / "runs" / f"{run_id}.json"
    if dry_run or out.exists():
        return out
    subprocess.run([
        sys.executable,
        str(BASE / "tools" / "run_autodl_blind_agent.py"),
        "--task-root",
        str(TASK_ROOT),
        "--task-root-label",
        "experiments/false_convergence_pilot/T6_real_repo_itsdangerous/",
        "--run-id",
        run_id,
        "--files",
        *spec["files"],
        "--out",
        str(out),
        "--raw-out",
        str(condition_dir / "raw" / f"{run_id}_raw_response.json"),
        "--cost-out",
        str(condition_dir / "cost" / f"{run_id}_cost.json"),
        "--search-budget",
        "180",
        "--max-lines-per-file",
        "1600",
        "--prompt-variant",
        spec["variant"],
        "--prompt-addon",
        spec["addon"],
        "--model",
        MODEL,
    ], cwd=ROOT.parent, check=True)
    return out


def verifier_prompt(run_id: str, candidates: list[str]) -> str:
    task_md = (TASK_ROOT / "TASK.md").read_text(encoding="utf-8")
    return f"""You are an online singleton verifier for a held-out itsdangerous audit.

Allowed context: candidate line snippets from the itsdangerous task directory.
Forbidden context: oracle files, score summaries, experiment results, and any
line not shown below.

Task instructions:

{task_md}

Review the candidate singleton list. Return only candidates that truly belong
to the timestamped signing and expiration audit. Do not add new lines.

Return JSON only:
{{
  "run_id": "{run_id}",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [
    {{"file_path": "repo/src/itsdangerous/timed.py", "line": 141}}
  ]
}}

Candidate snippets:

{base.candidate_packet(candidates)}
"""


def call_singleton_verifier(
    seed: str,
    condition: str,
    candidates: list[str],
    endpoint: str,
    api_key: str,
    dry_run: bool,
) -> tuple[set[str], dict[str, Any], Path]:
    run_id = f"T6_itsdangerous_{seed}_{condition}_G6_singleton_verifier"
    run_path = OUT_ROOT / "audit_policy_eval" / "runs" / seed / condition / f"{run_id}.json"
    raw_path = OUT_ROOT / "audit_policy_eval" / "raw" / seed / condition / f"{run_id}_raw_response.json"
    cost_path = OUT_ROOT / "audit_policy_eval" / "cost" / seed / condition / f"{run_id}_cost.json"
    if run_path.exists():
        raw = json.loads(run_path.read_text(encoding="utf-8"))
        return {base.parse_item(item) for item in raw.get("items", [])}, base.load_cost_dir(cost_path.parent), run_path
    if dry_run or not candidates:
        return set(), {"input_tokens": 0, "output_tokens": 0, "tool_calls": 0, "wall_clock_seconds": 0.0}, run_path
    started = now_iso()
    start = time.perf_counter()
    response = call_api(endpoint, MODEL, api_key, verifier_prompt(run_id, candidates))
    wall = time.perf_counter() - start
    ended = now_iso()
    parsed = parse_json_text(extract_output_text(response))
    allowed = set(candidates)
    run = {
        "run_id": run_id,
        "self_reported_completion": bool(parsed.get("self_reported_completion", True)),
        "self_reported_confidence": float(parsed.get("self_reported_confidence", 0.0) or 0.0),
        "items": [
            base.key_to_item(key)
            for item in parsed.get("items", [])
            if (key := base.parse_item(item)) in allowed
        ],
    }
    run_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    cost_path.parent.mkdir(parents=True, exist_ok=True)
    run_path.write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    raw_path.write_text(json.dumps(response, indent=2, ensure_ascii=False), encoding="utf-8")
    usage = response.get("usage", {})
    cost_path.write_text(json.dumps({
        "run_id": run_id,
        "started_at": started,
        "ended_at": ended,
        "model_name": MODEL,
        "policy": "singleton_audit",
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "tool_calls": 0,
        "wall_clock_seconds": wall,
        "candidate_count": len(candidates),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    return {base.parse_item(item) for item in run["items"]}, base.load_cost_dir(cost_path.parent), run_path


def write_outputs(rows: list[dict[str, Any]]) -> None:
    eval_root = OUT_ROOT / "audit_policy_eval"
    eval_root.mkdir(parents=True, exist_ok=True)
    csv_path = eval_root / "T6_ITSDANGEROUS_STAGED_RESULTS.csv"
    md_path = eval_root / "T6_ITSDANGEROUS_STAGED_RESULTS.md"
    json_path = eval_root / "T6_ITSDANGEROUS_STAGED_RESULTS.json"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    policies = ["no_audit", "singleton_audit", "source_partitioned_review", "staged_controller", "always_holdout"]
    lines = [
        "# T6 itsdangerous External Staged Controller Results",
        "",
        "The staged controller was frozen before evaluating this new repository.",
        "",
        "| policy | n | pre R | post R | precision | F1 | recovered TP | introduced FP | audit tok | e2e tok | FCR | safe cov | abstain |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for policy in policies:
        subset = [row for row in rows if row["policy"] == policy]
        safe_states = [row for row in subset if row["actual_safe"]]
        certified = [row for row in subset if row["decision"] == "safe_to_stop"]
        fcr = sum(1 for row in certified if row["false_certification"]) / len(certified) if certified else 0.0
        safe_cov = sum(1 for row in safe_states if row["decision"] == "safe_to_stop") / len(safe_states) if safe_states else 0.0
        abstain = sum(1 for row in subset if row["decision"] != "safe_to_stop") / len(subset)

        def avg(name: str) -> float:
            return statistics.mean(float(row[name]) for row in subset)

        precision = avg("post_precision")
        recall = avg("post_recall")
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        lines.append(
            f"| {policy.replace('_', '-')} | {len(subset)} | {avg('pre_recall'):.3f} | {recall:.3f} | "
            f"{precision:.3f} | {f1:.3f} | {avg('recovered_tp'):.1f} | {avg('introduced_fp'):.1f} | "
            f"{avg('audit_tokens'):.0f} | {avg('end_to_end_tokens'):.0f} | {fcr:.3f} | {safe_cov:.3f} | {abstain:.3f} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT_ROOT / "MANIFEST.json").write_text(json.dumps({
        "suite": "t6_itsdangerous_external_staged_controller",
        "status": "completed",
        "created_or_updated_at": now_iso(),
        "model": MODEL,
        "seeds": SEEDS,
        "conditions": CONDITIONS,
        "controller": base.FROZEN_CONTROLLER,
        "outputs": {"csv": str(csv_path), "json": str(json_path), "markdown": str(md_path)},
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(md_path)


def configure() -> None:
    base.TASK_ROOT = TASK_ROOT
    base.OUT_ROOT = OUT_ROOT
    base.ORACLE = ORACLE
    base.ORACLE_SIZE = ORACLE_SIZE
    base.TASK_ID = TASK_ID
    base.MODEL = MODEL
    base.SEEDS = SEEDS
    base.CONDITIONS = CONDITIONS
    base.COMMON_FILES = COMMON_FILES
    base.PARTITIONS = PARTITIONS
    base.FROZEN_CONTROLLER["certify_safe_if_all"]["declared_oracle_size_visible_in_task"] = ORACLE_SIZE
    base.FROZEN_CONTROLLER["certify_safe_if_all"]["final_item_count_ge_theta_times_declared_oracle_size"] = ceil(base.THETA * ORACLE_SIZE)
    base.source_family = source_family
    base.condition_specs = condition_specs
    base.run_agent = run_agent
    base.call_singleton_verifier = call_singleton_verifier
    base.write_outputs = write_outputs


def main() -> None:
    configure()
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", default=SEEDS)
    parser.add_argument("--conditions", nargs="+", default=CONDITIONS)
    parser.add_argument("--run-online", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--api-key-env", default="AUTODL_ART_API_KEY")
    parser.add_argument("--endpoint", default="https://www.autodl.art/api/v1/responses")
    args = parser.parse_args()
    if args.run_online and not os.environ.get(args.api_key_env):
        raise SystemExit(f"Missing API key env var: {args.api_key_env}")
    base.run_discovery(args)
    if not args.dry_run:
        base.write_outputs(base.evaluate(args))


if __name__ == "__main__":
    main()
