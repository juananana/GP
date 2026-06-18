from __future__ import annotations

import json
import math
import random
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from experiment_config import load_experiment_config, seeds, task_config

ROOT = Path(__file__).resolve().parents[4]
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"
TASK = PILOT / "blind_tasks" / "policy_docset_v1"
DOCS = TASK / "docs"
LOGS = TASK / "logs"
RESULTS = TASK / "results"
REPORTS = TASK / "reports"

TASK_ID = "T_blind_policy_docset_v1"
CONFIG = load_experiment_config()
POLICY_CONFIG = task_config(CONFIG, "policy_docset_v1")
VALIDATION_SEEDS = seeds(CONFIG, "validation")
CHALLENGER_SEEDS = seeds(CONFIG, "challenger") or VALIDATION_SEEDS
EVAL_RECALL_THRESHOLD = float(CONFIG.get("thresholds", {}).get("eval_only_recall_threshold", 0.90))
REPAIR_BUDGET = int(CONFIG.get("repair_budgets", {}).get("generated", 4))


DOCSET = {
    "access_control.md": """# Access Control

[P01] Service owners MUST rotate production API keys every 90 days.
[P02] Contractors MUST use time-limited accounts for production access.
[P03] Privileged access SHALL be reviewed by two independent approvers.
[P04] Break-glass access is allowed ONLY during customer-impacting incidents.
[P05] After break-glass use, the owner MUST file an incident note within 24 hours.
[P06] Shared administrative accounts are prohibited unless the legacy exception register lists an active waiver.
""",
    "data_handling.md": """# Data Handling

[P07] Customer exports MUST be encrypted at rest.
[P08] Raw diagnostic logs SHALL NOT include authentication secrets.
[P09] Temporary analysis copies must be deleted within 30 days.
[P10] De-identified samples may be retained for model debugging if the privacy review is attached.
[P11] Cross-region transfer is forbidden unless legal approval and customer notice are recorded.
[P12] Incident responders may snapshot affected records during an active severity-one investigation.
""",
    "release_process.md": """# Release Process

[P13] Release candidates MUST pass dependency vulnerability scanning.
[P14] A rollback owner MUST be named before a production deployment.
[P15] Feature flags SHALL default to off for regulated customers.
[P16] Emergency patches may bypass staging only with director approval.
[P17] Post-deployment verification must be completed within 6 hours.
[P18] Deprecated endpoints require customer migration notice at least 60 days before removal.
""",
    "audit_and_exceptions.md": """# Audit And Exceptions

[P19] Every policy exception MUST include an expiry date.
[P20] Expired exceptions SHALL be treated as denied requests.
[P21] Exception renewals require fresh risk acceptance from the data owner.
[P22] Audit evidence must be retained for 18 months.
[P23] Low-risk sandbox systems are exempt from quarterly access reviews.
[P24] Missing evidence must trigger a remediation ticket within 5 business days.
""",
}


ORACLE = [
    ("P01", "obligation", "access_control.md"),
    ("P02", "obligation", "access_control.md"),
    ("P03", "obligation", "access_control.md"),
    ("P04", "exception", "access_control.md"),
    ("P05", "deadline", "access_control.md"),
    ("P06", "exception", "access_control.md"),
    ("P07", "obligation", "data_handling.md"),
    ("P08", "prohibition", "data_handling.md"),
    ("P09", "deadline", "data_handling.md"),
    ("P10", "exception", "data_handling.md"),
    ("P11", "exception", "data_handling.md"),
    ("P12", "exception", "data_handling.md"),
    ("P13", "obligation", "release_process.md"),
    ("P14", "obligation", "release_process.md"),
    ("P15", "obligation", "release_process.md"),
    ("P16", "exception", "release_process.md"),
    ("P17", "deadline", "release_process.md"),
    ("P18", "deadline", "release_process.md"),
    ("P19", "obligation", "audit_and_exceptions.md"),
    ("P20", "prohibition", "audit_and_exceptions.md"),
    ("P21", "obligation", "audit_and_exceptions.md"),
    ("P22", "deadline", "audit_and_exceptions.md"),
    ("P23", "exception", "audit_and_exceptions.md"),
    ("P24", "deadline", "audit_and_exceptions.md"),
]


ROUTES = {
    "obligation_route": re.compile(r"\b(MUST|SHALL|required|require|requires)\b", re.I),
    "exception_route": re.compile(r"\b(ONLY|unless|exception|exempt|may|allowed|bypass|waiver)\b", re.I),
    "deadline_route": re.compile(r"\b(within|days|hours|months|before|expiry|expired)\b", re.I),
    "prohibition_route": re.compile(r"\b(prohibited|forbidden|SHALL NOT|denied)\b", re.I),
}


CONDITIONS = {
    "homogeneous": [
        ("H1", "obligation_route", ["access_control.md", "data_handling.md", "release_process.md", "audit_and_exceptions.md"]),
        ("H2", "obligation_route", ["access_control.md", "data_handling.md", "release_process.md", "audit_and_exceptions.md"]),
        ("H3", "obligation_route", ["access_control.md", "data_handling.md", "release_process.md", "audit_and_exceptions.md"]),
    ],
    "route_partitioned": [
        ("R1", "obligation_route", ["access_control.md", "data_handling.md", "release_process.md", "audit_and_exceptions.md"]),
        ("R2", "exception_route", ["access_control.md", "data_handling.md", "release_process.md", "audit_and_exceptions.md"]),
        ("R3", "deadline_route", ["access_control.md", "data_handling.md", "release_process.md", "audit_and_exceptions.md"]),
    ],
}


def ensure_dirs() -> None:
    for path in [DOCS, LOGS, RESULTS, REPORTS]:
        path.mkdir(parents=True, exist_ok=True)


def write_task_files() -> None:
    for name, text in DOCSET.items():
        (DOCS / name).write_text(text, encoding="utf-8")
    oracle_path = TASK / "hidden_oracle.jsonl"
    rows = []
    for item_id, bucket, doc_name in ORACLE:
        rows.append(
            {
                "task_id": TASK_ID,
                "item_id": item_id,
                "oracle_label": True,
                "oracle_bucket": bucket,
                "source_path": str(DOCS / doc_name),
                "source_family": doc_name.removesuffix(".md"),
                "source_route_stratum": "",
                "reportable": True,
            }
        )
    oracle_path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def item_id_from_line(line: str) -> str | None:
    match = re.search(r"\[(P\d+)\]", line)
    return match.group(1) if match else None


def route_potential(doc_name: str, route: str) -> int:
    lines = (DOCS / doc_name).read_text(encoding="utf-8").splitlines()
    return sum(1 for line in lines if ROUTES[route].search(line))


def source_family(doc_name: str) -> str:
    return doc_name.removesuffix(".md")


def log_event(events: list[dict], **kwargs: object) -> None:
    kwargs["source_route_stratum"] = f"{kwargs['source_family']}::{kwargs['search_route']}"
    events.append(kwargs)


def run_condition(condition: str, agents: list[tuple[str, str, list[str]]]) -> list[dict]:
    events: list[dict] = []
    discovered: set[str] = set()
    event_id = 0
    for agent_id, route, doc_names in agents:
        pattern = ROUTES[route]
        no_new_streak = 0
        for round_id, doc_name in enumerate(doc_names, start=1):
            doc_path = DOCS / doc_name
            lines = doc_path.read_text(encoding="utf-8").splitlines()
            matches = [line for line in lines if pattern.search(line)]
            new_in_round = 0
            event_id += 1
            log_event(
                events,
                task_id=TASK_ID,
                repo_id="policy_docset_v1",
                run_id=f"{TASK_ID}_{condition}",
                condition=condition,
                agent_id=agent_id,
                round_id=round_id,
                event_id=event_id,
                timestamp="",
                query_text=f"{route} over {doc_name}",
                tool_name="regex_scan",
                action_type="search",
                source_path=str(doc_path),
                source_family=source_family(doc_name),
                search_route=route,
                discovered_item_id=None,
                new_item=False,
                self_reported_completion=False,
                self_reported_confidence=0.4 + min(0.4, 0.1 * no_new_streak),
                stop_reason=None,
                token_or_cost=len(lines),
                notes=f"{len(matches)} matched lines",
            )
            for line in matches:
                item_id = item_id_from_line(line)
                if not item_id:
                    continue
                event_id += 1
                is_new = item_id not in discovered
                if is_new:
                    discovered.add(item_id)
                    new_in_round += 1
                log_event(
                    events,
                    task_id=TASK_ID,
                    repo_id="policy_docset_v1",
                    run_id=f"{TASK_ID}_{condition}",
                    condition=condition,
                    agent_id=agent_id,
                    round_id=round_id,
                    event_id=event_id,
                    timestamp="",
                    query_text=f"extract matched clause via {route}",
                    tool_name="regex_scan",
                    action_type="extract",
                    source_path=str(doc_path),
                    source_family=source_family(doc_name),
                    search_route=route,
                    discovered_item_id=item_id,
                    new_item=is_new,
                    self_reported_completion=False,
                    self_reported_confidence=0.5,
                    stop_reason=None,
                    token_or_cost=1,
                    notes=line.strip(),
                )
            no_new_streak = no_new_streak + 1 if new_in_round == 0 else 0
        event_id += 1
        log_event(
            events,
            task_id=TASK_ID,
            repo_id="policy_docset_v1",
            run_id=f"{TASK_ID}_{condition}",
            condition=condition,
            agent_id=agent_id,
            round_id=len(doc_names) + 1,
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


def summarize(events: list[dict]) -> pd.DataFrame:
    oracle_ids = {item_id for item_id, _, _ in ORACLE}
    all_strata = [f"{source_family(name)}::{route}" for name in DOCSET for route in ROUTES]
    rows = []
    for condition, sub_events in pd.DataFrame(events).groupby("condition"):
        exposure = Counter(sub_events["source_route_stratum"])
        discovery = Counter(sub_events.loc[sub_events["new_item"], "source_route_stratum"])
        exp_vals = np.array([exposure[s] for s in all_strata], dtype=float)
        disc_vals = np.array([discovery[s] for s in all_strata], dtype=float)
        found = set(sub_events.loc[sub_events["new_item"], "discovered_item_id"].dropna())
        recall = len(found & oracle_ids) / len(oracle_ids)
        rows.append(
            {
                "task_id": TASK_ID,
                "condition": condition,
                "n_events": len(sub_events),
                "n_agents": int(sub_events["agent_id"].nunique()),
                "n_exposure_strata": int((exp_vals > 0).sum()),
                "n_discovery_strata": int((disc_vals > 0).sum()),
                "source_route_coverage_ratio": float((exp_vals > 0).mean()),
                "exposure_gini": gini(exp_vals),
                "discovery_gini": gini(disc_vals),
                "found_true_items": len(found & oracle_ids),
                "oracle_total": len(oracle_ids),
                "recall": recall,
                "false_stop_at_90": bool(recall < EVAL_RECALL_THRESHOLD),
            }
        )
    return pd.DataFrame(rows)


def run_challenger(
    base_condition: str,
    events: list[dict],
    strategy: str,
    seed: int = 0,
    write_events: bool = False,
) -> tuple[list[dict], dict]:
    df = pd.DataFrame(events)
    base = df[df["condition"] == base_condition]
    exposure = Counter(base["source_route_stratum"])
    discovery = Counter(base.loc[base["new_item"], "source_route_stratum"])
    all_source_families = [source_family(name) for name in DOCSET]
    all_strata = [f"{family}::{route}" for family in all_source_families for route in ROUTES]
    if strategy == "low_exposure":
        targets = sorted(all_strata, key=lambda s: (exposure.get(s, 0), s))[:REPAIR_BUDGET]
    elif strategy == "low_discovery":
        targets = sorted(all_strata, key=lambda s: (discovery.get(s, 0), s))[:REPAIR_BUDGET]
    elif strategy == "residual_potential":
        potentials = {s: route_potential(f"{s.split('::', 1)[0]}.md", s.split("::", 1)[1]) for s in all_strata}
        targets = sorted(all_strata, key=lambda s: (exposure.get(s, 0), -potentials[s], s))[:REPAIR_BUDGET]
    elif strategy == "random":
        rng = random.Random(seed)
        targets = rng.sample(all_strata, min(REPAIR_BUDGET, len(all_strata)))
    else:
        raise ValueError(f"unknown challenger strategy: {strategy}")
    found_before = set(base.loc[base["new_item"], "discovered_item_id"].dropna())
    challenger_events = []
    event_id = 10000
    for idx, stratum in enumerate(targets, start=1):
        family, route = stratum.split("::", 1)
        doc_name = f"{family}.md"
        doc_path = DOCS / doc_name
        pattern = ROUTES[route]
        lines = doc_path.read_text(encoding="utf-8").splitlines()
        event_id += 1
        log_event(
            challenger_events,
            task_id=TASK_ID,
            repo_id="policy_docset_v1",
            run_id=f"{TASK_ID}_{base_condition}_{strategy}_challenger_seed{seed}",
            condition=f"{base_condition}_{strategy}_challenger",
            agent_id=f"C_{strategy}",
            round_id=idx,
            event_id=event_id,
            timestamp="",
            query_text=f"{strategy} challenger scans {route} over {doc_name}",
            tool_name="regex_scan",
            action_type="search",
            source_path=str(doc_path),
            source_family=family,
            search_route=route,
            discovered_item_id=None,
            new_item=False,
            self_reported_completion=False,
            self_reported_confidence=0.3,
            stop_reason=None,
            token_or_cost=len(lines),
            notes=f"selected by {strategy}; oracle not consulted",
        )
        for line in lines:
            if not pattern.search(line):
                continue
            item_id = item_id_from_line(line)
            if not item_id:
                continue
            event_id += 1
            is_new = item_id not in found_before
            if is_new:
                found_before.add(item_id)
            log_event(
                challenger_events,
                task_id=TASK_ID,
                repo_id="policy_docset_v1",
                run_id=f"{TASK_ID}_{base_condition}_{strategy}_challenger_seed{seed}",
                condition=f"{base_condition}_{strategy}_challenger",
                agent_id=f"C_{strategy}",
                round_id=idx,
                event_id=event_id,
                timestamp="",
                query_text=f"extract challenger clause via {route}",
                tool_name="regex_scan",
                action_type="extract",
                source_path=str(doc_path),
                source_family=family,
                search_route=route,
                discovered_item_id=item_id,
                new_item=is_new,
                self_reported_completion=False,
                self_reported_confidence=0.3,
                stop_reason=None,
                token_or_cost=1,
                notes=line.strip(),
            )
    oracle_ids = {item_id for item_id, _, _ in ORACLE}
    challenger_df = pd.DataFrame(challenger_events)
    base_true = set(base.loc[base["new_item"], "discovered_item_id"].dropna()) & oracle_ids
    new_true = set(challenger_df.loc[challenger_df["new_item"], "discovered_item_id"].dropna()) & oracle_ids
    cumulative_true = base_true | new_true
    metrics = {
        "base_condition": base_condition,
        "challenger": strategy,
        "seed": seed,
        "targeted_strata": ";".join(targets),
        "challenger_events": len(challenger_events),
        "base_true_items": len(base_true),
        "new_true_items": len(new_true),
        "cumulative_true_items": len(cumulative_true),
        "cumulative_recall": len(cumulative_true) / len(oracle_ids),
        "new_true_item_ids": ";".join(sorted(new_true)),
    }
    return (challenger_events if write_events else []), metrics


def write_report(metrics: pd.DataFrame, challenger: pd.DataFrame) -> None:
    path = REPORTS / "BLIND_POLICY_TASK_REPORT.md"
    metrics_md = metrics.to_markdown(index=False)
    challenger_md = challenger.to_markdown(index=False)
    summary_md = (
        challenger.groupby("challenger", as_index=False)
        .agg(
            runs=("seed", "count"),
            mean_new_true_items=("new_true_items", "mean"),
            max_new_true_items=("new_true_items", "max"),
            mean_cumulative_recall=("cumulative_recall", "mean"),
        )
        .to_markdown(index=False)
    )
    path.write_text(
        f"""# Blind Policy Task Report

This is a runtime-blind policy-clause discovery task. Search agents scan only the bounded source documents. The oracle file is written separately and is used only during scoring.

## Condition Metrics

{metrics_md}

## Challenger Metrics

{challenger_md}

## Challenger Summary

{summary_md}

## Interpretation

The homogeneous condition intentionally reuses one route across agents. It reaches a high self-reported stop state while missing oracle items outside the dominant route. The route-partitioned condition spreads exposure across route strata and recovers substantially more of the hidden set.

The low-exposure challenger is derived from runtime exposure counts only. Its recovered true positives are evidence that low-exposure strata contain residual missing mass after the blind stop. However, in this first task it does not beat the random challenger average. So the current evidence supports exposure localization as a stopping-risk diagnostic more strongly than it supports this exact bottom-k challenger rule as the final intervention.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    write_task_files()
    all_events = []
    for condition, agents in CONDITIONS.items():
        all_events.extend(run_condition(condition, agents))
    challenger_events, low_exp_metrics = run_challenger("homogeneous", all_events, "low_exposure", write_events=True)
    all_events.extend(challenger_events)
    challenger_rows = [low_exp_metrics]
    _, low_disc_metrics = run_challenger("homogeneous", all_events, "low_discovery")
    challenger_rows.append(low_disc_metrics)
    _, residual_metrics = run_challenger("homogeneous", all_events, "residual_potential")
    challenger_rows.append(residual_metrics)
    for seed in CHALLENGER_SEEDS:
        _, random_metrics = run_challenger("homogeneous", all_events, "random", seed=seed)
        challenger_rows.append(random_metrics)
    challenger_metrics = pd.DataFrame(challenger_rows)

    (LOGS / "action_events.jsonl").write_text(
        "\n".join(json.dumps(event, ensure_ascii=False) for event in all_events) + "\n",
        encoding="utf-8",
    )
    (LOGS / "oracle_items.jsonl").write_text((TASK / "hidden_oracle.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
    metrics = summarize(all_events)
    metrics.to_csv(RESULTS / "condition_metrics.csv", index=False)
    challenger_metrics.to_csv(RESULTS / "challenger_metrics.csv", index=False)
    challenger_metrics.groupby("challenger", as_index=False).agg(
        runs=("seed", "count"),
        mean_new_true_items=("new_true_items", "mean"),
        max_new_true_items=("new_true_items", "max"),
        mean_cumulative_recall=("cumulative_recall", "mean"),
    ).to_csv(RESULTS / "challenger_summary.csv", index=False)
    write_report(metrics, challenger_metrics)
    print(f"wrote {len(all_events)} blind action events")
    print(metrics.to_string(index=False))
    print(challenger_metrics.to_string(index=False))


if __name__ == "__main__":
    main()
