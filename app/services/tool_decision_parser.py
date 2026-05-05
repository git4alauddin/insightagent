import json

from pydantic import ValidationError

from app.schemas.agent import ToolDecision


class ToolDecisionParseError(Exception):
    pass


def parse_tool_decision(raw_output: str) -> ToolDecision:
    try:
        parsed_output = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise ToolDecisionParseError("Tool decision output was not valid JSON.") from exc

    try:
        return ToolDecision.model_validate(parsed_output)
    except ValidationError as exc:
        raise ToolDecisionParseError("Tool decision output did not match the expected schema.") from exc

