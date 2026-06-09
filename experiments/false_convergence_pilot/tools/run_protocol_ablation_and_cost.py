#!/usr/bin/env python3
"""Run protocol ablations and proxy cost analysis for Line A."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

from run_evidence_preserving_protocol import (
    CASES,
    COMMON_BLINDSPOT_JACCARD,
    CaseSpec,
    fmt,
    load_runs,
    mean,
)
from score_itemsets import (
    CONFIDENCE_THRESHOLD,
    THETA,
    jaccard,
    load_oracle,
    score_set,
)


ABLATIONS = [
    "consensus_only",
    "no_singleton_audit",
    "no_common_blindspot_trigger",
    "no_holdout",
    "full_protocol",
]


def case_state(base: Path, case: CaseSpec) -> dict[str, Any]:
    oracle, _ = load_oracle(base / case.oracle_path)
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
    pairwise = [
        jaccard(left["items"], right["items"])
        for left, right in combinations(g3_runs, 2)
    ]
    mean_confidence = mean([
        run["confidence"] for run in g3_runs if run["confidence"] is not None
    ])
    mean_jaccard = mean(pairwise)
    high_confidence = (
        mean_confidence is not None and mean_confidence >= CONFIDENCE_THRESHOLD
    )
    high_agreement = (
        mean_jaccard is not None and mean_jaccard >= COMMON_BLINDSPOT_JACCARD
    )
    return {
        "oracle": oracle,
        "g3_runs": g3_runs,
        "g6_runs": g6_runs,
        "consensus_items": {item for item, count in item_counts.items() if count >= 2},
        "union_items": set(item_counts),
        "singleton_items": {item for item, count in item_counts.items() if count == 1},
        "holdout_items": set().union(*(run["items"] for run in g6_runs)) if g6_runs else set(),
        "mean_confidence": mean_confidence,
        "mean_jaccard": mean_jaccard,
        "high_confidence": high_confidence,
        "high_agreement": high_agreement,
    }


def run_variant(state: dict[str, Any], variant: str, task_has_boundary_risk: bool) -> dict[str, Any]:
    consensus_items: set[str] = state["consensus_items"]
    union_items: set[str] = state["union_items"]
    singleton_items: set[str] = state["singleton_items"]
    holdout_items: set[str] = state["holdout_items"]

    singleton_trigger = bool(singleton_items)
    blindspot_trigger = (
        task_has_boundary_risk
        and state["high_confidence"]
        and state["high_agreement"]
    )

    use_singleton_audit = variant in {
        "no_common_blindspot_trigger",
        "no_holdout",
        "full_protocol",
    }
    use_blindspot_trigger = variant in {
        "no_singleton_audit",
        "no_holdout",
        "full_protocol",
    }
    use_holdout = variant in {
        "no_singleton_audit",
        "no_common_blindspot_trigger",
        "full_protocol",
    }

    risk_flags: list[str] = []
    if singleton_trigger and use_singleton_audit:
        risk_flags.append("singleton_evidence_requires_audit")
    if blindspot_trigger and use_blindspot_trigger:
        risk_flags.append("high_agreement_boundary_blindspot_risk")

    final_items = set(consensus_items)
    verified_singletons: set[str] = set()
    holdout_new_items: set[str] = set()
    holdout_triggered = bool(risk_flags)
    holdout_available = bool(holdout_items)

    if use_holdout and holdout_triggered and holdout_available:
        if "singleton_evidence_requires_audit" in risk_flags:
            verified_singletons = singleton_items & holdout_items
            final_items |= verified_singletons
        if "high_agreement_boundary_blindspot_risk" in risk_flags:
            holdout_new_items = holdout_items - union_items
            final_items |= holdout_new_items

    if variant == "consensus_only":
        status = "complete_by_consensus"
        completion = state["high_confidence"]
        holdout_used = False
    elif holdout_triggered and not use_holdout:
        status = "requires_audit_no_holdout"
        completion = False
        holdout_used = False
    elif holdout_triggered and use_holdout and holdout_available:
        status = "verified_after_holdout"
        completion = True
        holdout_used = True
    elif holdout_triggered:
        status = "requires_audit_holdout_missing"
        completion = False
        holdout_used = False
    else:
        status = "complete_no_audit_trigger"
        completion = state["high_confidence"]
        holdout_used = False

    return {
        "variant": variant,
        "items": final_items,
        "status": status,
        "completion": completion,
        "risk_flags": risk_flags,
        "audit_queue_size": len(singleton_items) if singleton_trigger and use_singleton_audit else 0,
        "holdout_triggered": holdout_triggered,
        "holdout_used": holdout_used,
        "verified_singletons": sorted(verified_singletons),
        "holdout_new_items": sorted(holdout_new_items),
    }


def evaluate(base: Path) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    for case in CASES:
        if not (base / case.runs_path).exists():
            continue
        state = case_state(base, case)
        oracle: set[str] = state["oracle"]
        consensus_metrics = score_set(state["consensus_items"], oracle)
        raw_union_metrics = score_set(state["union_items"], oracle)
        variants = []
        for variant in ABLATIONS:
            result = run_variant(state, variant, case.task_has_boundary_risk)
            metrics = score_set(result["items"], oracle)
            recovered_tp = metrics["true_positive"] - consensus_metrics["true_positive"]
            avoided_fp = raw_union_metrics["false_positive"] - metrics["false_positive"]
            audit_actions = result["audit_queue_size"] + (1 if result["holdout_used"] else 0)
            variants.append({
                "variant": variant,
                "status": result["status"],
                "risk_flags": result["risk_flags"],
                "found": metrics["found"],
                "true_positive": metrics["true_positive"],
                "false_positive": metrics["false_positive"],
                "recall": metrics["recall"],
                "precision": metrics["precision"],
                "completion": result["completion"],
                "false_stop": result["completion"] and metrics["recall"] < THETA,
                "audit_queue_size": result["audit_queue_size"],
                "holdout_used": result["holdout_used"],
                "verified_singletons": len(result["verified_singletons"]),
                "holdout_new_items": len(result["holdout_new_items"]),
                "recovered_tp_over_consensus": recovered_tp,
                "avoided_fp_vs_raw_union": avoided_fp,
                "audit_actions_proxy": audit_actions,
                "audit_actions_per_recovered_tp": (
                    None if recovered_tp <= 0 else audit_actions / recovered_tp
                ),
            })

        cases.append({
            "case_id": case.case_id,
            "mechanism": case.mechanism,
            "oracle_size": len(oracle),
            "mean_confidence": state["mean_confidence"],
            "mean_jaccard": state["mean_jaccard"],
            "singleton_count": len(state["singleton_items"]),
            "holdout_available": bool(state["holdout_items"]),
            "consensus_recall": consensus_metrics["recall"],
            "raw_union_precision": raw_union_metrics["precision"],
            "variants": variants,
        })
    return {
        "notes": {
            "cost_type": "proxy",
            "audit_actions_proxy": "audit_queue_size plus one unit for each triggered holdout run",
            "token_costs": "not available in current logs",
            "wall_clock_costs": "not available in current logs",
        },
        "cases": cases,
    }


def write_ablation_md(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Protocol Ablation Results",
        "",
        "Ablations are scored with the oracle only after the variant has selected",
        "its output. Oracle labels are not used to make protocol decisions.",
        "",
        "| case | mechanism | variant | status | TP | FP | recall | precision | completion | false_stop |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for case in summary["cases"]:
        for row in case["variants"]:
            lines.append(
                "| {case_id} | {mechanism} | {variant} | {status} | {tp} | {fp} | {recall} | {precision} | {completion} | {false_stop} |".format(
                    case_id=case["case_id"],
                    mechanism=case["mechanism"],
                    variant=row["variant"],
                    status=row["status"],
                    tp=row["true_positive"],
                    fp=row["false_positive"],
                    recall=fmt(row["recall"]),
                    precision=fmt(row["precision"]),
                    completion=fmt(row["completion"]),
                    false_stop=fmt(row["false_stop"]),
                )
            )
    lines.append("")
    lines.append("## Main Takeaways")
    lines.append("")
    lines.append("- Removing singleton audit leaves aggregation-loss singletons unrecovered.")
    lines.append("- Removing common-blindspot trigger leaves high-agreement blind spots unrecovered.")
    lines.append("- Removing holdout converts hidden risk into `requires_audit`, but cannot recover missing items.")
    lines.append("- Full protocol is the only variant that covers both failure mechanisms when holdout evidence is available.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_cost_md(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Protocol Cost Proxy Analysis",
        "",
        "Current logs do not contain reliable token or wall-clock accounting, so this",
        "table reports a proxy cost: `audit_queue_size + holdout_run_units`.",
        "",
        "| case | variant | audit_queue | holdout_used | audit_actions | recovered_TP | actions_per_recovered_TP | avoided_FP_vs_raw_union |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for case in summary["cases"]:
        for row in case["variants"]:
            if row["variant"] not in {"no_holdout", "full_protocol"}:
                continue
            lines.append(
                "| {case_id} | {variant} | {queue} | {holdout} | {actions} | {recovered} | {per_tp} | {avoided_fp} |".format(
                    case_id=case["case_id"],
                    variant=row["variant"],
                    queue=row["audit_queue_size"],
                    holdout=fmt(row["holdout_used"]),
                    actions=row["audit_actions_proxy"],
                    recovered=row["recovered_tp_over_consensus"],
                    per_tp=fmt(row["audit_actions_per_recovered_tp"]),
                    avoided_fp=row["avoided_fp_vs_raw_union"],
                )
            )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- The proxy cost is intentionally conservative and transparent.")
    lines.append("- Token and wall-clock cost should be added once run logs are collected.")
    lines.append("- `requires_audit` cases are not failures of the controller; they are cases where the controller refuses to certify completion without more evidence.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_cn(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Protocol Ablation 与成本代理分析",
        "",
        "日期：2026-06-08",
        "",
        "## 一句话结论",
        "",
        "ablation 结果支持当前方法设计：singleton audit 负责恢复 aggregation loss，common-blindspot trigger 负责发现高一致下的共同盲点，holdout 负责把风险从“待审计”推进到“已验证”。",
        "",
        "## Ablation 结论",
        "",
        "- 去掉 singleton audit：T1 seed01 / T2 seed01 的少数派真项无法恢复。",
        "- 去掉 common-blindspot trigger：T2 seed02/03 仍会停在 `28/30`。",
        "- 去掉 holdout：系统能发现风险并输出 `requires_audit`，但不能恢复漏项。",
        "- full protocol：在已有 holdout 的 case 中同时覆盖 aggregation loss 和 common blind spot；在 T1 seed02/03 中避免 raw union 的误报。",
        "",
        "## 成本说明",
        "",
        "当前日志没有可靠 token 和 wall-clock 记录，因此这里只报告 proxy cost：",
        "",
        "```text",
        "audit_actions_proxy = audit_queue_size + holdout_run_units",
        "```",
        "",
        "| case | full protocol 状态 | audit queue | holdout used | recovered TP | avoided FP vs raw union |",
        "| --- | --- | ---: | --- | ---: | ---: |",
    ]
    for case in summary["cases"]:
        row = next(item for item in case["variants"] if item["variant"] == "full_protocol")
        lines.append(
            "| {case_id} | {status} | {queue} | {holdout} | {recovered} | {avoided_fp} |".format(
                case_id=case["case_id"],
                status=row["status"],
                queue=row["audit_queue_size"],
                holdout=fmt(row["holdout_used"]),
                recovered=row["recovered_tp_over_consensus"],
                avoided_fp=row["avoided_fp_vs_raw_union"],
            )
        )
    lines.extend([
        "",
        "## 论文里怎么写",
        "",
        "这部分可以作为方法有效性的 stronger validation：不是只展示 full protocol 有效，而是证明每个组件分别对应一种失败机制。成本部分暂时写成 proxy analysis，并明确下一步要记录真实 token / wall-clock。",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_cn(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Protocol Ablation 与成本代理分析",
        "",
        "日期：2026-06-08",
        "",
        "## 一句话结论",
        "",
        "ablation 结果支持当前方法设计：singleton audit 负责恢复 aggregation loss，common-blindspot trigger 负责发现高一致下的共同盲点，holdout 负责把风险从“待审计”推进到“已验证”。",
        "",
        "## Ablation 结论",
        "",
        "- 去掉 singleton audit：T1 seed01 / T2 seed01 的少数派真项无法恢复。",
        "- 去掉 common-blindspot trigger：T2 seed02/03 仍会停在 `28/30`。",
        "- 去掉 holdout：系统能发现风险并输出 `requires_audit`，但不能恢复漏项。",
        "- full protocol：在已有 holdout 的 case 中同时覆盖 aggregation loss 和 common blind spot；在 raw union 会带来误报的 case 中保持更保守。",
        "",
        "## 成本说明",
        "",
        "当前日志已有 T4 summarizer 的 token / wall-clock 记录；协议级别仍先报告 proxy cost：",
        "",
        "```text",
        "audit_actions_proxy = audit_queue_size + holdout_run_units",
        "```",
        "",
        "| case | full protocol status | audit queue | holdout used | recovered TP | avoided FP vs raw union |",
        "| --- | --- | ---: | --- | ---: | ---: |",
    ]
    for case in summary["cases"]:
        row = next(item for item in case["variants"] if item["variant"] == "full_protocol")
        lines.append(
            "| {case_id} | {status} | {queue} | {holdout} | {recovered} | {avoided_fp} |".format(
                case_id=case["case_id"],
                status=row["status"],
                queue=row["audit_queue_size"],
                holdout=fmt(row["holdout_used"]),
                recovered=row["recovered_tp_over_consensus"],
                avoided_fp=row["avoided_fp_vs_raw_union"],
            )
        )
    lines.extend([
        "",
        "## 论文里怎么写",
        "",
        "这部分可以作为方法有效性的 stronger validation：不是只展示 full protocol 有效，而是证明每个组件分别对应一种失败机制。需要诚实说明，T4 seed02/03 中当前 holdout 召回仍不足，所以 protocol 更强的是风险暴露与保守停止，稳定恢复还需要更强审计策略。",
        "",
    ])
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
        default=Path("experiments/false_convergence_pilot/protocol_outputs/protocol_ablation_cost_results.json"),
    )
    parser.add_argument(
        "--out-ablation-md",
        type=Path,
        default=Path("experiments/false_convergence_pilot/reports/protocol/PROTOCOL_ABLATION_RESULTS.md"),
    )
    parser.add_argument(
        "--out-cost-md",
        type=Path,
        default=Path("experiments/false_convergence_pilot/reports/protocol/PROTOCOL_COST_PROXY_RESULTS.md"),
    )
    parser.add_argument(
        "--out-cn-md",
        type=Path,
        default=Path("experiments/false_convergence_pilot/reports/protocol/PROTOCOL_ABLATION_COST_RESULTS_CN.md"),
    )
    args = parser.parse_args()

    summary = evaluate(args.base)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_ablation_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_cost_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_cn_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_ablation_md(summary, args.out_ablation_md)
    write_cost_md(summary, args.out_cost_md)
    write_cn(summary, args.out_cn_md)


if __name__ == "__main__":
    main()
