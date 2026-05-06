from fastapi import APIRouter, HTTPException

from app.schemas.session import CreateSessionResponse, SessionMessagesResponse
from app.services.session_service import SessionServiceError, create_session, get_recent_messages


router = APIRouter(tags=["session"])


@router.post("/sessions", response_model=CreateSessionResponse)
def create_new_session() -> CreateSessionResponse:
    session_id = create_session()
    return CreateSessionResponse(session_id=session_id, status="success")


@router.get("/sessions/{session_id}/messages", response_model=SessionMessagesResponse)
def get_session_messages(session_id: str) -> SessionMessagesResponse:
    try:
        messages = get_recent_messages(session_id, limit=100)
    except SessionServiceError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "SESSION_NOT_FOUND",
                    "message": str(exc),
                }
            },
        ) from exc

    return SessionMessagesResponse(
        session_id=session_id,
        messages=messages,
        status="success",
    )

