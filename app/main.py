from fastapi import FastAPI

from app.api.routes_agent import router as agent_router
from app.api.routes_chat import router as chat_router
from app.api.routes_datasets import router as datasets_router
from app.api.routes_health import router as health_router
from app.api.routes_session import router as session_router
from app.config import settings
from app.utils.logger import configure_logging


configure_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(agent_router)
app.include_router(session_router)
app.include_router(datasets_router)
