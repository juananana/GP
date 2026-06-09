#!/usr/bin/env python3
"""Evaluate an evidence-preserving completion protocol on existing Line A runs."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any

from score_itemsets import (
    CONFIDENCE_THRESHOLD,
    THETA,
    bucket_recall,
    jaccard,
    load_oracle,
    normalize_run,
    score_set,
)


COMMON_BLINDSPOT_JACCARD = 0.95


@dataclass(frozen=True)
class CaseSpec:
    case_id: str
    mechanism: str
    oracle_path: str
    runs_path: str
    seed: str
    standard_summarizer_path: str | None = None
    union_summarizer_path: str | None = None
    task_has_boundary_risk: bool = True


CASES = [
    CaseSpec(
        case_id="T1_hard_seed01",
        mechanism="aggregation_loss",
        oracle_path="results/T1_hard_repo_oracle.json",
        runs_path="results/T1_hard_expanded_itemsets.json",
        seed="seed01",
        standard_summarizer_path="summarizer_outputs/T1_hard_seed01_sum_standard_itemsets.json",
        union_summarizer_path="summarizer_outputs/T1_hard_seed01_sum_union_preserving_blind_itemsets.json",
    ),
    CaseSpec(
        case_id="T1_hard_seed02",
        mechanism="precision_cost_control",
        oracle_path="results/T1_hard_repo_oracle.json",
        runs_path="results/T1_hard_expanded_itemsets.json",
        seed="seed02",
        standard_summarizer_path="summarizer_outputs/T1_hard_seed02_sum_standard_blind_itemsets.json",
        union_summarizer_path="summarizer_outputs/T1_hard_seed02_sum_union_preserving_blind_itemsets.json",
    ),
    CaseSpec(
        case_id="T1_hard_seed03",
        mechanism="precision_cost_control",
        oracle_path="results/T1_hard_repo_oracle.json",
        runs_path="results/T1_hard_seed03_completed_itemsets.json",
        seed="seed03",
        standard_summarizer_path="summarizer_outputs/T1_hard_seed03_sum_standard_blind_itemsets.json",
        union_summarizer_path="summarizer_outputs/T1_hard_seed03_sum_union_preserving_blind_itemsets.json",
    ),
    CaseSpec(
        case_id="T2_policy_docs_seed01",
        mechanism="aggregation_loss",
        oracle_path="results/T2_policy_docs_oracle.json",
        runs_path="results/T2_policy_docs_seed01_itemsets.json",
        seed="seed01",
        standard_summarizer_path="summarizer_outputs/T2_policy_docs_seed01_sum_standard_itemsets.json",
        union_summarizer_path="summarizer_outputs/T2_policy_docs_seed01_sum_union_preserving_blind_itemsets.json",
    ),
    CaseSpec(
        case_id="T2_policy_docs_seed02",
        mechanism="common_blind_spot",
        oracle_path="results/T2_policy_docs_oracle.json",
        runs_path="results/T2_policy_docs_seed02_itemsets.json",
        seed="seed02",
    ),
    CaseSpec(
        case_id="T2_policy_docs_seed03",
        mechanism="common_blind_spot",
        oracle_path="results/T2_policy_docs_oracle.json",
        runs_path="results/T2_policy_docs_seed03_itemsets.json",
        seed="seed03",
    ),
    CaseSpec(
        case_id="T4_real_repo_click_seed01_blind",
        mechanism="real_repo_precision_recall_boundary",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed01_blind_itemsets.json",
        seed="seed01",
        standard_summarizer_path="summarizer_outputs/T4_real_repo_click_seed01_sum_standard_autodl_itemsets.json",
        union_summarizer_path="summarizer_outputs/T4_real_repo_click_seed01_sum_union_preserving_autodl_itemsets.json",
    ),
    CaseSpec(
        case_id="T4_real_repo_click_seed02_blind",
        mechanism="real_repo_precision_recall_boundary",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed02_blind_itemsets.json",
        seed="seed02",
        standard_summarizer_path="summarizer_outputs/T4_real_repo_click_seed02_sum_standard_autodl_itemsets.json",
        union_summarizer_path="summarizer_outputs/T4_real_repo_click_seed02_sum_union_preserving_autodl_itemsets.json",
    ),
    CaseSpec(
        case_id="T4_real_repo_click_seed03_blind",
        mechanism="real_repo_precision_recall_boundary",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed03_blind_itemsets.json",
        seed="seed03",
        standard_summarizer_path="summarizer_outputs/T4_real_repo_click_seed03_sum_standard_autodl_itemsets.json",
        union_summarizer_path="summarizer_outputs/T4_real_repo_click_seed03_sum_union_preserving_autodl_itemsets.json",
    ),
    CaseSpec(
        case_id="T5_real_repo_requests_tls_seed01_blind",
        mechanism="second_real_repo_tls_audit",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed01_blind_itemsets.json",
        seed="seed01",
        standard_summarizer_path="summarizer_outputs/T5_real_repo_requests_tls_seed01_sum_standard_autodl_itemsets.json",
        union_summarizer_path="summarizer_outputs/T5_real_repo_requests_tls_seed01_sum_union_preserving_autodl_itemsets.json",
    ),
    CaseSpec(
        case_id="T5_real_repo_requests_tls_seed02_blind",
        mechanism="second_real_repo_tls_audit",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed02_blind_itemsets.json",
        seed="seed02",
        standard_summarizer_path="summarizer_outputs/T5_real_repo_requests_tls_seed02_sum_standard_autodl_itemsets.json",
        union_summarizer_path="summarizer_outputs/T5_real_repo_requests_tls_seed02_sum_union_preserving_autodl_itemsets.json",
    ),
    CaseSpec(
        case_id="T5_real_repo_requests_tls_seed03_blind",
        mechanism="second_real_repo_tls_audit",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed03_blind_itemsets.json",
        seed="seed03",
        standard_summarizer_path="summarizer_outputs/T5_real_repo_requests_tls_seed03_sum_standard_autodl_itemsets.json",
        union_summarizer_path="summarizer_outputs/T5_real_repo_requests_tls_seed03_sum_union_preserving_autodl_itemsets.json",
    ),
]


METHOD_ORDER = [
    "majority_consensus",
    "standard_summarizer_blind",
    "raw_union",
    "union_preserving_blind",
    "holdout_scout",
    "evidence_preserving_protocol",
]


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def load_runs(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [normalize_run(run) for run in raw["runs"]]


def load_single_run_items(path: Path) -> tuple[set[str], float | None, bool] | None:
    if not path.exists():
        return None
    runs = load_runs(path)
    if not runs:
        return None
    run = runs[0]
    return set(run["items"]), run["confidence"], bool(run["completion"])


def score_row(
    *,
    case: CaseSpec,
    method: str,
    items: set[str],
    oracle: set[str],
    buckets: dict[str, str],
    completion: bool,
    status: str,
    notes: str = "",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metrics = score_set(items, oracle)
    row: dict[str, Any] = {
        "case_id": case.case_id,
        "mechanism": case.mechanism,
        "method": method,
        "available": True,
        "status": status,
        "found": metrics["found"],
        "true_positive": metrics["true_positive"],
        "false_positive": metrics["false_positive"],
        "recall": metrics["recall"],
        "precision": metrics["precision"],
        "completion": completion,
        "false_stop": completion and metrics["recall"] < THETA,
        "bucket_recall": bucket_recall(items, oracle, buckets),
        "notes": notes,
    }
    if extra:
        row.update(extra)
    return row


def unavailable_row(case: CaseSpec, method: str, reason: str) -> dict[str, Any]:
    return {
        "case_id": case.case_id,
        "mechanism": case.mechanism,
        "method": method,
        "available": False,
        "status": "not_run",
        "found": None,
        "true_positive": None,
        "false_positive": None,
        "recall": None,
        "precision": None,
        "completion": False,
        "false_stop": False,
        "bucket_recall": None,
        "notes": reason,
    }


def protocol_items(
    *,
    consensus_items: set[str],
    union_items: set[str],
    singleton_items: set[str],
    holdout_items: set[str],
    mean_confidence: float | None,
    mean_jaccard: float | None,
    task_has_boundary_risk: bool,
) -> dict[str, Any]:
    high_confidence = (
        mean_confidence is not None and mean_confidence >= CONFIDENCE_THRESHOLD
    )
    high_agreement = (
        mean_jaccard is not None and mean_jaccard >= COMMON_BLINDSPOT_JACCARD
    )
    risk_flags: list[str] = []
    if singleton_items:
        risk_flags.append("singleton_evidence_requires_audit")
    if task_has_boundary_risk and high_confidence and high_agreement:
        risk_flags.append("high_agreement_boundary_blindspot_risk")

    holdout_triggered = bool(risk_flags)
    final_items = set(consensus_items)
    verified_singletons: set[str] = set()
    holdout_new_items: set[str] = set()

    if holdout_items and holdout_triggered:
        verified_singletons = singleton_items & holdout_items
        final_items |= verified_singletons
        if "high_agreement_boundary_blindspot_risk" in risk_flags:
            holdout_new_items = holdout_items - union_items
            final_items |= holdout_new_items

    if holdout_triggered and holdout_items:
        status = "verified_after_holdout"
        completion = True
    elif holdout_triggered:
        status = "requires_audit"
        completion = False
    else:
        status = "complete_no_audit_trigger"
        completion = True

    return {
        "items": final_items,
        "status": status,
        "completion": completion,
        "risk_flags": risk_flags,
        "holdout_triggered": holdout_triggered,
        "audit_queue_size": len(singleton_items),
        "verified_singletons": sorted(verified_singletons),
        "unverified_singletons": sorted(singleton_items - verified_singletons),
        "holdout_new_items": sorted(holdout_new_items),
    }


def evaluate_case(base: Path, case: CaseSpec) -> dict[str, Any]:
    oracle, buckets = load_oracle(base / case.oracle_path)
    runs = load_runs(base / case.runs_path)
    g3_runs = [
        run for run in runs
        if run["seed"] == case.seed and run["group"] == "G3"
    ]
    g6_runs = [
        run for run in runs
        if run["seed"] == case.seed and run["group"] == "G6"
    ]
    if len(g3_runs) != 3:
        raise ValueError(f"{case.case_id} expected 3 G3 runs, found {len(g3_runs)}")

    item_counts = Counter(item for run in g3_runs for item in run["items"])
    consensus_items = {item for item, count in item_counts.items() if count >= 2}
    union_items = set(item_counts)
    singleton_items = {item for item, count in item_counts.items() if count == 1}
    holdout_items = set().union(*(run["items"] for run in g6_runs)) if g6_runs else set()
    pairwise = [
        jaccard(left["items"], right["items"])
        for left, right in combinations(g3_runs, 2)
    ]
    mean_confidence = mean([
        run["confidence"] for run in g3_runs if run["confidence"] is not None
    ])
    mean_jaccard = mean(pairwise)
    completion_from_confidence = (
        mean_confidence is not None and mean_confidence >= CONFIDENCE_THRESHOLD
    )

    rows: list[dict[str, Any]] = []
    rows.append(score_row(
        case=case,
        method="majority_consensus",
        items=consensus_items,
        oracle=oracle,
        buckets=buckets,
        completion=completion_from_confidence,
        status="complete_by_consensus",
        notes="Items reported by at least two G3 agents.",
    ))

    if case.standard_summarizer_path:
        loaded = load_single_run_items(base / case.standard_summarizer_path)
        if loaded:
            items, confidence, completion = loaded
            rows.append(score_row(
                case=case,
                method="standard_summarizer_blind",
                items=items,
                oracle=oracle,
                buckets=buckets,
                completion=completion,
                status="blind_llm_summary",
                notes=f"confidence={fmt(confidence)}",
            ))
        else:
            rows.append(unavailable_row(case, "standard_summarizer_blind", "file missing"))
    else:
        rows.append(unavailable_row(case, "standard_summarizer_blind", "not run for this seed"))

    rows.append(score_row(
        case=case,
        method="raw_union",
        items=union_items,
        oracle=oracle,
        buckets=buckets,
        completion=completion_from_confidence,
        status="complete_by_union",
        notes="All unique G3-reported items.",
    ))

    if case.union_summarizer_path:
        loaded = load_single_run_items(base / case.union_summarizer_path)
        if loaded:
            items, confidence, completion = loaded
            rows.append(score_row(
                case=case,
                method="union_preserving_blind",
                items=items,
                oracle=oracle,
                buckets=buckets,
                completion=completion,
                status="blind_llm_union_summary",
                notes=f"confidence={fmt(confidence)}",
            ))
        else:
            rows.append(unavailable_row(case, "union_preserving_blind", "file missing"))
    else:
        rows.append(unavailable_row(case, "union_preserving_blind", "not run for this seed"))

    if holdout_items:
        holdout_completion = any(run["completion"] for run in g6_runs)
        rows.append(score_row(
            case=case,
            method="holdout_scout",
            items=holdout_items,
            oracle=oracle,
            buckets=buckets,
            completion=holdout_completion,
            status="independent_audit",
            notes="Independent holdout scout output.",
        ))
    else:
        rows.append(unavailable_row(case, "holdout_scout", "not run for this seed"))

    protocol = protocol_items(
        consensus_items=consensus_items,
        union_items=union_items,
        singleton_items=singleton_items,
        holdout_items=holdout_items,
        mean_confidence=mean_confidence,
        mean_jaccard=mean_jaccard,
        task_has_boundary_risk=case.task_has_boundary_risk,
    )
    rows.append(score_row(
        case=case,
        method="evidence_preserving_protocol",
        items=protocol["items"],
        oracle=oracle,
        buckets=buckets,
        completion=protocol["completion"],
        status=protocol["status"],
        notes="Consensus final plus audited singleton/common-blindspot recovery.",
        extra={
            "risk_flags": protocol["risk_flags"],
            "holdout_triggered": protocol["holdout_triggered"],
            "audit_queue_size": protocol["audit_queue_size"],
            "verified_singletons": protocol["verified_singletons"],
            "unverified_singletons": protocol["unverified_singletons"],
            "holdout_new_items": protocol["holdout_new_items"],
        },
    ))

    return {
        "case_id": case.case_id,
        "mechanism": case.mechanism,
        "seed": case.seed,
        "oracle_size": len(oracle),
        "g3_run_ids": [run["run_id"] for run in g3_runs],
        "holdout_run_ids": [run["run_id"] for run in g6_runs],
        "mean_confidence": mean_confidence,
        "pairwise_jaccard": pairwise,
        "mean_pairwise_jaccard": mean_jaccard,
        "singleton_count": len(singleton_items),
        "singleton_items": sorted(singleton_items),
        "consensus_missing_oracle_items": sorted(oracle - consensus_items),
        "raw_union_false_items": sorted(union_items - oracle),
        "rows": sorted(rows, key=lambda row: METHOD_ORDER.index(row["method"])),
    }


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines: list[str] = []
    lines.append("# Evidence-Preserving Completion Protocol Results")
    lines.append("")
    lines.append("## Protocol")
    lines.append("")
    lines.append(
        "The protocol keeps consensus items as the conservative final set, sends "
        "singleton evidence to an audit queue, and triggers boundary-focused "
        "holdout when G3 agreement and confidence are both high."
    )
    lines.append("")
    lines.append("It never uses the oracle for decisions; the oracle is used only for scoring.")
    lines.append("")
    lines.append("## Case Metrics")
    lines.append("")
    lines.append("| case | mechanism | mean_conf | mean_jaccard | singleton_count | consensus_missing | raw_union_fp |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: |")
    for case in summary["cases"]:
        lines.append(
            "| {case_id} | {mechanism} | {conf} | {jac} | {singletons} | {missing} | {union_fp} |".format(
                case_id=case["case_id"],
                mechanism=case["mechanism"],
                conf=fmt(case["mean_confidence"]),
                jac=fmt(case["mean_pairwise_jaccard"]),
                singletons=case["singleton_count"],
                missing=len(case["consensus_missing_oracle_items"]),
                union_fp=len(case["raw_union_false_items"]),
            )
        )
    lines.append("")
    lines.append("## Method Comparison")
    lines.append("")
    lines.append("| case | method | status | found | TP | FP | recall | precision | completion | false_stop | notes |")
    lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |")
    for case in summary["cases"]:
        for row in case["rows"]:
            lines.append(
                "| {case_id} | {method} | {status} | {found} | {tp} | {fp} | {recall} | {precision} | {completion} | {false_stop} | {notes} |".format(
                    case_id=case["case_id"],
                    method=row["method"],
                    status=row["status"],
                    found=fmt(row["found"]),
                    tp=fmt(row["true_positive"]),
                    fp=fmt(row["false_positive"]),
                    recall=fmt(row["recall"]),
                    precision=fmt(row["precision"]),
                    completion=fmt(row["completion"]),
                    false_stop=fmt(row["false_stop"]),
                    notes=row["notes"].replace("|", "/"),
                )
            )
    lines.append("")
    lines.append("## Protocol Audit Details")
    lines.append("")
    lines.append("| case | protocol_status | risk_flags | audit_queue | verified_singletons | unverified_singletons | holdout_new_items |")
    lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: |")
    for case in summary["cases"]:
        protocol = next(
            row for row in case["rows"]
            if row["method"] == "evidence_preserving_protocol"
        )
        lines.append(
            "| {case_id} | {status} | {flags} | {audit_queue} | {verified} | {unverified} | {holdout_new} |".format(
                case_id=case["case_id"],
                status=protocol["status"],
                flags=", ".join(protocol.get("risk_flags", [])) or "none",
                audit_queue=protocol.get("audit_queue_size", 0),
                verified=len(protocol.get("verified_singletons", [])),
                unverified=len(protocol.get("unverified_singletons", [])),
                holdout_new=len(protocol.get("holdout_new_items", [])),
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base",
        type=Path,
        default=Path("experiments/false_convergence_pilot"),
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("experiments/false_convergence_pilot/protocol_outputs/evidence_preserving_protocol_results.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("experiments/false_convergence_pilot/reports/protocol/EVIDENCE_PRESERVING_PROTOCOL_RESULTS.md"),
    )
    args = parser.parse_args()

    summary = {
        "protocol": {
            "common_blindspot_jaccard": COMMON_BLINDSPOT_JACCARD,
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "theta": THETA,
        },
        "cases": [
            evaluate_case(args.base, case)
            for case in CASES
            if (args.base / case.runs_path).exists()
        ],
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(summary, args.out_md)


if __name__ == "__main__":
    main()
