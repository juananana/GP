#!/usr/bin/env python3
"""Run held-out Click online validation for the frozen staged controller.

Requests TLS is treated as the development task. This script does not tune on
Click results: it writes the frozen escalation rules to a manifest, runs blind
Click discovery/audit calls when requested, and then scores held-out policies.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any

from run_autodl_blind_agent import call_api, extract_output_text, parse_json_text


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "false_convergence_pilot"
TASK_ROOT = BASE / "T4_real_repo_click"
OUT_ROOT = BASE / "online_heldout_click_staged_controller"
ORACLE = BASE / "results" / "T4_real_repo_click_deprecation_oracle.json"
MODEL = "gpt-5.3-codex"
TASK_ID = "T4_click_heldout_staged_controller"
ORACLE_SIZE = 149
THETA = 0.95
SEEDS = ["seed04", "seed05", "seed06"]
CONDITIONS = ["homogeneous", "source_partitioned", "independent_context"]

COMMON_FILES = [
    "repo/src/click/__init__.py",
    "repo/src/click/core.py",
    "repo/src/click/parser.py",
    "repo/tests/test_arguments.py",
    "repo/tests/test_options.py",
    "repo/tests/test_commands.py",
    "repo/docs/commands-and-groups.md",
    "repo/CHANGES.md",
]

PARTITIONS = {
    "src": [
        "repo/src/click/__init__.py",
        "repo/src/click/core.py",
        "repo/src/click/parser.py",
    ],
    "tests": [
        "repo/tests/test_arguments.py",
        "repo/tests/test_options.py",
        "repo/tests/test_commands.py",
    ],
    "docs_changelog": [
        "repo/docs/commands-and-groups.md",
        "repo/CHANGES.md",
    ],
}

FROZEN_CONTROLLER = {
    "name": "staged_singleton_then_source_partitioned_v1",
    "frozen_from": "Requests TLS development online audit results",
    "stage_order": [
        "conservative_consensus",
        "singleton_verifier",
        "source_partitioned_review_if_escalation_condition_holds",
        "abstain_unless_certification_conditions_hold",
    ],
    "escalate_to_source_review_if_any": {
        "singleton_ratio_ge": 0.10,
        "consensus_to_union_le": 0.92,
        "missing_required_source_family": True,
    },
    "certify_safe_if_all": {
        "no_source_escalation_triggered": True,
        "declared_oracle_size_visible_in_task": ORACLE_SIZE,
        "final_item_count_ge_theta_times_declared_oracle_size": ceil(THETA * ORACLE_SIZE),
        "all_required_source_families_present": True,
        "mean_confidence_ge": 0.75,
        "all_discovery_agents_report_completion": True,
        "singleton_verifier_executed_when_queue_nonempty": True,
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical(path: str, line: int | str) -> str:
    return f"{path.replace('\\', '/')}:{int(line)}"


def parse_item(item: Any) -> str:
    if isinstance(item, str):
        path, line = item.rsplit(":", 1)
        return canonical(path, line)
    return canonical(item["file_path"], item["line"])


def key_to_item(key: str) -> dict[str, Any]:
    path, line = key.rsplit(":", 1)
    return {"file_path": path, "line": int(line)}


def source_family(key: str) -> str:
    path = key.rsplit(":", 1)[0]
    if path.startswith("repo/src/"):
        return "src"
    if path.startswith("repo/tests/"):
        return "tests"
    if path.startswith("repo/docs/") or path == "repo/CHANGES.md":
        return "docs_changelog"
    return "other"


def condition_specs(seed: str) -> dict[str, list[dict[str, Any]]]:
    seed_note = f"Fixed held-out Click seed label: {seed}. Do not use previous run outputs."
    return {
        "homogeneous": [
            {
                "agent": f"agent{i:02d}",
                "files": COMMON_FILES,
                "variant": "click_standard_high_recall",
                "addon": (
                    f"{seed_note} Prioritize complete line-level coverage across "
                    "implementation, tests, documentation, and bounded changelog entries."
                ),
            }
            for i in range(1, 4)
        ],
        "source_partitioned": [
            {
                "agent": "agent01",
                "files": PARTITIONS["src"],
                "variant": "click_partition_src",
                "addon": f"{seed_note} Inspect only the implementation partition.",
            },
            {
                "agent": "agent02",
                "files": PARTITIONS["tests"],
                "variant": "click_partition_tests",
                "addon": f"{seed_note} Inspect only the tests partition.",
            },
            {
                "agent": "agent03",
                "files": PARTITIONS["docs_changelog"],
                "variant": "click_partition_docs_changelog",
                "addon": f"{seed_note} Inspect only docs and bounded changelog entries.",
            },
        ],
        "independent_context": [
            {
                "agent": "agent01",
                "files": PARTITIONS["src"] + PARTITIONS["tests"],
                "variant": "click_independent_src_tests",
                "addon": f"{seed_note} Start from source and tests.",
            },
            {
                "agent": "agent02",
                "files": PARTITIONS["tests"] + PARTITIONS["docs_changelog"],
                "variant": "click_independent_tests_docs",
                "addon": f"{seed_note} Start from tests, docs, and changelog.",
            },
            {
                "agent": "agent03",
                "files": PARTITIONS["docs_changelog"] + PARTITIONS["src"],
                "variant": "click_independent_docs_src",
                "addon": f"{seed_note} Start from docs/changelog and source.",
            },
        ],
    }


def run_subprocess(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT.parent, check=True)


def run_agent(seed: str, condition: str, spec: dict[str, Any], dry_run: bool) -> Path:
    run_id = f"T4_click_{seed}_{condition}_G3_{spec['agent']}"
    condition_dir = OUT_ROOT / seed / condition
    out = condition_dir / "runs" / f"{run_id}.json"
    if dry_run or out.exists():
        return out
    run_subprocess([
        sys.executable,
        str(BASE / "tools" / "run_autodl_blind_agent.py"),
        "--task-root",
        str(TASK_ROOT),
        "--task-root-label",
        "experiments/false_convergence_pilot/T4_real_repo_click/",
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
        "1400",
        "--prompt-variant",
        spec["variant"],
        "--prompt-addon",
        spec["addon"],
        "--model",
        MODEL,
    ])
    return out


def merge_and_score(seed: str, condition: str, run_files: list[Path], dry_run: bool) -> None:
    if dry_run or not all(path.exists() for path in run_files):
        return
    condition_dir = OUT_ROOT / seed / condition
    merged = condition_dir / "merged_itemsets.json"
    score_json = condition_dir / "score_summary.json"
    score_md = condition_dir / "score_summary.md"
    run_subprocess([
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
    run_subprocess([
        sys.executable,
        str(BASE / "tools" / "score_itemsets.py"),
        "--oracle",
        str(ORACLE),
        "--runs",
        str(merged),
        "--out-json",
        str(score_json),
        "--out-md",
        str(score_md),
    ])


def load_runs(seed: str, condition: str) -> list[dict[str, Any]]:
    return json.loads((OUT_ROOT / seed / condition / "merged_itemsets.json").read_text(encoding="utf-8"))["runs"]


def discovery_sets(seed: str, condition: str) -> dict[str, Any]:
    runs = load_runs(seed, condition)
    itemsets = [{parse_item(item) for item in run.get("items", [])} for run in runs]
    counts = Counter(item for itemset in itemsets for item in itemset)
    union = set(counts)
    consensus = {item for item, count in counts.items() if count >= 2}
    singleton = {item for item, count in counts.items() if count == 1}
    confidences = [float(run.get("self_reported_confidence", 0.0) or 0.0) for run in runs]
    completions = [bool(run.get("self_reported_completion", True)) for run in runs]
    return {
        "runs": runs,
        "sets": itemsets,
        "union": union,
        "consensus": consensus,
        "singleton": singleton,
        "mean_confidence": statistics.mean(confidences) if confidences else 0.0,
        "all_complete": all(completions),
        "singleton_ratio": len(singleton) / len(union) if union else 0.0,
        "consensus_to_union": len(consensus) / len(union) if union else 1.0,
    }


def load_oracle() -> set[str]:
    raw = json.loads(ORACLE.read_text(encoding="utf-8"))
    return {canonical(item["file_path"], item["line"]) for item in raw["items"]}


def score(items: set[str], oracle: set[str]) -> dict[str, Any]:
    tp = items & oracle
    fp = items - oracle
    return {
        "tp": len(tp),
        "fp": len(fp),
        "found": len(items),
        "recall": len(tp) / len(oracle),
        "precision": len(tp) / len(items) if items else 1.0,
    }


def load_cost_dir(path: Path) -> dict[str, Any]:
    total = {"input_tokens": 0, "output_tokens": 0, "tool_calls": 0, "wall_clock_seconds": 0.0}
    if not path.exists():
        return total
    for cost_path in path.glob("*_cost.json"):
        raw = json.loads(cost_path.read_text(encoding="utf-8"))
        total["input_tokens"] += int(raw.get("input_tokens") or 0)
        total["output_tokens"] += int(raw.get("output_tokens") or 0)
        total["tool_calls"] += int(raw.get("tool_calls") or 0)
        total["wall_clock_seconds"] += float(raw.get("wall_clock_seconds") or 0.0)
    return total


def add_cost(*costs: dict[str, Any]) -> dict[str, Any]:
    total = {"input_tokens": 0, "output_tokens": 0, "tool_calls": 0, "wall_clock_seconds": 0.0}
    for cost in costs:
        for key in total:
            total[key] += cost[key]
    return total


def line_snippet(rel_path: str, line: int, radius: int = 2) -> str:
    lines = (TASK_ROOT / rel_path).read_text(encoding="utf-8", errors="ignore").splitlines()
    start = max(1, line - radius)
    end = min(len(lines), line + radius)
    rendered = [f"### {rel_path}:{line}"]
    for line_no in range(start, end + 1):
        rendered.append(f"{line_no:04d}: {lines[line_no - 1]}")
    return "\n".join(rendered)


def candidate_packet(candidates: list[str]) -> str:
    chunks = []
    for idx, key in enumerate(candidates, start=1):
        path, line = key.rsplit(":", 1)
        chunks.append(f"Candidate {idx}: {key}\n{line_snippet(path, int(line))}")
    return "\n\n".join(chunks)


def verifier_prompt(run_id: str, candidates: list[str]) -> str:
    task_md = (TASK_ROOT / "TASK.md").read_text(encoding="utf-8")
    return f"""You are an online singleton verifier for a held-out Click audit.

Allowed context: candidate line snippets from the Click task directory.
Forbidden context: oracle files, score summaries, experiment results, and any
line not shown below.

Task instructions:

{task_md}

Review the candidate singleton list. Return only candidates that truly belong
to the deprecated API surface audit. Do not add new lines.

Return JSON only:
{{
  "run_id": "{run_id}",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [
    {{"file_path": "repo/src/click/core.py", "line": 1359}}
  ]
}}

Candidate snippets:

{candidate_packet(candidates)}
"""


def call_singleton_verifier(
    seed: str,
    condition: str,
    candidates: list[str],
    endpoint: str,
    api_key: str,
    dry_run: bool,
) -> tuple[set[str], dict[str, Any], Path]:
    run_id = f"T4_click_{seed}_{condition}_G6_singleton_verifier"
    run_path = OUT_ROOT / "audit_policy_eval" / "runs" / seed / condition / f"{run_id}.json"
    raw_path = OUT_ROOT / "audit_policy_eval" / "raw" / seed / condition / f"{run_id}_raw_response.json"
    cost_path = OUT_ROOT / "audit_policy_eval" / "cost" / seed / condition / f"{run_id}_cost.json"
    if run_path.exists():
        raw = json.loads(run_path.read_text(encoding="utf-8"))
        return {parse_item(item) for item in raw.get("items", [])}, load_cost_dir(cost_path.parent), run_path
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
        "items": [key_to_item(key) for item in parsed.get("items", []) if (key := parse_item(item)) in allowed],
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
    return {parse_item(item) for item in run["items"]}, load_cost_dir(cost_path.parent), run_path


def should_escalate(data: dict[str, Any]) -> tuple[bool, str]:
    reasons = []
    families = {source_family(item) for item in data["consensus"]}
    if data["singleton_ratio"] >= FROZEN_CONTROLLER["escalate_to_source_review_if_any"]["singleton_ratio_ge"]:
        reasons.append("singleton_ratio")
    if data["consensus_to_union"] <= FROZEN_CONTROLLER["escalate_to_source_review_if_any"]["consensus_to_union_le"]:
        reasons.append("consensus_union_gap")
    missing = {"src", "tests", "docs_changelog"} - families
    if missing:
        reasons.append("missing_source_family:" + ",".join(sorted(missing)))
    return bool(reasons), "+".join(reasons) if reasons else "no_escalation"


def certify(items: set[str], data: dict[str, Any], singleton_executed: bool, escalated: bool) -> tuple[str, str]:
    reasons = []
    if escalated:
        reasons.append("source_escalation_triggered")
    min_count = FROZEN_CONTROLLER["certify_safe_if_all"]["final_item_count_ge_theta_times_declared_oracle_size"]
    if len(items) < min_count:
        reasons.append("final_count_below_declared_threshold")
    if {source_family(item) for item in items} >= {"src", "tests", "docs_changelog"}:
        pass
    else:
        reasons.append("missing_required_source_family")
    if data["mean_confidence"] < FROZEN_CONTROLLER["certify_safe_if_all"]["mean_confidence_ge"]:
        reasons.append("mean_confidence_below_threshold")
    if not data["all_complete"]:
        reasons.append("not_all_agents_report_completion")
    if data["singleton"] and not singleton_executed:
        reasons.append("singleton_queue_not_verified")
    return ("safe_to_stop", "all_conditions_met") if not reasons else ("abstain", "+".join(reasons))


def stable_sample(items: set[str], seed: str, condition: str) -> set[str]:
    ranked = sorted(
        items,
        key=lambda item: hashlib.sha256(f"{seed}|{condition}|click_sample|{item}".encode("utf-8")).hexdigest(),
    )
    return set(ranked[: min(len(ranked), max(15, round(len(ranked) * 0.25)))])


def evaluate(args: argparse.Namespace) -> list[dict[str, Any]]:
    api_key = os.environ.get(args.api_key_env, "")
    if args.run_online and not api_key:
        raise SystemExit(f"Missing API key env var: {args.api_key_env}")
    oracle = load_oracle()
    rows = []
    for seed in args.seeds:
        source_union = discovery_sets(seed, "source_partitioned")["union"]
        independent_union = discovery_sets(seed, "independent_context")["union"]
        source_cost = load_cost_dir(OUT_ROOT / seed / "source_partitioned" / "cost")
        independent_cost = load_cost_dir(OUT_ROOT / seed / "independent_context" / "cost")
        for condition in args.conditions:
            data = discovery_sets(seed, condition)
            base = data["consensus"]
            base_cost = load_cost_dir(OUT_ROOT / seed / condition / "cost")
            singleton_items, singleton_cost, singleton_path = call_singleton_verifier(
                seed,
                condition,
                sorted(data["singleton"]),
                args.endpoint,
                api_key,
                not args.run_online,
            )
            escalate, reason = should_escalate(data)
            source_review_cost = {"input_tokens": 0, "output_tokens": 0, "tool_calls": 0, "wall_clock_seconds": 0.0}
            if condition != "source_partitioned":
                source_review_cost = source_cost
            staged = base | singleton_items | (source_union if escalate else set())
            cert, cert_reason = certify(staged, data, singleton_executed=bool(data["singleton"]), escalated=escalate)
            policies = {
                "no_audit": (base, {"input_tokens": 0, "output_tokens": 0, "tool_calls": 0, "wall_clock_seconds": 0.0}, "abstain", "no_audit"),
                "singleton_audit": (base | singleton_items, singleton_cost, "abstain", str(singleton_path)),
                "source_partitioned_review": (base | source_union, source_review_cost, "abstain", str(OUT_ROOT / seed / "source_partitioned")),
                "staged_controller": (staged, add_cost(singleton_cost, source_review_cost) if escalate else singleton_cost, cert, reason + "|" + cert_reason),
                "always_holdout": (
                    base | singleton_items | source_union | independent_union,
                    add_cost(singleton_cost, source_cost if condition != "source_partitioned" else {"input_tokens": 0, "output_tokens": 0, "tool_calls": 0, "wall_clock_seconds": 0.0}, independent_cost if condition != "independent_context" else {"input_tokens": 0, "output_tokens": 0, "tool_calls": 0, "wall_clock_seconds": 0.0}),
                    "abstain",
                    "source_partitioned+independent_context",
                ),
            }
            pre_score = score(base, oracle)
            for policy, (items, audit_cost, decision, evidence) in policies.items():
                post = score(items, oracle)
                recovered = (items - base) & oracle
                introduced = (items - base) - oracle
                audit_tokens = int(audit_cost["input_tokens"]) + int(audit_cost["output_tokens"])
                end_cost = add_cost(base_cost, audit_cost)
                end_tokens = int(end_cost["input_tokens"]) + int(end_cost["output_tokens"])
                rows.append({
                    "seed": seed,
                    "condition": condition,
                    "policy": policy,
                    "pre_recall": pre_score["recall"],
                    "post_recall": post["recall"],
                    "post_precision": post["precision"],
                    "recovered_tp": len(recovered),
                    "introduced_fp": len(introduced),
                    "audit_tokens": audit_tokens,
                    "end_to_end_tokens": end_tokens,
                    "audit_wall_clock_seconds": audit_cost["wall_clock_seconds"],
                    "end_to_end_wall_clock_seconds": end_cost["wall_clock_seconds"],
                    "decision": decision,
                    "actual_safe": post["recall"] >= THETA,
                    "false_certification": decision == "safe_to_stop" and post["recall"] < THETA,
                    "abstained_on_safe": decision != "safe_to_stop" and post["recall"] >= THETA,
                    "escalated_to_source": escalate if policy == "staged_controller" else "",
                    "controller_reason": evidence,
                })
    return rows


def write_outputs(rows: list[dict[str, Any]]) -> None:
    eval_root = OUT_ROOT / "audit_policy_eval"
    eval_root.mkdir(parents=True, exist_ok=True)
    csv_path = eval_root / "CLICK_HELDOUT_STAGED_RESULTS.csv"
    md_path = eval_root / "CLICK_HELDOUT_STAGED_RESULTS.md"
    json_path = eval_root / "CLICK_HELDOUT_STAGED_RESULTS.json"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    policies = ["no_audit", "singleton_audit", "source_partitioned_review", "staged_controller", "always_holdout"]
    lines = [
        "# Click Held-Out Staged Controller Results",
        "",
        "The staged controller was frozen from Requests TLS before evaluating Click.",
        "",
        "## Policy Means",
        "",
        "| policy | n | pre R | post R | precision | recovered TP | introduced FP | audit tok | e2e tok | FCR | safe cov | abstain |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for policy in policies:
        subset = [row for row in rows if row["policy"] == policy]
        safe_states = [row for row in subset if row["actual_safe"]]
        certified = [row for row in subset if row["decision"] == "safe_to_stop"]
        fcr = sum(1 for row in certified if row["false_certification"]) / len(certified) if certified else 0.0
        safe_cov = sum(1 for row in safe_states if row["decision"] == "safe_to_stop") / len(safe_states) if safe_states else 0.0
        abstain = sum(1 for row in subset if row["decision"] != "safe_to_stop") / len(subset)
        lines.append(
            "| {policy} | {n} | {pre:.3f} | {post:.3f} | {prec:.3f} | {rtp:.1f} | {ifp:.1f} | {atok:.0f} | {etok:.0f} | {fcr:.3f} | {sc:.3f} | {abs:.3f} |".format(
                policy=policy.replace("_", "-"),
                n=len(subset),
                pre=statistics.mean(row["pre_recall"] for row in subset),
                post=statistics.mean(row["post_recall"] for row in subset),
                prec=statistics.mean(row["post_precision"] for row in subset),
                rtp=statistics.mean(row["recovered_tp"] for row in subset),
                ifp=statistics.mean(row["introduced_fp"] for row in subset),
                atok=statistics.mean(row["audit_tokens"] for row in subset),
                etok=statistics.mean(row["end_to_end_tokens"] for row in subset),
                fcr=fcr,
                sc=safe_cov,
                abs=abstain,
            )
        )
    lines.extend(["", "## Frozen Controller", "", "```json", json.dumps(FROZEN_CONTROLLER, indent=2), "```"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT_ROOT / "MANIFEST.json").write_text(json.dumps({
        "suite": "click_heldout_staged_controller",
        "status": "completed",
        "created_or_updated_at": now_iso(),
        "model": MODEL,
        "seeds": SEEDS,
        "conditions": CONDITIONS,
        "frozen_controller": FROZEN_CONTROLLER,
        "outputs": {"csv": str(csv_path), "json": str(json_path), "markdown": str(md_path)},
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(md_path)


def run_discovery(args: argparse.Namespace) -> None:
    for seed in args.seeds:
        specs_by_condition = condition_specs(seed)
        for condition in args.conditions:
            run_files = [run_agent(seed, condition, spec, args.dry_run) for spec in specs_by_condition[condition]]
            merge_and_score(seed, condition, run_files, args.dry_run)


def main() -> None:
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
    run_discovery(args)
    if not args.dry_run:
        write_outputs(evaluate(args))


if __name__ == "__main__":
    main()
