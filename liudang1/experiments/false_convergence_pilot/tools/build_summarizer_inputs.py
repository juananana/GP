#!/usr/bin/env python3
"""Build blind aggregation packets from existing G3 itemsets."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def parse_seed(run_id: str) -> str:
    match = re.search(r"seed\d+", run_id)
    return match.group(0) if match else "seed_unknown"


def is_g3(run_id: str) -> bool:
    return "_G3_" in run_id or run_id.startswith("G3")


def item_to_text(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        if "file_path" in item and "line" in item:
            return f"{item['file_path']}:{item['line']}"
        if "source_id" in item and "item_id" in item:
            return f"{item['source_id']}::{item['item_id']}"
    return str(item)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", required=True, type=Path)
    parser.add_argument("--seed", required=True)
    parser.add_argument("--task-label", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    data = json.loads(args.runs.read_text(encoding="utf-8"))
    runs = [
        run for run in data["runs"]
        if is_g3(run["run_id"]) and parse_seed(run["run_id"]) == args.seed
    ]
    runs.sort(key=lambda run: run["run_id"])

    lines = [
        f"# Aggregation Packet: {args.task_label} {args.seed}",
        "",
        "This packet contains final reports from three blind G3 agents.",
        "Do not inspect task files, oracle files, holdout reports, or result summaries.",
        "Aggregate only from the reports below.",
        "",
        "Each reported item is an agent-claimed migration point. Some items may be",
        "reported by only one agent. The packet does not tell you which items are",
        "true positives.",
        "",
    ]

    for index, run in enumerate(runs, start=1):
        confidence = run.get("self_reported_confidence", run.get("confidence", "unknown"))
        lines.extend([
            f"## Agent {index}: {run['run_id']}",
            "",
            f"Self-reported confidence: {confidence}",
            "",
        ])
        for item in run.get("items", []):
            lines.append(f"- {item_to_text(item)}")
        lines.append("")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
