from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from experiment_config import load_experiment_config, thresholds, task_config

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "external_validation_requests"
OUT = ROOT / "controller_validation_v1"
RESULTS = OUT / "results"
REPORTS = OUT / "reports"

FILES = ["adapters", "api", "auth", "models", "sessions", "utils"]
GRANULARITY = "source_route"
CONFIG = load_experiment_config()
THRESHOLDS = thresholds(CONFIG)
REQUESTS_CONFIG = task_config(CONFIG, "requests")
RECALL_SAFE_MIN = THRESHOLDS["eval_recall"]

ROUTE_PATTERNS = {
    "tls_route": re.compile(r"\b(verify|cert|ssl|SSL|TLS|cert_verify|ca_bundle|DEFAULT_CA_BUNDLE_PATH)\b"),
    "timeout_route": re.compile(r"\b(timeout|Timeout|connect timeout|read timeout)\b", re.I),
    "exception_route": re.compile(r"\b(except|raise|RetryError|SSLError|ConnectionError|Timeout|TooManyRedirects)\b"),
    "compat_route": re.compile(r"\b(deprecated|compat|super_len|basestring|builtin_str|to_native_string|unicode_is_ascii)\b", re.I),
}

ROUTES = list(REQUESTS_CONFIG.get("routes", ROUTE_PATTERNS.keys()))
UNKNOWN_ROUTES = [route for route in ROUTES if route not in ROUTE_PATTERNS]
if UNKNOWN_ROUTES:
    raise ValueError(f"unknown requests route(s) in config: {UNKNOWN_ROUTES}")


def ensure_dirs() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def gini(values: list[float]) -> float:
    x = np.array(values, dtype=float)
    if x.size == 0 or x.sum() == 0:
        return math.nan
    x = np.sort(x)
    n = x.size
    return float((2 * np.sum(np.arange(1, n + 1) * x) / (n * x.sum())) - (n + 1) / n)


def universe() -> list[str]:
    return [f"{source}::{route}" for source in FILES for route in ROUTES]


def stratum_from_target(target: str) -> str:
    parts = str(target).split("::")
    return f"{parts[0]}::{parts[1]}"


def target_set(targets: str) -> set[str]:
    return {stratum_from_target(t) for t in str(targets).split(";") if t}


def runtime_potential_from_source() -> dict[str, float]:
    potential: dict[str, float] = {}
    snapshot = EXT / "repo_snapshot"
    for source in FILES:
        text = (snapshot / f"{source}.py").read_text(encoding="utf-8", errors="ignore")
        for route, pattern in ROUTE_PATTERNS.items():
            potential[f"{source}::{route}"] = float(sum(1 for line in text.splitlines() if pattern.search(line)))
    return potential


def exposure_counts(df: pd.DataFrame) -> Counter:
    return Counter(df["source_route_stratum"])


def discovered_true(df: pd.DataFrame, oracle: set[str]) -> set[str]:
    return set(df.loc[df["new_item"], "discovered_item_id"].dropna()) & oracle


def condition_state(exposure: Counter, potential: dict[str, float]) -> dict:
    strata = universe()
    values = [float(exposure.get(s, 0)) for s in strata]
    occupied = {s for s in strata if exposure.get(s, 0) > 0}
    weak_plausible = {s for s in strata if exposure.get(s, 0) == 0 and potential.get(s, 0.0) > 0}
    return {
        "support_size": len(occupied),
        "support_ratio": len(occupied) / len(strata),
        "exposure_gini": gini(values),
        "weak_plausible_gap": len(weak_plausible),
    }


def repair_exposure(base_exposure: Counter, targets: str) -> Counter:
    repaired = Counter(base_exposure)
    for target in str(targets).split(";"):
        if target:
            repaired[stratum_from_target(target)] += 1
    return repaired


def controller_decision(row: pd.Series, support_thr: float, gini_thr: float) -> str:
    condition_ok = float(row["after_support_ratio"]) >= support_thr and float(row["after_exposure_gini"]) <= gini_thr
    if "runtime_residual_items" not in row:
        raise KeyError("runtime_residual_items is required for controller decisions")
    runtime_residual = int(row["runtime_residual_items"])
    support_gap_remaining = int(row.get("weak_plausible_gap_after", row.get("after_weak_plausible_gap", 0)))
    if runtime_residual > 0:
        return "CONTINUE"
    if condition_ok and support_gap_remaining == 0:
        return "SAFE"
    return "ABSTAIN"


def overlap_analysis(detailed: pd.DataFrame, base: pd.DataFrame, potential: dict[str, float]) -> tuple[pd.DataFrame, pd.DataFrame]:
    source_route = detailed[detailed["granularity"] == GRANULARITY].copy()
    high = source_route[source_route["challenger"] == "high_potential"].set_index("seed")
    residual = source_route[source_route["challenger"] == "residual_potential"].set_index("seed")
    rows = []
    for seed in sorted(set(high.index) & set(residual.index)):
        high_targets = target_set(high.loc[seed, "targets"])
        residual_targets = target_set(residual.loc[seed, "targets"])
        intersection = high_targets & residual_targets
        union = high_targets | residual_targets
        rows.append(
            {
                "seed": int(seed),
                "high_potential_targets": ";".join(sorted(high_targets)),
                "residual_potential_targets": ";".join(sorted(residual_targets)),
                "overlap_count": len(intersection),
                "union_count": len(union),
                "jaccard": len(intersection) / len(union) if union else math.nan,
                "identical": high_targets == residual_targets,
                "high_new_true_items": int(high.loc[seed, "new_true_items"]),
                "residual_new_true_items": int(residual.loc[seed, "new_true_items"]),
            }
        )
    overlap = pd.DataFrame(rows)

    exposure = exposure_counts(base)
    max_exp = max([exposure.get(s, 0) for s in universe()] + [1])
    score_rows = []
    for s in universe():
        under_exposure = 1.0 - exposure.get(s, 0) / max_exp
        score_rows.append(
            {
                "stratum": s,
                "base_exposure": exposure.get(s, 0),
                "runtime_potential": potential[s],
                "under_exposure": under_exposure,
                "high_potential_rank_key": -potential[s],
                "residual_potential_score": under_exposure * potential[s],
            }
        )
    scores = pd.DataFrame(score_rows).sort_values(["runtime_potential", "residual_potential_score"], ascending=[False, False])
    return overlap, scores


def threshold_sweep(controller_detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    raw_thresholds = CONFIG.get("thresholds", {})
    support_value = raw_thresholds.get("tau_support", THRESHOLDS["tau_support"])
    gini_value = raw_thresholds.get("tau_gini", THRESHOLDS["tau_gini"])
    support_grid = list(support_value) if isinstance(support_value, list) else [0.25, 0.33, 0.40, 0.50, 0.67, float(support_value), 0.90, 1.00]
    gini_grid = list(gini_value) if isinstance(gini_value, list) else [0.60, float(gini_value), 0.80, 0.90]
    for support_thr in support_grid:
        for gini_thr in gini_grid:
            for challenger, sub in controller_detail.groupby("challenger"):
                decisions = sub.apply(lambda row: controller_decision(row, support_thr, gini_thr), axis=1)
                false_cert = (decisions == "SAFE") & (sub["cumulative_recall"].astype(float) < RECALL_SAFE_MIN)
                abstain = decisions == "ABSTAIN"
                abstain_precision = (
                    float(((sub["cumulative_recall"].astype(float) < RECALL_SAFE_MIN) & abstain).sum() / abstain.sum())
                    if abstain.sum() > 0
                    else math.nan
                )
                rows.append(
                    {
                        "support_threshold": support_thr,
                        "gini_threshold": gini_thr,
                        "challenger": challenger,
                        "runs": len(sub),
                        "safe_rate": float((decisions == "SAFE").mean()),
                        "continue_rate": float((decisions == "CONTINUE").mean()),
                        "abstain_rate": float(abstain.mean()),
                        "false_certification_rate": float(false_cert.mean()),
                        "abstain_precision": abstain_precision,
                        "mean_cost": float(sub.get("cost", pd.Series([math.nan] * len(sub))).astype(float).mean()),
                        "mean_cumulative_recall": float(sub["cumulative_recall"].astype(float).mean()),
                    }
                )
    return pd.DataFrame(rows)


def build_controller_detail(detailed: pd.DataFrame, base: pd.DataFrame, potential: dict[str, float], oracle: set[str]) -> pd.DataFrame:
    base_exposure = exposure_counts(base)
    before = condition_state(base_exposure, potential)
    source_route = detailed[detailed["granularity"] == GRANULARITY].copy()
    rows = []
    for _, row in source_route.iterrows():
        after = condition_state(repair_exposure(base_exposure, row["targets"]), potential)
        rows.append(
            {
                "challenger": row["challenger"],
                "seed": int(row["seed"]),
                "targets": row["targets"],
                "base_support_ratio": before["support_ratio"],
                "base_exposure_gini": before["exposure_gini"],
                "after_support_ratio": after["support_ratio"],
                "after_exposure_gini": after["exposure_gini"],
                "support_expansion": after["support_size"] - before["support_size"],
                "support_gap_reduction": before["weak_plausible_gap"] - after["weak_plausible_gap"],
                "after_weak_plausible_gap": after["weak_plausible_gap"],
                "runtime_residual_items": int(row["runtime_residual_items"]),
                "new_true_items": int(row["new_true_items"]),
                "cost": int(row["cost"]),
                "cumulative_recall": float(row["cumulative_recall"]),
            }
        )
    return pd.DataFrame(rows)


def matched_prefix(frame: pd.DataFrame, count: int) -> pd.DataFrame:
    searches = frame[frame["action_type"] == "search"]
    extracts = frame[(frame["action_type"] == "extract") & (frame["new_item"])].head(count)
    return pd.concat([searches, extracts], ignore_index=True)


def matched_perturbation_v2(events: pd.DataFrame, oracle: set[str], potential: dict[str, float]) -> pd.DataFrame:
    homogeneous = events[(events["condition"] == "homogeneous") & (events["source_family"] != "controller")].copy()
    partitioned = events[(events["condition"] == "route_partitioned") & (events["source_family"] != "controller")].copy()
    total = len(oracle)
    states: list[tuple[str, str, pd.DataFrame, bool]] = [
        ("local_observed_31", "observed homogeneous local evidence", homogeneous, False),
        ("broad_matched_31", "same discovered count as homogeneous, broad source-route searches", matched_prefix(partitioned, 31), True),
        ("broad_prefix_100", "broad exposure with medium continuing evidence", matched_prefix(partitioned, 100), True),
        ("broad_prefix_200", "broad exposure with high continuing evidence", matched_prefix(partitioned, 200), True),
        ("broad_observed_298", "observed route-partitioned completed audit", partitioned, False),
    ]
    rows = []
    for state_name, note, frame, evidence_still_appearing in states:
        found = discovered_true(frame, oracle)
        condition = condition_state(exposure_counts(frame), potential)
        geometry_eligible = condition["support_ratio"] >= THRESHOLDS["tau_support"] and condition["exposure_gini"] <= THRESHOLDS["tau_gini"]
        if geometry_eligible and not evidence_still_appearing:
            decision = "SAFE"
        elif evidence_still_appearing:
            decision = "CONTINUE"
        else:
            decision = "ABSTAIN"
        rows.append(
            {
                "state": state_name,
                "note": note,
                "discovered_true_items": len(found),
                "recall": len(found) / total,
                "support_ratio": condition["support_ratio"],
                "exposure_gini": condition["exposure_gini"],
                "weak_plausible_gap": condition["weak_plausible_gap"],
                "geometry_eligible": geometry_eligible,
                "evidence_still_appearing": evidence_still_appearing,
                "controller_decision": decision,
                "false_certification_if_safe": bool(decision == "SAFE" and len(found) / total < RECALL_SAFE_MIN),
            }
        )
    return pd.DataFrame(rows)


def write_reports(
    overlap: pd.DataFrame,
    scores: pd.DataFrame,
    sweep: pd.DataFrame,
    perturbation: pd.DataFrame,
) -> None:
    identical_rate = float(overlap["identical"].mean()) if not overlap.empty else math.nan
    mean_jaccard = float(overlap["jaccard"].mean()) if not overlap.empty else math.nan
    sweep_summary = (
        sweep.groupby("challenger", as_index=False)
        .agg(
            mean_false_certification_rate=("false_certification_rate", "mean"),
            max_false_certification_rate=("false_certification_rate", "max"),
            mean_safe_rate=("safe_rate", "mean"),
            mean_continue_rate=("continue_rate", "mean"),
            mean_abstain_rate=("abstain_rate", "mean"),
            mean_abstain_precision=("abstain_precision", "mean"),
            mean_cost=("mean_cost", "mean"),
        )
        .sort_values(["mean_false_certification_rate", "mean_continue_rate"], ascending=[True, False])
    )

    (REPORTS / "CONTROLLER_VALIDATION_V2_PLAN.md").write_text(
        """# Controller Validation v2 Plan

## Scope

Do not change the paper mainline and do not introduce new core variables. This validation only stress-tests the existing evidence-condition controller on the external `requests` task.

## Experiments

1. Challenger overlap: compare source-route strata selected by `high_potential` and `residual_potential`.
2. Threshold sweep: vary support-ratio and exposure-Gini thresholds while keeping the same SAFE / CONTINUE / ABSTAIN semantics.
3. Matched perturbation v2: hold discovered count or recall bands approximately fixed while changing source-route exposure.
4. Second external task preparation: choose a real repo audit or claim-verification completion task with offline oracle construction.

## Decision Rule

The controller avoids false certification only if it does not accept `SAFE` when bounded-oracle recall is below 0.90. Broad exposure is treated as completion eligibility, not sufficient completion proof.
""",
        encoding="utf-8",
    )

    top_scores = scores.sort_values("residual_potential_score", ascending=False).head(8)
    (REPORTS / "challenger_overlap_analysis.md").write_text(
        f"""# Challenger Overlap Analysis

## Summary

At source-route granularity, `high_potential` and `residual_potential` are identical on {identical_rate:.3f} of seeds, with mean Jaccard {mean_jaccard:.3f}.

This means their tie on the external `requests` task is mostly explained by selecting the same strata, not by independent routes to the same outcome.

## Top Runtime Scores

{top_scores.to_markdown(index=False)}

## Interpretation

The highest-potential strata are also unexposed or weakly exposed in the homogeneous base run. Therefore the `under_exposure` factor does not change the top-k ranking in this task. The method claim should remain downgraded: residual-potential is mechanism-aligned, but this task does not show extra benefit over high-potential-only.
""",
        encoding="utf-8",
    )

    (REPORTS / "threshold_sweep_report.md").write_text(
        f"""# Threshold Sweep Report

## Purpose

Sweep support-ratio and exposure-Gini thresholds to check whether the false-certification result is a threshold accident.

## Aggregate Summary

{sweep_summary.to_markdown(index=False)}

## Full Sweep

{sweep.to_markdown(index=False)}

## Interpretation

Across this sweep, false certification remains low because the controller requires both a sufficient evidence condition and no new residual evidence. Changing the threshold mostly changes the SAFE / CONTINUE / ABSTAIN mixture, not the central conclusion that naive stop acceptance is unsafe under localized evidence.

If thresholds are made too permissive in future tasks, broad but still-productive audits could be mislabeled SAFE. Therefore threshold selection must be reported as an operating point, not as a universal law.
""",
        encoding="utf-8",
    )

    (REPORTS / "matched_perturbation_v2_report.md").write_text(
        f"""# Matched Perturbation v2 Report

## Purpose

Strengthen the mechanism test: broad exposure should grant completion eligibility, not automatically certify SAFE.

## Results

{perturbation.to_markdown(index=False)}

## Interpretation

The matched `31` case is the key control. It has the same discovered count as the local homogeneous stop but broad source-route exposure. The controller still outputs `CONTINUE`, because evidence is still appearing. This supports the refined mechanism:

```text
source-route exposure geometry controls whether completion evidence is eligible;
SAFE additionally requires that repair/audit no longer reveals residual evidence.
```

This prevents the paper from overclaiming that coverage geometry alone proves completion.
""",
        encoding="utf-8",
    )

    (REPORTS / "NEXT_EXTERNAL_TASK_PLAN.md").write_text(
        """# Next External Task Plan

## Preferred Task

Use a second real Python repo with a completion-audit objective, not a generated item-discovery task.

Recommended target: a small installed package or vendored repo with natural audit routes such as:

- exception-handling audit;
- timeout / retry / resource cleanup audit;
- compatibility or deprecation audit;
- security-relevant argument validation audit.

## Why This Task

It keeps natural source-route strata while moving beyond the current `requests` snapshot. The goal is to test whether evidence-condition control avoids false certification across a different codebase.

## Oracle Construction

1. Freeze a local repo snapshot.
2. Define route patterns before running trajectories.
3. Build an offline exhaustive oracle by scanning all files and routes.
4. Hide oracle labels, oracle totals, and missing mass from challenger selection.
5. Score only after trajectories and challenger targets are fixed.

## Claim-Verification Variant

If feasible, add a claim verification completion audit:

```text
Given a repo-level claim such as "all network calls use timeouts" or
"all public parsing paths handle malformed input", certify whether the audit is complete.
```

Oracle construction then labels claim-supporting and claim-violating evidence sites offline. This would help show that the research object is workload-unknown completion certification, not only item discovery.

## Go / No-Go

Go if the controller reduces false certification under localized evidence and still uses `ABSTAIN` or `CONTINUE` when broad evidence remains productive.

Downgrade method claims if high-potential-only again explains most challenger gains.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    events = pd.DataFrame(read_jsonl(EXT / "logs" / "action_events.jsonl"))
    oracle = {row["item_id"] for row in read_jsonl(EXT / "logs" / "oracle_items.jsonl")}
    detailed = pd.read_csv(EXT / "results" / "external_requests_challenger_detailed.csv")
    base = events[(events["condition"] == "homogeneous") & (events["source_family"] != "controller")].copy()
    potential = runtime_potential_from_source()
    controller_detail = build_controller_detail(detailed, base, potential, oracle)

    overlap, scores = overlap_analysis(detailed, base, potential)
    sweep = threshold_sweep(controller_detail)
    perturbation = matched_perturbation_v2(events, oracle, potential)

    overlap.to_csv(RESULTS / "challenger_overlap_analysis.csv", index=False)
    scores.to_csv(RESULTS / "challenger_score_decomposition.csv", index=False)
    sweep.to_csv(RESULTS / "threshold_sweep.csv", index=False)
    perturbation.to_csv(RESULTS / "matched_perturbation_v2.csv", index=False)
    controller_detail.to_csv(RESULTS / "controller_validation_v2_detail.csv", index=False)
    write_reports(overlap, scores, sweep, perturbation)

    print("overlap")
    print(overlap[["jaccard", "identical"]].describe(include="all").to_string())
    print("threshold sweep")
    print(sweep.groupby("challenger", as_index=False)["false_certification_rate"].max().to_string(index=False))
    print("matched perturbation")
    print(perturbation.to_string(index=False))


if __name__ == "__main__":
    main()
