from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

from experiment_config import load_experiment_config, thresholds


ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"
UNIFIED = PILOT / "unified_pipeline" / "results"
SUPP = PILOT / "credibility_supplement" / "results"
OUT = PILOT / "unified_pipeline" / "results"


def _row(frame: pd.DataFrame, *, task: str, condition: str, state_type: str, source: str, recall_threshold: float) -> dict:
    safe = frame["decision"] == "SAFE"
    cont = frame["decision"] == "CONTINUE"
    abstain = frame["decision"] == "ABSTAIN"
    oracle_safe = frame["recall"].astype(float) >= recall_threshold
    oracle_unsafe = ~oracle_safe
    return {
        "task": task,
        "condition": condition,
        "state_type": state_type,
        "source": source,
        "n": int(len(frame)),
        "oracle_safe_n": int(oracle_safe.sum()),
        "oracle_unsafe_n": int(oracle_unsafe.sum()),
        "safe": int(safe.sum()),
        "continue": int(cont.sum()),
        "abstain": int(abstain.sum()),
        "false_certification_rate": float(((safe) & oracle_unsafe).sum() / oracle_unsafe.sum()) if oracle_unsafe.sum() else math.nan,
        "safe_coverage": float(((safe) & oracle_safe).sum() / oracle_safe.sum()) if oracle_safe.sum() else math.nan,
        "continue_rate": float(cont.mean()) if len(frame) else math.nan,
        "abstention_rate": float(abstain.mean()) if len(frame) else math.nan,
        "mean_repair_gain": float(frame["repair_gain"].mean()) if "repair_gain" in frame else 0.0,
        "mean_cost": float(frame["cost"].mean()) if "cost" in frame else 0.0,
    }


def fixed_stop_rows(recall_threshold: float) -> list[dict]:
    scores = pd.read_csv(UNIFIED / "posthoc_scores.csv")
    scores = scores.rename(columns={"found_true_items": "repair_gain"})
    scores["repair_gain"] = 0.0
    scores["cost"] = 0.0
    rows = []
    for (task, condition), sub in scores.groupby(["task", "condition"], sort=True):
        rows.append(
            _row(
                sub,
                task=task,
                condition=condition,
                state_type="fixed_stop_state",
                source="unified_runtime_posthoc",
                recall_threshold=recall_threshold,
            )
        )
    rows.append(
        _row(
            scores,
            task="external_repos",
            condition="all_fixed_stop_states",
            state_type="fixed_stop_state",
            source="unified_runtime_posthoc",
            recall_threshold=recall_threshold,
        )
    )
    return rows


def seeded_repair_rows(recall_threshold: float) -> list[dict]:
    detail = pd.read_csv(SUPP / "controller_decision_detail.csv")
    detail = detail[detail["state_type"] == "seeded_unsafe_repair"].copy()
    rows = []
    for (task, condition), sub in detail.groupby(["task", "condition"], sort=True):
        rows.append(
            _row(
                sub,
                task=task,
                condition=condition,
                state_type="seeded_unsafe_repair",
                source="seeded_repair_validation",
                recall_threshold=recall_threshold,
            )
        )
    rows.append(
        _row(
            detail,
            task="external_repos",
            condition="all_seeded_unsafe_repairs",
            state_type="seeded_unsafe_repair",
            source="seeded_repair_validation",
            recall_threshold=recall_threshold,
        )
    )
    return rows


def seeded_safe_rows(recall_threshold: float) -> list[dict]:
    safe = pd.read_csv(SUPP / "seeded_safe_state_validation.csv")
    safe = safe.rename(columns={"cumulative_recall": "recall"})
    rows = []
    for (task, challenger), sub in safe.groupby(["task", "challenger"], sort=True):
        rows.append(
            _row(
                sub,
                task=task,
                condition=f"safe_state:{challenger}",
                state_type="seeded_safe_complete",
                source="seeded_safe_state_validation",
                recall_threshold=recall_threshold,
            )
        )
    rows.append(
        _row(
            safe,
            task="external_repos",
            condition="all_seeded_safe_complete",
            state_type="seeded_safe_complete",
            source="seeded_safe_state_validation",
            recall_threshold=recall_threshold,
        )
    )
    return rows


def build_table() -> pd.DataFrame:
    config = load_experiment_config()
    recall_threshold = thresholds(config)["eval_recall"]
    rows = fixed_stop_rows(recall_threshold)
    rows.extend(seeded_repair_rows(recall_threshold))
    rows.extend(seeded_safe_rows(recall_threshold))
    out = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT / "controller_decision_table.csv", index=False)
    return out


def main() -> None:
    table = build_table()
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
