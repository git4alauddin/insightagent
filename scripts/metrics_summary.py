import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


class MetricsSummaryError(Exception):
    pass


def extract_json_payload(line: str) -> dict[str, Any] | None:
    stripped_line = line.strip()
    if not stripped_line:
        return None

    json_start = stripped_line.find("{")
    if json_start == -1:
        return None

    try:
        payload = json.loads(stripped_line[json_start:])
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None
    return payload


def load_log_events(log_path: Path) -> list[dict[str, Any]]:
    if not log_path.exists():
        raise MetricsSummaryError(f"Log file not found: {log_path}")

    events: list[dict[str, Any]] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        payload = extract_json_payload(line)
        if payload is not None:
            events.append(payload)
    return events


def build_metrics_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    request_events = [
        event for event in events if event.get("event") == "request_completed"
    ]
    tool_events = [
        event for event in events if event.get("event") == "agent_tool_completed"
    ]

    return {
        "requests": build_request_summary(request_events),
        "agent_tools": build_agent_tool_summary(tool_events),
    }


def build_request_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(events)
    successful = sum(1 for event in events if is_successful_request(event))
    failed = total - successful
    latencies = [
        float(event["latency_ms"])
        for event in events
        if is_number(event.get("latency_ms"))
    ]

    endpoint_counts = Counter(
        str(event.get("endpoint") or event.get("path") or "unknown")
        for event in events
    )
    error_categories = Counter(
        str(event["error_category"])
        for event in events
        if event.get("error_category")
    )

    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "success_rate": calculate_rate(successful, total),
        "average_latency_ms": calculate_average(latencies),
        "endpoint_counts": sort_counter(endpoint_counts),
        "error_categories": sort_counter(error_categories),
    }


def build_agent_tool_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(events)
    successful = sum(
        1 for event in events if str(event.get("tool_status")) == "success"
    )
    tool_usage = Counter(str(event.get("tool_used") or "unknown") for event in events)
    tool_status_counts = Counter(
        str(event.get("tool_status") or "unknown") for event in events
    )

    return {
        "total": total,
        "successful": successful,
        "failed": total - successful,
        "success_rate": calculate_rate(successful, total),
        "tool_usage": sort_counter(tool_usage),
        "tool_status_counts": sort_counter(tool_status_counts),
    }


def is_successful_request(event: dict[str, Any]) -> bool:
    status = event.get("status")
    if status == "success":
        return True
    if status == "failed":
        return False

    status_code = event.get("status_code")
    if is_number(status_code):
        return int(status_code) < 400
    return False


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def calculate_rate(count: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round(count / total, 4)


def calculate_average(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def sort_counter(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def save_summary(summary: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize InsightAgent structured JSON logs."
    )
    parser.add_argument(
        "--logs",
        required=True,
        type=Path,
        help="Path to a log file containing structured JSON log lines.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path where the summary JSON should be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    events = load_log_events(args.logs)
    summary = build_metrics_summary(events)
    summary_json = json.dumps(summary, indent=2)

    if args.output:
        save_summary(summary, args.output)

    print(summary_json)


if __name__ == "__main__":
    main()
