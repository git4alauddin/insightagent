import pytest

from app.services.tool_decision_parser import ToolDecisionParseError, parse_tool_decision


def test_parse_tool_decision_accepts_valid_json() -> None:
    raw_output = """
    {
      "tool_name": "calculator",
      "tool_input": {"expression": "25 * 18"},
      "reason": "The user asked for arithmetic calculation."
    }
    """

    result = parse_tool_decision(raw_output)

    assert result.tool_name == "calculator"
    assert result.tool_input["expression"] == "25 * 18"


def test_parse_tool_decision_rejects_invalid_json() -> None:
    with pytest.raises(ToolDecisionParseError, match="not valid JSON"):
        parse_tool_decision("{bad json")


def test_parse_tool_decision_rejects_invalid_schema() -> None:
    raw_output = """
    {
      "tool_name": "weather",
      "tool_input": {"city": "Kolkata"},
      "reason": "The user asked for weather."
    }
    """

    with pytest.raises(ToolDecisionParseError, match="expected schema"):
        parse_tool_decision(raw_output)


def test_parse_tool_decision_rejects_blank_reason() -> None:
    raw_output = """
    {
      "tool_name": "none",
      "tool_input": {},
      "reason": "   "
    }
    """

    with pytest.raises(ToolDecisionParseError, match="expected schema"):
        parse_tool_decision(raw_output)

