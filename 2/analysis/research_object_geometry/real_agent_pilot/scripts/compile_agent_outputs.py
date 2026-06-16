from __future__ import annotations

import json
import os
import re
from pathlib import Path


ROOT = Path(os.environ.get("PILOT_ROOT", Path(__file__).resolve().parents[4]))
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"
RAW = PILOT / "logs" / "agent_outputs.json"
ACTION_OUT = PILOT / "logs" / "action_events.jsonl"
ORACLE_OUT = PILOT / "logs" / "oracle_items.jsonl"


def parse_numeric_id(value: object) -> int:
    text = str(value or "0")
    matches = re.findall(r"\d+", text)
    return int(matches[-1]) if matches else 0


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"missing {RAW}")
    data = json.loads(RAW.read_text(encoding="utf-8"))
    action_events = []
    oracle_items = {}
    task_id = data.get("task_id", "T_doc_dynamic_workflow_smoke")
    condition = data.get("condition", "route_partitioned_smoke")
    for agent in data["agents"]:
        agent_id = agent["agent_id"]
        run_id = agent.get("run_id", f"{task_id}_{condition}_{agent_id}")
        for event in agent.get("action_events", []):
            event = dict(event)
            event["round_id"] = parse_numeric_id(event.get("round_id", 0))
            event["event_id"] = parse_numeric_id(event.get("event_id", 0))
            event.setdefault("task_id", task_id)
            event.setdefault("repo_id", "local_docs")
            event.setdefault("run_id", run_id)
            event.setdefault("condition", condition)
            event.setdefault("agent_id", agent_id)
            event.setdefault("timestamp", "")
            event.setdefault("tool_name", "manual_read")
            event.setdefault("self_reported_completion", None)
            event.setdefault("self_reported_confidence", None)
            event.setdefault("stop_reason", None)
            event.setdefault("token_or_cost", None)
            event.setdefault("notes", "")
            event["source_route_stratum"] = f"{event.get('source_family', 'unknown')}::{event.get('search_route', 'unknown')}"
            action_events.append(event)
        for item in agent.get("discovered_items", []):
            item_id = item["item_id"]
            oracle_items[item_id] = {
                "task_id": task_id,
                "item_id": item_id,
                "oracle_label": True,
                "oracle_bucket": item.get("category", "unknown"),
                "source_path": item.get("source_path", ""),
                "source_family": item.get("source_family", ""),
                "source_route_stratum": f"{item.get('source_family', 'unknown')}::{item.get('search_route', 'unknown')}",
                "reportable": True,
            }
    ACTION_OUT.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in action_events) + "\n", encoding="utf-8")
    ORACLE_OUT.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in oracle_items.values()) + "\n", encoding="utf-8")
    print(f"wrote {len(action_events)} action events")
    print(f"wrote {len(oracle_items)} oracle proxy items")


if __name__ == "__main__":
    main()
