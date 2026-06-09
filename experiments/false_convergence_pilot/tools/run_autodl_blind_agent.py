#!/usr/bin/env python3
"""Run an AutoDL.Art blind discovery agent over a bounded task directory.

The runner intentionally reads only the task directory. It builds a compact
line-numbered context packet from selected source files and calls the Responses
API. Oracle, score, incidence, and summarizer-output files are not read.
"""

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
        with urllib.request.urlopen(request, timeout=600) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"AutoDL API HTTP {exc.code}: {body}") from exc


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()


def line_numbered_file(task_root: Path, rel_path: str, max_lines: int) -> str:
    path = task_root / rel_path
    lines = read_lines(path)
    rendered = [f"### {rel_path}"]
    for line_no, text in enumerate(lines[:max_lines], start=1):
        rendered.append(f"{line_no:04d}: {text}")
    if len(lines) > max_lines:
        rendered.append(f"... truncated after {max_lines} lines; original line count={len(lines)}")
    return "\n".join(rendered)


def build_context(task_root: Path, files: list[str], max_lines_per_file: int) -> str:
    chunks: list[str] = []
    missing: list[str] = []
    for rel_path in files:
        path = task_root / rel_path
        if not path.exists() or not path.is_file():
            missing.append(rel_path)
            continue
        chunks.append(line_numbered_file(task_root, rel_path, max_lines_per_file))
    if missing:
        chunks.append("### Missing requested files\n" + "\n".join(missing))
    return "\n\n".join(chunks)


def prompt_for(
    *,
    run_id: str,
    task_md: str,
    context: str,
    task_root_label: str,
    search_budget: int,
) -> str:
    return f"""You are an independent blind discovery agent.

Allowed context: {task_root_label}
Forbidden context: oracle files, score summaries, smoke itemsets, incidence logs,
protocol outputs, summarizer outputs, and any experiment results outside the
allowed task directory.

Task instructions:

{task_md}

Search budget and self-stop condition:
- Inspect the provided line-numbered task context.
- Return exact line-level items only.
- Stop when you have exhausted the provided context and cannot justify adding
  more concrete line items without guessing.
- Prefer high recall, but do not include unrelated keyword hits.
- Use this exact run_id: {run_id}
- Hard cap: return at most {search_budget} items.

Return JSON only with this shape:

{{
  "run_id": "{run_id}",
  "self_reported_completion": true,
  "self_reported_confidence": 0.0,
  "items": [
    {{"file_path": "repo/src/requests/adapters.py", "line": 321}}
  ]
}}

Line-numbered context:

{context}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-root", required=True, type=Path)
    parser.add_argument("--task-root-label", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--files", nargs="+", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--raw-out", required=True, type=Path)
    parser.add_argument("--cost-out", required=True, type=Path)
    parser.add_argument("--search-budget", type=int, default=400)
    parser.add_argument("--max-lines-per-file", type=int, default=3500)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--api-key-env", default="AUTODL_ART_API_KEY")
    args = parser.parse_args()

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"Missing API key env var: {args.api_key_env}")

    task_md = (args.task_root / "TASK.md").read_text(encoding="utf-8")
    context = build_context(args.task_root, args.files, args.max_lines_per_file)
    input_text = prompt_for(
        run_id=args.run_id,
        task_md=task_md,
        context=context,
        task_root_label=args.task_root_label,
        search_budget=args.search_budget,
    )

    started_at = now_iso()
    start_time = time.perf_counter()
    response = call_api(args.endpoint, args.model, api_key, input_text)
    wall_clock = time.perf_counter() - start_time
    ended_at = now_iso()

    output_text = extract_output_text(response)
    run = normalize_run(parse_json_text(output_text), args.run_id)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.raw_out.parent.mkdir(parents=True, exist_ok=True)
    args.cost_out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    args.raw_out.write_text(json.dumps(response, indent=2, ensure_ascii=False), encoding="utf-8")
    args.cost_out.write_text(json.dumps({
        "run_id": args.run_id,
        "started_at": started_at,
        "ended_at": ended_at,
        "model_name": args.model,
        "prompt_variant": "autodl_blind_line_numbered_context",
        "input_tokens": response.get("usage", {}).get("input_tokens"),
        "output_tokens": response.get("usage", {}).get("output_tokens"),
        "tool_calls": None,
        "wall_clock_seconds": wall_clock,
        "stop_reason": "api_response",
        "notes": {
            "task_root": str(args.task_root),
            "files": args.files,
            "search_budget": args.search_budget,
            "max_lines_per_file": args.max_lines_per_file,
        },
    }, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
