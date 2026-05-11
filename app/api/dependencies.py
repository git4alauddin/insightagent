from secrets import compare_digest

from fastapi import Header, HTTPException

from app.config import settings


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not settings.api_key:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "API_KEY_NOT_CONFIGURED",
                    "message": "API key authentication is not configured.",
                }
            },
        )

    if not x_api_key or not compare_digest(x_api_key, settings.api_key):
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "A valid x-api-key header is required.",
                }
            },
        )
