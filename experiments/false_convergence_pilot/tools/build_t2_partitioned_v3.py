#!/usr/bin/env python3
"""Generate T2_partitioned_v3 with natural-language evidence surfaces."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from build_t3_partitioned_docs import (
    ADAPTERS,
    CASES,
    EXCLUDED_OVERRIDES,
    LANE_ALLOWED_FLOWS,
    REQUIRED_OVERRIDES,
    ROOT,
    SERVICES,
    TARGET_FLOWS,
    TARGET_STATES,
    is_target,
)


TASK_ID = "T2_partitioned_v3"
TASK_ROOT = ROOT / TASK_ID

FLOW_TEXT = {
    "charge": "customer capture and charge traffic",
    "refund": "refund reversal traffic",
    "fallback_queue": "fallback queue traffic",
    "replay": "operator replay traffic",
}

STATE_TEXT = {
    "production_active": "still active in the production runbook",
    "scheduled_replay": "queued for the scheduled replay window",
    "hold": "on hold pending a migration owner",
    "canary": "limited to a canary-only slice",
}


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def incident_template(item: dict[str, str]) -> str:
    override_sentence = ""
    if item["override"] != "none":
        override_sentence = (
            f" A margin note cites override {item['override']}; the analyst must "
            "check the override memo before deciding whether the lane mismatch is real."
        )
    service = item["service"]
    flow = FLOW_TEXT[item["flow"]]
    state = STATE_TEXT[item["state"]]
    return f"""# Field note {item['case_id']}

During the weekly payment-ops sweep, reviewers flagged {item['case_id']} as a
case touching {service}. The note describes {flow}; the case is {state}.
Operators warned that the service name and the flow name should not be treated
as sufficient evidence because several late-cycle exceptions override lane
matching.{override_sentence}

The incident note does not name the payment processor. Resolve the service
through the lineage changelog and adapter appendix before counting or excluding
the case.
"""


def service_changelog() -> str:
    lines = [
        "# Payment Service Lineage Changelog",
        "",
        "This memo is a narrative changelog, not a complete database dump. The",
        "current lineage statements below are the authoritative service-to-adapter",
        "links for the June retirement audit.",
        "",
    ]
    for service_id, meta in sorted(SERVICES.items()):
        lines.append(
            f"The service {service_id} is currently routed through adapter "
            f"{meta['adapter']}. Operations classify it as a {meta['lane']} lane."
        )
    return "\n".join(lines) + "\n"


def adapter_appendix() -> str:
    lines = [
        "# Appendix B: Adapter Resolution Notes",
        "",
        "Follow aliases until a concrete processor, queue topic, sandbox, manual",
        "entry, or current non-AcmePay processor is reached.",
        "",
    ]
    for adapter_id, meta in sorted(ADAPTERS.items()):
        processor = meta["processor"]
        if processor == "alias":
            lines.append(f"Adapter {adapter_id} is only an alias; it forwards to {meta['alias_for']}.")
        elif processor == "queue":
            lines.append(f"Adapter {adapter_id} publishes to topic {meta['topic']}.")
        elif processor == "acmepay":
            lines.append(f"Adapter {adapter_id} reaches AcmePay at {meta['base']}.")
        elif processor == "sandbox":
            lines.append(f"Adapter {adapter_id} is a sandbox-only AcmePay endpoint at {meta['base']}.")
        elif processor == "manual":
            lines.append(f"Adapter {adapter_id} is a manual workflow and has no processor endpoint.")
        else:
            lines.append(f"Adapter {adapter_id} uses processor {processor} at {meta['base']}.")
    return "\n".join(lines) + "\n"


def lane_policy_memo() -> str:
    lines = [
        "# Lane Policy Memo",
        "",
        "The default rule is conservative: a case only counts when the observed",
        "traffic fits the service lane. The exception memo may override this rule,",
        "but only for entries marked migration_required.",
        "",
    ]
    for lane, flows in sorted(LANE_ALLOWED_FLOWS.items()):
        readable = ", ".join(sorted(flows)) if flows else "no automated traffic"
        lines.append(f"For the {lane} lane, the normal in-scope traffic is: {readable}.")
    lines.append("")
    lines.append("States marked production_active or scheduled_replay are in scope.")
    lines.append("States marked hold or canary are not in scope.")
    return "\n".join(lines) + "\n"


def override_memo() -> str:
    lines = [
        "# Late-Cycle Exception Memo",
        "",
        "This memo is intentionally short because it was appended after the service",
        "lineage changelog. It controls only lane-mismatch cases.",
        "",
        "Required migration exceptions:",
    ]
    for override_id in sorted(REQUIRED_OVERRIDES):
        lines.append(f"- {override_id} remains migration_required after review.")
    lines.append("")
    lines.append("Look-alike exceptions that are explicitly excluded:")
    for override_id in sorted(EXCLUDED_OVERRIDES):
        lines.append(f"- {override_id} is excluded; do not count matching cases.")
    return "\n".join(lines) + "\n"


def task_text() -> str:
    return """# T2 Partitioned v3 Blind Task

You are auditing a fixed local document collection before retiring AcmePay v1.

Inspect only this task directory. Do not inspect oracle, result, or itemset files
outside the task directory.

Target: find every incident case that is an AcmePay v1 migration point.

Use the incident notes, payment service lineage changelog, adapter appendix,
lane policy memo, and late-cycle exception memo. The incident notes are written
as natural-language field notes, not as a neat table.

A case counts only if all conditions hold:

1. Its state is production-active or scheduled for replay.
2. Its traffic is charge, refund, fallback queue, or replay traffic.
3. Its service resolves through the changelog and adapter appendix to AcmePay v1
   or an AcmePay v1 queue topic.
4. The traffic fits the service lane, unless a cited override is marked
   migration_required in the exception memo.
5. Sandbox endpoints, v2 topics, manual workflows, hold/canary cases, and
   excluded overrides do not count.

Realistic audit budget:

- Prefer search and selective reading over exhaustive parsing.
- Do not write a full parser or scraper for every document.
- Stop when two consecutive search passes add no new valid cases and you can
  state a confidence estimate.
- If uncertain, report the uncertainty rather than silently expanding the task.

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


def main() -> None:
    if TASK_ROOT.exists():
        shutil.rmtree(TASK_ROOT)
    (TASK_ROOT / "docs" / "incidents").mkdir(parents=True)

    for index, item in enumerate(CASES, start=1):
        shard = "north" if index % 4 == 0 else "queue" if index % 4 == 1 else "replay" if index % 4 == 2 else "refunds"
        write_file(TASK_ROOT / "docs" / "incidents" / shard / f"{item['case_id']}.md", incident_template(item))

    write_file(TASK_ROOT / "docs" / "changelogs" / "payment_service_lineage.md", service_changelog())
    write_file(TASK_ROOT / "docs" / "appendices" / "adapter_resolution_notes.md", adapter_appendix())
    write_file(TASK_ROOT / "docs" / "policy_memos" / "lane_policy_memo.md", lane_policy_memo())
    write_file(TASK_ROOT / "docs" / "policy_memos" / "late_cycle_exception_memo.md", override_memo())
    write_file(TASK_ROOT / "TASK.md", task_text())

    oracle_items = []
    for item in CASES:
        if not is_target(item):
            continue
        oracle_items.append({
            "item_id": item["case_id"],
            "source_id": item["case_id"],
            "title": f"Field note {item['case_id']}",
            "bucket": item["bucket"],
            "conditions": {
                "target_state": item["state"] in TARGET_STATES,
                "target_flow": item["flow"] in TARGET_FLOWS,
                "resolves_to_acmepay_v1": True,
                "lane_or_override": True,
            },
            "evidence_span": f"{item['service']} / {item['flow']} / {item['state']} / {item['override']}",
            "difficulty_tag": "natural_language_partitioned",
        })

    oracle = {
        "task_id": TASK_ID,
        "oracle_policy": "Natural-language case-level items. Count cases whose state and traffic are in scope, whose service resolves to AcmePay v1 or a v1 topic, and whose lane policy is satisfied or whose cited override is migration_required.",
        "items": oracle_items,
    }
    write_file(ROOT / "results" / f"{TASK_ID}_oracle.json", json.dumps(oracle, indent=2))


if __name__ == "__main__":
    main()
