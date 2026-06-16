from __future__ import annotations

import importlib.util
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[4]
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"
SCRIPTS = PILOT / "scripts"
OUT = PILOT / "method_validation_v1"
RESULTS = OUT / "results"
REPORTS = OUT / "reports"

N_SEEDS = 200
BOOTSTRAP_SEEDS = 2000
CHALLENGERS = [
    "random",
    "low_exposure",
    "low_discovery",
    "high_potential",
    "residual_potential",
    "free_search_continuation",
]
GRANULARITIES = ["source_only", "source_route", "source_route_action"]


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ensure_dirs() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)


def build_task_state(module: Any, task_name: str) -> dict[str, Any]:
    module.ensure_dirs()
    module.write_task_files()
    all_events = []
    for condition, agents in module.CONDITIONS.items():
        all_events.extend(module.run_condition(condition, agents))
    base_df = pd.DataFrame(all_events)
    oracle_ids = {item_id for item_id, _, _ in module.ORACLE}
    base = base_df[base_df["condition"] == "homogeneous"].copy()
    found_base = set(base.loc[base["new_item"], "discovered_item_id"].dropna()) & oracle_ids
    return {
        "module": module,
        "task_name": task_name,
        "events": all_events,
        "base_df": base_df,
        "base": base,
        "oracle_ids": oracle_ids,
        "oracle_total": len(oracle_ids),
        "base_true_items": len(found_base),
        "base_recall": len(found_base) / len(oracle_ids),
    }


def file_names(module: Any) -> list[str]:
    if hasattr(module, "DOCSET"):
        return list(module.DOCSET)
    return list(module.FILES)


def suffix(module: Any) -> str:
    return ".md" if hasattr(module, "DOCSET") else ".py"


def routes(module: Any) -> list[str]:
    return list(module.ROUTES)


def source_family(module: Any, name: str) -> str:
    return module.source_family(name)


def stratum_key(module: Any, filename: str, route: str, granularity: str, action: str = "search") -> str:
    source = source_family(module, filename)
    if granularity == "source_only":
        return source
    if granularity == "source_route":
        return f"{source}::{route}"
    if granularity == "source_route_action":
        return f"{source}::{route}::{action}"
    raise ValueError(granularity)


def all_strata(module: Any, granularity: str, actions: list[str] | None = None) -> list[str]:
    actions = actions or ["search"]
    if granularity == "source_only":
        return [source_family(module, name) for name in file_names(module)]
    if granularity == "source_route":
        return [stratum_key(module, name, route, granularity) for name in file_names(module) for route in routes(module)]
    return [
        stratum_key(module, name, route, granularity, action)
        for name in file_names(module)
        for route in routes(module)
        for action in actions
    ]


def event_stratum(event: pd.Series, granularity: str) -> str:
    if granularity == "source_only":
        return str(event["source_family"])
    if granularity == "source_route":
        return f"{event['source_family']}::{event['search_route']}"
    return f"{event['source_family']}::{event['search_route']}::{event['action_type']}"


def potential(module: Any, stratum: str, granularity: str) -> float:
    if granularity == "source_only":
        filename = f"{stratum}{suffix(module)}"
        return sum(module.route_potential(filename, route) for route in routes(module))
    parts = stratum.split("::")
    filename = f"{parts[0]}{suffix(module)}"
    route = parts[1]
    return float(module.route_potential(filename, route))


def candidate_items_for_stratum(module: Any, stratum: str, granularity: str) -> tuple[set[str], int]:
    names = file_names(module)
    route_list = routes(module)
    if granularity == "source_only":
        selected = [(f"{stratum}{suffix(module)}", route) for route in route_list]
    else:
        parts = stratum.split("::")
        selected = [(f"{parts[0]}{suffix(module)}", parts[1])]

    found: set[str] = set()
    cost = 0
    for filename, route in selected:
        if filename not in names:
            continue
        base_dir = module.DOCS if hasattr(module, "DOCS") else module.REPO
        lines = (base_dir / filename).read_text(encoding="utf-8").splitlines()
        cost += len(lines)
        pattern = module.ROUTES[route]
        for line in lines:
            if not pattern.search(line):
                continue
            item_id = module.item_id_from_line(line)
            if item_id:
                found.add(item_id)
    return found, cost


def counts_for_base(state: dict[str, Any], granularity: str) -> tuple[Counter, Counter]:
    exposure: Counter = Counter()
    discovery: Counter = Counter()
    for _, row in state["base"].iterrows():
        if row["source_family"] == "controller":
            continue
        key = event_stratum(row, granularity)
        exposure[key] += 1
        if bool(row["new_item"]):
            discovery[key] += 1
    return exposure, discovery


def select_targets(
    state: dict[str, Any],
    granularity: str,
    challenger: str,
    seed: int,
    budget_k: int = 4,
) -> list[str]:
    module = state["module"]
    universe = all_strata(module, granularity)
    exposure, discovery = counts_for_base(state, granularity)
    potentials = {s: potential(module, s, granularity) for s in universe}
    max_exp = max([exposure.get(s, 0) for s in universe] + [1])
    rng = random.Random(seed)

    if challenger == "random":
        return rng.sample(universe, min(budget_k, len(universe)))
    if challenger == "low_exposure":
        return sorted(universe, key=lambda s: (exposure.get(s, 0), s))[:budget_k]
    if challenger == "low_discovery":
        return sorted(universe, key=lambda s: (discovery.get(s, 0), s))[:budget_k]
    if challenger == "high_potential":
        return sorted(universe, key=lambda s: (-potentials[s], s))[:budget_k]
    if challenger == "residual_potential":
        def score(s: str) -> tuple[float, str]:
            under = 1.0 - (exposure.get(s, 0) / max_exp)
            return (-(under * potentials[s]), s)
        return sorted(universe, key=score)[:budget_k]
    if challenger == "free_search_continuation":
        # Simulates an unguided extra continuation: sample routes with probability
        # proportional to runtime-visible potential only, with no under-exposure term.
        weighted = sorted(universe)
        weights = np.array([potentials[s] + 1e-6 for s in weighted], dtype=float)
        weights = weights / weights.sum()
        np_rng = np.random.default_rng(seed)
        return list(np_rng.choice(weighted, size=min(budget_k, len(weighted)), replace=False, p=weights))
    raise ValueError(challenger)


def evaluate_challenger(state: dict[str, Any], granularity: str, challenger: str, seed: int) -> dict[str, Any]:
    module = state["module"]
    targets = select_targets(state, granularity, challenger, seed)
    base_found = set(state["base"].loc[state["base"]["new_item"], "discovered_item_id"].dropna()) & state["oracle_ids"]
    new_items: set[str] = set()
    cost = 0
    for target in targets:
        candidates, target_cost = candidate_items_for_stratum(module, target, granularity)
        cost += target_cost
        new_items |= (candidates & state["oracle_ids"]) - base_found
        base_found |= candidates & state["oracle_ids"]
    new_true = len(new_items)
    cumulative_true = state["base_true_items"] + new_true
    cumulative_recall = cumulative_true / state["oracle_total"]
    return {
        "task": state["task_name"],
        "task_id": module.TASK_ID,
        "granularity": granularity,
        "challenger": challenger,
        "seed": seed,
        "targets": ";".join(targets),
        "base_true_items": state["base_true_items"],
        "base_recall": state["base_recall"],
        "oracle_total": state["oracle_total"],
        "new_true_items": new_true,
        "cost": cost,
        "novelty_per_cost": new_true / cost if cost else 0.0,
        "cumulative_true_items": cumulative_true,
        "cumulative_recall": cumulative_recall,
        "false_stop_before": state["base_recall"] < 0.90,
        "false_stop_after": cumulative_recall < 0.90,
        "false_stop_reduction": int((state["base_recall"] < 0.90) and (cumulative_recall >= 0.90)),
        "new_true_item_ids": ";".join(sorted(new_items)),
    }


def bootstrap_ci(values: np.ndarray, seed: int = 0) -> tuple[float, float]:
    if values.size == 0:
        return math.nan, math.nan
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(BOOTSTRAP_SEEDS):
        sample = rng.choice(values, size=values.size, replace=True)
        means.append(float(np.mean(sample)))
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, sub in results.groupby(["task", "task_id", "granularity", "challenger"]):
        values = sub["new_true_items"].to_numpy(dtype=float)
        npc = sub["novelty_per_cost"].to_numpy(dtype=float)
        recall = sub["cumulative_recall"].to_numpy(dtype=float)
        false_reduction = sub["false_stop_reduction"].to_numpy(dtype=float)
        ci_low, ci_high = bootstrap_ci(values)
        npc_low, npc_high = bootstrap_ci(npc)
        rec_low, rec_high = bootstrap_ci(recall)
        rows.append(
            {
                "task": keys[0],
                "task_id": keys[1],
                "granularity": keys[2],
                "challenger": keys[3],
                "runs": len(sub),
                "mean_new_true_items": float(values.mean()),
                "std_new_true_items": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
                "new_true_ci95_low": ci_low,
                "new_true_ci95_high": ci_high,
                "mean_novelty_per_cost": float(npc.mean()),
                "std_novelty_per_cost": float(npc.std(ddof=1)) if len(npc) > 1 else 0.0,
                "novelty_per_cost_ci95_low": npc_low,
                "novelty_per_cost_ci95_high": npc_high,
                "mean_cumulative_recall": float(recall.mean()),
                "std_cumulative_recall": float(recall.std(ddof=1)) if len(recall) > 1 else 0.0,
                "cumulative_recall_ci95_low": rec_low,
                "cumulative_recall_ci95_high": rec_high,
                "mean_false_stop_reduction": float(false_reduction.mean()),
            }
        )
    return pd.DataFrame(rows)


def add_random_percentiles(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (task, granularity), sub in summary.groupby(["task", "granularity"]):
        random_mean = sub.loc[sub["challenger"] == "random", "mean_new_true_items"]
        random_std = sub.loc[sub["challenger"] == "random", "std_new_true_items"]
        if random_mean.empty:
            continue
        mu = float(random_mean.iloc[0])
        sigma = float(random_std.iloc[0])
        for _, row in sub.iterrows():
            percentile = math.nan
            if sigma > 0:
                z = (row["mean_new_true_items"] - mu) / sigma
                percentile = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
            record = row.to_dict()
            record["percentile_vs_random_normal_approx"] = percentile
            record["delta_mean_new_true_vs_random"] = row["mean_new_true_items"] - mu
            rows.append(record)
    return pd.DataFrame(rows)


def write_report(summary: pd.DataFrame, detailed: pd.DataFrame) -> None:
    rp = summary[summary["challenger"] == "residual_potential"].copy()
    pivot = summary.pivot_table(
        index=["task", "granularity"],
        columns="challenger",
        values="mean_new_true_items",
        aggfunc="first",
    ).reset_index()
    for col in CHALLENGERS:
        if col not in pivot:
            pivot[col] = np.nan
    pivot["rp_minus_random"] = pivot["residual_potential"] - pivot["random"]
    pivot["rp_minus_low_exposure"] = pivot["residual_potential"] - pivot["low_exposure"]
    pivot["rp_minus_high_potential"] = pivot["residual_potential"] - pivot["high_potential"]
    pivot.to_csv(RESULTS / "ablation_summary.csv", index=False)

    robust = rp[[
        "task",
        "granularity",
        "mean_new_true_items",
        "std_new_true_items",
        "new_true_ci95_low",
        "new_true_ci95_high",
        "mean_novelty_per_cost",
        "mean_cumulative_recall",
        "mean_false_stop_reduction",
        "percentile_vs_random_normal_approx",
        "delta_mean_new_true_vs_random",
    ]]

    report = f"""# Method Validation v1

Frozen research angle:

> source-route exposure localization on the coverage simplex as a stopping-risk diagnostic

Frozen method candidate:

> residual-potential challenger = under-exposure × runtime-computable potential

## Leakage Control

Potential uses only runtime-visible source text and route match counts. It never uses oracle labels, oracle missing mass, undiscovered true item counts, post-hoc recall, or any oracle-derived missing distribution. Oracle labels are used only after challenger selection to score new true items.

## Challenger Summary

{summary.to_markdown(index=False)}

## Residual-Potential Focus

{robust.to_markdown(index=False)}

## Ablation

{pivot.to_markdown(index=False)}

## Decision Notes

- Stable support requires residual-potential to beat random, low-exposure, and high-potential across both tasks and strata granularities.
- If high-potential-only matches residual-potential, the intervention is mainly a potential heuristic rather than a geometry-derived under-exposure method.
- If residual-potential wins only at source-route but fails at source-only or source-route-action, report that the method depends on the chosen coverage geometry.
"""
    (REPORTS / "METHOD_VALIDATION_V1_REPORT.md").write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    policy = load_module("policy_task", SCRIPTS / "run_blind_policy_task.py")
    code = load_module("code_task", SCRIPTS / "run_blind_code_task.py")
    states = [
        build_task_state(policy, "policy_docset_v1"),
        build_task_state(code, "code_repo_v1"),
    ]

    rows = []
    for state in states:
        for granularity in GRANULARITIES:
            for challenger in CHALLENGERS:
                for seed in range(N_SEEDS):
                    rows.append(evaluate_challenger(state, granularity, challenger, seed))
    detailed = pd.DataFrame(rows)
    detailed.to_csv(RESULTS / "method_validation_v1_detailed.csv", index=False)

    summary = summarize(detailed)
    summary = add_random_percentiles(summary)
    summary.to_csv(RESULTS / "method_validation_v1_summary.csv", index=False)
    write_report(summary, detailed)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
