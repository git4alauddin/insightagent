import logging
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import ExceptionHandler


logger = logging.getLogger(__name__)


from app.api.middleware import REQUEST_ID_HEADER


def _get_request_id(request: Request) -> str | None:
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        return str(request_id)
    return None


def _build_error_response(
    status_code: int,
    code: str,
    message: str,
    request_id: str | None,
) -> JSONResponse:
    content = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }

    headers = {}
    if request_id:
        headers[REQUEST_ID_HEADER] = request_id

    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=headers,
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
    code, message = _extract_error_detail(exc.detail)
    return _build_error_response(exc.status_code, code, message, _get_request_id(request))


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    del exc
    return _build_error_response(
        status_code=422,
        code="INVALID_INPUT",
        message="Request validation failed.",
        request_id=_get_request_id(request),
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
        request_id=_get_request_id(request),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        StarletteHTTPException,
        cast(ExceptionHandler, http_exception_handler),
    )
    app.add_exception_handler(
        RequestValidationError,
        cast(ExceptionHandler, validation_exception_handler),
    )
    app.add_exception_handler(
        Exception,
        cast(ExceptionHandler, unexpected_exception_handler),
    )
