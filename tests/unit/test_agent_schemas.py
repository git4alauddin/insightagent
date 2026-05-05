import pytest
from pydantic import ValidationError

from app.schemas.agent import AgentQueryRequest, AgentQueryResponse, ToolDecision


def test_agent_query_request_accepts_and_trims_message() -> None:
    request = AgentQueryRequest(message="  What is 25 * 18?  ")
    assert request.message == "What is 25 * 18?"


def test_agent_query_request_rejects_blank_message() -> None:
    with pytest.raises(ValidationError):
        AgentQueryRequest(message="   ")


def test_tool_decision_accepts_valid_input() -> None:
    decision = ToolDecision(
        tool_name="calculator",
        tool_input={"expression": "25 * 18"},
        reason="The user asked for arithmetic calculation.",
    )

    assert decision.tool_name == "calculator"
    assert decision.tool_input["expression"] == "25 * 18"


def test_tool_decision_rejects_blank_reason() -> None:
    with pytest.raises(ValidationError):
        ToolDecision(
            tool_name="calculator",
            tool_input={"expression": "25 * 18"},
            reason="   ",
        )


def test_tool_decision_rejects_unknown_tool_name() -> None:
    with pytest.raises(ValidationError):
        ToolDecision(
            tool_name="weather",  # not in ToolName literal
            tool_input={"city": "Kolkata"},
            reason="User asked for weather.",
        )


def test_agent_query_response_accepts_valid_payload() -> None:
    response = AgentQueryResponse(
        answer="25 x 18 = 450.",
        confidence="high",
        tool_used="calculator",
        tool_input={"expression": "25 * 18"},
        tool_output_summary="The calculator returned 450.",
        tool_status="success",
        status="success",
    )

    assert response.tool_used == "calculator"
    assert response.tool_status == "success"


def test_agent_query_response_rejects_blank_answer() -> None:
    with pytest.raises(ValidationError):
        AgentQueryResponse(
            answer="   ",
            confidence="medium",
            tool_used="none",
            tool_input={},
            tool_output_summary="No tool required.",
            tool_status="skipped",
            status="failed",
        )


def test_agent_query_response_rejects_invalid_tool_status() -> None:
    with pytest.raises(ValidationError):
        AgentQueryResponse(
            answer="Done.",
            confidence="low",
            tool_used="none",
            tool_input={},
            tool_output_summary="No tool required.",
            tool_status="done",  # invalid
            status="success",
        )
