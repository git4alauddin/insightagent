import json
import logging
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.agent_controller import AgentControllerError


client = TestClient(app)
client.headers.update({"x-api-key": "test-api-key", "x-request-id": "test-request-id"})


def test_agent_query_returns_success_response() -> None:
    mock_response = {
        "answer": "Tool 'calculator' completed successfully.",
        "confidence": "high",
        "tool_used": "calculator",
        "tool_input": {"expression": "25 * 18"},
        "tool_output_summary": "450",
        "tool_status": "success",
        "status": "success",
    }

    with patch("app.api.routes_agent.run_agent_query", return_value=mock_response):
        response = client.post("/agent/query", json={"message": "What is 25 * 18?"})

    assert response.status_code == 200
    assert response.json() == mock_response


def test_agent_query_logs_tool_trace(caplog) -> None:
    mock_response = {
        "answer": "Tool 'calculator' completed successfully.",
        "confidence": "high",
        "tool_used": "calculator",
        "tool_input": {"expression": "25 * 18"},
        "tool_output_summary": "450",
        "tool_status": "success",
        "status": "success",
    }

    with patch("app.api.routes_agent.run_agent_query", return_value=mock_response):
        with caplog.at_level(logging.INFO, logger="app.api.routes_agent"):
            response = client.post(
                "/agent/query",
                json={"message": "What is 25 * 18?"},
                headers={
                    "x-api-key": "test-api-key",
                    "x-request-id": "agent-log-request-123",
                },
            )

    log_payloads = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "app.api.routes_agent"
    ]
    tool_log = next(
        payload for payload in log_payloads if payload["event"] == "agent_tool_completed"
    )

    assert response.status_code == 200
    assert tool_log["request_id"] == "agent-log-request-123"
    assert tool_log["tool_used"] == "calculator"
    assert tool_log["tool_status"] == "success"
    assert tool_log["agent_status"] == "success"
    assert tool_log["tool_output_summary"] == "450"


def test_agent_query_returns_controlled_error_when_controller_fails() -> None:
    with patch(
        "app.api.routes_agent.run_agent_query",
        side_effect=AgentControllerError("Tool decision output was not valid JSON."),
    ):
        response = client.post("/agent/query", json={"message": "What is 25 * 18?"})

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "AGENT_CONTROLLER_ERROR",
            "message": "Tool decision output was not valid JSON.",
            "request_id": "test-request-id",
        }
    }
