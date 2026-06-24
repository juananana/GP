from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"
SUPP = PILOT / "credibility_supplement" / "results"
METHOD = PILOT / "method_validation_v1" / "results"
OUT = PILOT / "unified_pipeline" / "results"


def build_source_route_ablation() -> dict[str, pd.DataFrame]:
    diagnostic = pd.read_csv(SUPP / "source_only_vs_source_route.csv")
    repair = pd.read_csv(METHOD / "ablation_summary.csv")
    repair_long = repair.melt(
        id_vars=["task", "granularity"],
        value_vars=["random", "high_potential", "residual_potential"],
        var_name="repair_policy",
        value_name="mean_new_true_items",
    )
    OUT.mkdir(parents=True, exist_ok=True)
    diagnostic.to_csv(OUT / "source_route_diagnostic_ablation.csv", index=False)
    repair_long.to_csv(OUT / "source_route_repair_ablation.csv", index=False)
    report = f"""# Source-only vs Source-route Ablation

This export is diagnostic rather than a new oracle rule.  The source-only
column asks whether all source families were touched; source-route additionally
asks whether evidence was produced under the declared route lenses.  Oracle
recall is used only after the stop state is fixed.

## Stop-state diagnostic

{diagnostic.to_markdown(index=False)}

## Repair-policy granularity summary

{repair_long.to_markdown(index=False)}
"""
    (OUT / "SOURCE_ROUTE_ABLATION.md").write_text(report, encoding="utf-8")
    return {"diagnostic": diagnostic, "repair": repair_long}


def main() -> None:
    outputs = build_source_route_ablation()
    print(outputs["diagnostic"].to_string(index=False))
    print(outputs["repair"].to_string(index=False))


if __name__ == "__main__":
    main()
