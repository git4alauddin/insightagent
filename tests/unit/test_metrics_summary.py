import json
from pathlib import Path

import pytest

from scripts.metrics_summary import (
    MetricsSummaryError,
    build_metrics_summary,
    extract_json_payload,
    load_log_events,
    save_summary,
)


def test_extract_json_payload_reads_plain_json_line() -> None:
    payload = extract_json_payload('{"event": "request_completed", "status": "success"}')

    assert payload == {"event": "request_completed", "status": "success"}


def test_extract_json_payload_reads_prefixed_log_line() -> None:
    payload = extract_json_payload(
        '2026-05-12 INFO app.api.middleware - {"event": "request_completed"}'
    )

    assert payload == {"event": "request_completed"}


def test_extract_json_payload_ignores_invalid_lines() -> None:
    assert extract_json_payload("INFO app started") is None
    assert extract_json_payload("{not-json}") is None
    assert extract_json_payload('["not", "an", "event"]') is None


def test_load_log_events_reads_json_events_and_skips_noise(tmp_path: Path) -> None:
    log_path = tmp_path / "app.log"
    log_path.write_text(
        "\n".join(
            [
                "server started",
                json.dumps({"event": "request_completed", "status_code": 200}),
                'INFO - {"event": "agent_tool_completed", "tool_used": "calculator"}',
                "{broken-json}",
            ]
        ),
        encoding="utf-8",
    )

    events = load_log_events(log_path)

    assert events == [
        {"event": "request_completed", "status_code": 200},
        {"event": "agent_tool_completed", "tool_used": "calculator"},
    ]


def test_load_log_events_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(MetricsSummaryError, match="Log file not found"):
        load_log_events(tmp_path / "missing.log")


def test_build_metrics_summary_counts_requests_and_tool_usage() -> None:
    events = [
        {
            "event": "request_completed",
            "endpoint": "/health",
            "status_code": 200,
            "status": "success",
            "latency_ms": 10.0,
            "error_category": None,
        },
        {
            "event": "request_completed",
            "endpoint": "/agent/query",
            "status_code": 200,
            "status": "success",
            "latency_ms": 20.0,
            "error_category": None,
        },
        {
            "event": "request_completed",
            "endpoint": "/agent/query",
            "status_code": 401,
            "status": "failed",
            "latency_ms": 30.0,
            "error_category": "AUTH_ERROR",
        },
        {
            "event": "agent_tool_completed",
            "tool_used": "calculator",
            "tool_status": "success",
        },
        {
            "event": "agent_tool_completed",
            "tool_used": "calculator",
            "tool_status": "success",
        },
        {
            "event": "agent_tool_completed",
            "tool_used": "date_time",
            "tool_status": "failed",
        },
    ]

    summary = build_metrics_summary(events)

    assert summary["requests"] == {
        "total": 3,
        "successful": 2,
        "failed": 1,
        "success_rate": 0.6667,
        "average_latency_ms": 20.0,
        "endpoint_counts": {
            "/agent/query": 2,
            "/health": 1,
        },
        "error_categories": {
            "AUTH_ERROR": 1,
        },
    }
    assert summary["agent_tools"] == {
        "total": 3,
        "successful": 2,
        "failed": 1,
        "success_rate": 0.6667,
        "tool_usage": {
            "calculator": 2,
            "date_time": 1,
        },
        "tool_status_counts": {
            "failed": 1,
            "success": 2,
        },
    }
    assert summary["usage"] == {
        "available_events": 0,
        "unavailable_events": 6,
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "estimated_cost_usd": None,
    }


def test_build_metrics_summary_sums_usage_when_available() -> None:
    summary = build_metrics_summary(
        [
            {
                "event": "request_completed",
                "status": "success",
                "input_tokens": 10,
                "output_tokens": 5,
                "total_tokens": 15,
                "estimated_cost_usd": 0.001,
            },
            {
                "event": "request_completed",
                "status": "success",
                "input_tokens": "20",
                "output_tokens": "10",
                "total_tokens": "30",
                "estimated_cost_usd": "0.0025",
            },
            {
                "event": "agent_tool_completed",
                "tool_used": "calculator",
                "tool_status": "success",
            },
        ]
    )

    assert summary["usage"] == {
        "available_events": 2,
        "unavailable_events": 1,
        "input_tokens": 30,
        "output_tokens": 15,
        "total_tokens": 45,
        "estimated_cost_usd": 0.0035,
    }


def test_build_metrics_summary_falls_back_to_status_code_and_unknown_names() -> None:
    summary = build_metrics_summary(
        [
            {"event": "request_completed", "path": "/ready", "status_code": 503},
            {"event": "agent_tool_completed"},
        ]
    )

    assert summary["requests"]["failed"] == 1
    assert summary["requests"]["endpoint_counts"] == {"/ready": 1}
    assert summary["agent_tools"]["failed"] == 1
    assert summary["agent_tools"]["tool_usage"] == {"unknown": 1}
    assert summary["agent_tools"]["tool_status_counts"] == {"unknown": 1}


def test_save_summary_writes_json_file(tmp_path: Path) -> None:
    output_path = tmp_path / "nested" / "summary.json"
    summary = {"requests": {"total": 1}}

    save_summary(summary, output_path)

    assert json.loads(output_path.read_text(encoding="utf-8")) == summary
