#!/usr/bin/env python3
"""Run an AutoDL.Art Responses API summarizer over a G3 aggregation packet."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_ENDPOINT = "https://www.autodl.art/api/v1/responses"
DEFAULT_MODEL = "gpt-5.3-codex"


POLICY_PROMPTS = {
    "standard": """You are aggregating final reports from three blind agents.

Produce one concise final answer containing the items that are sufficiently
supported by the reports. Prefer high precision. If an item is reported by only
one agent and the other reports do not corroborate it, include it only if the
packet itself gives enough evidence to treat it as reliable.

Return JSON only with this shape:

{
  "run_id": "<run_id>",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [
    {"file_path": "repo/src/click/core.py", "line": 1359}
  ],
  "uncertain_or_dropped_singletons": []
}
""",
    "union_preserving": """You are aggregating final reports from three blind agents.

Your goal is to preserve recall from the reports. Include every unique reported
item unless it is explicitly malformed, duplicated under another spelling, or
contradicted by the packet itself. Do not drop an item merely because only one
agent reported it. Mark singleton items separately so they can be audited later.
The packet contains line-level bullet items. If any valid line-level bullet
items appear in the packet, returning an empty items list is invalid.

Return JSON only with this shape:

{
  "run_id": "<run_id>",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [
    {"file_path": "repo/src/click/core.py", "line": 1359}
  ],
  "singleton_items_preserved": [],
  "malformed_or_contradicted_items_dropped": []
}
""",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def extract_output_text(response: dict[str, Any]) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    chunks: list[str] = []
    for output in response.get("output", []):
        for content in output.get("content", []):
            if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                chunks.append(content["text"])
    if chunks:
        return "\n".join(chunks)
    raise ValueError("Could not find output_text in API response")


def parse_json_text(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def normalize_item(item: Any) -> dict[str, Any]:
    if isinstance(item, dict) and "file_path" in item and "line" in item:
        return {
            "file_path": str(item["file_path"]).replace("\\", "/"),
            "line": int(item["line"]),
        }
    if isinstance(item, str) and ":" in item:
        path, line = item.rsplit(":", 1)
        return {"file_path": path.replace("\\", "/"), "line": int(line)}
    raise ValueError(f"Unsupported item format: {item!r}")


def normalize_run(run: dict[str, Any], run_id: str) -> dict[str, Any]:
    run["run_id"] = run_id
    run["self_reported_completion"] = bool(run.get("self_reported_completion", True))
    run["self_reported_confidence"] = float(run.get("self_reported_confidence", 0.0))
    run["items"] = [normalize_item(item) for item in run.get("items", [])]
    return run


def call_api(endpoint: str, model: str, api_key: str, input_text: str) -> dict[str, Any]:
    payload = json.dumps({
        "model": model,
        "input": input_text,
    }).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"AutoDL API HTTP {exc.code}: {body}") from exc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--policy", required=True, choices=sorted(POLICY_PROMPTS))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--raw-out", required=True, type=Path)
    parser.add_argument("--cost-out", required=True, type=Path)
    parser.add_argument("--task-id", default="T4_real_repo_click_deprecation")
    parser.add_argument("--oracle-size", type=int, default=149)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--api-key-env", default="AUTODL_ART_API_KEY")
    args = parser.parse_args()

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"Missing API key env var: {args.api_key_env}")

    packet = args.packet.read_text(encoding="utf-8")
    input_text = (
        f"{POLICY_PROMPTS[args.policy]}\n\n"
        f"Use this exact run_id: {args.run_id}\n\n"
        "Aggregation packet:\n\n"
        f"{packet}"
    )
    started_at = now_iso()
    start_time = time.perf_counter()
    response = call_api(args.endpoint, args.model, api_key, input_text)
    wall_clock = time.perf_counter() - start_time
    ended_at = now_iso()

    output_text = extract_output_text(response)
    run = normalize_run(parse_json_text(output_text), args.run_id)
    if (
        args.policy == "union_preserving"
        and not run["items"]
        and re.search(r"^-\s+repo/.+?:\d+\s*$", packet, flags=re.MULTILINE)
    ):
        raise ValueError(
            "Invalid union-preserving summarizer output: packet has line-level "
            "items but model returned an empty items list."
        )
    wrapped = {
        "task_id": args.task_id,
        "oracle_size": args.oracle_size,
        "runs": [run],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.raw_out.parent.mkdir(parents=True, exist_ok=True)
    args.cost_out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(wrapped, indent=2, ensure_ascii=False), encoding="utf-8")
    args.raw_out.write_text(json.dumps(response, indent=2, ensure_ascii=False), encoding="utf-8")
    args.cost_out.write_text(json.dumps({
        "run_id": args.run_id,
        "task_id": args.task_id,
        "started_at": started_at,
        "ended_at": ended_at,
        "model_name": args.model,
        "prompt_variant": f"autodl_{args.policy}",
        "input_tokens": response.get("usage", {}).get("input_tokens"),
        "output_tokens": response.get("usage", {}).get("output_tokens"),
        "tool_calls": None,
        "wall_clock_seconds": wall_clock,
        "stop_reason": "api_response",
        "notes": None,
    }, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
