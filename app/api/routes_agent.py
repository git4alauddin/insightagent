from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import require_api_key
from app.api.rate_limit import enforce_rate_limit
from app.schemas.agent import AgentQueryRequest, AgentQueryResponse
from app.services.agent_controller import AgentControllerError, run_agent_query


router = APIRouter(
    tags=["agent"],
    dependencies=[Depends(require_api_key), Depends(enforce_rate_limit)],
)


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
