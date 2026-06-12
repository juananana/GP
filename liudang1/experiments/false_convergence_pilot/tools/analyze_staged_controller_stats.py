#!/usr/bin/env python3
"""Seed-clustered bootstrap summaries for online audit-controller runs."""

from __future__ import annotations

import csv
import random
import statistics
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "false_convergence_pilot"
OUT_DIR = BASE / "reports" / "stats"
OUT_MD = OUT_DIR / "STAGED_CONTROLLER_BOOTSTRAP_AND_PAIRED_TESTS.md"
OUT_CSV = OUT_DIR / "STAGED_CONTROLLER_BOOTSTRAP_AND_PAIRED_TESTS.csv"
BOOTSTRAPS = 5000
RNG = random.Random(20260611)

INPUTS = {
    "Requests": BASE
    / "online_audit_controller"
    / "T5_requests_tls"
    / "audit_policy_eval"
    / "ONLINE_AUDIT_POLICY_RESULTS.csv",
    "Click": BASE
    / "online_heldout_click_staged_controller"
    / "audit_policy_eval"
    / "CLICK_HELDOUT_STAGED_RESULTS.csv",
    "itsdangerous": BASE
    / "online_external_itsdangerous_staged_controller"
    / "audit_policy_eval"
    / "T6_ITSDANGEROUS_STAGED_RESULTS.csv",
}

POLICY_ORDER = [
    "no_audit",
    "singleton_audit",
    "source_partitioned_review",
    "staged_controller",
    "always_holdout",
]
COMPARATORS = ["singleton_audit", "source_partitioned_review", "always_holdout"]


def fnum(row: dict[str, str], key: str, default: float = 0.0) -> float:
    value = row.get(key, "")
    if value in ("", "None", None):
        return default
    return float(value)


def load_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for dataset, path in INPUTS.items():
        if not path.exists():
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            for raw in csv.DictReader(handle):
                policy = raw["policy"]
                if policy not in POLICY_ORDER:
                    continue
                recall = fnum(raw, "post_recall")
                precision = fnum(raw, "post_precision")
                f1 = 0.0 if recall + precision == 0 else 2 * recall * precision / (recall + precision)
                row = {
                    "dataset": dataset,
                    "seed": raw["seed"],
                    "condition": raw.get("condition", "NA"),
                    "cluster": f"{dataset}:{raw['seed']}",
                    "pair": f"{dataset}:{raw['seed']}:{raw.get('condition', 'NA')}",
                    "policy": policy,
                    "pre_recall": fnum(raw, "pre_recall"),
                    "recall": recall,
                    "precision": precision,
                    "f1": f1,
                    "recovered_tp": fnum(raw, "recovered_tp"),
                    "introduced_fp": fnum(raw, "introduced_fp"),
                    "audit_tokens": fnum(raw, "audit_tokens"),
                    "end_to_end_tokens": fnum(raw, "end_to_end_tokens", 0.0),
                    "wall_clock": fnum(raw, "end_to_end_wall_clock_seconds", fnum(raw, "audit_wall_clock_seconds", 0.0)),
                    "decision": raw.get("decision", ""),
                    "actual_safe": raw.get("actual_safe", ""),
                    "false_certification": 1.0 if raw.get("false_certification") == "True" else 0.0,
                    "abstained": 1.0 if raw.get("decision") == "abstain" else 0.0,
                }
                rows.append(row)
    return rows


def mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = (len(ordered) - 1) * q
    lo = int(idx)
    hi = min(lo + 1, len(ordered) - 1)
    frac = idx - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac


def cluster_bootstrap(rows: list[dict[str, object]], metric: str) -> tuple[float, float, float]:
    clusters: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        clusters[str(row["cluster"])].append(row)
    keys = list(clusters)
    observed = mean([float(row[metric]) for row in rows])
    samples: list[float] = []
    for _ in range(BOOTSTRAPS):
        sample_rows: list[dict[str, object]] = []
        for key in (RNG.choice(keys) for _ in keys):
            sample_rows.extend(clusters[key])
        samples.append(mean([float(row[metric]) for row in sample_rows]))
    return observed, percentile(samples, 0.025), percentile(samples, 0.975)


def paired_rows(rows: list[dict[str, object]], comparator: str) -> list[dict[str, object]]:
    by_pair_policy: dict[tuple[str, str], dict[str, object]] = {}
    for row in rows:
        by_pair_policy[(str(row["pair"]), str(row["policy"]))] = row
    paired: list[dict[str, object]] = []
    pairs = sorted({str(row["pair"]) for row in rows})
    for pair in pairs:
        staged = by_pair_policy.get((pair, "staged_controller"))
        base = by_pair_policy.get((pair, comparator))
        if staged is None or base is None:
            continue
        paired.append({
            "cluster": staged["cluster"],
            "dataset": staged["dataset"],
            "pair": pair,
            "recall_diff": float(staged["recall"]) - float(base["recall"]),
            "precision_diff": float(staged["precision"]) - float(base["precision"]),
            "f1_diff": float(staged["f1"]) - float(base["f1"]),
            "audit_token_diff": float(staged["audit_tokens"]) - float(base["audit_tokens"]),
        })
    return paired


def paired_bootstrap(paired: list[dict[str, object]], metric: str) -> tuple[float, float, float]:
    clusters: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in paired:
        clusters[str(row["cluster"])].append(row)
    keys = list(clusters)
    observed = mean([float(row[metric]) for row in paired])
    samples: list[float] = []
    for _ in range(BOOTSTRAPS):
        sample_rows: list[dict[str, object]] = []
        for key in (RNG.choice(keys) for _ in keys):
            sample_rows.extend(clusters[key])
        samples.append(mean([float(row[metric]) for row in sample_rows]))
    return observed, percentile(samples, 0.025), percentile(samples, 0.975)


def sign_flip_pvalue(diffs: list[float]) -> float:
    if not diffs:
        return 1.0
    observed = abs(mean(diffs))
    count = 0
    trials = min(20000, 2 ** len(diffs))
    if 2 ** len(diffs) <= 20000:
        for mask in range(2 ** len(diffs)):
            sample = [diff if (mask >> i) & 1 else -diff for i, diff in enumerate(diffs)]
            if abs(mean(sample)) >= observed - 1e-12:
                count += 1
        return count / (2 ** len(diffs))
    for _ in range(trials):
        sample = [diff if RNG.random() < 0.5 else -diff for diff in diffs]
        if abs(mean(sample)) >= observed - 1e-12:
            count += 1
    return count / trials


def fmt(value: float) -> str:
    return f"{value:.3f}"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows()

    csv_rows: list[dict[str, object]] = []
    lines = [
        "# Staged Controller Bootstrap and Paired Tests",
        "",
        f"Inputs: {', '.join(dataset for dataset, path in INPUTS.items() if path.exists())}.",
        f"Bootstrap: {BOOTSTRAPS} resamples over dataset/seed clusters.",
        "",
        "Requests rows are included in policy summaries but excluded from staged paired tests because that development run did not contain a frozen staged-controller arm.",
        "",
        "## Policy Means with Seed-Clustered 95% CI",
        "",
        "| dataset | policy | n | recall mean [95% CI] | precision mean [95% CI] | F1 mean [95% CI] | audit tokens | recovered TP | introduced FP | FCR among certified | safe coverage | abstention |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for dataset in INPUTS:
        for policy in POLICY_ORDER:
            subset = [row for row in rows if row["dataset"] == dataset and row["policy"] == policy]
            if not subset:
                continue
            recall = cluster_bootstrap(subset, "recall")
            precision = cluster_bootstrap(subset, "precision")
            f1 = cluster_bootstrap(subset, "f1")
            audit_tokens = mean([float(row["audit_tokens"]) for row in subset])
            recovered_tp = mean([float(row["recovered_tp"]) for row in subset])
            introduced_fp = mean([float(row["introduced_fp"]) for row in subset])
            certified = [row for row in subset if row["decision"] == "safe_to_stop"]
            safe = [row for row in subset if row["actual_safe"] == "True"]
            fcr = (
                mean([float(row["false_certification"]) for row in certified])
                if certified
                else None
            )
            safe_coverage = (
                mean([1.0 if row["decision"] == "safe_to_stop" else 0.0 for row in safe])
                if safe
                else 0.0
            )
            abstention = (
                mean([float(row["abstained"]) for row in subset])
                if any(str(row["decision"]) for row in subset)
                else None
            )
            fcr_text = "NA" if fcr is None else fmt(fcr)
            abstention_text = "NA" if abstention is None else fmt(abstention)
            lines.append(
                f"| {dataset} | {policy} | {len(subset)} | "
                f"{fmt(recall[0])} [{fmt(recall[1])}, {fmt(recall[2])}] | "
                f"{fmt(precision[0])} [{fmt(precision[1])}, {fmt(precision[2])}] | "
                f"{fmt(f1[0])} [{fmt(f1[1])}, {fmt(f1[2])}] | "
                f"{audit_tokens:.0f} | {recovered_tp:.1f} | {introduced_fp:.1f} | "
                f"{fcr_text} | {fmt(safe_coverage)} | {abstention_text} |"
            )
            csv_rows.append({
                "section": "policy_mean",
                "dataset": dataset,
                "policy": policy,
                "n": len(subset),
                "recall": recall[0],
                "recall_ci_low": recall[1],
                "recall_ci_high": recall[2],
                "precision": precision[0],
                "precision_ci_low": precision[1],
                "precision_ci_high": precision[2],
                "f1": f1[0],
                "f1_ci_low": f1[1],
                "f1_ci_high": f1[2],
                "audit_tokens": audit_tokens,
                "recovered_tp": recovered_tp,
                "introduced_fp": introduced_fp,
                "fcr": fcr,
                "safe_coverage": safe_coverage,
                "abstention": abstention,
            })

    lines += [
        "",
        "## Paired Staged-Controller Comparisons",
        "",
        "| comparator | pairs | datasets | recall diff [95% CI] | precision diff [95% CI] | F1 diff [95% CI] | audit-token diff [95% CI] | sign-flip p, recall |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    staged_rows = [row for row in rows if row["dataset"] in {"Click", "itsdangerous"}]
    for comparator in COMPARATORS:
        paired = paired_rows(staged_rows, comparator)
        recall = paired_bootstrap(paired, "recall_diff")
        precision = paired_bootstrap(paired, "precision_diff")
        f1 = paired_bootstrap(paired, "f1_diff")
        audit_tokens = paired_bootstrap(paired, "audit_token_diff")
        pvalue = sign_flip_pvalue([float(row["recall_diff"]) for row in paired])
        datasets = ",".join(sorted({str(row["dataset"]) for row in paired}))
        lines.append(
            f"| {comparator} | {len(paired)} | {datasets} | "
            f"{fmt(recall[0])} [{fmt(recall[1])}, {fmt(recall[2])}] | "
            f"{fmt(precision[0])} [{fmt(precision[1])}, {fmt(precision[2])}] | "
            f"{fmt(f1[0])} [{fmt(f1[1])}, {fmt(f1[2])}] | "
            f"{audit_tokens[0]:.0f} [{audit_tokens[1]:.0f}, {audit_tokens[2]:.0f}] | "
            f"{pvalue:.3f} |"
        )
        csv_rows.append({
            "section": "paired_diff",
            "dataset": datasets,
            "policy": f"staged_vs_{comparator}",
            "n": len(paired),
            "recall": recall[0],
            "recall_ci_low": recall[1],
            "recall_ci_high": recall[2],
            "precision": precision[0],
            "precision_ci_low": precision[1],
            "precision_ci_high": precision[2],
            "f1": f1[0],
            "f1_ci_low": f1[1],
            "f1_ci_high": f1[2],
            "audit_tokens": audit_tokens[0],
            "audit_tokens_ci_low": audit_tokens[1],
            "audit_tokens_ci_high": audit_tokens[2],
            "p_recall_sign_flip": pvalue,
        })

    lines += [
        "",
        "Interpretation: the paired tests are descriptive at this size. They test whether the frozen staged controller improves recall over the corresponding baseline under seed-clustered resampling; they do not justify retuning the controller on these data.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = sorted({key for row in csv_rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
    print(OUT_MD)


if __name__ == "__main__":
    main()
