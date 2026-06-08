#!/usr/bin/env python3
"""Generate a closed-world document-search task for Line A validation."""

from __future__ import annotations

import json
import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


SERVICES = {
    "svc-atlas-checkout": "stripe_current",
    "svc-orbit-charge": "orbit_bridge",
    "svc-nova-charge": "nova_gateway",
    "svc-eu-refund": "eu_refund_shadow",
    "svc-ap-refund": "ap_refund_shadow",
    "svc-ledger-replay": "ledger_replay_eu",
    "svc-fallback-charge": "charge_fallback_topic",
    "svc-fallback-refund": "refund_fallback_topic",
    "svc-recheck": "current_recheck",
    "svc-sandbox-pay": "sandbox_acmepay",
    "svc-west-invoice": "stripe_current",
    "svc-legacy-adjust": "manual_review",
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

TARGET_FLOWS = {"charge", "refund", "fallback_queue", "replay"}
TARGET_STATES = {"production_active", "scheduled_replay"}


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


def case(case_id: str, service: str, flow: str, state: str, section: str, note: str) -> dict[str, str]:
    return {
        "case_id": case_id,
        "service": service,
        "flow": flow,
        "state": state,
        "section": section,
        "note": note,
    }


CASES = [
    case("CASE-001", "svc-orbit-charge", "charge", "production_active", "north", "tenant is inferred from service catalog"),
    case("CASE-002", "svc-nova-charge", "charge", "production_active", "north", "adapter resolves through a rollover alias"),
    case("CASE-003", "svc-eu-refund", "refund", "production_active", "west", "refund path is region based"),
    case("CASE-004", "svc-ap-refund", "refund", "production_active", "east", "refund path is region based"),
    case("CASE-005", "svc-fallback-charge", "fallback_queue", "production_active", "queues", "topic is resolved by queue adapter"),
    case("CASE-006", "svc-fallback-refund", "fallback_queue", "production_active", "queues", "topic is resolved by queue adapter"),
    case("CASE-007", "svc-ledger-replay", "replay", "scheduled_replay", "replay", "replay uses regional legacy shadow"),
    case("CASE-008", "svc-orbit-charge", "charge", "scheduled_replay", "replay", "late retry path"),
    case("CASE-009", "svc-nova-charge", "charge", "scheduled_replay", "replay", "late retry path"),
    case("CASE-010", "svc-eu-refund", "refund", "scheduled_replay", "replay", "manual replay pending"),
    case("CASE-011", "svc-fallback-refund", "replay", "scheduled_replay", "replay", "queue replay pending"),
    case("CASE-012", "svc-fallback-charge", "replay", "scheduled_replay", "replay", "queue replay pending"),
    case("CASE-013", "svc-atlas-checkout", "charge", "production_active", "north", "current stripe path"),
    case("CASE-014", "svc-recheck", "fallback_queue", "production_active", "queues", "acmepay v2 recheck is not legacy v1"),
    case("CASE-015", "svc-sandbox-pay", "charge", "production_active", "sandbox", "sandbox v1 should be excluded"),
    case("CASE-016", "svc-orbit-charge", "charge", "hold", "north", "held rollout should be excluded"),
    case("CASE-017", "svc-eu-refund", "refund", "canary", "west", "canary should be excluded"),
    case("CASE-018", "svc-west-invoice", "invoice", "production_active", "west", "non-payment flow"),
    case("CASE-019", "svc-legacy-adjust", "manual_adjustment", "production_active", "ops", "manual workflow"),
    case("CASE-020", "svc-nova-charge", "invoice", "production_active", "north", "legacy adapter but wrong flow"),
    case("CASE-021", "svc-ap-refund", "refund", "production_active", "east", "same service, different source section"),
    case("CASE-022", "svc-orbit-charge", "charge", "production_active", "north", "same service, another region batch"),
    case("CASE-023", "svc-fallback-charge", "fallback_queue", "production_active", "queues", "retry topic through fallback adapter"),
    case("CASE-024", "svc-fallback-refund", "fallback_queue", "production_active", "queues", "retry topic through fallback adapter"),
    case("CASE-025", "svc-ledger-replay", "replay", "scheduled_replay", "replay", "ledger batch replay"),
    case("CASE-026", "svc-recheck", "replay", "scheduled_replay", "replay", "current v2 replay"),
    case("CASE-027", "svc-sandbox-pay", "replay", "scheduled_replay", "sandbox", "sandbox replay"),
    case("CASE-028", "svc-atlas-checkout", "refund", "production_active", "west", "stripe refund"),
    case("CASE-029", "svc-nova-charge", "charge", "production_active", "north", "rollover alias in catalog"),
    case("CASE-030", "svc-eu-refund", "refund", "production_active", "west", "shadow refund path"),
    case("CASE-031", "svc-ap-refund", "refund", "scheduled_replay", "east", "scheduled regional replay"),
    case("CASE-032", "svc-orbit-charge", "charge", "production_active", "north", "tenant checkout charge"),
    case("CASE-033", "svc-fallback-refund", "fallback_queue", "hold", "queues", "held queue should be excluded"),
    case("CASE-034", "svc-fallback-charge", "fallback_queue", "canary", "queues", "canary queue should be excluded"),
    case("CASE-035", "svc-ledger-replay", "audit", "scheduled_replay", "replay", "wrong flow"),
    case("CASE-036", "svc-eu-refund", "refund", "production_active", "west", "manual refund batch"),
    case("CASE-037", "svc-ap-refund", "refund", "production_active", "east", "manual refund batch"),
    case("CASE-038", "svc-nova-charge", "charge", "scheduled_replay", "north", "scheduled charge retry"),
    case("CASE-039", "svc-orbit-charge", "charge", "scheduled_replay", "north", "scheduled charge retry"),
    case("CASE-040", "svc-fallback-charge", "fallback_queue", "production_active", "queues", "charge queue batch"),
    case("CASE-041", "svc-fallback-refund", "fallback_queue", "production_active", "queues", "refund queue batch"),
    case("CASE-042", "svc-recheck", "fallback_queue", "production_active", "queues", "v2 topic distractor"),
    case("CASE-043", "svc-atlas-checkout", "charge", "scheduled_replay", "north", "stripe scheduled retry"),
    case("CASE-044", "svc-sandbox-pay", "charge", "hold", "sandbox", "sandbox and held"),
    case("CASE-045", "svc-legacy-adjust", "replay", "scheduled_replay", "ops", "manual replay, no adapter"),
    case("CASE-046", "svc-ledger-replay", "replay", "production_active", "replay", "active ledger replay"),
    case("CASE-047", "svc-nova-charge", "refund", "production_active", "north", "adapter is legacy; flow is refund but service is charge pipeline"),
    case("CASE-048", "svc-orbit-charge", "refund", "production_active", "north", "adapter is legacy; flow is refund but service is charge pipeline"),
]

EXTRA_V2_CASES = [
    case("CASE-049", "svc-nova-charge", "refund", "production_active", "north", "boundary: charge-named service with refund flow"),
    case("CASE-050", "svc-orbit-charge", "refund", "scheduled_replay", "north", "boundary: charge-named service with scheduled refund"),
    case("CASE-051", "svc-eu-refund", "charge", "production_active", "west", "boundary: refund-named service with charge flow"),
    case("CASE-052", "svc-ap-refund", "charge", "scheduled_replay", "east", "boundary: refund-named service with scheduled charge"),
    case("CASE-053", "svc-ledger-replay", "refund", "production_active", "replay", "boundary: replay service with refund flow"),
    case("CASE-054", "svc-fallback-charge", "refund", "production_active", "queues", "boundary: charge fallback adapter with refund flow"),
    case("CASE-055", "svc-fallback-refund", "charge", "production_active", "queues", "boundary: refund fallback adapter with charge flow"),
    case("CASE-056", "svc-nova-charge", "fallback_queue", "production_active", "queues", "boundary: tenant adapter with queue flow"),
    case("CASE-057", "svc-atlas-checkout", "fallback_queue", "production_active", "queues", "stripe queue distractor"),
    case("CASE-058", "svc-recheck", "refund", "production_active", "queues", "v2 topic distractor with target-looking flow"),
    case("CASE-059", "svc-sandbox-pay", "refund", "production_active", "sandbox", "sandbox distractor with target-looking flow"),
    case("CASE-060", "svc-legacy-adjust", "charge", "production_active", "ops", "manual workflow distractor with target-looking flow"),
]


def is_target(item: dict[str, str]) -> bool:
    if item["state"] not in TARGET_STATES:
        return False
    if item["flow"] not in TARGET_FLOWS:
        return False
    if item["service"] == "svc-sandbox-pay":
        return False
    return resolves_to_acmepay_v1(SERVICES[item["service"]])


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=["v1", "v2"], default="v1")
    args = parser.parse_args()

    task_id = "T2_policy_docs" if args.variant == "v1" else "T2_policy_docs_v2"
    task_root = ROOT / task_id
    cases = CASES if args.variant == "v1" else CASES + EXTRA_V2_CASES

    if task_root.exists():
        shutil.rmtree(task_root)
    (task_root / "docs" / "cases").mkdir(parents=True)

    registry_lines = ["# Adapter Registry", ""]
    for name, entry in sorted(ADAPTERS.items()):
        detail = ", ".join(f"{key}={value}" for key, value in entry.items())
        registry_lines.append(f"- adapter_id: {name}; {detail}")
    write_file(task_root / "docs" / "registry" / "adapter_registry.md", "\n".join(registry_lines) + "\n")

    catalog_lines = ["# Service Catalog", ""]
    for service, adapter in sorted(SERVICES.items()):
        catalog_lines.append(f"- service_id: {service}; adapter_id: {adapter}")
    write_file(task_root / "docs" / "registry" / "service_catalog.md", "\n".join(catalog_lines) + "\n")

    for item in cases:
        text = f"""# {item['case_id']} Payment Operations Note

case_id: {item['case_id']}
service_id: {item['service']}
flow: {item['flow']}
state: {item['state']}
source_section: {item['section']}

Operator note: {item['note']}.

Audit instruction: resolve the service_id through the service catalog and adapter
registry before deciding whether this case is an AcmePay v1 migration point.
"""
        write_file(task_root / "docs" / "cases" / f"{item['case_id']}.md", text)

    task = """# T2 Policy Docs Blind Task

You are auditing a fixed local document collection before retiring AcmePay v1.

Inspect only this task directory. Do not inspect oracle, result, or itemset files
outside the task directory.

Target: find every case in `docs/cases/` that is an AcmePay v1 migration point.

A case is a migration point only if all conditions hold:

1. The case state is `production_active` or `scheduled_replay`.
2. The flow is one of `charge`, `refund`, `fallback_queue`, or `replay`.
3. The case service resolves through `docs/registry/service_catalog.md` and
   `docs/registry/adapter_registry.md` to AcmePay v1.
4. Sandbox AcmePay entries, v2 topics, canary states, hold states, manual-only
   workflows, and wrong-flow cases are excluded.

Important: some cases do not mention AcmePay directly. You must follow aliases
in the adapter registry until they resolve.

For each item, output:

```json
{
  "source_id": "CASE-001",
  "item_id": "CASE-001",
  "evidence_span": "short exact evidence",
  "matched_conditions": ["state", "flow", "service_resolution"]
}
```
"""
    write_file(task_root / "TASK.md", task)

    oracle_items = []
    for item in cases:
        if not is_target(item):
            continue
        oracle_items.append({
            "item_id": item["case_id"],
            "source_id": item["case_id"],
            "title": f"{item['case_id']} Payment Operations Note",
            "bucket": "alias_resolution" if ADAPTERS[SERVICES[item["service"]]]["processor"] == "alias" else "queue_resolution",
            "conditions": {
                "target_state": item["state"] in TARGET_STATES,
                "target_flow": item["flow"] in TARGET_FLOWS,
                "resolves_to_acmepay_v1": True,
            },
            "evidence_span": f"{item['service']} / {item['flow']} / {item['state']}",
            "source_region": item["section"],
            "difficulty_tag": "multi_doc_resolution",
        })

    oracle = {
        "task_id": task_id,
        "oracle_policy": "Case-level items. A case is counted if its state and flow are in scope and its service resolves through the catalog and adapter registry to AcmePay v1. Sandbox, v2, hold, canary, manual-only, and wrong-flow cases are excluded.",
        "items": oracle_items,
    }
    write_file(ROOT / f"{task_id}_oracle.json", json.dumps(oracle, indent=2))


if __name__ == "__main__":
    main()
