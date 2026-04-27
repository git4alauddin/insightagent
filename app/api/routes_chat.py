import time

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMServiceError, generate_answer


router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    start_time = time.perf_counter()

    try:
        answer = generate_answer(request.message)
    except LLMServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "LLM_SERVICE_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc

    latency_ms = (time.perf_counter() - start_time) * 1000

    return ChatResponse(
        answer=answer,
        model=settings.llm_model,
        latency_ms=round(latency_ms, 2),
        status="success",
    )