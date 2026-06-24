from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

spec = importlib.util.spec_from_file_location("run_unified_pipeline", ROOT / "run_unified_pipeline.py")
run_unified_pipeline = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run_unified_pipeline)


def test_runtime_outputs_do_not_contain_posthoc_fields() -> None:
    outputs = run_unified_pipeline.export_task("requests")
    states = outputs["runtime_states"]
    decisions = outputs["runtime_decisions"]

    forbidden = {"oracle_total", "recall", "new_true_items", "undiscovered_true_item_count"}
    assert forbidden.isdisjoint(states.columns)
    assert forbidden.isdisjoint(decisions.columns)
    assert set(decisions["decision"]).issubset({"SAFE", "CONTINUE", "ABSTAIN"})


def test_unified_requests_scores_match_legacy_condition_metrics() -> None:
    outputs = run_unified_pipeline.export_task("requests")
    scores = outputs["posthoc_scores"].set_index("condition")
    legacy = run_unified_pipeline.pd.read_csv(
        ROOT / "external_validation_requests" / "results" / "external_requests_condition_metrics.csv"
    ).set_index("condition")

    for condition in ["homogeneous", "route_partitioned"]:
        assert abs(float(scores.loc[condition, "recall"]) - float(legacy.loc[condition, "recall"])) < 1e-12
        assert int(scores.loc[condition, "found_true_items"]) == int(legacy.loc[condition, "found_true_items"])
        assert int(scores.loc[condition, "oracle_total"]) == int(legacy.loc[condition, "oracle_total"])


def test_unified_urllib3_scores_match_legacy_condition_metrics() -> None:
    outputs = run_unified_pipeline.export_task("urllib3")
    scores = outputs["posthoc_scores"].set_index("condition")
    legacy = run_unified_pipeline.pd.read_csv(
        ROOT / "external_validation_v2" / "results" / "condition_summary.csv"
    ).set_index("condition")

    for condition in ["homogeneous", "route_partitioned", "extended_audit"]:
        assert abs(float(scores.loc[condition, "recall"]) - float(legacy.loc[condition, "recall"])) < 1e-12
        assert int(scores.loc[condition, "found_true_items"]) == int(legacy.loc[condition, "found_true_items"])
        assert int(scores.loc[condition, "oracle_total"]) == int(legacy.loc[condition, "oracle_total"])

