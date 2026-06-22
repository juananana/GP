from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INVENTORY_DIR = ROOT / "configs" / "task_inventories"


def load_task_inventory(name_or_path: str | Path) -> dict[str, Any]:
    path = Path(name_or_path)
    if not path.suffix:
        path = DEFAULT_INVENTORY_DIR / f"{path}.yaml"
    if not path.is_absolute():
        path = ROOT / path
    text = path.read_text(encoding="utf-8")
    inventory = yaml.safe_load(text) or {}
    inventory["_path"] = str(path)
    inventory["_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return inventory


def source_files(inventory: dict[str, Any]) -> list[str]:
    return [str(item["source_path"]) for item in inventory.get("sources", [])]


def source_family_map(inventory: dict[str, Any]) -> dict[str, str]:
    return {str(item["source_path"]): str(item["source_family"]) for item in inventory.get("sources", [])}


def route_patterns(inventory: dict[str, Any]) -> dict[str, re.Pattern[str]]:
    patterns: dict[str, re.Pattern[str]] = {}
    for route in inventory.get("routes", []):
        if route.get("route_type") != "regex":
            raise ValueError(f"unsupported route_type for {route.get('route_id')}: {route.get('route_type')}")
        patterns[str(route["route_id"])] = re.compile(str(route["definition"]))
    return patterns

