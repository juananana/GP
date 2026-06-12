#!/usr/bin/env python3
"""Build and evaluate completion_certificate_v2 diagnostic states.

This script creates a new v2 pipeline without modifying v1 artifacts. The data
collector is a deterministic offline scanner over task source files. It is not
an online LLM blind run. Oracles are used only after candidate generation for
offline labels, residual missing mass, model training/evaluation, and audit
policy scoring.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import beta
from sklearn.calibration import calibration_curve
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from score_itemsets import THETA, canonical, load_oracle, score_set


BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "v2_outputs"
LOG_DIR = OUT / "run_logs"
STATE_DIR = OUT / "state_logs"
FEATURE_DIR = OUT / "features"
MODEL_DIR = OUT / "models"
FIG_DIR = OUT / "figures"
REPORT_DIR = OUT / "reports"


SAFE_TARGET_RECALL = 0.95
ALLOWED_FCR = 0.05
CALIBRATION_CONFIDENCE = 0.95


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    repository: str
    task_family: str
    task_root: str
    oracle_path: str
    source_commit: str | None
    include_globs: tuple[str, ...]
    base_keywords: tuple[str, ...]
    prompt_variants: tuple[tuple[str, tuple[str, ...]], ...]
    partition_groups: tuple[tuple[str, ...], ...]


TASKS = [
    TaskSpec(
        task_id="T2_policy_docs_v2_offline",
        repository="local_policy_docs",
        task_family="synthetic_policy_docs",
        task_root="T2_policy_docs",
        oracle_path="results/T2_policy_docs_oracle.json",
        source_commit=None,
        include_globs=("docs/**/*.md",),
        base_keywords=("acmepay", "v1", "charge", "refund", "fallback", "replay", "production_active", "scheduled_replay"),
        prompt_variants=(
            ("direct_acmepay", ("acmepay", "v1", "adapter", "legacy")),
            ("flow_state", ("production_active", "scheduled_replay", "charge", "refund", "fallback_queue", "replay")),
            ("registry_alias", ("registry", "service", "alias", "adapter")),
            ("negative_filter", ("sandbox", "canary", "manual", "hold", "v2")),
            ("broad_policy", ("case", "state", "flow", "service")),
        ),
        partition_groups=(("docs/cases",), ("docs/registry",), ("docs",)),
    ),
    TaskSpec(
        task_id="T4_click_deprecation_v2_offline",
        repository="click",
        task_family="real_repo_click_deprecation",
        task_root="T4_real_repo_click",
        oracle_path="results/T4_real_repo_click_deprecation_oracle.json",
        source_commit="8a1b1a33d739be05b7e91251e3c0dde77c5e152f",
        include_globs=("repo/**/*.py", "repo/**/*.md", "repo/**/*.rst"),
        base_keywords=("deprecat", "warning", "warn", "hidden", "help", "Command", "Option", "Argument", "parser"),
        prompt_variants=(
            ("implementation", ("deprecated", "deprecation", "warn", "ParameterSource", "Command", "Option", "Argument")),
            ("tests", ("deprecated", "pytest.warns", "CliRunner", "warning", "help")),
            ("docs_changelog", ("deprecated", "DeprecationWarning", "help", "command", "changelog")),
            ("broad_api", ("hidden", "help", "parser", "format", "suffix", "invalid")),
            ("narrow_deprecated", ("deprecated", "deprecation")),
        ),
        partition_groups=(("repo/src",), ("repo/tests",), ("repo/docs", "repo/CHANGES.md")),
    ),
    TaskSpec(
        task_id="T5_requests_tls_v2_offline",
        repository="requests",
        task_family="real_repo_requests_tls",
        task_root="T5_real_repo_requests_tls",
        oracle_path="results/T5_real_repo_requests_tls_oracle.json",
        source_commit="1190afd14fca74292946d62c4c8169880a47ff67",
        include_globs=("repo/**/*.py", "repo/**/*.md", "repo/**/*.rst"),
        base_keywords=("ssl", "tls", "cert", "certificate", "verify", "ca bundle", "certifi", "SSL", "TLS"),
        prompt_variants=(
            ("verify_behavior", ("verify", "SSL", "TLS", "cert", "certificate")),
            ("ca_bundle", ("certifi", "CA_BUNDLE", "ca bundle", "DEFAULT_CA_BUNDLE_PATH", "extract_zipped_paths")),
            ("client_cert", ("cert", "key", "client certificate", "cert_verify")),
            ("tests_docs", ("ssl", "cert", "verify", "pytest", "docs")),
            ("broad_tls", ("ssl", "tls", "certificate", "CA", "HTTPS")),
        ),
        partition_groups=(("repo/src",), ("repo/tests",), ("repo/docs", "repo/README.md")),
    ),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    for path in (LOG_DIR, STATE_DIR, FEATURE_DIR, MODEL_DIR, FIG_DIR, REPORT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def iter_task_files(task: TaskSpec) -> list[Path]:
    root = BASE / task.task_root
    files: set[Path] = set()
    for glob in task.include_globs:
        files.update(path for path in root.glob(glob) if path.is_file())
    skip_parts = {".git", "__pycache__", ".venv", "node_modules"}
    return sorted(path for path in files if not any(part in skip_parts for part in path.parts))


def rel_to_task(path: Path, task: TaskSpec) -> str:
    return path.relative_to(BASE / task.task_root).as_posix()


def token_estimate(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


def line_region(line_no: int, window: int = 20) -> str:
    start = max(1, ((line_no - 1) // window) * window + 1)
    end = start + window - 1
    return f"L{start}-L{end}"


def contains_any(line: str, keywords: Iterable[str]) -> bool:
    lower = line.lower()
    return any(keyword.lower() in lower for keyword in keywords)


def score_line(line: str, keywords: Iterable[str]) -> int:
    lower = line.lower()
    return sum(lower.count(keyword.lower()) for keyword in keywords)


def source_id(item: str) -> str:
    if "::" in item:
        return item.split("::", 1)[0]
    return item.rsplit(":", 1)[0].replace("\\", "/")


def canonical_from_rel(rel_path: str, line_no: int) -> str:
    return canonical(rel_path, line_no)


def path_matches_partition(rel_path: str, prefixes: tuple[str, ...]) -> bool:
    normalized = rel_path.replace("\\", "/")
    return any(normalized == prefix or normalized.startswith(prefix.rstrip("/") + "/") for prefix in prefixes)


def select_files(task: TaskSpec, files: list[Path], search_strategy: str, agent_index: int, rng: random.Random) -> list[Path]:
    if search_strategy == "source_partitioned":
        partitions = task.partition_groups
        prefixes = partitions[(agent_index - 1) % len(partitions)]
        selected = [path for path in files if path_matches_partition(rel_to_task(path, task), prefixes)]
        return selected or files
    shuffled = files[:]
    rng.shuffle(shuffled)
    return shuffled


def confidence_from_hits(total_hits: int, budget_lines: int, prompt_variant: str, search_strategy: str) -> float:
    density = total_hits / max(1, budget_lines)
    base = 0.48 + 0.38 * min(1.0, density * 18)
    if prompt_variant in {"broad_policy", "broad_api", "broad_tls"}:
        base += 0.04
    if search_strategy == "source_partitioned":
        base -= 0.03
    return round(max(0.05, min(0.98, base)), 3)


def scan_agent_run(
    *,
    task: TaskSpec,
    seed: int,
    agent_index: int,
    agent_count: int,
    prompt_variant: str,
    model: str,
    search_strategy: str,
    budget_level: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    stable_seed = int(hashlib.sha256(
        f"{task.task_id}:{seed}:{agent_index}:{agent_count}:{prompt_variant}:{model}:{search_strategy}:{budget_level}".encode("utf-8")
    ).hexdigest()[:12], 16)
    rng = random.Random(stable_seed)
    files = iter_task_files(task)
    selected_files = select_files(task, files, search_strategy, agent_index, rng)
    variant_keywords = dict(task.prompt_variants)[prompt_variant]
    keywords = tuple(dict.fromkeys(task.base_keywords + variant_keywords))
    budget_by_level = {"low": 220, "medium": 700, "high": 1800}
    if budget_level == "high":
        budget_by_level["high"] = 8000
    budget_lines = budget_by_level[budget_level]
    if model.endswith("small"):
        budget_lines = int(budget_lines * 0.82)
    elif model.endswith("large"):
        budget_lines = int(budget_lines * 1.18)

    run_id = (
        f"{task.task_id}_seed{seed:02d}_k{agent_count}_agent{agent_index}_"
        f"{prompt_variant}_{search_strategy}_{budget_level}_{model}"
    )
    started = time.perf_counter()
    logs: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    lines_scanned = 0
    total_hits = 0
    round_id = 0

    for path in selected_files:
        if lines_scanned >= budget_lines:
            break
        rel_path = rel_to_task(path, task)
        text = read_text(path)
        file_lines = text.splitlines()
        round_id += 1
        action = f"{search_strategy}:{prompt_variant}:{rel_path}"
        file_token_input = token_estimate(text[:12000]) + token_estimate(" ".join(keywords))
        file_hits = 0
        candidate_line_numbers: set[int] = set()
        for line_no, line in enumerate(file_lines, start=1):
            if lines_scanned >= budget_lines:
                break
            lines_scanned += 1
            if not contains_any(line, keywords):
                continue
            score = score_line(line, keywords)
            if score <= 0:
                continue
            include_prob = min(0.98, 0.42 + 0.14 * score)
            if budget_level == "high":
                include_prob += 0.08
            if budget_level == "low":
                include_prob -= 0.10
            if model.endswith("small"):
                include_prob -= 0.06
            if model.endswith("large"):
                include_prob += 0.04
            if rng.random() > max(0.05, min(0.99, include_prob)):
                continue
            if task.task_family == "synthetic_policy_docs" and "/cases/" in rel_path:
                case_id = Path(rel_path).stem
                candidate = f"{case_id}::{case_id}"
                candidate_line_numbers.add(line_no)
                total_hits += 1
                file_hits += 1
                if candidate not in seen:
                    seen.add(candidate)
                    items.append({"source_id": case_id, "item_id": case_id})
            else:
                radius = 0
                if budget_level == "medium":
                    radius = 1
                elif budget_level == "high":
                    radius = 4 if model.endswith("large") else 3
                for candidate_line in range(max(1, line_no - radius), min(len(file_lines), line_no + radius) + 1):
                    candidate = canonical_from_rel(rel_path, candidate_line)
                    candidate_line_numbers.add(candidate_line)
                    total_hits += 1
                    file_hits += 1
                    if candidate not in seen:
                        seen.add(candidate)
                        items.append({"file_path": rel_path, "line": candidate_line})
        for candidate_line in sorted(candidate_line_numbers):
            candidate = f"{Path(rel_path).stem}::{Path(rel_path).stem}" if task.task_family == "synthetic_policy_docs" and "/cases/" in rel_path else canonical_from_rel(rel_path, candidate_line)
            logs.append({
                "run_id": run_id,
                "repository": task.repository,
                "task_family": task.task_family,
                "seed": seed,
                "agent_id": f"agent{agent_index}",
                "model": model,
                "prompt_variant": prompt_variant,
                "round_id": round_id,
                "query_or_action": action,
                "source_file": rel_path,
                "source_region": line_region(candidate_line),
                "candidate_item": candidate,
                "first_seen_round": round_id,
                "support_count": 1,
                "confidence": None,
                "token_input": file_token_input,
                "token_output": token_estimate(file_lines[candidate_line - 1]) if 0 <= candidate_line - 1 < len(file_lines) else 1,
                "tool_calls": 1,
                "wall_clock": None,
                "search_strategy": search_strategy,
                "budget_level": budget_level,
                "collection_mode": "deterministic_offline_scanner",
            })
        if file_hits == 0:
            logs.append({
                "run_id": run_id,
                "repository": task.repository,
                "task_family": task.task_family,
                "seed": seed,
                "agent_id": f"agent{agent_index}",
                "model": model,
                "prompt_variant": prompt_variant,
                "round_id": round_id,
                "query_or_action": action,
                "source_file": rel_path,
                "source_region": "file_scan_no_candidate",
                "candidate_item": None,
                "first_seen_round": None,
                "support_count": 0,
                "confidence": None,
                "token_input": file_token_input,
                "token_output": 1,
                "tool_calls": 1,
                "wall_clock": None,
                "search_strategy": search_strategy,
                "budget_level": budget_level,
                "collection_mode": "deterministic_offline_scanner",
            })

    wall_clock = time.perf_counter() - started
    confidence = confidence_from_hits(total_hits, max(1, lines_scanned), prompt_variant, search_strategy)
    per_log_wall = wall_clock / max(1, len(logs))
    support_counts = Counter(row["candidate_item"] for row in logs if row["candidate_item"])
    first_seen = {}
    for row in logs:
        item = row["candidate_item"]
        if item and item not in first_seen:
            first_seen[item] = row["round_id"]
    for row in logs:
        item = row["candidate_item"]
        row["confidence"] = confidence
        row["wall_clock"] = per_log_wall
        if item:
            row["support_count"] = support_counts[item]
            row["first_seen_round"] = first_seen[item]

    run = {
        "run_id": run_id,
        "repository": task.repository,
        "task_family": task.task_family,
        "seed": seed,
        "agent_id": f"agent{agent_index}",
        "model": model,
        "prompt_variant": prompt_variant,
        "search_strategy": search_strategy,
        "budget_level": budget_level,
        "self_reported_completion": confidence >= 0.8,
        "self_reported_confidence": confidence,
        "items": items,
        "collection_mode": "deterministic_offline_scanner",
        "source_commit": task.source_commit,
        "lines_scanned": lines_scanned,
        "token_input": sum(row["token_input"] for row in logs),
        "token_output": sum(row["token_output"] for row in logs),
        "tool_calls": sum(row["tool_calls"] for row in logs),
        "wall_clock": wall_clock,
    }
    return run, logs


def generate_runs() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    all_runs: list[dict[str, Any]] = []
    all_logs: list[dict[str, Any]] = []
    agent_counts = (1, 2, 3, 5)
    budget_levels = ("low", "medium", "high")
    search_strategies = ("free_search", "source_partitioned")
    models_by_condition = {
        "homogeneous": ("offline-scout-base",) * 5,
        "prompt_diverse": ("offline-scout-base",) * 5,
        "model_heterogeneous": ("offline-scout-small", "offline-scout-base", "offline-scout-large", "offline-scout-base", "offline-scout-large"),
    }
    for task in TASKS:
        variants = [name for name, _ in task.prompt_variants]
        for seed in range(1, 6):
            for agent_count in agent_counts:
                for condition, models in models_by_condition.items():
                    for search_strategy in search_strategies:
                        for budget_level in budget_levels:
                            for agent_index in range(1, agent_count + 1):
                                if condition == "homogeneous":
                                    prompt_variant = variants[0]
                                else:
                                    prompt_variant = variants[(agent_index - 1 + seed) % len(variants)]
                                model = models[(agent_index - 1) % len(models)]
                                run, logs = scan_agent_run(
                                    task=task,
                                    seed=seed,
                                    agent_index=agent_index,
                                    agent_count=agent_count,
                                    prompt_variant=prompt_variant,
                                    model=model,
                                    search_strategy=search_strategy,
                                    budget_level=budget_level,
                                )
                                run["agent_condition"] = condition
                                for row in logs:
                                    row["agent_condition"] = condition
                                all_runs.append(run)
                                all_logs.extend(logs)
    return all_runs, all_logs


def split_name(seed: int) -> str:
    if seed in (1, 2):
        return "train"
    if seed == 3:
        return "calibration"
    return "test"


def parse_item(item: dict[str, Any]) -> str:
    if "source_id" in item and "item_id" in item:
        return f"{item['source_id']}::{item['item_id']}"
    return canonical(item["file_path"], item["line"])


def pairwise_mean_jaccard(sets: list[set[str]]) -> float:
    if len(sets) < 2:
        return 1.0
    values = []
    for left, right in combinations(sets, 2):
        union = left | right
        values.append(len(left & right) / len(union) if union else 1.0)
    return float(np.mean(values)) if values else 1.0


def source_set(items: set[str]) -> set[str]:
    return {source_id(item) for item in items}


def source_coverage(items: set[str], all_sources: set[str]) -> float:
    if not all_sources:
        return 0.0
    return len(source_set(items) & all_sources) / len(all_sources)


def effective_exploration_size(agent_count: int, output_jaccard: float) -> float:
    rho = min(1.0, max(0.0, output_jaccard))
    return agent_count / (1 + (agent_count - 1) * rho)


def chao_unseen(counts: Counter[str]) -> float:
    f1 = sum(1 for value in counts.values() if value == 1)
    f2 = sum(1 for value in counts.values() if value == 2)
    if f1 == 0:
        return 0.0
    if f2 == 0:
        return f1 * (f1 - 1) / 2
    return (f1 * f1) / (2 * f2)


def query_similarity(logs_by_run: dict[str, list[dict[str, Any]]], run_ids: list[str]) -> float:
    query_sets = []
    for run_id in run_ids:
        query_sets.append({row["query_or_action"] for row in logs_by_run.get(run_id, [])})
    return pairwise_mean_jaccard(query_sets)


def search_path_overlap(logs_by_run: dict[str, list[dict[str, Any]]], run_ids: list[str]) -> float:
    path_sets = []
    for run_id in run_ids:
        path_sets.append({row["source_file"] for row in logs_by_run.get(run_id, [])})
    return pairwise_mean_jaccard(path_sets)


def marginal_gains(agent_item_sets: list[set[str]]) -> list[int]:
    seen: set[str] = set()
    gains = []
    for items in agent_item_sets:
        gains.append(len(items - seen))
        seen |= items
    return gains


def novelty_decay(gains: list[int]) -> float:
    if len(gains) < 2 or gains[0] == 0:
        return 0.0
    return 1.0 - (gains[-1] / gains[0])


def per_source_singleton_density(counts: Counter[str]) -> float:
    by_source: dict[str, list[int]] = defaultdict(list)
    for item, count in counts.items():
        by_source[source_id(item)].append(count)
    densities = []
    for values in by_source.values():
        densities.append(sum(1 for value in values if value == 1) / len(values))
    return float(np.mean(densities)) if densities else 0.0


def v1_risk_proxy(row: dict[str, Any]) -> float:
    risk = 0.0
    risk += 0.12 if row["mean_confidence"] < 0.8 else 0.0
    risk += 0.25 * min(1.0, row["singleton_ratio"] / 0.20)
    risk += 0.22 * min(1.0, row["chao_missing_ratio"] / 0.10)
    risk += 0.20 * min(1.0, row["corr_adjusted_chao_missing_ratio"] / 0.15)
    risk += 0.15 * max(0.0, (0.30 - row["source_coverage"]) / 0.30)
    if row["output_jaccard"] >= 0.95:
        risk += 0.12
    return min(1.0, risk)


def build_states(runs: list[dict[str, Any]], logs: list[dict[str, Any]]) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    logs_by_run: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in logs:
        logs_by_run[row["run_id"]].append(row)

    by_task = {task.task_id: task for task in TASKS}
    oracle_by_task = {task.task_id: load_oracle(BASE / task.oracle_path)[0] for task in TASKS}
    sources_by_task = {
        task.task_id: {rel_to_task(path, task) for path in iter_task_files(task)}
        for task in TASKS
    }
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        grouped[(
            run["task_family"],
            run["repository"],
            run["seed"],
            run["agent_condition"],
            run["search_strategy"],
            run["budget_level"],
            run["prompt_variant"] if run["agent_condition"] == "homogeneous" else "mixed_prompts",
            run["model"] if run["agent_condition"] == "homogeneous" else "mixed_models",
            re.sub(r"_agent\d+_", "_agentX_", run["run_id"]),
        )].append(run)

    rows: list[dict[str, Any]] = []
    state_records: list[dict[str, Any]] = []
    for key, group_runs in grouped.items():
        group_runs = sorted(group_runs, key=lambda run: run["agent_id"])
        agent_count = len(group_runs)
        if agent_count not in {1, 2, 3, 5}:
            continue
        sample = group_runs[0]
        task = next(t for t in TASKS if t.repository == sample["repository"] and t.task_family == sample["task_family"])
        oracle = oracle_by_task[task.task_id]
        all_sources = sources_by_task[task.task_id]
        run_ids = [run["run_id"] for run in group_runs]
        agent_item_sets = [{parse_item(item) for item in run["items"]} for run in group_runs]
        union_items = set().union(*agent_item_sets) if agent_item_sets else set()
        counts = Counter(item for items in agent_item_sets for item in items)
        metrics = score_set(union_items, oracle)
        gains = marginal_gains(agent_item_sets)
        incidences = sum(counts.values())
        f1 = sum(1 for value in counts.values() if value == 1)
        f2 = sum(1 for value in counts.values() if value == 2)
        gt_missing_mass = f1 / incidences if incidences else 1.0
        chao = chao_unseen(counts)
        chao_missing_ratio = chao / (len(union_items) + chao) if len(union_items) + chao else 1.0
        output_j = pairwise_mean_jaccard(agent_item_sets)
        source_overlap = pairwise_mean_jaccard([source_set(items) for items in agent_item_sets])
        eff_size = effective_exploration_size(agent_count, output_j)
        corr_adjusted = min(1.0, chao_missing_ratio * (agent_count / eff_size if eff_size else 1.0))
        state_id = (
            f"{task.task_id}_seed{sample['seed']:02d}_k{agent_count}_"
            f"{sample['agent_condition']}_{sample['search_strategy']}_{sample['budget_level']}_pre"
        )
        row = {
            "state_id": state_id,
            "stage": "pre_audit",
            "task_id": task.task_id,
            "repository": sample["repository"],
            "task_family": sample["task_family"],
            "seed": sample["seed"],
            "split": split_name(sample["seed"]),
            "agent_condition": sample["agent_condition"],
            "search_strategy": sample["search_strategy"],
            "budget_level": sample["budget_level"],
            "nominal_agent_count": agent_count,
            "mean_confidence": float(np.mean([run["self_reported_confidence"] for run in group_runs])),
            "output_jaccard": output_j,
            "source_overlap": source_overlap,
            "source_coverage": source_coverage(union_items, all_sources),
            "query_similarity": query_similarity(logs_by_run, run_ids),
            "search_path_overlap": search_path_overlap(logs_by_run, run_ids),
            "marginal_discovery_gain_last": gains[-1] if gains else 0,
            "marginal_discovery_gain_mean": float(np.mean(gains)) if gains else 0.0,
            "novelty_decay": novelty_decay(gains),
            "singletons_f1": f1,
            "doubletons_f2": f2,
            "singleton_ratio": f1 / len(union_items) if union_items else 1.0,
            "doubleton_ratio": f2 / len(union_items) if union_items else 0.0,
            "per_source_singleton_density": per_source_singleton_density(counts),
            "good_turing_missing_mass": gt_missing_mass,
            "chao_unseen_estimate": chao,
            "chao_missing_ratio": chao_missing_ratio,
            "corr_adjusted_chao_missing_ratio": corr_adjusted,
            "effective_exploration_size": eff_size,
            "found": metrics["found"],
            "true_positive": metrics["true_positive"],
            "false_positive": metrics["false_positive"],
            "recall": metrics["recall"],
            "precision": metrics["precision"],
            "f1_score": 2 * metrics["recall"] * metrics["precision"] / (metrics["recall"] + metrics["precision"]) if metrics["recall"] + metrics["precision"] else 0.0,
            "residual_missing_mass": max(0.0, 1.0 - metrics["recall"]),
            "unsafe": metrics["recall"] < SAFE_TARGET_RECALL,
            "token_input": sum(run["token_input"] for run in group_runs),
            "token_output": sum(run["token_output"] for run in group_runs),
            "tool_calls": sum(run["tool_calls"] for run in group_runs),
            "wall_clock": sum(run["wall_clock"] for run in group_runs),
            "run_ids": json.dumps(run_ids),
            "collection_mode": "deterministic_offline_scanner",
        }
        row["v1_risk_proxy"] = v1_risk_proxy(row)
        rows.append(row)
        state_records.append({
            **row,
            "run_ids": run_ids,
            "union_items": sorted(union_items),
            "true_items": metrics["true_items"],
            "false_items": metrics["false_items"],
            "marginal_discovery_gains": gains,
        })
    return pd.DataFrame(rows), state_records


FEATURE_COLUMNS = [
    "nominal_agent_count",
    "mean_confidence",
    "output_jaccard",
    "source_overlap",
    "source_coverage",
    "query_similarity",
    "search_path_overlap",
    "marginal_discovery_gain_last",
    "marginal_discovery_gain_mean",
    "novelty_decay",
    "singletons_f1",
    "doubletons_f2",
    "singleton_ratio",
    "doubleton_ratio",
    "per_source_singleton_density",
    "good_turing_missing_mass",
    "chao_missing_ratio",
    "corr_adjusted_chao_missing_ratio",
    "effective_exploration_size",
]


def ece_score(y_true: np.ndarray, y_prob: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0.0, 1.0, bins + 1)
    ece = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (y_prob >= low) & (y_prob <= high if high == 1.0 else y_prob < high)
        if not np.any(mask):
            continue
        ece += np.mean(mask) * abs(float(np.mean(y_prob[mask])) - float(np.mean(y_true[mask])))
    return float(ece)


def fcr_upper_bound(false_count: int, certified_count: int, confidence: float = CALIBRATION_CONFIDENCE) -> float | None:
    if certified_count == 0:
        return None
    return float(beta.ppf(confidence, false_count + 1, certified_count - false_count))


def choose_threshold(cal_df: pd.DataFrame, risks: np.ndarray, allowed_fcr: float = ALLOWED_FCR) -> float | None:
    candidates = sorted(set(float(value) for value in risks))
    best = None
    best_coverage = -1
    for threshold in candidates:
        certified = cal_df[risks <= threshold]
        if certified.empty:
            continue
        false_count = int(certified["unsafe"].sum())
        upper = fcr_upper_bound(false_count, len(certified))
        if upper is not None and upper <= allowed_fcr and len(certified) > best_coverage:
            best = threshold
            best_coverage = len(certified)
    return best


def metric_bundle(df: pd.DataFrame, risks: np.ndarray, threshold: float | None) -> dict[str, Any]:
    y = df["unsafe"].astype(int).to_numpy()
    metrics: dict[str, Any] = {
        "n": int(len(df)),
        "unsafe_rate": float(np.mean(y)) if len(y) else None,
    }
    if len(set(y)) == 2:
        metrics["auroc"] = float(roc_auc_score(y, risks))
        metrics["auprc"] = float(average_precision_score(y, risks))
    else:
        metrics["auroc"] = None
        metrics["auprc"] = None
    clipped = np.clip(risks, 0.0, 1.0)
    metrics["brier"] = float(brier_score_loss(y, clipped)) if len(y) else None
    metrics["ece"] = ece_score(y, clipped) if len(y) else None
    if threshold is None:
        metrics.update({
            "safe_threshold": None,
            "certified": 0,
            "false_certifications": 0,
            "false_certification_rate": None,
            "fcr_confidence_upper_bound": None,
            "safe_coverage": 0.0,
            "abstention_rate": 1.0,
        })
        return metrics
    certified_mask = risks <= threshold
    certified = df[certified_mask]
    false_count = int(certified["unsafe"].sum()) if len(certified) else 0
    safe_df = df[~df["unsafe"]]
    metrics.update({
        "safe_threshold": float(threshold),
        "certified": int(len(certified)),
        "false_certifications": false_count,
        "false_certification_rate": false_count / len(certified) if len(certified) else None,
        "fcr_confidence_upper_bound": fcr_upper_bound(false_count, len(certified)) if len(certified) else None,
        "safe_coverage": float(np.sum(certified_mask & (~df["unsafe"].to_numpy())) / len(safe_df)) if len(safe_df) else None,
        "abstention_rate": float(1.0 - np.mean(certified_mask)) if len(df) else None,
    })
    return metrics


def risk_coverage_rows(df: pd.DataFrame, risks: np.ndarray, method: str) -> list[dict[str, Any]]:
    rows = []
    for threshold in np.linspace(0.0, 1.0, 21):
        certified = df[risks <= threshold]
        false_count = int(certified["unsafe"].sum()) if len(certified) else 0
        rows.append({
            "method": method,
            "risk_threshold": float(threshold),
            "coverage": float(len(certified) / len(df)) if len(df) else 0.0,
            "false_certification_rate": false_count / len(certified) if len(certified) else None,
            "certified": int(len(certified)),
        })
    return rows


def fit_models(df: pd.DataFrame) -> tuple[dict[str, Any], pd.DataFrame]:
    train = df[df["split"] == "train"].copy()
    cal = df[df["split"] == "calibration"].copy()
    test = df[df["split"] == "test"].copy()
    x_train = train[FEATURE_COLUMNS]
    y_train = train["unsafe"].astype(int)
    x_cal = cal[FEATURE_COLUMNS]
    x_test = test[FEATURE_COLUMNS]

    model_specs: dict[str, Any] = {
        "logistic_regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, penalty=None)),
        ]),
        "regularized_logistic_regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, penalty="l2", C=0.5)),
        ]),
        "decision_tree": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", DecisionTreeClassifier(max_depth=4, min_samples_leaf=8, random_state=7)),
        ]),
        "gradient_boosting": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", GradientBoostingClassifier(random_state=7, max_depth=2, n_estimators=80, learning_rate=0.05)),
        ]),
    }

    risk_scores: dict[str, dict[str, np.ndarray]] = {}
    baselines = {
        "v1_handcrafted_rule": "v1_risk_proxy",
        "confidence_only": "mean_confidence",
        "overlap_only": "output_jaccard",
        "no_new_item": "marginal_discovery_gain_last",
        "good_turing_only": "good_turing_missing_mass",
        "chao_only": "chao_missing_ratio",
    }
    for name, column in baselines.items():
        def risk_for(frame: pd.DataFrame, col: str = column, method: str = name) -> np.ndarray:
            values = frame[col].astype(float).to_numpy()
            if method == "confidence_only":
                return np.clip(1.0 - values, 0.0, 1.0)
            if method == "overlap_only":
                return np.clip(1.0 - values, 0.0, 1.0)
            if method == "no_new_item":
                max_value = max(1.0, float(np.nanmax(df[col].to_numpy())))
                return np.clip(values / max_value, 0.0, 1.0)
            return np.clip(values, 0.0, 1.0)

        risk_scores[name] = {
            "calibration": risk_for(cal),
            "test": risk_for(test),
        }

    for name, model in model_specs.items():
        model.fit(x_train, y_train)
        risk_scores[name] = {
            "calibration": model.predict_proba(x_cal)[:, 1],
            "test": model.predict_proba(x_test)[:, 1],
        }

    summary: dict[str, Any] = {
        "target": f"unsafe = recall < {SAFE_TARGET_RECALL}",
        "feature_columns": FEATURE_COLUMNS,
        "splits": {
            "train": int(len(train)),
            "calibration": int(len(cal)),
            "test": int(len(test)),
        },
        "threshold_selection": {
            "split": "calibration",
            "allowed_fcr_upper_bound": ALLOWED_FCR,
            "confidence": CALIBRATION_CONFIDENCE,
        },
        "methods": {},
    }
    curve_rows: list[dict[str, Any]] = []
    for method, scores in risk_scores.items():
        threshold = choose_threshold(cal, scores["calibration"])
        summary["methods"][method] = {
            "calibration": metric_bundle(cal, scores["calibration"], threshold),
            "test": metric_bundle(test, scores["test"], threshold),
        }
        curve_rows.extend(risk_coverage_rows(test, scores["test"], method))
        test[f"risk_{method}"] = scores["test"]
    return summary, pd.DataFrame(curve_rows)


def feature_correlations(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in FEATURE_COLUMNS + ["v1_risk_proxy"]:
        pearson = df[[column, "residual_missing_mass"]].corr(method="pearson").iloc[0, 1]
        spearman = df[[column, "residual_missing_mass"]].corr(method="spearman").iloc[0, 1]
        rows.append({
            "feature": column,
            "pearson_with_residual_missing_mass": None if pd.isna(pearson) else float(pearson),
            "spearman_with_residual_missing_mass": None if pd.isna(spearman) else float(spearman),
        })
    return pd.DataFrame(rows)


def audit_policy_eval(df: pd.DataFrame, states: list[dict[str, Any]]) -> pd.DataFrame:
    state_by_id = {state["state_id"]: state for state in states}
    rows = []
    for _, row in df.iterrows():
        state = state_by_id[row["state_id"]]
        union_items = set(state["union_items"])
        task = next(t for t in TASKS if t.task_id == row["task_id"])
        oracle = load_oracle(BASE / task.oracle_path)[0]
        task_sources = defaultdict(set)
        for item in oracle:
            task_sources[source_id(item)].add(item)
        counts = Counter()
        for item in union_items:
            counts[item] += 1
        singletons = {item for item, count in counts.items() if count == 1}
        rng = random.Random(int(row["seed"]) * 919 + len(row["state_id"]))
        missing = sorted(oracle - union_items)
        random_holdout = set(rng.sample(missing, k=min(len(missing), max(1, len(oracle) // 20)))) if missing else set()
        boundary_sources = sorted(source_set(union_items))
        boundary_holdout = set()
        for src in boundary_sources[: max(1, len(boundary_sources) // 3)]:
            boundary_holdout |= task_sources.get(src, set()) - union_items
        uncovered_sources = [src for src in task_sources if src not in source_set(union_items)]
        partition_holdout = set()
        for src in uncovered_sources[: max(1, len(uncovered_sources) // 4)]:
            partition_holdout |= task_sources[src]

        policies = {
            "no_audit": set(),
            "singleton_audit": singletons & oracle,
            "random_holdout": random_holdout,
            "boundary_focused_holdout": boundary_holdout,
            "source_partitioned_audit": partition_holdout,
            "always_holdout": set(missing),
            "risk_triggered_audit": partition_holdout if row["v1_risk_proxy"] >= 0.60 else set(),
        }
        pre_metrics = score_set(union_items, oracle)
        for policy, additions in policies.items():
            final_items = union_items | additions
            post_metrics = score_set(final_items, oracle)
            recovered = len((final_items - union_items) & oracle)
            introduced_fp = len((final_items - union_items) - oracle)
            token_cost = len(additions) * 18 + (len(singletons) * 6 if policy == "singleton_audit" else 0)
            tool_cost = max(0, math.ceil(len(additions) / 25))
            wall_cost = token_cost / 2500
            rows.append({
                "state_id": row["state_id"],
                "split": row["split"],
                "policy": policy,
                "pre_recall": pre_metrics["recall"],
                "post_recall": post_metrics["recall"],
                "pre_precision": pre_metrics["precision"],
                "post_precision": post_metrics["precision"],
                "recovered_true_positives": recovered,
                "introduced_false_positives": introduced_fp,
                "token_cost": token_cost,
                "tool_calls": tool_cost,
                "wall_clock": wall_cost,
                "cost_per_recovered_true_positive": token_cost / recovered if recovered else None,
                "unnecessary_audit_on_already_safe": bool(pre_metrics["recall"] >= SAFE_TARGET_RECALL and additions),
            })
    return pd.DataFrame(rows)


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})


def plot_outputs(df: pd.DataFrame, corr: pd.DataFrame, curves: pd.DataFrame, model_summary: dict[str, Any]) -> None:
    top = corr.copy()
    top["abs_spearman"] = top["spearman_with_residual_missing_mass"].abs()
    top = top.sort_values("abs_spearman", ascending=False).head(12)
    plt.figure(figsize=(8, 5))
    plt.barh(top["feature"], top["spearman_with_residual_missing_mass"])
    plt.axvline(0, color="black", linewidth=0.8)
    plt.xlabel("Spearman correlation with residual missing mass")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "v2_feature_residual_correlation.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 5))
    for method in ["v1_handcrafted_rule", "regularized_logistic_regression", "gradient_boosting", "chao_only"]:
        subset = curves[curves["method"] == method]
        if subset.empty:
            continue
        plt.plot(subset["coverage"], subset["false_certification_rate"].fillna(0), marker="o", label=method)
    plt.xlabel("Certified coverage on test")
    plt.ylabel("False certification rate")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "v2_risk_coverage_curve.png", dpi=180)
    plt.close()

    gb = model_summary["methods"].get("gradient_boosting", {})
    if gb:
        test = df[df["split"] == "test"]
        # Calibration plot is drawn with v1 proxy as a fallback because learned
        # probabilities are persisted in JSON summary, not attached to all rows.
        y_true = test["unsafe"].astype(int).to_numpy()
        y_prob = np.clip(test["v1_risk_proxy"].to_numpy(), 0.0, 1.0)
        if len(np.unique(y_true)) == 2:
            frac, mean_pred = calibration_curve(y_true, y_prob, n_bins=8, strategy="uniform")
            plt.figure(figsize=(5, 5))
            plt.plot(mean_pred, frac, marker="o", label="v1 proxy")
            plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
            plt.xlabel("Mean predicted risk")
            plt.ylabel("Observed unsafe frequency")
            plt.tight_layout()
            plt.savefig(FIG_DIR / "v2_calibration_curve_v1_proxy.png", dpi=180)
            plt.close()


def write_report(
    *,
    runs: list[dict[str, Any]],
    logs: list[dict[str, Any]],
    df: pd.DataFrame,
    corr: pd.DataFrame,
    model_summary: dict[str, Any],
    audit_df: pd.DataFrame,
) -> None:
    split_table = df.groupby(["split", "repository", "task_family", "seed"]).size().reset_index(name="states")
    best_methods = []
    for method, data in model_summary["methods"].items():
        test = data["test"]
        best_methods.append({
            "method": method,
            "auroc": test["auroc"],
            "auprc": test["auprc"],
            "brier": test["brier"],
            "ece": test["ece"],
            "fcr": test["false_certification_rate"],
            "fcr_upper": test["fcr_confidence_upper_bound"],
            "safe_coverage": test["safe_coverage"],
            "abstention": test["abstention_rate"],
            "threshold": test["safe_threshold"],
        })
    method_df = pd.DataFrame(best_methods).sort_values(["auroc", "auprc"], ascending=False, na_position="last")
    audit_summary = audit_df[audit_df["split"] == "test"].groupby("policy").agg(
        states=("state_id", "count"),
        pre_recall=("pre_recall", "mean"),
        post_recall=("post_recall", "mean"),
        post_precision=("post_precision", "mean"),
        recovered_true_positives=("recovered_true_positives", "sum"),
        introduced_false_positives=("introduced_false_positives", "sum"),
        token_cost=("token_cost", "sum"),
        tool_calls=("tool_calls", "sum"),
        wall_clock=("wall_clock", "sum"),
        unnecessary_audit_rate=("unnecessary_audit_on_already_safe", "mean"),
    ).reset_index()
    audit_summary["cost_per_recovered_true_positive"] = audit_summary.apply(
        lambda row: row["token_cost"] / row["recovered_true_positives"] if row["recovered_true_positives"] else None,
        axis=1,
    )

    lines = [
        "# Completion Certificate v2 Results",
        "",
        f"Generated at: `{utc_now()}`",
        "",
        "## Scope",
        "",
        "This is a deterministic offline diagnostic experiment. It creates new logged states from task source files. It is not a new online LLM blind run. Oracles are used only for offline scoring, residual missing mass, calibration, and audit-policy evaluation.",
        "",
        "## Data",
        "",
        f"- Runs generated: `{len(runs)}`",
        f"- Candidate/action log rows: `{len(logs)}`",
        f"- Pre-audit states: `{len(df)}`",
        f"- Safe states (`recall >= {SAFE_TARGET_RECALL}`): `{int((~df['unsafe']).sum())}`",
        f"- Unsafe states: `{int(df['unsafe'].sum())}`",
        "",
        "## Train/Calibration/Test Split",
        "",
        split_table.to_markdown(index=False),
        "",
        "Split grouping is by `(repository, task_family, seed)`. No derived state from a group crosses splits.",
        "",
        "## Feature Correlation With Residual Missing Mass",
        "",
        corr.sort_values("spearman_with_residual_missing_mass", key=lambda s: s.abs(), ascending=False).head(12).to_markdown(index=False),
        "",
        "## v2 Risk Estimation and Calibration",
        "",
        "SAFE thresholds are selected only on the calibration split using a Clopper-Pearson-style FCR upper bound target. This is an empirical calibration rule, not a distribution-free theoretical guarantee.",
        "",
        method_df.to_markdown(index=False),
        "",
        "## Audit Policy Test-Split Summary",
        "",
        audit_summary.to_markdown(index=False),
        "",
        "## Output Files",
        "",
        "- `run_logs/v2_candidate_logs.csv`",
        "- `run_logs/v2_runs.json`",
        "- `state_logs/v2_states.json`",
        "- `features/v2_state_features.csv`",
        "- `features/v2_feature_correlations.csv`",
        "- `models/v2_model_metrics.json`",
        "- `models/v2_risk_coverage_curve.csv`",
        "- `models/v2_audit_policy_eval.csv`",
        "- `figures/v2_feature_residual_correlation.png`",
        "- `figures/v2_risk_coverage_curve.png`",
        "- `figures/v2_calibration_curve_v1_proxy.png`",
        "",
        "## TODO",
        "",
        "- Run online LLM agents with the same logging schema when API/runtime budget is available.",
        "- Replace deterministic holdout simulations with real post-audit agent traces.",
        "- Run SeekerGym once a local checkout/schema is available.",
        "- Inspect learned-model stability before promoting v2 to the paper's main method.",
    ]
    (REPORT_DIR / "COMPLETION_CERTIFICATE_V2_RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    method_df.to_csv(REPORT_DIR / "v2_test_method_summary.csv", index=False)
    audit_summary.to_csv(REPORT_DIR / "v2_audit_policy_summary.csv", index=False)


def main() -> None:
    global OUT, LOG_DIR, STATE_DIR, FEATURE_DIR, MODEL_DIR, FIG_DIR, REPORT_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    OUT = args.output_dir
    LOG_DIR = OUT / "run_logs"
    STATE_DIR = OUT / "state_logs"
    FEATURE_DIR = OUT / "features"
    MODEL_DIR = OUT / "models"
    FIG_DIR = OUT / "figures"
    REPORT_DIR = OUT / "reports"
    ensure_dirs()

    started = utc_now()
    runs, logs = generate_runs()
    df, state_records = build_states(runs, logs)
    corr = feature_correlations(df)
    model_summary, curves = fit_models(df)
    audit_df = audit_policy_eval(df, state_records)

    (LOG_DIR / "v2_runs.json").write_text(json.dumps(runs, indent=2), encoding="utf-8")
    log_fields = [
        "run_id", "repository", "task_family", "seed", "agent_id", "model",
        "prompt_variant", "round_id", "query_or_action", "source_file",
        "source_region", "candidate_item", "first_seen_round", "support_count",
        "confidence", "token_input", "token_output", "tool_calls", "wall_clock",
        "search_strategy", "budget_level", "agent_condition", "collection_mode",
    ]
    write_csv(LOG_DIR / "v2_candidate_logs.csv", logs, log_fields)
    (STATE_DIR / "v2_states.json").write_text(json.dumps(state_records, indent=2), encoding="utf-8")
    df.to_csv(FEATURE_DIR / "v2_state_features.csv", index=False)
    corr.to_csv(FEATURE_DIR / "v2_feature_correlations.csv", index=False)
    curves.to_csv(MODEL_DIR / "v2_risk_coverage_curve.csv", index=False)
    audit_df.to_csv(MODEL_DIR / "v2_audit_policy_eval.csv", index=False)
    (MODEL_DIR / "v2_model_metrics.json").write_text(json.dumps(model_summary, indent=2), encoding="utf-8")

    split_manifest = {
        "created_at": utc_now(),
        "started_at": started,
        "split_rule": "grouped by (repository, task_family, seed); train=seeds 1-2, calibration=seed 3, test=seeds 4-5",
        "groups": df.groupby(["split", "repository", "task_family", "seed"]).size().reset_index(name="state_count").to_dict(orient="records"),
        "no_oracle_use_in_candidate_generation": True,
        "collection_mode": "deterministic_offline_scanner",
    }
    (OUT / "V2_SPLIT_MANIFEST.json").write_text(json.dumps(split_manifest, indent=2), encoding="utf-8")

    plot_outputs(df, corr, curves, model_summary)
    write_report(runs=runs, logs=logs, df=df, corr=corr, model_summary=model_summary, audit_df=audit_df)
    print(json.dumps({
        "output_dir": str(OUT),
        "runs": len(runs),
        "log_rows": len(logs),
        "states": len(df),
        "splits": model_summary["splits"],
        "report": str(REPORT_DIR / "COMPLETION_CERTIFICATE_V2_RESULTS.md"),
    }, indent=2))


if __name__ == "__main__":
    main()
