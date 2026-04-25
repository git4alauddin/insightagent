from fastapi import FastAPI

from app.api.routes_health import router as health_router
from app.config import settings
from app.utils.logger import configure_logging


configure_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(health_router)