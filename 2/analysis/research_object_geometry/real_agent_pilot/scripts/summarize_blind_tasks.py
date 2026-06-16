from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[4]
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"
BLIND = PILOT / "blind_tasks"
OUT = PILOT / "results"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    condition_frames = []
    challenger_frames = []
    for task_dir in sorted(BLIND.iterdir()):
        condition_path = task_dir / "results" / "condition_metrics.csv"
        challenger_path = task_dir / "results" / "challenger_summary.csv"
        if condition_path.exists():
            frame = pd.read_csv(condition_path)
            frame.insert(0, "task_dir", task_dir.name)
            condition_frames.append(frame)
        if challenger_path.exists():
            frame = pd.read_csv(challenger_path)
            frame.insert(0, "task_dir", task_dir.name)
            challenger_frames.append(frame)

    conditions = pd.concat(condition_frames, ignore_index=True)
    challengers = pd.concat(challenger_frames, ignore_index=True)
    conditions.to_csv(OUT / "blind_tasks_condition_summary.csv", index=False)
    challengers.to_csv(OUT / "blind_tasks_challenger_summary.csv", index=False)

    comparable = conditions[conditions["condition"].isin(["homogeneous", "route_partitioned"])]
    pivot = comparable.pivot(index=["task_dir", "task_id"], columns="condition", values=["exposure_gini", "recall", "source_route_coverage_ratio"])
    pivot.columns = [f"{metric}_{condition}" for metric, condition in pivot.columns]
    pivot = pivot.reset_index()
    pivot["delta_exposure_gini_homogeneous_minus_partitioned"] = pivot["exposure_gini_homogeneous"] - pivot["exposure_gini_route_partitioned"]
    pivot["delta_recall_partitioned_minus_homogeneous"] = pivot["recall_route_partitioned"] - pivot["recall_homogeneous"]
    pivot["pattern_replicated"] = (
        (pivot["delta_exposure_gini_homogeneous_minus_partitioned"] > 0)
        & (pivot["delta_recall_partitioned_minus_homogeneous"] > 0)
    )
    pivot.to_csv(OUT / "blind_tasks_cross_task_go_nogo.csv", index=False)

    report = PILOT / "docs" / "BLIND_TASKS_CROSS_TASK_REPORT.md"
    report.write_text(
        f"""# Blind Tasks Cross-Task Report

## Cross-Task Diagnostic Pattern

{pivot.to_markdown(index=False)}

## Condition Summary

{conditions.to_markdown(index=False)}

## Challenger Summary

{challengers.to_markdown(index=False)}

## Decision

The diagnostic pattern is replicated when homogeneous route reuse has higher exposure localization and lower recall than route-partitioned search. Challenger results remain secondary: they can confirm residual missing mass, but the method should not be finalized until challenger selection beats random across more tasks and seeds.
""",
        encoding="utf-8",
    )
    print(pivot.to_string(index=False))


if __name__ == "__main__":
    main()
