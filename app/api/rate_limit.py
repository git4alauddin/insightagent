import time
from collections import defaultdict, deque

from fastapi import Header, HTTPException, Request

from app.config import settings


_request_records: dict[str, deque[float]] = defaultdict(deque)


def reset_rate_limit_store() -> None:
    _request_records.clear()


def _rate_limit_scope(request: Request) -> tuple[str, int]:
    if request.url.path == "/datasets/upload":
        return "upload", settings.rate_limit_uploads_per_minute
    return "request", settings.rate_limit_requests_per_minute


def _rate_limit_key(request: Request, api_key: str | None, scope: str) -> str:
    client_host = request.client.host if request.client else "unknown"
    identity = api_key or client_host
    return f"{scope}:{identity}"


def enforce_rate_limit(
    request: Request,
    x_api_key: str | None = Header(default=None),
) -> None:
    if not settings.rate_limit_enabled:
        return

    scope, limit = _rate_limit_scope(request)
    if limit <= 0:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "RATE_LIMIT_NOT_CONFIGURED",
                    "message": "Rate limit must be greater than zero.",
                }
            },
        )

    now = time.monotonic()
    window_start = now - settings.rate_limit_window_seconds
    key = _rate_limit_key(request, x_api_key, scope)
    records = _request_records[key]

    while records and records[0] <= window_start:
        records.popleft()

    if len(records) >= limit:
        raise HTTPException(
            status_code=429,
            detail={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Rate limit exceeded. Please retry later.",
                }
            },
        )

    records.append(now)
