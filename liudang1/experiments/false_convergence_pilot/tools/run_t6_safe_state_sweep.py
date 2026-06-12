#!/usr/bin/env python3
"""Run a small T6 safe-state sweep with boundary-focused holdout agents."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from run_t6_itsdangerous_staged_controller import MODEL, ORACLE, OUT_ROOT, TASK_ROOT
from score_itemsets import canonical, load_oracle, parse_item, score_set


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "false_convergence_pilot"
SAFE_ROOT = OUT_ROOT / "safe_state_sweep"
TASK_ID = "T6_itsdangerous_safe_state_sweep"
ORACLE_SIZE = 160
FILES = [
    "repo/src/itsdangerous/timed.py",
    "repo/src/itsdangerous/exc.py",
    "repo/src/itsdangerous/__init__.py",
    "repo/tests/test_itsdangerous/test_timed.py",
    "repo/docs/timed.rst",
    "repo/docs/exceptions.rst",
    "repo/docs/url_safe.rst",
    "repo/CHANGES.rst",
]


def parse_run_items(path: Path) -> set[str]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {parsed for item in raw.get("items", []) if (parsed := parse_item(item))}


def existing_seed_union(seed: str) -> set[str]:
    items: set[str] = set()
    for condition in ["homogeneous", "source_partitioned", "independent_context"]:
        for path in (OUT_ROOT / seed / condition / "runs").glob("*.json"):
            items |= parse_run_items(path)
    return items


def run_boundary_agent(seed: str, agent: int, dry_run: bool) -> Path:
    run_id = f"T6_itsdangerous_{seed}_safe_sweep_G6_boundary_agent{agent:02d}"
    out = SAFE_ROOT / seed / "runs" / f"{run_id}.json"
    if dry_run or out.exists():
        return out
    addon = (
        f"Fixed safe-state sweep seed label: {seed}. Focus on timestamp-related "
        "exception/date_signed behavior, SignatureExpired/BadTimeSignature, "
        "max_age edge cases, future timestamps, overflow notes, and bounded "
        "changelog/documentation lines. Return exact in-scope lines only."
    )
    subprocess.run([
        sys.executable,
        str(BASE / "tools" / "run_autodl_blind_agent.py"),
        "--task-root",
        str(TASK_ROOT),
        "--task-root-label",
        "experiments/false_convergence_pilot/T6_real_repo_itsdangerous/",
        "--run-id",
        run_id,
        "--files",
        *FILES,
        "--out",
        str(out),
        "--raw-out",
        str(SAFE_ROOT / seed / "raw" / f"{run_id}_raw_response.json"),
        "--cost-out",
        str(SAFE_ROOT / seed / "cost" / f"{run_id}_cost.json"),
        "--search-budget",
        "260",
        "--max-lines-per-file",
        "1600",
        "--prompt-variant",
        "t6_boundary_safe_state_sweep",
        "--prompt-addon",
        addon,
        "--model",
        MODEL,
    ], cwd=ROOT.parent, check=True)
    return out


def load_costs(seed: str) -> dict[str, float]:
    total = {"input_tokens": 0, "output_tokens": 0, "tool_calls": 0, "wall_clock_seconds": 0.0}
    for path in (SAFE_ROOT / seed / "cost").glob("*_cost.json"):
        raw = json.loads(path.read_text(encoding="utf-8"))
        total["input_tokens"] += int(raw.get("input_tokens") or 0)
        total["output_tokens"] += int(raw.get("output_tokens") or 0)
        total["tool_calls"] += int(raw.get("tool_calls") or 0)
        total["wall_clock_seconds"] += float(raw.get("wall_clock_seconds") or 0.0)
    return total


def write_summary(seed: str, run_paths: list[Path]) -> None:
    oracle, buckets = load_oracle(ORACLE)
    base_items = existing_seed_union(seed)
    boundary_items = set().union(*(parse_run_items(path) for path in run_paths if path.exists()))
    final_items = base_items | boundary_items
    base_score = score_set(base_items, oracle)
    final_score = score_set(final_items, oracle)
    cost = load_costs(seed)
    summary = {
        "task_id": TASK_ID,
        "seed": seed,
        "base_union": {k: v for k, v in base_score.items() if k not in {"true_items", "false_items"}},
        "safe_sweep": {k: v for k, v in final_score.items() if k not in {"true_items", "false_items"}},
        "recovered_tp": len((final_items - base_items) & oracle),
        "introduced_fp": len((final_items - base_items) - oracle),
        "safe_state": final_score["recall"] >= 0.95,
        "cost": cost,
        "run_paths": [str(path) for path in run_paths],
    }
    SAFE_ROOT.mkdir(parents=True, exist_ok=True)
    (SAFE_ROOT / f"{seed}_SAFE_STATE_SWEEP_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    lines = [
        "# T6 Safe-State Sweep",
        "",
        f"Seed: `{seed}`",
        "",
        "| state | recall | precision | found | tp | fp |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        "| base union | {recall:.3f} | {precision:.3f} | {found} | {true_positive} | {false_positive} |".format(**summary["base_union"]),
        "| + boundary sweep | {recall:.3f} | {precision:.3f} | {found} | {true_positive} | {false_positive} |".format(**summary["safe_sweep"]),
        "",
        f"Safe state reached: `{summary['safe_state']}`",
        f"Recovered TP: `{summary['recovered_tp']}`",
        f"Introduced FP: `{summary['introduced_fp']}`",
        f"Audit tokens: `{cost['input_tokens'] + cost['output_tokens']}`",
    ]
    (SAFE_ROOT / f"{seed}_SAFE_STATE_SWEEP_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(SAFE_ROOT / f"{seed}_SAFE_STATE_SWEEP_SUMMARY.md")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default="seed04")
    parser.add_argument("--agents", type=int, default=3)
    parser.add_argument("--run-online", action="store_true")
    args = parser.parse_args()
    if args.run_online and not os.environ.get("AUTODL_ART_API_KEY"):
        raise SystemExit("Missing AUTODL_ART_API_KEY")
    paths = [run_boundary_agent(args.seed, idx, not args.run_online) for idx in range(1, args.agents + 1)]
    write_summary(args.seed, paths)


if __name__ == "__main__":
    main()
