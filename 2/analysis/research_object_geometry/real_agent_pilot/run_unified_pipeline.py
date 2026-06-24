from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from experiment_config import load_experiment_config, thresholds
from task_inventory import load_task_inventory
from unified_posthoc import score_states
from unified_runtime import build_runtime_states, decide_runtime_states, runtime_potential


ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "analysis" / "research_object_geometry" / "real_agent_pilot"
OUT = PILOT / "unified_pipeline"
RESULTS = OUT / "results"

TASKS = {
    "requests": {
        "inventory": "requests",
        "logs": PILOT / "external_validation_requests" / "logs",
        "snapshot": PILOT / "external_validation_requests" / "repo_snapshot",
        "line_prior": False,
    },
    "urllib3": {
        "inventory": "urllib3",
        "logs": PILOT / "external_validation_v2" / "logs",
        "snapshot": PILOT / "external_validation_v2" / "repo_snapshot",
        "line_prior": True,
    },
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows)
    path.write_text(text + "\n", encoding="utf-8")


def export_task(task: str) -> dict[str, pd.DataFrame]:
    info = TASKS[task]
    config = load_experiment_config()
    thresh = thresholds(config)
    inventory = load_task_inventory(str(info["inventory"]))
    events = read_jsonl(Path(info["logs"]) / "action_events.jsonl")
    oracle = read_jsonl(Path(info["logs"]) / "oracle_items.jsonl")
    potential = runtime_potential(Path(info["snapshot"]), inventory, include_line_prior=bool(info["line_prior"]))
    states = build_runtime_states(task=task, events=events, inventory=inventory, potential=potential)
    decisions = decide_runtime_states(states, support_threshold=thresh["tau_support"], gini_threshold=thresh["tau_gini"])
    scores = score_states(
        task=task,
        states=states,
        decisions=decisions,
        events=events,
        oracle_items=oracle,
        recall_threshold=thresh["eval_recall"],
    )
    RESULTS.mkdir(parents=True, exist_ok=True)
    outputs = {
        "runtime_states": states,
        "runtime_decisions": decisions,
        "posthoc_scores": scores,
    }
    frames: dict[str, pd.DataFrame] = {}
    for name, rows in outputs.items():
        write_jsonl(RESULTS / f"{task}_{name}.jsonl", rows)
        frame = pd.DataFrame(rows)
        frame.to_csv(RESULTS / f"{task}_{name}.csv", index=False)
        frames[name] = frame
    return frames


def export_all(tasks: list[str] | None = None) -> None:
    selected = tasks or list(TASKS)
    combined: dict[str, list[pd.DataFrame]] = {
        "runtime_states": [],
        "runtime_decisions": [],
        "posthoc_scores": [],
    }
    for task in selected:
        outputs = export_task(task)
        for name, frame in outputs.items():
            combined[name].append(frame)
    for name, frames in combined.items():
        if frames:
            pd.concat(frames, ignore_index=True).to_csv(RESULTS / f"{name}.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", action="append", choices=sorted(TASKS), help="Task(s) to export. Defaults to all.")
    args = parser.parse_args()
    export_all(args.task)


if __name__ == "__main__":
    main()
