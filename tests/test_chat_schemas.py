from app.schemas.chat import ChatRequest, ChatResponse


def test_chat_request_accepts_message() -> None:
    request = ChatRequest(message="Hello")

    assert request.message == "Hello"


def test_chat_response_accepts_numeric_latency() -> None:
    response = ChatResponse(
        answer="Hi",
        model="test-model",
        latency_ms=12.5,
        status="success",
    )

    assert response.latency_ms == 12.5
