from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[4]
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot" / "claim_verification_pilot"
RESULTS = PILOT / "results"
PAPER_GENERATED = ROOT / "paper" / "generated"

TAU_SUPPORT = 0.75
TAU_GINI = 0.70


def decide(policy: str, row: pd.Series) -> str:
    eligible = row["source_route_support"] >= TAU_SUPPORT and row["gini"] <= TAU_GINI
    if policy == "Naive stop":
        return "SAFE"
    if policy == "Source-only":
        return "SAFE" if row["source_support"] >= TAU_SUPPORT else "ABSTAIN"
    if policy == "Verifier-gate":
        return "ABSTAIN" if row["verifier_warning"] else "SAFE"
    if policy == "Eligibility-only":
        return "SAFE" if eligible else "ABSTAIN"
    if policy == "Full controller":
        if not eligible:
            return "CONTINUE" if row["residual_positive"] else "ABSTAIN"
        return "CONTINUE" if row["residual_positive"] else "SAFE"
    raise ValueError(policy)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    PAPER_GENERATED.mkdir(parents=True, exist_ok=True)
    states = pd.read_csv(PILOT / "claim_states.csv")
    states["oracle_safe"] = states["oracle_safe"].astype(bool)
    states["residual_positive"] = states["residual_positive"].astype(bool)
    states["verifier_warning"] = states["verifier_warning"].astype(bool)

    policies = ["Naive stop", "Source-only", "Verifier-gate", "Eligibility-only", "Full controller"]
    rows = []
    detail_rows = []
    for policy in policies:
        decisions = states.apply(lambda row: decide(policy, row), axis=1)
        unsafe = ~states["oracle_safe"]
        safe = states["oracle_safe"]
        unsafe_safe = int(((decisions == "SAFE") & unsafe).sum())
        unsafe_continue = int(((decisions == "CONTINUE") & unsafe).sum())
        unsafe_abstain = int(((decisions == "ABSTAIN") & unsafe).sum())
        safe_safe = int(((decisions == "SAFE") & safe).sum())
        safe_continue = int(((decisions == "CONTINUE") & safe).sum())
        safe_abstain = int(((decisions == "ABSTAIN") & safe).sum())
        cost = float(states.loc[decisions == "CONTINUE", "repair_cost"].mean()) if (decisions == "CONTINUE").any() else 0.0
        rows.append(
            {
                "policy": policy,
                "unsafe_n": int(unsafe.sum()),
                "safe_n": int(safe.sum()),
                "unsafe_sca": f"{unsafe_safe}/{unsafe_continue}/{unsafe_abstain}",
                "safe_sca": f"{safe_safe}/{safe_continue}/{safe_abstain}",
                "fcr": unsafe_safe / int(unsafe.sum()),
                "safe_coverage": safe_safe / int(safe.sum()),
                "mean_continue_cost": cost,
            }
        )
        for claim_id, decision in zip(states["claim_id"], decisions):
            detail_rows.append({"policy": policy, "claim_id": claim_id, "decision": decision})

    summary = pd.DataFrame(rows)
    summary.to_csv(RESULTS / "claim_verification_pilot_summary.csv", index=False)
    pd.DataFrame(detail_rows).to_csv(RESULTS / "claim_verification_pilot_decisions.csv", index=False)

    tex_rows = []
    for row in summary.itertuples(index=False):
        tex_rows.append(
            f"{row.policy} & {row.unsafe_n} & {row.safe_n} & {row.unsafe_sca} & "
            f"{row.safe_sca} & {row.fcr:.3f} & {row.safe_coverage:.3f} & {row.mean_continue_cost:.1f} \\\\"
        )
    table = r"""\begin{table}[t]
\centering
\small
\setlength{\tabcolsep}{2.5pt}
\caption{Small claim-verification pilot with human-style audit routes. Routes
are support, contradiction, exception-path, config-default, and scope-boundary.
This deterministic pilot is a scoped sanity check for completion control, not a
human-annotated benchmark. S/C/A reports SAFE/CONTINUE/ABSTAIN counts.}
\label{tab:claim_verification_pilot}
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lrrrrrrr}
\toprule
Policy & Unsafe & Safe & Unsafe S/C/A & Safe S/C/A & FCR & Safe cov. & Cost \\
\midrule
""" + "\n".join(tex_rows) + r"""
\bottomrule
\end{tabular}}
\end{table}
"""
    (PAPER_GENERATED / "table_claim_verification_pilot.tex").write_text(table, encoding="utf-8")


if __name__ == "__main__":
    main()
