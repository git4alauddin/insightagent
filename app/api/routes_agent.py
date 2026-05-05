from fastapi import APIRouter, HTTPException

from app.schemas.agent import AgentQueryRequest, AgentQueryResponse
from app.services.agent_controller import AgentControllerError, run_agent_query


router = APIRouter(tags=["agent"])


@router.post("/agent/query", response_model=AgentQueryResponse)
def agent_query(request: AgentQueryRequest) -> AgentQueryResponse:
    try:
        return run_agent_query(request.message)
    except AgentControllerError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "AGENT_CONTROLLER_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc

