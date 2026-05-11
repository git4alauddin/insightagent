from fastapi import FastAPI

from app.api.cors import register_cors_middleware
from app.api.error_handlers import register_exception_handlers
from app.api.middleware import register_request_id_middleware
from app.api.routes_agent import router as agent_router
from app.api.routes_chat import router as chat_router
from app.api.routes_datasets import router as datasets_router
from app.api.routes_health import router as health_router
from app.api.routes_session import router as session_router
from app.config import settings
from app.utils.logger import configure_logging


configure_logging()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )

    register_cors_middleware(app)
    register_exception_handlers(app)
    register_request_id_middleware(app)

    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(agent_router)
    app.include_router(session_router)
    app.include_router(datasets_router)

    return app


app = create_app()
