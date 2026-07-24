from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any


COST_FIELDS = {"cost", "cost_usd", "estimated_cost_usd", "total_cost_usd"}


REQUIRED_SPAN_FIELDS = {
    "trace_id",
    "span_id",
    "parent_span_id",
    "kind",
    "name",
    "status",
    "attributes",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON on line {line_number}") from error
        if not isinstance(value, dict):
            raise ValueError(f"Line {line_number} must contain a JSON object")
        records.append(value)
    return records


def validate_spans(spans: list[dict[str, Any]]) -> None:
    ids: dict[str, dict[str, Any]] = {}
    for span in spans:
        missing = REQUIRED_SPAN_FIELDS - span.keys()
        if missing:
            raise ValueError(f"Missing span fields: {sorted(missing)}")
        span_id = str(span["span_id"])
        if span_id in ids:
            raise ValueError(f"Duplicate span_id: {span_id}")
        if span["status"] not in {"ok", "error"}:
            raise ValueError(f"Invalid span status: {span['status']}")
        ids[span_id] = span

    for span in spans:
        parent_id = span["parent_span_id"]
        if parent_id is not None:
            if parent_id not in ids:
                raise ValueError(f"Unknown parent_span_id: {parent_id}")
            if ids[parent_id]["trace_id"] != span["trace_id"]:
                raise ValueError("Parent and child must share trace_id")
        if span.get("started_at") and span.get("ended_at"):
            if _parse_time(span["ended_at"]) < _parse_time(span["started_at"]):
                raise ValueError(f"Span ends before it starts: {span['span_id']}")

    for span in spans:
        seen: set[str] = set()
        current = span
        while current["parent_span_id"] is not None:
            parent_id = str(current["parent_span_id"])
            if parent_id in seen:
                raise ValueError(f"Parent cycle detected at: {parent_id}")
            seen.add(parent_id)
            current = ids[parent_id]


def summarize_portable(spans: list[dict[str, Any]]) -> dict[str, Any]:
    validate_spans(spans)
    kind_counts = Counter(str(span["kind"]) for span in spans)
    errors = [span for span in spans if span["status"] == "error"]
    retries = [
        span for span in spans if span["attributes"].get("retry_of") is not None
    ]
    roots = [span for span in spans if span["parent_span_id"] is None]
    timed = [
        span for span in spans if span.get("started_at") and span.get("ended_at")
    ]

    return {
        "trace_count": len({str(span["trace_id"]) for span in spans}),
        "span_count": len(spans),
        "root_spans": len(roots),
        "kind_counts": dict(sorted(kind_counts.items())),
        "error_spans": len(errors),
        "error_span_ids": [str(span["span_id"]) for span in errors],
        "retry_spans": len(retries),
        "handoff_spans": kind_counts.get("handoff", 0),
        "timed_spans": len(timed),
        "root_duration_ms": sum(_duration_ms(span) for span in roots),
        "input_tokens": _sum_attribute(spans, "input_tokens"),
        "output_tokens": _sum_attribute(spans, "output_tokens"),
        "cost_usd": round(_sum_attribute(spans, "cost_usd"), 6),
    }


def summarize_codex(events: list[dict[str, Any]]) -> dict[str, Any]:
    completed_items = [
        event["item"]
        for event in events
        if event.get("type") == "item.completed"
        and isinstance(event.get("item"), dict)
    ]
    commands = [
        item for item in completed_items if item.get("type") == "command_execution"
    ]
    failed_commands = [
        item
        for item in commands
        if item.get("status") == "failed" or item.get("exit_code") not in {0, None}
    ]
    usage_event = next(
        (event for event in reversed(events) if event.get("type") == "turn.completed"),
        None,
    )
    failed_turn = any(event.get("type") == "turn.failed" for event in events)
    thread_event = next(
        (event for event in events if event.get("type") == "thread.started"), {}
    )
    usage = usage_event.get("usage", {}) if usage_event else {}

    return {
        "event_count": len(events),
        "thread_id": thread_event.get("thread_id"),
        "turn_status": "failed" if failed_turn else "completed" if usage_event else "unknown",
        "tool_calls": len(commands),
        "successful_tool_calls": len(commands) - len(failed_commands),
        "failed_tool_calls": len(failed_commands),
        "failed_tool_exit_codes": [item.get("exit_code") for item in failed_commands],
        "agent_messages": sum(
            item.get("type") == "agent_message" for item in completed_items
        ),
        "handoff_events": sum(
            "handoff" in str(event.get("type", "")).lower()
            or "handoff" in str(event.get("item", {}).get("type", "")).lower()
            for event in events
        ),
        "usage": usage,
        "duration_available": any("timestamp" in event for event in events),
        "cost_available": any(_has_numeric_cost(event) for event in events),
    }


def _has_numeric_cost(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            (key.lower() in COST_FIELDS and type(item) in {int, float})
            or _has_numeric_cost(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_has_numeric_cost(item) for item in value)
    return False


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _duration_ms(span: dict[str, Any]) -> int:
    if not span.get("started_at") or not span.get("ended_at"):
        return 0
    delta = _parse_time(span["ended_at"]) - _parse_time(span["started_at"])
    return round(delta.total_seconds() * 1000)


def _sum_attribute(spans: list[dict[str, Any]], key: str) -> float:
    total = 0.0
    for span in spans:
        value = span["attributes"].get(key)
        if isinstance(value, (int, float)):
            total += float(value)
    return total


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Coding Agent trace records")
    subparsers = parser.add_subparsers(dest="command", required=True)
    portable = subparsers.add_parser("portable")
    portable.add_argument("--trace", type=Path, required=True)
    codex = subparsers.add_parser("codex")
    codex.add_argument("--events", type=Path, required=True)
    args = parser.parse_args(argv)

    records = load_jsonl(args.trace if args.command == "portable" else args.events)
    report = (
        summarize_portable(records)
        if args.command == "portable"
        else summarize_codex(records)
    )
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
