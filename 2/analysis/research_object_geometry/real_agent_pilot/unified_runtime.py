from __future__ import annotations

import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from runtime_contracts import assert_runtime_record, require_runtime_residual, runtime_decision_view
from task_inventory import route_patterns, source_family_map, source_files


def gini(values: list[float] | np.ndarray) -> float:
    x = np.array(values, dtype=float)
    if x.size == 0 or x.sum() == 0:
        return math.nan
    x = np.sort(x)
    n = x.size
    return float((2 * np.sum(np.arange(1, n + 1) * x) / (n * x.sum())) - (n + 1) / n)


def source_route_universe(inventory: dict[str, Any]) -> list[str]:
    files = source_files(inventory)
    families = source_family_map(inventory)
    routes = route_patterns(inventory)
    return [f"{families[path]}::{route}" for path in files for route in routes]


def file_lines(snapshot: Path, rel: str) -> tuple[str, ...]:
    return tuple((snapshot / rel).read_text(encoding="utf-8", errors="ignore").splitlines())


def route_matches(snapshot: Path, rel: str, route: str, routes: dict[str, Any]) -> list[tuple[int, str]]:
    pattern = routes[route]
    return [(i, line.strip()) for i, line in enumerate(file_lines(snapshot, rel), start=1) if pattern.search(line)]


def runtime_potential(snapshot: Path, inventory: dict[str, Any], *, include_line_prior: bool) -> dict[str, float]:
    files = source_files(inventory)
    families = source_family_map(inventory)
    routes = route_patterns(inventory)
    out: dict[str, float] = {}
    for rel in files:
        prior = math.log1p(max(len(file_lines(snapshot, rel)), 1)) if include_line_prior else 0.0
        for route in routes:
            out[f"{families[rel]}::{route}"] = len(route_matches(snapshot, rel, route, routes)) + prior
    return out


def build_runtime_states(
    *,
    task: str,
    events: list[dict[str, Any]],
    inventory: dict[str, Any],
    potential: dict[str, float],
) -> list[dict[str, Any]]:
    universe = source_route_universe(inventory)
    df = pd.DataFrame(events)
    rows: list[dict[str, Any]] = []
    for condition, sub in df.groupby("condition", sort=True):
        visible = sub[sub["source_family"] != "controller"].copy()
        exposure = Counter(visible["source_route_stratum"])
        values = [float(exposure.get(stratum, 0)) for stratum in universe]
        occupied = {stratum for stratum in universe if exposure.get(stratum, 0) > 0}
        weak = {stratum for stratum in universe if exposure.get(stratum, 0) == 0 and potential.get(stratum, 0.0) > 0}
        discovered = set(visible.loc[visible["new_item"], "discovered_item_id"].dropna())
        row = {
            "task": task,
            "task_id": str(sub["task_id"].iloc[0]),
            "trajectory_id": str(sub["run_id"].iloc[0]),
            "stop_state_id": f"{task}:{condition}:fixed_stop",
            "inventory_id": str(inventory["inventory_id"]),
            "condition": str(condition),
            "state_type": "fixed_stop_state",
            "n_events": int(len(sub)),
            "n_agents": int(sub["agent_id"].nunique()),
            "support_size": int(len(occupied)),
            "support": float(len(occupied) / len(universe)),
            "gini": gini(values),
            "weak_plausible_gap": int(len(weak)),
            "runtime_residual_items": 0,
            "residual_warning": False,
            "unresolved_warning": bool(weak),
            "runtime_discovered_items": int(len(discovered)),
        }
        assert_runtime_record(row, context=f"{task}:{condition} runtime state")
        rows.append(row)
    return rows


def decide_runtime_states(
    states: list[dict[str, Any]],
    *,
    support_threshold: float,
    gini_threshold: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for state in states:
        runtime = runtime_decision_view(state, context=f"{state['stop_state_id']} controller")
        residual = require_runtime_residual(runtime, context=f"{state['stop_state_id']} controller")
        geometry_ok = float(runtime["support"]) >= support_threshold and float(runtime["gini"]) <= gini_threshold
        weak_gap = float(runtime.get("weak_plausible_gap", 0))
        if residual > 0 or weak_gap > 0:
            decision = "CONTINUE"
            diagnosis = "runtime residual or unvisited plausible source-route strata"
        elif geometry_ok:
            decision = "SAFE"
            diagnosis = "source-route geometry eligible with no runtime residual warning"
        else:
            decision = "ABSTAIN"
            diagnosis = "insufficient source-route geometry"
        rows.append(
            {
                "task": state["task"],
                "task_id": state["task_id"],
                "runtime_state_id": state["stop_state_id"],
                "controller_version": "evidence_condition_unified_v1",
                "policy": "Full controller",
                "decision": decision,
                "diagnosis": diagnosis,
            }
        )
    return rows
