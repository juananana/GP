from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("task_inventory", ROOT / "task_inventory.py")
task_inventory = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(task_inventory)


def test_requests_inventory_is_frozen_and_loadable() -> None:
    inventory = task_inventory.load_task_inventory("requests")
    files = task_inventory.source_files(inventory)
    families = task_inventory.source_family_map(inventory)
    routes = task_inventory.route_patterns(inventory)

    assert inventory["inventory_id"] == "requests_pattern_inventory_v1"
    assert files == ["adapters.py", "api.py", "auth.py", "models.py", "sessions.py", "utils.py"]
    assert families["adapters.py"] == "adapters"
    assert list(routes) == ["tls_route", "timeout_route", "exception_route", "compat_route"]


def test_urllib3_inventory_is_frozen_and_loadable() -> None:
    inventory = task_inventory.load_task_inventory("urllib3")
    files = task_inventory.source_files(inventory)
    families = task_inventory.source_family_map(inventory)
    routes = task_inventory.route_patterns(inventory)

    assert inventory["inventory_id"] == "urllib3_pattern_inventory_v1"
    assert files == [
        "connection.py",
        "connectionpool.py",
        "poolmanager.py",
        "response.py",
        "util/retry.py",
        "util/timeout.py",
    ]
    assert families["util/retry.py"] == "util_retry"
    assert list(routes) == ["timeout_route", "retry_route", "tls_route", "exception_route", "cleanup_route"]

