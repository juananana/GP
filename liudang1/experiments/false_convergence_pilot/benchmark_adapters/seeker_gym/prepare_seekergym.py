#!/usr/bin/env python3
"""Prepare SeekerGym exports for the local completion-certificate pipeline.

This script is intentionally conservative. It does not claim benchmark results;
it only validates paths and writes a manifest/TODO until a concrete SeekerGym
schema is wired in.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seekergym-root", type=Path, required=True)
    parser.add_argument("--split", default="validation")
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "adapter": "seekergym",
        "status": "schema_mapping_todo",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "seekergym_root": str(args.seekergym_root),
        "seekergym_root_exists": args.seekergym_root.exists(),
        "split": args.split,
        "outputs_not_generated": [
            "oracle.json",
            "itemsets.json",
            "run_cost_logs/*.json",
        ],
        "todo": [
            "Confirm SeekerGym local schema.",
            "Map episode targets to closed-world oracle items.",
            "Map agent traces to local run itemsets.",
            "Record model, prompt, budget, seed, token, tool-call, and wall-clock logs.",
        ],
    }
    (args.out_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
