#!/usr/bin/env python3
"""Postprocess T5 blind-agent outputs once the independent runs are complete."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_files(seed: str) -> list[str]:
    return [
        f"T5_G3_{seed}_agent01.json",
        f"T5_G3_{seed}_agent02.json",
        f"T5_G3_{seed}_agent03.json",
        f"T5_G6_holdout_{seed}.json",
    ]


def run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--base",
        type=Path,
        default=Path("experiments/false_convergence_pilot"),
    )
    parser.add_argument("--seed", default="seed01")
    args = parser.parse_args()

    root = args.root.resolve()
    base = args.base
    run_dir = base / "T5_real_repo_requests_tls_blind_runs"
    files = run_files(args.seed)
    missing = [name for name in files if not (root / run_dir / name).exists()]
    if missing:
        missing_text = "\n".join(f"- {run_dir / name}" for name in missing)
        raise SystemExit(
            "T5 blind outputs are not complete yet. Missing files:\n"
            f"{missing_text}"
        )

    result_dir = base / "results"
    merged = result_dir / f"T5_real_repo_requests_tls_{args.seed}_blind_itemsets.json"
    score_json = result_dir / f"T5_real_repo_requests_tls_{args.seed}_blind_score_summary.json"
    score_md = result_dir / f"T5_real_repo_requests_tls_{args.seed}_blind_score_summary.md"
    oracle = result_dir / "T5_real_repo_requests_tls_oracle.json"

    run([
        sys.executable,
        str(base / "tools" / "merge_blind_itemsets.py"),
        "--task-id",
        "T5_real_repo_requests_tls_audit",
        "--oracle-size",
        "304",
        "--inputs",
        *[str(run_dir / name) for name in files],
        "--out",
        str(merged),
    ], cwd=root)

    run([
        sys.executable,
        str(base / "tools" / "score_itemsets.py"),
        "--oracle",
        str(oracle),
        "--runs",
        str(merged),
        "--out-json",
        str(score_json),
        "--out-md",
        str(score_md),
    ], cwd=root)

    print("T5 blind postprocess complete.")
    print(f"- merged: {merged}")
    print(f"- score: {score_md}")


if __name__ == "__main__":
    main()
