#!/usr/bin/env python3
"""Plot online audit-policy recall/cost tradeoff."""

from __future__ import annotations

import csv
from pathlib import Path
from statistics import mean, pstdev

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "false_convergence_pilot" / "online_audit_controller" / "T5_requests_tls" / "audit_policy_eval" / "ONLINE_AUDIT_POLICY_RESULTS.csv"
OUT = ROOT.parent / "papers" / "aaai_false_convergence" / "figures" / "online_audit_policy_pareto.pdf"
SUMMARY = ROOT / "false_convergence_pilot" / "online_audit_controller" / "T5_requests_tls" / "audit_policy_eval" / "ONLINE_AUDIT_POLICY_FIGURE_SUMMARY.csv"

ORDER = [
    "no_audit",
    "random_holdout",
    "singleton_audit",
    "boundary_focused_holdout",
    "source_partitioned_review",
    "risk_triggered_audit",
    "always_holdout",
]

LABELS = {
    "no_audit": "No audit",
    "random_holdout": "Random",
    "singleton_audit": "Singleton",
    "boundary_focused_holdout": "Boundary",
    "source_partitioned_review": "Source-part.",
    "risk_triggered_audit": "Risk-triggered",
    "always_holdout": "Always",
}


def load_rows() -> list[dict[str, float | str]]:
    rows = []
    with RESULTS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append({
                "policy": row["policy"],
                "post_recall": float(row["post_recall"]),
                "audit_tokens": float(row["audit_tokens"]),
                "recovered_tp": float(row["recovered_tp"]),
            })
    return rows


def main() -> None:
    rows = load_rows()
    grouped = {policy: [row for row in rows if row["policy"] == policy] for policy in ORDER}
    summary_rows = []
    for policy in ORDER:
        subset = grouped[policy]
        recalls = [float(row["post_recall"]) for row in subset]
        tokens = [float(row["audit_tokens"]) / 1000 for row in subset]
        recovered = [float(row["recovered_tp"]) for row in subset]
        summary_rows.append({
            "policy": policy,
            "mean_recall": mean(recalls),
            "sd_recall": pstdev(recalls),
            "mean_tokens_k": mean(tokens),
            "sd_tokens_k": pstdev(tokens),
            "mean_recovered_tp": mean(recovered),
        })

    plt.rcParams.update({
        "font.size": 8,
        "axes.labelsize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
    })
    fig, ax = plt.subplots(figsize=(3.35, 2.25))
    colors = {
        "no_audit": "#4D4D4D",
        "random_holdout": "#6AA84F",
        "singleton_audit": "#3C78D8",
        "boundary_focused_holdout": "#E69138",
        "source_partitioned_review": "#8E7CC3",
        "risk_triggered_audit": "#CC0000",
        "always_holdout": "#666666",
    }
    for row in summary_rows:
        policy = row["policy"]
        ax.errorbar(
            row["mean_tokens_k"],
            row["mean_recall"],
            xerr=row["sd_tokens_k"],
            yerr=row["sd_recall"],
            fmt="o",
            ms=4.5,
            lw=0.9,
            capsize=2,
            color=colors[policy],
            label=LABELS[policy],
        )
    ax.axhline(0.95, color="#999999", lw=0.8, linestyle="--")
    ax.text(2, 0.956, "target 0.95", color="#666666", fontsize=7, va="bottom")
    ax.set_xlabel("Audit tokens (k)")
    ax.set_ylabel("Post-audit recall")
    ax.set_xlim(left=-5)
    ax.set_ylim(0.45, 0.82)
    ax.grid(True, color="#E6E6E6", linewidth=0.6)
    ax.legend(loc="lower right", frameon=False, ncol=1, handletextpad=0.2)
    fig.tight_layout(pad=0.4)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT)
    with SUMMARY.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)
    print(OUT)


if __name__ == "__main__":
    main()
