#!/usr/bin/env python3
"""Evaluate a source-aware audit policy on real-repo candidate items.

This is an offline prototype for method development. It uses deterministic
task-policy predicates over repository source lines to audit candidate items
from agent unions and holdouts. It does not use oracle labels directly when
selecting items, but for T4/T5 the predicate intentionally mirrors the
pre-registered oracle construction policy, so report it as an audit-policy
upper-bound prototype rather than as a blind LLM run.
"""

from __future__ import annotations

import argparse
import json
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


def t4_click_deprecation(rel_path: str, line_no: int, text: str) -> bool:
    lower = text.lower()
    if "deprecated" not in lower and "deprecationwarning" not in lower:
        return False
    if rel_path in T4_TARGET_FILES:
        return True
    if rel_path == "CHANGES.md" and line_no <= T4_CHANGELOG_MAX_LINE:
        return True
    return False


PREDICATES: dict[str, Callable[[str, int, str], bool]] = {
    "t4_click_deprecation": t4_click_deprecation,
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


def audited_items(
    *,
    base: Path,
    case: AuditCase,
    candidates: set[str],
) -> set[str]:
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


def evaluate_case(base: Path, case: AuditCase) -> dict[str, Any]:
    oracle, _ = load_oracle(base / case.oracle_path)
    runs = load_runs(base / case.runs_path)
    g3_runs = [run for run in runs if run["seed"] == case.seed and run["group"] == "G3"]
    g6_runs = [run for run in runs if run["seed"] == case.seed and run["group"] == "G6"]
    if len(g3_runs) != 3:
        raise ValueError(f"{case.case_id} expected 3 G3 runs, found {len(g3_runs)}")

    counts = Counter(item for run in g3_runs for item in run["items"])
    consensus = {item for item, count in counts.items() if count >= 2}
    union = set(counts)
    holdout = set().union(*(run["items"] for run in g6_runs)) if g6_runs else set()
    candidate_union = union | holdout
    audited_union = audited_items(base=base, case=case, candidates=candidate_union)
    audited_singletons = audited_items(
        base=base,
        case=case,
        candidates={item for item, count in counts.items() if count == 1},
    )
    audited_protocol = consensus | audited_singletons | (audited_union - union)

    pairwise = [
        jaccard(left["items"], right["items"])
        for left, right in combinations(g3_runs, 2)
    ]

    return {
        "case_id": case.case_id,
        "task_id": case.task_id,
        "seed": case.seed,
        "reportable": case.reportable,
        "candidate_union_size": len(candidate_union),
        "mean_pairwise_jaccard": sum(pairwise) / len(pairwise) if pairwise else None,
        "rows": [
            {"method": "majority_consensus", **score_set(consensus, oracle)},
            {"method": "raw_union", **score_set(union, oracle)},
            {"method": "holdout_union", **score_set(holdout, oracle)},
            {"method": "source_aware_audited_union", **score_set(audited_union, oracle)},
            {"method": "source_aware_protocol_v1", **score_set(audited_protocol, oracle)},
        ],
    }


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in row.items()
        if key not in {"true_items", "false_items"}
    }


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Source-Aware Audit v1 Results",
        "",
        "This is an offline audit-policy prototype. It audits candidate line items",
        "against deterministic source predicates derived from the task policy.",
        "Report it as an upper-bound prototype, not as a blind LLM result.",
        "",
        "| case | method | found | TP | FP | recall | precision |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for case in summary["cases"]:
        for row in case["rows"]:
            lines.append(
                "| {case_id} | {method} | {found} | {tp} | {fp} | {recall} | {precision} |".format(
                    case_id=case["case_id"],
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
        "## Interpretation",
        "",
        "- If audited union improves precision over raw union while keeping high recall, the task policy can support stronger audit.",
        "- If audited protocol still misses items, the missing mass is outside the current candidate pool and requires broader search, not only candidate filtering.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path("experiments/false_convergence_pilot"))
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("experiments/false_convergence_pilot/protocol_outputs/source_aware_audit_v1_results.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("experiments/false_convergence_pilot/reports/protocol/SOURCE_AWARE_AUDIT_V1_RESULTS.md"),
    )
    args = parser.parse_args()

    cases = [evaluate_case(args.base, case) for case in CASES]
    summary = {
        "notes": {
            "status": "offline_audit_policy_prototype",
            "oracle_use": "oracle is used only for scoring; predicates mirror task policy",
        },
        "cases": [
            {
                **{key: value for key, value in case.items() if key != "rows"},
                "rows": [compact_row(row) for row in case["rows"]],
            }
            for case in cases
        ],
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(summary, args.out_md)


if __name__ == "__main__":
    main()
