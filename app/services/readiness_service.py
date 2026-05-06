from pathlib import Path

from app.config import settings
from app.db.database import get_connection
from app.schemas.common import DependencyStatus, ReadinessResponse


def check_database() -> DependencyStatus:
    try:
        connection = get_connection()
        try:
            connection.execute("SELECT 1")
        finally:
            connection.close()
    except Exception as exc:
        return DependencyStatus(
            name="database",
            status="failed",
            detail=f"Database check failed: {exc}",
        )

    return DependencyStatus(
        name="database",
        status="ok",
        detail="Database is reachable.",
    )


def check_storage() -> DependencyStatus:
    try:
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        return DependencyStatus(
            name="storage",
            status="failed",
            detail=f"Storage check failed: {exc}",
        )

    return DependencyStatus(
        name="storage",
        status="ok",
        detail=f"Storage path is available: {upload_dir}",
    )


def check_llm_config() -> DependencyStatus:
    if not settings.llm_api_key:
        return DependencyStatus(
            name="llm_config",
            status="failed",
            detail="LLM API key is missing.",
        )

    if not settings.llm_model:
        return DependencyStatus(
            name="llm_config",
            status="failed",
            detail="LLM model is missing.",
        )

    return DependencyStatus(
        name="llm_config",
        status="ok",
        detail="LLM configuration is present.",
    )


def run_readiness_checks() -> ReadinessResponse:
    checks = [
        check_database(),
        check_storage(),
        check_llm_config(),
    ]
    overall_status = "ready" if all(check.status == "ok" for check in checks) else "not_ready"
    return ReadinessResponse(status=overall_status, checks=checks)
