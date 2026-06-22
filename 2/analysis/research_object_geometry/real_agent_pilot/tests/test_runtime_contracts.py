from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("runtime_contracts", ROOT / "runtime_contracts.py")
runtime_contracts = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(runtime_contracts)


def test_runtime_record_rejects_oracle_and_posthoc_fields() -> None:
    record = {
        "support": 0.8,
        "gini": 0.3,
        "runtime_residual_items": 0,
        "recall": 0.92,
        "new_true_items": 3,
    }

    with pytest.raises(ValueError, match="recall"):
        runtime_contracts.assert_runtime_record(record, context="unit test")


def test_runtime_decision_view_strips_posthoc_aggregate_fields() -> None:
    aggregate_row = {
        "task": "requests",
        "support": 0.8,
        "gini": 0.3,
        "runtime_residual_items": 0,
        "recall": 0.92,
        "new_true_items": 3,
        "oracle_total": 10,
    }

    view = runtime_contracts.runtime_decision_view(aggregate_row)

    assert view == {
        "task": "requests",
        "support": 0.8,
        "gini": 0.3,
        "runtime_residual_items": 0,
    }
    runtime_contracts.assert_runtime_record(view)


def test_runtime_residual_is_required_for_runtime_decisions() -> None:
    with pytest.raises(KeyError):
        runtime_contracts.require_runtime_residual({"support": 1.0}, context="unit test")


def test_default_supplement_runner_excludes_legacy_v1_controller() -> None:
    runner = ROOT / "credibility_supplement" / "run_credibility_supplement.py"
    text = runner.read_text(encoding="utf-8")
    active_script_block = text.split("def run_existing_experiments", 1)[1].split("def read_jsonl", 1)[0]

    assert "run_controller_validation_v1.py" not in active_script_block
    assert "run_controller_validation_v2.py" in active_script_block


def test_controller_v2_uses_runtime_contracts() -> None:
    script = ROOT / "controller_validation_v1" / "run_controller_validation_v2.py"
    text = script.read_text(encoding="utf-8")

    assert "runtime_decision_view(row, context=\"controller v2 decision\")" in text
    assert "require_runtime_residual(runtime, context=\"controller v2 decision\")" in text
