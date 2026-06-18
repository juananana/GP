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
TASK = PILOT / "blind_tasks" / "code_repo_v1"
REPO = TASK / "repo"
LOGS = TASK / "logs"
RESULTS = TASK / "results"
REPORTS = TASK / "reports"

TASK_ID = "T_blind_code_repo_v1"
CONFIG = load_experiment_config()
CODE_CONFIG = task_config(CONFIG, "code_repo_v1")
VALIDATION_SEEDS = seeds(CONFIG, "validation")
CHALLENGER_SEEDS = seeds(CONFIG, "challenger") or VALIDATION_SEEDS
EVAL_RECALL_THRESHOLD = float(CONFIG.get("thresholds", {}).get("eval_only_recall_threshold", 0.90))
REPAIR_BUDGET = int(CONFIG.get("repair_budgets", {}).get("generated", 4))


FILES = {
    "auth.py": '''import hashlib
import requests

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()  # [C01] deprecated weak hash

API_SECRET = "dev-secret"  # [C02] hardcoded secret

def login(session, url):
    try:
        return session.get(url, verify=False)  # [C03] weak TLS verification
    except Exception:
        return None  # [C04] swallowed auth failure

def migrate_user(user):
    # [C05] TODO legacy migration path still active
    return requests.post("/v1/users/migrate", json=user)  # [C06] deprecated endpoint
''',
    "payments.py": '''from datetime import datetime
import requests

def charge(db, user_id, amount):
    now = datetime.utcnow()  # [C07] deprecated timezone-naive clock
    query = "select * from cards where user_id = " + str(user_id)  # [C08] sql concat
    try:
        cents = int(float(amount) * 100)  # [C09] float money conversion
        return db.execute(query), cents, now
    except Exception:
        pass  # [C10] silent payment failure

def retry_capture(client, payload):
    # [C11] retry loop has no backoff
    for _ in range(3):
        client.post("/capture", json=payload)
''',
    "storage.py": '''import os
import pickle
import tempfile

def load_blob(path):
    return pickle.load(open(path, "rb"))  # [C12] unsafe pickle load

def open_cache(path):
    os.chmod(path, 0o777)  # [C13] world writable cache

def parse_rule(expr):
    return eval(expr)  # [C14] eval on rule expression

def write_temp(data):
    tmp = tempfile.NamedTemporaryFile(delete=False)  # [C15] temp file not cleaned
    tmp.write(data)
    return tmp.name
''',
    "api_client.py": '''import logging
import requests

def fetch_profile(token):
    logging.info("token=%s", token)  # [C16] token logged
    return requests.get("https://api.example.com/v1/profile")  # [C17] deprecated API and no timeout

def call_partner(session, payload):
    try:
        return session.post("https://partner.example.com", json=payload, timeout=None)  # [C18] disabled timeout
    except Exception:
        return {"ok": True}  # [C19] false success on exception

def old_sync(client):
    # [C20] legacy sync path should be removed
    return client.sync_v1()
''',
}


ORACLE = [
    ("C01", "security", "auth.py"),
    ("C02", "security", "auth.py"),
    ("C03", "security", "auth.py"),
    ("C04", "resilience", "auth.py"),
    ("C05", "compatibility", "auth.py"),
    ("C06", "compatibility", "auth.py"),
    ("C07", "compatibility", "payments.py"),
    ("C08", "security", "payments.py"),
    ("C09", "correctness", "payments.py"),
    ("C10", "resilience", "payments.py"),
    ("C11", "resilience", "payments.py"),
    ("C12", "security", "storage.py"),
    ("C13", "security", "storage.py"),
    ("C14", "security", "storage.py"),
    ("C15", "resilience", "storage.py"),
    ("C16", "security", "api_client.py"),
    ("C17", "compatibility", "api_client.py"),
    ("C18", "resilience", "api_client.py"),
    ("C19", "resilience", "api_client.py"),
    ("C20", "compatibility", "api_client.py"),
]


ROUTES = {
    "compat_route": re.compile(r"\b(deprecated|legacy|TODO|/v1|utcnow|sync_v1)\b", re.I),
    "security_route": re.compile(r"\b(md5|secret|verify=False|sql|pickle|chmod|0o777|eval|token)\b", re.I),
    "resilience_route": re.compile(r"\b(except|pass|backoff|timeout|delete=False|return None|ok\": True)\b", re.I),
}


CONDITIONS = {
    "homogeneous": [
        ("H1", "compat_route", list(FILES)),
        ("H2", "compat_route", list(FILES)),
        ("H3", "compat_route", list(FILES)),
    ],
    "route_partitioned": [
        ("R1", "compat_route", list(FILES)),
        ("R2", "security_route", list(FILES)),
        ("R3", "resilience_route", list(FILES)),
    ],
}


def ensure_dirs() -> None:
    for path in [REPO, LOGS, RESULTS, REPORTS]:
        path.mkdir(parents=True, exist_ok=True)


def source_family(name: str) -> str:
    return name.removesuffix(".py")


def item_id_from_line(line: str) -> str | None:
    match = re.search(r"\[(C\d+)\]", line)
    return match.group(1) if match else None


def route_potential(filename: str, route: str) -> int:
    lines = (REPO / filename).read_text(encoding="utf-8").splitlines()
    return sum(1 for line in lines if ROUTES[route].search(line))


def write_task_files() -> None:
    for name, text in FILES.items():
        (REPO / name).write_text(text, encoding="utf-8")
    rows = []
    for item_id, bucket, filename in ORACLE:
        rows.append(
            {
                "task_id": TASK_ID,
                "item_id": item_id,
                "oracle_label": True,
                "oracle_bucket": bucket,
                "source_path": str(REPO / filename),
                "source_family": source_family(filename),
                "source_route_stratum": "",
                "reportable": True,
            }
        )
    (TASK / "hidden_oracle.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def log_event(events: list[dict], **kwargs: object) -> None:
    kwargs["source_route_stratum"] = f"{kwargs['source_family']}::{kwargs['search_route']}"
    events.append(kwargs)


def run_condition(condition: str, agents: list[tuple[str, str, list[str]]]) -> list[dict]:
    events: list[dict] = []
    discovered: set[str] = set()
    event_id = 0
    for agent_id, route, file_names in agents:
        pattern = ROUTES[route]
        for round_id, filename in enumerate(file_names, start=1):
            path = REPO / filename
            lines = path.read_text(encoding="utf-8").splitlines()
            matches = [line for line in lines if pattern.search(line)]
            event_id += 1
            log_event(
                events,
                task_id=TASK_ID,
                repo_id="code_repo_v1",
                run_id=f"{TASK_ID}_{condition}",
                condition=condition,
                agent_id=agent_id,
                round_id=round_id,
                event_id=event_id,
                timestamp="",
                query_text=f"{route} over {filename}",
                tool_name="regex_scan",
                action_type="search",
                source_path=str(path),
                source_family=source_family(filename),
                search_route=route,
                discovered_item_id=None,
                new_item=False,
                self_reported_completion=False,
                self_reported_confidence=0.45,
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
                log_event(
                    events,
                    task_id=TASK_ID,
                    repo_id="code_repo_v1",
                    run_id=f"{TASK_ID}_{condition}",
                    condition=condition,
                    agent_id=agent_id,
                    round_id=round_id,
                    event_id=event_id,
                    timestamp="",
                    query_text=f"extract matched code risk via {route}",
                    tool_name="regex_scan",
                    action_type="extract",
                    source_path=str(path),
                    source_family=source_family(filename),
                    search_route=route,
                    discovered_item_id=item_id,
                    new_item=is_new,
                    self_reported_completion=False,
                    self_reported_confidence=0.5,
                    stop_reason=None,
                    token_or_cost=1,
                    notes=line.strip(),
                )
        event_id += 1
        log_event(
            events,
            task_id=TASK_ID,
            repo_id="code_repo_v1",
            run_id=f"{TASK_ID}_{condition}",
            condition=condition,
            agent_id=agent_id,
            round_id=len(file_names) + 1,
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
    all_strata = [f"{source_family(name)}::{route}" for name in FILES for route in ROUTES]
    rows = []
    df = pd.DataFrame(events)
    for condition, sub in df.groupby("condition"):
        exposure = Counter(sub["source_route_stratum"])
        discovery = Counter(sub.loc[sub["new_item"], "source_route_stratum"])
        exp_vals = np.array([exposure[s] for s in all_strata], dtype=float)
        disc_vals = np.array([discovery[s] for s in all_strata], dtype=float)
        found = set(sub.loc[sub["new_item"], "discovered_item_id"].dropna())
        recall = len(found & oracle_ids) / len(oracle_ids)
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
                "found_true_items": len(found & oracle_ids),
                "oracle_total": len(oracle_ids),
                "recall": recall,
                "false_stop_at_90": bool(recall < EVAL_RECALL_THRESHOLD),
            }
        )
    return pd.DataFrame(rows)


def run_challenger(base_condition: str, events: list[dict], strategy: str, seed: int = 0, write_events: bool = False) -> tuple[list[dict], dict]:
    df = pd.DataFrame(events)
    base = df[df["condition"] == base_condition]
    exposure = Counter(base["source_route_stratum"])
    discovery = Counter(base.loc[base["new_item"], "source_route_stratum"])
    all_strata = [f"{source_family(name)}::{route}" for name in FILES for route in ROUTES]
    if strategy == "low_exposure":
        targets = sorted(all_strata, key=lambda s: (exposure.get(s, 0), s))[:REPAIR_BUDGET]
    elif strategy == "low_discovery":
        targets = sorted(all_strata, key=lambda s: (discovery.get(s, 0), s))[:REPAIR_BUDGET]
    elif strategy == "residual_potential":
        potentials = {s: route_potential(f"{s.split('::', 1)[0]}.py", s.split("::", 1)[1]) for s in all_strata}
        targets = sorted(all_strata, key=lambda s: (exposure.get(s, 0), -potentials[s], s))[:REPAIR_BUDGET]
    elif strategy == "random":
        targets = random.Random(seed).sample(all_strata, min(REPAIR_BUDGET, len(all_strata)))
    else:
        raise ValueError(strategy)

    found_before = set(base.loc[base["new_item"], "discovered_item_id"].dropna())
    challenger_events: list[dict] = []
    event_id = 10000
    for idx, stratum in enumerate(targets, start=1):
        family, route = stratum.split("::", 1)
        filename = f"{family}.py"
        path = REPO / filename
        lines = path.read_text(encoding="utf-8").splitlines()
        event_id += 1
        log_event(
            challenger_events,
            task_id=TASK_ID,
            repo_id="code_repo_v1",
            run_id=f"{TASK_ID}_{base_condition}_{strategy}_challenger_seed{seed}",
            condition=f"{base_condition}_{strategy}_challenger",
            agent_id=f"C_{strategy}",
            round_id=idx,
            event_id=event_id,
            timestamp="",
            query_text=f"{strategy} challenger scans {route} over {filename}",
            tool_name="regex_scan",
            action_type="search",
            source_path=str(path),
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
            if not ROUTES[route].search(line):
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
                repo_id="code_repo_v1",
                run_id=f"{TASK_ID}_{base_condition}_{strategy}_challenger_seed{seed}",
                condition=f"{base_condition}_{strategy}_challenger",
                agent_id=f"C_{strategy}",
                round_id=idx,
                event_id=event_id,
                timestamp="",
                query_text=f"extract challenger risk via {route}",
                tool_name="regex_scan",
                action_type="extract",
                source_path=str(path),
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
    cdf = pd.DataFrame(challenger_events)
    base_true = set(base.loc[base["new_item"], "discovered_item_id"].dropna()) & oracle_ids
    new_true = set(cdf.loc[cdf["new_item"], "discovered_item_id"].dropna()) & oracle_ids
    cumulative_true = base_true | new_true
    return (challenger_events if write_events else []), {
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


def write_report(metrics: pd.DataFrame, challenger: pd.DataFrame) -> None:
    summary = challenger.groupby("challenger", as_index=False).agg(
        runs=("seed", "count"),
        mean_new_true_items=("new_true_items", "mean"),
        max_new_true_items=("new_true_items", "max"),
        mean_cumulative_recall=("cumulative_recall", "mean"),
    )
    (REPORTS / "BLIND_CODE_TASK_REPORT.md").write_text(
        f"""# Blind Code Task Report

This runtime-blind code discovery task asks agents to find compatibility, security, correctness, and resilience risk sites in a bounded generated repository. The oracle is stored separately and used only during scoring.

## Condition Metrics

{metrics.to_markdown(index=False)}

## Challenger Summary

{summary.to_markdown(index=False)}

## Challenger Metrics

{challenger.to_markdown(index=False)}

## Interpretation

This second task reproduces the main diagnostic pattern if homogeneous route reuse has higher exposure localization and lower recall than route-partitioned search. Challenger results should be treated as intervention diagnostics, not final method evidence, unless they beat random baselines.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    write_task_files()
    all_events: list[dict] = []
    for condition, agents in CONDITIONS.items():
        all_events.extend(run_condition(condition, agents))
    challenger_events, low_exp = run_challenger("homogeneous", all_events, "low_exposure", write_events=True)
    all_events.extend(challenger_events)
    rows = [low_exp]
    _, low_disc = run_challenger("homogeneous", all_events, "low_discovery")
    rows.append(low_disc)
    _, residual = run_challenger("homogeneous", all_events, "residual_potential")
    rows.append(residual)
    for seed in CHALLENGER_SEEDS:
        _, rand = run_challenger("homogeneous", all_events, "random", seed=seed)
        rows.append(rand)
    challenger = pd.DataFrame(rows)
    metrics = summarize(all_events)

    (LOGS / "action_events.jsonl").write_text(
        "\n".join(json.dumps(event, ensure_ascii=False) for event in all_events) + "\n",
        encoding="utf-8",
    )
    (LOGS / "oracle_items.jsonl").write_text((TASK / "hidden_oracle.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
    metrics.to_csv(RESULTS / "condition_metrics.csv", index=False)
    challenger.to_csv(RESULTS / "challenger_metrics.csv", index=False)
    challenger.groupby("challenger", as_index=False).agg(
        runs=("seed", "count"),
        mean_new_true_items=("new_true_items", "mean"),
        max_new_true_items=("new_true_items", "max"),
        mean_cumulative_recall=("cumulative_recall", "mean"),
    ).to_csv(RESULTS / "challenger_summary.csv", index=False)
    write_report(metrics, challenger)
    print(metrics.to_string(index=False))
    print(challenger.groupby("challenger", as_index=False).agg(runs=("seed", "count"), mean_new_true_items=("new_true_items", "mean"), max_new_true_items=("new_true_items", "max")).to_string(index=False))


if __name__ == "__main__":
    main()
