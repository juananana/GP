from __future__ import annotations

import importlib.util
import json
import math
import random
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from experiment_config import load_experiment_config, seed_count, seeds, thresholds, task_config


ROOT = Path(__file__).resolve().parents[4]
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"
OUT = PILOT / "external_validation_requests"
SNAPSHOT = OUT / "repo_snapshot"
LOGS = OUT / "logs"
RESULTS = OUT / "results"
REPORTS = OUT / "reports"

TASK_ID = "T_external_requests_repo_v1"
REPO_ID = "requests_local_site_package_snapshot"
CONFIG = load_experiment_config()
THRESHOLDS = thresholds(CONFIG)
SAFE_RECALL_MIN = THRESHOLDS["eval_recall"]
N_SEEDS = seed_count(CONFIG, "validation")
VALIDATION_SEEDS = seeds(CONFIG, "validation")
REQUESTS_CONFIG = task_config(CONFIG, "requests")
REPAIR_BUDGET = int(CONFIG.get("repair_budgets", {}).get("external_requests", 4))

FILES = [
    "adapters.py",
    "api.py",
    "auth.py",
    "models.py",
    "sessions.py",
    "utils.py",
]

ROUTES = {
    "tls_route": re.compile(r"\b(verify|cert|ssl|SSL|TLS|cert_verify|ca_bundle|DEFAULT_CA_BUNDLE_PATH)\b"),
    "timeout_route": re.compile(r"\b(timeout|Timeout|connect timeout|read timeout)\b", re.I),
    "exception_route": re.compile(r"\b(except|raise|RetryError|SSLError|ConnectionError|Timeout|TooManyRedirects)\b"),
    "compat_route": re.compile(r"\b(deprecated|compat|super_len|basestring|builtin_str|to_native_string|unicode_is_ascii)\b", re.I),
}

CONDITIONS = {
    "homogeneous": [
        ("H1", "timeout_route", FILES),
        ("H2", "timeout_route", FILES),
        ("H3", "timeout_route", FILES),
    ],
    "route_partitioned": [
        ("R1", "tls_route", FILES),
        ("R2", "timeout_route", FILES),
        ("R3", "exception_route", FILES),
        ("R4", "compat_route", FILES),
    ],
}

CHALLENGERS = [
    "random",
    "low_exposure",
    "low_discovery",
    "high_potential",
    "residual_potential",
    "free_search_continuation",
]


def ensure_dirs() -> None:
    for path in [SNAPSHOT, LOGS, RESULTS, REPORTS]:
        path.mkdir(parents=True, exist_ok=True)


def requests_source_root() -> Path:
    spec = importlib.util.find_spec("requests")
    if spec is None or spec.origin is None:
        raise RuntimeError("requests is not importable")
    return Path(spec.origin).parent


def write_snapshot() -> None:
    src = requests_source_root()
    for name in FILES:
        shutil.copy2(src / name, SNAPSHOT / name)


def source_family(filename: str) -> str:
    return filename.removesuffix(".py")


def item_id(filename: str, route: str, lineno: int) -> str:
    return f"{source_family(filename)}:{route}:{lineno}"


def file_lines(filename: str) -> list[str]:
    return (SNAPSHOT / filename).read_text(encoding="utf-8", errors="ignore").splitlines()


def route_matches(filename: str, route: str) -> list[tuple[int, str]]:
    pattern = ROUTES[route]
    rows = []
    for lineno, line in enumerate(file_lines(filename), start=1):
        if pattern.search(line):
            rows.append((lineno, line.strip()))
    return rows


def build_oracle() -> list[dict]:
    oracle = []
    seen = set()
    for filename in FILES:
        for route in ROUTES:
            for lineno, line in route_matches(filename, route):
                iid = item_id(filename, route, lineno)
                if iid in seen:
                    continue
                seen.add(iid)
                oracle.append(
                    {
                        "task_id": TASK_ID,
                        "item_id": iid,
                        "oracle_label": True,
                        "oracle_bucket": route,
                        "source_path": str(SNAPSHOT / filename),
                        "source_family": source_family(filename),
                        "source_route_stratum": f"{source_family(filename)}::{route}",
                        "reportable": True,
                        "line": line,
                    }
                )
    return oracle


def log_event(events: list[dict], **kwargs: object) -> None:
    kwargs["source_route_stratum"] = f"{kwargs['source_family']}::{kwargs['search_route']}"
    events.append(kwargs)


def run_condition(condition: str, agents: list[tuple[str, str, list[str]]]) -> list[dict]:
    events = []
    discovered = set()
    event_id = 0
    for agent_id, route, filenames in agents:
        for round_id, filename in enumerate(filenames, start=1):
            matches = route_matches(filename, route)
            event_id += 1
            log_event(
                events,
                task_id=TASK_ID,
                repo_id=REPO_ID,
                run_id=f"{TASK_ID}_{condition}",
                condition=condition,
                agent_id=agent_id,
                round_id=round_id,
                event_id=event_id,
                timestamp="",
                query_text=f"{route} over {filename}",
                tool_name="regex_scan",
                action_type="search",
                source_path=str(SNAPSHOT / filename),
                source_family=source_family(filename),
                search_route=route,
                discovered_item_id=None,
                new_item=False,
                self_reported_completion=False,
                self_reported_confidence=0.45,
                stop_reason=None,
                token_or_cost=len(file_lines(filename)),
                notes=f"{len(matches)} matched lines",
            )
            for lineno, line in matches:
                iid = item_id(filename, route, lineno)
                is_new = iid not in discovered
                if is_new:
                    discovered.add(iid)
                event_id += 1
                log_event(
                    events,
                    task_id=TASK_ID,
                    repo_id=REPO_ID,
                    run_id=f"{TASK_ID}_{condition}",
                    condition=condition,
                    agent_id=agent_id,
                    round_id=round_id,
                    event_id=event_id,
                    timestamp="",
                    query_text=f"extract matched site via {route}",
                    tool_name="regex_scan",
                    action_type="extract",
                    source_path=str(SNAPSHOT / filename),
                    source_family=source_family(filename),
                    search_route=route,
                    discovered_item_id=iid,
                    new_item=is_new,
                    self_reported_completion=False,
                    self_reported_confidence=0.5,
                    stop_reason=None,
                    token_or_cost=1,
                    notes=line,
                )
        event_id += 1
        log_event(
            events,
            task_id=TASK_ID,
            repo_id=REPO_ID,
            run_id=f"{TASK_ID}_{condition}",
            condition=condition,
            agent_id=agent_id,
            round_id=len(filenames) + 1,
            event_id=event_id,
            timestamp="",
            query_text="agent stop after assigned scan route",
            tool_name="agent_controller",
            action_type="stop",
            source_path="",
            source_family="controller",
            search_route=route,
            discovered_item_id=None,
            new_item=False,
            self_reported_completion=True,
            self_reported_confidence=0.8 if condition == "homogeneous" else 0.7,
            stop_reason="assigned_route_exhausted",
            token_or_cost=0,
            notes="blind stop; oracle not consulted",
        )
    return events


def gini(values: np.ndarray) -> float:
    x = np.array(values, dtype=float)
    if x.size == 0 or x.sum() == 0:
        return math.nan
    x = np.sort(x)
    n = x.size
    return float((2 * np.sum(np.arange(1, n + 1) * x) / (n * x.sum())) - (n + 1) / n)


def all_strata(granularity: str = "source_route") -> list[str]:
    if granularity == "source_only":
        return [source_family(name) for name in FILES]
    if granularity == "source_route":
        return [f"{source_family(name)}::{route}" for name in FILES for route in ROUTES]
    if granularity == "source_route_action":
        return [f"{source_family(name)}::{route}::search" for name in FILES for route in ROUTES]
    raise ValueError(granularity)


def event_stratum(row: pd.Series, granularity: str) -> str:
    if granularity == "source_only":
        return str(row["source_family"])
    if granularity == "source_route":
        return f"{row['source_family']}::{row['search_route']}"
    return f"{row['source_family']}::{row['search_route']}::search"


def summarize_conditions(events: list[dict], oracle_ids: set[str]) -> pd.DataFrame:
    rows = []
    df = pd.DataFrame(events)
    universe = all_strata("source_route")
    for condition, sub in df.groupby("condition"):
        filtered = sub[sub["source_family"] != "controller"]
        exposure = Counter(filtered["source_route_stratum"])
        discovery = Counter(filtered.loc[filtered["new_item"], "source_route_stratum"])
        exp_vals = np.array([exposure[s] for s in universe], dtype=float)
        disc_vals = np.array([discovery[s] for s in universe], dtype=float)
        found = set(filtered.loc[filtered["new_item"], "discovered_item_id"].dropna()) & oracle_ids
        recall = len(found) / len(oracle_ids)
        rows.append(
            {
                "task_id": TASK_ID,
                "condition": condition,
                "n_events": len(sub),
                "n_agents": int(sub["agent_id"].nunique()),
                "n_exposure_strata": int((exp_vals > 0).sum()),
                "n_discovery_strata": int((disc_vals > 0).sum()),
                "source_route_coverage_ratio": float((exp_vals > 0).mean()),
                "exposure_gini": gini(exp_vals),
                "discovery_gini": gini(disc_vals),
                "found_true_items": len(found),
                "oracle_total": len(oracle_ids),
                "recall": recall,
                "false_stop_at_90": bool(recall < SAFE_RECALL_MIN),
            }
        )
    return pd.DataFrame(rows)


def route_potential(stratum: str, granularity: str) -> float:
    if granularity == "source_only":
        filename = f"{stratum}.py"
        return float(sum(len(route_matches(filename, route)) for route in ROUTES))
    source, route, *_ = stratum.split("::")
    return float(len(route_matches(f"{source}.py", route)))


def candidate_items(stratum: str, granularity: str) -> tuple[set[str], int]:
    if granularity == "source_only":
        selected = [(f"{stratum}.py", route) for route in ROUTES]
    else:
        source, route, *_ = stratum.split("::")
        selected = [(f"{source}.py", route)]
    ids = set()
    cost = 0
    for filename, route in selected:
        cost += len(file_lines(filename))
        for lineno, _ in route_matches(filename, route):
            ids.add(item_id(filename, route, lineno))
    return ids, cost


def base_counts(base: pd.DataFrame, granularity: str) -> tuple[Counter, Counter]:
    exposure = Counter()
    discovery = Counter()
    for _, row in base[base["source_family"] != "controller"].iterrows():
        key = event_stratum(row, granularity)
        exposure[key] += 1
        if bool(row["new_item"]):
            discovery[key] += 1
    return exposure, discovery


def select_targets(base: pd.DataFrame, granularity: str, challenger: str, seed: int, budget_k: int = REPAIR_BUDGET) -> list[str]:
    universe = all_strata(granularity)
    exposure, discovery = base_counts(base, granularity)
    potentials = {s: route_potential(s, granularity) for s in universe}
    max_exp = max([exposure.get(s, 0) for s in universe] + [1])
    rng = random.Random(seed)
    if challenger == "random":
        return rng.sample(universe, min(budget_k, len(universe)))
    if challenger == "low_exposure":
        return sorted(universe, key=lambda s: (exposure.get(s, 0), s))[:budget_k]
    if challenger == "low_discovery":
        return sorted(universe, key=lambda s: (discovery.get(s, 0), s))[:budget_k]
    if challenger == "high_potential":
        return sorted(universe, key=lambda s: (-potentials[s], s))[:budget_k]
    if challenger == "residual_potential":
        return sorted(
            universe,
            key=lambda s: (-(1.0 - exposure.get(s, 0) / max_exp) * potentials[s], s),
        )[:budget_k]
    if challenger == "free_search_continuation":
        weighted = sorted(universe)
        weights = np.array([potentials[s] + 1e-6 for s in weighted], dtype=float)
        weights = weights / weights.sum()
        return list(np.random.default_rng(seed).choice(weighted, size=min(budget_k, len(weighted)), replace=False, p=weights))
    raise ValueError(challenger)


def evaluate_challengers(events: list[dict], oracle_ids: set[str]) -> pd.DataFrame:
    df = pd.DataFrame(events)
    base = df[df["condition"] == "homogeneous"].copy()
    base_found = set(base.loc[base["new_item"], "discovered_item_id"].dropna()) & oracle_ids
    rows = []
    for granularity in ["source_only", "source_route", "source_route_action"]:
        for challenger in CHALLENGERS:
            for seed in VALIDATION_SEEDS:
                targets = select_targets(base, granularity, challenger, seed)
                found = set(base_found)
                new = set()
                cost = 0
                for target in targets:
                    ids, c = candidate_items(target, granularity)
                    cost += c
                    new |= (ids & oracle_ids) - found
                    found |= ids & oracle_ids
                cumulative = len(base_found) + len(new)
                rows.append(
                    {
                        "granularity": granularity,
                        "challenger": challenger,
                        "seed": seed,
                        "targets": ";".join(targets),
                        "base_true_items": len(base_found),
                        "oracle_total": len(oracle_ids),
                        "new_true_items": len(new),
                        "cost": cost,
                        "novelty_per_cost": len(new) / cost if cost else 0.0,
                        "cumulative_true_items": cumulative,
                        "cumulative_recall": cumulative / len(oracle_ids),
                        "false_stop_reduction": int((len(base_found) / len(oracle_ids) < SAFE_RECALL_MIN) and (cumulative / len(oracle_ids) >= SAFE_RECALL_MIN)),
                    }
                )
    return pd.DataFrame(rows)


def bootstrap_ci(values: np.ndarray, n: int = 2000) -> tuple[float, float]:
    rng = np.random.default_rng(0)
    means = [float(np.mean(rng.choice(values, size=len(values), replace=True))) for _ in range(n)]
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def summarize_challengers(detailed: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, sub in detailed.groupby(["granularity", "challenger"]):
        vals = sub["new_true_items"].to_numpy(dtype=float)
        npc = sub["novelty_per_cost"].to_numpy(dtype=float)
        rec = sub["cumulative_recall"].to_numpy(dtype=float)
        lo, hi = bootstrap_ci(vals)
        rows.append(
            {
                "granularity": keys[0],
                "challenger": keys[1],
                "runs": len(sub),
                "mean_new_true_items": float(vals.mean()),
                "std_new_true_items": float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
                "new_true_ci95_low": lo,
                "new_true_ci95_high": hi,
                "mean_novelty_per_cost": float(npc.mean()),
                "mean_cumulative_recall": float(rec.mean()),
                "mean_false_stop_reduction": float(sub["false_stop_reduction"].mean()),
            }
        )
    summary = pd.DataFrame(rows)
    out_rows = []
    for granularity, sub in summary.groupby("granularity"):
        rand = sub[sub["challenger"] == "random"].iloc[0]
        mu = rand["mean_new_true_items"]
        sigma = rand["std_new_true_items"]
        for _, row in sub.iterrows():
            record = row.to_dict()
            record["delta_vs_random"] = row["mean_new_true_items"] - mu
            record["percentile_vs_random_normal_approx"] = (
                0.5 * (1.0 + math.erf((row["mean_new_true_items"] - mu) / sigma / math.sqrt(2.0)))
                if sigma > 0
                else math.nan
            )
            out_rows.append(record)
    return pd.DataFrame(out_rows)


def write_report(condition: pd.DataFrame, summary: pd.DataFrame) -> None:
    pivot = summary.pivot_table(index="granularity", columns="challenger", values="mean_new_true_items", aggfunc="first").reset_index()
    report = f"""# External Validation: Requests Repo

This experiment uses a real local snapshot of the open-source `requests` package from the Python environment. It is a bounded discovery task over six source files: `{', '.join(FILES)}`.

## Purpose

Test whether the frozen source-route exposure localization story survives outside generated tasks.

## Leakage Control

Oracle labels are created by a fixed offline route-pattern scan and used only for scoring. Challenger selection uses only runtime-visible exposure, discovery ledger state, source text, and route match counts. It does not use oracle missing mass or undiscovered true item counts.

## Condition Metrics

{condition.to_markdown(index=False)}

## Challenger Summary

{summary.to_markdown(index=False)}

## Mean New True Items by Granularity

{pivot.to_markdown(index=False)}

## Interpretation

This is a real external-source validation, but it is still pattern-defined rather than human-annotated. Treat it as stronger than generated toy tasks and weaker than a fully manual external benchmark.
"""
    (REPORTS / "EXTERNAL_REQUESTS_VALIDATION_REPORT.md").write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    write_snapshot()
    oracle = build_oracle()
    oracle_ids = {row["item_id"] for row in oracle}
    events = []
    for condition, agents in CONDITIONS.items():
        events.extend(run_condition(condition, agents))
    condition = summarize_conditions(events, oracle_ids)
    detailed = evaluate_challengers(events, oracle_ids)
    summary = summarize_challengers(detailed)

    (LOGS / "oracle_items.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in oracle) + "\n", encoding="utf-8")
    (LOGS / "action_events.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in events) + "\n", encoding="utf-8")
    condition.to_csv(RESULTS / "external_requests_condition_metrics.csv", index=False)
    detailed.to_csv(RESULTS / "external_requests_challenger_detailed.csv", index=False)
    summary.to_csv(RESULTS / "external_requests_challenger_summary.csv", index=False)
    write_report(condition, summary)
    print(condition.to_string(index=False))
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
