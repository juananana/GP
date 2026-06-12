#!/usr/bin/env python3
"""Run the T5 Requests TLS blind-agent and summarizer pipeline."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "false_convergence_pilot"
TASK_ROOT = BASE / "T5_real_repo_requests_tls"
BLIND_RUNS = BASE / "T5_real_repo_requests_tls_blind_runs"
RESULTS = BASE / "results"
SUMMARIZER_INPUTS = BASE / "summarizer_inputs"
SUMMARIZER_OUTPUTS = BASE / "summarizer_outputs"
RUN_COST_LOGS = BASE / "run_cost_logs"


COMMON_FILES = [
    "TASK.md",
    "repo/src/requests/adapters.py",
    "repo/src/requests/sessions.py",
    "repo/src/requests/certs.py",
    "repo/src/requests/utils.py",
    "repo/src/requests/exceptions.py",
    "repo/tests/test_requests.py",
    "repo/tests/conftest.py",
    "repo/tests/testserver/server.py",
    "repo/tests/certs/README.md",
    "repo/docs/user/advanced.rst",
    "repo/docs/community/faq.rst",
    "repo/docs/community/recommended.rst",
    "repo/README.md",
]


AGENT_FILE_PLANS = {
    "agent01": [
        "repo/src/requests/adapters.py",
        "repo/src/requests/sessions.py",
        "repo/src/requests/certs.py",
        "repo/src/requests/utils.py",
        "repo/src/requests/exceptions.py",
        "repo/tests/test_requests.py",
        "repo/docs/user/advanced.rst",
        "repo/tests/certs/README.md",
    ],
    "agent02": [
        "repo/docs/user/advanced.rst",
        "repo/src/requests/utils.py",
        "repo/src/requests/adapters.py",
        "repo/tests/test_requests.py",
        "repo/tests/conftest.py",
        "repo/tests/testserver/server.py",
        "repo/docs/community/faq.rst",
        "repo/docs/community/recommended.rst",
    ],
    "agent03": [
        "repo/tests/test_requests.py",
        "repo/src/requests/sessions.py",
        "repo/src/requests/adapters.py",
        "repo/src/requests/certs.py",
        "repo/src/requests/utils.py",
        "repo/README.md",
        "repo/docs/user/advanced.rst",
        "repo/tests/certs/README.md",
    ],
    "holdout": [
        "repo/src/requests/adapters.py",
        "repo/src/requests/sessions.py",
        "repo/src/requests/utils.py",
        "repo/tests/test_requests.py",
        "repo/tests/testserver/server.py",
        "repo/docs/user/advanced.rst",
        "repo/docs/community/faq.rst",
        "repo/docs/community/recommended.rst",
        "repo/tests/certs/README.md",
        "repo/README.md",
    ],
}


def run(command: list[str], cwd: Path, dry_run: bool) -> None:
    printable = " ".join(str(part) for part in command)
    if dry_run:
        print(printable)
        return
    subprocess.run(command, cwd=cwd, check=True)


def run_agent(seed: str, role: str, dry_run: bool, force: bool) -> None:
    if role == "holdout":
        run_id = f"T5_G6_holdout_{seed}"
        out_name = f"{run_id}.json"
    else:
        run_id = f"T5_G3_{seed}_{role}"
        out_name = f"{run_id}.json"
    out = BLIND_RUNS / out_name
    if out.exists() and not force:
        print(f"skip existing {out}")
        return
    run([
        sys.executable,
        str(BASE / "tools" / "run_autodl_blind_agent.py"),
        "--task-root",
        str(TASK_ROOT),
        "--task-root-label",
        "experiments/false_convergence_pilot/T5_real_repo_requests_tls/",
        "--run-id",
        run_id,
        "--files",
        *AGENT_FILE_PLANS[role],
        "--out",
        str(out),
        "--raw-out",
        str(BLIND_RUNS / f"{run_id}_raw_response.json"),
        "--cost-out",
        str(RUN_COST_LOGS / f"{run_id}_cost.json"),
        "--search-budget",
        "360",
    ], ROOT.parent, dry_run)


def score_summarizer(
    *,
    seed: str,
    policy: str,
    itemsets: Path,
    dry_run: bool,
) -> None:
    stem = f"T5_real_repo_requests_tls_{seed}_sum_{policy}_autodl"
    run([
        sys.executable,
        str(BASE / "tools" / "score_itemsets.py"),
        "--oracle",
        str(RESULTS / "T5_real_repo_requests_tls_oracle.json"),
        "--runs",
        str(itemsets),
        "--out-json",
        str(SUMMARIZER_OUTPUTS / f"{stem}_score_summary.json"),
        "--out-md",
        str(SUMMARIZER_OUTPUTS / f"{stem}_score_summary.md"),
    ], ROOT.parent, dry_run)


def run_summarizer(seed: str, policy: str, dry_run: bool, force: bool) -> None:
    stem = f"T5_real_repo_requests_tls_{seed}_sum_{policy}_autodl"
    out = SUMMARIZER_OUTPUTS / f"{stem}_itemsets.json"
    if out.exists() and not force:
        print(f"skip existing {out}")
        score_summarizer(seed=seed, policy=policy, itemsets=out, dry_run=dry_run)
        return
    run([
        sys.executable,
        str(BASE / "tools" / "run_autodl_summarizer.py"),
        "--packet",
        str(SUMMARIZER_INPUTS / f"T5_real_repo_requests_tls_{seed}_g3_packet.md"),
        "--policy",
        policy,
        "--run-id",
        f"T5_{seed}_sum_{policy}_autodl",
        "--task-id",
        "T5_real_repo_requests_tls_audit",
        "--oracle-size",
        "304",
        "--out",
        str(out),
        "--raw-out",
        str(SUMMARIZER_OUTPUTS / f"{stem}_raw_response.json"),
        "--cost-out",
        str(RUN_COST_LOGS / f"{stem}_cost.json"),
    ], ROOT.parent, dry_run)
    score_summarizer(seed=seed, policy=policy, itemsets=out, dry_run=dry_run)


def score_aggregate(*, seed: str, name: str, itemsets: Path, dry_run: bool) -> None:
    run([
        sys.executable,
        str(BASE / "tools" / "score_itemsets.py"),
        "--oracle",
        str(RESULTS / "T5_real_repo_requests_tls_oracle.json"),
        "--runs",
        str(itemsets),
        "--out-json",
        str(SUMMARIZER_OUTPUTS / f"T5_real_repo_requests_tls_{seed}_sum_{name}_score_summary.json"),
        "--out-md",
        str(SUMMARIZER_OUTPUTS / f"T5_real_repo_requests_tls_{seed}_sum_{name}_score_summary.md"),
    ], ROOT.parent, dry_run)


def build_deterministic_aggregates(seed: str, dry_run: bool) -> None:
    runs_path = RESULTS / f"T5_real_repo_requests_tls_{seed}_blind_itemsets.json"
    consensus_out = SUMMARIZER_OUTPUTS / f"T5_real_repo_requests_tls_{seed}_sum_consensus_itemsets.json"
    union_out = SUMMARIZER_OUTPUTS / f"T5_real_repo_requests_tls_{seed}_sum_union_preserving_itemsets.json"

    run([
        sys.executable,
        str(BASE / "tools" / "build_consensus_aggregate.py"),
        "--runs",
        str(runs_path),
        "--seed",
        seed,
        "--run-id",
        f"T5_{seed}_sum_consensus",
        "--out",
        str(consensus_out),
    ], ROOT.parent, dry_run)
    score_aggregate(seed=seed, name="consensus", itemsets=consensus_out, dry_run=dry_run)

    run([
        sys.executable,
        str(BASE / "tools" / "build_union_preserving_aggregate.py"),
        "--runs",
        str(runs_path),
        "--seed",
        seed,
        "--run-id",
        f"T5_{seed}_sum_union_preserving",
        "--out",
        str(union_out),
    ], ROOT.parent, dry_run)
    score_aggregate(seed=seed, name="union_preserving", itemsets=union_out, dry_run=dry_run)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default="seed01")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-agents", action="store_true")
    parser.add_argument("--skip-summarizers", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not os.environ.get("AUTODL_ART_API_KEY"):
        raise SystemExit(
            "Missing AUTODL_ART_API_KEY. Set it in the current shell before "
            "running this pipeline. Do not write the key to repo files."
        )

    if not args.skip_agents:
        for role in ("agent01", "agent02", "agent03", "holdout"):
            run_agent(args.seed, role, args.dry_run, args.force)

    run([
        sys.executable,
        str(BASE / "tools" / "run_t5_blind_postprocess.py"),
        "--seed",
        args.seed,
    ], ROOT.parent, args.dry_run)

    run([
        sys.executable,
        str(BASE / "tools" / "build_summarizer_inputs.py"),
        "--runs",
        str(RESULTS / f"T5_real_repo_requests_tls_{args.seed}_blind_itemsets.json"),
        "--seed",
        args.seed,
        "--task-label",
        "T5 real Requests TLS audit",
        "--out",
        str(SUMMARIZER_INPUTS / f"T5_real_repo_requests_tls_{args.seed}_g3_packet.md"),
    ], ROOT.parent, args.dry_run)

    build_deterministic_aggregates(args.seed, args.dry_run)

    if not args.skip_summarizers:
        for policy in ("standard", "union_preserving"):
            run_summarizer(args.seed, policy, args.dry_run, args.force)


if __name__ == "__main__":
    main()
