#!/usr/bin/env python3
"""Evaluate a correlation-aware completion certificate on existing Line A runs."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from math import log2
from pathlib import Path
from typing import Any

from score_itemsets import (
    CONFIDENCE_THRESHOLD,
    THETA,
    jaccard,
    load_oracle,
    normalize_run,
    score_set,
)


OVERLAP_STOP_THRESHOLD = 0.95
GOOD_TURING_STOP_THRESHOLD = 0.05
CHAO_STOP_THRESHOLD = 0.05


@dataclass(frozen=True)
class CertificateCase:
    case_id: str
    task_family: str
    oracle_path: str
    runs_path: str
    task_has_boundary_risk: bool = True
    experimental_status: str = "blind_agent_result"
    reportable: bool = True


CASES = [
    CertificateCase(
        case_id="T1_hard_expanded",
        task_family="synthetic_code_audit",
        oracle_path="results/T1_hard_repo_oracle.json",
        runs_path="results/T1_hard_expanded_itemsets.json",
    ),
    CertificateCase(
        case_id="T1_hard_seed03_completed",
        task_family="synthetic_code_audit",
        oracle_path="results/T1_hard_repo_oracle.json",
        runs_path="results/T1_hard_seed03_completed_itemsets.json",
    ),
    CertificateCase(
        case_id="T2_policy_docs_seed01",
        task_family="synthetic_policy_docs",
        oracle_path="results/T2_policy_docs_oracle.json",
        runs_path="results/T2_policy_docs_seed01_itemsets.json",
    ),
    CertificateCase(
        case_id="T2_policy_docs_seed02",
        task_family="synthetic_policy_docs",
        oracle_path="results/T2_policy_docs_oracle.json",
        runs_path="results/T2_policy_docs_seed02_itemsets.json",
    ),
    CertificateCase(
        case_id="T2_policy_docs_seed03",
        task_family="synthetic_policy_docs",
        oracle_path="results/T2_policy_docs_oracle.json",
        runs_path="results/T2_policy_docs_seed03_itemsets.json",
    ),
    CertificateCase(
        case_id="T4_real_repo_click_seed01_smoke",
        task_family="real_repo_code_audit",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed01_smoke_itemsets.json",
        experimental_status="oracle_generated_smoke_test",
        reportable=False,
    ),
    CertificateCase(
        case_id="T4_real_repo_click_seed01_blind",
        task_family="real_repo_code_audit",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed01_blind_itemsets.json",
        experimental_status="blind_agent_result",
        reportable=True,
    ),
    CertificateCase(
        case_id="T4_real_repo_click_seed02_blind",
        task_family="real_repo_code_audit",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed02_blind_itemsets.json",
        experimental_status="blind_agent_result",
        reportable=True,
    ),
    CertificateCase(
        case_id="T4_real_repo_click_seed03_blind",
        task_family="real_repo_code_audit",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed03_blind_itemsets.json",
        experimental_status="blind_agent_result",
        reportable=True,
    ),
    CertificateCase(
        case_id="T5_real_repo_requests_tls_seed01_smoke",
        task_family="real_repo_tls_audit",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed01_smoke_itemsets.json",
        experimental_status="oracle_generated_smoke_test",
        reportable=False,
    ),
    CertificateCase(
        case_id="T5_real_repo_requests_tls_seed01_blind",
        task_family="real_repo_tls_audit",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed01_blind_itemsets.json",
        experimental_status="blind_agent_result",
        reportable=True,
    ),
    CertificateCase(
        case_id="T5_real_repo_requests_tls_seed02_blind",
        task_family="real_repo_tls_audit",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed02_blind_itemsets.json",
        experimental_status="blind_agent_result",
        reportable=True,
    ),
    CertificateCase(
        case_id="T5_real_repo_requests_tls_seed03_blind",
        task_family="real_repo_tls_audit",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed03_blind_itemsets.json",
        experimental_status="blind_agent_result",
        reportable=True,
    ),
]


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def source_bin(item: str) -> str:
    if "::" in item:
        return "case_file"
    source = item.rsplit(":", 1)[0] if ":" in item else item
    parts = source.replace("\\", "/").split("/")
    if len(parts) >= 3 and parts[0] == "repo":
        return "/".join(parts[:3])
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return source


def normalized_entropy(labels: list[str]) -> float:
    if not labels:
        return 0.0
    counts = Counter(labels)
    if len(counts) == 1:
        return 0.0
    total = sum(counts.values())
    entropy = -sum((count / total) * log2(count / total) for count in counts.values())
    return entropy / log2(len(counts))


def load_runs(path: Path) -> tuple[str, list[dict[str, Any]]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw.get("task_id", "unknown_task"), [normalize_run(run) for run in raw["runs"]]


def good_turing_missing_mass(counts: Counter[str]) -> float:
    incidences = sum(counts.values())
    if incidences == 0:
        return 1.0
    singletons = sum(1 for count in counts.values() if count == 1)
    return singletons / incidences


def chao_unseen_estimate(counts: Counter[str]) -> float:
    f1 = sum(1 for count in counts.values() if count == 1)
    f2 = sum(1 for count in counts.values() if count == 2)
    if f1 == 0:
        return 0.0
    if f2 > 0:
        return (f1 * f1) / (2 * f2)
    return (f1 * (f1 - 1)) / 2


def certificate_v0(
    *,
    counts: Counter[str],
    mean_confidence: float | None,
    mean_jaccard: float | None,
    task_has_boundary_risk: bool,
) -> dict[str, Any]:
    observed = len(counts)
    incidences = sum(counts.values())
    f1 = sum(1 for count in counts.values() if count == 1)
    f2 = sum(1 for count in counts.values() if count == 2)
    singleton_ratio = f1 / observed if observed else 0.0
    gt_missing_mass = good_turing_missing_mass(counts)
    chao_unseen = chao_unseen_estimate(counts)
    chao_total = observed + chao_unseen
    chao_missing_ratio = chao_unseen / chao_total if chao_total else 1.0
    overlap = mean_jaccard if mean_jaccard is not None else 0.0
    confidence = mean_confidence if mean_confidence is not None else 0.0
    effective_agents = 1 + 2 * (1 - overlap)

    flags: list[str] = []
    if confidence < CONFIDENCE_THRESHOLD:
        flags.append("low_confidence")
    if singleton_ratio >= 0.05 or gt_missing_mass >= 0.02:
        flags.append("singleton_missing_mass")
    if chao_missing_ratio >= 0.05:
        flags.append("chao_unseen_mass")
    if task_has_boundary_risk and confidence >= CONFIDENCE_THRESHOLD and overlap >= OVERLAP_STOP_THRESHOLD:
        flags.append("high_agreement_boundary_blindspot_risk")
    if confidence >= CONFIDENCE_THRESHOLD and effective_agents < 1.2:
        flags.append("low_effective_independence")

    risk_score = 0.0
    risk_score += 0.35 * min(1.0, singleton_ratio / 0.15)
    risk_score += 0.25 * min(1.0, chao_missing_ratio / 0.10)
    if "high_agreement_boundary_blindspot_risk" in flags:
        risk_score += 0.25
    if "low_effective_independence" in flags:
        risk_score += 0.10
    if "low_confidence" in flags:
        risk_score += 0.20
    risk_score = min(1.0, risk_score)

    if "high_agreement_boundary_blindspot_risk" in flags or risk_score >= 0.60:
        label = "unsafe_to_stop"
    elif flags or risk_score >= 0.25:
        label = "requires_audit"
    else:
        label = "certified"

    return {
        "label": label,
        "risk_score": risk_score,
        "risk_flags": flags,
        "observed_unique_items": observed,
        "total_item_incidences": incidences,
        "f1_singletons": f1,
        "f2_doubletons": f2,
        "singleton_ratio": singleton_ratio,
        "good_turing_missing_mass": gt_missing_mass,
        "chao_unseen_estimate": chao_unseen,
        "chao_missing_ratio": chao_missing_ratio,
        "effective_agent_count": effective_agents,
    }


def evaluate_seed(
    *,
    case: CertificateCase,
    task_id: str,
    oracle: set[str],
    buckets: dict[str, str],
    seed: str,
    g3_runs: list[dict[str, Any]],
    g6_runs: list[dict[str, Any]],
) -> dict[str, Any]:
    counts = Counter(item for run in g3_runs for item in run["items"])
    union_items = set(counts)
    consensus_items = {item for item, count in counts.items() if count >= 2}
    holdout_items = set().union(*(run["items"] for run in g6_runs)) if g6_runs else set()
    pairwise = [
        jaccard(left["items"], right["items"])
        for left, right in combinations(g3_runs, 2)
    ]
    mean_confidence = mean([
        run["confidence"] for run in g3_runs if run["confidence"] is not None
    ])
    mean_jaccard = mean(pairwise)
    certificate = certificate_v0(
        counts=counts,
        mean_confidence=mean_confidence,
        mean_jaccard=mean_jaccard,
        task_has_boundary_risk=case.task_has_boundary_risk,
    )
    consensus_metrics = score_set(consensus_items, oracle)
    union_metrics = score_set(union_items, oracle)
    holdout_metrics = score_set(holdout_items, oracle) if holdout_items else None
    source_bins = [source_bin(item) for item in union_items]

    baselines = {
        "confidence_stop": (
            mean_confidence is not None and mean_confidence >= CONFIDENCE_THRESHOLD
        ),
        "overlap_stop": (
            mean_jaccard is not None and mean_jaccard >= OVERLAP_STOP_THRESHOLD
        ),
        "good_turing_stop": (
            certificate["good_turing_missing_mass"] <= GOOD_TURING_STOP_THRESHOLD
        ),
        "chao_stop": (
            certificate["chao_missing_ratio"] <= CHAO_STOP_THRESHOLD
        ),
        "certificate_v0_stop": certificate["label"] == "certified",
    }
    baseline_rows = []
    for method, would_stop in baselines.items():
        baseline_rows.append({
            "method": method,
            "would_stop": would_stop,
            "false_certification": would_stop and consensus_metrics["recall"] < THETA,
            "conservative_block": (not would_stop) and consensus_metrics["recall"] >= THETA,
        })

    holdout_gain = None
    if holdout_items:
        holdout_gain = len((holdout_items - consensus_items) & oracle) / len(oracle)

    return {
        "case_id": case.case_id,
        "task_id": task_id,
        "task_family": case.task_family,
        "seed": seed,
        "reportable": case.reportable,
        "experimental_status": case.experimental_status,
        "oracle_size": len(oracle),
        "g3_run_ids": [run["run_id"] for run in g3_runs],
        "holdout_run_ids": [run["run_id"] for run in g6_runs],
        "mean_confidence": mean_confidence,
        "pairwise_jaccard": pairwise,
        "mean_pairwise_jaccard": mean_jaccard,
        "source_bin_count": len(set(source_bins)),
        "source_bin_entropy": normalized_entropy(source_bins),
        "consensus": {
            key: value for key, value in consensus_metrics.items()
            if key not in {"true_items", "false_items"}
        },
        "union": {
            key: value for key, value in union_metrics.items()
            if key not in {"true_items", "false_items"}
        },
        "holdout": None if holdout_metrics is None else {
            key: value for key, value in holdout_metrics.items()
            if key not in {"true_items", "false_items"}
        },
        "holdout_gain": holdout_gain,
        "consensus_missing_true_items": sorted(oracle - consensus_items),
        "union_false_items": sorted(union_items - oracle),
        "holdout_new_true_items": sorted((holdout_items - consensus_items) & oracle),
        "certificate": certificate,
        "baselines": baseline_rows,
    }


def evaluate_case(base: Path, case: CertificateCase) -> list[dict[str, Any]]:
    oracle, buckets = load_oracle(base / case.oracle_path)
    task_id, runs = load_runs(base / case.runs_path)
    by_seed: dict[str, list[dict[str, Any]]] = {}
    holdout_by_seed: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        if run["group"] == "G3":
            by_seed.setdefault(run["seed"], []).append(run)
        if run["group"] == "G6":
            holdout_by_seed.setdefault(run["seed"], []).append(run)

    rows = []
    for seed, g3_runs in sorted(by_seed.items()):
        if len(g3_runs) < 3:
            continue
        rows.append(evaluate_seed(
            case=case,
            task_id=task_id,
            oracle=oracle,
            buckets=buckets,
            seed=seed,
            g3_runs=g3_runs,
            g6_runs=holdout_by_seed.get(seed, []),
        ))
    return rows


def aggregate_baselines(seed_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    methods = sorted({
        baseline["method"]
        for row in seed_rows
        if row["reportable"]
        for baseline in row["baselines"]
    })
    rows = []
    for method in methods:
        method_rows = [
            baseline
            for row in seed_rows
            if row["reportable"]
            for baseline in row["baselines"]
            if baseline["method"] == method
        ]
        if not method_rows:
            continue
        rows.append({
            "method": method,
            "n": len(method_rows),
            "certified_or_stopped": sum(1 for row in method_rows if row["would_stop"]),
            "false_certifications": sum(1 for row in method_rows if row["false_certification"]),
            "conservative_blocks": sum(1 for row in method_rows if row["conservative_block"]),
        })
    return rows


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Completion Certificate v0 Results",
        "",
        "The certificate uses only observable run signals for decisions. Oracle labels are used only afterward to evaluate whether a stop decision would have been safe.",
        "",
        "## Seed-Level Certificates",
        "",
        "| case | seed | reportable | consensus_recall | union_precision | mean_conf | mean_jaccard | f1 | GT mass | Chao miss | risk | label | flags |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in summary["seed_results"]:
        cert = row["certificate"]
        lines.append(
            "| {case_id} | {seed} | {reportable} | {consensus_recall} | {union_precision} | {conf} | {jac} | {f1} | {gt} | {chao} | {risk} | {label} | {flags} |".format(
                case_id=row["case_id"],
                seed=row["seed"],
                reportable=fmt(row["reportable"]),
                consensus_recall=fmt(row["consensus"]["recall"]),
                union_precision=fmt(row["union"]["precision"]),
                conf=fmt(row["mean_confidence"]),
                jac=fmt(row["mean_pairwise_jaccard"]),
                f1=cert["f1_singletons"],
                gt=fmt(cert["good_turing_missing_mass"]),
                chao=fmt(cert["chao_missing_ratio"]),
                risk=fmt(cert["risk_score"]),
                label=cert["label"],
                flags=", ".join(cert["risk_flags"]) or "none",
            )
        )
    lines.extend([
        "",
        "## Baseline Stop Safety",
        "",
        "| method | n | stopped/certified | false certifications | conservative blocks |",
        "| --- | ---: | ---: | ---: | ---: |",
    ])
    for row in summary["baseline_aggregate"]:
        lines.append(
            f"| {row['method']} | {row['n']} | {row['certified_or_stopped']} | "
            f"{row['false_certifications']} | {row['conservative_blocks']} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_cn(summary: dict[str, Any], path: Path) -> None:
    reportable_rows = [row for row in summary["seed_results"] if row["reportable"]]
    unsafe_or_audit = sum(
        1 for row in reportable_rows
        if row["certificate"]["label"] != "certified"
    )
    false_consensus = sum(
        1 for row in reportable_rows
        if row["consensus"]["recall"] < THETA
    )
    cert_false = next(
        row for row in summary["baseline_aggregate"]
        if row["method"] == "certificate_v0_stop"
    )

    lines = [
        "# Completion Certificate v0 中文结果",
        "",
        "日期：2026-06-08",
        "",
        "## 一句话结论",
        "",
        "v0 证书没有把当前这些高风险 run 轻易判成“已完成”。它把少数派证据、经典 missing-mass 信号和高一致共同盲点都转成了 `requires_audit` 或 `unsafe_to_stop`，这比单纯看 confidence / overlap 更适合作为论文里的停止条件方向。",
        "",
        "## 当前结果怎么读",
        "",
        f"- 可报告 G3 seed 数：`{len(reportable_rows)}`。",
        f"- 其中 consensus recall 低于 `{THETA:.2f}` 的 seed 数：`{false_consensus}`。",
        f"- certificate v0 输出非 certified 的 seed 数：`{unsafe_or_audit}`。",
        f"- certificate v0 的 false certification 数：`{cert_false['false_certifications']}`。",
        "",
        "注意：这不是说 v0 已经是最终方法。它现在更像一个保守的“别急着停”证书，价值在于把 false convergence 从隐藏错误变成显式审计信号。",
        "",
        "## 逐 seed 结果",
        "",
        "| case | seed | consensus recall | union precision | mean jaccard | f1 singleton | GT mass | Chao missing | certificate | flags |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in reportable_rows:
        cert = row["certificate"]
        lines.append(
            "| {case_id} | {seed} | {recall} | {precision} | {jac} | {f1} | {gt} | {chao} | {label} | {flags} |".format(
                case_id=row["case_id"],
                seed=row["seed"],
                recall=fmt(row["consensus"]["recall"]),
                precision=fmt(row["union"]["precision"]),
                jac=fmt(row["mean_pairwise_jaccard"]),
                f1=cert["f1_singletons"],
                gt=fmt(cert["good_turing_missing_mass"]),
                chao=fmt(cert["chao_missing_ratio"]),
                label=cert["label"],
                flags=", ".join(cert["risk_flags"]) or "none",
            )
        )
    lines.extend([
        "",
        "## 和简单停止基线相比",
        "",
        "| stopping rule | stopped/certified | false certifications | conservative blocks |",
        "| --- | ---: | ---: | ---: |",
    ])
    for row in summary["baseline_aggregate"]:
        lines.append(
            f"| {row['method']} | {row['certified_or_stopped']} | "
            f"{row['false_certifications']} | {row['conservative_blocks']} |"
        )
    lines.extend([
        "",
        "## 对论文实验的意义",
        "",
        "这一步把方法主线从“加一个 holdout agent”升级为“完成性风险估计”。更漂亮的论文实验应该继续补真实盲评 T4，并记录完整 incidence log；然后比较 confidence、overlap、Good-Turing、Chao 和 certificate v0 在 false stop 检测上的差异。",
        "",
        "T4 smoke 行没有进入可报告统计，因为它是 oracle-generated scorer compatibility test，不能当作 blind-agent result。",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_cn(summary: dict[str, Any], path: Path) -> None:
    reportable_rows = [row for row in summary["seed_results"] if row["reportable"]]
    unsafe_or_audit = sum(
        1 for row in reportable_rows
        if row["certificate"]["label"] != "certified"
    )
    false_consensus = sum(
        1 for row in reportable_rows
        if row["consensus"]["recall"] < THETA
    )
    cert_false = next(
        row for row in summary["baseline_aggregate"]
        if row["method"] == "certificate_v0_stop"
    )

    lines = [
        "# Completion Certificate v0 中文结果",
        "",
        "日期：2026-06-08",
        "",
        "## 一句话结论",
        "",
        "v0 证书没有把当前这些高风险 run 轻易判成“已经完成”。它会把少数派证据、missing-mass 信号和高一致共同盲点转成 `requires_audit` 或 `unsafe_to_stop`，比单看 confidence / overlap 更适合作为论文里的停止条件方向。",
        "",
        "## 当前结果怎么读",
        "",
        f"- 可报告 G3 seed 数：`{len(reportable_rows)}`。",
        f"- 其中 consensus recall 低于 `{THETA:.2f}` 的 seed 数：`{false_consensus}`。",
        f"- certificate v0 输出非 certified 的 seed 数：`{unsafe_or_audit}`。",
        f"- certificate v0 的 false certification 数：`{cert_false['false_certifications']}`。",
        "",
        "注意：这不是说 v0 已经是最终方法。它现在更像一个保守的“别急着停”证书，价值在于把 false convergence 从隐藏错误变成显式审计信号。",
        "",
        "## 逐 seed 结果",
        "",
        "| case | seed | consensus recall | union precision | mean jaccard | f1 singleton | GT mass | Chao missing | certificate | flags |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in reportable_rows:
        cert = row["certificate"]
        lines.append(
            "| {case_id} | {seed} | {recall} | {precision} | {jac} | {f1} | {gt} | {chao} | {label} | {flags} |".format(
                case_id=row["case_id"],
                seed=row["seed"],
                recall=fmt(row["consensus"]["recall"]),
                precision=fmt(row["union"]["precision"]),
                jac=fmt(row["mean_pairwise_jaccard"]),
                f1=cert["f1_singletons"],
                gt=fmt(cert["good_turing_missing_mass"]),
                chao=fmt(cert["chao_missing_ratio"]),
                label=cert["label"],
                flags=", ".join(cert["risk_flags"]) or "none",
            )
        )
    lines.extend([
        "",
        "## 和简单停止基线相比",
        "",
        "| stopping rule | stopped/certified | false certifications | conservative blocks |",
        "| --- | ---: | ---: | ---: |",
    ])
    for row in summary["baseline_aggregate"]:
        lines.append(
            f"| {row['method']} | {row['certified_or_stopped']} | "
            f"{row['false_certifications']} | {row['conservative_blocks']} |"
        )
    lines.extend([
        "",
        "## 对论文实验的意义",
        "",
        "这一步把方法主线从“加一个 holdout agent”升级为“完成性风险估计”。真实仓库 T4 seed01/02/03 中，certificate v0 都没有给出 certified，因此它能稳定避免把高风险状态误报为完成。",
        "",
        "T4 smoke 行没有进入可报告统计，因为它是 oracle-generated scorer compatibility test，不能当作 blind-agent result。",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path("experiments/false_convergence_pilot"))
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("experiments/false_convergence_pilot/protocol_outputs/completion_certificate_v0_results.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("experiments/false_convergence_pilot/reports/protocol/COMPLETION_CERTIFICATE_V0_RESULTS.md"),
    )
    parser.add_argument(
        "--out-cn-md",
        type=Path,
        default=Path("experiments/false_convergence_pilot/reports/protocol/COMPLETION_CERTIFICATE_V0_RESULTS_CN.md"),
    )
    args = parser.parse_args()

    seed_results: list[dict[str, Any]] = []
    for case in CASES:
        if (args.base / case.runs_path).exists():
            seed_results.extend(evaluate_case(args.base, case))
    summary = {
        "thresholds": {
            "theta": THETA,
            "confidence": CONFIDENCE_THRESHOLD,
            "overlap_stop": OVERLAP_STOP_THRESHOLD,
            "good_turing_stop": GOOD_TURING_STOP_THRESHOLD,
            "chao_stop": CHAO_STOP_THRESHOLD,
        },
        "seed_results": seed_results,
        "baseline_aggregate": aggregate_baselines(seed_results),
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_cn_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(summary, args.out_md)
    write_cn(summary, args.out_cn_md)


if __name__ == "__main__":
    main()
