#!/usr/bin/env python3
"""Build a deterministic consensus aggregate from G3 itemsets."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
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
            return f"{item['file_path']}:{int(item['line'])}"
        if "source_id" in item and "item_id" in item:
            return f"{item['source_id']}::{item['item_id']}"
    return str(item)


def confidence_of(run: dict[str, Any]) -> float | None:
    confidence = run.get("self_reported_confidence", run.get("confidence"))
    return None if confidence is None else float(confidence)


def mean(values: list[float]) -> float | None:
    return None if not values else sum(values) / len(values)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", required=True, type=Path)
    parser.add_argument("--seed", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--min-support", type=int, default=2)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    data = json.loads(args.runs.read_text(encoding="utf-8"))
    g3_runs = [
        run for run in data["runs"]
        if is_g3(run["run_id"]) and parse_seed(run["run_id"]) == args.seed
    ]
    if not g3_runs:
        raise SystemExit(f"No G3 runs found for seed {args.seed}")

    counts = Counter(
        item_to_text(item)
        for run in g3_runs
        for item in run.get("items", [])
    )
    confidences = [
        value for run in g3_runs
        if (value := confidence_of(run)) is not None
    ]
    items = sorted(
        item for item, count in counts.items()
        if count >= args.min_support
    )
    dropped = sorted(
        item for item, count in counts.items()
        if count < args.min_support
    )

    aggregate = {
        "task_id": data.get("task_id"),
        "oracle_size": data.get("oracle_size"),
        "runs": [
            {
                "run_id": args.run_id,
                "self_reported_completion": True,
                "self_reported_confidence": mean(confidences),
                "items": items,
                "aggregation_policy": "deterministic_min_support_consensus",
                "min_support": args.min_support,
                "uncertain_or_dropped_singletons": dropped,
                "source_g3_run_ids": sorted(run["run_id"] for run in g3_runs),
            }
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(aggregate, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
