from typing import TypedDict

from app.prompts.structured_v2 import build_structured_prompt
from app.schemas.structured import StructuredLLMResponse
from app.services.llm_service import (
    LLMServiceError,
    LLMUsage,
    combine_usage,
    generate_answer,
    generate_answer_with_usage,
)
from app.services.structured_parser import (
    StructuredOutputParseError,
    parse_structured_response,
)


MAX_STRUCTURED_OUTPUT_ATTEMPTS = 2


class StructuredLLMServiceError(Exception):
    pass


class StructuredLLMResult(TypedDict):
    response: StructuredLLMResponse
    usage: LLMUsage


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


def generate_structured_answer_with_usage(message: str) -> StructuredLLMResult:
    prompt = build_structured_prompt(message)
    usages: list[LLMUsage] = []

    for _ in range(MAX_STRUCTURED_OUTPUT_ATTEMPTS):
        try:
            result = generate_answer_with_usage(prompt)
        except LLMServiceError as exc:
            raise StructuredLLMServiceError(str(exc)) from exc

        usages.append(result["usage"])

        try:
            return {
                "response": parse_structured_response(result["answer"]),
                "usage": combine_usage(usages),
            }
        except StructuredOutputParseError:
            continue

    return {
        "response": build_structured_fallback_response(),
        "usage": combine_usage(usages),
    }
