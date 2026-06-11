#!/usr/bin/env python3
"""Summarize completed Requests TLS online discovery runs across seeds."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "false_convergence_pilot"
OLD_ONLINE = BASE / "online_blind_validation" / "T5_requests_tls_seed04"
NEW_ONLINE = BASE / "online_audit_controller" / "T5_requests_tls"
OUT_CSV = NEW_ONLINE / "ONLINE_DISCOVERY_GRID_SUMMARY.csv"
OUT_MD = NEW_ONLINE / "ONLINE_DISCOVERY_GRID_SUMMARY.md"

CONDITION_LABELS = {
    "homogeneous": "homogeneous",
    "prompt_diverse": "prompt-diverse",
    "source_partitioned": "source-partitioned",
    "independent_context": "independent-context",
}


def load_old_seed04() -> list[dict[str, Any]]:
    path = OLD_ONLINE / "ONLINE_VALIDATION_SUMMARY.csv"
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append({
                "seed": row["seed"],
                "condition": row["condition"],
                "mean_confidence": float(row["mean_confidence"]),
                "mean_jaccard": float(row["mean_jaccard"]),
                "singleton_ratio": float(row["singleton_ratio"]),
                "consensus_recall": float(row["consensus_recall"]),
                "union_recall": float(row["union_recall"]),
                "union_precision": float(row["union_precision"]),
                "input_tokens": int(float(row["input_tokens"])),
                "output_tokens": int(float(row["output_tokens"])),
                "wall_clock_seconds": float(row["wall_clock_seconds"]),
                "tool_calls": int(float(row.get("tool_calls") or 0)),
                "source": "online_blind_validation_seed04",
            })
    return rows


def load_costs(condition_dir: Path) -> tuple[int, int, float, int]:
    input_tokens = 0
    output_tokens = 0
    wall_clock = 0.0
    tool_calls = 0
    for path in (condition_dir / "cost").glob("*_cost.json"):
        raw = json.loads(path.read_text(encoding="utf-8"))
        input_tokens += int(raw.get("input_tokens") or 0)
        output_tokens += int(raw.get("output_tokens") or 0)
        wall_clock += float(raw.get("wall_clock_seconds") or 0.0)
        tool_calls += int(raw.get("tool_calls") or 0)
    return input_tokens, output_tokens, wall_clock, tool_calls


def load_new_grid() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for score_path in NEW_ONLINE.glob("seed*/**/score_summary.json"):
        condition_dir = score_path.parent
        condition = condition_dir.name
        seed = condition_dir.parent.name
        if seed == "seed04" and condition in {"homogeneous", "prompt_diverse", "source_partitioned"}:
            continue
        raw = json.loads(score_path.read_text(encoding="utf-8"))
        if "aggregates" in raw:
            aggregate = raw["aggregates"][0]
            mean_jaccard = aggregate.get("mean_jaccard")
            consensus_recall = aggregate.get("consensus_recall")
            union_recall = aggregate.get("union_recall")
            union_precision = aggregate.get("union_precision")
        else:
            aggregate = raw["seed_summaries"][0]
            mean_jaccard = aggregate.get("mean_pairwise_jaccard")
            consensus_recall = aggregate["consensus"]["recall"]
            union_recall = aggregate["union"]["recall"]
            union_precision = aggregate["union"]["precision"]
        input_tokens, output_tokens, wall_clock, tool_calls = load_costs(condition_dir)
        rows.append({
            "seed": seed,
            "condition": condition,
            "mean_confidence": aggregate.get("mean_confidence"),
            "mean_jaccard": mean_jaccard,
            "singleton_ratio": aggregate.get("singleton_ratio"),
            "consensus_recall": consensus_recall,
            "union_recall": union_recall,
            "union_precision": union_precision,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "wall_clock_seconds": wall_clock,
            "tool_calls": tool_calls,
            "source": "online_audit_controller_discovery",
        })
    return rows


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for condition in CONDITION_LABELS:
        subset = [row for row in rows if row["condition"] == condition]
        if not subset:
            continue
        output.append({
            "condition": condition,
            "n": len(subset),
            "mean_union_recall": mean(row["union_recall"] for row in subset),
            "sd_union_recall": pstdev(row["union_recall"] for row in subset) if len(subset) > 1 else 0.0,
            "mean_consensus_recall": mean(row["consensus_recall"] for row in subset),
            "sd_consensus_recall": pstdev(row["consensus_recall"] for row in subset) if len(subset) > 1 else 0.0,
            "mean_precision": mean(row["union_precision"] for row in subset),
            "mean_tokens": mean(row["input_tokens"] + row["output_tokens"] for row in subset),
            "mean_wall_clock": mean(row["wall_clock_seconds"] for row in subset),
        })
    return output


def write_csv(rows: list[dict[str, Any]]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "seed",
        "condition",
        "mean_confidence",
        "mean_jaccard",
        "singleton_ratio",
        "consensus_recall",
        "union_recall",
        "union_precision",
        "input_tokens",
        "output_tokens",
        "wall_clock_seconds",
        "tool_calls",
        "source",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_md(rows: list[dict[str, Any]], grouped: list[dict[str, Any]]) -> None:
    lines = [
        "# Online Discovery Grid Summary",
        "",
        "This file summarizes completed online discovery runs only. It is not a",
        "post-audit controller result: online verifier/holdout audit policies remain",
        "unrun.",
        "",
        "## Per-Condition Means",
        "",
        "| condition | n | union R | union R sd | consensus R | consensus R sd | precision | tokens | wall-clock s |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in grouped:
        lines.append(
            "| {condition} | {n} | {ur} | {ursd} | {cr} | {crsd} | {prec} | {tok} | {wall} |".format(
                condition=CONDITION_LABELS[row["condition"]],
                n=row["n"],
                ur=fmt(row["mean_union_recall"]),
                ursd=fmt(row["sd_union_recall"]),
                cr=fmt(row["mean_consensus_recall"]),
                crsd=fmt(row["sd_consensus_recall"]),
                prec=fmt(row["mean_precision"]),
                tok=str(round(row["mean_tokens"])),
                wall=fmt(row["mean_wall_clock"]),
            )
        )
    lines.extend([
        "",
        "## Per-Seed Rows",
        "",
        "| seed | condition | Jaccard | consensus R | union R | precision | tokens | wall-clock s | source |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ])
    for row in sorted(rows, key=lambda x: (x["seed"], x["condition"])):
        lines.append(
            "| {seed} | {condition} | {jac} | {cr} | {ur} | {prec} | {tokens} | {wall} | {source} |".format(
                seed=row["seed"],
                condition=CONDITION_LABELS.get(row["condition"], row["condition"]),
                jac=fmt(row["mean_jaccard"]),
                cr=fmt(row["consensus_recall"]),
                ur=fmt(row["union_recall"]),
                prec=fmt(row["union_precision"]),
                tokens=row["input_tokens"] + row["output_tokens"],
                wall=fmt(row["wall_clock_seconds"]),
                source=row["source"],
            )
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = load_old_seed04() + load_new_grid()
    rows = sorted(rows, key=lambda x: (x["seed"], x["condition"]))
    grouped = summarize(rows)
    write_csv(rows)
    write_md(rows, grouped)
    print(OUT_MD)


if __name__ == "__main__":
    main()
