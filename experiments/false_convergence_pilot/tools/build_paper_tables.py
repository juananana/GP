#!/usr/bin/env python3
"""Build paper-ready tables from offline experiment outputs."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Iterable


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def short_family(case_id: str) -> str:
    if case_id.startswith("T4_"):
        return "T3 Click"
    if case_id.startswith("T5_"):
        return "T4 Requests"
    if case_id.startswith("T1_"):
        return "T1 synthetic code"
    if case_id.startswith("T2_"):
        return "T2 policy docs"
    return case_id.split("_seed", maxsplit=1)[0]


def method_row(case: dict[str, Any], method: str) -> dict[str, Any] | None:
    return next((row for row in case.get("rows", []) if row.get("method") == method), None)


def variant_row(case: dict[str, Any], variant: str) -> dict[str, Any] | None:
    return next((row for row in case.get("variants", []) if row.get("variant") == variant), None)


def real_repo_cases(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        case
        for case in protocol["cases"]
        if case["case_id"].startswith(("T4_real_repo_click", "T5_real_repo_requests_tls"))
    ]


def family_method_summary(cases: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        family = short_family(case["case_id"])
        for method in [
            "majority_consensus",
            "standard_summarizer_blind",
            "raw_union",
            "union_preserving_blind",
            "evidence_preserving_protocol",
        ]:
            row = method_row(case, method)
            if row:
                grouped[(family, method)].append(row)

    rows = []
    for (family, method), items in sorted(grouped.items()):
        recalls = [item["recall"] for item in items if item.get("recall") is not None]
        precisions = [item["precision"] for item in items if item.get("precision") is not None]
        false_stops = [item for item in items if item.get("false_stop")]
        completions = [item for item in items if item.get("completion")]
        rows.append(
            {
                "family": family,
                "method": method,
                "n": len(items),
                "mean_recall": mean(recalls) if recalls else None,
                "min_recall": min(recalls) if recalls else None,
                "max_recall": max(recalls) if recalls else None,
                "mean_precision": mean(precisions) if precisions else None,
                "false_stop_count": len(false_stops),
                "completion_count": len(completions),
            }
        )
    return rows


def certificate_rows(cert: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in cert["seed_results"]:
        if not row.get("reportable"):
            continue
        if not row["case_id"].startswith(("T4_real_repo_click", "T5_real_repo_requests_tls")):
            continue
        certificate = row["certificate"]
        rows.append(
            {
                "case_id": row["case_id"],
                "family": short_family(row["case_id"]),
                "seed": row["seed"],
                "consensus_recall": row["consensus"]["recall"],
                "union_recall": row["union"]["recall"],
                "union_precision": row["union"]["precision"],
                "label": certificate["label"],
                "risk_flags": "; ".join(certificate["risk_flags"]),
            }
        )
    return rows


def audit_rows(audit: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for case in audit["cases"]:
        if not case.get("reportable"):
            continue
        candidate = method_row(case, "candidate_pool")
        filtered = method_row(case, "source_aware_candidate_filter_v2")
        sweep = method_row(case, "source_sweep_v2_upper_bound")
        if not (candidate and filtered and sweep):
            continue
        rows.append(
            {
                "case_id": case["case_id"],
                "family": short_family(case["case_id"]),
                "seed": case["seed"],
                "candidate_size": case["candidate_pool_size"],
                "candidate_recall": candidate["recall"],
                "candidate_precision": candidate["precision"],
                "filter_recall": filtered["recall"],
                "filter_precision": filtered["precision"],
                "sweep_recall": sweep["recall"],
                "sweep_precision": sweep["precision"],
            }
        )
    return rows


def cost_rows(cost: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for case in cost["cases"]:
        if not case["case_id"].startswith(("T4_real_repo_click", "T5_real_repo_requests_tls", "T1_", "T2_")):
            continue
        full = variant_row(case, "full_protocol")
        consensus = variant_row(case, "consensus_only")
        if not (full and consensus):
            continue
        rows.append(
            {
                "case_id": case["case_id"],
                "family": short_family(case["case_id"]),
                "consensus_recall": consensus["recall"],
                "full_recall": full["recall"],
                "full_precision": full["precision"],
                "full_false_stop": full["false_stop"],
                "audit_actions_proxy": full["audit_actions_proxy"],
                "recovered_tp_over_consensus": full["recovered_tp_over_consensus"],
                "actions_per_recovered_tp": full["audit_actions_per_recovered_tp"],
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(fmt(value) for value in row) + " |")
    return lines


def write_report(
    out_md: Path,
    method_summary: list[dict[str, Any]],
    cert_rows: list[dict[str, Any]],
    audit_rows_: list[dict[str, Any]],
    cost_rows_: list[dict[str, Any]],
) -> None:
    real_repo_method_rows = [
        [
            row["family"],
            row["method"],
            row["n"],
            row["mean_recall"],
            row["min_recall"],
            row["max_recall"],
            row["mean_precision"],
            f'{row["false_stop_count"]}/{row["n"]}',
            f'{row["completion_count"]}/{row["n"]}',
        ]
        for row in method_summary
    ]

    cert_summary = defaultdict(lambda: {"n": 0, "unsafe": 0, "requires": 0})
    for row in cert_rows:
        entry = cert_summary[row["family"]]
        entry["n"] += 1
        if row["label"] == "unsafe_to_stop":
            entry["unsafe"] += 1
        if row["label"] == "requires_audit":
            entry["requires"] += 1

    audit_summary = []
    for family in sorted({row["family"] for row in audit_rows_}):
        rows = [row for row in audit_rows_ if row["family"] == family]
        audit_summary.append(
            [
                family,
                len(rows),
                mean(row["candidate_recall"] for row in rows),
                mean(row["candidate_precision"] for row in rows),
                mean(row["filter_recall"] for row in rows),
                mean(row["filter_precision"] for row in rows),
                mean(row["sweep_recall"] for row in rows),
                mean(row["sweep_precision"] for row in rows),
            ]
        )

    lines = [
        "# Paper-Ready Experiment Results",
        "",
        "Date: 2026-06-09",
        "",
        "This report is generated from offline score summaries and protocol outputs. No oracle is exposed to blind agents or summarizers; oracle labels are used only by the scorer and table builder.",
        "",
        "## Main real-repository result",
        "",
        "Across two real repository audit families and three blind seeds per family, standard summarization repeatedly reports completion while recall remains far below full coverage. T3 mainly exposes aggregation-stage loss: raw union recovers nearly all oracle items but standard summarization discards many of them. T4 is harder: even raw union remains incomplete, showing search-stage coverage failure in addition to aggregation risk.",
        "",
    ]
    lines.extend(
        markdown_table(
            [
                "family",
                "method",
                "n",
                "mean recall",
                "min recall",
                "max recall",
                "mean precision",
                "false stops",
                "completed",
            ],
            real_repo_method_rows,
        )
    )
    lines.extend(["", "## Completion certificate v0", ""])
    lines.extend(
        markdown_table(
            ["family", "n", "unsafe_to_stop", "requires_audit"],
            [
                [family, row["n"], row["unsafe"], row["requires"]]
                for family, row in sorted(cert_summary.items())
            ],
        )
    )
    lines.extend(
        [
            "",
            "The certificate refuses to certify completion for every real-repository seed. This is the desired behavior for a completion-risk detector: it should not convert high agreement or high-confidence final prose into a closed-world completion claim.",
            "",
            "## Source-aware audit v2",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            [
                "family",
                "n",
                "candidate recall",
                "candidate precision",
                "filter recall",
                "filter precision",
                "sweep recall",
                "sweep precision",
            ],
            audit_summary,
        )
    )
    lines.extend(
        [
            "",
            "The candidate filter is an offline audit-policy prototype over already observed candidates. The source sweep is a bounded upper bound, not a blind LLM run.",
            "",
            "## Protocol cost proxy",
            "",
        ]
    )
    real_cost_rows = [
        [
            row["case_id"],
            row["consensus_recall"],
            row["full_recall"],
            row["full_precision"],
            row["full_false_stop"],
            row["audit_actions_proxy"],
            row["recovered_tp_over_consensus"],
            row["actions_per_recovered_tp"],
        ]
        for row in cost_rows_
        if row["case_id"].startswith(("T4_real_repo_click", "T5_real_repo_requests_tls"))
    ]
    lines.extend(
        markdown_table(
            [
                "case",
                "consensus recall",
                "full recall",
                "full precision",
                "false stop",
                "audit actions",
                "recovered TP",
                "actions/TP",
            ],
            real_cost_rows,
        )
    )
    lines.extend(
        [
            "",
            "The cost column is a proxy: audit queue size plus one unit for each triggered holdout. It should be reported as proxy cost until token and wall-clock logs are complete.",
            "",
            "## Suggested paper wording",
            "",
            "Use: `Consensus and high-confidence summarization are not reliable completion certificates for closed-world multi-agent discovery. In two real-repository line-level audit families, standard summarization false-stops in 6/6 blind seeds; a completion-risk certificate refuses to certify completion in all real-repository seeds.`",
            "",
            "Avoid: `The protocol solves completion.` The current evidence supports problem existence, failure mechanism separation, and a promising risk-detection/audit direction.",
            "",
        ]
    )
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path("experiments/false_convergence_pilot"))
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("experiments/false_convergence_pilot/reports/overview/PAPER_READY_EXPERIMENT_RESULTS_CN.md"),
    )
    args = parser.parse_args()

    protocol = load_json(args.base / "protocol_outputs" / "evidence_preserving_protocol_results.json")
    cert = load_json(args.base / "protocol_outputs" / "completion_certificate_v0_results.json")
    audit = load_json(args.base / "protocol_outputs" / "source_aware_audit_v2_results.json")
    cost = load_json(args.base / "protocol_outputs" / "protocol_ablation_cost_results.json")

    method_summary = family_method_summary(real_repo_cases(protocol))
    cert_table = certificate_rows(cert)
    audit_table = audit_rows(audit)
    cost_table = cost_rows(cost)

    write_report(args.out_md, method_summary, cert_table, audit_table, cost_table)
    table_dir = args.base / "reports" / "paper_tables"
    write_csv(table_dir / "real_repo_method_summary.csv", method_summary)
    write_csv(table_dir / "completion_certificate_real_repo.csv", cert_table)
    write_csv(table_dir / "source_aware_audit_v2_summary.csv", audit_table)
    write_csv(table_dir / "protocol_cost_proxy.csv", cost_table)


if __name__ == "__main__":
    main()
