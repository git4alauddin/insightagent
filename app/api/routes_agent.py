import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.dependencies import require_api_key
from app.api.rate_limit import enforce_rate_limit
from app.schemas.agent import AgentQueryRequest, AgentQueryResponse
from app.services.agent_controller import AgentControllerError, run_agent_query


router = APIRouter(
    tags=["agent"],
    dependencies=[Depends(require_api_key), Depends(enforce_rate_limit)],
)
logger = logging.getLogger(__name__)


def _get_request_id(request: Request) -> str | None:
    request_id = getattr(request.state, "request_id", None)
    return str(request_id) if request_id else None


def _log_agent_tool_trace(
    request: Request,
    response: AgentQueryResponse,
) -> None:
    logger.info(
        json.dumps(
            {
                "event": "agent_tool_completed",
                "request_id": _get_request_id(request),
                "tool_used": response.tool_used,
                "tool_status": response.tool_status,
                "agent_status": response.status,
                "tool_output_summary": response.tool_output_summary,
            }
        )
    )


@router.post("/agent/query", response_model=AgentQueryResponse)
def agent_query(
    request: Request,
    payload: AgentQueryRequest,
) -> AgentQueryResponse:
    try:
        response = AgentQueryResponse.model_validate(run_agent_query(payload.message))
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

    _log_agent_tool_trace(request, response)
    return response
