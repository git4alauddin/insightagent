from openai import OpenAI

from app.config import settings


class LLMServiceError(Exception):
    pass


def generate_answer(message: str) -> str:
    if not settings.llm_api_key:
        raise LLMServiceError("LLM API key is not configured.")

    client = OpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout=settings.llm_timeout_seconds,
    )

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "user", "content": message},
        ],
    )

    answer = response.choices[0].message.content

    if not answer:
        raise LLMServiceError("LLM returned an empty response.")

    return answer
