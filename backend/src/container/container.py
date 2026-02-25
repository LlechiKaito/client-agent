from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from application.errors.application_error import ApplicationError
from config.settings import FRONTEND_URL
from presentation.errors.error_handler import (
    application_error_handler,
    unhandled_error_handler,
)
from presentation.routes.health_routes import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="Client Agent API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)

    app.include_router(health_router, prefix="/api")

    return app
