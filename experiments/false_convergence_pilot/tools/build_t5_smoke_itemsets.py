#!/usr/bin/env python3
"""Create a non-experimental smoke itemset for T5 scorer compatibility."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORACLE = ROOT / "results" / "T5_real_repo_requests_tls_oracle.json"
OUT = ROOT / "results" / "T5_real_repo_requests_tls_seed01_smoke_itemsets.json"


def main() -> None:
    oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
    items = [
        f"{item['file_path']}:{item['line']}"
        for item in oracle["items"]
    ]
    raw = {
        "task_id": "T5_real_repo_requests_tls_audit",
        "oracle_size": len(items),
        "non_experimental_notice": (
            "Smoke scorer compatibility file generated from oracle. "
            "Do not report as blind-agent result."
        ),
        "runs": [
            {
                "run_id": "T5_G3_seed01_smoke_agent01",
                "group_id": "G3",
                "self_reported_completion": True,
                "self_reported_confidence": 1.0,
                "items": items,
            },
            {
                "run_id": "T5_G3_seed01_smoke_agent02",
                "group_id": "G3",
                "self_reported_completion": True,
                "self_reported_confidence": 1.0,
                "items": items,
            },
            {
                "run_id": "T5_G3_seed01_smoke_agent03",
                "group_id": "G3",
                "self_reported_completion": True,
                "self_reported_confidence": 1.0,
                "items": items,
            },
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(raw, indent=2), encoding="utf-8")
    print(f"Wrote T5 smoke itemsets with {len(items)} items")


if __name__ == "__main__":
    main()
