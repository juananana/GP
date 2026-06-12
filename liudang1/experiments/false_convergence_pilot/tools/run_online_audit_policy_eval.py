#!/usr/bin/env python3
"""Evaluate online audit-controller policies for Requests TLS.

This script closes the P0 loop after blind discovery:

pre-audit consensus -> frozen policy trigger -> online audit evidence ->
post-audit score.

Policy triggers and audit queues are computed only from blind discovery logs.
The oracle is loaded only after policy outputs are fixed, for reporting.
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
from pathlib import Path
from typing import Any

from run_autodl_blind_agent import (
    call_api,
    extract_output_text,
    parse_json_text,
    prompt_for,
)


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "false_convergence_pilot"
TASK_ROOT = BASE / "T5_real_repo_requests_tls"
OUT_ROOT = BASE / "online_audit_controller" / "T5_requests_tls"
OLD_ONLINE = BASE / "online_blind_validation" / "T5_requests_tls_seed04"
EVAL_ROOT = OUT_ROOT / "audit_policy_eval"
ORACLE_PATH = BASE / "results" / "T5_real_repo_requests_tls_oracle.json"
MODEL = "gpt-5.3-codex"
TASK_ID = "T5_real_repo_requests_tls_online_audit_policy_eval"
ORACLE_SIZE = 304

SEEDS = ["seed04", "seed05", "seed06", "seed07", "seed08"]
CONDITIONS = ["homogeneous", "prompt_diverse", "source_partitioned", "independent_context"]

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

POLICIES = [
    "no_audit",
    "random_holdout",
    "singleton_audit",
    "boundary_focused_holdout",
    "source_partitioned_review",
    "always_holdout",
    "risk_triggered_audit",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical(file_path: str, line: int | str) -> str:
    return f"{file_path.replace('\\', '/')}:{int(line)}"


def parse_item(item: Any) -> str:
    if isinstance(item, str):
        path, line = item.rsplit(":", 1)
        return canonical(path, line)
    return canonical(item["file_path"], item["line"])


def key_to_item(key: str) -> dict[str, Any]:
    path, line = key.rsplit(":", 1)
    return {"file_path": path, "line": int(line)}


def condition_dir(seed: str, condition: str) -> Path:
    candidate = OUT_ROOT / seed / condition
    if (candidate / "merged_itemsets.json").exists():
        return candidate
    if seed == "seed04":
        return OLD_ONLINE / condition
    return candidate


def load_merged(seed: str, condition: str) -> dict[str, Any]:
    path = condition_dir(seed, condition) / "merged_itemsets.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_runs(seed: str, condition: str) -> list[dict[str, Any]]:
    return load_merged(seed, condition)["runs"]


def run_items(run: dict[str, Any]) -> set[str]:
    return {parse_item(item) for item in run.get("items", [])}


def discovery_sets(seed: str, condition: str) -> dict[str, Any]:
    runs = load_runs(seed, condition)
    sets = [run_items(run) for run in runs]
    counts = Counter(item for itemset in sets for item in itemset)
    union = set(counts)
    consensus = {item for item, count in counts.items() if count >= 2}
    singleton = {item for item, count in counts.items() if count == 1}
    confidences = [
        float(run.get("self_reported_confidence", run.get("confidence", 0.0)) or 0.0)
        for run in runs
    ]
    completions = [
        bool(run.get("self_reported_completion", True))
        for run in runs
    ]
    return {
        "runs": runs,
        "sets": sets,
        "union": union,
        "consensus": consensus,
        "singleton": singleton,
        "mean_confidence": statistics.mean(confidences) if confidences else 0.0,
        "all_complete": all(completions),
        "singleton_ratio": len(singleton) / len(union) if union else 0.0,
        "consensus_to_union": len(consensus) / len(union) if union else 1.0,
    }


def load_oracle() -> set[str]:
    raw = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
    return {canonical(item["file_path"], item["line"]) for item in raw["items"]}


def score(items: set[str], oracle: set[str]) -> dict[str, Any]:
    tp = items & oracle
    fp = items - oracle
    return {
        "found": len(items),
        "tp": len(tp),
        "fp": len(fp),
        "recall": len(tp) / len(oracle) if oracle else 0.0,
        "precision": len(tp) / len(items) if items else 1.0,
        "true_items": tp,
        "false_items": fp,
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


def add_cost(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_tokens": int(left.get("input_tokens") or 0) + int(right.get("input_tokens") or 0),
        "output_tokens": int(left.get("output_tokens") or 0) + int(right.get("output_tokens") or 0),
        "tool_calls": int(left.get("tool_calls") or 0) + int(right.get("tool_calls") or 0),
        "wall_clock_seconds": float(left.get("wall_clock_seconds") or 0.0) + float(right.get("wall_clock_seconds") or 0.0),
    }


def zero_cost() -> dict[str, Any]:
    return {"input_tokens": 0, "output_tokens": 0, "tool_calls": 0, "wall_clock_seconds": 0.0}


def discovery_cost(seed: str, condition: str) -> dict[str, Any]:
    return load_cost_dir(condition_dir(seed, condition) / "cost")


def line_snippet(rel_path: str, line: int, radius: int = 2) -> str:
    path = TASK_ROOT / rel_path
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    start = max(1, line - radius)
    end = min(len(lines), line + radius)
    rendered = [f"### {rel_path}:{line}"]
    for line_no in range(start, end + 1):
        rendered.append(f"{line_no:04d}: {lines[line_no - 1]}")
    return "\n".join(rendered)


def candidate_packet(candidates: list[str]) -> str:
    chunks: list[str] = []
    for idx, key in enumerate(candidates, start=1):
        path, line_text = key.rsplit(":", 1)
        chunks.append(f"Candidate {idx}: {key}\n{line_snippet(path, int(line_text))}")
    return "\n\n".join(chunks)


def stable_sample(items: set[str], seed: str, condition: str, fraction: float = 0.25, minimum: int = 20) -> list[str]:
    ranked = sorted(
        items,
        key=lambda item: hashlib.sha256(f"{seed}|{condition}|random_holdout|{item}".encode("utf-8")).hexdigest(),
    )
    take = min(len(ranked), max(minimum, round(len(ranked) * fraction)))
    return ranked[:take]


def verifier_prompt(run_id: str, task_md: str, candidates: list[str], policy: str) -> str:
    return f"""You are an online audit verifier for a line-level repository audit.

Allowed context: candidate line snippets from the Requests TLS task directory.
Forbidden context: oracle files, score summaries, experiment results, and any
line not shown in the candidate snippets.

Task instructions:

{task_md}

Audit policy: {policy}

Review the candidate list. Return only candidates that truly belong to the TLS
certificate verification and certificate handling audit. Do not add new lines.
If a candidate is a nearby but non-substantive line, omit it.

Return JSON only with this shape:

{{
  "run_id": "{run_id}",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [
    {{"file_path": "repo/src/requests/adapters.py", "line": 321}}
  ]
}}

Candidate snippets:

{candidate_packet(candidates)}
"""


def parse_audit_run(raw_text: str, run_id: str, allowed: set[str] | None = None) -> dict[str, Any]:
    parsed = parse_json_text(raw_text)
    parsed["run_id"] = run_id
    parsed["self_reported_completion"] = bool(parsed.get("self_reported_completion", True))
    parsed["self_reported_confidence"] = float(parsed.get("self_reported_confidence", 0.0) or 0.0)
    items = []
    for item in parsed.get("items", []):
        key = parse_item(item)
        if allowed is None or key in allowed:
            items.append(key_to_item(key))
    parsed["items"] = items
    return parsed


def call_verifier(
    *,
    seed: str,
    condition: str,
    policy: str,
    candidates: list[str],
    endpoint: str,
    api_key: str,
    dry_run: bool,
) -> tuple[set[str], dict[str, Any], Path]:
    run_id = f"T5_online_{seed}_{condition}_{policy}_G6_verifier"
    run_path = EVAL_ROOT / "runs" / seed / condition / f"{run_id}.json"
    raw_path = EVAL_ROOT / "raw" / seed / condition / f"{run_id}_raw_response.json"
    cost_path = EVAL_ROOT / "cost" / seed / condition / f"{run_id}_cost.json"
    if run_path.exists():
        raw = json.loads(run_path.read_text(encoding="utf-8"))
        return {parse_item(item) for item in raw.get("items", [])}, load_cost_dir(cost_path.parent), run_path
    if dry_run or not candidates:
        return set(), zero_cost(), run_path
    task_md = (TASK_ROOT / "TASK.md").read_text(encoding="utf-8")
    input_text = verifier_prompt(run_id, task_md, candidates, policy)
    started = now_iso()
    start = time.perf_counter()
    response = call_api(endpoint, MODEL, api_key, input_text)
    wall = time.perf_counter() - start
    ended = now_iso()
    run = parse_audit_run(extract_output_text(response), run_id, set(candidates))
    run_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    cost_path.parent.mkdir(parents=True, exist_ok=True)
    run_path.write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    raw_path.write_text(json.dumps(response, indent=2, ensure_ascii=False), encoding="utf-8")
    usage = response.get("usage", {})
    cost = {
        "run_id": run_id,
        "started_at": started,
        "ended_at": ended,
        "model_name": MODEL,
        "policy": policy,
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "tool_calls": 0,
        "wall_clock_seconds": wall,
        "candidate_count": len(candidates),
    }
    cost_path.write_text(json.dumps(cost, indent=2, ensure_ascii=False), encoding="utf-8")
    return {parse_item(item) for item in run.get("items", [])}, load_cost_dir(cost_path.parent), run_path


def call_boundary_holdout(seed: str, endpoint: str, api_key: str, dry_run: bool) -> tuple[set[str], dict[str, Any], Path]:
    run_id = f"T5_online_{seed}_boundary_focused_holdout_G6_agent01"
    run_path = EVAL_ROOT / "boundary_runs" / seed / f"{run_id}.json"
    cost_path = EVAL_ROOT / "boundary_cost" / seed / f"{run_id}_cost.json"
    raw_path = EVAL_ROOT / "boundary_raw" / seed / f"{run_id}_raw_response.json"
    if run_path.exists():
        raw = json.loads(run_path.read_text(encoding="utf-8"))
        return {parse_item(item) for item in raw.get("items", [])}, load_cost_dir(cost_path.parent), run_path
    if dry_run:
        return set(), zero_cost(), run_path
    prompt_addon = (
        f"Fixed audit seed label: {seed}. This is a boundary-focused holdout audit. "
        "Prioritize commonly missed TLS certificate lines in tests, fixtures, "
        "documentation, environment-variable CA bundle behavior, client certificates, "
        "and SSL error boundaries. Return exact lines only."
    )
    cmd = [
        sys.executable,
        str(BASE / "tools" / "run_autodl_blind_agent.py"),
        "--task-root",
        str(TASK_ROOT),
        "--task-root-label",
        "experiments/false_convergence_pilot/T5_real_repo_requests_tls/",
        "--run-id",
        run_id,
        "--files",
        *COMMON_FILES,
        "--out",
        str(run_path),
        "--raw-out",
        str(raw_path),
        "--cost-out",
        str(cost_path),
        "--search-budget",
        "180",
        "--max-lines-per-file",
        "1200",
        "--prompt-variant",
        "boundary_focused_holdout",
        "--prompt-addon",
        prompt_addon,
        "--model",
        MODEL,
        "--endpoint",
        endpoint,
    ]
    subprocess.run(cmd, cwd=ROOT.parent, check=True)
    raw = json.loads(run_path.read_text(encoding="utf-8"))
    return {parse_item(item) for item in raw.get("items", [])}, load_cost_dir(cost_path.parent), run_path


def score_summary_path(seed: str, condition: str) -> Path:
    return condition_dir(seed, condition) / "score_summary.json"


def preaudit_stats(seed: str, condition: str) -> dict[str, Any]:
    score_path = score_summary_path(seed, condition)
    if score_path.exists():
        raw = json.loads(score_path.read_text(encoding="utf-8"))
        if raw.get("seed_summaries"):
            summary = raw["seed_summaries"][0]
            return {
                "mean_pairwise_jaccard": summary.get("mean_pairwise_jaccard", 0.0),
                "mean_confidence": summary.get("mean_confidence", 0.0),
                "singleton_ratio": summary.get("singleton_ratio", 0.0),
            }
    data = discovery_sets(seed, condition)
    return {
        "mean_pairwise_jaccard": None,
        "mean_confidence": data["mean_confidence"],
        "singleton_ratio": data["singleton_ratio"],
    }


def risk_trigger(data: dict[str, Any], stats: dict[str, Any]) -> tuple[bool, str]:
    reasons: list[str] = []
    if data["all_complete"] and stats["mean_confidence"] >= 0.75:
        reasons.append("self_reported_completion_confidence")
    if data["singleton_ratio"] >= 0.12:
        reasons.append("singleton_ratio_ge_0.12")
    if data["consensus_to_union"] <= 0.88:
        reasons.append("consensus_union_gap_ge_12pct")
    jaccard = stats.get("mean_pairwise_jaccard")
    if jaccard is not None and jaccard >= 0.70 and data["consensus_to_union"] <= 0.92:
        reasons.append("high_overlap_but_nontrivial_union_gap")
    if len(data["consensus"]) < 180:
        reasons.append("small_consensus_cardinality")
    return bool(reasons), "+".join(reasons) if reasons else "no_trigger"


def evidence_union(seed: str, condition: str) -> set[str]:
    try:
        return discovery_sets(seed, condition)["union"]
    except FileNotFoundError:
        return set()


def evaluate(args: argparse.Namespace) -> list[dict[str, Any]]:
    api_key = os.environ.get(args.api_key_env, "")
    if args.run_online_audits and not api_key:
        raise SystemExit(f"Missing API key env var: {args.api_key_env}")
    oracle = load_oracle()
    rows: list[dict[str, Any]] = []
    boundary_cache: dict[str, tuple[set[str], dict[str, Any], Path]] = {}
    for seed in args.seeds:
        if args.run_online_audits or (EVAL_ROOT / "boundary_runs" / seed).exists():
            boundary_cache[seed] = call_boundary_holdout(seed, args.endpoint, api_key, not args.run_online_audits)
        for condition in args.conditions:
            data = discovery_sets(seed, condition)
            stats = preaudit_stats(seed, condition)
            pre_items = data["consensus"]
            pre_score = score(pre_items, oracle)
            singleton_candidates = sorted(data["singleton"])
            random_candidates = stable_sample(data["singleton"], seed, condition)
            singleton_items, singleton_cost, singleton_path = call_verifier(
                seed=seed,
                condition=condition,
                policy="singleton_audit",
                candidates=singleton_candidates,
                endpoint=args.endpoint,
                api_key=api_key,
                dry_run=not args.run_online_audits,
            )
            random_items, random_cost, random_path = call_verifier(
                seed=seed,
                condition=condition,
                policy="random_holdout",
                candidates=random_candidates,
                endpoint=args.endpoint,
                api_key=api_key,
                dry_run=not args.run_online_audits,
            )
            boundary_items, boundary_cost, boundary_path = boundary_cache.get(seed, (set(), zero_cost(), Path("")))
            source_items = evidence_union(seed, "source_partitioned")
            independent_items = evidence_union(seed, "independent_context")
            source_cost = zero_cost() if condition == "source_partitioned" else discovery_cost(seed, "source_partitioned")
            independent_cost = zero_cost() if condition == "independent_context" else discovery_cost(seed, "independent_context")
            triggered, trigger_reason = risk_trigger(data, stats)
            policy_specs = {
                "no_audit": (pre_items, zero_cost(), "none", 0, ""),
                "random_holdout": (pre_items | random_items, random_cost, "online_candidate_verifier", len(random_candidates), str(random_path)),
                "singleton_audit": (pre_items | singleton_items, singleton_cost, "online_singleton_verifier", len(singleton_candidates), str(singleton_path)),
                "boundary_focused_holdout": (pre_items | boundary_items, boundary_cost, "online_boundary_holdout", len(boundary_items), str(boundary_path)),
                "source_partitioned_review": (pre_items | source_items, source_cost, "online_source_partitioned_review", len(source_items), str(condition_dir(seed, "source_partitioned"))),
                "always_holdout": (
                    pre_items | source_items | independent_items,
                    add_cost(source_cost, independent_cost),
                    "online_source_partitioned_plus_independent_review",
                    len(source_items | independent_items),
                    f"{condition_dir(seed, 'source_partitioned')};{condition_dir(seed, 'independent_context')}",
                ),
                "risk_triggered_audit": (
                    pre_items | singleton_items | boundary_items if triggered else pre_items,
                    add_cost(singleton_cost, boundary_cost) if triggered else zero_cost(),
                    "online_singleton_plus_boundary_if_triggered" if triggered else "not_triggered",
                    len(singleton_candidates) + len(boundary_items) if triggered else 0,
                    f"{singleton_path};{boundary_path}" if triggered else "",
                ),
            }
            for policy in POLICIES:
                post_items, audit_cost, evidence_kind, queue_size, evidence_path = policy_specs[policy]
                post_score = score(post_items, oracle)
                recovered = (post_items - pre_items) & oracle
                introduced = (post_items - pre_items) - oracle
                tokens = int(audit_cost["input_tokens"]) + int(audit_cost["output_tokens"])
                rows.append({
                    "seed": seed,
                    "condition": condition,
                    "policy": policy,
                    "pre_recall": pre_score["recall"],
                    "post_recall": post_score["recall"],
                    "post_precision": post_score["precision"],
                    "pre_tp": pre_score["tp"],
                    "post_tp": post_score["tp"],
                    "recovered_tp": len(recovered),
                    "introduced_fp": len(introduced),
                    "audit_input_tokens": int(audit_cost["input_tokens"]),
                    "audit_output_tokens": int(audit_cost["output_tokens"]),
                    "audit_tokens": tokens,
                    "audit_tool_calls": int(audit_cost["tool_calls"]),
                    "audit_wall_clock_seconds": float(audit_cost["wall_clock_seconds"]),
                    "audit_queue_size": queue_size,
                    "cost_per_recovered_tp": tokens / len(recovered) if recovered else None,
                    "risk_triggered": triggered if policy == "risk_triggered_audit" else "",
                    "risk_trigger_reason": trigger_reason if policy == "risk_triggered_audit" else "",
                    "evidence_kind": evidence_kind,
                    "evidence_path": evidence_path,
                })
    return rows


def write_outputs(rows: list[dict[str, Any]]) -> None:
    EVAL_ROOT.mkdir(parents=True, exist_ok=True)
    csv_path = EVAL_ROOT / "ONLINE_AUDIT_POLICY_RESULTS.csv"
    json_path = EVAL_ROOT / "ONLINE_AUDIT_POLICY_RESULTS.json"
    md_path = EVAL_ROOT / "ONLINE_AUDIT_POLICY_RESULTS.md"
    fieldnames = list(rows[0].keys()) if rows else []
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["policy"], []).append(row)
    lines = [
        "# Online Audit-Policy Results",
        "",
        "Policy triggers and queues are computed from frozen blind-discovery logs.",
        "Oracle scoring is applied only after online audit evidence is written.",
        "",
        "## Policy Means",
        "",
        "| policy | n | pre R | post R | precision | recovered TP | introduced FP | audit tokens | wall-clock s | cost/TP |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for policy in POLICIES:
        subset = grouped.get(policy, [])
        if not subset:
            continue
        cost_values = [row["cost_per_recovered_tp"] for row in subset if row["cost_per_recovered_tp"] is not None]
        lines.append(
            "| {policy} | {n} | {pre:.3f} | {post:.3f} | {prec:.3f} | {rtp:.1f} | {ifp:.1f} | {tok:.0f} | {wall:.1f} | {ctp} |".format(
                policy=policy.replace("_", "-"),
                n=len(subset),
                pre=statistics.mean(row["pre_recall"] for row in subset),
                post=statistics.mean(row["post_recall"] for row in subset),
                prec=statistics.mean(row["post_precision"] for row in subset),
                rtp=statistics.mean(row["recovered_tp"] for row in subset),
                ifp=statistics.mean(row["introduced_fp"] for row in subset),
                tok=statistics.mean(row["audit_tokens"] for row in subset),
                wall=statistics.mean(row["audit_wall_clock_seconds"] for row in subset),
                ctp=f"{statistics.mean(cost_values):.0f}" if cost_values else "",
            )
        )
    lines.extend([
        "",
        "## Per-Seed/Condition Rows",
        "",
        "| seed | condition | policy | pre R | post R | recovered TP | introduced FP | tokens | trigger |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ])
    for row in rows:
        lines.append(
            "| {seed} | {condition} | {policy} | {pre:.3f} | {post:.3f} | {rtp} | {ifp} | {tok} | {trigger} |".format(
                seed=row["seed"],
                condition=row["condition"].replace("_", "-"),
                policy=row["policy"].replace("_", "-"),
                pre=row["pre_recall"],
                post=row["post_recall"],
                rtp=row["recovered_tp"],
                ifp=row["introduced_fp"],
                tok=row["audit_tokens"],
                trigger=row["risk_trigger_reason"],
            )
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest = {
        "suite": "online_audit_policy_eval_requests_tls",
        "status": "completed",
        "created_or_updated_at": now_iso(),
        "model": MODEL,
        "task_id": TASK_ID,
        "oracle_used_only_for_final_scoring": True,
        "outputs": {
            "csv": str(csv_path),
            "json": str(json_path),
            "markdown": str(md_path),
        },
    }
    (EVAL_ROOT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(md_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", default=SEEDS)
    parser.add_argument("--conditions", nargs="+", default=CONDITIONS)
    parser.add_argument("--run-online-audits", action="store_true")
    parser.add_argument("--api-key-env", default="AUTODL_ART_API_KEY")
    parser.add_argument("--endpoint", default="https://www.autodl.art/api/v1/responses")
    args = parser.parse_args()
    rows = evaluate(args)
    write_outputs(rows)


if __name__ == "__main__":
    main()
