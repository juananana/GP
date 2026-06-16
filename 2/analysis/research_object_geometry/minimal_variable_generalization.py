from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis" / "research_object_geometry"
RESULTS = OUT / "results"
DOCS = OUT / "docs"
IN = RESULTS / "controlled_geometry_v2_runs.csv"


FEATURE_SETS = {
    "coverage_gini": ["coverage_gini"],
    "coverage_ratio": ["source_coverage_ratio"],
    "effective_rank": ["source_normalized_effective_rank"],
    "stopped_round": ["stopped_round"],
    "gini_plus_coverage": ["coverage_gini", "source_coverage_ratio"],
    "gini_plus_erank": ["coverage_gini", "source_normalized_effective_rank"],
    "coverage_plus_erank": ["source_coverage_ratio", "source_normalized_effective_rank"],
    "minimal_three": ["coverage_gini", "source_coverage_ratio", "source_normalized_effective_rank"],
}


def evaluate(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    y = df["false_completion"].astype(int).to_numpy()
    for name, cols in FEATURE_SETS.items():
        x = df[cols].astype(float)
        mask = x.notna().all(axis=1)
        if mask.sum() < 8 or len(np.unique(y[mask])) < 2:
            rows.append({"feature_set": name, "scope": "global", "heldout_n_strata": "none", "n": int(mask.sum()), "auroc": np.nan})
            continue
        model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced"))
        model.fit(x[mask], y[mask])
        score = model.predict_proba(x[mask])[:, 1]
        rows.append({"feature_set": name, "scope": "global_in_sample", "heldout_n_strata": "none", "n": int(mask.sum()), "auroc": roc_auc_score(y[mask], score)})

        for heldout in sorted(df["n_strata"].unique()):
            train = mask & (df["n_strata"] != heldout)
            test = mask & (df["n_strata"] == heldout)
            if train.sum() < 8 or test.sum() < 8 or len(np.unique(y[train])) < 2 or len(np.unique(y[test])) < 2:
                auc = np.nan
            else:
                model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced"))
                model.fit(x[train], y[train])
                score = model.predict_proba(x[test])[:, 1]
                auc = roc_auc_score(y[test], score)
            rows.append({"feature_set": name, "scope": "leave_world_out", "heldout_n_strata": heldout, "n": int(test.sum()), "auroc": auc})
    return pd.DataFrame(rows)


def summarize(eval_df: pd.DataFrame) -> pd.DataFrame:
    loo = eval_df[eval_df["scope"] == "leave_world_out"].copy()
    return (
        loo.groupby("feature_set")
        .agg(mean_leave_world_auroc=("auroc", "mean"), min_leave_world_auroc=("auroc", "min"), folds=("auroc", "count"))
        .reset_index()
        .sort_values(["mean_leave_world_auroc", "min_leave_world_auroc"], ascending=False)
    )


def write_report(eval_df: pd.DataFrame, summary: pd.DataFrame) -> None:
    global_df = eval_df[eval_df["scope"] == "global_in_sample"].sort_values("auroc", ascending=False)
    lines = [
        "# Minimal Variable Generalization Test",
        "",
        "Purpose: avoid inventing unnecessary geometry variables. We test whether coverage localization alone generalizes across simulated worlds, and whether adding coverage ratio or effective rank actually helps.",
        "",
        "## Global In-Sample AUROC",
        "",
        global_df.to_markdown(index=False),
        "",
        "## Leave-World-Out AUROC",
        "",
        summary.to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        "A variable should only enter the theory if it improves leave-world-out prediction or explains a distinct mechanism. If coverage Gini alone is competitive with richer feature sets, the paper should keep the core theory simple and use other metrics only as diagnostics.",
    ]
    (DOCS / "minimal_variable_generalization_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df = pd.read_csv(IN)
    eval_df = evaluate(df)
    summary = summarize(eval_df)
    eval_df.to_csv(RESULTS / "minimal_variable_generalization_full.csv", index=False)
    summary.to_csv(RESULTS / "minimal_variable_generalization_summary.csv", index=False)
    write_report(eval_df, summary)
    print(DOCS / "minimal_variable_generalization_report.md")


if __name__ == "__main__":
    main()
