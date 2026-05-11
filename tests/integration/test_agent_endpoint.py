from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.agent_controller import AgentControllerError


client = TestClient(app)
client.headers.update({"x-api-key": "test-api-key"})


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


def test_agent_query_returns_controlled_error_when_controller_fails() -> None:
    with patch(
        "app.api.routes_agent.run_agent_query",
        side_effect=AgentControllerError("Tool decision output was not valid JSON."),
    ):
        response = client.post("/agent/query", json={"message": "What is 25 * 18?"})

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "error": {
                "code": "AGENT_CONTROLLER_ERROR",
                "message": "Tool decision output was not valid JSON.",
            }
        }
    }
