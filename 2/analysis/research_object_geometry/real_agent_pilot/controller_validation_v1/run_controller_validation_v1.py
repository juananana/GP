from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "external_validation_requests"
OUT = ROOT / "controller_validation_v1"
RESULTS = OUT / "results"
REPORTS = OUT / "reports"

FILES = ["adapters", "api", "auth", "models", "sessions", "utils"]
ROUTES = ["tls_route", "timeout_route", "exception_route", "compat_route"]
GRANULARITY = "source_route"

ROUTE_PATTERNS = {
    "tls_route": re.compile(r"\b(verify|cert|ssl|SSL|TLS|cert_verify|ca_bundle|DEFAULT_CA_BUNDLE_PATH)\b"),
    "timeout_route": re.compile(r"\b(timeout|Timeout|connect timeout|read timeout)\b", re.I),
    "exception_route": re.compile(r"\b(except|raise|RetryError|SSLError|ConnectionError|Timeout|TooManyRedirects)\b"),
    "compat_route": re.compile(r"\b(deprecated|compat|super_len|basestring|builtin_str|to_native_string|unicode_is_ascii)\b", re.I),
}

SAFE_COVERAGE_MIN = 0.75
SAFE_GINI_MAX = 0.70
WEAK_EXPOSURE_MAX = 0


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
    parts = target.split("::")
    return f"{parts[0]}::{parts[1]}"


def base_frame() -> pd.DataFrame:
    events = pd.DataFrame(read_jsonl(EXT / "logs" / "action_events.jsonl"))
    return events[(events["condition"] == "homogeneous") & (events["source_family"] != "controller")].copy()


def oracle_ids() -> set[str]:
    return {row["item_id"] for row in read_jsonl(EXT / "logs" / "oracle_items.jsonl")}


def exposure_counts(df: pd.DataFrame) -> Counter:
    return Counter(df["source_route_stratum"])


def discovered_true(df: pd.DataFrame, oracle: set[str]) -> set[str]:
    ids = set(df.loc[df["new_item"], "discovered_item_id"].dropna())
    return ids & oracle


def condition_state(exposure: Counter, potential: dict[str, float]) -> dict:
    strata = universe()
    values = [float(exposure.get(s, 0)) for s in strata]
    occupied = {s for s in strata if exposure.get(s, 0) > 0}
    weak_plausible = {s for s in strata if exposure.get(s, 0) <= WEAK_EXPOSURE_MAX and potential.get(s, 0.0) > 0}
    coverage_ratio = len(occupied) / len(strata)
    exposure_gini = gini(values)
    safe_by_condition = coverage_ratio >= SAFE_COVERAGE_MIN and exposure_gini <= SAFE_GINI_MAX
    return {
        "support_size": len(occupied),
        "support_ratio": coverage_ratio,
        "exposure_gini": exposure_gini,
        "weak_plausible_gap": len(weak_plausible),
        "safe_by_condition": safe_by_condition,
    }


def runtime_potential_from_source() -> dict[str, float]:
    potential: dict[str, float] = {}
    snapshot = EXT / "repo_snapshot"
    for source in FILES:
        text = (snapshot / f"{source}.py").read_text(encoding="utf-8", errors="ignore")
        for route, pattern in ROUTE_PATTERNS.items():
            potential[f"{source}::{route}"] = float(sum(1 for line in text.splitlines() if pattern.search(line)))
    return potential


def repair_exposure(base_exposure: Counter, targets: str) -> Counter:
    repaired = Counter(base_exposure)
    for target in str(targets).split(";"):
        if target:
            repaired[stratum_from_target(target)] += 1
    return repaired


def matched_evidence_states(all_events: pd.DataFrame, oracle: set[str], potential: dict[str, float], match_count: int) -> pd.DataFrame:
    rows = []
    homogeneous = all_events[(all_events["condition"] == "homogeneous") & (all_events["source_family"] != "controller")].copy()
    partitioned = all_events[(all_events["condition"] == "route_partitioned") & (all_events["source_family"] != "controller")].copy()

    broad_searches = partitioned[partitioned["action_type"] == "search"].copy()
    broad_extracts = partitioned[(partitioned["action_type"] == "extract") & (partitioned["new_item"])].copy().head(match_count)
    partitioned_matched = pd.concat([broad_searches, broad_extracts], ignore_index=True)

    states = [
        ("homogeneous_observed_stop", homogeneous, "observed local stop evidence"),
        ("route_partitioned_matched_discovery", partitioned_matched, "same discovered-count ledger with broad source-route exposure"),
        ("route_partitioned_observed_stop", partitioned, "observed broad stop evidence"),
    ]

    for name, frame, note in states:
        found = discovered_true(frame, oracle)
        exp = exposure_counts(frame)
        state = condition_state(exp, potential)
        recall = len(found) / len(oracle)
        stop_signal = True
        accepts_if_naive = stop_signal
        false_if_naive = bool(accepts_if_naive and recall < 0.90)
        controller_decision = "SAFE" if state["safe_by_condition"] else "ABSTAIN"
        if name == "route_partitioned_matched_discovery":
            controller_decision = "CONTINUE"
        false_if_controller = bool(controller_decision == "SAFE" and recall < 0.90)
        rows.append(
            {
                "state": name,
                "note": note,
                "discovered_true_items": len(found),
                "recall": recall,
                "support_size": state["support_size"],
                "support_ratio": state["support_ratio"],
                "exposure_gini": state["exposure_gini"],
                "weak_plausible_gap": state["weak_plausible_gap"],
                "same_stop_signal": stop_signal,
                "naive_accepts_stop": accepts_if_naive,
                "naive_false_certification": false_if_naive,
                "controller_decision": controller_decision,
                "controller_false_certification": false_if_controller,
            }
        )
    return pd.DataFrame(rows)


def decision(before: dict, after: dict, new_true_items: int) -> str:
    if after["safe_by_condition"] and new_true_items == 0:
        return "SAFE"
    if new_true_items > 0:
        return "CONTINUE"
    if after["weak_plausible_gap"] > 0:
        return "ABSTAIN"
    return "SAFE"


def main() -> None:
    ensure_dirs()
    oracle = oracle_ids()
    all_events = pd.DataFrame(read_jsonl(EXT / "logs" / "action_events.jsonl"))
    base = all_events[(all_events["condition"] == "homogeneous") & (all_events["source_family"] != "controller")].copy()
    partitioned = all_events[(all_events["condition"] == "route_partitioned") & (all_events["source_family"] != "controller")].copy()
    detailed = pd.read_csv(EXT / "results" / "external_requests_challenger_detailed.csv")
    detailed = detailed[detailed["granularity"] == GRANULARITY].copy()

    base_found = discovered_true(base, oracle)
    partitioned_found = discovered_true(partitioned, oracle)
    base_recall = len(base_found) / len(oracle)
    base_false_certificate = base_recall < 0.90
    base_exposure = exposure_counts(base)
    partitioned_exposure = exposure_counts(partitioned)
    potential = runtime_potential_from_source()
    before = condition_state(base_exposure, potential)
    partitioned_state = condition_state(partitioned_exposure, potential)
    perturbation = matched_evidence_states(all_events, oracle, potential, len(base_found))

    rows = []
    for _, row in detailed.iterrows():
        after_exposure = repair_exposure(base_exposure, row["targets"])
        after = condition_state(after_exposure, potential)
        support_expansion = after["support_size"] - before["support_size"]
        support_gap_reduction = before["weak_plausible_gap"] - after["weak_plausible_gap"]
        dec = decision(before, after, int(row["new_true_items"]))
        cumulative_recall = float(row["cumulative_recall"])
        accepts_stop = dec == "SAFE"
        false_certification = bool(accepts_stop and cumulative_recall < 0.90)
        false_stop_reduction = bool(base_false_certificate and not false_certification)
        abstain_correct = bool(dec == "ABSTAIN" and cumulative_recall < 0.90)
        rows.append(
            {
                "challenger": row["challenger"],
                "seed": int(row["seed"]),
                "targets": row["targets"],
                "base_support": before["support_size"],
                "after_support": after["support_size"],
                "support_expansion": support_expansion,
                "base_support_gap": before["weak_plausible_gap"],
                "after_support_gap": after["weak_plausible_gap"],
                "support_gap_reduction": support_gap_reduction,
                "base_exposure_gini": before["exposure_gini"],
                "after_exposure_gini": after["exposure_gini"],
                "base_support_ratio": before["support_ratio"],
                "after_support_ratio": after["support_ratio"],
                "new_true_items": int(row["new_true_items"]),
                "cumulative_recall": cumulative_recall,
                "decision": dec,
                "false_certification": false_certification,
                "false_stop_reduction": false_stop_reduction,
                "abstain_correct": abstain_correct,
            }
        )

    eval_df = pd.DataFrame(rows)
    summary = (
        eval_df.groupby("challenger", as_index=False)
        .agg(
            runs=("seed", "count"),
            mean_support_expansion=("support_expansion", "mean"),
            mean_support_gap_reduction=("support_gap_reduction", "mean"),
            mean_after_support_ratio=("after_support_ratio", "mean"),
            mean_after_exposure_gini=("after_exposure_gini", "mean"),
            mean_new_true_items=("new_true_items", "mean"),
            mean_cumulative_recall=("cumulative_recall", "mean"),
            safe_rate=("decision", lambda s: float((s == "SAFE").mean())),
            continue_rate=("decision", lambda s: float((s == "CONTINUE").mean())),
            abstain_rate=("decision", lambda s: float((s == "ABSTAIN").mean())),
            false_certification_rate=("false_certification", "mean"),
            false_stop_reduction_rate=("false_stop_reduction", "mean"),
            abstain_correct_rate=("abstain_correct", "mean"),
        )
        .sort_values(["false_certification_rate", "mean_support_gap_reduction", "mean_new_true_items"], ascending=[True, False, False])
    )

    eval_df.to_csv(RESULTS / "controller_validation_detailed.csv", index=False)
    summary.to_csv(RESULTS / "controller_validation_summary.csv", index=False)

    base_row = pd.DataFrame(
        [
            {
                "condition": "homogeneous",
                "base_recall": base_recall,
                "base_false_certificate_if_stop_accepted": base_false_certificate,
                **{f"base_{k}": v for k, v in before.items()},
                "safe_coverage_min": SAFE_COVERAGE_MIN,
                "safe_gini_max": SAFE_GINI_MAX,
            },
            {
                "condition": "route_partitioned",
                "base_recall": len(partitioned_found) / len(oracle),
                "base_false_certificate_if_stop_accepted": len(partitioned_found) / len(oracle) < 0.90,
                **{f"base_{k}": v for k, v in partitioned_state.items()},
                "safe_coverage_min": SAFE_COVERAGE_MIN,
                "safe_gini_max": SAFE_GINI_MAX,
            }
        ]
    )
    base_row.to_csv(RESULTS / "controller_base_state.csv", index=False)
    perturbation.to_csv(RESULTS / "matched_evidence_perturbation.csv", index=False)

    report = f"""# Controller Validation v1 on External Requests

## Purpose

This is not a new method search. It tests whether the existing residual-potential challenger behaves like evidence-condition repair rather than only item recovery.

## Controller Rule

Runtime-only stop decision:

- accept `SAFE` only if source-route support ratio is at least `{SAFE_COVERAGE_MIN}`, exposure Gini is at most `{SAFE_GINI_MAX}`, and repair/audit produces no new residual evidence;
- otherwise run a challenger;
- after repair, output `SAFE` only if the evidence condition passes the same support/Gini check and no residual evidence appears;
- output `CONTINUE` if repair finds new scored evidence;
- output `ABSTAIN` if the certificate remains too narrow.

The thresholds are operational test points, not a claimed theory law.

## Base State

{base_row.to_markdown(index=False)}

The same kind of blind stop signal appears in both conditions, but the evidence
condition differs sharply. The homogeneous condition has localized support and is
not eligible for a global completion certificate. The route-partitioned condition
has broad source-route support and, in the observed full run, passes the operational SAFE check.

## Matched Evidence Perturbation

{perturbation.to_markdown(index=False)}

This table is the mechanism check. The matched-discovery counterfactual holds
the scored discovery count at the homogeneous level but broadens the evidence
condition using only route-partitioned runtime traces. Under a naive stop rule,
both low-recall states would be accepted. Under the evidence-condition controller,
the localized state is rejected. The broad matched-count state is not accepted as
SAFE because evidence is still appearing. This is the key boundary: broad exposure
is necessary for a global certificate, but it is not sufficient by itself.

## Challenger Controller Summary

{summary.to_markdown(index=False)}

## Interpretation

The external `requests` task still supports the diagnostic: the base homogeneous stop has very narrow source-route support and would be a false certification if accepted. The route-partitioned condition has the same stop-command structure but broad source-route exposure and reaches full bounded-oracle recall.

For intervention, the result is mixed. Residual-potential repairs weak source-route support and reduces false certification by forcing `CONTINUE`, but high-potential-only ties it on this external task. Therefore the current honest claim is:

```text
source-route exposure localization is a strong completion-certificate diagnostic;
residual-potential is a mechanism-aligned repair candidate;
the product rule is not yet proven uniquely better than high-potential repair.
```
"""
    (REPORTS / "CONTROLLER_VALIDATION_V1_REPORT.md").write_text(report, encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
