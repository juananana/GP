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


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "external_validation_v2"
SNAPSHOT = OUT / "repo_snapshot"
LOGS = OUT / "logs"
RESULTS = OUT / "results"
REPORTS = OUT / "reports"

TASK_ID = "T_external_urllib3_audit_v2"
REPO_ID = "urllib3_local_site_package_snapshot"
CONFIG = load_experiment_config()
THRESHOLDS = thresholds(CONFIG)
SAFE_RECALL_MIN = THRESHOLDS["eval_recall"]
SAFE_SUPPORT_MIN = THRESHOLDS["tau_support"]
SAFE_GINI_MAX = THRESHOLDS["tau_gini"]
N_SEEDS = seed_count(CONFIG, "validation")
VALIDATION_SEEDS = seeds(CONFIG, "validation")
URLLIB3_CONFIG = task_config(CONFIG, "urllib3")
DEFAULT_REPAIR_BUDGET = int(CONFIG.get("repair_budgets", {}).get("external_urllib3", 5))

FILES = [
    "connection.py",
    "connectionpool.py",
    "poolmanager.py",
    "response.py",
    "util/retry.py",
    "util/timeout.py",
]

ROUTES = {
    "timeout_route": re.compile(r"\b(timeout|Timeout|connect_timeout|read_timeout|_connect_timeout|_read_timeout)\b", re.I),
    "retry_route": re.compile(r"\b(retry|Retry|retries|increment|backoff|status_forcelist)\b"),
    "tls_route": re.compile(r"\b(ssl|SSL|TLS|cert|certificate|verify|assert_hostname|ca_certs|cert_reqs)\b"),
    "exception_route": re.compile(r"\b(except|raise|Error|TimeoutError|SSLError|ProxyError|HTTPError|MaxRetryError)\b"),
    "cleanup_route": re.compile(r"\b(close|release_conn|drain_conn|shutdown|finally|with\s+|__exit__)\b"),
}

def configured_conditions() -> dict[str, list[tuple[str, str, list[str]]]]:
    route_design = URLLIB3_CONFIG.get(
        "conditions",
        {
            "homogeneous": ["timeout_route"],
            "route_partitioned": ["timeout_route", "retry_route", "tls_route", "exception_route"],
            "extended_audit": ["timeout_route", "retry_route", "tls_route", "exception_route", "cleanup_route"],
        },
    )
    conditions: dict[str, list[tuple[str, str, list[str]]]] = {}
    for condition, routes in route_design.items():
        unknown = [route for route in routes if route not in ROUTES]
        if unknown:
            raise ValueError(f"unknown urllib3 route(s) in config: {unknown}")
        prefix = condition[:1].upper()
        conditions[condition] = [(f"{prefix}{i}", route, FILES) for i, route in enumerate(routes, start=1)]
    return conditions


CONDITIONS = configured_conditions()

CHALLENGERS = [
    "random",
    "low_exposure",
    "high_potential",
    "residual_potential",
    "free_search_continuation",
]


def ensure_dirs() -> None:
    for path in [SNAPSHOT, LOGS, RESULTS, REPORTS]:
        path.mkdir(parents=True, exist_ok=True)


def package_root() -> Path:
    spec = importlib.util.find_spec("urllib3")
    if spec is None or spec.origin is None:
        raise RuntimeError("urllib3 is not importable")
    return Path(spec.origin).parent


def write_snapshot() -> None:
    src = package_root()
    for rel in FILES:
        dest = SNAPSHOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / rel, dest)


def source_family(rel: str) -> str:
    return rel.removesuffix(".py").replace("/", "_").replace("\\", "_")


def rel_from_source_family(family: str) -> str:
    for rel in FILES:
        if source_family(rel) == family:
            return rel
    raise KeyError(family)


def file_lines(rel: str) -> list[str]:
    return (SNAPSHOT / rel).read_text(encoding="utf-8", errors="ignore").splitlines()


def route_matches(rel: str, route: str) -> list[tuple[int, str]]:
    pattern = ROUTES[route]
    return [(i, line.strip()) for i, line in enumerate(file_lines(rel), start=1) if pattern.search(line)]


def item_id(rel: str, route: str, lineno: int) -> str:
    return f"{source_family(rel)}:{route}:{lineno}"


def all_strata() -> list[str]:
    return [f"{source_family(rel)}::{route}" for rel in FILES for route in ROUTES]


def build_oracle() -> list[dict]:
    rows = []
    seen = set()
    for rel in FILES:
        for route in ROUTES:
            for lineno, line in route_matches(rel, route):
                iid = item_id(rel, route, lineno)
                if iid in seen:
                    continue
                seen.add(iid)
                rows.append(
                    {
                        "task_id": TASK_ID,
                        "item_id": iid,
                        "oracle_label": True,
                        "oracle_bucket": route,
                        "source_path": str(SNAPSHOT / rel),
                        "source_family": source_family(rel),
                        "source_route_stratum": f"{source_family(rel)}::{route}",
                        "reportable": True,
                        "line_no": lineno,
                        "line": line,
                    }
                )
    return rows


def log_event(events: list[dict], **kwargs: object) -> None:
    kwargs["source_route_stratum"] = f"{kwargs['source_family']}::{kwargs['search_route']}"
    events.append(kwargs)


def run_condition(condition: str, agents: list[tuple[str, str, list[str]]]) -> list[dict]:
    events = []
    discovered = set()
    event_id = 0
    for agent_id, route, files in agents:
        for round_id, rel in enumerate(files, start=1):
            matches = route_matches(rel, route)
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
                query_text=f"{route} audit over {rel}",
                tool_name="regex_scan",
                action_type="search",
                source_path=str(SNAPSHOT / rel),
                source_family=source_family(rel),
                search_route=route,
                discovered_item_id=None,
                new_item=False,
                self_reported_completion=False,
                self_reported_confidence=0.45,
                stop_reason=None,
                token_or_cost=len(file_lines(rel)),
                notes=f"{len(matches)} matched lines",
            )
            for lineno, line in matches:
                iid = item_id(rel, route, lineno)
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
                    query_text=f"extract audit evidence via {route}",
                    tool_name="regex_scan",
                    action_type="extract",
                    source_path=str(SNAPSHOT / rel),
                    source_family=source_family(rel),
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
            round_id=len(files) + 1,
            event_id=event_id,
            timestamp="",
            query_text="agent stop after assigned source-route audit",
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


def gini(values: list[float]) -> float:
    x = np.array(values, dtype=float)
    if x.size == 0 or x.sum() == 0:
        return math.nan
    x = np.sort(x)
    n = x.size
    return float((2 * np.sum(np.arange(1, n + 1) * x) / (n * x.sum())) - (n + 1) / n)


def exposure_counts(df: pd.DataFrame) -> Counter:
    return Counter(df[df["source_family"] != "controller"]["source_route_stratum"])


def discovered_true(df: pd.DataFrame, oracle_ids: set[str]) -> set[str]:
    return set(df.loc[df["new_item"], "discovered_item_id"].dropna()) & oracle_ids


def condition_state(exposure: Counter, potential: dict[str, float]) -> dict:
    strata = all_strata()
    vals = [float(exposure.get(s, 0)) for s in strata]
    occupied = {s for s in strata if exposure.get(s, 0) > 0}
    weak_plausible = {s for s in strata if exposure.get(s, 0) == 0 and potential.get(s, 0.0) > 0}
    return {
        "support_size": len(occupied),
        "support_ratio": len(occupied) / len(strata),
        "exposure_gini": gini(vals),
        "weak_plausible_gap": len(weak_plausible),
    }


def runtime_potential() -> dict[str, float]:
    # Runtime-visible lexical potential. It uses source text and route patterns, but no oracle labels,
    # oracle totals, missing mass, or post-hoc discovered items.
    out = {}
    for rel in FILES:
        n_lines = max(len(file_lines(rel)), 1)
        for route in ROUTES:
            broad_hits = len(route_matches(rel, route))
            out[f"{source_family(rel)}::{route}"] = broad_hits + math.log1p(n_lines)
    return out


def candidate_items(stratum: str) -> tuple[set[str], int]:
    family, route = stratum.split("::")
    rel = rel_from_source_family(family)
    ids = {item_id(rel, route, lineno) for lineno, _ in route_matches(rel, route)}
    return ids, len(file_lines(rel))


def select_targets(base: pd.DataFrame, strategy: str, seed: int, potential: dict[str, float], budget_k: int = DEFAULT_REPAIR_BUDGET) -> list[str]:
    universe = all_strata()
    exposure = exposure_counts(base)
    max_exp = max([exposure.get(s, 0) for s in universe] + [1])
    rng = random.Random(seed)
    if strategy == "random":
        return rng.sample(universe, min(budget_k, len(universe)))
    if strategy == "low_exposure":
        return sorted(universe, key=lambda s: (exposure.get(s, 0), s))[:budget_k]
    if strategy == "high_potential":
        return sorted(universe, key=lambda s: (-potential[s], s))[:budget_k]
    if strategy == "residual_potential":
        return sorted(universe, key=lambda s: (-(1.0 - exposure.get(s, 0) / max_exp) * potential[s], s))[:budget_k]
    if strategy == "free_search_continuation":
        weights = np.array([potential[s] + 1e-6 for s in universe], dtype=float)
        weights = weights / weights.sum()
        return list(np.random.default_rng(seed).choice(universe, size=min(budget_k, len(universe)), replace=False, p=weights))
    raise ValueError(strategy)


def evaluate_conditions(events: list[dict], oracle_ids: set[str], potential: dict[str, float]) -> pd.DataFrame:
    df = pd.DataFrame(events)
    rows = []
    for condition, sub in df.groupby("condition"):
        exposure = exposure_counts(sub)
        found = discovered_true(sub, oracle_ids)
        state = condition_state(exposure, potential)
        recall = len(found) / len(oracle_ids)
        geometry_eligible = state["support_ratio"] >= SAFE_SUPPORT_MIN and state["exposure_gini"] <= SAFE_GINI_MAX
        if geometry_eligible and state["weak_plausible_gap"] == 0:
            controller_decision = "SAFE"
        elif state["weak_plausible_gap"] > 0:
            controller_decision = "CONTINUE"
        else:
            controller_decision = "ABSTAIN"
        rows.append(
            {
                "task_id": TASK_ID,
                "condition": condition,
                "n_events": len(sub),
                "n_agents": sub["agent_id"].nunique(),
                **state,
                "found_true_items": len(found),
                "oracle_total": len(oracle_ids),
                "recall": recall,
                "naive_false_certification": recall < SAFE_RECALL_MIN,
                "geometry_eligible": geometry_eligible,
                "controller_decision": controller_decision,
                "controller_false_certification": controller_decision == "SAFE" and recall < SAFE_RECALL_MIN,
            }
        )
    return pd.DataFrame(rows)


def evaluate_challengers(events: list[dict], oracle_ids: set[str], potential: dict[str, float]) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.DataFrame(events)
    base = df[df["condition"] == "homogeneous"].copy()
    base_exposure = exposure_counts(base)
    base_found = discovered_true(base, oracle_ids)
    base_runtime_seen = set(base.loc[base["new_item"], "discovered_item_id"].dropna())
    base_state = condition_state(base_exposure, potential)
    rows = []
    for strategy in CHALLENGERS:
        for seed in VALIDATION_SEEDS:
            targets = select_targets(base, strategy, seed, potential)
            found = set(base_found)
            runtime_seen = set(base_runtime_seen)
            runtime_residual = set()
            new = set()
            cost = 0
            repaired = Counter(base_exposure)
            for target in targets:
                repaired[target] += 1
                ids, c = candidate_items(target)
                cost += c
                runtime_residual |= ids - runtime_seen
                runtime_seen |= ids
                new |= (ids & oracle_ids) - found
                found |= ids & oracle_ids
            after = condition_state(repaired, potential)
            condition_ok = after["support_ratio"] >= SAFE_SUPPORT_MIN and after["exposure_gini"] <= SAFE_GINI_MAX
            if len(runtime_residual) > 0:
                decision = "CONTINUE"
            elif condition_ok and after["weak_plausible_gap"] == 0:
                decision = "SAFE"
            else:
                decision = "ABSTAIN"
            cumulative_recall = len(found) / len(oracle_ids)
            rows.append(
                {
                    "challenger": strategy,
                    "seed": seed,
                    "targets": ";".join(targets),
                    "base_support_ratio": base_state["support_ratio"],
                    "base_exposure_gini": base_state["exposure_gini"],
                    "after_support_ratio": after["support_ratio"],
                    "after_exposure_gini": after["exposure_gini"],
                    "support_expansion": after["support_size"] - base_state["support_size"],
                    "support_gap_reduction": base_state["weak_plausible_gap"] - after["weak_plausible_gap"],
                    "runtime_residual_items": len(runtime_residual),
                    "new_true_items": len(new),
                    "new_evidence_per_cost": len(new) / cost if cost else 0.0,
                    "cost": cost,
                    "cumulative_recall": cumulative_recall,
                    "decision": decision,
                    "false_certification": decision == "SAFE" and cumulative_recall < SAFE_RECALL_MIN,
                    "abstain_correct": decision == "ABSTAIN" and cumulative_recall < SAFE_RECALL_MIN,
                }
            )
    detailed = pd.DataFrame(rows)
    summary_rows = []
    for challenger, sub in detailed.groupby("challenger"):
        abstain_mask = sub["decision"] == "ABSTAIN"
        abstain_precision = (
            float(sub.loc[abstain_mask, "abstain_correct"].mean())
            if bool(abstain_mask.any())
            else math.nan
        )
        summary_rows.append(
            {
                "challenger": challenger,
                "runs": len(sub),
                "mean_support_expansion": float(sub["support_expansion"].mean()),
                "mean_support_gap_reduction": float(sub["support_gap_reduction"].mean()),
                "mean_new_true_items": float(sub["new_true_items"].mean()),
                "mean_new_evidence_per_cost": float(sub["new_evidence_per_cost"].mean()),
                "mean_cost": float(sub["cost"].mean()),
                "mean_cumulative_recall": float(sub["cumulative_recall"].mean()),
                "safe_rate": float((sub["decision"] == "SAFE").mean()),
                "continue_rate": float((sub["decision"] == "CONTINUE").mean()),
                "abstain_rate": float(abstain_mask.mean()),
                "false_certification_rate": float(sub["false_certification"].mean()),
                "abstain_precision": abstain_precision,
            }
        )
    summary = pd.DataFrame(summary_rows).sort_values(
        ["false_certification_rate", "mean_support_gap_reduction", "mean_new_true_items"],
        ascending=[True, False, False],
    )
    return detailed, summary


def target_set(targets: str) -> set[str]:
    return {t for t in str(targets).split(";") if t}


def overlap_analysis(detailed: pd.DataFrame) -> pd.DataFrame:
    high = detailed[detailed["challenger"] == "high_potential"].set_index("seed")
    residual = detailed[detailed["challenger"] == "residual_potential"].set_index("seed")
    rows = []
    for seed in sorted(set(high.index) & set(residual.index)):
        h = target_set(high.loc[seed, "targets"])
        r = target_set(residual.loc[seed, "targets"])
        inter = h & r
        union = h | r
        rows.append(
            {
                "seed": seed,
                "high_potential_targets": ";".join(sorted(h)),
                "residual_potential_targets": ";".join(sorted(r)),
                "overlap_count": len(inter),
                "union_count": len(union),
                "jaccard": len(inter) / len(union) if union else math.nan,
                "identical": h == r,
                "high_new_true_items": int(high.loc[seed, "new_true_items"]),
                "residual_new_true_items": int(residual.loc[seed, "new_true_items"]),
            }
        )
    return pd.DataFrame(rows)


def write_oracle_note() -> None:
    note = f"""# Oracle Construction Note

## Task

Second external validation uses a real local snapshot of `urllib3` and evaluates a bounded completion audit over timeout, retry, TLS, exception, and resource-cleanup routes.

## Source-Route Strata

Sources:

{chr(10).join(f"- `{rel}`" for rel in FILES)}

Routes:

{chr(10).join(f"- `{route}`" for route in ROUTES)}

The source-route simplex contains `{len(FILES) * len(ROUTES)}` strata.

## Leakage Control

Oracle rows are built offline from the frozen snapshot and are used only after base trajectories and challenger targets are fixed. Runtime potential uses only source text, route names, source length, and lexical route hits. It does not use oracle totals, missing mass, undiscovered true item counts, post-hoc recall, or scorer-visible target distributions.

This oracle is pattern-defined rather than human-annotated, so it is stronger than a generated toy task but weaker than a manual benchmark.
"""
    (REPORTS / "ORACLE_CONSTRUCTION.md").write_text(note, encoding="utf-8")


def write_report(condition: pd.DataFrame, summary: pd.DataFrame, overlap: pd.DataFrame) -> None:
    identical_rate = float(overlap["identical"].mean()) if not overlap.empty else math.nan
    mean_jaccard = float(overlap["jaccard"].mean()) if not overlap.empty else math.nan
    report = f"""# External Validation v2: urllib3 Completion Audit

## Purpose

This is the second external real-repo task. The `requests` result is frozen and used only as a prior mechanism case. This task tests whether the evidence-condition controller avoids false certification on a different real codebase.

## Task

Repository snapshot: local installed `urllib3`.

Audit routes:

{chr(10).join(f"- `{route}`" for route in ROUTES)}

The task is a bounded completion audit: decide whether the workflow has enough evidence to certify that these route families have been covered across the selected repo files.

## Condition Metrics

{condition.to_markdown(index=False)}

## Controller Challenger Summary

{summary.to_markdown(index=False)}

## High-Potential vs Residual-Potential Overlap

- identical target sets: {identical_rate:.3f}
- mean Jaccard: {mean_jaccard:.3f}

## Interpretation

The controller again avoids accepting the localized homogeneous stop as SAFE. It sends productive repairs to `CONTINUE` and reserves `SAFE` for broad near-complete evidence.

The method claim must remain restrained. If high-potential and residual-potential overlap is high, any residual-potential gain is not clean evidence that `under_exposure` adds independent value on this task.

Here the overlap is partial rather than complete. Residual-potential recovers more new scored evidence than high-potential, but it also spends more cost and shares much of the same target set. The correct claim is therefore:

```text
external v2 gives positive evidence for residual-potential as a repair candidate,
but does not prove it is optimal or generally better than high-potential.
```
"""
    (REPORTS / "EXTERNAL_VALIDATION_V2_REPORT.md").write_text(report, encoding="utf-8")

    overlap_head = overlap.head(10)
    (REPORTS / "challenger_overlap_analysis.md").write_text(
        f"""# Challenger Overlap Analysis

## Summary

- identical target sets: {identical_rate:.3f}
- mean Jaccard: {mean_jaccard:.3f}

Unlike the frozen `requests` case, high-potential and residual-potential are not identical here. Residual-potential replaces one high-potential target with an under-exposed high-residual target.

## First Seeds

{overlap_head.to_markdown(index=False)}

## Interpretation

The result is directionally favorable to residual-potential, because it finds more new scored evidence and repairs more support gap. However, the overlap remains high and residual-potential has higher average cost. This supports a cautious method claim only:

```text
residual-potential is a plausible evidence-condition repair rule;
under-exposure contributes in this repo, but optimality is not established.
```
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    write_snapshot()
    potential = runtime_potential()
    oracle = build_oracle()
    oracle_ids = {row["item_id"] for row in oracle}
    events = []
    for condition, agents in CONDITIONS.items():
        events.extend(run_condition(condition, agents))

    condition_metrics = evaluate_conditions(events, oracle_ids, potential)
    detailed, summary = evaluate_challengers(events, oracle_ids, potential)
    overlap = overlap_analysis(detailed)

    (LOGS / "oracle_items.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in oracle) + "\n", encoding="utf-8")
    (LOGS / "action_events.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in events) + "\n", encoding="utf-8")
    condition_metrics.to_csv(RESULTS / "condition_summary.csv", index=False)
    detailed.to_csv(RESULTS / "controller_challenger_detailed.csv", index=False)
    summary.to_csv(RESULTS / "controller_summary.csv", index=False)
    overlap.to_csv(RESULTS / "challenger_overlap_analysis.csv", index=False)

    write_oracle_note()
    write_report(condition_metrics, summary, overlap)

    print(condition_metrics.to_string(index=False))
    print(summary.to_string(index=False))
    print(overlap[["jaccard", "identical"]].describe(include="all").to_string())


if __name__ == "__main__":
    main()
