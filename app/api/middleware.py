from uuid import uuid4

from fastapi import FastAPI, Request


REQUEST_ID_HEADER = "x-request-id"


def _resolve_request_id(request: Request) -> str:
    incoming_request_id = request.headers.get(REQUEST_ID_HEADER)
    if incoming_request_id and incoming_request_id.strip():
        return incoming_request_id.strip()
    return f"req_{uuid4().hex}"


def register_request_id_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = _resolve_request_id(request)
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
