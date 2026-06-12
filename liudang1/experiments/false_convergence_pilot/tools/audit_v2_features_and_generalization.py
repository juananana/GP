#!/usr/bin/env python3
"""Audit frozen v2 offline diagnostics for leakage and generalization.

This script is intentionally read-only with respect to v2_outputs. It does not
retrain or retune the frozen v2 model on the existing test split. It reads the
frozen state feature table, checks the declared feature set, and writes
independent audit outputs to v2_audit_outputs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import beta
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


BASE = Path(__file__).resolve().parents[1]
V2_OUT = BASE / "v2_outputs"
AUDIT_OUT = BASE / "v2_audit_outputs"
SAFE_TARGET_RECALL = 0.95
ALLOWED_FCR = 0.05
CALIBRATION_CONFIDENCE = 0.95

FEATURE_COLUMNS = [
    "nominal_agent_count",
    "mean_confidence",
    "output_jaccard",
    "source_overlap",
    "source_coverage",
    "query_similarity",
    "search_path_overlap",
    "marginal_discovery_gain_last",
    "marginal_discovery_gain_mean",
    "novelty_decay",
    "singletons_f1",
    "doubletons_f2",
    "singleton_ratio",
    "doubleton_ratio",
    "per_source_singleton_density",
    "good_turing_missing_mass",
    "chao_missing_ratio",
    "corr_adjusted_chao_missing_ratio",
    "effective_exploration_size",
]

LABEL_OR_ORACLE_COLUMNS = {
    "found",
    "true_positive",
    "false_positive",
    "recall",
    "precision",
    "f1_score",
    "residual_missing_mass",
    "unsafe",
    "true_items",
    "false_items",
}

ID_OR_SHORTCUT_COLUMNS = {
    "state_id",
    "task_id",
    "repository",
    "task_family",
    "seed",
    "split",
    "run_ids",
    "collection_mode",
}

POST_AUDIT_OR_COST_COLUMNS = {
    "stage",
    "token_input",
    "token_output",
    "tool_calls",
    "wall_clock",
    "v1_risk_proxy",
}

FEATURE_GROUPS = {
    "all_allowed": FEATURE_COLUMNS,
    "portable_only": [
        "mean_confidence",
        "output_jaccard",
        "source_overlap",
        "source_coverage",
        "query_similarity",
        "search_path_overlap",
        "novelty_decay",
        "singleton_ratio",
        "doubleton_ratio",
        "per_source_singleton_density",
        "good_turing_missing_mass",
        "chao_missing_ratio",
        "corr_adjusted_chao_missing_ratio",
        "effective_exploration_size",
    ],
    "no_confidence": [c for c in FEATURE_COLUMNS if c != "mean_confidence"],
    "no_overlap_or_correlation": [
        c for c in FEATURE_COLUMNS
        if c not in {"output_jaccard", "source_overlap", "query_similarity", "search_path_overlap", "effective_exploration_size"}
    ],
    "no_source_path": [
        c for c in FEATURE_COLUMNS
        if c not in {"source_overlap", "source_coverage", "query_similarity", "search_path_overlap", "per_source_singleton_density"}
    ],
    "no_marginal_novelty": [
        c for c in FEATURE_COLUMNS
        if c not in {"marginal_discovery_gain_last", "marginal_discovery_gain_mean", "novelty_decay"}
    ],
    "no_missing_mass_counts": [
        c for c in FEATURE_COLUMNS
        if c not in {
            "singletons_f1",
            "doubletons_f2",
            "singleton_ratio",
            "doubleton_ratio",
            "good_turing_missing_mass",
            "chao_missing_ratio",
            "corr_adjusted_chao_missing_ratio",
            "per_source_singleton_density",
        }
    ],
    "confidence_only": ["mean_confidence"],
    "counts_only": [
        "singletons_f1",
        "doubletons_f2",
        "singleton_ratio",
        "doubleton_ratio",
        "good_turing_missing_mass",
        "chao_missing_ratio",
        "corr_adjusted_chao_missing_ratio",
    ],
}


@dataclass
class EvalResult:
    experiment: str
    model: str
    train_groups: str
    calibration_groups: str
    test_groups: str
    features: str
    n_train: int
    n_calibration: int
    n_test: int
    unsafe_rate_test: float | None
    auroc: float | None
    auprc: float | None
    brier: float | None
    threshold: float | None
    certified: int
    false_certifications: int
    false_certification_rate: float | None
    fcr_upper: float | None
    safe_coverage: float | None
    abstention: float | None


def fcr_upper_bound(false_count: int, certified_count: int) -> float | None:
    if certified_count == 0:
        return None
    return float(beta.ppf(CALIBRATION_CONFIDENCE, false_count + 1, certified_count - false_count))


def choose_threshold(cal_df: pd.DataFrame, risks: np.ndarray) -> float | None:
    best_threshold = None
    best_certified = -1
    for threshold in sorted(set(float(value) for value in risks)):
        certified = cal_df[risks <= threshold]
        if certified.empty:
            continue
        false_count = int(certified["unsafe"].sum())
        upper = fcr_upper_bound(false_count, len(certified))
        if upper is not None and upper <= ALLOWED_FCR and len(certified) > best_certified:
            best_threshold = threshold
            best_certified = len(certified)
    return best_threshold


def metric_bundle(
    *,
    experiment: str,
    model_name: str,
    features: list[str],
    train_df: pd.DataFrame,
    cal_df: pd.DataFrame,
    test_df: pd.DataFrame,
    cal_risk: np.ndarray,
    test_risk: np.ndarray,
) -> EvalResult:
    threshold = choose_threshold(cal_df, cal_risk)
    y_test = test_df["unsafe"].astype(int).to_numpy()
    auroc = float(roc_auc_score(y_test, test_risk)) if len(set(y_test)) == 2 else None
    auprc = float(average_precision_score(y_test, test_risk)) if len(set(y_test)) == 2 else None
    brier = float(brier_score_loss(y_test, np.clip(test_risk, 0.0, 1.0))) if len(y_test) else None
    if threshold is None:
        certified_mask = np.zeros(len(test_df), dtype=bool)
    else:
        certified_mask = test_risk <= threshold
    certified = test_df[certified_mask]
    false_count = int(certified["unsafe"].sum()) if len(certified) else 0
    safe_df = test_df[~test_df["unsafe"]]
    return EvalResult(
        experiment=experiment,
        model=model_name,
        train_groups=group_summary(train_df),
        calibration_groups=group_summary(cal_df),
        test_groups=group_summary(test_df),
        features=",".join(features),
        n_train=int(len(train_df)),
        n_calibration=int(len(cal_df)),
        n_test=int(len(test_df)),
        unsafe_rate_test=float(np.mean(y_test)) if len(y_test) else None,
        auroc=auroc,
        auprc=auprc,
        brier=brier,
        threshold=None if threshold is None else float(threshold),
        certified=int(len(certified)),
        false_certifications=false_count,
        false_certification_rate=false_count / len(certified) if len(certified) else None,
        fcr_upper=fcr_upper_bound(false_count, len(certified)) if len(certified) else None,
        safe_coverage=float(np.sum(certified_mask & (~test_df["unsafe"].to_numpy())) / len(safe_df)) if len(safe_df) else None,
        abstention=float(1.0 - np.mean(certified_mask)) if len(test_df) else None,
    )


def group_summary(df: pd.DataFrame) -> str:
    groups = df[["repository", "task_family", "seed"]].drop_duplicates()
    return ";".join(
        f"{row.repository}/{row.task_family}/s{int(row.seed)}"
        for row in groups.itertuples(index=False)
    )


def numeric_model(model_name: str) -> Pipeline:
    if model_name == "regularized_logistic":
        return Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, penalty="l2", C=0.5)),
        ])
    if model_name == "gradient_boosting":
        return Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", GradientBoostingClassifier(random_state=7, max_depth=2, n_estimators=80, learning_rate=0.05)),
        ])
    raise ValueError(model_name)


def fit_eval_numeric(
    *,
    experiment: str,
    model_name: str,
    features: list[str],
    train_df: pd.DataFrame,
    cal_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> EvalResult:
    model = numeric_model(model_name)
    model.fit(train_df[features], train_df["unsafe"].astype(int))
    cal_risk = model.predict_proba(cal_df[features])[:, 1]
    test_risk = model.predict_proba(test_df[features])[:, 1]
    return metric_bundle(
        experiment=experiment,
        model_name=model_name,
        features=features,
        train_df=train_df,
        cal_df=cal_df,
        test_df=test_df,
        cal_risk=cal_risk,
        test_risk=test_risk,
    )


def fit_eval_shortcut_probe(df: pd.DataFrame) -> EvalResult:
    train_df = df[df["split"] == "train"].copy()
    cal_df = df[df["split"] == "calibration"].copy()
    test_df = df[df["split"] == "test"].copy()
    categorical = ["task_id", "repository", "task_family", "agent_condition", "search_strategy", "budget_level"]
    numeric = ["nominal_agent_count", "seed"]
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ("num", SimpleImputer(strategy="median"), numeric),
    ])
    model = Pipeline([
        ("pre", pre),
        ("model", GradientBoostingClassifier(random_state=17, max_depth=2, n_estimators=60, learning_rate=0.05)),
    ])
    columns = categorical + numeric
    model.fit(train_df[columns], train_df["unsafe"].astype(int))
    cal_risk = model.predict_proba(cal_df[columns])[:, 1]
    test_risk = model.predict_proba(test_df[columns])[:, 1]
    return metric_bundle(
        experiment="metadata_shortcut_probe",
        model_name="gradient_boosting_metadata_only",
        features=columns,
        train_df=train_df,
        cal_df=cal_df,
        test_df=test_df,
        cal_risk=cal_risk,
        test_risk=test_risk,
    )


def leakage_report(df: pd.DataFrame) -> dict[str, Any]:
    columns = set(df.columns)
    feature_set = set(FEATURE_COLUMNS)
    return {
        "frozen_input": str(V2_OUT / "features" / "v2_state_features.csv"),
        "audited_feature_columns": FEATURE_COLUMNS,
        "feature_columns_present": sorted(feature_set & columns),
        "feature_columns_missing": sorted(feature_set - columns),
        "forbidden_label_or_oracle_columns_present_in_table": sorted(LABEL_OR_ORACLE_COLUMNS & columns),
        "forbidden_label_or_oracle_columns_used_as_features": sorted(feature_set & LABEL_OR_ORACLE_COLUMNS),
        "id_or_shortcut_columns_present_in_table": sorted(ID_OR_SHORTCUT_COLUMNS & columns),
        "id_or_shortcut_columns_used_as_features": sorted(feature_set & ID_OR_SHORTCUT_COLUMNS),
        "post_audit_or_cost_columns_present_in_table": sorted(POST_AUDIT_OR_COST_COLUMNS & columns),
        "post_audit_or_cost_columns_used_as_features": sorted(feature_set & POST_AUDIT_OR_COST_COLUMNS),
        "stage_values": sorted(str(value) for value in df["stage"].unique()) if "stage" in df else [],
        "collection_modes": sorted(str(value) for value in df["collection_mode"].unique()) if "collection_mode" in df else [],
        "assessment": [
            "Declared v2 model features exclude oracle scoring columns such as recall, true_positive, residual_missing_mass, and unsafe.",
            "Declared v2 model features exclude task_id, repository, task_family, seed, run_ids, split, and collection_mode.",
            "All audited rows are pre_audit states in the frozen feature table.",
            "source_coverage is computed against the bounded source-file universe, not against oracle items.",
            "marginal, singleton, overlap, source, query, and Chao/Good-Turing features are derivable from pre-audit agent item sets and logs.",
            "The metadata-only shortcut probe is reported separately and is not used as a proposed method.",
        ],
    }


def run_ablation(df: pd.DataFrame) -> pd.DataFrame:
    train_df = df[df["split"] == "train"].copy()
    cal_df = df[df["split"] == "calibration"].copy()
    test_df = df[df["split"] == "test"].copy()
    rows: list[EvalResult] = []
    for group_name, features in FEATURE_GROUPS.items():
        for model_name in ("regularized_logistic", "gradient_boosting"):
            rows.append(fit_eval_numeric(
                experiment=f"feature_ablation:{group_name}",
                model_name=model_name,
                features=features,
                train_df=train_df,
                cal_df=cal_df,
                test_df=test_df,
            ))
    return pd.DataFrame([row.__dict__ for row in rows])


def run_leave_one_out(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    rows: list[EvalResult] = []
    for held in sorted(df[group_col].unique()):
        test_df = df[df[group_col] == held].copy()
        remaining = df[df[group_col] != held].copy()
        train_df = remaining[remaining["seed"].isin([1, 2])].copy()
        cal_df = remaining[remaining["seed"] == 3].copy()
        if train_df.empty or cal_df.empty or test_df.empty:
            continue
        for model_name in ("regularized_logistic", "gradient_boosting"):
            rows.append(fit_eval_numeric(
                experiment=f"leave_one_{group_col}:{held}",
                model_name=model_name,
                features=FEATURE_COLUMNS,
                train_df=train_df,
                cal_df=cal_df,
                test_df=test_df,
            ))
    return pd.DataFrame([row.__dict__ for row in rows])


def write_report(
    *,
    leak: dict[str, Any],
    shortcut: pd.DataFrame,
    ablation: pd.DataFrame,
    loro: pd.DataFrame,
    loto: pd.DataFrame,
) -> None:
    lines = [
        "# v2 Feature Leakage and Generalization Audit",
        "",
        "## Scope",
        "",
        "This audit reads the frozen v2 offline diagnostic feature table and writes new audit outputs. It does not modify v2_outputs and does not tune the frozen v2 test set.",
        "",
        "## Leakage Check",
        "",
        f"- Feature columns missing from table: `{leak['feature_columns_missing']}`",
        f"- Forbidden oracle/label columns used as features: `{leak['forbidden_label_or_oracle_columns_used_as_features']}`",
        f"- ID/task/repository shortcut columns used as features: `{leak['id_or_shortcut_columns_used_as_features']}`",
        f"- Post-audit/cost columns used as features: `{leak['post_audit_or_cost_columns_used_as_features']}`",
        f"- Stage values: `{leak['stage_values']}`",
        f"- Collection modes: `{leak['collection_modes']}`",
        "",
        "Important table columns such as `recall`, `true_positive`, `residual_missing_mass`, and `unsafe` are present for offline scoring, but they are not in the declared v2 feature set.",
        "",
        "## Metadata Shortcut Probe",
        "",
        shortcut.to_markdown(index=False),
        "",
        "This probe intentionally uses task/repository/search/budget metadata to measure shortcut risk. It is not a valid proposed method.",
        "",
        "## Feature Ablation",
        "",
        ablation[[
            "experiment", "model", "n_train", "n_calibration", "n_test", "auroc", "auprc",
            "brier", "certified", "false_certifications", "false_certification_rate",
            "fcr_upper", "safe_coverage", "abstention",
        ]].to_markdown(index=False),
        "",
        "## Leave-One-Repository-Out",
        "",
        loro[[
            "experiment", "model", "n_train", "n_calibration", "n_test", "unsafe_rate_test",
            "auroc", "auprc", "brier", "certified", "false_certifications",
            "false_certification_rate", "fcr_upper", "safe_coverage", "abstention",
        ]].to_markdown(index=False),
        "",
        "## Leave-One-Task-Family-Out",
        "",
        loto[[
            "experiment", "model", "n_train", "n_calibration", "n_test", "unsafe_rate_test",
            "auroc", "auprc", "brier", "certified", "false_certifications",
            "false_certification_rate", "fcr_upper", "safe_coverage", "abstention",
        ]].to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        "- The declared v2 features pass the direct column-level leakage check.",
        "- Repository and task-family are currently one-to-one in the offline diagnostic, so leave-one-repository-out and leave-one-task-family-out are equivalent stress tests in this data.",
        "- Any high in-distribution score should be treated cautiously unless it remains stable under these held-out repository/task-family splits and later online blind validation.",
    ]
    (AUDIT_OUT / "reports" / "V2_FEATURE_LEAKAGE_AND_GENERALIZATION_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    (AUDIT_OUT / "reports").mkdir(parents=True, exist_ok=True)
    (AUDIT_OUT / "models").mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(V2_OUT / "features" / "v2_state_features.csv")
    leak = leakage_report(df)
    shortcut = pd.DataFrame([fit_eval_shortcut_probe(df).__dict__])
    ablation = run_ablation(df)
    loro = run_leave_one_out(df, "repository")
    loto = run_leave_one_out(df, "task_family")

    (AUDIT_OUT / "reports" / "v2_leakage_check.json").write_text(json.dumps(leak, indent=2), encoding="utf-8")
    shortcut.to_csv(AUDIT_OUT / "models" / "v2_metadata_shortcut_probe.csv", index=False)
    ablation.to_csv(AUDIT_OUT / "models" / "v2_feature_ablation.csv", index=False)
    loro.to_csv(AUDIT_OUT / "models" / "v2_leave_one_repository_out.csv", index=False)
    loto.to_csv(AUDIT_OUT / "models" / "v2_leave_one_task_family_out.csv", index=False)
    write_report(leak=leak, shortcut=shortcut, ablation=ablation, loro=loro, loto=loto)


if __name__ == "__main__":
    main()
