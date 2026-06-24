from __future__ import annotations

import math
from typing import Any

import pandas as pd


def score_states(
    *,
    task: str,
    states: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    events: list[dict[str, Any]],
    oracle_items: list[dict[str, Any]],
    recall_threshold: float,
) -> list[dict[str, Any]]:
    df = pd.DataFrame(events)
    oracle_ids = {str(row["item_id"]) for row in oracle_items if bool(row.get("oracle_label", True))}
    decision_by_state = {row["runtime_state_id"]: row for row in decisions}
    rows: list[dict[str, Any]] = []
    for state in states:
        sub = df[df["condition"] == state["condition"]]
        found = set(sub.loc[sub["new_item"], "discovered_item_id"].dropna()) & oracle_ids
        recall = len(found) / len(oracle_ids) if oracle_ids else math.nan
        decision = decision_by_state[state["stop_state_id"]]
        rows.append(
            {
                "task": task,
                "task_id": state["task_id"],
                "runtime_decision_id": state["stop_state_id"],
                "oracle_id": f"{task}:pattern_oracle",
                "condition": state["condition"],
                "state_type": state["state_type"],
                "decision": decision["decision"],
                "success": bool(recall >= recall_threshold),
                "oracle_total": int(len(oracle_ids)),
                "found_true_items": int(len(found)),
                "recall": float(recall),
                "false_certification": bool(decision["decision"] == "SAFE" and recall < recall_threshold),
                "safe_coverage_label": bool(decision["decision"] == "SAFE" and recall >= recall_threshold),
            }
        )
    return rows
