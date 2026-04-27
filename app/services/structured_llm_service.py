from app.prompts.structured_v2 import build_structured_prompt
from app.schemas.structured import StructuredLLMResponse
from app.services.llm_service import LLMServiceError, generate_answer
from app.services.structured_parser import (
    StructuredOutputParseError,
    parse_structured_response,
)


MAX_STRUCTURED_OUTPUT_ATTEMPTS = 2


class StructuredLLMServiceError(Exception):
    pass


def build_structured_fallback_response() -> StructuredLLMResponse:
    return StructuredLLMResponse(
        answer="I could not generate a valid structured response.",
        confidence="low",
        reasoning_summary="The model output failed validation.",
        next_action="Please retry or simplify the question.",
        prompt_version="v2.1",
        status="failed",
    )


def generate_structured_answer(message: str) -> StructuredLLMResponse:
    prompt = build_structured_prompt(message)

    for _ in range(MAX_STRUCTURED_OUTPUT_ATTEMPTS):
        try:
            raw_output = generate_answer(prompt)
        except LLMServiceError as exc:
            raise StructuredLLMServiceError(str(exc)) from exc

        try:
            return parse_structured_response(raw_output)
        except StructuredOutputParseError:
            continue

    return build_structured_fallback_response()
