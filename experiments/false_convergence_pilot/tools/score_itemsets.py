#!/usr/bin/env python3
"""Score AgentCompletion itemset runs against a closed-world oracle."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any


THETA = 0.95
TAU = 0.70
CONFIDENCE_THRESHOLD = 0.80


def canonical(file_path: str, line: int | str) -> str:
    return f"{file_path.replace('\\', '/')}:{int(line)}"


def parse_item(item: Any) -> str | None:
    if isinstance(item, str):
        if "::" in item:
            return item
        if ":" not in item:
            return None
        path, line = item.rsplit(":", 1)
        try:
            return canonical(path, int(line))
        except ValueError:
            return None
    if isinstance(item, dict):
        if "file_path" in item and "line" in item:
            return canonical(str(item["file_path"]), item["line"])
        if "source_id" in item and "item_id" in item:
            return f"{item['source_id']}::{item['item_id']}"
    return None


def parse_seed(run_id: str) -> str:
    match = re.search(r"seed\d+", run_id)
    return match.group(0) if match else "seed_unknown"


def parse_group(run_id: str, explicit_group: str | None = None) -> str:
    if explicit_group:
        return explicit_group
    for group in ("G1", "G2", "G3", "G6"):
        if f"_{group}_" in run_id or run_id.startswith(group):
            return group
    return "unknown"


def jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def load_oracle(path: Path) -> tuple[set[str], dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    oracle: set[str] = set()
    buckets: dict[str, str] = {}
    for item in data["items"]:
        if "file_path" in item:
            key = canonical(item["file_path"], item["line"])
        else:
            key = f"{item['source_id']}::{item['item_id']}"
        oracle.add(key)
        buckets[key] = item.get("bucket") or item.get("difficulty_tag") or "unbucketed"
    return oracle, buckets


def normalize_run(run: dict[str, Any]) -> dict[str, Any]:
    items = {parsed for item in run.get("items", []) if (parsed := parse_item(item))}
    confidence = run.get("self_reported_confidence", run.get("confidence"))
    completion = run.get("self_reported_completion")
    if completion is None:
        completion = bool(confidence is not None and float(confidence) >= CONFIDENCE_THRESHOLD)
    return {
        "run_id": run["run_id"],
        "seed": parse_seed(run["run_id"]),
        "group": parse_group(run["run_id"], run.get("group_id")),
        "confidence": None if confidence is None else float(confidence),
        "completion": bool(completion),
        "items": items,
        "raw_items": run.get("items", []),
    }


def score_set(items: set[str], oracle: set[str]) -> dict[str, Any]:
    true_items = items & oracle
    false_items = items - oracle
    return {
        "found": len(items),
        "true_positive": len(true_items),
        "false_positive": len(false_items),
        "recall": len(true_items) / len(oracle) if oracle else 0.0,
        "precision": len(true_items) / len(items) if items else 1.0,
        "true_items": sorted(true_items),
        "false_items": sorted(false_items),
    }


def bucket_recall(items: set[str], oracle: set[str], buckets: dict[str, str]) -> dict[str, float]:
    by_bucket: dict[str, set[str]] = defaultdict(set)
    for key in oracle:
        by_bucket[buckets.get(key, "unbucketed")].add(key)
    return {
        bucket: len(items & bucket_items) / len(bucket_items)
        for bucket, bucket_items in sorted(by_bucket.items())
    }


def summarize(raw: dict[str, Any], oracle: set[str], buckets: dict[str, str]) -> dict[str, Any]:
    runs = [normalize_run(run) for run in raw["runs"]]
    summaries: list[dict[str, Any]] = []
    for run in runs:
        metrics = score_set(run["items"], oracle)
        summaries.append({
            "run_id": run["run_id"],
            "seed": run["seed"],
            "group": run["group"],
            "confidence": run["confidence"],
            "completion": run["completion"],
            "found": metrics["found"],
            "true_positive": metrics["true_positive"],
            "false_positive": metrics["false_positive"],
            "recall": metrics["recall"],
            "precision": metrics["precision"],
            "false_stop": run["completion"] and metrics["recall"] < THETA,
            "bucket_recall": bucket_recall(run["items"], oracle, buckets),
        })

    by_seed: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_run_id = {run["run_id"]: run for run in runs}
    for run in runs:
        by_seed[run["seed"]].append(run)

    seed_summaries: list[dict[str, Any]] = []
    gamma = max(0.05, 3 / len(oracle)) if oracle else 0.05
    for seed, seed_runs in sorted(by_seed.items()):
        g3_runs = [run for run in seed_runs if run["group"] == "G3"]
        g6_runs = [run for run in seed_runs if run["group"] == "G6"]
        if len(g3_runs) < 3:
            continue

        pairwise = [
            jaccard(left["items"], right["items"])
            for left, right in combinations(g3_runs, 2)
        ]
        item_counts = Counter(item for run in g3_runs for item in run["items"])
        union_items = set(item_counts)
        consensus_items = {item for item, count in item_counts.items() if count >= 2}
        singleton_count = sum(1 for count in item_counts.values() if count == 1)
        consensus_metrics = score_set(consensus_items, oracle)
        union_metrics = score_set(union_items, oracle)
        holdout_items = set()
        if g6_runs:
            holdout_items = set().union(*(run["items"] for run in g6_runs))
        holdout_metrics = score_set(holdout_items, oracle) if holdout_items else None
        holdout_gain = None
        if holdout_items:
            holdout_gain = len((holdout_items - consensus_items) & oracle) / len(oracle)

        mean_confidence = mean([
            run["confidence"] for run in g3_runs if run["confidence"] is not None
        ])
        mean_overlap = mean(pairwise)
        false_convergence = None
        if holdout_gain is not None and mean_confidence is not None and mean_overlap is not None:
            false_convergence = (
                consensus_metrics["recall"] < THETA
                and mean_confidence >= CONFIDENCE_THRESHOLD
                and mean_overlap >= TAU
                and holdout_gain >= gamma
            )

        seed_summaries.append({
            "seed": seed,
            "g3_run_ids": [run["run_id"] for run in g3_runs],
            "mean_confidence": mean_confidence,
            "pairwise_jaccard": pairwise,
            "mean_pairwise_jaccard": mean_overlap,
            "singleton_ratio": singleton_count / len(union_items) if union_items else 0.0,
            "consensus": {
                key: value for key, value in consensus_metrics.items()
                if key not in {"true_items", "false_items"}
            },
            "union": {
                key: value for key, value in union_metrics.items()
                if key not in {"true_items", "false_items"}
            },
            "holdout": None if holdout_metrics is None else {
                key: value for key, value in holdout_metrics.items()
                if key not in {"true_items", "false_items"}
            },
            "holdout_gain": holdout_gain,
            "false_convergence_consensus": false_convergence,
            "consensus_bucket_recall": bucket_recall(consensus_items, oracle, buckets),
            "union_bucket_recall": bucket_recall(union_items, oracle, buckets),
            "holdout_bucket_recall": None if not holdout_items else bucket_recall(holdout_items, oracle, buckets),
            "consensus_missing_true_items": sorted(oracle - consensus_items),
            "holdout_new_true_items": sorted((holdout_items - consensus_items) & oracle),
        })

    return {
        "task_id": raw.get("task_id"),
        "oracle_size": len(oracle),
        "thresholds": {
            "theta": THETA,
            "tau": TAU,
            "confidence": CONFIDENCE_THRESHOLD,
            "gamma": gamma,
        },
        "run_summaries": summaries,
        "seed_summaries": seed_summaries,
        "raw_run_ids": sorted(by_run_id),
    }


def fmt(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines: list[str] = []
    lines.append(f"# {summary['task_id']} Expanded Score Summary")
    lines.append("")
    lines.append(f"Oracle size: {summary['oracle_size']}")
    lines.append("")
    lines.append("## Individual Runs")
    lines.append("")
    lines.append("| run_id | group | seed | confidence | found | tp | fp | recall | precision | false_stop |")
    lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |")
    for run in summary["run_summaries"]:
        lines.append(
            "| {run_id} | {group} | {seed} | {confidence} | {found} | {tp} | {fp} | {recall} | {precision} | {false_stop} |".format(
                run_id=run["run_id"],
                group=run["group"],
                seed=run["seed"],
                confidence=fmt(run["confidence"]),
                found=run["found"],
                tp=run["true_positive"],
                fp=run["false_positive"],
                recall=fmt(run["recall"]),
                precision=fmt(run["precision"]),
                false_stop=str(run["false_stop"]).lower(),
            )
        )
    lines.append("")
    lines.append("## G3 Seed Aggregates")
    lines.append("")
    lines.append("| seed | mean_conf | mean_jaccard | singleton_ratio | consensus_recall | union_recall | holdout_recall | holdout_gain | false_convergence |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |")
    for seed in summary["seed_summaries"]:
        holdout = seed["holdout"]
        lines.append(
            "| {seed_id} | {conf} | {jac} | {singletons} | {consensus} | {union} | {holdout_recall} | {gain} | {fc} |".format(
                seed_id=seed["seed"],
                conf=fmt(seed["mean_confidence"]),
                jac=fmt(seed["mean_pairwise_jaccard"]),
                singletons=fmt(seed["singleton_ratio"]),
                consensus=fmt(seed["consensus"]["recall"]),
                union=fmt(seed["union"]["recall"]),
                holdout_recall="null" if holdout is None else fmt(holdout["recall"]),
                gain=fmt(seed["holdout_gain"]),
                fc=fmt(seed["false_convergence_consensus"]).lower(),
            )
        )
    lines.append("")
    lines.append("## Bucket Recall By Seed")
    for seed in summary["seed_summaries"]:
        lines.append("")
        lines.append(f"### {seed['seed']}")
        lines.append("")
        lines.append("| bucket | consensus | union | holdout |")
        lines.append("| --- | ---: | ---: | ---: |")
        buckets = sorted(seed["consensus_bucket_recall"])
        for bucket in buckets:
            holdout_bucket = seed["holdout_bucket_recall"]
            lines.append(
                "| {bucket} | {consensus} | {union} | {holdout} |".format(
                    bucket=bucket,
                    consensus=fmt(seed["consensus_bucket_recall"][bucket]),
                    union=fmt(seed["union_bucket_recall"][bucket]),
                    holdout="null" if holdout_bucket is None else fmt(holdout_bucket[bucket]),
                )
            )
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oracle", required=True, type=Path)
    parser.add_argument("--runs", required=True, type=Path)
    parser.add_argument("--out-json", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    args = parser.parse_args()

    oracle, buckets = load_oracle(args.oracle)
    raw = json.loads(args.runs.read_text(encoding="utf-8"))
    summary = summarize(raw, oracle, buckets)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(summary, args.out_md)


if __name__ == "__main__":
    main()
