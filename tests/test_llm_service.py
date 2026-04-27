from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from httpx import Request
from openai import APITimeoutError

from app.services.llm_service import LLMServiceError, generate_answer


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
