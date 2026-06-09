#!/usr/bin/env python3
"""Merge individual blind-agent itemset JSON files into a scorer input file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_run(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "runs" in data:
        if len(data["runs"]) != 1:
            raise ValueError(f"{path} contains {len(data['runs'])} runs; expected one")
        data = data["runs"][0]
    for key in ("run_id", "self_reported_completion", "self_reported_confidence", "items"):
        if key not in data:
            raise ValueError(f"{path} missing required key: {key}")
    if not isinstance(data["items"], list):
        raise ValueError(f"{path} items must be a list")
    return data


def normalize_item(item: Any) -> Any:
    if isinstance(item, dict):
        if "file_path" in item and "line" in item:
            return {
                "file_path": str(item["file_path"]).replace("\\", "/"),
                "line": int(item["line"]),
            }
        raise ValueError(f"Unsupported item object: {item}")
    if isinstance(item, str):
        if ":" not in item:
            raise ValueError(f"Unsupported item string: {item}")
        path, line = item.rsplit(":", 1)
        return {"file_path": path.replace("\\", "/"), "line": int(line)}
    raise ValueError(f"Unsupported item type: {item!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--oracle-size", required=True, type=int)
    parser.add_argument("--inputs", nargs="+", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    runs = []
    seen_run_ids: set[str] = set()
    for path in args.inputs:
        run = load_run(path)
        if run["run_id"] in seen_run_ids:
            raise ValueError(f"Duplicate run_id: {run['run_id']}")
        seen_run_ids.add(run["run_id"])
        run["items"] = [normalize_item(item) for item in run["items"]]
        runs.append(run)

    merged = {
        "task_id": args.task_id,
        "oracle_size": args.oracle_size,
        "runs": sorted(runs, key=lambda run: run["run_id"]),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
