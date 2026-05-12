import json
import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request


REQUEST_ID_HEADER = "x-request-id"
SESSION_ID_HEADER = "x-session-id"
logger = logging.getLogger(__name__)


def _resolve_request_id(request: Request) -> str:
    incoming_request_id = request.headers.get(REQUEST_ID_HEADER)
    if incoming_request_id and incoming_request_id.strip():
        return incoming_request_id.strip()
    return f"req_{uuid4().hex}"


def _resolve_session_id(request: Request) -> str | None:
    incoming_session_id = request.headers.get(SESSION_ID_HEADER)
    if incoming_session_id and incoming_session_id.strip():
        return incoming_session_id.strip()

    query_session_id = request.query_params.get("session_id")
    if query_session_id and query_session_id.strip():
        return query_session_id.strip()

    return None


def _request_status(status_code: int) -> str:
    return "success" if status_code < 400 else "failed"


def _error_category(status_code: int) -> str | None:
    if status_code < 400:
        return None

    if status_code in {401, 403}:
        return "AUTH_ERROR"

    if status_code == 422:
        return "VALIDATION_ERROR"

    if status_code == 429:
        return "RATE_LIMIT_ERROR"

    if status_code >= 500:
        return "INTERNAL_ERROR"

    return "HTTP_ERROR"


def _coerce_int(value) -> int | None:
    if value is None or isinstance(value, bool):
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _coerce_float(value) -> float | None:
    if value is None or isinstance(value, bool):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _request_usage(request: Request) -> dict[str, int | float | None]:
    usage = getattr(request.state, "usage", None)
    if not isinstance(usage, dict):
        usage = {}

    return {
        "input_tokens": _coerce_int(usage.get("input_tokens")),
        "output_tokens": _coerce_int(usage.get("output_tokens")),
        "total_tokens": _coerce_int(usage.get("total_tokens")),
        "estimated_cost_usd": _coerce_float(usage.get("estimated_cost_usd")),
    }


def register_request_id_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        start_time = time.perf_counter()
        request_id = _resolve_request_id(request)
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        status = _request_status(response.status_code)
        logger.info(
            json.dumps(
                {
                    "event": "request_completed",
                    "request_id": request_id,
                    "session_id": _resolve_session_id(request),
                    "method": request.method,
                    "endpoint": request.url.path,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "status": status,
                    "error_category": _error_category(response.status_code),
                    "latency_ms": latency_ms,
                    **_request_usage(request),
                }
            )
        )
        return response
