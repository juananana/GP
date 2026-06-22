from __future__ import annotations

from collections.abc import Mapping
from typing import Any

try:
    import pandas as pd
except ImportError:  # pragma: no cover - pandas is present in the experiment env
    pd = None  # type: ignore[assignment]


POSTHOC_ORACLE_ONLY_FIELDS = frozenset(
    {
        "oracle_label",
        "oracle_bucket",
        "oracle_total",
        "recall",
        "bounded_oracle_recall",
        "undiscovered_true_item_count",
        "hidden_missing_mass",
        "new_true_items",
        "new_true_item_ids",
        "cumulative_recall",
        "found_true_items",
        "oracle_safe",
        "false_certification",
        "false_certification_rate",
        "safe_coverage",
    }
)

RUNTIME_DECISION_FIELDS = frozenset(
    {
        "task_id",
        "task",
        "run_id",
        "condition",
        "state_type",
        "seed",
        "budget",
        "policy",
        "challenger",
        "support",
        "gini",
        "source_route_support",
        "source_route_gini",
        "after_support_ratio",
        "after_exposure_gini",
        "geometry_ok",
        "weak_plausible_gap",
        "weak_plausible_gap_after",
        "after_weak_plausible_gap",
        "runtime_residual_items",
        "residual_warning",
        "unresolved_warning",
        "repair_targets",
        "targets",
        "cost",
        "repair_cost",
    }
)


def _as_dict(record: Mapping[str, Any] | Any) -> dict[str, Any]:
    if pd is not None and isinstance(record, pd.Series):
        return record.to_dict()
    if isinstance(record, Mapping):
        return dict(record)
    raise TypeError(f"runtime records must be mappings, got {type(record)!r}")


def forbidden_runtime_fields(record: Mapping[str, Any] | Any) -> set[str]:
    values = _as_dict(record)
    return set(values) & set(POSTHOC_ORACLE_ONLY_FIELDS)


def assert_runtime_record(record: Mapping[str, Any] | Any, *, context: str = "runtime decision") -> None:
    forbidden = sorted(forbidden_runtime_fields(record))
    if forbidden:
        joined = ", ".join(forbidden)
        raise ValueError(f"{context} received post-hoc/oracle-only field(s): {joined}")


def runtime_decision_view(record: Mapping[str, Any] | Any, *, context: str = "runtime decision") -> dict[str, Any]:
    values = _as_dict(record)
    view = {key: values[key] for key in values.keys() & RUNTIME_DECISION_FIELDS}
    assert_runtime_record(view, context=context)
    return view


def require_runtime_residual(record: Mapping[str, Any] | Any, *, context: str) -> float:
    values = _as_dict(record)
    if "runtime_residual_items" not in values:
        raise KeyError(f"runtime_residual_items is required for runtime decision in {context}")
    return float(values["runtime_residual_items"])

