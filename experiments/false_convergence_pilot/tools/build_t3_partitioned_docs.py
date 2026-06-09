#!/usr/bin/env python3
"""Generate T3 partitioned docs for strict Line A validation."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "T3_partitioned_policy_docs"
TASK_ROOT = ROOT / TASK_ID

TARGET_STATES = {"production_active", "scheduled_replay"}
TARGET_FLOWS = {"charge", "refund", "fallback_queue", "replay"}

SERVICES = {
    "svc-orbit-charge": {"adapter": "orbit_bridge", "lane": "charge"},
    "svc-nova-charge": {"adapter": "nova_gateway", "lane": "charge"},
    "svc-eu-refund": {"adapter": "eu_refund_shadow", "lane": "refund"},
    "svc-ap-refund": {"adapter": "ap_refund_shadow", "lane": "refund"},
    "svc-fallback-charge": {"adapter": "charge_fallback_topic", "lane": "queue"},
    "svc-fallback-refund": {"adapter": "refund_fallback_topic", "lane": "queue"},
    "svc-ledger-replay": {"adapter": "ledger_replay_eu", "lane": "replay"},
    "svc-atlas-checkout": {"adapter": "stripe_current", "lane": "charge"},
    "svc-recheck": {"adapter": "current_recheck", "lane": "queue"},
    "svc-sandbox-pay": {"adapter": "sandbox_acmepay", "lane": "charge"},
    "svc-manual-adjust": {"adapter": "manual_review", "lane": "manual"},
}

ADAPTERS = {
    "stripe_current": {"processor": "stripe", "base": "https://pay.example.local/v2"},
    "orbit_bridge": {"processor": "alias", "alias_for": "acmepay_v1_tenant_orbit"},
    "nova_gateway": {"processor": "alias", "alias_for": "tenant_nova_rollover"},
    "tenant_nova_rollover": {"processor": "alias", "alias_for": "acmepay_v1_tenant_nova"},
    "eu_refund_shadow": {"processor": "alias", "alias_for": "region_eu_legacy"},
    "ap_refund_shadow": {"processor": "alias", "alias_for": "region_ap_legacy"},
    "ledger_replay_eu": {"processor": "alias", "alias_for": "region_eu_legacy"},
    "charge_fallback_topic": {"processor": "queue", "topic": "acmepay.v1.charge"},
    "refund_fallback_topic": {"processor": "queue", "topic": "acmepay.v1.refund"},
    "current_recheck": {"processor": "queue", "topic": "acmepay.v2.recheck"},
    "sandbox_acmepay": {"processor": "sandbox", "base": "https://sandbox.acmepay.local/v1"},
    "manual_review": {"processor": "manual", "base": "n/a"},
    "acmepay_v1_tenant_orbit": {"processor": "acmepay", "base": "https://orbit.acmepay.local/v1"},
    "acmepay_v1_tenant_nova": {"processor": "acmepay", "base": "https://nova.acmepay.local/v1"},
    "region_eu_legacy": {"processor": "acmepay", "base": "https://eu.acmepay.local/v1"},
    "region_ap_legacy": {"processor": "acmepay", "base": "https://ap.acmepay.local/v1"},
}

LANE_ALLOWED_FLOWS = {
    "charge": {"charge"},
    "refund": {"refund"},
    "queue": {"fallback_queue", "replay"},
    "replay": {"replay"},
    "manual": set(),
}

REQUIRED_OVERRIDES = {
    "XOV-101",
    "XOV-102",
    "XOV-103",
    "XOV-104",
    "XOV-105",
    "XOV-106",
    "XOV-107",
    "XOV-108",
}

EXCLUDED_OVERRIDES = {
    "XOV-201",
    "XOV-202",
    "XOV-203",
    "XOV-204",
    "XOV-205",
    "XOV-206",
    "XOV-207",
    "XOV-208",
}


def case(case_id: str, service: str, flow: str, state: str, bucket: str, override: str = "none") -> dict[str, str]:
    return {
        "case_id": case_id,
        "service": service,
        "flow": flow,
        "state": state,
        "bucket": bucket,
        "override": override,
    }


CASES = [
    case("CASE-001", "svc-orbit-charge", "charge", "production_active", "direct_lane"),
    case("CASE-002", "svc-nova-charge", "charge", "production_active", "alias_chain"),
    case("CASE-003", "svc-eu-refund", "refund", "production_active", "alias_chain"),
    case("CASE-004", "svc-ap-refund", "refund", "production_active", "alias_chain"),
    case("CASE-005", "svc-fallback-charge", "fallback_queue", "production_active", "queue_topic"),
    case("CASE-006", "svc-fallback-refund", "fallback_queue", "production_active", "queue_topic"),
    case("CASE-007", "svc-ledger-replay", "replay", "scheduled_replay", "alias_chain"),
    case("CASE-008", "svc-orbit-charge", "charge", "scheduled_replay", "direct_lane"),
    case("CASE-009", "svc-nova-charge", "charge", "scheduled_replay", "alias_chain"),
    case("CASE-010", "svc-eu-refund", "refund", "scheduled_replay", "alias_chain"),
    case("CASE-011", "svc-fallback-refund", "replay", "scheduled_replay", "queue_topic"),
    case("CASE-012", "svc-fallback-charge", "replay", "scheduled_replay", "queue_topic"),
    case("CASE-013", "svc-atlas-checkout", "charge", "production_active", "non_target"),
    case("CASE-014", "svc-recheck", "fallback_queue", "production_active", "non_target"),
    case("CASE-015", "svc-sandbox-pay", "charge", "production_active", "non_target"),
    case("CASE-016", "svc-orbit-charge", "charge", "hold", "non_target"),
    case("CASE-017", "svc-eu-refund", "refund", "canary", "non_target"),
    case("CASE-018", "svc-manual-adjust", "charge", "production_active", "non_target"),
    case("CASE-019", "svc-nova-charge", "refund", "production_active", "override_required", "XOV-101"),
    case("CASE-020", "svc-orbit-charge", "refund", "production_active", "override_required", "XOV-102"),
    case("CASE-021", "svc-eu-refund", "charge", "production_active", "override_required", "XOV-103"),
    case("CASE-022", "svc-ap-refund", "charge", "scheduled_replay", "override_required", "XOV-104"),
    case("CASE-023", "svc-ledger-replay", "refund", "production_active", "override_required", "XOV-105"),
    case("CASE-024", "svc-fallback-charge", "refund", "production_active", "override_required", "XOV-106"),
    case("CASE-025", "svc-fallback-refund", "charge", "production_active", "override_required", "XOV-107"),
    case("CASE-026", "svc-nova-charge", "fallback_queue", "production_active", "override_required", "XOV-108"),
    case("CASE-027", "svc-nova-charge", "refund", "production_active", "override_excluded", "XOV-201"),
    case("CASE-028", "svc-orbit-charge", "refund", "production_active", "override_excluded", "XOV-202"),
    case("CASE-029", "svc-eu-refund", "charge", "production_active", "override_excluded", "XOV-203"),
    case("CASE-030", "svc-ap-refund", "charge", "scheduled_replay", "override_excluded", "XOV-204"),
    case("CASE-031", "svc-ledger-replay", "refund", "production_active", "override_excluded", "XOV-205"),
    case("CASE-032", "svc-fallback-charge", "refund", "production_active", "override_excluded", "XOV-206"),
    case("CASE-033", "svc-fallback-refund", "charge", "production_active", "override_excluded", "XOV-207"),
    case("CASE-034", "svc-nova-charge", "fallback_queue", "production_active", "override_excluded", "XOV-208"),
    case("CASE-035", "svc-orbit-charge", "charge", "production_active", "direct_lane"),
    case("CASE-036", "svc-nova-charge", "charge", "production_active", "alias_chain"),
    case("CASE-037", "svc-eu-refund", "refund", "production_active", "alias_chain"),
    case("CASE-038", "svc-ap-refund", "refund", "production_active", "alias_chain"),
    case("CASE-039", "svc-fallback-charge", "fallback_queue", "production_active", "queue_topic"),
    case("CASE-040", "svc-fallback-refund", "fallback_queue", "production_active", "queue_topic"),
    case("CASE-041", "svc-ledger-replay", "replay", "scheduled_replay", "alias_chain"),
    case("CASE-042", "svc-orbit-charge", "charge", "scheduled_replay", "direct_lane"),
    case("CASE-043", "svc-nova-charge", "charge", "scheduled_replay", "alias_chain"),
    case("CASE-044", "svc-eu-refund", "refund", "scheduled_replay", "alias_chain"),
    case("CASE-045", "svc-fallback-refund", "replay", "scheduled_replay", "queue_topic"),
    case("CASE-046", "svc-fallback-charge", "replay", "scheduled_replay", "queue_topic"),
    case("CASE-047", "svc-atlas-checkout", "refund", "production_active", "non_target"),
    case("CASE-048", "svc-recheck", "replay", "scheduled_replay", "non_target"),
    case("CASE-049", "svc-sandbox-pay", "refund", "production_active", "non_target"),
    case("CASE-050", "svc-manual-adjust", "replay", "scheduled_replay", "non_target"),
    case("CASE-051", "svc-orbit-charge", "charge", "production_active", "direct_lane"),
    case("CASE-052", "svc-nova-charge", "charge", "production_active", "alias_chain"),
    case("CASE-053", "svc-eu-refund", "refund", "production_active", "alias_chain"),
    case("CASE-054", "svc-ap-refund", "refund", "production_active", "alias_chain"),
    case("CASE-055", "svc-fallback-charge", "fallback_queue", "production_active", "queue_topic"),
    case("CASE-056", "svc-fallback-refund", "fallback_queue", "production_active", "queue_topic"),
    case("CASE-057", "svc-ledger-replay", "replay", "production_active", "alias_chain"),
    case("CASE-058", "svc-orbit-charge", "refund", "scheduled_replay", "override_required", "XOV-102"),
    case("CASE-059", "svc-eu-refund", "charge", "scheduled_replay", "override_required", "XOV-103"),
    case("CASE-060", "svc-fallback-refund", "charge", "scheduled_replay", "override_required", "XOV-107"),
    case("CASE-061", "svc-nova-charge", "charge", "production_active", "alias_chain"),
    case("CASE-062", "svc-ap-refund", "refund", "scheduled_replay", "alias_chain"),
    case("CASE-063", "svc-fallback-charge", "replay", "production_active", "queue_topic"),
    case("CASE-064", "svc-recheck", "fallback_queue", "scheduled_replay", "non_target"),
]


def resolves_to_acmepay_v1(adapter: str) -> bool:
    seen: set[str] = set()
    current = adapter
    while current not in seen:
        seen.add(current)
        entry = ADAPTERS[current]
        processor = entry["processor"]
        if processor == "acmepay" and str(entry.get("base", "")).endswith("/v1"):
            return True
        if processor == "queue" and str(entry.get("topic", "")).startswith("acmepay.v1."):
            return True
        if processor == "alias":
            current = entry["alias_for"]
            continue
        return False
    return False


def is_target(item: dict[str, str]) -> bool:
    if item["state"] not in TARGET_STATES:
        return False
    if item["flow"] not in TARGET_FLOWS:
        return False
    service = SERVICES[item["service"]]
    if not resolves_to_acmepay_v1(service["adapter"]):
        return False
    if item["override"] in EXCLUDED_OVERRIDES:
        return False
    if item["flow"] in LANE_ALLOWED_FLOWS[service["lane"]]:
        return True
    return item["override"] in REQUIRED_OVERRIDES


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    if TASK_ROOT.exists():
        shutil.rmtree(TASK_ROOT)
    (TASK_ROOT / "docs" / "cases").mkdir(parents=True)

    service_lines = ["# Service Catalog", ""]
    for service_id, meta in sorted(SERVICES.items()):
        service_lines.append(
            f"- service_id: {service_id}; adapter_id: {meta['adapter']}; lane: {meta['lane']}"
        )
    write_file(TASK_ROOT / "docs" / "catalog" / "service_catalog.md", "\n".join(service_lines) + "\n")

    adapter_lines = ["# Adapter Registry", ""]
    for adapter_id, meta in sorted(ADAPTERS.items()):
        detail = ", ".join(f"{key}={value}" for key, value in meta.items())
        adapter_lines.append(f"- adapter_id: {adapter_id}; {detail}")
    write_file(TASK_ROOT / "docs" / "registry" / "adapter_registry.md", "\n".join(adapter_lines) + "\n")

    lane_lines = [
        "# Lane Policy",
        "",
        "A case normally counts only when the case flow is allowed for the service lane.",
        "",
    ]
    for lane, flows in sorted(LANE_ALLOWED_FLOWS.items()):
        lane_lines.append(f"- lane: {lane}; allowed_flows: {', '.join(sorted(flows)) or 'none'}")
    write_file(TASK_ROOT / "docs" / "policies" / "lane_policy.md", "\n".join(lane_lines) + "\n")

    override_lines = [
        "# Exception Overrides",
        "",
        "Only overrides with disposition=migration_required make a lane-mismatch case count.",
        "",
    ]
    for override_id in sorted(REQUIRED_OVERRIDES):
        override_lines.append(f"- override_id: {override_id}; disposition=migration_required")
    for override_id in sorted(EXCLUDED_OVERRIDES):
        override_lines.append(f"- override_id: {override_id}; disposition=excluded")
    write_file(TASK_ROOT / "docs" / "policies" / "exception_overrides.md", "\n".join(override_lines) + "\n")

    for item in CASES:
        note = "standard lane case"
        if item["bucket"] == "override_required":
            note = "lane mismatch; exception override decides whether it counts"
        if item["bucket"] == "override_excluded":
            note = "lane mismatch; similar to required overrides but explicitly excluded"
        text = f"""# {item['case_id']} Partitioned Operations Case

case_id: {item['case_id']}
service_id: {item['service']}
flow: {item['flow']}
state: {item['state']}
override_id: {item['override']}

Audit note: {note}.

Resolution requires checking the service catalog, adapter registry, lane policy,
and exception overrides. Do not decide from this case file alone.
"""
        write_file(TASK_ROOT / "docs" / "cases" / f"{item['case_id']}.md", text)

    task = """# T3 Partitioned Policy Docs Blind Task

You are auditing a fixed local document collection before retiring AcmePay v1.

Inspect only this task directory. Do not inspect oracle, result, or itemset files
outside the task directory.

Target: find every case in `docs/cases/` that is an AcmePay v1 migration point.

A case is a migration point only if all conditions hold:

1. The state is `production_active` or `scheduled_replay`.
2. The flow is one of `charge`, `refund`, `fallback_queue`, or `replay`.
3. The service resolves through `docs/catalog/service_catalog.md` and
   `docs/registry/adapter_registry.md` to AcmePay v1.
4. The case satisfies `docs/policies/lane_policy.md`, unless its
   `override_id` is listed as `disposition=migration_required` in
   `docs/policies/exception_overrides.md`.
5. Overrides listed as `disposition=excluded`, sandbox services, v2 topics,
   manual workflows, hold states, and canary states are excluded.

Important: some true cases look like lane mismatches. Some false cases look
almost identical but have excluded overrides. You must verify the override
disposition rather than relying on service or flow names.

For each item, output:

```json
{
  "source_id": "CASE-001",
  "item_id": "CASE-001",
  "evidence_span": "short exact evidence",
  "matched_conditions": ["state", "flow", "service_resolution", "lane_or_override"]
}
```
"""
    write_file(TASK_ROOT / "TASK.md", task)

    oracle_items = []
    for item in CASES:
        if not is_target(item):
            continue
        oracle_items.append({
            "item_id": item["case_id"],
            "source_id": item["case_id"],
            "title": f"{item['case_id']} Partitioned Operations Case",
            "bucket": item["bucket"],
            "conditions": {
                "target_state": item["state"] in TARGET_STATES,
                "target_flow": item["flow"] in TARGET_FLOWS,
                "resolves_to_acmepay_v1": True,
                "lane_or_override": True,
            },
            "evidence_span": f"{item['service']} / {item['flow']} / {item['state']} / {item['override']}",
            "difficulty_tag": "partitioned_multi_source",
        })

    oracle = {
        "task_id": TASK_ID,
        "oracle_policy": "Case-level items. A case is counted when state and flow are in scope, service resolves to AcmePay v1, and lane policy is satisfied or a migration_required override applies. Excluded overrides, sandbox, v2, manual, hold, and canary cases are excluded.",
        "items": oracle_items,
    }
    write_file(ROOT / "results" / f"{TASK_ID}_oracle.json", json.dumps(oracle, indent=2))


if __name__ == "__main__":
    main()
