#!/usr/bin/env python3
"""Build an honest status report for the online audit-controller evidence loop."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "false_convergence_pilot"
OLD_ONLINE = BASE / "online_blind_validation" / "T5_requests_tls_seed04"
NEW_OUT = BASE / "online_audit_controller" / "T5_requests_tls"
REPORT = NEW_OUT / "ONLINE_AUDIT_CONTROLLER_GAP_REPORT.md"
SUMMARY_JSON = NEW_OUT / "ONLINE_AUDIT_CONTROLLER_GAP_REPORT.json"
DISCOVERY_GRID = NEW_OUT / "ONLINE_DISCOVERY_GRID_SUMMARY.csv"
POLICY_RESULTS = NEW_OUT / "audit_policy_eval" / "ONLINE_AUDIT_POLICY_RESULTS.csv"

REQUIRED_SEEDS = ["seed04", "seed05", "seed06", "seed07", "seed08"]
REQUIRED_DISCOVERY = [
    "homogeneous",
    "prompt_diverse",
    "source_partitioned",
    "independent_context",
]
REQUIRED_POLICIES = [
    "no_audit",
    "random_holdout",
    "singleton_audit",
    "boundary_focused_holdout",
    "source_partitioned_review",
    "always_holdout",
    "risk_triggered_audit",
]


def read_seed04_summary() -> list[dict[str, Any]]:
    path = OLD_ONLINE / "ONLINE_VALIDATION_SUMMARY.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def status_for_discovery(seed: str, condition: str) -> str:
    if seed == "seed04" and condition in {"homogeneous", "prompt_diverse", "source_partitioned"}:
        return "completed_minimal_seed04"
    candidate = NEW_OUT / seed / condition / "score_summary.json"
    if candidate.exists():
        return "completed"
    return "not_run"


def build_summary() -> dict[str, Any]:
    seed04 = read_seed04_summary()
    policies_completed = POLICY_RESULTS.exists()
    discovery = [
        {
            "seed": seed,
            "condition": condition,
            "status": status_for_discovery(seed, condition),
        }
        for seed in REQUIRED_SEEDS
        for condition in REQUIRED_DISCOVERY
    ]
    audit = [
        {
            "seed": seed,
            "policy": policy,
            "status": "completed" if policies_completed else "not_run_online",
            "reason": "online audit-policy results written" if policies_completed else "online verifier/holdout audit agents are not implemented or executed yet",
        }
        for seed in REQUIRED_SEEDS
        for policy in REQUIRED_POLICIES
    ]
    return {
        "claim_status": "requests_p0_method_effect_loop_completed_but_not_completion_certifying" if policies_completed else "diagnostic_loop_complete_method_effect_loop_incomplete",
        "requests_seed04_discovery_summary": seed04,
        "required_discovery_grid": discovery,
        "required_audit_policy_grid": audit,
        "paper_level_requirements_met": False,
        "policy_results": str(POLICY_RESULTS) if policies_completed else None,
        "discovery_grid": str(DISCOVERY_GRID) if DISCOVERY_GRID.exists() else None,
        "minimum_missing_items": [
            "Add independent oracle second-pass review before submission.",
            "Run at least one public benchmark subset or keep external benchmark claims out of the main paper.",
            "Add more real repositories before claiming repository-general audit-controller performance.",
            "Run second-model or cross-provider validation before claiming model-general behavior.",
        ],
    }


def fmt_float(value: str) -> str:
    try:
        return f"{float(value):.3f}"
    except Exception:
        return value


def write_markdown(summary: dict[str, Any]) -> None:
    lines = [
        "# Online Audit-Controller Status Report",
        "",
        "This report is intentionally conservative. It separates the completed",
        "Requests P0 online audit-controller loop from broader paper-level claims",
        "that still require more repositories, independent oracle review, and public",
        "benchmark validation.",
        "",
        "## Current Claim Status",
        "",
        f"- Claim status: `{summary['claim_status']}`.",
        "- Requests P0 method-effect loop: completed when policy results are present.",
        "- Completion certification: not achieved; all online policies remain below the 0.95 recall threshold.",
        "- Paper-level general online audit-controller claim: not yet supported.",
        "",
        "## Discovery Grid Status",
        "",
        "| seed | homogeneous | prompt-diverse | source-partitioned | independent-context |",
        "| --- | --- | --- | --- | --- |",
    ]
    by_seed_condition = {
        (row["seed"], row["condition"]): row["status"]
        for row in summary["required_discovery_grid"]
    }
    for seed in REQUIRED_SEEDS:
        lines.append(
            "| {seed} | {homogeneous} | {prompt_diverse} | {source_partitioned} | {independent_context} |".format(
                seed=seed,
                homogeneous=by_seed_condition[(seed, "homogeneous")],
                prompt_diverse=by_seed_condition[(seed, "prompt_diverse")],
                source_partitioned=by_seed_condition[(seed, "source_partitioned")],
                independent_context=by_seed_condition[(seed, "independent_context")],
            )
        )
    lines.extend(["", "## Online Audit Policy Status", ""])
    if POLICY_RESULTS.exists():
        lines.extend([
            f"Policy results: `{POLICY_RESULTS}`.",
            "",
            "| policy | n | pre R | post R | precision | recovered TP | introduced FP | audit tokens |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ])
        with POLICY_RESULTS.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for policy in REQUIRED_POLICIES:
            subset = [row for row in rows if row["policy"] == policy]
            if not subset:
                continue
            def avg(name: str) -> float:
                return sum(float(row[name]) for row in subset) / len(subset)
            lines.append(
                f"| {policy} | {len(subset)} | {avg('pre_recall'):.3f} | {avg('post_recall'):.3f} | "
                f"{avg('post_precision'):.3f} | {avg('recovered_tp'):.1f} | "
                f"{avg('introduced_fp'):.1f} | {avg('audit_tokens'):.0f} |"
            )
    else:
        lines.append("Online audit policies are not run yet.")
    lines.extend(["", "## Remaining Work Before Broader Paper-Level Claim", ""])
    for item in summary["minimum_missing_items"]:
        lines.append(f"- {item}")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    summary = build_summary()
    NEW_OUT.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(summary)
    print(REPORT)


if __name__ == "__main__":
    main()
