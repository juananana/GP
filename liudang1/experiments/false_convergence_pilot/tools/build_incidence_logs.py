#!/usr/bin/env python3
"""Build item-level incidence logs from existing AgentCompletion itemsets."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from score_itemsets import load_oracle, normalize_run


@dataclass(frozen=True)
class IncidenceCase:
    case_id: str
    task_family: str
    oracle_path: str
    runs_path: str
    experimental_status: str = "blind_agent_result"
    reportable: bool = True


CASES = [
    IncidenceCase(
        case_id="T1_hard_expanded",
        task_family="synthetic_code_audit",
        oracle_path="results/T1_hard_repo_oracle.json",
        runs_path="results/T1_hard_expanded_itemsets.json",
    ),
    IncidenceCase(
        case_id="T1_hard_seed03_completed",
        task_family="synthetic_code_audit",
        oracle_path="results/T1_hard_repo_oracle.json",
        runs_path="results/T1_hard_seed03_completed_itemsets.json",
    ),
    IncidenceCase(
        case_id="T2_policy_docs_seed01",
        task_family="synthetic_policy_docs",
        oracle_path="results/T2_policy_docs_oracle.json",
        runs_path="results/T2_policy_docs_seed01_itemsets.json",
    ),
    IncidenceCase(
        case_id="T2_policy_docs_seed02",
        task_family="synthetic_policy_docs",
        oracle_path="results/T2_policy_docs_oracle.json",
        runs_path="results/T2_policy_docs_seed02_itemsets.json",
    ),
    IncidenceCase(
        case_id="T2_policy_docs_seed03",
        task_family="synthetic_policy_docs",
        oracle_path="results/T2_policy_docs_oracle.json",
        runs_path="results/T2_policy_docs_seed03_itemsets.json",
    ),
    IncidenceCase(
        case_id="T2_partitioned_v3_seed01",
        task_family="naturalized_policy_docs",
        oracle_path="results/T2_partitioned_v3_oracle.json",
        runs_path="results/T2_partitioned_v3_seed01_itemsets.json",
    ),
    IncidenceCase(
        case_id="T3_partitioned_seed01",
        task_family="partitioned_policy_docs",
        oracle_path="results/T3_partitioned_policy_docs_oracle.json",
        runs_path="results/T3_partitioned_seed01_itemsets.json",
    ),
    IncidenceCase(
        case_id="T4_real_repo_click_seed01_smoke",
        task_family="real_repo_code_audit",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed01_smoke_itemsets.json",
        experimental_status="oracle_generated_smoke_test",
        reportable=False,
    ),
    IncidenceCase(
        case_id="T4_real_repo_click_seed01_blind",
        task_family="real_repo_code_audit",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed01_blind_itemsets.json",
        experimental_status="blind_agent_result",
        reportable=True,
    ),
    IncidenceCase(
        case_id="T4_real_repo_click_seed02_blind",
        task_family="real_repo_code_audit",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed02_blind_itemsets.json",
        experimental_status="blind_agent_result",
        reportable=True,
    ),
    IncidenceCase(
        case_id="T4_real_repo_click_seed03_blind",
        task_family="real_repo_code_audit",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed03_blind_itemsets.json",
        experimental_status="blind_agent_result",
        reportable=True,
    ),
    IncidenceCase(
        case_id="T5_real_repo_requests_tls_seed01_smoke",
        task_family="real_repo_tls_audit",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed01_smoke_itemsets.json",
        experimental_status="oracle_generated_smoke_test",
        reportable=False,
    ),
    IncidenceCase(
        case_id="T5_real_repo_requests_tls_seed01_blind",
        task_family="real_repo_tls_audit",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed01_blind_itemsets.json",
        experimental_status="blind_agent_result",
        reportable=True,
    ),
    IncidenceCase(
        case_id="T5_real_repo_requests_tls_seed02_blind",
        task_family="real_repo_tls_audit",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed02_blind_itemsets.json",
        experimental_status="blind_agent_result",
        reportable=True,
    ),
    IncidenceCase(
        case_id="T5_real_repo_requests_tls_seed03_blind",
        task_family="real_repo_tls_audit",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed03_blind_itemsets.json",
        experimental_status="blind_agent_result",
        reportable=True,
    ),
]


FIELDNAMES = [
    "task_id",
    "task_family",
    "case_id",
    "seed",
    "group_id",
    "run_id",
    "agent_id",
    "round_id",
    "prompt_variant",
    "model_name",
    "item_id",
    "canonical_item",
    "source_id",
    "source_bin",
    "query_path",
    "first_seen_round",
    "support_count",
    "is_singleton",
    "self_reported_completion",
    "self_reported_confidence",
    "aggregation_status",
    "audit_status",
    "oracle_label",
    "oracle_bucket",
    "reportable",
    "experimental_status",
]


def agent_id(run_id: str) -> str:
    match = re.search(r"(agent\d+|holdout|G1)", run_id, flags=re.IGNORECASE)
    return match.group(1) if match else run_id


def source_id_for(item: str) -> str:
    if "::" in item:
        return item.split("::", 1)[0]
    if ":" in item:
        return item.rsplit(":", 1)[0]
    return "unknown"


def item_id_for(item: str) -> str:
    if "::" in item:
        return item.split("::", 1)[1]
    return item


def source_bin_for(item: str) -> str:
    source_id = source_id_for(item)
    if source_id.startswith("CASE-"):
        return "case_file"
    parts = source_id.replace("\\", "/").split("/")
    if len(parts) >= 3 and parts[0] == "repo":
        return "/".join(parts[:3])
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return source_id


def aggregation_status(group_id: str, support_count: int) -> str:
    if group_id == "G6":
        return "holdout"
    if group_id == "G1":
        return "single_agent"
    if group_id == "G3":
        if support_count >= 2:
            return "consensus"
        if support_count == 1:
            return "singleton"
    return "unknown"


def audit_status(group_id: str, item: str, g3_union: set[str], holdout_items: set[str], support_count: int) -> str:
    if group_id == "G6":
        return "holdout_new" if item not in g3_union else "holdout_confirmed"
    if group_id == "G3" and support_count == 1:
        return "holdout_confirmed" if item in holdout_items else "pending"
    if group_id == "G1":
        return "not_applicable"
    return "not_required"


def load_runs(path: Path) -> tuple[str, list[dict[str, Any]]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw.get("task_id", "unknown_task"), [normalize_run(run) for run in raw["runs"]]


def build_rows(base: Path, case: IncidenceCase) -> list[dict[str, Any]]:
    oracle, buckets = load_oracle(base / case.oracle_path)
    task_id, runs = load_runs(base / case.runs_path)
    rows: list[dict[str, Any]] = []

    g3_by_seed: dict[str, list[dict[str, Any]]] = {}
    g6_by_seed: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        if run["group"] == "G3":
            g3_by_seed.setdefault(run["seed"], []).append(run)
        if run["group"] == "G6":
            g6_by_seed.setdefault(run["seed"], []).append(run)

    support_by_seed = {
        seed: Counter(item for run in seed_runs for item in run["items"])
        for seed, seed_runs in g3_by_seed.items()
    }
    g3_union_by_seed = {
        seed: set(counter)
        for seed, counter in support_by_seed.items()
    }
    holdout_by_seed = {
        seed: set().union(*(run["items"] for run in seed_runs))
        for seed, seed_runs in g6_by_seed.items()
    }

    for run in runs:
        seed = run["seed"]
        support_counter = support_by_seed.get(seed, Counter())
        g3_union = g3_union_by_seed.get(seed, set())
        holdout_items = holdout_by_seed.get(seed, set())
        for item in sorted(run["items"]):
            support_count = support_counter.get(item, 1 if run["group"] == "G1" else 0)
            row = {
                "task_id": task_id,
                "task_family": case.task_family,
                "case_id": case.case_id,
                "seed": seed,
                "group_id": run["group"],
                "run_id": run["run_id"],
                "agent_id": agent_id(run["run_id"]),
                "round_id": None,
                "prompt_variant": None,
                "model_name": None,
                "item_id": item_id_for(item),
                "canonical_item": item,
                "source_id": source_id_for(item),
                "source_bin": source_bin_for(item),
                "query_path": None,
                "first_seen_round": None,
                "support_count": support_count,
                "is_singleton": run["group"] == "G3" and support_count == 1,
                "self_reported_completion": run["completion"],
                "self_reported_confidence": run["confidence"],
                "aggregation_status": aggregation_status(run["group"], support_count),
                "audit_status": audit_status(run["group"], item, g3_union, holdout_items, support_count),
                "oracle_label": item in oracle,
                "oracle_bucket": buckets.get(item),
                "reportable": case.reportable,
                "experimental_status": case.experimental_status,
            }
            rows.append(row)
    return rows


def write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, Any]], path: Path) -> None:
    by_case: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_case.setdefault(row["case_id"], []).append(row)

    lines = [
        "# Incidence Log Summary",
        "",
        "This file summarizes item-level incidence logs. Oracle labels are included only for offline scoring; blind agents must not access these logs.",
        "",
        "| case | task_family | reportable | status | rows | unique_items | singleton_rows | holdout_new_rows | oracle_positive_rows |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for case_id, case_rows in sorted(by_case.items()):
        unique_items = {row["canonical_item"] for row in case_rows}
        singleton_rows = sum(1 for row in case_rows if row["aggregation_status"] == "singleton")
        holdout_new = sum(1 for row in case_rows if row["audit_status"] == "holdout_new")
        positives = sum(1 for row in case_rows if row["oracle_label"])
        first = case_rows[0]
        lines.append(
            f"| {case_id} | {first['task_family']} | {str(first['reportable']).lower()} | "
            f"{first['experimental_status']} | {len(case_rows)} | {len(unique_items)} | "
            f"{singleton_rows} | {holdout_new} | {positives} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path("experiments/false_convergence_pilot"))
    parser.add_argument(
        "--out-jsonl",
        type=Path,
        default=Path("experiments/false_convergence_pilot/incidence_logs/line_a_incidence_log.jsonl"),
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("experiments/false_convergence_pilot/incidence_logs/line_a_incidence_log.csv"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("experiments/false_convergence_pilot/reports/protocol/INCIDENCE_LOG_SUMMARY.md"),
    )
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    for case in CASES:
        case_path = args.base / case.runs_path
        if case_path.exists():
            rows.extend(build_rows(args.base, case))

    rows.sort(key=lambda row: (
        row["case_id"],
        row["seed"],
        row["group_id"],
        row["run_id"],
        row["canonical_item"],
    ))
    write_jsonl(rows, args.out_jsonl)
    write_csv(rows, args.out_csv)
    write_markdown(rows, args.out_md)


if __name__ == "__main__":
    main()
