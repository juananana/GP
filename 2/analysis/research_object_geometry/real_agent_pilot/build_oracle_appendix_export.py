from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"
SUPP = PILOT / "credibility_supplement" / "results"
OUT = PILOT / "unified_pipeline" / "results"


def build_oracle_appendix_export() -> dict[str, pd.DataFrame]:
    summary = pd.read_csv(SUPP / "oracle_appendix_summary.csv")
    patterns = pd.read_csv(SUPP / "oracle_route_pattern_examples.csv")
    sanity = pd.read_csv(SUPP / "oracle_sanity_check.csv")
    OUT.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT / "oracle_appendix_summary.csv", index=False)
    patterns.to_csv(OUT / "oracle_route_pattern_examples.csv", index=False)
    sanity.to_csv(OUT / "oracle_sanity_check.csv", index=False)
    report = f"""# Oracle Appendix Export

The external repository oracle is pattern-defined and line-level.  It is used
only after runtime states, controller decisions, and repair targets have been
fixed.  It should be described as a bounded completion-audit oracle, not as a
human-annotated universal truth set.

## Oracle construction summary

{summary.to_markdown(index=False)}

## Route patterns and examples

{patterns.to_markdown(index=False)}

## Positive-sample sanity check

{sanity.to_markdown(index=False)}
"""
    (OUT / "ORACLE_APPENDIX.md").write_text(report, encoding="utf-8")
    return {"summary": summary, "patterns": patterns, "sanity": sanity}


def main() -> None:
    outputs = build_oracle_appendix_export()
    print(outputs["summary"].to_string(index=False))
    print(outputs["sanity"].to_string(index=False))


if __name__ == "__main__":
    main()
