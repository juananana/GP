from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[4]
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"
CONFIG_DIR = ROOT / "configs"
DEFAULT_CONFIG = CONFIG_DIR / "full_200seed.yaml"


def load_experiment_config(path: str | Path | None = None) -> dict[str, Any]:
    config_path = Path(path or os.environ.get("EVIDENCE_CONFIG", DEFAULT_CONFIG))
    if not config_path.is_absolute():
        config_path = ROOT / config_path
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    config["_config_path"] = str(config_path)
    return config


def thresholds(config: dict[str, Any]) -> dict[str, float]:
    values = config.get("thresholds", {})
    support = values["tau_support"]
    gini = values["tau_gini"]
    if isinstance(support, list):
        support = 0.75 if 0.75 in support else support[0]
    if isinstance(gini, list):
        gini = 0.70 if 0.70 in gini else gini[0]
    return {
        "tau_support": float(support),
        "tau_gini": float(gini),
        "eval_recall": float(values["eval_only_recall_threshold"]),
    }


def seeds(config: dict[str, Any], key: str = "validation") -> list[int]:
    value = config.get("seeds", {}).get(key, [])
    if isinstance(value, int):
        return list(range(value))
    return [int(v) for v in value]


def seed_count(config: dict[str, Any], key: str = "validation") -> int:
    return len(seeds(config, key))


def task_config(config: dict[str, Any], task: str) -> dict[str, Any]:
    return dict(config.get("tasks", {}).get(task, {}))


def output_path(config: dict[str, Any], key: str) -> Path:
    value = config.get("outputs", {}).get(key)
    if value is None:
        raise KeyError(f"missing outputs.{key} in config")
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def oracle_path(config: dict[str, Any], key: str) -> Path:
    value = config.get("oracle_paths", {}).get(key)
    if value is None:
        raise KeyError(f"missing oracle_paths.{key} in config")
    path = Path(value)
    return path if path.is_absolute() else ROOT / path
