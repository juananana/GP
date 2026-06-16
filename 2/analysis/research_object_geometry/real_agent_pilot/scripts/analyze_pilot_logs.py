from __future__ import annotations

import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(os.environ.get("PILOT_ROOT", Path(__file__).resolve().parents[4]))
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"
LOGS = PILOT / "logs"
RESULTS = PILOT / "results"


def ensure_dirs() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def gini(values: np.ndarray) -> float:
    x = np.array(values, dtype=float)
    if x.size == 0 or x.sum() == 0:
        return math.nan
    x = np.sort(x)
    n = x.size
    return float((2 * np.sum(np.arange(1, n + 1) * x) / (n * x.sum())) - (n + 1) / n)


def analyze():
    events = pd.DataFrame(load_jsonl(LOGS / "action_events.jsonl"))
    oracle = pd.DataFrame(load_jsonl(LOGS / "oracle_items.jsonl"))
    if events.empty:
        raise SystemExit("no action_events.jsonl found")

    events["stratum"] = events["source_route_stratum"].fillna("unknown")
    events["new_item"] = events["new_item"].fillna(False).astype(bool)

    rows = []
    for (task_id, run_id, condition, agent_id), sub in events.groupby(["task_id", "run_id", "condition", "agent_id"]):
        exposure = Counter(sub["stratum"])
        discovery = Counter(sub.loc[sub["new_item"], "stratum"])
        all_strata = sorted(set(exposure) | set(discovery))
        exp_vals = np.array([exposure[s] for s in all_strata], dtype=float)
        disc_vals = np.array([discovery[s] for s in all_strata], dtype=float)
        exp_total = exp_vals.sum()
        disc_total = disc_vals.sum()
        rows.append(
            {
                "task_id": task_id,
                "run_id": run_id,
                "condition": condition,
                "agent_id": agent_id,
                "n_events": len(sub),
                "n_exposure_strata": int((exp_vals > 0).sum()),
                "n_discovery_strata": int((disc_vals > 0).sum()),
                "exposure_gini": gini(exp_vals),
                "discovery_gini": gini(disc_vals),
                "exposure_entropy": float(-np.sum((exp_vals / exp_total) * np.log(exp_vals / exp_total + 1e-12))) if exp_total else math.nan,
                "discovery_entropy": float(-np.sum((disc_vals / disc_total) * np.log(disc_vals / disc_total + 1e-12))) if disc_total else math.nan,
                "exposure_ratio": float((exp_vals > 0).mean()) if exp_vals.size else math.nan,
                "discovery_ratio": float((disc_vals > 0).mean()) if disc_vals.size else math.nan,
                "discovery_per_exposure": float(disc_total / exp_total) if exp_total else math.nan,
            }
        )

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "pilot_agent_geometry_summary.csv", index=False)

    run_rows = []
    for (task_id, condition), sub in events.groupby(["task_id", "condition"]):
        exposure = Counter(sub["stratum"])
        discovery = Counter(sub.loc[sub["new_item"], "stratum"])
        all_strata = sorted(set(exposure) | set(discovery))
        exp_vals = np.array([exposure[s] for s in all_strata], dtype=float)
        disc_vals = np.array([discovery[s] for s in all_strata], dtype=float)
        exp_total = exp_vals.sum()
        disc_total = disc_vals.sum()
        run_rows.append(
            {
                "task_id": task_id,
                "condition": condition,
                "n_agents": int(sub["agent_id"].nunique()),
                "n_events": len(sub),
                "n_exposure_strata": int((exp_vals > 0).sum()),
                "n_discovery_strata": int((disc_vals > 0).sum()),
                "run_exposure_gini": gini(exp_vals),
                "run_discovery_gini": gini(disc_vals),
                "run_exposure_entropy": float(-np.sum((exp_vals / exp_total) * np.log(exp_vals / exp_total + 1e-12))) if exp_total else math.nan,
                "run_discovery_entropy": float(-np.sum((disc_vals / disc_total) * np.log(disc_vals / disc_total + 1e-12))) if disc_total else math.nan,
                "run_discovery_per_exposure": float(disc_total / exp_total) if exp_total else math.nan,
            }
        )

    run_out = pd.DataFrame(run_rows)
    run_out.to_csv(RESULTS / "pilot_run_geometry_summary.csv", index=False)

    if not oracle.empty:
        oracle.to_csv(RESULTS / "pilot_oracle_items.csv", index=False)

    print(f"wrote {len(out)} agent summaries to {RESULTS / 'pilot_agent_geometry_summary.csv'}")
    print(f"wrote {len(run_out)} run summaries to {RESULTS / 'pilot_run_geometry_summary.csv'}")


if __name__ == "__main__":
    ensure_dirs()
    analyze()
