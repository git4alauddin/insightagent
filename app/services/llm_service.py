from openai import APIConnectionError, APITimeoutError, OpenAI, OpenAIError

from app.config import settings


class LLMServiceError(Exception):
    pass


def generate_answer_from_messages(messages: list[dict[str, str]]) -> str:
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

    if not answer:
        raise LLMServiceError("LLM returned an empty response.")

    return answer


def generate_answer(message: str) -> str:
    return generate_answer_from_messages([{"role": "user", "content": message}])
