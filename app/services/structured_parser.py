import json

from pydantic import ValidationError

from app.schemas.structured import StructuredLLMResponse


class StructuredOutputParseError(Exception):
    pass


def parse_structured_response(raw_output: str) -> StructuredLLMResponse:
    try:
        parsed_output = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise StructuredOutputParseError("LLM output was not valid JSON.") from exc

    try:
        return StructuredLLMResponse.model_validate(parsed_output)
    except ValidationError as exc:
        raise StructuredOutputParseError("LLM output did not match the expected schema.") from exc
