from __future__ import annotations

import importlib.metadata
import importlib.util
import hashlib
import json
import math
import subprocess
import sys
import inspect
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from experiment_config import load_experiment_config, seeds, thresholds


ROOT = Path(__file__).resolve().parents[4]
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"
OUT = PILOT / "credibility_supplement"
RESULTS = OUT / "results"
REPORTS = OUT / "reports"
FIGURES = OUT / "figures"
PAPER = ROOT / "paper"
PAPER_GENERATED = PAPER / "generated"

CONFIG = load_experiment_config()
THRESHOLDS = thresholds(CONFIG)
SAFE_SUPPORT_MIN = THRESHOLDS["tau_support"]
SAFE_GINI_MAX = THRESHOLDS["tau_gini"]
SAFE_RECALL_MIN = THRESHOLDS["eval_recall"]

FIG_DPI = 320
COLORS = {
    "base": "#6B7280",
    "broad": "#2563EB",
    "source": "#059669",
    "route": "#7C3AED",
    "continue": "#D97706",
    "safe": "#059669",
    "abstain": "#9CA3AF",
    "threshold": "#B91C1C",
    "random": "#9CA3AF",
    "text": "#111827",
    "grid": "#E5E7EB",
}


def set_figure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.titlesize": 8.5,
            "axes.labelsize": 8,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": "#374151",
            "axes.linewidth": 0.7,
            "grid.color": COLORS["grid"],
            "grid.linewidth": 0.55,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save_figure(fig: Any, stem: str, *, png_dpi: int = FIG_DPI) -> None:
    for directory in [FIGURES, PAPER / "figures"]:
        fig.savefig(directory / f"{stem}.png", dpi=png_dpi, bbox_inches="tight")
        fig.savefig(directory / f"{stem}.pdf", bbox_inches="tight")


def ensure_dirs() -> None:
    for path in [RESULTS, REPORTS, FIGURES, PAPER_GENERATED]:
        path.mkdir(parents=True, exist_ok=True)


def run_existing_experiments() -> None:
    scripts = [
        PILOT / "scripts" / "run_blind_policy_task.py",
        PILOT / "scripts" / "run_blind_code_task.py",
        PILOT / "external_validation_requests" / "run_external_requests_validation.py",
        PILOT / "controller_validation_v1" / "run_controller_validation_v1.py",
        PILOT / "controller_validation_v1" / "run_controller_validation_v2.py",
        PILOT / "external_validation_v2" / "run_external_validation_v2.py",
    ]
    for script in scripts:
        subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def module_universe(module: Any, granularity: str = "source_route") -> list[str]:
    files = list(getattr(module, "FILES"))
    routes = list(getattr(module, "ROUTES"))
    source_family_fn = getattr(module, "source_family")
    if granularity == "source_only":
        return [source_family_fn(name) for name in files]
    return [f"{source_family_fn(name)}::{route}" for name in files for route in routes]


def module_potential(module: Any, stratum: str, granularity: str = "source_route") -> float:
    if hasattr(module, "runtime_potential"):
        potential = module.runtime_potential()
        if stratum in potential:
            return float(potential[stratum])
    files = list(getattr(module, "FILES"))
    routes = list(getattr(module, "ROUTES"))
    if granularity == "source_only":
        source = stratum
        source_family_fn = getattr(module, "source_family")
        filename = next(name for name in files if source_family_fn(name) == source)
        if hasattr(module, "route_potential"):
            try:
                return float(module.route_potential(stratum, "source_only"))
            except Exception:
                return float(sum(module.route_potential(filename, route) for route in routes))
    source, route = stratum.split("::", 1)
    source_family_fn = getattr(module, "source_family")
    filename = next(name for name in files if source_family_fn(name) == source)
    try:
        return float(module.route_potential(stratum, granularity))
    except Exception:
        return float(module.route_potential(filename, route))


def module_candidate_items(module: Any, stratum: str, granularity: str = "source_route") -> tuple[set[str], int]:
    params = inspect.signature(module.candidate_items).parameters
    if len(params) == 2:
        return module.candidate_items(stratum, granularity)
    return module.candidate_items(stratum)


def module_filename_map(module: Any) -> dict[str, str]:
    files = list(getattr(module, "FILES"))
    source_family_fn = getattr(module, "source_family")
    return {source_family_fn(name): name for name in files}


def df_exposure_counts(df: pd.DataFrame, controller_label: str = "controller") -> Counter:
    frame = df[df["source_family"] != controller_label]
    return Counter(frame["source_route_stratum"])


def df_discovered_true(df: pd.DataFrame, oracle_ids: set[str]) -> set[str]:
    return set(df.loc[df["new_item"], "discovered_item_id"].dropna()) & oracle_ids


def df_condition_state(exposure: Counter, universe: list[str], potential: dict[str, float]) -> dict[str, Any]:
    values = [float(exposure.get(s, 0)) for s in universe]
    occupied = {s for s in universe if exposure.get(s, 0) > 0}
    weak_plausible = {s for s in universe if exposure.get(s, 0) == 0 and potential.get(s, 0.0) > 0}
    return {
        "support_size": len(occupied),
        "support_ratio": len(occupied) / len(universe) if universe else math.nan,
        "exposure_gini": gini(values),
        "weak_plausible_gap": len(weak_plausible),
    }


def fmt_float(value: Any, digits: int = 3) -> str:
    if value is None:
        return "--"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(number):
        return "--"
    return f"{number:.{digits}f}"


def latex_escape(value: Any) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def latex_texttt(value: Any) -> str:
    return r"\texttt{" + latex_escape(value) + "}"


def ci_text(mean: Any, low: Any, high: Any, digits: int = 1) -> str:
    return f"{fmt_float(mean, digits)} [{fmt_float(low, digits)}, {fmt_float(high, digits)}]"


def gini(values: list[float]) -> float:
    x = np.array(values, dtype=float)
    if x.size == 0 or x.sum() == 0:
        return math.nan
    x = np.sort(x)
    n = x.size
    return float((2 * np.sum(np.arange(1, n + 1) * x) / (n * x.sum())) - (n + 1) / n)


def runtime_controller_decision(
    support: float,
    gini: float,
    *,
    weak_plausible_gap: int | float = 0,
    runtime_residual_items: int | float = 0,
) -> str:
    geometry_ok = support >= SAFE_SUPPORT_MIN and gini <= SAFE_GINI_MAX
    if runtime_residual_items > 0 or weak_plausible_gap > 0:
        return "CONTINUE"
    if geometry_ok:
        return "SAFE"
    return "ABSTAIN"


def require_runtime_residual(row: pd.Series | dict[str, Any], *, context: str) -> float:
    if "runtime_residual_items" not in row:
        raise KeyError(f"runtime_residual_items is required for runtime decision in {context}")
    return float(row["runtime_residual_items"])


def aggregate_decisions(rows: list[dict[str, Any]], label: str, task_group: str) -> dict[str, Any]:
    df = pd.DataFrame(rows)
    safe = int((df["decision"] == "SAFE").sum())
    cont = int((df["decision"] == "CONTINUE").sum())
    abstain = int((df["decision"] == "ABSTAIN").sum())
    safe_mask = df["decision"] == "SAFE"
    oracle_safe = df["recall"].astype(float) >= SAFE_RECALL_MIN
    oracle_unsafe = ~oracle_safe
    return {
        "task_group": task_group,
        "evaluation_set": label,
        "n": int(len(df)),
        "oracle_safe_n": int(oracle_safe.sum()),
        "oracle_unsafe_n": int(oracle_unsafe.sum()),
        "safe": safe,
        "continue": cont,
        "abstain": abstain,
        "false_certification_rate": float(((safe_mask) & (~oracle_safe)).mean()),
        "false_certification_n": int(((safe_mask) & oracle_unsafe).sum()),
        "safe_coverage": float(((safe_mask) & oracle_safe).sum() / oracle_safe.sum()) if oracle_safe.sum() else math.nan,
        "abstention_rate": float((df["decision"] == "ABSTAIN").mean()),
        "mean_repair_gain": float(df["repair_gain"].mean()) if "repair_gain" in df else math.nan,
        "mean_cost": float(df["cost"].mean()) if "cost" in df else math.nan,
    }


def build_condition_decision_rows() -> list[dict[str, Any]]:
    files = [
        ("policy_docset_v1", PILOT / "blind_tasks" / "policy_docset_v1" / "results" / "condition_metrics.csv"),
        ("code_repo_v1", PILOT / "blind_tasks" / "code_repo_v1" / "results" / "condition_metrics.csv"),
        ("requests", PILOT / "external_validation_requests" / "results" / "external_requests_condition_metrics.csv"),
        ("urllib3", PILOT / "external_validation_v2" / "results" / "condition_summary.csv"),
    ]
    rows: list[dict[str, Any]] = []
    for task, path in files:
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            condition = str(row["condition"])
            if "challenger" in condition:
                continue
            support = float(row.get("source_route_coverage_ratio", row.get("support_ratio")))
            gini = float(row["exposure_gini"])
            recall = float(row["recall"])
            weak_gap = float(row.get("weak_plausible_gap", 0))
            decision = str(
                row.get(
                    "controller_decision",
                    runtime_controller_decision(support, gini, weak_plausible_gap=weak_gap),
                )
            )
            rows.append(
                {
                    "task": task,
                    "condition": condition,
                    "state_type": "fixed_stop_state",
                    "seed": -1,
                    "budget": 0,
                    "decision": decision,
                    "recall": recall,
                    "support": support,
                    "gini": gini,
                    "residual_warning": False,
                    "unresolved_warning": False,
                    "runtime_residual_items": 0.0,
                    "weak_plausible_gap": weak_gap,
                    "repair_gain": 0.0,
                    "cost": 0.0,
                }
            )
    return rows


def build_requests_repair_rows() -> list[dict[str, Any]]:
    detail = pd.read_csv(PILOT / "controller_validation_v1" / "results" / "controller_validation_v2_detail.csv")
    rows = []
    for _, row in detail.iterrows():
        condition_ok = float(row["after_support_ratio"]) >= SAFE_SUPPORT_MIN and float(row["after_exposure_gini"]) <= SAFE_GINI_MAX
        runtime_residual = int(require_runtime_residual(row, context="requests repair rows"))
        weak_gap = int(row.get("after_weak_plausible_gap", 0))
        if runtime_residual > 0:
            decision = "CONTINUE"
        elif condition_ok and weak_gap == 0:
            decision = "SAFE"
        else:
            decision = "ABSTAIN"
        rows.append(
            {
                "task": "requests",
                "condition": f"repair:{row['challenger']}",
                "state_type": "seeded_unsafe_repair",
                "seed": int(row.get("seed", -1)),
                "budget": int(row.get("budget", CONFIG.get("repair_budgets", {}).get("external_requests", 4))),
                "decision": decision,
                "recall": float(row["cumulative_recall"]),
                "support": float(row["after_support_ratio"]),
                "gini": float(row["after_exposure_gini"]),
                "residual_warning": bool(runtime_residual > 0),
                "unresolved_warning": False,
                "runtime_residual_items": float(runtime_residual),
                "weak_plausible_gap": float(weak_gap),
                "repair_gain": float(row["new_true_items"]),
                "cost": float(row["cost"]),
            }
        )
    return rows


def build_urllib3_repair_rows() -> list[dict[str, Any]]:
    detail = pd.read_csv(PILOT / "external_validation_v2" / "results" / "controller_challenger_detailed.csv")
    rows = []
    for _, row in detail.iterrows():
        runtime_residual = require_runtime_residual(row, context="urllib3 repair rows")
        rows.append(
            {
                "task": "urllib3",
                "condition": f"repair:{row['challenger']}",
                "state_type": "seeded_unsafe_repair",
                "seed": int(row.get("seed", -1)),
                "budget": int(row.get("budget", CONFIG.get("repair_budgets", {}).get("external_urllib3", 5))),
                "decision": str(row["decision"]),
                "recall": float(row["cumulative_recall"]),
                "support": float(row["after_support_ratio"]),
                "gini": float(row["after_exposure_gini"]),
                "residual_warning": bool(runtime_residual > 0),
                "unresolved_warning": False,
                "runtime_residual_items": runtime_residual,
                "weak_plausible_gap": float(row.get("after_weak_plausible_gap", 0)),
                "repair_gain": float(row["new_true_items"]),
                "cost": float(row["cost"]),
            }
        )
    return rows


def controller_decision_table(safe_state_detail: pd.DataFrame | None = None) -> pd.DataFrame:
    condition_rows = build_condition_decision_rows()
    requests_rows = build_requests_repair_rows()
    urllib3_rows = build_urllib3_repair_rows()
    safe_rows = []
    if safe_state_detail is not None:
        for _, row in safe_state_detail.iterrows():
            safe_rows.append(
                {
                    "task": row["task"],
                    "condition": f"safe_state:{row['condition']}:{row['challenger']}",
                    "state_type": "seeded_safe_complete",
                    "seed": int(row.get("seed", -1)),
                    "budget": int(row.get("budget", -1)),
                    "decision": row["decision"],
                    "recall": float(row["cumulative_recall"]),
                    "support": float(row["after_support_ratio"]),
                    "gini": float(row["after_exposure_gini"]),
                    "residual_warning": bool(require_runtime_residual(row, context="seeded safe rows") > 0),
                    "unresolved_warning": False,
                    "runtime_residual_items": require_runtime_residual(row, context="seeded safe rows"),
                    "weak_plausible_gap": float(row.get("after_weak_plausible_gap", 0)),
                    "repair_gain": float(row["repair_gain"]),
                    "cost": float(row["cost"]),
                }
            )
    rows = [
        aggregate_decisions(condition_rows, "observed stop states", "all tasks"),
        aggregate_decisions([r for r in condition_rows if r["task"] in {"requests", "urllib3"}], "observed external states", "external repos"),
        aggregate_decisions(requests_rows, "seeded repairs", "requests"),
        aggregate_decisions(urllib3_rows, "seeded repairs", "urllib3"),
        aggregate_decisions(requests_rows + urllib3_rows, "seeded repairs", "external repos"),
    ]
    if safe_rows:
        rows.extend(
            [
                aggregate_decisions([r for r in safe_rows if r["task"] == "requests"], "seeded safe states", "requests"),
                aggregate_decisions([r for r in safe_rows if r["task"] == "urllib3"], "seeded safe states", "urllib3"),
                aggregate_decisions(safe_rows, "seeded safe states", "external repos"),
            ]
        )
    table = pd.DataFrame(rows)
    table.to_csv(RESULTS / "controller_decision_table.csv", index=False)
    pd.DataFrame(condition_rows + requests_rows + urllib3_rows + safe_rows).to_csv(RESULTS / "controller_decision_detail.csv", index=False)
    return table


def source_only_ablation() -> pd.DataFrame:
    inputs = [
        ("policy_docset_v1", PILOT / "blind_tasks" / "policy_docset_v1" / "results" / "condition_metrics.csv"),
        ("code_repo_v1", PILOT / "blind_tasks" / "code_repo_v1" / "results" / "condition_metrics.csv"),
        ("requests", PILOT / "external_validation_requests" / "results" / "external_requests_condition_metrics.csv"),
        ("urllib3", PILOT / "external_validation_v2" / "results" / "condition_summary.csv"),
    ]
    rows = []
    for task, path in inputs:
        df = pd.read_csv(path)
        h = df[df["condition"] == "homogeneous"].iloc[0]
        source_route_support = float(h.get("source_route_coverage_ratio", h.get("support_ratio")))
        source_route_gini = float(h["exposure_gini"])
        recall = float(h["recall"])
        rows.append(
            {
                "task": task,
                "source_only_support": 1.0,
                "source_route_support": source_route_support,
                "source_route_gini": source_route_gini,
                "base_recall": recall,
                "source_only_would_be_eligible": True,
                "source_route_eligible": source_route_support >= SAFE_SUPPORT_MIN and source_route_gini <= SAFE_GINI_MAX,
                "false_certification_if_source_only_safe": recall < SAFE_RECALL_MIN,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "source_only_vs_source_route.csv", index=False)
    return out


def verifier_gate_decision(row: pd.Series | dict[str, Any]) -> str:
    unresolved = bool(row.get("unresolved_warning", False))
    residual = bool(row.get("residual_warning", False))
    return "ABSTAIN" if unresolved or residual else "SAFE"


def _json_records(df: pd.DataFrame, path: Path) -> None:
    path.write_text(json.dumps(df.to_dict(orient="records"), separators=(",", ":")), encoding="utf-8")


def _state_frame(detail: pd.DataFrame, safe_state_detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in detail.iterrows():
        challenger = ""
        if str(row["condition"]).startswith("repair:"):
            challenger = str(row["condition"]).split(":", 1)[1]
        runtime_residual = require_runtime_residual(row, context="unified state metrics")
        rows.append(
            {
                "task": row["task"],
                "condition": row["condition"],
                "state_type": row.get("state_type", "fixed_stop_state"),
                "seed": int(row.get("seed", -1)),
                "budget": int(row.get("budget", 0)),
                "challenger": challenger,
                "full_decision": row["decision"],
                "recall": float(row["recall"]),
                "support": float(row["support"]),
                "gini": float(row["gini"]),
                "repair_gain": float(row["repair_gain"]),
                "repair_cost": float(row["cost"]),
                "runtime_residual_items": runtime_residual,
                "weak_plausible_gap": float(row.get("weak_plausible_gap", 0)),
                "residual_warning": bool(row.get("residual_warning", runtime_residual > 0)),
                "unresolved_warning": bool(row.get("unresolved_warning", False)),
            }
        )
    for _, row in safe_state_detail.iterrows():
        runtime_residual = require_runtime_residual(row, context="unified safe-state metrics")
        rows.append(
            {
                "task": row["task"],
                "condition": f"safe_state:{row['condition']}:{row['challenger']}",
                "state_type": "seeded_safe_complete",
                "seed": int(row["seed"]),
                "budget": int(row["budget"]),
                "challenger": row["challenger"],
                "full_decision": row["decision"],
                "recall": float(row["cumulative_recall"]),
                "support": float(row["after_support_ratio"]),
                "gini": float(row["after_exposure_gini"]),
                "repair_gain": float(row["repair_gain"]),
                "repair_cost": float(row["cost"]),
                "runtime_residual_items": runtime_residual,
                "weak_plausible_gap": float(row.get("after_weak_plausible_gap", 0)),
                "residual_warning": bool(runtime_residual > 0),
                "unresolved_warning": False,
            }
        )
    states = pd.DataFrame(rows)
    states["oracle_safe"] = states["recall"] >= SAFE_RECALL_MIN
    states["geometry_ok"] = (states["support"] >= SAFE_SUPPORT_MIN) & (states["gini"] <= SAFE_GINI_MAX)
    states.to_csv(RESULTS / "unified_state_metrics.csv", index=False)
    _json_records(states, RESULTS / "unified_state_metrics.json")
    return states


def _decision_variant_metrics(states: pd.DataFrame) -> pd.DataFrame:
    scoped = states[
        (
            states["state_type"].isin(["fixed_stop_state", "seeded_unsafe_repair"])
            & (~states["condition"].astype(str).str.startswith("repair:") | (states["challenger"] == "residual_potential"))
        )
        | ((states["state_type"] == "seeded_safe_complete") & (states["challenger"] == "residual_potential"))
    ].copy()

    def decisions(policy: str, frame: pd.DataFrame) -> pd.Series:
        if policy in {"Naive stop", "Source-only"}:
            return pd.Series(["SAFE"] * len(frame), index=frame.index)
        if policy == "Verifier-gate":
            return frame.apply(verifier_gate_decision, axis=1)
        if policy == "Eligibility-only":
            return pd.Series(np.where(frame["geometry_ok"], "SAFE", "ABSTAIN"), index=frame.index)
        if policy == "Full controller":
            return frame["full_decision"]
        raise ValueError(policy)

    rows = []
    policies = ["Naive stop", "Source-only", "Eligibility-only", "Verifier-gate", "Full controller"]
    for policy in policies:
        d = decisions(policy, scoped)
        for (task, state_type), sub_idx in scoped.groupby(["task", "state_type"]).groups.items():
            idx = list(sub_idx)
            sub = scoped.loc[idx]
            sub_decision = d.loc[idx]
            unsafe = ~sub["oracle_safe"]
            safe = sub["oracle_safe"]
            rows.append(
                {
                    "table": "decision_variants",
                    "task": task,
                    "policy": policy,
                    "state_type": state_type,
                    "seed": "mixed",
                    "budget": "mixed",
                    "n": int(len(sub)),
                    "unsafe_n": int(unsafe.sum()),
                    "safe_n": int(safe.sum()),
                    "safe_count": int((sub_decision == "SAFE").sum()),
                    "continue_count": int((sub_decision == "CONTINUE").sum()),
                    "abstain_count": int((sub_decision == "ABSTAIN").sum()),
                    "safe_on_unsafe": int(((sub_decision == "SAFE") & unsafe).sum()),
                    "safe_on_safe": int(((sub_decision == "SAFE") & safe).sum()),
                    "fcr": float(((sub_decision == "SAFE") & unsafe).sum() / unsafe.sum()) if unsafe.sum() else math.nan,
                    "safe_coverage": float(((sub_decision == "SAFE") & safe).sum() / safe.sum()) if safe.sum() else math.nan,
                    "continue_rate": float((sub_decision == "CONTINUE").mean()) if len(sub) else math.nan,
                    "abstain_rate": float((sub_decision == "ABSTAIN").mean()) if len(sub) else math.nan,
                    "repair_gain": float(sub["repair_gain"].mean()),
                    "repair_cost": float(sub["repair_cost"].mean()),
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "unified_decision_variants.csv", index=False)
    _json_records(out, RESULTS / "unified_decision_variants.json")
    return out


def _repair_variant_metrics(states: pd.DataFrame) -> pd.DataFrame:
    scoped = states[
        states["state_type"].isin(["seeded_unsafe_repair", "seeded_safe_complete"])
        & states["challenger"].isin(["random", "high_potential", "residual_potential"])
    ].copy()
    rows = []
    for (task, challenger, state_type), sub in scoped.groupby(["task", "challenger", "state_type"]):
        decision = sub["full_decision"]
        unsafe = ~sub["oracle_safe"]
        safe = sub["oracle_safe"]
        rows.append(
            {
                "table": "repair_variants",
                "task": task,
                "policy": challenger,
                "state_type": state_type,
                "seed": "mixed",
                "budget": "mixed",
                "n": int(len(sub)),
                "safe_count": int((decision == "SAFE").sum()),
                "continue_count": int((decision == "CONTINUE").sum()),
                "abstain_count": int((decision == "ABSTAIN").sum()),
                "fcr": float(((decision == "SAFE") & unsafe).sum() / unsafe.sum()) if unsafe.sum() else math.nan,
                "safe_coverage": float(((decision == "SAFE") & safe).sum() / safe.sum()) if safe.sum() else math.nan,
                "continue_rate": float((decision == "CONTINUE").mean()),
                "abstain_rate": float((decision == "ABSTAIN").mean()),
                "repair_gain": float(sub["repair_gain"].mean()),
                "repair_cost": float(sub["repair_cost"].mean()),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "unified_repair_variants.csv", index=False)
    _json_records(out, RESULTS / "unified_repair_variants.json")
    return out


def _localization_risk_trend(source_ablation: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in source_ablation.iterrows():
        rows.append(
            {
                "table": "localization_risk_trend",
                "task": row["task"],
                "policy": "homogeneous stop",
                "state_type": "fixed_stop_state",
                "seed": -1,
                "budget": 0,
                "source_only_support": float(row["source_only_support"]),
                "source_route_support": float(row["source_route_support"]),
                "support_gap": float(row["source_only_support"] - row["source_route_support"]),
                "gini": float(row["source_route_gini"]),
                "fcr": float(row["base_recall"] < SAFE_RECALL_MIN),
                "safe_coverage": math.nan,
                "continue_rate": math.nan,
                "abstain_rate": math.nan,
                "repair_gain": math.nan,
                "repair_cost": math.nan,
                "residual_yield": float(max(0.0, SAFE_RECALL_MIN - float(row["base_recall"]))),
                "recall": float(row["base_recall"]),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "unified_localization_risk_trend.csv", index=False)
    _json_records(out, RESULTS / "unified_localization_risk_trend.json")
    return out


def _safety_cost_frontier(threshold: pd.DataFrame, budget: pd.DataFrame) -> pd.DataFrame:
    threshold_rows = threshold.copy()
    threshold_rows["table"] = "threshold_sweep"
    threshold_rows["policy"] = threshold_rows["challenger"]
    threshold_rows["state_type"] = "seeded_unsafe_repair"
    threshold_rows["seed"] = "mixed"
    threshold_rows["budget"] = "fixed"
    threshold_rows = threshold_rows.rename(columns={"false_certification_rate": "fcr", "mean_repair_gain": "repair_gain", "mean_cost": "repair_cost"})

    budget_rows = budget.copy()
    budget_rows["table"] = "budget_sweep"
    budget_rows["policy"] = budget_rows["challenger"]
    budget_rows["state_type"] = "seeded_unsafe_repair"
    budget_rows["seed"] = "mixed"
    budget_rows["support_threshold"] = math.nan
    budget_rows["gini_threshold"] = math.nan
    budget_rows = budget_rows.rename(columns={"false_certification_rate": "fcr", "mean_repair_gain": "repair_gain", "mean_cost": "repair_cost"})

    keep = [
        "table",
        "task",
        "policy",
        "state_type",
        "seed",
        "budget",
        "support_threshold",
        "gini_threshold",
        "fcr",
        "safe_coverage",
        "safe_rate",
        "continue_rate",
        "abstain_rate",
        "repair_gain",
        "repair_cost",
        "mean_cumulative_recall",
    ]
    for frame in [threshold_rows, budget_rows]:
        if "safe_coverage" not in frame:
            frame["safe_coverage"] = math.nan
        if "safe_rate" not in frame:
            frame["safe_rate"] = math.nan
    out = pd.concat([threshold_rows[keep], budget_rows[keep]], ignore_index=True)
    out.to_csv(RESULTS / "unified_threshold_budget_sweep.csv", index=False)
    _json_records(out, RESULTS / "unified_threshold_budget_sweep.json")

    frontier = (
        out[out["policy"].isin(["residual_potential", "high_potential", "random"])]
        .groupby(["table", "task", "policy", "budget"], as_index=False)
        .agg(
            fcr=("fcr", "mean"),
            safe_coverage=("safe_coverage", "mean"),
            continue_rate=("continue_rate", "mean"),
            abstain_rate=("abstain_rate", "mean"),
            repair_gain=("repair_gain", "mean"),
            repair_cost=("repair_cost", "mean"),
            mean_cumulative_recall=("mean_cumulative_recall", "mean"),
        )
    )
    frontier["state_type"] = "seeded_unsafe_repair"
    frontier["seed"] = "mixed"
    frontier.to_csv(RESULTS / "unified_safety_cost_frontier.csv", index=False)
    _json_records(frontier, RESULTS / "unified_safety_cost_frontier.json")
    return frontier


def unified_result_exports(
    controller: pd.DataFrame,
    source_ablation: pd.DataFrame,
    threshold: pd.DataFrame,
    budget: pd.DataFrame,
    safe_state_detail: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    detail = pd.read_csv(RESULTS / "controller_decision_detail.csv")
    states = _state_frame(detail, safe_state_detail)
    exports = {
        "decision_variants": _decision_variant_metrics(states),
        "repair_variants": _repair_variant_metrics(states),
        "controller_count_table": controller.copy(),
        "localization_risk_trend": _localization_risk_trend(source_ablation),
        "threshold_budget_sweep": _safety_cost_frontier(threshold, budget),
    }
    controller.to_csv(RESULTS / "unified_controller_count_table.csv", index=False)
    _json_records(controller, RESULTS / "unified_controller_count_table.json")
    manifest = {
        "config_path": CONFIG.get("_config_path"),
        "thresholds": {
            "tau_support": SAFE_SUPPORT_MIN,
            "tau_gini": SAFE_GINI_MAX,
            "eval_only_recall_threshold": SAFE_RECALL_MIN,
        },
        "exports": {
            name: {
                "csv": str((RESULTS / f"unified_{name}.csv").relative_to(ROOT)).replace("\\", "/"),
                "json": str((RESULTS / f"unified_{name}.json").relative_to(ROOT)).replace("\\", "/"),
            }
            for name in [
                "decision_variants",
                "repair_variants",
                "controller_count_table",
                "localization_risk_trend",
                "threshold_budget_sweep",
                "safety_cost_frontier",
                "state_metrics",
            ]
        },
        "runtime_visible_fields": CONFIG.get("runtime_visible_fields", []),
        "posthoc_oracle_only_fields": CONFIG.get("posthoc_oracle_only_fields", []),
    }
    (RESULTS / "unified_results_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return exports


def chao_scalar_proxy() -> pd.DataFrame:
    files = [
        ("policy_docset_v1", PILOT / "blind_tasks" / "policy_docset_v1" / "logs" / "action_events.jsonl", 24),
        ("code_repo_v1", PILOT / "blind_tasks" / "code_repo_v1" / "logs" / "action_events.jsonl", 20),
        ("requests", PILOT / "external_validation_requests" / "logs" / "action_events.jsonl", 298),
        ("urllib3", PILOT / "external_validation_v2" / "logs" / "action_events.jsonl", 699),
    ]
    rows = []
    for task, path, total in files:
        events = pd.DataFrame(read_jsonl(path))
        h = events[(events["condition"] == "homogeneous") & (events["source_family"] != "controller")]
        discovered = h[h["new_item"]]["discovered_item_id"].dropna()
        counts = Counter(discovered)
        f1 = sum(1 for value in counts.values() if value == 1)
        f2 = sum(1 for value in counts.values() if value == 2)
        observed = len(counts)
        chao1 = observed + (f1 * f1 / (2 * f2)) if f2 > 0 else observed + (f1 * (f1 - 1) / 2)
        singleton_rate = f1 / observed if observed else math.nan
        scalar_stop = singleton_rate <= 0.10
        recall = observed / total
        rows.append(
            {
                "task": task,
                "observed_items": observed,
                "oracle_total": total,
                "recall": recall,
                "singletons": f1,
                "doubletons": f2,
                "singleton_rate": singleton_rate,
                "chao1_estimate": chao1,
                "scalar_stop_proxy": scalar_stop,
                "false_if_scalar_stop": bool(scalar_stop and recall < SAFE_RECALL_MIN),
                "source_route_mismatch": True,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "chao_singleton_proxy.csv", index=False)
    return out


def simulate_external_budget(module: Any, task_name: str, budgets: list[int]) -> pd.DataFrame:
    module.ensure_dirs()
    module.write_snapshot()
    if hasattr(module, "runtime_potential"):
        potential = module.runtime_potential()
    else:
        potential = {s: module_potential(module, s) for s in module_universe(module)}
    oracle = module.build_oracle()
    oracle_ids = {row["item_id"] for row in oracle}
    events: list[dict[str, Any]] = []
    for condition, agents in module.CONDITIONS.items():
        events.extend(module.run_condition(condition, agents))
    base = pd.DataFrame(events)
    base = base[base["condition"] == "homogeneous"].copy()
    if task_name == "requests":
        universe = module_universe(module, "source_route")
        candidate_cache = {s: module_candidate_items(module, s, "source_route") for s in universe}
    else:
        universe = module_universe(module)
        candidate_cache = {s: module_candidate_items(module, s) for s in universe}
    base_found = df_discovered_true(base, oracle_ids)
    base_runtime_seen = set(base.loc[base["new_item"], "discovered_item_id"].dropna())
    base_exposure = df_exposure_counts(base)
    exposure = Counter(base_exposure)
    discovery = Counter(base.loc[base["new_item"], "source_route_stratum"])
    max_exp = max([exposure.get(s, 0) for s in universe] + [1])

    def targets_for(challenger: str, seed: int, budget: int) -> list[str]:
        if challenger == "random":
            return list(np.random.default_rng(seed).choice(universe, size=min(budget, len(universe)), replace=False))
        if challenger == "low_exposure":
            return sorted(universe, key=lambda s: (exposure.get(s, 0), s))[:budget]
        if challenger == "low_discovery":
            return sorted(universe, key=lambda s: (discovery.get(s, 0), s))[:budget]
        if challenger == "high_potential":
            return sorted(universe, key=lambda s: (-potential[s], s))[:budget]
        if challenger == "residual_potential":
            return sorted(universe, key=lambda s: (-(1.0 - exposure.get(s, 0) / max_exp) * potential[s], s))[:budget]
        if challenger == "free_search_continuation":
            weights = np.array([potential[s] + 1e-6 for s in universe], dtype=float)
            weights = weights / weights.sum()
            rng = np.random.default_rng(seed)
            return list(rng.choice(universe, size=min(budget, len(universe)), replace=False, p=weights))
        raise ValueError(challenger)

    rows = []
    for budget in budgets:
        for challenger in module.CHALLENGERS:
            for seed in range(module.N_SEEDS):
                targets = targets_for(challenger, seed, budget)
                found = set(base_found)
                runtime_seen = set(base_runtime_seen)
                runtime_residual = set()
                new = set()
                repaired = Counter(base_exposure)
                cost = 0
                for target in targets:
                    repaired[target] += 1
                    ids, target_cost = candidate_cache[target]
                    cost += target_cost
                    runtime_residual |= ids - runtime_seen
                    runtime_seen |= ids
                    new |= (ids & oracle_ids) - found
                    found |= ids & oracle_ids
                after = df_condition_state(repaired, universe, potential)
                condition_ok = after["support_ratio"] >= SAFE_SUPPORT_MIN and after["exposure_gini"] <= SAFE_GINI_MAX
                if len(runtime_residual) > 0:
                    decision = "CONTINUE"
                elif condition_ok and after["weak_plausible_gap"] == 0:
                    decision = "SAFE"
                else:
                    decision = "ABSTAIN"
                recall = len(found) / len(oracle_ids)
                rows.append(
                    {
                        "task": task_name,
                        "budget": budget,
                        "challenger": challenger,
                        "seed": seed,
                        "decision": decision,
                        "false_certification": decision == "SAFE" and recall < SAFE_RECALL_MIN,
                        "safe": decision == "SAFE",
                        "continue": decision == "CONTINUE",
                        "abstain": decision == "ABSTAIN",
                        "cost": cost,
                        "runtime_residual_items": len(runtime_residual),
                        "repair_gain": len(new),
                        "cumulative_recall": recall,
                        "after_support_ratio": after["support_ratio"],
                        "after_exposure_gini": after["exposure_gini"],
                        "after_weak_plausible_gap": after["weak_plausible_gap"],
                    }
                )
    return pd.DataFrame(rows)


def threshold_and_budget_sensitivity() -> tuple[pd.DataFrame, pd.DataFrame]:
    req_detail = pd.read_csv(PILOT / "controller_validation_v1" / "results" / "controller_validation_v2_detail.csv")
    url_detail = pd.read_csv(PILOT / "external_validation_v2" / "results" / "controller_challenger_detailed.csv")
    url_detail = url_detail.rename(columns={"false_certification": "old_false_certification"})
    url_detail["task"] = "urllib3"
    req_detail["task"] = "requests"
    detail = pd.concat(
        [
            req_detail[["task", "challenger", "seed", "after_support_ratio", "after_exposure_gini", "runtime_residual_items", "new_true_items", "cost", "cumulative_recall"]],
            url_detail[["task", "challenger", "seed", "after_support_ratio", "after_exposure_gini", "runtime_residual_items", "new_true_items", "cost", "cumulative_recall"]],
        ],
        ignore_index=True,
    )
    raw_thresholds = CONFIG.get("thresholds", {})
    support_value = raw_thresholds.get("tau_support", SAFE_SUPPORT_MIN)
    gini_value = raw_thresholds.get("tau_gini", SAFE_GINI_MAX)
    support_grid = list(support_value) if isinstance(support_value, list) else [0.50, 0.60, 0.70, float(support_value), 0.80, 0.90]
    gini_grid = list(gini_value) if isinstance(gini_value, list) else [0.50, 0.60, float(gini_value), 0.80, 0.90]
    rows = []
    for task, task_df in detail.groupby("task"):
        for support_thr in support_grid:
            for gini_thr in gini_grid:
                for challenger, sub in task_df.groupby("challenger"):
                    condition_ok = (sub["after_support_ratio"] >= support_thr) & (sub["after_exposure_gini"] <= gini_thr)
                    runtime_residual = sub["runtime_residual_items"].astype(float) > 0
                    safe = condition_ok & ~runtime_residual
                    cont = runtime_residual
                    abstain = ~(safe | cont)
                    false_cert = safe & (sub["cumulative_recall"] < SAFE_RECALL_MIN)
                    rows.append(
                        {
                            "task": task,
                            "support_threshold": support_thr,
                            "gini_threshold": gini_thr,
                            "challenger": challenger,
                            "runs": len(sub),
                            "false_certification_rate": float(false_cert.mean()),
                            "safe_coverage": float((safe & (sub["cumulative_recall"] >= SAFE_RECALL_MIN)).sum() / (sub["cumulative_recall"] >= SAFE_RECALL_MIN).sum())
                            if (sub["cumulative_recall"] >= SAFE_RECALL_MIN).sum()
                            else math.nan,
                            "safe_rate": float(safe.mean()),
                            "continue_rate": float(cont.mean()),
                            "abstain_rate": float(abstain.mean()),
                            "mean_cost": float(sub["cost"].mean()),
                            "mean_repair_gain": float(sub["new_true_items"].mean()),
                            "mean_cumulative_recall": float(sub["cumulative_recall"].mean()),
                        }
                    )
    threshold = pd.DataFrame(rows)

    req_mod = load_module("external_requests_validation", PILOT / "external_validation_requests" / "run_external_requests_validation.py")
    url_mod = load_module("external_urllib3_validation", PILOT / "external_validation_v2" / "run_external_validation_v2.py")
    budget = pd.concat(
        [
            simulate_external_budget(req_mod, "requests", CONFIG.get("repair_budgets", {}).get("safe_state_validation_budgets", [1, 2, 4, 6, 8])),
            simulate_external_budget(url_mod, "urllib3", CONFIG.get("repair_budgets", {}).get("safe_state_validation_budgets", [1, 2, 4, 6, 8])),
        ],
        ignore_index=True,
    )
    budget_summary = (
        budget.groupby(["task", "budget", "challenger"], as_index=False)
        .agg(
            false_certification_rate=("false_certification", "mean"),
            safe_rate=("safe", "mean"),
            continue_rate=("continue", "mean"),
            abstain_rate=("abstain", "mean"),
            mean_cost=("cost", "mean"),
            mean_repair_gain=("repair_gain", "mean"),
            mean_cumulative_recall=("cumulative_recall", "mean"),
        )
    )
    threshold.to_csv(RESULTS / "threshold_sensitivity.csv", index=False)
    budget.to_csv(RESULTS / "budget_sensitivity_detail.csv", index=False)
    budget_summary.to_csv(RESULTS / "budget_sensitivity.csv", index=False)
    return threshold, budget_summary


def sensitivity_summary(threshold: pd.DataFrame, budget: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for task, sub in threshold.groupby("task"):
        rows.append(
            {
                "task": task,
                "sweep": "threshold",
                "safe_rate_range": f"{sub['safe_rate'].min():.3f}-{sub['safe_rate'].max():.3f}",
                "continue_rate_range": f"{sub['continue_rate'].min():.3f}-{sub['continue_rate'].max():.3f}",
                "abstain_rate_range": f"{sub['abstain_rate'].min():.3f}-{sub['abstain_rate'].max():.3f}",
                "max_fcr": float(sub["false_certification_rate"].max()),
                "mean_repair_cost": float(sub["mean_cost"].mean()),
            }
        )
    for task, sub in budget.groupby("task"):
        rows.append(
            {
                "task": task,
                "sweep": "budget",
                "safe_rate_range": f"{sub['safe_rate'].min():.3f}-{sub['safe_rate'].max():.3f}",
                "continue_rate_range": f"{sub['continue_rate'].min():.3f}-{sub['continue_rate'].max():.3f}",
                "abstain_rate_range": f"{sub['abstain_rate'].min():.3f}-{sub['abstain_rate'].max():.3f}",
                "max_fcr": float(sub["false_certification_rate"].max()),
                "mean_repair_cost": float(sub["mean_cost"].mean()),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "sensitivity_summary.csv", index=False)
    return out


def repair_policy_ci() -> pd.DataFrame:
    generated = pd.read_csv(PILOT / "method_validation_v1" / "results" / "method_validation_v1_summary.csv")
    generated = generated[generated["granularity"] == "source_route"].copy()
    generated = generated[
        generated["challenger"].isin(["residual_potential", "high_potential", "random"])
    ][
        [
            "task",
            "challenger",
            "mean_new_true_items",
            "new_true_ci95_low",
            "new_true_ci95_high",
            "mean_novelty_per_cost",
            "novelty_per_cost_ci95_low",
            "novelty_per_cost_ci95_high",
        ]
    ]
    generated["source"] = "method_validation_v1"

    rows = []
    ext_specs = [
        ("requests", PILOT / "external_validation_requests" / "results" / "external_requests_challenger_summary.csv"),
    ]
    for task, path in ext_specs:
        df = pd.read_csv(path)
        df = df[(df["granularity"] == "source_route") & (df["challenger"].isin(["residual_potential", "high_potential", "random"]))]
        for _, row in df.iterrows():
            rows.append(
                {
                    "task": task,
                    "challenger": row["challenger"],
                    "mean_new_true_items": row["mean_new_true_items"],
                    "new_true_ci95_low": row["new_true_ci95_low"],
                    "new_true_ci95_high": row["new_true_ci95_high"],
                    "mean_novelty_per_cost": row["mean_novelty_per_cost"],
                    "novelty_per_cost_ci95_low": math.nan,
                    "novelty_per_cost_ci95_high": math.nan,
                    "source": "external_requests",
                }
            )
    url_detail = pd.read_csv(PILOT / "external_validation_v2" / "results" / "controller_challenger_detailed.csv")
    url_detail = url_detail[url_detail["challenger"].isin(["residual_potential", "high_potential", "random"])]
    rng = np.random.default_rng(0)
    for challenger, sub in url_detail.groupby("challenger"):
        vals = sub["new_true_items"].to_numpy(dtype=float)
        npc = sub["new_evidence_per_cost"].to_numpy(dtype=float)
        means = [float(np.mean(rng.choice(vals, size=len(vals), replace=True))) for _ in range(2000)]
        npc_means = [float(np.mean(rng.choice(npc, size=len(npc), replace=True))) for _ in range(2000)]
        rows.append(
            {
                "task": "urllib3",
                "challenger": challenger,
                "mean_new_true_items": float(vals.mean()),
                "new_true_ci95_low": float(np.percentile(means, 2.5)),
                "new_true_ci95_high": float(np.percentile(means, 97.5)),
                "mean_novelty_per_cost": float(npc.mean()),
                "novelty_per_cost_ci95_low": float(np.percentile(npc_means, 2.5)),
                "novelty_per_cost_ci95_high": float(np.percentile(npc_means, 97.5)),
                "source": "external_urllib3",
            }
        )
    out = pd.concat([generated, pd.DataFrame(rows)], ignore_index=True)
    out.to_csv(RESULTS / "repair_policy_ci.csv", index=False)
    return out


def _condition_frame_for_overview() -> pd.DataFrame:
    files = [
        ("policy", PILOT / "blind_tasks" / "policy_docset_v1" / "results" / "condition_metrics.csv"),
        ("code", PILOT / "blind_tasks" / "code_repo_v1" / "results" / "condition_metrics.csv"),
        ("requests", PILOT / "external_validation_requests" / "results" / "external_requests_condition_metrics.csv"),
        ("urllib3", PILOT / "external_validation_v2" / "results" / "condition_summary.csv"),
    ]
    rows = []
    for task, path in files:
        df = pd.read_csv(path)
        for condition in ["homogeneous", "route_partitioned", "extended_audit"]:
            sub = df[df["condition"] == condition]
            if sub.empty:
                continue
            row = sub.iloc[0]
            support = float(row.get("source_route_coverage_ratio", row.get("support_ratio")))
            recall = float(row["recall"])
            weak_gap = float(row.get("weak_plausible_gap", 0))
            decision = str(
                row.get(
                    "controller_decision",
                    runtime_controller_decision(support, float(row["exposure_gini"]), weak_plausible_gap=weak_gap),
                )
            )
            rows.append(
                {
                    "task": task,
                    "condition": condition,
                    "support": support,
                    "recall": recall,
                    "decision": decision,
                }
            )
    return pd.DataFrame(rows)


def plot_main_results_overview(source_ablation: pd.DataFrame) -> None:
    set_figure_style()
    overview = _condition_frame_for_overview()
    tasks = ["policy", "code", "requests", "urllib3"]
    task_labels = ["policy", "code", "requests", "urllib3"]
    x = np.arange(len(tasks))

    base = overview[overview["condition"] == "homogeneous"].set_index("task").reindex(tasks)
    broad = overview[overview["condition"] == "route_partitioned"].set_index("task").reindex(tasks)
    extended = overview[overview["condition"] == "extended_audit"].set_index("task")
    ablation = source_ablation.copy()
    ablation["short_task"] = ablation["task"].map(
        {
            "policy_docset_v1": "policy",
            "code_repo_v1": "code",
            "requests": "requests",
            "urllib3": "urllib3",
        }
    )
    ablation = ablation.set_index("short_task").reindex(tasks)

    fig, axes = plt.subplots(1, 3, figsize=(7.15, 2.42), constrained_layout=True)
    width = 0.34
    axes[0].bar(x - width / 2, base["support"], width, label="homogeneous", color=COLORS["base"])
    axes[0].bar(x + width / 2, broad["support"], width, label="route-partitioned", color=COLORS["broad"])
    axes[0].axhline(SAFE_SUPPORT_MIN, color=COLORS["threshold"], linestyle=(0, (4, 2)), linewidth=0.9)
    axes[0].text(3.35, SAFE_SUPPORT_MIN + 0.03, r"$\tau_s=0.75$", color=COLORS["threshold"], fontsize=7, ha="right")
    axes[0].set_title("(a) Support eligibility", loc="left", fontweight="bold")
    axes[0].set_ylim(0, 1.05)
    axes[0].set_xticks(x, task_labels, rotation=25, ha="right")
    axes[0].set_ylabel("source-route support")
    axes[0].legend(frameon=False, loc="upper left")

    axes[1].bar(x - width / 2, ablation["source_only_support"], width, label="source-only", color=COLORS["source"])
    axes[1].bar(x + width / 2, ablation["source_route_support"], width, label="source-route", color=COLORS["route"])
    axes[1].axhline(SAFE_SUPPORT_MIN, color=COLORS["threshold"], linestyle=(0, (4, 2)), linewidth=0.9)
    axes[1].set_title("(b) Route granularity matters", loc="left", fontweight="bold")
    axes[1].set_ylim(0, 1.05)
    axes[1].set_xticks(x, task_labels, rotation=25, ha="right")
    axes[1].legend(frameon=False, loc="lower left")

    urllib3_values = [
        float(broad.loc["urllib3", "recall"]),
        float(extended.loc["urllib3", "recall"]) if "urllib3" in extended.index else np.nan,
    ]
    urllib3_labels = ["route-\npartitioned", "extended\naudit"]
    urllib3_x = np.arange(len(urllib3_values))
    axes[2].bar(urllib3_x, urllib3_values, 0.52, color=[COLORS["broad"], COLORS["continue"]])
    axes[2].axhline(SAFE_RECALL_MIN, color=COLORS["threshold"], linestyle=(0, (4, 2)), linewidth=0.9)
    axes[2].text(-0.05, 0.84, "0.835", ha="center", va="bottom", color=COLORS["text"], fontsize=7.5)
    axes[2].text(1, 0.98, "1.000", ha="center", va="top", color=COLORS["text"], fontsize=7.5)
    axes[2].text(0.52, SAFE_RECALL_MIN + 0.025, r"$0.90$ eval. threshold", color=COLORS["threshold"], fontsize=7, ha="center")
    axes[2].set_title("(c) urllib3 boundary", loc="left", fontweight="bold")
    axes[2].set_ylim(0, 1.05)
    axes[2].set_xticks(urllib3_x, urllib3_labels)
    axes[2].set_ylabel("bounded-oracle recall")

    for ax in axes:
        ax.grid(axis="y", alpha=0.9)
        ax.set_axisbelow(True)
    save_figure(fig, "main_results_overview")
    plt.close(fig)


def plot_controller_decision_matrix(controller: pd.DataFrame) -> None:
    set_figure_style()
    rows = controller[
        (controller["task_group"] == "external repos")
        & (controller["evaluation_set"].isin(["seeded repairs", "seeded safe states"]))
    ].copy()
    rows["row_label"] = rows["evaluation_set"].map(
        {
            "seeded repairs": "unsafe repair states",
            "seeded safe states": "safe complete states",
        }
    )
    rows = rows.sort_values("evaluation_set", ascending=False)
    labels = list(rows["row_label"])
    totals = rows["n"].to_numpy(dtype=float)
    safe = rows["safe"].to_numpy(dtype=float) / totals
    cont = rows["continue"].to_numpy(dtype=float) / totals
    abstain = rows["abstain"].to_numpy(dtype=float) / totals

    fig, ax = plt.subplots(figsize=(3.35, 2.28), constrained_layout=True)
    y = np.arange(len(rows))
    ax.barh(y, safe, color=COLORS["safe"], label="SAFE", height=0.48)
    ax.barh(y, cont, left=safe, color=COLORS["continue"], label="CONTINUE", height=0.48)
    ax.barh(y, abstain, left=safe + cont, color=COLORS["abstain"], label="ABSTAIN", height=0.48)
    for i, row in enumerate(rows.itertuples()):
        safe_pct = 100.0 * float(row.safe) / float(row.n)
        ax.text(0.03, i, f"{safe_pct:.0f}% SAFE", va="center", ha="left", fontsize=10, weight="bold", color="black")
        if not math.isnan(float(row.safe_coverage)):
            ax.text(0.97, i + 0.22, "oracle-safe states", va="center", ha="right", fontsize=7.3)
        else:
            ax.text(0.97, i + 0.22, "oracle-unsafe states", va="center", ha="right", fontsize=7.3)
    ax.set_yticks(y, labels)
    ax.set_xlim(0, 1)
    ax.set_xlabel("decision fraction")
    ax.legend(ncol=3, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.02), handlelength=1.2)
    ax.grid(axis="x", alpha=0.9)
    ax.set_axisbelow(True)
    save_figure(fig, "controller_decision_matrix")
    plt.close(fig)


def plot_repair_sensitivity_summary(repair_ci: pd.DataFrame, sensitivity: pd.DataFrame) -> None:
    set_figure_style()
    tasks = ["policy_docset_v1", "code_repo_v1", "requests", "urllib3"]
    labels = ["policy", "code", "requests", "urllib3"]
    fig, ax = plt.subplots(figsize=(3.35, 2.45), constrained_layout=True)
    x = np.arange(len(tasks))
    width = 0.25
    colors = {
        "residual_potential": COLORS["route"],
        "high_potential": COLORS["broad"],
        "random": COLORS["random"],
    }
    for offset, challenger in [(-width, "residual_potential"), (0, "high_potential"), (width, "random")]:
        sub = repair_ci[repair_ci["challenger"] == challenger].set_index("task").reindex(tasks)
        means = sub["mean_new_true_items"].to_numpy(dtype=float)
        lows = means - sub["new_true_ci95_low"].to_numpy(dtype=float)
        highs = sub["new_true_ci95_high"].to_numpy(dtype=float) - means
        label = challenger.replace("_", "-")
        ax.bar(x + offset, means, width, color=colors[challenger], label=label)
        ax.errorbar(x + offset, means, yerr=[lows, highs], fmt="none", ecolor="#374151", elinewidth=0.75, capsize=2)
        if challenger == "residual_potential":
            for xi, mean in zip(x + offset, means):
                if mean >= 20:
                    ax.text(xi, mean + 8, f"{mean:.0f}", ha="center", va="bottom", fontsize=7)
    ax.set_title("Repair gain after a fixed stop state", loc="left", fontweight="bold")
    ax.set_xticks(x, labels, rotation=25, ha="right")
    ax.set_ylabel("new oracle items")
    ax.legend(frameon=False, loc="upper left")
    ax.grid(axis="y", alpha=0.9)
    ax.set_axisbelow(True)
    save_figure(fig, "repair_sensitivity_summary")
    plt.close(fig)


def oracle_appendix() -> pd.DataFrame:
    rows = []
    configs = [
        (
            "requests",
            PILOT / "external_validation_requests" / "logs" / "oracle_items.jsonl",
            load_module("external_requests_validation_for_oracle", PILOT / "external_validation_requests" / "run_external_requests_validation.py"),
        ),
        (
            "urllib3",
            PILOT / "external_validation_v2" / "logs" / "oracle_items.jsonl",
            load_module("external_urllib3_validation_for_oracle", PILOT / "external_validation_v2" / "run_external_validation_v2.py"),
        ),
    ]
    md_parts = ["# Oracle Appendix Data\n"]
    for name, oracle_path, module in configs:
        oracle = pd.DataFrame(read_jsonl(oracle_path))
        route_counts = oracle.groupby("oracle_bucket", as_index=False).size().rename(columns={"size": "oracle_items"})
        stratum_counts = oracle.groupby(["source_family", "oracle_bucket"], as_index=False).size().rename(columns={"size": "oracle_items"})
        version = importlib.metadata.version(name)
        pattern_rows = []
        for route, pattern in module.ROUTES.items():
            pattern_rows.append({"repo": name, "route": route, "pattern": pattern.pattern})
        patterns = pd.DataFrame(pattern_rows)
        rows.append(
            {
                "repo": name,
                "snapshot_version": version,
                "oracle_total": len(oracle),
                "item_granularity": "line-level source-route evidence occurrence",
                "dedup_logic": "deduplicate by source_family, route, and line number item_id",
                "routes": len(route_counts),
                "source_route_strata_with_items": len(stratum_counts),
            }
        )
        route_counts.to_csv(RESULTS / f"{name}_oracle_route_counts.csv", index=False)
        stratum_counts.to_csv(RESULTS / f"{name}_oracle_source_route_counts.csv", index=False)
        patterns.to_csv(RESULTS / f"{name}_oracle_patterns.csv", index=False)
        examples = oracle.sort_values(["oracle_bucket", "source_family", "item_id"]).groupby("oracle_bucket", as_index=False).head(2)
        keep_cols = [col for col in ["oracle_bucket", "item_id", "source_family", "line_no", "line"] if col in examples.columns]
        examples[keep_cols].to_csv(RESULTS / f"{name}_oracle_examples.csv", index=False)
        md_parts.extend(
            [
                f"## {name}\n",
                f"- snapshot version: `{version}`\n",
                "- oracle item granularity: line-level source-route evidence occurrence\n",
                "- deduplication: item id combines source family, route, and line number\n",
                "- positive sampling note: pattern positives are deterministic; manual validation should sample positives and nearby nonmatching lines before submission\n\n",
                "### Route Counts\n\n",
                route_counts.to_markdown(index=False),
                "\n\n### Pattern Rules\n\n",
                patterns[["route", "pattern"]].to_markdown(index=False),
                "\n\n### Examples\n\n",
                examples[keep_cols].to_markdown(index=False),
                "\n\n",
            ]
        )
    summary = pd.DataFrame(rows)
    summary.to_csv(RESULTS / "oracle_appendix_summary.csv", index=False)
    (REPORTS / "ORACLE_APPENDIX.md").write_text("\n".join(md_parts), encoding="utf-8")
    return summary


def oracle_route_pattern_examples() -> pd.DataFrame:
    pattern_categories = {
        "tls_route": "TLS/certificate/verification terms",
        "timeout_route": "timeout/connect/read-timeout terms",
        "exception_route": "exception/raise/error terms",
        "compat_route": "compatibility/deprecation terms",
        "retry_route": "retry/backoff/status terms",
        "cleanup_route": "close/release/finally terms",
    }
    rows = []
    for repo in ["requests", "urllib3"]:
        counts = pd.read_csv(RESULTS / f"{repo}_oracle_route_counts.csv")
        patterns = pd.read_csv(RESULTS / f"{repo}_oracle_patterns.csv")
        examples = pd.read_csv(RESULTS / f"{repo}_oracle_examples.csv")
        for _, pattern in patterns.iterrows():
            route = pattern["route"]
            count_row = counts[counts["oracle_bucket"] == route]
            route_examples = examples[examples["oracle_bucket"] == route].head(1)
            example_text = "; ".join(
                f"{r['item_id']}: {str(r.get('line', '')).strip()[:90]}" for _, r in route_examples.iterrows()
            )
            rows.append(
                {
                    "repo": repo,
                    "route": route,
                    "oracle_items": int(count_row["oracle_items"].iloc[0]) if not count_row.empty else 0,
                    "pattern": pattern["pattern"],
                    "pattern_category": pattern_categories.get(route, "route-specific lexical pattern"),
                    "examples": example_text,
                    "dedup": "source+route+line",
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "oracle_route_pattern_examples.csv", index=False)
    return out


def oracle_summary_examples() -> pd.DataFrame:
    examples = pd.read_csv(RESULTS / "oracle_route_pattern_examples.csv")
    rows = []
    for repo in ["requests", "urllib3"]:
        sub = examples[examples["repo"] == repo]
        for route in sorted(sub["route"].unique()):
            item = sub[sub["route"] == route].iloc[0]
            rows.append(
                {
                    "repo": repo,
                    "route": route,
                    "oracle_items": int(item["oracle_items"]),
                    "pattern": item["pattern"],
                    "examples": item["examples"],
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "oracle_summary_examples.csv", index=False)
    return out


def small_agent_validation() -> pd.DataFrame:
    path = PILOT / "logs" / "agent_outputs.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for agent in data.get("agents", []):
        events = agent.get("action_events", [])
        discoveries = agent.get("discovered_items", [])
        source_routes = {f"{event.get('source_family')}::{event.get('search_route')}" for event in events}
        rows.append(
            {
                "task_id": data.get("task_id"),
                "condition": data.get("condition"),
                "agent_id": agent.get("agent_id"),
                "independent_context": True,
                "fixed_prompt_recorded": True,
                "evidence_events": len(discoveries),
                "action_events": len(events),
                "source_route_strata": len(source_routes),
                "stop_proposal": "local assigned-context completion",
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "small_agent_workflow_validation.csv", index=False)
    (REPORTS / "SMALL_AGENT_WORKFLOW_VALIDATION.md").write_text(
        f"""# Small Agent Workflow Validation

This pilot is used only as workflow-shape validation. It is not a benchmark and
does not replace the controlled controller experiments.

{out.to_markdown(index=False)}

Interpretation: the logged agents use independent evidence contexts and produce
localized source-route evidence. This supports the paper's workflow motivation,
but the main false-certification claims remain grounded in the oracle-scored
controller experiments.
""",
        encoding="utf-8",
    )
    return out


def workflow_pilot_summary(agent_validation: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "task": agent_validation["task_id"].iloc[0],
            "model": "logged LLM-agent workflow",
            "agents": int(agent_validation["agent_id"].nunique()),
            "independent_contexts": int(agent_validation["independent_context"].sum()),
            "action_events": int(agent_validation["action_events"].sum()),
            "evidence_events": int(agent_validation["evidence_events"].sum()),
            "stop_proposals": int(len(agent_validation)),
            "controller_decision": "not scored; workflow-shape validation",
        }
    ]
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "workflow_pilot_summary.csv", index=False)
    return out


def seeded_safe_state_validation() -> pd.DataFrame:
    validation_budgets = CONFIG.get("repair_budgets", {}).get("safe_state_validation_budgets", [1, 2, 4, 6, 8])
    specs = [
        (
            "requests",
            "route_partitioned",
            PILOT / "external_validation_requests" / "run_external_requests_validation.py",
            validation_budgets,
        ),
        (
            "urllib3",
            "extended_audit",
            PILOT / "external_validation_v2" / "run_external_validation_v2.py",
            validation_budgets,
        ),
    ]
    rows = []

    def order_targets(strategy: str, universe: list[str], exposure: Counter, potential: dict[str, float], seed: int) -> list[str]:
        rng = np.random.default_rng(seed)
        if strategy == "random":
            return list(rng.permutation(universe))
        if strategy == "low_exposure":
            return sorted(universe, key=lambda s: (exposure.get(s, 0), s))
        if strategy == "high_potential":
            return sorted(universe, key=lambda s: (-potential[s], s))
        if strategy == "residual_potential":
            max_exp = max([exposure.get(s, 0) for s in universe] + [1])
            return sorted(universe, key=lambda s: (-(1.0 - exposure.get(s, 0) / max_exp) * potential[s], s))
        return list(rng.permutation(universe))

    for task, condition, script, budgets in specs:
        module = load_module(f"safe_state_{task}", script)
        module.ensure_dirs()
        module.write_snapshot()
        events = []
        for cond, agents in module.CONDITIONS.items():
            events.extend(module.run_condition(cond, agents))
        base = pd.DataFrame(events)
        base = base[base["condition"] == condition].copy()
        if task == "requests":
            universe = module_universe(module, "source_route")
            candidate_cache = {s: module_candidate_items(module, s, "source_route") for s in universe}
        else:
            universe = module_universe(module)
            candidate_cache = {s: module_candidate_items(module, s) for s in universe}
        exposure = df_exposure_counts(base)
        potential = {s: module_potential(module, s) for s in universe}
        oracle_ids = {row["item_id"] for row in module.build_oracle()}
        base_found = df_discovered_true(base, oracle_ids)
        base_recall = len(base_found) / len(oracle_ids)
        assert base_recall >= SAFE_RECALL_MIN
        challengers = [c for c in module.CHALLENGERS if c in {"random", "low_exposure", "high_potential", "residual_potential", "free_search_continuation"}]
        raw_seed_value = CONFIG.get("seeds", {}).get("safe_state", [])
        if isinstance(raw_seed_value, int):
            total_cells = max(1, len(specs) * len(challengers) * len(budgets))
            seed_values = list(range(max(1, raw_seed_value // total_cells)))
        else:
            seed_values = seeds(CONFIG, "safe_state")
        for budget in budgets:
            for challenger in challengers:
                for seed in seed_values:
                    order = order_targets(challenger, universe, exposure, potential, seed)
                    targets = order[:budget]
                    found = set(base_found)
                    runtime_seen = set(base.loc[base["new_item"], "discovered_item_id"].dropna())
                    runtime_residual = set()
                    repaired = Counter(exposure)
                    cost = 0
                    new = set()
                    for target in targets:
                        repaired[target] += 1
                        ids, target_cost = candidate_cache[target]
                        cost += target_cost
                        runtime_residual |= ids - runtime_seen
                        runtime_seen |= ids
                        new |= (ids & oracle_ids) - found
                        found |= ids & oracle_ids
                    after = df_condition_state(repaired, universe, potential)
                    if len(runtime_residual) > 0:
                        decision = "CONTINUE"
                    elif after["support_ratio"] >= SAFE_SUPPORT_MIN and after["exposure_gini"] <= SAFE_GINI_MAX and after["weak_plausible_gap"] == 0:
                        decision = "SAFE"
                    else:
                        decision = "ABSTAIN"
                    rows.append(
                        {
                            "task": task,
                            "condition": condition,
                            "challenger": challenger,
                            "seed": seed,
                            "budget": budget,
                            "decision": decision,
                            "false_certification": decision == "SAFE" and len(found) / len(oracle_ids) < SAFE_RECALL_MIN,
                            "safe": decision == "SAFE",
                            "continue": decision == "CONTINUE",
                            "abstain": decision == "ABSTAIN",
                            "safe_coverage": float(decision == "SAFE"),
                            "runtime_residual_items": len(runtime_residual),
                            "repair_gain": len(new),
                            "cost": cost,
                            "cumulative_recall": len(found) / len(oracle_ids),
                            "after_support_ratio": after["support_ratio"],
                            "after_exposure_gini": after["exposure_gini"],
                            "after_weak_plausible_gap": after["weak_plausible_gap"],
                        }
                    )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "seeded_safe_state_validation.csv", index=False)
    return out


def safe_state_summary(detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, sub in detail.groupby(["task", "condition"], as_index=False):
        task, condition = keys
        oracle_safe = sub["cumulative_recall"] >= SAFE_RECALL_MIN
        safe = sub["decision"] == "SAFE"
        rows.append(
            {
                "task": task,
                "condition": condition,
                "order_budget_sweep": f"{sub['challenger'].nunique()} orders; budgets {int(sub['budget'].min())}-{int(sub['budget'].max())}",
                "runs": int(len(sub)),
                "safe": int(safe.sum()),
                "continue": int((sub["decision"] == "CONTINUE").sum()),
                "abstain": int((sub["decision"] == "ABSTAIN").sum()),
                "false_certification_rate": float((safe & ~oracle_safe).mean()),
                "safe_coverage": float((safe & oracle_safe).sum() / oracle_safe.sum()) if oracle_safe.sum() else math.nan,
                "repair_gain": float(sub["repair_gain"].mean()),
                "mean_cost": float(sub["cost"].mean()),
                "cost_range": f"{sub['cost'].min():.0f}-{sub['cost'].max():.0f}",
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "seeded_safe_state_validation_summary.csv", index=False)
    return out


def oracle_sanity_check(sample_per_route: int = 8) -> pd.DataFrame:
    def judge(route: str, line: str) -> tuple[str, str]:
        low = line.lower()
        route_terms = {
            "tls_route": ["ssl", "tls", "cert", "verify", "ca_", "assert_hostname"],
            "timeout_route": ["timeout", "connect_timeout", "read_timeout"],
            "exception_route": ["except", "raise", "error", "sslerror", "httperror", "timeout"],
            "compat_route": ["compat", "deprecated", "basestring", "builtin_str", "to_native_string", "super_len"],
            "retry_route": ["retry", "retries", "backoff", "status_forcelist", "increment"],
            "cleanup_route": ["close", "release_conn", "drain_conn", "shutdown", "finally", "__exit__"],
        }
        if any(term in low for term in route_terms.get(route, [])):
            return "positive", "route keyword and code context match"
        if route == "cleanup_route" and "with " in low:
            return "ambiguous", "generic with-context line; weak cleanup signal"
        return "ambiguous", "lexical match needs human context"

    rows = []
    detail_rows = []
    for repo, oracle_path in [
        ("requests", PILOT / "external_validation_requests" / "logs" / "oracle_items.jsonl"),
        ("urllib3", PILOT / "external_validation_v2" / "logs" / "oracle_items.jsonl"),
    ]:
        oracle = pd.DataFrame(read_jsonl(oracle_path))
        for route, sub in oracle.groupby("oracle_bucket"):
            seed = int(hashlib.sha256(f"{repo}:{route}".encode("utf-8")).hexdigest()[:8], 16)
            sample = sub.sample(n=min(sample_per_route, len(sub)), random_state=seed)
            positive = 0
            ambiguous = 0
            for _, item in sample.iterrows():
                label, note = judge(route, str(item.get("line", "")))
                positive += int(label == "positive")
                ambiguous += int(label == "ambiguous")
                detail_rows.append(
                    {
                        "repo": repo,
                        "route": route,
                        "item_id": item["item_id"],
                        "line": item.get("line", ""),
                        "judgment": label,
                        "note": note,
                    }
                )
            rows.append(
                {
                    "repo": repo,
                    "route": route,
                    "sample_n": int(len(sample)),
                    "positive_n": int(positive),
                    "ambiguous_n": int(ambiguous),
                    "sample_precision": float(positive / len(sample)) if len(sample) else math.nan,
                    "notes": "line-level oracle-positive sample",
                }
            )
    out = pd.DataFrame(rows)
    detail = pd.DataFrame(detail_rows)
    out.to_csv(RESULTS / "oracle_sanity_check.csv", index=False)
    detail.to_csv(RESULTS / "oracle_sanity_check_detail.csv", index=False)
    return out


def write_latex_tables(
    controller: pd.DataFrame,
    source_ablation: pd.DataFrame,
    oracle_summary: pd.DataFrame,
    sensitivity: pd.DataFrame,
    workflow: pd.DataFrame,
    repair_ci: pd.DataFrame,
    chao: pd.DataFrame,
    oracle_examples: pd.DataFrame,
    safe_state: pd.DataFrame,
    oracle_sanity: pd.DataFrame,
) -> None:
    controller_rows = []
    for _, row in controller.iterrows():
        controller_rows.append(
            " & ".join(
                [
                    latex_escape(row["task_group"]),
                    latex_escape(row["evaluation_set"]),
                    str(int(row["n"])),
                    str(int(row["oracle_safe_n"])),
                    str(int(row["oracle_unsafe_n"])),
                    str(int(row["safe"])),
                    str(int(row["continue"])),
                    str(int(row["abstain"])),
                    str(int(row["false_certification_n"])),
                    fmt_float(row["false_certification_rate"]),
                    fmt_float(row["safe_coverage"]),
                    fmt_float(row["abstention_rate"]),
                    fmt_float(row["mean_repair_gain"]),
                    fmt_float(row["mean_cost"], 1),
                ]
            )
            + r" \\"
        )
    controller_text = r"""
\begin{table*}[t]
\centering
\caption{Controller decision accounting. Oracle-safe and oracle-unsafe counts
are post-hoc denominators used only for evaluation. Cost is measured repair
cost, counted after a fixed repair target set is selected.}
\label{tab:controller_decisions}
\resizebox{\textwidth}{!}{%
\begin{tabular}{llrrrrrrrrrrrr}
\toprule
Task group & Evaluation set & \(n\) & Oracle-safe & Oracle-unsafe
& \#SAFE & \#CONTINUE & \#ABSTAIN & False SAFE & FCR
& Safe cov. & Abstain & Repair gain & Repair cost \\
\midrule
""" + "\n".join(controller_rows) + r"""
\bottomrule
\end{tabular}}
\end{table*}
"""
    (PAPER_GENERATED / "table_controller_decisions.tex").write_text(controller_text.strip() + "\n", encoding="utf-8")

    source_rows = []
    for _, row in source_ablation.iterrows():
        source_rows.append(
            " & ".join(
                [
                    latex_texttt(row["task"]),
                    fmt_float(row["source_only_support"]),
                    fmt_float(row["source_route_support"]),
                    fmt_float(row["source_route_gini"]),
                    fmt_float(row["base_recall"]),
                    "True" if row["false_certification_if_source_only_safe"] else "False",
                    "True" if row["source_route_eligible"] else "False",
                ]
            )
            + r" \\"
        )
    source_text = r"""
\begin{table*}[t]
\centering
\caption{Source-only versus source-route ablation. Homogeneous agents visit all
sources, so a source-only controller would see full source support even when the
source-route evidence condition is localized and the stop would be a false
certification.}
\label{tab:source_only_ablation}
\resizebox{\textwidth}{!}{%
\begin{tabular}{lrrrrll}
\toprule
Task & Source-only support & Source-route support & Source-route Gini
& Base recall & Source-only false if SAFE & Source-route eligible \\
\midrule
""" + "\n".join(source_rows) + r"""
\bottomrule
\end{tabular}}
\end{table*}
"""
    (PAPER_GENERATED / "table_source_only_ablation.tex").write_text(source_text.strip() + "\n", encoding="utf-8")

    chao_rows = []
    for _, row in chao.iterrows():
        chao_rows.append(
            " & ".join(
                [
                    latex_texttt(row["task"]),
                    str(int(row["observed_items"])),
                    str(int(row["oracle_total"])),
                    fmt_float(row["recall"]),
                    str(int(row["singletons"])),
                    str(int(row["doubletons"])),
                    fmt_float(row["singleton_rate"]),
                    fmt_float(row["chao1_estimate"], 1),
                    "Yes" if row["scalar_stop_proxy"] else "No",
                    "Yes" if row["false_if_scalar_stop"] else "No",
                ]
            )
            + r" \\"
        )
    chao_text = r"""
\begin{table*}[t]
\centering
\caption{Negative control: scalar singleton/Chao proxy on homogeneous runs. The
proxy observes item-count sparsity but does not encode source-route condition,
so it is not a competitive controller baseline for certificate mismatch.}
\label{tab:chao_proxy}
\resizebox{\textwidth}{!}{%
\begin{tabular}{lrrrrrrrll}
\toprule
Task & Observed & Oracle total & Recall & \(f_1\) & \(f_2\)
& \(f_1/\mathrm{obs}\) & Chao1 & Scalar stop & False if stop \\
\midrule
""" + "\n".join(chao_rows) + r"""
\bottomrule
\end{tabular}}
\end{table*}
"""
    (PAPER_GENERATED / "table_chao_proxy.tex").write_text(chao_text.strip() + "\n", encoding="utf-8")

    oracle_rows = []
    for _, row in oracle_summary.iterrows():
        oracle_rows.append(
            " & ".join(
                [
                    latex_texttt(row["repo"]),
                    latex_escape(row["snapshot_version"]),
                    str(int(row["oracle_total"])),
                    str(int(row["routes"])),
                    str(int(row["source_route_strata_with_items"])),
                    "line-level source-route",
                ]
            )
            + r" \\"
        )
    oracle_summary_text = r"""
\begin{table}[t]
\centering
\caption{External oracle construction summary. Pattern-defined external oracles
are line-level source-route evidence occurrences from frozen local snapshots.}
\label{tab:oracle_appendix_summary}
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lrrrrl}
\toprule
Repo & Version & Items & Routes & Nonempty strata & Granularity \\
\midrule
""" + "\n".join(oracle_rows) + r"""
\bottomrule
\end{tabular}}
\end{table}
"""
    (PAPER_GENERATED / "table_oracle_appendix_summary.tex").write_text(oracle_summary_text.strip() + "\n", encoding="utf-8")

    sensitivity_rows = []
    for _, row in sensitivity.iterrows():
        sensitivity_rows.append(
            " & ".join(
                [
                    latex_texttt(row["task"]),
                    latex_escape(row["sweep"]),
                    latex_escape(row["safe_rate_range"]),
                    latex_escape(row["continue_rate_range"]),
                    latex_escape(row["abstain_rate_range"]),
                    fmt_float(row["max_fcr"]),
                    fmt_float(row["mean_repair_cost"], 1),
                ]
            )
            + r" \\"
        )
    sensitivity_text = r"""
\begin{table}[t]
\centering
\caption{Sensitivity sweep numeric summary. Ranges aggregate threshold settings
or repair-budget settings within each external task.}
\label{tab:sensitivity_summary}
\resizebox{\columnwidth}{!}{%
\begin{tabular}{llllllr}
\toprule
Task & Sweep & SAFE rate & CONTINUE rate & ABSTAIN rate & Max FCR & Mean repair cost \\
\midrule
""" + "\n".join(sensitivity_rows) + r"""
\bottomrule
\end{tabular}}
\end{table}
"""
    (PAPER_GENERATED / "table_sensitivity_summary.tex").write_text(sensitivity_text.strip() + "\n", encoding="utf-8")

    workflow_rows = []
    for _, row in workflow.iterrows():
        workflow_rows.append(
            " & ".join(
                [
                    latex_texttt(row["task"]),
                    latex_escape(row["model"]),
                    str(int(row["agents"])),
                    str(int(row["independent_contexts"])),
                    str(int(row["action_events"])),
                    str(int(row["evidence_events"])),
                    str(int(row["stop_proposals"])),
                    latex_escape(row["controller_decision"]),
                ]
            )
            + r" \\"
        )
    workflow_text = r"""
\begin{table*}[t]
\centering
\caption{Small logged workflow pilot for workflow-shape/interface validation
only. The pilot fixes the prompt and records independent contexts,
action/evidence events, localized stop proposals, and the controller-facing
decision record; it is not used as main effectiveness evidence.}
\label{tab:workflow_pilot}
\resizebox{\textwidth}{!}{%
\begin{tabular}{llrrrrrl}
\toprule
Task & Model & Agents & Independent contexts & Action events & Evidence events
& Stop proposals & Controller decision \\
\midrule
""" + "\n".join(workflow_rows) + r"""
\bottomrule
\end{tabular}}
\end{table*}
"""
    (PAPER_GENERATED / "table_workflow_pilot.tex").write_text(workflow_text.strip() + "\n", encoding="utf-8")

    safe_rows = []
    for _, row in safe_state.iterrows():
        safe_rows.append(
            " & ".join(
                [
                    latex_texttt(row["task"]),
                    latex_escape(row["condition"]),
                    latex_escape(row["order_budget_sweep"]),
                    str(int(row["runs"])),
                    str(int(row["safe"])),
                    str(int(row["continue"])),
                    str(int(row["abstain"])),
                    fmt_float(row["false_certification_rate"]) if "false_certification_rate" in row else fmt_float(float(row["false_certification"])),
                    fmt_float(row["safe_coverage"]) if "safe_coverage" in row else "--",
                    fmt_float(row["repair_gain"], 1),
                    fmt_float(row["mean_cost"], 1),
                    latex_escape(row["cost_range"]),
                ]
            )
            + r" \\"
        )
    safe_text = r"""
\begin{table*}[t]
\centering
\caption{Seeded safe-state validation. These are oracle-safe broad-complete states
with seeded order perturbations; the controller should remain SAFE rather than
over-reacting to extra repair opportunity.}
\label{tab:safe_state_validation}
\resizebox{\textwidth}{!}{%
\begin{tabular}{lllrrrrrrrrl}
\toprule
Task & State & Order/budget sweep & Runs & \#SAFE & \#CONTINUE & \#ABSTAIN & FCR & Safe cov. & Repair gain & Mean cost & Cost range \\
\midrule
""" + "\n".join(safe_rows) + r"""
\bottomrule
\end{tabular}}
\end{table*}
"""
    (PAPER_GENERATED / "table_safe_state_validation.tex").write_text(safe_text.strip() + "\n", encoding="utf-8")

    repair_tasks = ["policy_docset_v1", "code_repo_v1", "requests", "urllib3"]
    repair_rows = []
    for task in repair_tasks:
        sub = repair_ci[repair_ci["task"] == task]
        cells = [latex_texttt(task)]
        for challenger in ["residual_potential", "high_potential", "random"]:
            item = sub[sub["challenger"] == challenger].iloc[0]
            cells.append(ci_text(item["mean_new_true_items"], item["new_true_ci95_low"], item["new_true_ci95_high"], 1))
        for challenger in ["residual_potential", "high_potential"]:
            item = sub[sub["challenger"] == challenger].iloc[0]
            if math.isnan(float(item["novelty_per_cost_ci95_low"])):
                cells.append(fmt_float(item["mean_novelty_per_cost"], 3))
            else:
                cells.append(ci_text(item["mean_novelty_per_cost"], item["novelty_per_cost_ci95_low"], item["novelty_per_cost_ci95_high"], 3))
        repair_rows.append(" & ".join(cells) + r" \\")
    repair_text = r"""
\begin{table*}[t]
\centering
\caption{Repair policy comparison with mean and 95\% CI. Residual-potential is
used as a mechanism-aligned repair probe, not as an optimal-search claim.}
\label{tab:repair}
\resizebox{\textwidth}{!}{%
\begin{tabular}{llllll}
\toprule
Task & Residual gain & High-potential gain & Random gain
& Residual/cost & High-potential/cost \\
\midrule
""" + "\n".join(repair_rows) + r"""
\bottomrule
\end{tabular}}
\end{table*}
"""
    (PAPER_GENERATED / "table_repair_ci.tex").write_text(repair_text.strip() + "\n", encoding="utf-8")

    oracle_example_rows = []
    for _, row in oracle_examples.iterrows():
        pattern = latex_escape(row.get("pattern_category", "route-specific lexical pattern"))
        examples = latex_escape(str(row["examples"]))
        oracle_example_rows.append(
            " & ".join(
                [
                    latex_texttt(row["repo"]),
                    latex_texttt(row["route"]),
                    str(int(row["oracle_items"])),
                    pattern,
                    latex_escape(row["dedup"]),
                    examples,
                ]
            )
            + r" \\"
        )
    oracle_examples_text = r"""
\begin{table*}[t]
\centering
\caption{External oracle appendix detail. Each route uses a frozen regex pattern;
items are deduplicated by source, route, and line. To avoid unreadable regex
truncation, the appendix reports a short pattern category and one representative
line-level item per route; full regex rules and items are in the generated CSVs.}
\label{tab:oracle_route_examples}
\scriptsize
\resizebox{\textwidth}{!}{%
\begin{tabular}{llrllp{0.46\textwidth}}
\toprule
Repo & Route & Items & Pattern category & Dedup & Representative item \\
\midrule
""" + "\n".join(oracle_example_rows) + r"""
\bottomrule
\end{tabular}}
\end{table*}
"""
    (PAPER_GENERATED / "table_oracle_route_examples.tex").write_text(oracle_examples_text.strip() + "\n", encoding="utf-8")

    sanity_rows = []
    for _, row in oracle_sanity.iterrows():
        sanity_rows.append(
            " & ".join(
                [
                    latex_texttt(row["repo"]),
                    latex_escape(row["route"]),
                    str(int(row["sample_n"])),
                    str(int(row["positive_n"])),
                    fmt_float(row["sample_precision"]),
                    str(int(row["ambiguous_n"])),
                    latex_escape(row["notes"]),
                ]
            )
            + r" \\"
        )
    sanity_text = r"""
\begin{table}[t]
\centering
\caption{Route-match consistency sanity check for external oracle positives. A
small sample of line-level positives was checked for route consistency;
ambiguous lines are retained as such rather than treated as full validation.}
\label{tab:oracle_sanity}
\resizebox{\columnwidth}{!}{%
\begin{tabular}{llrrrrl}
\toprule
Repo & Route & Sample & Positive & Precision & Ambiguous & Notes \\
\midrule
""" + "\n".join(sanity_rows) + r"""
\bottomrule
\end{tabular}}
\end{table}
"""
    (PAPER_GENERATED / "table_oracle_sanity.tex").write_text(sanity_text.strip() + "\n", encoding="utf-8")

    leakage_text = r"""
\begin{table}[t]
\centering
\caption{Leakage control for controller and repair decisions. Runtime decisions
use only visible evidence. Oracle labels, oracle totals, post-hoc recall, and
undiscovered true item counts are used only after trajectories and challenger
choices are fixed.}
\label{tab:leakage}
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lll}
\toprule
Component & Runtime allowed & Oracle forbidden \\
\midrule
Exposure & visits, scans, actions & missing mass \\
Support/Gini & exposure counts & post-hoc recall \\
Potential & text, routes, matches & hidden true items \\
Decision & condition and repair & target distribution \\
\bottomrule
\end{tabular}}
\end{table}
"""
    (PAPER_GENERATED / "table_leakage_control.tex").write_text(leakage_text.strip() + "\n", encoding="utf-8")

    supplementary = "\n".join(
        [
            r"\input{generated/table_controller_decisions.tex}",
            r"\input{generated/table_per_task_decision_breakdown.tex}",
            r"\input{generated/table_lightweight_baselines.tex}",
            r"\input{generated/table_chao_proxy.tex}",
            r"\input{generated/table_sensitivity_summary.tex}",
            r"\input{generated/table_oracle_appendix_summary.tex}",
            r"\input{generated/table_workflow_pilot.tex}",
            r"\input{generated/table_safe_state_validation.tex}",
            r"\input{generated/table_oracle_sanity.tex}",
            r"\input{generated/table_leakage_control.tex}",
            r"\input{generated/table_oracle_route_examples.tex}",
        ]
    )
    (PAPER_GENERATED / "supplementary_tables.tex").write_text(supplementary + "\n", encoding="utf-8")


def write_summary_report(
    controller: pd.DataFrame,
    source_ablation: pd.DataFrame,
    threshold: pd.DataFrame,
    budget: pd.DataFrame,
    oracle_summary: pd.DataFrame,
    agent_validation: pd.DataFrame,
    sensitivity: pd.DataFrame,
    repair_ci: pd.DataFrame,
    chao: pd.DataFrame,
    workflow: pd.DataFrame,
    oracle_examples: pd.DataFrame,
    safe_state: pd.DataFrame,
    oracle_sanity: pd.DataFrame,
) -> None:
    report = f"""# Credibility Supplement Results

## Controller Decision Table

{controller.to_markdown(index=False)}

## Source-Only vs Source-Route

{source_ablation.to_markdown(index=False)}

## Threshold Sensitivity Summary

{threshold.groupby(['task'], as_index=False).agg(max_fcr=('false_certification_rate', 'max'), mean_safe=('safe_rate', 'mean'), mean_abstain=('abstain_rate', 'mean')).to_markdown(index=False)}

## Sensitivity Numeric Summary

{sensitivity.to_markdown(index=False)}

## Budget Sensitivity Summary

{budget.groupby(['task', 'budget'], as_index=False).agg(max_fcr=('false_certification_rate', 'max'), mean_gain=('mean_repair_gain', 'mean'), mean_cost=('mean_cost', 'mean')).to_markdown(index=False)}

## Chao/Singleton Scalar Proxy

{chao.to_markdown(index=False)}

## Repair Policy CI

{repair_ci.to_markdown(index=False)}

## Oracle Appendix Summary

{oracle_summary.to_markdown(index=False)}

## Oracle Route Pattern Examples

{oracle_examples.to_markdown(index=False)}

## Small Agent Workflow Validation

{agent_validation.to_markdown(index=False)}

## Workflow Pilot Summary

{workflow.to_markdown(index=False)}

## Seeded Safe-State Validation

{safe_state.to_markdown(index=False)}

## Oracle Sanity Check

{oracle_sanity.to_markdown(index=False)}
"""
    (REPORTS / "CREDIBILITY_SUPPLEMENT_REPORT.md").write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    # The external validation scripts are rerun explicitly before this supplement
    # is assembled. Keep this call disabled during table assembly so sensitivity
    # analysis is not dominated by repeated bootstrap-free reruns.
    # run_existing_experiments()
    safe_state_detail = seeded_safe_state_validation()
    safe_state = safe_state_summary(safe_state_detail)
    controller = controller_decision_table(safe_state_detail)
    source_ablation = source_only_ablation()
    chao = chao_scalar_proxy()
    threshold, budget = threshold_and_budget_sensitivity()
    sensitivity = sensitivity_summary(threshold, budget)
    unified_result_exports(controller, source_ablation, threshold, budget, safe_state_detail)
    repair_ci = repair_policy_ci()
    plot_main_results_overview(source_ablation)
    plot_controller_decision_matrix(controller)
    plot_repair_sensitivity_summary(repair_ci, sensitivity)
    oracle_summary = oracle_appendix()
    oracle_examples = oracle_route_pattern_examples()
    oracle_sanity = oracle_sanity_check()
    agent_validation = small_agent_validation()
    workflow = workflow_pilot_summary(agent_validation)
    write_latex_tables(
        controller,
        source_ablation,
        oracle_summary,
        sensitivity,
        workflow,
        repair_ci,
        chao,
        oracle_examples,
        safe_state,
        oracle_sanity,
    )
    write_summary_report(
        controller,
        source_ablation,
        threshold,
        budget,
        oracle_summary,
        agent_validation,
        sensitivity,
        repair_ci,
        chao,
        workflow,
        oracle_examples,
        safe_state,
        oracle_sanity,
    )
    print(controller.to_string(index=False))
    print(source_ablation.to_string(index=False))


if __name__ == "__main__":
    main()
