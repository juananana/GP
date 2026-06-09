#!/usr/bin/env python3
"""Build a compact dashboard for the current Line A state.

The generated dashboard intentionally uses ASCII-heavy English text so it is
robust to Windows console code-page quirks.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def method_row(case: dict[str, Any], method: str) -> dict[str, Any]:
    return next(row for row in case["rows"] if row["method"] == method)


def source_aware_section(base: Path) -> list[str]:
    data = load_json(base / "protocol_outputs" / "source_aware_audit_v2_results.json")
    if not data:
        return ["## Source-Aware Audit v2", "", "Not generated yet.", ""]

    lines = [
        "## Source-Aware Audit v2",
        "",
        "| case | seed | candidate recall | candidate precision | filter recall | filter precision | sweep recall | sweep precision |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for case in data["cases"]:
        if not case["reportable"]:
            continue
        candidate = method_row(case, "candidate_pool")
        filtered = method_row(case, "source_aware_candidate_filter_v2")
        sweep = method_row(case, "source_sweep_v2_upper_bound")
        lines.append(
            "| {case_id} | {seed} | {candidate_recall} | {candidate_precision} | {filter_recall} | {filter_precision} | {sweep_recall} | {sweep_precision} |".format(
                case_id=case["case_id"],
                seed=case["seed"],
                candidate_recall=fmt(candidate["recall"]),
                candidate_precision=fmt(candidate["precision"]),
                filter_recall=fmt(filtered["recall"]),
                filter_precision=fmt(filtered["precision"]),
                sweep_recall=fmt(sweep["recall"]),
                sweep_precision=fmt(sweep["precision"]),
            )
        )
    lines.extend([
        "",
        "Candidate filter audits only G3/holdout candidates. Source sweep is a bounded policy upper bound, not a blind LLM result.",
        "",
    ])
    return lines


def protocol_section(base: Path) -> list[str]:
    data = load_json(base / "protocol_outputs" / "evidence_preserving_protocol_results.json")
    if not data:
        return ["## Protocol Overview", "", "Not generated yet.", ""]

    lines = [
        "## Protocol Overview",
        "",
        "| case | mean conf | mean jaccard | singletons | consensus recall | standard recall | raw-union recall | certificate target |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for case in data["cases"]:
        consensus = method_row(case, "majority_consensus")
        standard = method_row(case, "standard_summarizer_blind")
        raw_union = method_row(case, "raw_union")
        lines.append(
            "| {case_id} | {conf} | {jac} | {singletons} | {consensus_recall} | {standard_recall} | {union_recall} | {target} |".format(
                case_id=case["case_id"],
                conf=fmt(case["mean_confidence"]),
                jac=fmt(case["mean_pairwise_jaccard"]),
                singletons=case["singleton_count"],
                consensus_recall=fmt(consensus["recall"]),
                standard_recall=fmt(standard["recall"]),
                union_recall=fmt(raw_union["recall"]),
                target="stop-risk" if consensus["recall"] < 0.95 else "precision-risk",
            )
        )
    lines.append("")
    return lines


def certificate_section(base: Path) -> list[str]:
    data = load_json(base / "protocol_outputs" / "completion_certificate_v0_results.json")
    if not data:
        return ["## Completion Certificate v0", "", "Not generated yet.", ""]

    lines = [
        "## Completion Certificate v0",
        "",
        "| case | seed | reportable | consensus recall | union recall | union precision | label | flags |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in data["seed_results"]:
        if not row["reportable"]:
            continue
        cert = row["certificate"]
        lines.append(
            "| {case_id} | {seed} | {reportable} | {consensus_recall} | {union_recall} | {union_precision} | {label} | {flags} |".format(
                case_id=row["case_id"],
                seed=row["seed"],
                reportable=fmt(row["reportable"]),
                consensus_recall=fmt(row["consensus"]["recall"]),
                union_recall=fmt(row["union"]["recall"]),
                union_precision=fmt(row["union"]["precision"]),
                label=cert["label"],
                flags=", ".join(cert["risk_flags"]) or "none",
            )
        )
    lines.append("")
    return lines


def write_dashboard(base: Path, out_path: Path) -> None:
    lines = [
        "# Line A Experiment Dashboard",
        "",
        "Date: 2026-06-08",
        "",
        "## Current Takeaway",
        "",
        "T4 establishes stable real-repository aggregation-stage false stop: standard summarization self-reports completion in 3/3 seeds while omitting many oracle items. T5 adds a second real-repository family where search coverage is harder: consensus and raw union both remain incomplete across 3 seeds, and the certificate consistently refuses to stop.",
        "",
    ]
    lines.extend(protocol_section(base))
    lines.extend(certificate_section(base))
    lines.extend(source_aware_section(base))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path("experiments/false_convergence_pilot"))
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("experiments/false_convergence_pilot/reports/overview/EXPERIMENT_DASHBOARD_CN.md"),
    )
    args = parser.parse_args()
    write_dashboard(args.base, args.out_md)


if __name__ == "__main__":
    main()
