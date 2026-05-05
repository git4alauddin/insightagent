from unittest.mock import patch

import pytest

from app.services.agent_controller import AgentControllerError, run_agent_query


def test_run_agent_query_executes_calculator_tool() -> None:
    raw_decision = """
    {
      "tool_name": "calculator",
      "tool_input": {"expression": "25 * 18"},
      "reason": "The user asked for arithmetic calculation."
    }
    """

    with patch("app.services.agent_controller.generate_answer", return_value=raw_decision):
        result = run_agent_query("What is 25 * 18?")

    assert result.tool_used == "calculator"
    assert result.tool_status == "success"
    assert result.status == "success"
    assert result.tool_output_summary == "450"


def test_run_agent_query_handles_none_tool_path() -> None:
    raw_decision = """
    {
      "tool_name": "none",
      "tool_input": {},
      "reason": "No external tool is needed."
    }
    """

    with patch("app.services.agent_controller.generate_answer", return_value=raw_decision):
        result = run_agent_query("Explain what CSV means.")

    assert result.tool_used == "none"
    assert result.tool_status == "skipped"
    assert result.status == "success"


def test_run_agent_query_raises_on_invalid_tool_decision_json() -> None:
    with patch("app.services.agent_controller.generate_answer", return_value="{bad json"):
        with pytest.raises(AgentControllerError, match="not valid JSON"):
            run_agent_query("What is 25 * 18?")


def test_run_agent_query_raises_when_tool_execution_fails() -> None:
    raw_decision = """
    {
      "tool_name": "calculator",
      "tool_input": {"expression": "10 / 0"},
      "reason": "Arithmetic calculation requested."
    }
    """

    with patch("app.services.agent_controller.generate_answer", return_value=raw_decision):
        with pytest.raises(AgentControllerError, match="Tool execution failed"):
            run_agent_query("What is 10 / 0?")

