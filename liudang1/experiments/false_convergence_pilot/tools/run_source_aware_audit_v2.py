#!/usr/bin/env python3
"""Evaluate stronger source-aware audit policies.

This script separates two increasingly strong audit levels:

1. candidate_filter_v2 audits every candidate already reported by G3 or holdout,
   including consensus items. This can remove consensus false positives and
   recover candidate-pool omissions without adding unseen source lines.
2. source_sweep_v2 applies the same pre-registered task predicate to the bounded
   target source files. This is an audit-policy upper-bound prototype, useful for
   asking whether a stronger audit could recover missing items outside the
   current candidate pool.

The script uses oracle labels only for scoring after the policy has selected
items. The deterministic predicates mirror the task construction policy, so
source_sweep_v2 must not be reported as a blind LLM result.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Callable

from score_itemsets import jaccard, load_oracle, normalize_run, score_set


@dataclass(frozen=True)
class AuditCase:
    case_id: str
    task_id: str
    oracle_path: str
    runs_path: str
    repo_root: str
    predicate_name: str
    seed: str
    reportable: bool = True


CASES = [
    AuditCase(
        case_id="T4_real_repo_click_seed01_blind",
        task_id="T4_real_repo_click_deprecation",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed01_blind_itemsets.json",
        repo_root="T4_real_repo_click",
        predicate_name="t4_click_deprecation",
        seed="seed01",
    ),
    AuditCase(
        case_id="T4_real_repo_click_seed02_blind",
        task_id="T4_real_repo_click_deprecation",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed02_blind_itemsets.json",
        repo_root="T4_real_repo_click",
        predicate_name="t4_click_deprecation",
        seed="seed02",
    ),
    AuditCase(
        case_id="T4_real_repo_click_seed03_blind",
        task_id="T4_real_repo_click_deprecation",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        runs_path="results/T4_real_repo_click_seed03_blind_itemsets.json",
        repo_root="T4_real_repo_click",
        predicate_name="t4_click_deprecation",
        seed="seed03",
    ),
    AuditCase(
        case_id="T5_real_repo_requests_tls_seed01_smoke",
        task_id="T5_real_repo_requests_tls_audit",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed01_smoke_itemsets.json",
        repo_root="T5_real_repo_requests_tls",
        predicate_name="t5_requests_tls",
        seed="seed01",
        reportable=False,
    ),
    AuditCase(
        case_id="T5_real_repo_requests_tls_seed01_blind",
        task_id="T5_real_repo_requests_tls_audit",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed01_blind_itemsets.json",
        repo_root="T5_real_repo_requests_tls",
        predicate_name="t5_requests_tls",
        seed="seed01",
        reportable=True,
    ),
    AuditCase(
        case_id="T5_real_repo_requests_tls_seed02_blind",
        task_id="T5_real_repo_requests_tls_audit",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed02_blind_itemsets.json",
        repo_root="T5_real_repo_requests_tls",
        predicate_name="t5_requests_tls",
        seed="seed02",
        reportable=True,
    ),
    AuditCase(
        case_id="T5_real_repo_requests_tls_seed03_blind",
        task_id="T5_real_repo_requests_tls_audit",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        runs_path="results/T5_real_repo_requests_tls_seed03_blind_itemsets.json",
        repo_root="T5_real_repo_requests_tls",
        predicate_name="t5_requests_tls",
        seed="seed03",
        reportable=True,
    ),
]


T4_TARGET_FILES = {
    "src/click/__init__.py",
    "src/click/core.py",
    "src/click/parser.py",
    "tests/test_arguments.py",
    "tests/test_commands.py",
    "tests/test_options.py",
    "docs/commands-and-groups.md",
}
T4_CHANGELOG_MAX_LINE = 420

T5_TARGET_FILES = {
    "README.md",
    "src/requests/adapters.py",
    "src/requests/api.py",
    "src/requests/certs.py",
    "src/requests/exceptions.py",
    "src/requests/sessions.py",
    "src/requests/utils.py",
    "tests/conftest.py",
    "tests/test_requests.py",
    "tests/testserver/server.py",
    "tests/certs/README.md",
    "docs/user/advanced.rst",
    "docs/community/faq.rst",
    "docs/community/recommended.rst",
}
T5_TLS_TERMS = (
    "tls",
    "ssl",
    "certificate",
    "certificates",
    "certifi",
    "ca bundle",
    "ca_bundle",
    "ca_cert",
    "cacert",
    "requests_ca_bundle",
    "curl_ca_bundle",
    "default_ca_bundle_path",
    "client cert",
    "client certificate",
    "cert_file",
    "key_file",
    "cert_reqs",
    "cert_none",
    "cert_required",
    "sslerror",
    "verify",
)


def normalized(text: str) -> str:
    return re.sub(r"[^a-z0-9_]+", " ", text.lower())


def t4_click_deprecation(rel_path: str, line_no: int, text: str) -> bool:
    lower = text.lower()
    if "deprecated" not in lower and "deprecationwarning" not in lower:
        return False
    if rel_path in T4_TARGET_FILES:
        return True
    if rel_path == "CHANGES.md" and line_no <= T4_CHANGELOG_MAX_LINE:
        return True
    return False


def t5_requests_tls(rel_path: str, line_no: int, text: str) -> bool:
    del line_no
    norm = normalized(text)
    if rel_path not in T5_TARGET_FILES:
        return False
    if rel_path == "README.md":
        return "tls ssl verification" in norm
    if rel_path.startswith("docs/"):
        return any(term.replace("_", " ") in norm for term in T5_TLS_TERMS)
    if rel_path.startswith("tests/certs/"):
        return "certificate" in norm or "certificates" in norm or "mtls" in norm
    return any(term in norm for term in T5_TLS_TERMS)


PREDICATES: dict[str, Callable[[str, int, str], bool]] = {
    "t4_click_deprecation": t4_click_deprecation,
    "t5_requests_tls": t5_requests_tls,
}

SWEEP_FILES = {
    "t4_click_deprecation": sorted(T4_TARGET_FILES | {"CHANGES.md"}),
    "t5_requests_tls": sorted(T5_TARGET_FILES),
}


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def load_runs(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [normalize_run(run) for run in raw["runs"]]


def parse_line_item(item: str) -> tuple[str, int] | None:
    if "::" in item or ":" not in item:
        return None
    path, line = item.rsplit(":", 1)
    try:
        return path, int(line)
    except ValueError:
        return None


def source_line(base: Path, repo_root: str, item: str) -> tuple[str, int, str] | None:
    parsed = parse_line_item(item)
    if not parsed:
        return None
    path, line_no = parsed
    if not path.startswith("repo/"):
        return None
    rel_path = path.removeprefix("repo/")
    file_path = base / repo_root / "repo" / rel_path
    if not file_path.exists() or not file_path.is_file():
        return None
    lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if line_no < 1 or line_no > len(lines):
        return None
    return rel_path, line_no, lines[line_no - 1]


def audited_items(*, base: Path, case: AuditCase, candidates: set[str]) -> set[str]:
    predicate = PREDICATES[case.predicate_name]
    kept: set[str] = set()
    for item in candidates:
        loaded = source_line(base, case.repo_root, item)
        if not loaded:
            continue
        rel_path, line_no, text = loaded
        if predicate(rel_path, line_no, text):
            kept.add(item)
    return kept


def source_sweep_items(*, base: Path, case: AuditCase) -> set[str]:
    predicate = PREDICATES[case.predicate_name]
    repo = base / case.repo_root / "repo"
    kept: set[str] = set()
    for rel_path in SWEEP_FILES[case.predicate_name]:
        path = repo / rel_path
        if not path.exists() or not path.is_file():
            continue
        for line_no, text in enumerate(
            path.read_text(encoding="utf-8", errors="ignore").splitlines(),
            start=1,
        ):
            if predicate(rel_path, line_no, text):
                kept.add(f"repo/{rel_path}:{line_no}")
    return kept


def compact_score(items: set[str], oracle: set[str]) -> dict[str, Any]:
    score = score_set(items, oracle)
    return {
        key: value
        for key, value in score.items()
        if key not in {"true_items", "false_items"}
    }


def evaluate_case(base: Path, case: AuditCase) -> dict[str, Any] | None:
    runs_path = base / case.runs_path
    oracle_path = base / case.oracle_path
    if not runs_path.exists() or not oracle_path.exists():
        return None

    oracle, _ = load_oracle(oracle_path)
    runs = load_runs(runs_path)
    g3_runs = [run for run in runs if run["seed"] == case.seed and run["group"] == "G3"]
    g6_runs = [run for run in runs if run["seed"] == case.seed and run["group"] == "G6"]
    if len(g3_runs) != 3:
        return None

    counts = Counter(item for run in g3_runs for item in run["items"])
    consensus = {item for item, count in counts.items() if count >= 2}
    union = set(counts)
    holdout = set().union(*(run["items"] for run in g6_runs)) if g6_runs else set()
    candidate_pool = union | holdout
    audited_candidate_pool = audited_items(base=base, case=case, candidates=candidate_pool)
    swept = source_sweep_items(base=base, case=case)
    source_sweep_topup = audited_candidate_pool | (swept - candidate_pool)

    pairwise = [
        jaccard(left["items"], right["items"])
        for left, right in combinations(g3_runs, 2)
    ]

    rows = [
        {"method": "majority_consensus", **compact_score(consensus, oracle)},
        {"method": "raw_union", **compact_score(union, oracle)},
        {"method": "holdout_union", **compact_score(holdout, oracle)},
        {"method": "candidate_pool", **compact_score(candidate_pool, oracle)},
        {"method": "source_aware_candidate_filter_v2", **compact_score(audited_candidate_pool, oracle)},
        {"method": "source_sweep_v2_upper_bound", **compact_score(source_sweep_topup, oracle)},
    ]

    return {
        "case_id": case.case_id,
        "task_id": case.task_id,
        "seed": case.seed,
        "reportable": case.reportable,
        "candidate_pool_size": len(candidate_pool),
        "source_sweep_size": len(swept),
        "source_sweep_new_items": len(swept - candidate_pool),
        "mean_pairwise_jaccard": sum(pairwise) / len(pairwise) if pairwise else None,
        "rows": rows,
    }


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Source-Aware Audit v2 Results",
        "",
        "This report separates candidate-pool filtering from source-sweep audit.",
        "`source_aware_candidate_filter_v2` audits items already discovered by G3/holdout.",
        "`source_sweep_v2_upper_bound` is an audit-policy upper bound, not a blind LLM result.",
        "",
        "| case | reportable | method | found | TP | FP | recall | precision |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for case in summary["cases"]:
        for row in case["rows"]:
            lines.append(
                "| {case_id} | {reportable} | {method} | {found} | {tp} | {fp} | {recall} | {precision} |".format(
                    case_id=case["case_id"],
                    reportable=fmt(case["reportable"]),
                    method=row["method"],
                    found=row["found"],
                    tp=row["true_positive"],
                    fp=row["false_positive"],
                    recall=fmt(row["recall"]),
                    precision=fmt(row["precision"]),
                )
            )
    lines.extend([
        "",
        "## Notes",
        "",
        "- Candidate filtering is the cleaner reportable direction when blind agents already surfaced the item.",
        "- Source sweep shows whether a stronger audit policy can recover items missing from all current candidates.",
        "- T5 smoke rows are scorer/pipeline checks only; T5 blind rows are reportable evidence.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path("experiments/false_convergence_pilot"))
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("experiments/false_convergence_pilot/protocol_outputs/source_aware_audit_v2_results.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("experiments/false_convergence_pilot/reports/protocol/SOURCE_AWARE_AUDIT_V2_RESULTS.md"),
    )
    args = parser.parse_args()

    cases = [case for raw in CASES if (case := evaluate_case(args.base, raw)) is not None]
    summary = {
        "notes": {
            "status": "offline_audit_policy_prototype",
            "oracle_use": "oracle is used only for scoring; predicates mirror task policy",
            "candidate_filter_v2": "audits all existing G3/holdout candidates",
            "source_sweep_v2": "upper-bound source sweep over bounded target files",
        },
        "cases": cases,
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(summary, args.out_md)


if __name__ == "__main__":
    main()
