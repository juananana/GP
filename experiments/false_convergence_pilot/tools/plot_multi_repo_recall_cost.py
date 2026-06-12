#!/usr/bin/env python3
"""Build the multi-repository online recall-cost figure for the paper."""

from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "false_convergence_pilot"
PAPER_FIG = ROOT.parent / "papers" / "aaai_false_convergence" / "figures" / "multi_repo_recall_cost.pdf"

INPUTS = [
    (
        "Requests",
        BASE / "online_audit_controller" / "T5_requests_tls" / "audit_policy_eval" / "ONLINE_AUDIT_POLICY_RESULTS.csv",
    ),
    (
        "Click",
        BASE / "online_heldout_click_staged_controller" / "audit_policy_eval" / "CLICK_HELDOUT_STAGED_RESULTS.csv",
    ),
    (
        "itsdangerous",
        BASE / "online_external_itsdangerous_staged_controller" / "audit_policy_eval" / "T6_ITSDANGEROUS_STAGED_RESULTS.csv",
    ),
]

POLICIES = [
    "no_audit",
    "singleton_audit",
    "source_partitioned_review",
    "staged_controller",
    "always_holdout",
]
LABELS = {
    "no_audit": "No audit",
    "singleton_audit": "Singleton",
    "source_partitioned_review": "Source review",
    "staged_controller": "Staged",
    "always_holdout": "Always",
}
MARKERS = {
    "no_audit": "o",
    "singleton_audit": "s",
    "source_partitioned_review": "^",
    "staged_controller": "D",
    "always_holdout": "X",
}


def fnum(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    return 0.0 if value in ("", "None", None) else float(value)


def load(path: Path) -> dict[str, list[dict[str, float]]]:
    grouped: dict[str, list[dict[str, float]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            policy = row["policy"]
            if policy not in POLICIES:
                continue
            grouped[policy].append({
                "recall": fnum(row, "post_recall"),
                "tokens": fnum(row, "audit_tokens") / 1000.0,
            })
    return grouped


def stderr(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0
    return statistics.stdev(values) / (len(values) ** 0.5)


def main() -> None:
    plt.rcParams.update({
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "legend.fontsize": 7,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.2), sharey=True)
    for ax, (title, path) in zip(axes, INPUTS):
        grouped = load(path)
        for policy in POLICIES:
            rows = grouped.get(policy, [])
            if not rows:
                continue
            recalls = [row["recall"] for row in rows]
            tokens = [row["tokens"] for row in rows]
            ax.errorbar(
                statistics.mean(tokens),
                statistics.mean(recalls),
                xerr=stderr(tokens),
                yerr=stderr(recalls),
                marker=MARKERS[policy],
                markersize=4.5,
                linewidth=0.9,
                capsize=2,
                label=LABELS[policy],
            )
        ax.axhline(0.95, color="0.55", linestyle="--", linewidth=0.8)
        ax.set_title(title)
        ax.set_xlabel("audit tokens (k)")
        ax.grid(True, linewidth=0.3, alpha=0.35)
    axes[0].set_ylabel("post-audit recall")
    handles, labels = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, -0.08))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    PAPER_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(PAPER_FIG)
    print(PAPER_FIG)


if __name__ == "__main__":
    main()
