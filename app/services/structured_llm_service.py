from app.prompts.structured_v2 import build_structured_prompt
from app.schemas.structured import StructuredLLMResponse
from app.services.llm_service import LLMServiceError, generate_answer
from app.services.structured_parser import (
    StructuredOutputParseError,
    parse_structured_response,
)


class StructuredLLMServiceError(Exception):
    pass


def generate_structured_answer(message: str) -> StructuredLLMResponse:
    prompt = build_structured_prompt(message)

    try:
        raw_output = generate_answer(prompt)
    except LLMServiceError as exc:
        raise StructuredLLMServiceError(str(exc)) from exc

    try:
        return parse_structured_response(raw_output)
    except StructuredOutputParseError as exc:
        raise StructuredLLMServiceError(str(exc)) from exc
