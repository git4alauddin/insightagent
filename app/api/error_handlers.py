import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


logger = logging.getLogger(__name__)


def _build_error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
            }
        },
    )


def _extract_error_detail(detail: Any) -> tuple[str, str]:
    if isinstance(detail, dict):
        error = detail.get("error")
        if isinstance(error, dict):
            code = str(error.get("code") or "HTTP_ERROR")
            message = str(error.get("message") or "Request failed.")
            return code, message

        code = str(detail.get("code") or "HTTP_ERROR")
        message = str(detail.get("message") or "Request failed.")
        return code, message

    return "HTTP_ERROR", str(detail or "Request failed.")


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    del request
    code, message = _extract_error_detail(exc.detail)
    return _build_error_response(exc.status_code, code, message)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    del request, exc
    return _build_error_response(
        status_code=422,
        code="INVALID_INPUT",
        message="Request validation failed.",
    )


async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception("Unhandled request error on %s", request.url.path, exc_info=exc)
    return _build_error_response(
        status_code=500,
        code="INTERNAL_ERROR",
        message="An unexpected error occurred.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unexpected_exception_handler)
