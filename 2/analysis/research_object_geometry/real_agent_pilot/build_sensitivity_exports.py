from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"
SUPP = PILOT / "credibility_supplement" / "results"
OUT = PILOT / "unified_pipeline" / "results"


def build_sensitivity_exports() -> dict[str, pd.DataFrame]:
    threshold = pd.read_csv(SUPP / "threshold_sensitivity.csv")
    budget = pd.read_csv(SUPP / "budget_sensitivity.csv")
    budget_detail = pd.read_csv(SUPP / "budget_sensitivity_detail.csv")
    frontier = (
        budget.groupby(["task", "challenger"], as_index=False)
        .agg(
            min_fcr=("false_certification_rate", "min"),
            max_continue_rate=("continue_rate", "max"),
            max_abstain_rate=("abstain_rate", "max"),
            max_repair_gain=("mean_repair_gain", "max"),
            min_cost=("mean_cost", "min"),
            max_cost=("mean_cost", "max"),
        )
        .sort_values(["task", "challenger"])
    )
    OUT.mkdir(parents=True, exist_ok=True)
    threshold.to_csv(OUT / "threshold_sensitivity.csv", index=False)
    budget.to_csv(OUT / "budget_sensitivity.csv", index=False)
    budget_detail.to_csv(OUT / "budget_sensitivity_detail.csv", index=False)
    frontier.to_csv(OUT / "safety_cost_frontier_summary.csv", index=False)
    report = f"""# Threshold and Budget Sensitivity

These tables report the complete sweep, not a selected optimum.  The false
certification label is computed only after each runtime decision is fixed.

## Safety-cost frontier summary

{frontier.to_markdown(index=False)}
"""
    (OUT / "SENSITIVITY_SUMMARY.md").write_text(report, encoding="utf-8")
    return {
        "threshold": threshold,
        "budget": budget,
        "budget_detail": budget_detail,
        "frontier": frontier,
    }


def main() -> None:
    outputs = build_sensitivity_exports()
    print(outputs["frontier"].to_string(index=False))


if __name__ == "__main__":
    main()
