from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[2]
IN = ROOT / "analysis" / "coverage_geometry_diagnostics" / "results" / "run_level_summary.csv"
OUT = ROOT / "analysis" / "research_object_geometry"
RESULTS = OUT / "results"
DOCS = OUT / "docs"


METRICS = [
    "mean_pairwise_item_jaccard_from_score",
    "mean_pairwise_source_jaccard",
    "source_coverage_count",
    "file_coverage_count",
    "singleton_ratio_from_score",
    "source_pairwise_cosine",
    "source_normalized_effective_rank",
    "file_entropy_effective_rank",
    "source_logdet_volume",
    "source_marginal_logdet_gain",
    "source_concentration_entropy",
    "source_concentration_hhi",
    "source_concentration_gini",
    "mean_confidence",
]


def ensure_dirs():
    RESULTS.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)


def corr(x, y):
    mask = x.notna() & y.notna()
    if mask.sum() < 4:
        return np.nan, np.nan, int(mask.sum())
    if x[mask].nunique() < 2 or y[mask].nunique() < 2:
        return np.nan, np.nan, int(mask.sum())
    rho, p = spearmanr(x[mask], y[mask])
    return float(rho), float(p), int(mask.sum())


def metric_recall_table(df):
    rows = []
    y = pd.to_numeric(df["union_recall"], errors="coerce")
    for metric in METRICS:
        x = pd.to_numeric(df[metric], errors="coerce")
        rho, p, n = corr(x, y)
        rows.append({"scope": "global", "repository": "all", "metric": metric, "n": n, "spearman_with_recall": rho, "p_value": p})
        for repo, sub in df.groupby("repository"):
            sx = pd.to_numeric(sub[metric], errors="coerce")
            sy = pd.to_numeric(sub["union_recall"], errors="coerce")
            rrho, rp, rn = corr(sx, sy)
            rows.append({"scope": "within_repo", "repository": repo, "metric": metric, "n": rn, "spearman_with_recall": rrho, "p_value": rp})
    return pd.DataFrame(rows)


def condition_summary(df):
    cols = [
        "union_recall",
        "source_normalized_effective_rank",
        "source_logdet_volume",
        "source_marginal_logdet_gain",
        "source_concentration_hhi",
        "mean_pairwise_source_jaccard",
        "singleton_ratio_from_score",
    ]
    return (
        df.groupby(["repository", "condition"])[cols]
        .agg(["count", "mean", "std"])
        .reset_index()
    )


def label_counts(df):
    rows = []
    for theta, col in [
        ("0.90", "false_completion_theta_090"),
        ("0.95", "false_completion_theta_095"),
        ("1.00", "false_completion_theta_100"),
    ]:
        labels = df[col].astype(bool)
        rows.append(
            {
                "theta": theta,
                "false_completion": int(labels.sum()),
                "not_false_completion": int((~labels).sum()),
                "label_has_two_classes": bool(labels.nunique() == 2),
            }
        )
    return pd.DataFrame(rows)


def stability_table(corr_df):
    rows = []
    for metric, sub in corr_df[corr_df["scope"] == "within_repo"].groupby("metric"):
        vals = sub["spearman_with_recall"].dropna()
        if vals.empty:
            rows.append({"metric": metric, "repos_with_signal": 0, "positive_repos": 0, "negative_repos": 0, "sign_consistent": False})
            continue
        pos = int((vals > 0).sum())
        neg = int((vals < 0).sum())
        rows.append(
            {
                "metric": metric,
                "repos_with_signal": int(len(vals)),
                "positive_repos": pos,
                "negative_repos": neg,
                "sign_consistent": bool(pos == len(vals) or neg == len(vals)),
            }
        )
    return pd.DataFrame(rows)


def write_report(df, labels, corr_df, stable_df, cond_df):
    global_corr = corr_df[corr_df["scope"] == "global"].copy()
    global_corr = global_corr.sort_values("spearman_with_recall", key=lambda s: s.abs(), ascending=False, na_position="last")
    top_global = global_corr.head(8)
    stable = stable_df.sort_values(["sign_consistent", "repos_with_signal"], ascending=[False, False]).head(8)

    all_false = labels["not_false_completion"].sum() == 0
    has_action_logs = False

    lines = [
        "# Geometry-Control Question Validation",
        "",
        "Question:",
        "",
        "> Is multi-agent workflow false stopping controlled by a stable coverage-geometry quantity?",
        "",
        "This report uses existing historical logs only as read-only observations. It does not use the archived `liudang1/` direction as the new research line, and it does not claim a method or phase transition.",
        "",
        "## Identification Checks",
        "",
        labels.to_markdown(index=False),
        "",
        f"- Safe/false discriminative test available: `{not all_false}`.",
        f"- Action-trajectory geometry available: `{has_action_logs}`.",
        "- Current logs contain source/item ledger geometry, but not query/action/tool trajectories.",
        "",
        "## Continuous Recall Association",
        "",
        "Because all inspected states are false completions at high-recall thresholds, we cannot test safe-vs-false separation. As a weaker diagnostic, we ask whether geometry variables correlate with the degree of union recall.",
        "",
        top_global.to_markdown(index=False),
        "",
        "Caution: the strongest global association is `source_coverage_count`, but it has no usable within-repository signal in this slice. That makes it likely to be a repository/task-size confound rather than a stable control variable.",
        "",
        "## Cross-Repository Sign Stability",
        "",
        stable.to_markdown(index=False),
        "",
        "## Condition-Level Observation",
        "",
        "The condition table is saved as CSV because it is wide. It should be read as descriptive only, not as causal evidence.",
        "",
        "## Verdict",
        "",
        "**Current answer: not verified.**",
        "",
        "The existing data show that false completion is real in these historical runs, but they do not verify that a stable coverage-geometry quantity controls it.",
        "",
        "Reasons:",
        "",
        "- There is no safe-completion comparison class at theta 0.90, 0.95, or 1.00.",
        "- The logs lack action trajectory fields, so source-path geometry is only a proxy.",
        "- Continuous correlations with recall are exploratory and cannot establish safe-stopping control.",
        "- The strongest global association is confounded by repository/task differences; within-repository variation is the relevant test.",
        "- A geometry quantity must beat simple source coverage/overlap baselines across repositories before it can become the research core.",
        "",
        "## Minimum Next Validation",
        "",
        "To verify the question rather than only motivate it, run a small new diagnostic with:",
        "",
        "- at least two repositories or task types;",
        "- both false-completion states and safe or near-safe states;",
        "- per-round query/action/tool/source-route logs;",
        "- homogeneous, route-partitioned, and extended/audited conditions;",
        "- a challenger aimed at weak or residual coverage regions;",
        "- oracle labels used only after the blind runs finish.",
        "",
        "The geometry line becomes credible only if one runtime-computable coverage variable predicts unsafe stopping better than source coverage, overlap, no-new-item rounds, and confidence, and the pattern repeats across tasks.",
    ]
    (DOCS / "geometry_control_validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ensure_dirs()
    df = pd.read_csv(IN)
    labels = label_counts(df)
    corr_df = metric_recall_table(df)
    stable_df = stability_table(corr_df)
    cond_df = condition_summary(df)

    labels.to_csv(RESULTS / "label_availability.csv", index=False)
    corr_df.to_csv(RESULTS / "geometry_metric_recall_correlations.csv", index=False)
    stable_df.to_csv(RESULTS / "cross_repo_sign_stability.csv", index=False)
    cond_df.to_csv(RESULTS / "condition_level_descriptive_stats.csv", index=False)
    write_report(df, labels, corr_df, stable_df, cond_df)
    print(f"Wrote validation report to {DOCS / 'geometry_control_validation_report.md'}")


if __name__ == "__main__":
    main()
