from typing import TypedDict

from openai import APIConnectionError, APITimeoutError, OpenAI, OpenAIError

from app.config import settings


class LLMServiceError(Exception):
    pass


class LLMUsage(TypedDict):
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    estimated_cost_usd: float | None


class LLMResult(TypedDict):
    answer: str
    usage: LLMUsage


def combine_usage(usages: list[LLMUsage]) -> LLMUsage:
    return {
        "input_tokens": _sum_usage_field(usages, "input_tokens"),
        "output_tokens": _sum_usage_field(usages, "output_tokens"),
        "total_tokens": _sum_usage_field(usages, "total_tokens"),
        "estimated_cost_usd": _sum_usage_field(usages, "estimated_cost_usd"),
    }


def _sum_usage_field(usages: list[LLMUsage], field_name: str) -> int | float | None:
    values = [
        usage[field_name]
        for usage in usages
        if usage.get(field_name) is not None
    ]
    if not values:
        return None
    return sum(values)


MODEL_PRICING_PER_MILLION_TOKENS = {
    "llama-3.1-8b-instant": {
        "input": 0.05,
        "output": 0.08,
    },
}


def estimate_cost_usd(
    model: str,
    input_tokens: int | None,
    output_tokens: int | None,
) -> float | None:
    pricing = MODEL_PRICING_PER_MILLION_TOKENS.get(model)
    if pricing is None or input_tokens is None or output_tokens is None:
        return None

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return round(input_cost + output_cost, 8)


def extract_usage(response) -> LLMUsage:
    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "prompt_tokens", None)
    output_tokens = getattr(usage, "completion_tokens", None)

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": getattr(usage, "total_tokens", None),
        "estimated_cost_usd": estimate_cost_usd(
            model=settings.llm_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        ),
    }


def generate_answer_result_from_messages(messages: list[dict[str, str]]) -> LLMResult:
    if not settings.llm_api_key:
        raise LLMServiceError("LLM API key is not configured.")

    client = OpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout=settings.llm_timeout_seconds,
    )

    try:
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
        )
    except APITimeoutError as exc:
        raise LLMServiceError("LLM request timed out.") from exc
    except APIConnectionError as exc:
        raise LLMServiceError("LLM provider connection failed.") from exc
    except OpenAIError as exc:
        raise LLMServiceError("LLM provider request failed.") from exc

    answer = response.choices[0].message.content
    usage = extract_usage(response)

    if not answer:
        raise LLMServiceError("LLM returned an empty response.")

    return {
        "answer": answer,
        "usage": usage,
    }


def generate_answer_from_messages(messages: list[dict[str, str]]) -> str:
    return generate_answer_result_from_messages(messages)["answer"]


def generate_answer_with_usage(message: str) -> LLMResult:
    return generate_answer_result_from_messages([{"role": "user", "content": message}])


def generate_answer(message: str) -> str:
    return generate_answer_from_messages([{"role": "user", "content": message}])
