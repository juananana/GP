from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RESULTS = ROOT / "results"


def fnum(value: object, default: float | None = None) -> float | None:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def method_row(task: str, challenger: str) -> pd.Series | None:
    path = ROOT / "method_validation_v1" / "results" / "method_validation_v1_summary.csv"
    df = read_csv(path)
    sub = df[(df["task"] == task) & (df["granularity"] == "source_route") & (df["challenger"] == challenger)]
    return sub.iloc[0] if not sub.empty else None


def requests_row(challenger: str) -> pd.Series:
    path = ROOT / "external_validation_requests" / "results" / "external_requests_challenger_summary.csv"
    df = read_csv(path)
    return df[(df["granularity"] == "source_route") & (df["challenger"] == challenger)].iloc[0]


def urllib3_row(challenger: str) -> pd.Series:
    path = ROOT / "external_validation_v2" / "results" / "controller_summary.csv"
    df = read_csv(path)
    return df[df["challenger"] == challenger].iloc[0]


def condition_decision(support_ratio: float, gini: float, recall: float, weak_gap: float | None = None) -> str:
    if weak_gap is not None:
        if support_ratio >= 0.75 and gini <= 0.70 and weak_gap == 0:
            return "SAFE"
        return "CONTINUE"
    if support_ratio >= 0.75 and gini <= 0.70 and recall >= 0.90:
        return "SAFE"
    return "CONTINUE"


def add_generated_task(rows: list[dict], task_name: str, condition_path: Path, method_task: str) -> None:
    cond = read_csv(condition_path)
    base = cond[cond["condition"] == "homogeneous"].iloc[0]
    broad = cond[cond["condition"] == "route_partitioned"].iloc[0]
    residual = method_row(method_task, "residual_potential")
    high = method_row(method_task, "high_potential")
    random = method_row(method_task, "random")

    base_support = fnum(base["source_route_coverage_ratio"], 0.0)
    broad_support = fnum(broad["source_route_coverage_ratio"], 0.0)
    base_gini = fnum(base["exposure_gini"], 0.0)
    broad_gini = fnum(broad["exposure_gini"], 0.0)
    base_recall = fnum(base["recall"], 0.0)
    broad_recall = fnum(broad["recall"], 0.0)

    residual_gain = fnum(residual["mean_new_true_items"]) if residual is not None else None
    high_gain = fnum(high["mean_new_true_items"]) if high is not None else None
    random_gain = fnum(random["mean_new_true_items"]) if random is not None else None

    rows.append(
        {
            "task": task_name,
            "task_type": "bounded_generated_scored_subclass",
            "base_condition": "homogeneous",
            "base_support_ratio": base_support,
            "base_exposure_gini": base_gini,
            "base_recall": base_recall,
            "base_false_certification_if_stop": base_recall < 0.90,
            "base_controller_decision": condition_decision(base_support, base_gini, base_recall),
            "broad_condition": "route_partitioned",
            "broad_support_ratio": broad_support,
            "broad_exposure_gini": broad_gini,
            "broad_recall": broad_recall,
            "broad_false_certification_if_stop": broad_recall < 0.90,
            "broad_controller_decision": condition_decision(broad_support, broad_gini, broad_recall),
            "safe_or_near_complete_condition": "route_partitioned",
            "safe_or_near_complete_recall": broad_recall,
            "residual_repair_gain": residual_gain,
            "high_potential_repair_gain": high_gain,
            "random_repair_gain": random_gain,
            "residual_minus_high_gain": None if residual_gain is None or high_gain is None else residual_gain - high_gain,
            "residual_minus_random_gain": None if residual_gain is None or random_gain is None else residual_gain - random_gain,
            "residual_cost_normalized_evidence": fnum(residual["mean_novelty_per_cost"]) if residual is not None else None,
            "high_potential_cost_normalized_evidence": fnum(high["mean_novelty_per_cost"]) if high is not None else None,
            "residual_false_certification_rate_after_repair": None,
            "residual_high_overlap_jaccard": None,
            "residual_high_identical_rate": None,
            "boundary_note": "Generated scored subclass; useful for mechanism pattern, weaker for external validity.",
        }
    )


def build_summary() -> pd.DataFrame:
    rows: list[dict] = []
    add_generated_task(
        rows,
        "policy_docset_v1",
        ROOT / "blind_tasks" / "policy_docset_v1" / "results" / "condition_metrics.csv",
        "policy_docset_v1",
    )
    add_generated_task(
        rows,
        "code_repo_v1",
        ROOT / "blind_tasks" / "code_repo_v1" / "results" / "condition_metrics.csv",
        "code_repo_v1",
    )

    req_cond = read_csv(ROOT / "external_validation_requests" / "results" / "external_requests_condition_metrics.csv")
    req_base = req_cond[req_cond["condition"] == "homogeneous"].iloc[0]
    req_broad = req_cond[req_cond["condition"] == "route_partitioned"].iloc[0]
    req_resid = requests_row("residual_potential")
    req_high = requests_row("high_potential")
    req_rand = requests_row("random")
    rows.append(
        {
            "task": "requests",
            "task_type": "external_real_repo_pattern_oracle",
            "base_condition": "homogeneous",
            "base_support_ratio": fnum(req_base["source_route_coverage_ratio"]),
            "base_exposure_gini": fnum(req_base["exposure_gini"]),
            "base_recall": fnum(req_base["recall"]),
            "base_false_certification_if_stop": fnum(req_base["recall"]) < 0.90,
            "base_controller_decision": "CONTINUE",
            "broad_condition": "route_partitioned",
            "broad_support_ratio": fnum(req_broad["source_route_coverage_ratio"]),
            "broad_exposure_gini": fnum(req_broad["exposure_gini"]),
            "broad_recall": fnum(req_broad["recall"]),
            "broad_false_certification_if_stop": fnum(req_broad["recall"]) < 0.90,
            "broad_controller_decision": "SAFE",
            "safe_or_near_complete_condition": "route_partitioned",
            "safe_or_near_complete_recall": fnum(req_broad["recall"]),
            "residual_repair_gain": fnum(req_resid["mean_new_true_items"]),
            "high_potential_repair_gain": fnum(req_high["mean_new_true_items"]),
            "random_repair_gain": fnum(req_rand["mean_new_true_items"]),
            "residual_minus_high_gain": fnum(req_resid["mean_new_true_items"]) - fnum(req_high["mean_new_true_items"]),
            "residual_minus_random_gain": fnum(req_resid["mean_new_true_items"]) - fnum(req_rand["mean_new_true_items"]),
            "residual_cost_normalized_evidence": fnum(req_resid["mean_novelty_per_cost"]),
            "high_potential_cost_normalized_evidence": fnum(req_high["mean_novelty_per_cost"]),
            "residual_false_certification_rate_after_repair": 0.0,
            "residual_high_overlap_jaccard": 1.0,
            "residual_high_identical_rate": 1.0,
            "boundary_note": "Residual-potential and high-potential select identical strata; no independent under-exposure evidence.",
        }
    )

    u_cond = read_csv(ROOT / "external_validation_v2" / "results" / "condition_summary.csv")
    u_base = u_cond[u_cond["condition"] == "homogeneous"].iloc[0]
    u_broad = u_cond[u_cond["condition"] == "route_partitioned"].iloc[0]
    u_safe = u_cond[u_cond["condition"] == "extended_audit"].iloc[0]
    u_resid = urllib3_row("residual_potential")
    u_high = urllib3_row("high_potential")
    u_rand = urllib3_row("random")
    u_overlap = read_csv(ROOT / "external_validation_v2" / "results" / "challenger_overlap_analysis.csv")
    rows.append(
        {
            "task": "urllib3",
            "task_type": "external_real_repo_pattern_oracle",
            "base_condition": "homogeneous",
            "base_support_ratio": fnum(u_base["support_ratio"]),
            "base_exposure_gini": fnum(u_base["exposure_gini"]),
            "base_recall": fnum(u_base["recall"]),
            "base_false_certification_if_stop": str(u_base["naive_false_certification"]).lower() == "true",
            "base_controller_decision": u_base["controller_decision"],
            "broad_condition": "route_partitioned",
            "broad_support_ratio": fnum(u_broad["support_ratio"]),
            "broad_exposure_gini": fnum(u_broad["exposure_gini"]),
            "broad_recall": fnum(u_broad["recall"]),
            "broad_false_certification_if_stop": str(u_broad["naive_false_certification"]).lower() == "true",
            "broad_controller_decision": u_broad["controller_decision"],
            "safe_or_near_complete_condition": "extended_audit",
            "safe_or_near_complete_recall": fnum(u_safe["recall"]),
            "residual_repair_gain": fnum(u_resid["mean_new_true_items"]),
            "high_potential_repair_gain": fnum(u_high["mean_new_true_items"]),
            "random_repair_gain": fnum(u_rand["mean_new_true_items"]),
            "residual_minus_high_gain": fnum(u_resid["mean_new_true_items"]) - fnum(u_high["mean_new_true_items"]),
            "residual_minus_random_gain": fnum(u_resid["mean_new_true_items"]) - fnum(u_rand["mean_new_true_items"]),
            "residual_cost_normalized_evidence": fnum(u_resid["mean_new_evidence_per_cost"]),
            "high_potential_cost_normalized_evidence": fnum(u_high["mean_new_evidence_per_cost"]),
            "residual_false_certification_rate_after_repair": fnum(u_resid["false_certification_rate"]),
            "residual_high_overlap_jaccard": float(u_overlap["jaccard"].mean()),
            "residual_high_identical_rate": float(u_overlap["identical"].mean()),
            "boundary_note": "Residual-potential has larger total repair gain, but high-potential has similar cost-normalized evidence.",
        }
    )

    return pd.DataFrame(rows)


def write_docs(summary: pd.DataFrame) -> None:
    report_table = summary[
        [
            "task",
            "base_support_ratio",
            "base_exposure_gini",
            "base_recall",
            "base_false_certification_if_stop",
            "base_controller_decision",
            "broad_support_ratio",
            "broad_exposure_gini",
            "broad_recall",
            "broad_controller_decision",
            "residual_repair_gain",
            "high_potential_repair_gain",
            "residual_cost_normalized_evidence",
            "high_potential_cost_normalized_evidence",
            "residual_high_overlap_jaccard",
        ]
    ]

    (DOCS / "CROSS_TASK_SYNTHESIS_REPORT.md").write_text(
        f"""# Cross-Task Synthesis Report

## Scope

This synthesis freezes the current evidence without changing the paper mainline. It aggregates four task families: `policy_docset_v1`, `code_repo_v1`, `requests`, and `urllib3`.

## Unified Result Table

{report_table.to_markdown(index=False)}

## Evidence Chain

Across all four tasks, homogeneous route reuse produces localized evidence conditions and would be unsafe if accepted as a global completion certificate. Broader source-route evidence improves completion eligibility, but the `urllib3` route-partitioned case shows that broad exposure alone is not sufficient: it is geometry-eligible but still below the 0.90 oracle threshold, so the controller outputs `CONTINUE`.

The strongest supported contribution is therefore:

```text
evidence-condition diagnostic/controller prevents locally conditioned evidence from being accepted as global completion proof.
```

## Repair Evidence

Residual-potential is positive but bounded. It beats random and simple low-exposure in several source-route settings, ties high-potential exactly on `requests`, and improves total repair gain on `urllib3` while having similar or slightly worse cost efficiency than high-potential.

## Boundary

The current evidence does not prove residual-potential optimality. It supports residual-potential as a mechanism-aligned repair instance.
""",
        encoding="utf-8",
    )

    (DOCS / "METHOD_CLAIM_BOUNDARY.md").write_text(
        """# Method Claim Boundary

## What We Can Claim

The paper can claim an evidence-condition diagnostic and controller:

```text
no-new / agreement / self-completion should not be accepted as global completion evidence unless the source-route evidence condition is broad enough and repair/audit no longer reveals residual evidence.
```

Residual-potential can be presented as a mechanism-aligned repair candidate:

```text
priority(s) = under_exposure(s) x runtime_computable_potential(s)
```

## What We Cannot Claim

Do not claim residual-potential is optimal or universally better than high-potential.

Observed boundary:

- `requests`: residual-potential and high-potential select identical source-route strata.
- `urllib3`: residual-potential recovers more total scored evidence, but high-potential has similar cost-normalized evidence.

## Paper Stance

The main contribution is the evidence-condition diagnostic/controller. The repair rule is an instantiated intervention with positive evidence, not the final word on optimal challenger design.
""",
        encoding="utf-8",
    )

    (DOCS / "PAPER_SKELETON_V0.md").write_text(
        """# Paper Skeleton v0

## Problem Formulation

Study workload-unknown dynamic agent workflows that must decide whether a task is complete under partial, routed, and budgeted evidence. Item discovery is a scored subclass, not the full problem.

The failure mode is certificate mismatch: local progress evidence is used as a global completion certificate.

## Evidence-Condition Geometry

Define source-route strata `s` and runtime exposure distribution:

```text
p_exp(t, s) = v_t(s) / sum_s v_t(s)
```

This distribution describes the condition under which no-new, agreement, and self-completion evidence was produced.

## Controller Algorithm

1. Log source-route exposure during the workflow.
2. When a stop is proposed, compute support ratio and exposure localization.
3. If the evidence condition is too narrow, reject `SAFE`.
4. Run evidence-condition repair over weak but runtime-plausible strata.
5. Output `SAFE`, `CONTINUE`, or `ABSTAIN`.

`SAFE` requires broad evidence and no residual evidence from repair/audit.

## Experimental Protocol

Tasks:

- generated policy document set;
- generated code repo;
- external `requests` repo audit;
- external `urllib3` repo audit.

Controls:

- homogeneous route reuse;
- route-partitioned audit;
- extended or near-complete audit;
- random, low-exposure, high-potential, residual-potential, free-search continuation.

Leakage control: oracle labels are used only after trajectories and challenger choices are fixed.

## Result Table Skeleton

Columns:

- task;
- base support ratio;
- base exposure Gini;
- base recall;
- base false certification;
- controller decision;
- broad support ratio;
- broad recall;
- residual repair gain;
- high-potential repair gain;
- cost-normalized evidence;
- overlap between high-potential and residual-potential.

## Limitations

Current external oracles are pattern-defined, not human annotated. Residual-potential is not proven optimal. More non-item-discovery completion audits are needed.
""",
        encoding="utf-8",
    )

    (DOCS / "CLAIM_VERIFICATION_TASK_PLAN.md").write_text(
        """# Claim Verification Task Plan

## Purpose

Test whether the research object extends beyond item discovery by using a claim verification completion audit.

## Candidate Task

Given a repo-level claim such as:

```text
All network-facing calls either set a timeout or route through a retry/timeout policy.
```

The workflow must decide whether the audit is complete, not merely enumerate matching items.

## Source-Route Strata

Sources are repo files or modules. Routes are claim-specific audit lenses, such as timeout, retry, exception path, configuration default, and test coverage route.

## Oracle Construction

Build offline labels for:

- supporting evidence;
- contradicting evidence;
- unresolved evidence requiring further audit.

The oracle is hidden until trajectories and challenger choices are fixed.

## Limitation

This task needs more careful human or semi-manual oracle design than pattern-defined item discovery. If time is limited, keep it as a planned external validity extension rather than a required result.
""",
        encoding="utf-8",
    )


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    summary = build_summary()
    summary.to_csv(RESULTS / "cross_task_summary.csv", index=False)
    write_docs(summary)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
