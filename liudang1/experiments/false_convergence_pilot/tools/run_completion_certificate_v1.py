#!/usr/bin/env python3
"""Decoupled completion certificate and audit-policy evaluation.

This v1 evaluator separates:

1. pre-audit certificate: exploration-only signals, no holdout gain;
2. audit policy: decides what evidence to request/inspect;
3. post-audit certificate: reruns the same rule on the updated evidence ledger.

Oracle labels are used only for offline metrics.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import combinations
from math import log2
from pathlib import Path
from typing import Any, Iterable

from score_itemsets import CONFIDENCE_THRESHOLD, THETA, jaccard, load_oracle, normalize_run, score_set


SAFE = "SAFE-TO-STOP"
UNSAFE = "UNSAFE-TO-STOP"
AUDIT = "REQUIRES-AUDIT"

OVERLAP_HIGH = 0.95
CHAO_MISSING_SAFE = 0.05
RISK_SAFE = 0.25
RISK_UNSAFE = 0.60
MIN_SOURCE_COVERAGE = 0.30


@dataclass(frozen=True)
class CaseSpec:
    case_id: str
    family: str
    oracle_path: str
    runs_path: str
    task_root: str | None
    source_globs: tuple[str, ...]
    boundary_risk: bool = True
    reportable: bool = True


CASES = [
    CaseSpec(
        case_id="T1_hard",
        family="synthetic_code_audit",
        oracle_path="results/T1_hard_repo_oracle.json",
        runs_path="results/T1_hard_expanded_itemsets.json",
        task_root="T1_acmepay_repo",
        source_globs=("*.py", "*.md"),
    ),
    CaseSpec(
        case_id="T1_hard_seed03",
        family="synthetic_code_audit",
        oracle_path="results/T1_hard_repo_oracle.json",
        runs_path="results/T1_hard_seed03_completed_itemsets.json",
        task_root="T1_acmepay_repo",
        source_globs=("*.py", "*.md"),
    ),
    CaseSpec(
        case_id="T2_policy_docs_seed01",
        family="synthetic_policy_docs",
        oracle_path="results/T2_policy_docs_oracle.json",
        runs_path="results/T2_policy_docs_seed01_itemsets.json",
        task_root="T2_policy_docs",
        source_globs=("*.md",),
    ),
    CaseSpec(
        case_id="T2_policy_docs_seed02",
        family="synthetic_policy_docs",
        oracle_path="results/T2_policy_docs_oracle.json",
        runs_path="results/T2_policy_docs_seed02_itemsets.json",
        task_root="T2_policy_docs",
        source_globs=("*.md",),
    ),
    CaseSpec(
        case_id="T2_policy_docs_seed03",
        family="synthetic_policy_docs",
        oracle_path="results/T2_policy_docs_oracle.json",
        runs_path="results/T2_policy_docs_seed03_itemsets.json",
        task_root="T2_policy_docs",
        source_globs=("*.md",),
    ),
    CaseSpec(
        case_id="T4_real_repo_click_seed01_blind",
        family="real_repo_click_deprecation",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed01_blind_itemsets.json",
        task_root="T4_real_repo_click",
        source_globs=("*.py", "*.md", "*.rst"),
    ),
    CaseSpec(
        case_id="T4_real_repo_click_seed02_blind",
        family="real_repo_click_deprecation",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed02_blind_itemsets.json",
        task_root="T4_real_repo_click",
        source_globs=("*.py", "*.md", "*.rst"),
    ),
    CaseSpec(
        case_id="T4_real_repo_click_seed03_blind",
        family="real_repo_click_deprecation",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed03_blind_itemsets.json",
        task_root="T4_real_repo_click",
        source_globs=("*.py", "*.md", "*.rst"),
    ),
    CaseSpec(
        case_id="T5_real_repo_requests_tls_seed01_blind",
        family="real_repo_requests_tls",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed01_blind_itemsets.json",
        task_root="T5_real_repo_requests_tls",
        source_globs=("*.py", "*.md", "*.rst"),
    ),
    CaseSpec(
        case_id="T5_real_repo_requests_tls_seed02_blind",
        family="real_repo_requests_tls",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed02_blind_itemsets.json",
        task_root="T5_real_repo_requests_tls",
        source_globs=("*.py", "*.md", "*.rst"),
    ),
    CaseSpec(
        case_id="T5_real_repo_requests_tls_seed03_blind",
        family="real_repo_requests_tls",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed03_blind_itemsets.json",
        task_root="T5_real_repo_requests_tls",
        source_globs=("*.py", "*.md", "*.rst"),
    ),
]


def mean(values: Iterable[float | None]) -> float | None:
    kept = [value for value in values if value is not None]
    return sum(kept) / len(kept) if kept else None


def source_id(item: str) -> str:
    if "::" in item:
        return item.split("::", maxsplit=1)[0]
    return item.rsplit(":", maxsplit=1)[0].replace("\\", "/")


def source_bin(item: str) -> str:
    source = source_id(item)
    parts = source.split("/")
    if len(parts) >= 3 and parts[0] == "repo":
        return "/".join(parts[:3])
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return source


def normalized_entropy(labels: list[str]) -> float:
    if not labels:
        return 0.0
    counts = Counter(labels)
    if len(counts) <= 1:
        return 0.0
    total = sum(counts.values())
    entropy = -sum((count / total) * log2(count / total) for count in counts.values())
    return entropy / log2(len(counts))


def source_universe(base: Path, case: CaseSpec) -> set[str]:
    if case.task_root is None:
        return set()
    root = base / case.task_root
    if not root.exists():
        return set()
    paths: set[str] = set()
    for glob in case.source_globs:
        for path in root.rglob(glob):
            if path.is_file():
                rel = path.relative_to(root).as_posix()
                paths.add(rel)
                if rel.startswith("repo/"):
                    paths.add(rel.removeprefix("repo/"))
    return paths


def source_coverage(items: set[str], universe: set[str]) -> dict[str, Any]:
    observed = {source_id(item) for item in items}
    if not universe:
        return {
            "observed_sources": len(observed),
            "source_universe_size": None,
            "source_coverage": None,
        }
    normalized = {src.removeprefix("repo/") for src in observed}
    covered = observed | normalized
    return {
        "observed_sources": len(observed),
        "source_universe_size": len(universe),
        "source_coverage": len(covered & universe) / len(universe) if universe else None,
    }


def f1_score(recall: float, precision: float) -> float:
    if recall + precision == 0:
        return 0.0
    return 2 * recall * precision / (recall + precision)


def chao_unseen(counts: Counter[str]) -> float:
    f1 = sum(1 for count in counts.values() if count == 1)
    f2 = sum(1 for count in counts.values() if count == 2)
    if f1 == 0:
        return 0.0
    if f2 == 0:
        return f1 * (f1 - 1) / 2
    return (f1 * f1) / (2 * f2)


def effective_exploration_size(agent_count: int, output_jaccard: float | None) -> float:
    if agent_count <= 0:
        return 0.0
    rho = max(0.0, min(1.0, output_jaccard if output_jaccard is not None else 0.0))
    return agent_count / (1 + (agent_count - 1) * rho)


def certificate_rule(
    *,
    stage: str,
    counts: Counter[str],
    confidences: list[float | None],
    agent_items: list[set[str]],
    boundary_risk: bool,
    source_stats: dict[str, Any],
    post_audit_signals: dict[str, Any] | None = None,
) -> dict[str, Any]:
    observed = len(counts)
    incidences = sum(counts.values())
    f1 = sum(1 for count in counts.values() if count == 1)
    f2 = sum(1 for count in counts.values() if count == 2)
    singleton_ratio = f1 / observed if observed else 1.0
    doubleton_ratio = f2 / observed if observed else 0.0
    gt_missing_mass = f1 / incidences if incidences else 1.0
    chao = chao_unseen(counts)
    chao_missing_ratio = chao / (observed + chao) if observed + chao else 1.0

    pairwise_output = [jaccard(left, right) for left, right in combinations(agent_items, 2)]
    source_sets = [{source_bin(item) for item in items} for items in agent_items]
    pairwise_source = [jaccard(left, right) for left, right in combinations(source_sets, 2)]
    output_jaccard = mean(pairwise_output)
    source_overlap = mean(pairwise_source)
    confidence = mean(confidences)
    source_cov = source_stats.get("source_coverage")
    source_cov_for_risk = 0.50 if source_cov is None else source_cov
    eff_size = effective_exploration_size(len(agent_items), output_jaccard)
    corr_factor = len(agent_items) / eff_size if eff_size > 0 else 1.0
    adjusted_chao_missing = min(1.0, chao_missing_ratio * corr_factor)

    post_audit_signals = post_audit_signals or {}
    unresolved_singletons = post_audit_signals.get("unresolved_singletons", f1)
    audit_verified_items = post_audit_signals.get("audit_verified_items", 0)
    holdout_gain = post_audit_signals.get("holdout_gain")

    risk_components = {
        "low_confidence": 0.0 if confidence is not None and confidence >= CONFIDENCE_THRESHOLD else 0.12,
        "singleton_missing_mass": 0.25 * min(1.0, singleton_ratio / 0.20),
        "chao_missing_mass": 0.22 * min(1.0, chao_missing_ratio / 0.10),
        "correlation_adjusted_missing_mass": 0.20 * min(1.0, adjusted_chao_missing / 0.15),
        "low_source_coverage": 0.15 * max(0.0, (MIN_SOURCE_COVERAGE - source_cov_for_risk) / MIN_SOURCE_COVERAGE),
        "high_overlap_boundary_risk": 0.0,
        "unresolved_audit_evidence": 0.0,
    }
    if boundary_risk and output_jaccard is not None and output_jaccard >= OVERLAP_HIGH:
        risk_components["high_overlap_boundary_risk"] = 0.12
    if stage == "post_audit" and unresolved_singletons > 0:
        risk_components["unresolved_audit_evidence"] = 0.12

    risk_score = min(1.0, sum(risk_components.values()))
    flags = [name for name, value in risk_components.items() if value > 0]

    unresolved_singleton_gate = singleton_ratio <= 0.05 or (
        stage == "post_audit" and unresolved_singletons == 0
    )
    safe_conditions = [
        confidence is not None and confidence >= CONFIDENCE_THRESHOLD,
        adjusted_chao_missing <= CHAO_MISSING_SAFE,
        unresolved_singleton_gate,
        risk_score < RISK_SAFE,
    ]
    if all(safe_conditions):
        label = SAFE
    elif risk_score >= RISK_UNSAFE or adjusted_chao_missing >= 0.20:
        label = UNSAFE
    else:
        label = AUDIT

    return {
        "stage": stage,
        "label": label,
        "risk_score": risk_score,
        "risk_components": risk_components,
        "flags": flags,
        "signals": {
            "mean_confidence": confidence,
            "agent_count": len(agent_items),
            "observed_unique_items": observed,
            "item_incidences": incidences,
            "singletons_f1": f1,
            "doubletons_f2": f2,
            "singleton_ratio": singleton_ratio,
            "doubleton_ratio": doubleton_ratio,
            "good_turing_missing_mass": gt_missing_mass,
            "chao_unseen_estimate": chao,
            "chao_missing_ratio": chao_missing_ratio,
            "correlation_adjusted_chao_missing_ratio": adjusted_chao_missing,
            "output_jaccard": output_jaccard,
            "source_overlap": source_overlap,
            "effective_exploration_size": eff_size,
            "source_coverage": source_cov,
            "observed_sources": source_stats.get("observed_sources"),
            "source_universe_size": source_stats.get("source_universe_size"),
            "holdout_gain_post_audit_only": holdout_gain,
            "audit_verified_items_post_audit_only": audit_verified_items,
            "unresolved_singletons_post_audit_only": unresolved_singletons,
            "query_path_similarity": "not_logged",
        },
        "thresholds": {
            "theta": THETA,
            "confidence": CONFIDENCE_THRESHOLD,
            "safe_risk_score": RISK_SAFE,
            "unsafe_risk_score": RISK_UNSAFE,
            "safe_adjusted_chao_missing": CHAO_MISSING_SAFE,
            "min_source_coverage": MIN_SOURCE_COVERAGE,
            "high_overlap": OVERLAP_HIGH,
        },
    }


def load_runs(path: Path) -> tuple[str, list[dict[str, Any]]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw.get("task_id", "unknown_task"), [normalize_run(run) for run in raw["runs"]]


def cost_for_runs(base: Path, run_ids: list[str]) -> dict[str, Any]:
    totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "tool_calls": 0,
        "wall_clock_seconds": 0.0,
        "missing_token_logs": 0,
        "missing_tool_call_logs": 0,
        "cost_log_files": [],
    }
    for run_id in run_ids:
        path = base / "run_cost_logs" / f"{run_id}_cost.json"
        if not path.exists():
            totals["missing_token_logs"] += 1
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        totals["cost_log_files"].append(path.name)
        for key in ("input_tokens", "output_tokens"):
            if data.get(key) is None:
                totals["missing_token_logs"] += 1
            else:
                totals[key] += data[key]
        if data.get("tool_calls") is None:
            totals["missing_tool_call_logs"] += 1
        else:
            totals["tool_calls"] += data["tool_calls"]
        if data.get("wall_clock_seconds") is not None:
            totals["wall_clock_seconds"] += data["wall_clock_seconds"]
    return totals


def make_state(
    *,
    base: Path,
    case: CaseSpec,
    task_id: str,
    oracle: set[str],
    source_universe_: set[str],
    state_id: str,
    stage: str,
    runs: list[dict[str, Any]],
    final_items: set[str],
    post_audit_signals: dict[str, Any] | None = None,
) -> dict[str, Any]:
    counts = Counter(item for run in runs for item in run["items"])
    agent_items = [set(run["items"]) for run in runs]
    cert = certificate_rule(
        stage=stage,
        counts=counts,
        confidences=[run["confidence"] for run in runs],
        agent_items=agent_items,
        boundary_risk=case.boundary_risk,
        source_stats=source_coverage(set(counts), source_universe_),
        post_audit_signals=post_audit_signals,
    )
    metrics = score_set(final_items, oracle)
    recall = metrics["recall"]
    precision = metrics["precision"]
    run_ids = [run["run_id"] for run in runs]
    return {
        "state_id": state_id,
        "case_id": case.case_id,
        "task_id": task_id,
        "family": case.family,
        "stage": stage,
        "run_ids": run_ids,
        "reportable": case.reportable,
        "final_item_policy": "raw_union_pre_audit" if stage == "pre_audit" else "audit_augmented_union",
        "metrics": {
            "found": metrics["found"],
            "true_positive": metrics["true_positive"],
            "false_positive": metrics["false_positive"],
            "recall": recall,
            "precision": precision,
            "f1": f1_score(recall, precision),
            "safe_completion_oracle_label": recall >= THETA,
        },
        "certificate": cert,
        "cost": cost_for_runs(base, run_ids),
        "audit_cost": post_audit_signals.get("audit_cost") if post_audit_signals else None,
        "correlation": {
            "nominal_agent_count": len(runs),
            "effective_exploration_size": cert["signals"]["effective_exploration_size"],
            "output_jaccard": cert["signals"]["output_jaccard"],
            "source_overlap": cert["signals"]["source_overlap"],
            "source_coverage": cert["signals"]["source_coverage"],
            "query_path_similarity": "not_logged",
            "marginal_discovery_gain": marginal_gains(agent_items),
            "chao_missing_ratio": cert["signals"]["chao_missing_ratio"],
            "correlation_adjusted_chao_missing_ratio": cert["signals"]["correlation_adjusted_chao_missing_ratio"],
        },
    }


def marginal_gains(agent_items: list[set[str]]) -> list[int]:
    seen: set[str] = set()
    gains = []
    for items in agent_items:
        gains.append(len(items - seen))
        seen |= items
    return gains


def audit_policy(pre_cert: dict[str, Any], g3_runs: list[dict[str, Any]], holdout_runs: list[dict[str, Any]]) -> dict[str, Any]:
    g3_counts = Counter(item for run in g3_runs for item in run["items"])
    singleton_items = {item for item, count in g3_counts.items() if count == 1}
    holdout_items = set().union(*(run["items"] for run in holdout_runs)) if holdout_runs else set()
    actions: list[str] = []
    if pre_cert["label"] in {UNSAFE, AUDIT}:
        if singleton_items:
            actions.append("singleton_audit")
        if holdout_runs:
            actions.append("holdout_audit")
        else:
            actions.append("holdout_audit_todo")
    verified_singletons = singleton_items & holdout_items
    final_items = set(g3_counts) | holdout_items
    return {
        "actions": actions,
        "final_items": final_items,
        "verified_singletons": verified_singletons,
        "unresolved_singletons": singleton_items - verified_singletons,
        "holdout_items": holdout_items,
    }


def evaluate_case(base: Path, case: CaseSpec) -> list[dict[str, Any]]:
    oracle, _ = load_oracle(base / case.oracle_path)
    task_id, runs = load_runs(base / case.runs_path)
    universe = source_universe(base, case)
    by_seed: dict[str, list[dict[str, Any]]] = {}
    holdouts: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        if run["group"] == "G3":
            by_seed.setdefault(run["seed"], []).append(run)
        if run["group"] == "G6":
            holdouts.setdefault(run["seed"], []).append(run)

    states: list[dict[str, Any]] = []
    for seed, g3_runs in sorted(by_seed.items()):
        g3_runs = sorted(g3_runs, key=lambda run: run["run_id"])
        for idx, run in enumerate(g3_runs, start=1):
            states.append(make_state(
                base=base,
                case=case,
                task_id=task_id,
                oracle=oracle,
                source_universe_=universe,
                state_id=f"{case.case_id}_{seed}_pre_g1_agent{idx}",
                stage="pre_audit",
                runs=[run],
                final_items=set(run["items"]),
            ))
        for pair_idx, pair in enumerate(combinations(g3_runs, 2), start=1):
            pair_runs = list(pair)
            states.append(make_state(
                base=base,
                case=case,
                task_id=task_id,
                oracle=oracle,
                source_universe_=universe,
                state_id=f"{case.case_id}_{seed}_pre_g2_pair{pair_idx}",
                stage="pre_audit",
                runs=pair_runs,
                final_items=set().union(*(run["items"] for run in pair_runs)),
            ))
        pre_g3 = make_state(
            base=base,
            case=case,
            task_id=task_id,
            oracle=oracle,
            source_universe_=universe,
            state_id=f"{case.case_id}_{seed}_pre_g3",
            stage="pre_audit",
            runs=g3_runs,
            final_items=set().union(*(run["items"] for run in g3_runs)),
        )
        states.append(pre_g3)
        audit = audit_policy(pre_g3["certificate"], g3_runs, holdouts.get(seed, []))
        if holdouts.get(seed):
            post_runs = g3_runs + holdouts[seed]
            holdout_new = audit["holdout_items"] - set().union(*(run["items"] for run in g3_runs))
            oracle_new = holdout_new & oracle
            states.append(make_state(
                base=base,
                case=case,
                task_id=task_id,
                oracle=oracle,
                source_universe_=universe,
                state_id=f"{case.case_id}_{seed}_post_holdout",
                stage="post_audit",
                runs=post_runs,
                final_items=audit["final_items"],
                post_audit_signals={
                    "audit_verified_items": len(audit["verified_singletons"]),
                    "unresolved_singletons": len(audit["unresolved_singletons"]),
                    "holdout_gain": len(oracle_new) / len(oracle) if oracle else 0.0,
                    "audit_cost": {
                        "audit_actions": len(audit["actions"]),
                        "singleton_candidates": len(audit["verified_singletons"]) + len(audit["unresolved_singletons"]),
                        "holdout_items": len(audit["holdout_items"]),
                    },
                },
            ))
    return states


def baseline_decisions(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cert = state["certificate"]
    signals = cert["signals"]
    label = cert["label"]
    self_reported = signals["mean_confidence"] is not None and signals["mean_confidence"] >= CONFIDENCE_THRESHOLD
    no_new_item = bool(state["correlation"]["marginal_discovery_gain"]) and state["correlation"]["marginal_discovery_gain"][-1] == 0
    chao_only = signals["chao_missing_ratio"] <= CHAO_MISSING_SAFE
    overlap_only = signals["output_jaccard"] is not None and signals["output_jaccard"] >= OVERLAP_HIGH
    decisions = {
        "self_reported_completion": self_reported,
        "confidence_only": self_reported,
        "overlap_only": overlap_only,
        "no_new_item_stopping": no_new_item,
        "raw_union": state["stage"] == "pre_audit",
        "chao_only": chao_only,
        "always_unsafe": False,
        "always_holdout": state["stage"] == "post_audit",
        "proposed_certificate": label == SAFE,
    }
    safe = state["metrics"]["safe_completion_oracle_label"]
    return {
        method: {
            "would_certify_or_stop": would_stop,
            "false_certification": would_stop and not safe,
            "safe_certification": would_stop and safe,
            "abstained_or_required_audit": not would_stop,
        }
        for method, would_stop in decisions.items()
    }


def aggregate(states: list[dict[str, Any]]) -> dict[str, Any]:
    reportable = [state for state in states if state["reportable"]]
    methods = sorted(baseline_decisions(reportable[0])) if reportable else []
    baseline_rows = []
    for method in methods:
        decisions = [baseline_decisions(state)[method] for state in reportable]
        safe_states = [state for state in reportable if state["metrics"]["safe_completion_oracle_label"]]
        baseline_rows.append({
            "method": method,
            "n": len(reportable),
            "certified_or_stopped": sum(1 for row in decisions if row["would_certify_or_stop"]),
            "false_certifications": sum(1 for row in decisions if row["false_certification"]),
            "false_certification_rate": (
                sum(1 for row in decisions if row["false_certification"]) /
                max(1, sum(1 for row in decisions if row["would_certify_or_stop"]))
            ),
            "safe_coverage": (
                sum(1 for state in safe_states if baseline_decisions(state)[method]["would_certify_or_stop"]) /
                len(safe_states) if safe_states else None
            ),
            "abstention_rate": sum(1 for row in decisions if row["abstained_or_required_audit"]) / len(decisions),
        })
    risks = [state["certificate"]["risk_score"] for state in reportable]
    unsafe_labels = [not state["metrics"]["safe_completion_oracle_label"] for state in reportable]
    return {
        "state_count": len(reportable),
        "safe_state_count": sum(1 for state in reportable if state["metrics"]["safe_completion_oracle_label"]),
        "unsafe_state_count": sum(1 for state in reportable if not state["metrics"]["safe_completion_oracle_label"]),
        "mean_post_audit_recall": mean([
            state["metrics"]["recall"] for state in reportable
            if state["stage"] == "post_audit"
        ]),
        "mean_pre_audit_recall": mean([
            state["metrics"]["recall"] for state in reportable
            if state["stage"] == "pre_audit"
        ]),
        "cost_summary": cost_summary(reportable),
        "baseline_metrics": baseline_rows,
        "auroc": auroc(risks, unsafe_labels),
        "auprc": auprc(risks, unsafe_labels),
        "risk_coverage_curve": risk_coverage_curve(reportable),
    }


def cost_summary(states: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "input_tokens_logged": sum(state["cost"]["input_tokens"] for state in states),
        "output_tokens_logged": sum(state["cost"]["output_tokens"] for state in states),
        "tool_calls_logged": sum(state["cost"]["tool_calls"] for state in states),
        "wall_clock_seconds_logged": sum(state["cost"]["wall_clock_seconds"] for state in states),
        "states_with_missing_token_logs": sum(1 for state in states if state["cost"]["missing_token_logs"] > 0),
        "states_with_missing_tool_call_logs": sum(1 for state in states if state["cost"]["missing_tool_call_logs"] > 0),
        "post_audit_states": sum(1 for state in states if state["stage"] == "post_audit"),
        "post_audit_actions_logged": sum(
            (state.get("audit_cost") or {}).get("audit_actions", 0)
            for state in states
        ),
        "post_audit_holdout_items_reviewed": sum(
            (state.get("audit_cost") or {}).get("holdout_items", 0)
            for state in states
        ),
        "post_audit_singleton_candidates": sum(
            (state.get("audit_cost") or {}).get("singleton_candidates", 0)
            for state in states
        ),
    }


def auroc(scores: list[float], labels: list[bool]) -> float | None:
    positives = [(score, label) for score, label in zip(scores, labels) if label]
    negatives = [(score, label) for score, label in zip(scores, labels) if not label]
    if not positives or not negatives:
        return None
    wins = 0.0
    total = len(positives) * len(negatives)
    for pos_score, _ in positives:
        for neg_score, _ in negatives:
            if pos_score > neg_score:
                wins += 1
            elif pos_score == neg_score:
                wins += 0.5
    return wins / total


def auprc(scores: list[float], labels: list[bool]) -> float | None:
    if not any(labels):
        return None
    ranked = sorted(zip(scores, labels), reverse=True)
    tp = 0
    fp = 0
    points = []
    total_pos = sum(labels)
    for _, label in ranked:
        if label:
            tp += 1
        else:
            fp += 1
        precision = tp / (tp + fp)
        recall = tp / total_pos
        points.append((recall, precision))
    area = 0.0
    prev_recall = 0.0
    for recall, precision in points:
        area += (recall - prev_recall) * precision
        prev_recall = recall
    return area


def risk_coverage_curve(states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for threshold in [0.10, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60]:
        certified = [state for state in states if state["certificate"]["risk_score"] <= threshold]
        if not certified:
            rows.append({"risk_threshold": threshold, "coverage": 0.0, "false_certification_rate": None})
            continue
        false_cert = sum(1 for state in certified if not state["metrics"]["safe_completion_oracle_label"])
        rows.append({
            "risk_threshold": threshold,
            "coverage": len(certified) / len(states),
            "false_certification_rate": false_cert / len(certified),
        })
    return rows


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Completion Certificate v1 Results",
        "",
        f"Generated at: `{summary['run_log']['ended_at']}`",
        "",
        "## Rule",
        "",
        "Pre-audit certificate uses exploration-only signals: confidence, output overlap, singleton/doubleton counts, Good-Turing missing mass, Chao unseen mass, source coverage, and effective exploration size. Holdout gain is only logged in post-audit states.",
        "",
        "Labels: `SAFE-TO-STOP`, `UNSAFE-TO-STOP`, `REQUIRES-AUDIT`.",
        "",
        "## Aggregate Metrics",
        "",
        f"- Reportable states: `{summary['aggregate']['state_count']}`",
        f"- Safe states by oracle recall threshold: `{summary['aggregate']['safe_state_count']}`",
        f"- Unsafe states by oracle recall threshold: `{summary['aggregate']['unsafe_state_count']}`",
        f"- Risk-score AUROC for unsafe-state detection: `{summary['aggregate']['auroc']}`",
        f"- Risk-score AUPRC for unsafe-state detection: `{summary['aggregate']['auprc']}`",
        f"- Mean pre-audit recall: `{summary['aggregate']['mean_pre_audit_recall']}`",
        f"- Mean post-audit recall: `{summary['aggregate']['mean_post_audit_recall']}`",
        "",
        "The current v1 rule is intentionally conservative. A low false-certification rate with low safe coverage should be interpreted as a risk detector, not as a solved stopping rule.",
        "",
        "## Logged Cost Summary",
        "",
        "Token and wall-clock logs are incomplete for older T4 runs; missing fields are counted rather than imputed.",
        "",
        "```json",
        json.dumps(summary["aggregate"]["cost_summary"], indent=2),
        "```",
        "",
        "## Stopping Baselines",
        "",
        "| method | n | stopped | false certs | false cert rate | safe coverage | abstention rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary["aggregate"]["baseline_metrics"]:
        lines.append(
            "| {method} | {n} | {stopped} | {false} | {fcr} | {safe_cov} | {abstain} |".format(
                method=row["method"],
                n=row["n"],
                stopped=row["certified_or_stopped"],
                false=row["false_certifications"],
                fcr=fmt(row["false_certification_rate"]),
                safe_cov=fmt(row["safe_coverage"]),
                abstain=fmt(row["abstention_rate"]),
            )
        )
    lines.extend([
        "",
        "## States",
        "",
        "| state | stage | recall | precision | f1 | oracle safe | label | risk | output J | source overlap | eff size | adj Chao |",
        "| --- | --- | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for state in summary["states"]:
        cert = state["certificate"]
        sig = cert["signals"]
        lines.append(
            "| {state_id} | {stage} | {recall} | {precision} | {f1} | {safe} | {label} | {risk} | {j} | {src} | {eff} | {adj} |".format(
                state_id=state["state_id"],
                stage=state["stage"],
                recall=fmt(state["metrics"]["recall"]),
                precision=fmt(state["metrics"]["precision"]),
                f1=fmt(state["metrics"]["f1"]),
                safe=state["metrics"]["safe_completion_oracle_label"],
                label=cert["label"],
                risk=fmt(cert["risk_score"]),
                j=fmt(sig["output_jaccard"]),
                src=fmt(sig["source_overlap"]),
                eff=fmt(sig["effective_exploration_size"]),
                adj=fmt(sig["correlation_adjusted_chao_missing_ratio"]),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path("experiments/false_convergence_pilot"))
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("experiments/false_convergence_pilot/protocol_outputs/completion_certificate_v1_results.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("experiments/false_convergence_pilot/reports/protocol/COMPLETION_CERTIFICATE_V1_RESULTS.md"),
    )
    args = parser.parse_args()
    started = datetime.now(timezone.utc)
    states: list[dict[str, Any]] = []
    for case in CASES:
        runs_path = args.base / case.runs_path
        oracle_path = args.base / case.oracle_path
        if runs_path.exists() and oracle_path.exists():
            states.extend(evaluate_case(args.base, case))
    ended = datetime.now(timezone.utc)
    summary = {
        "rule_version": "completion_certificate_v1_decoupled",
        "labels": [SAFE, UNSAFE, AUDIT],
        "thresholds": {
            "theta": THETA,
            "confidence": CONFIDENCE_THRESHOLD,
            "overlap_high": OVERLAP_HIGH,
            "safe_risk_score": RISK_SAFE,
            "unsafe_risk_score": RISK_UNSAFE,
            "safe_adjusted_chao_missing": CHAO_MISSING_SAFE,
            "min_source_coverage": MIN_SOURCE_COVERAGE,
        },
        "run_log": {
            "started_at": started.isoformat(),
            "ended_at": ended.isoformat(),
            "wall_clock_seconds": (ended - started).total_seconds(),
            "input_files": [case.runs_path for case in CASES],
            "oracle_files_for_offline_scoring_only": [case.oracle_path for case in CASES],
        },
        "aggregate": aggregate(states),
        "states": states,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(summary, args.out_md)


if __name__ == "__main__":
    main()
