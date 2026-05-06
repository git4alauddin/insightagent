from fastapi import APIRouter, Response

from app.config import settings
from app.schemas.common import HealthResponse, ReadinessResponse
from app.services.readiness_service import run_readiness_checks


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )


@router.get("/ready", response_model=ReadinessResponse)
def readiness_check(response: Response) -> ReadinessResponse:
    readiness = run_readiness_checks()
    if readiness.status != "ready":
        response.status_code = 503
    return readiness

