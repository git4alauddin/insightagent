import time

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.dependencies import require_api_key
from app.api.rate_limit import enforce_rate_limit
from app.config import settings
from app.schemas.chat import ChatRequest, ChatResponse, MemoryChatRequest, MemoryChatResponse
from app.schemas.structured import StructuredLLMResponse
from app.services.llm_service import LLMServiceError, generate_answer_with_usage
from app.services.memory_chat_service import MemoryChatServiceError, run_memory_chat
from app.services.structured_llm_service import (
    StructuredLLMServiceError,
    generate_structured_answer,
)


router = APIRouter(
    tags=["chat"],
    dependencies=[Depends(require_api_key), Depends(enforce_rate_limit)],
)


@router.post("/chat", response_model=ChatResponse)
def chat(chat_request: ChatRequest, request: Request) -> ChatResponse:
    start_time = time.perf_counter()

    try:
        result = generate_answer_with_usage(chat_request.message)
        answer = result["answer"]
        request.state.usage = result["usage"]
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


@router.post("/chat/structured", response_model=StructuredLLMResponse)
def structured_chat(request: ChatRequest) -> StructuredLLMResponse:
    try:
        return generate_structured_answer(request.message)
    except StructuredLLMServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "STRUCTURED_LLM_SERVICE_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc


@router.post("/chat/memory", response_model=MemoryChatResponse)
def memory_chat(request: MemoryChatRequest) -> MemoryChatResponse:
    try:
        return run_memory_chat(
            message=request.message,
            session_id=request.session_id,
        )
    except MemoryChatServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "MEMORY_CHAT_SERVICE_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc
