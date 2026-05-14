from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from httpx import Request
from openai import APITimeoutError

from app.services.llm_service import (
    LLMServiceError,
    estimate_cost_usd,
    generate_answer,
    generate_answer_with_usage,
)


def test_generate_answer_requires_api_key() -> None:
    with patch("app.services.llm_service.settings.llm_api_key", None):
        with pytest.raises(LLMServiceError, match="LLM API key is not configured."):
            generate_answer("Hello")


def test_generate_answer_converts_timeout_error() -> None:
    timeout_error = APITimeoutError(request=Request("POST", "https://example.test/llm"))
    mock_create = Mock(side_effect=timeout_error)
    mock_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=mock_create)
        )
    )

    with patch("app.services.llm_service.settings.llm_api_key", "test-key"):
        with patch("app.services.llm_service.OpenAI", return_value=mock_client):
            with pytest.raises(LLMServiceError, match="LLM request timed out."):
                generate_answer("Hello")


def test_generate_answer_returns_answer_text() -> None:
    mock_response = SimpleNamespace(
        choices=[
            SimpleNamespace(message=SimpleNamespace(content="Hello back"))
        ],
        usage=SimpleNamespace(
            prompt_tokens=11,
            completion_tokens=4,
            total_tokens=15,
        ),
    )

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("app.services.llm_service.settings.llm_api_key", "test-key"):
        with patch("app.services.llm_service.OpenAI", return_value=mock_client):
            result = generate_answer("Hello")

    assert result == "Hello back"


def test_generate_answer_with_usage_returns_answer_and_token_counts() -> None:
    mock_response = SimpleNamespace(
        choices=[
            SimpleNamespace(message=SimpleNamespace(content="Hello back"))
        ],
        usage=SimpleNamespace(
            prompt_tokens=11,
            completion_tokens=4,
            total_tokens=15,
        ),
    )

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("app.services.llm_service.settings.llm_api_key", "test-key"):
        with patch("app.services.llm_service.OpenAI", return_value=mock_client):
            result = generate_answer_with_usage("Hello")

    assert result == {
        "answer": "Hello back",
        "usage": {
            "input_tokens": 11,
            "output_tokens": 4,
            "total_tokens": 15,
            "estimated_cost_usd": 0.00000087,
        },
    }


def test_estimate_cost_usd_uses_known_model_pricing() -> None:
    assert estimate_cost_usd(
        model="llama-3.1-8b-instant",
        input_tokens=42,
        output_tokens=8,
    ) == 0.00000274


def test_estimate_cost_usd_returns_none_for_unknown_model() -> None:
    assert estimate_cost_usd(
        model="unknown-model",
        input_tokens=42,
        output_tokens=8,
    ) is None


def test_generate_answer_rejects_empty_response() -> None:
    mock_response = SimpleNamespace(
        choices=[
            SimpleNamespace(message=SimpleNamespace(content=""))
        ]
    )

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("app.services.llm_service.settings.llm_api_key", "test-key"):
        with patch("app.services.llm_service.OpenAI", return_value=mock_client):
            with pytest.raises(LLMServiceError, match="LLM returned an empty response."):
                generate_answer("Hello")
