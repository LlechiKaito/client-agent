from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from linebot.v3.webhook import WebhookParser

from application.errors.application_error import ApplicationError
from application.services.webhook.webhook_application_service import WebhookApplicationService
from application.usecases.webhook.echo_message_use_case import EchoMessageUseCase
from config.settings import FRONTEND_URL, LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from infrastructure.external.line.line_messaging_client import LineMessagingClient
from presentation.errors.error_handler import (
    application_error_handler,
    unhandled_error_handler,
)
from presentation.routes.health_routes import router as health_router
from presentation.routes.webhook_routes import init_webhook_routes
from presentation.routes.webhook_routes import router as webhook_router


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

    line_messaging_client = LineMessagingClient(
        channel_access_token=LINE_CHANNEL_ACCESS_TOKEN,
    )
    echo_use_case = EchoMessageUseCase(
        message_repository=line_messaging_client,
    )
    webhook_service = WebhookApplicationService(
        echo_message_use_case=echo_use_case,
    )
    webhook_parser = WebhookParser(channel_secret=LINE_CHANNEL_SECRET)

    init_webhook_routes(
        webhook_parser=webhook_parser,
        webhook_service=webhook_service,
    )

    app.include_router(health_router, prefix="/api")
    app.include_router(webhook_router)

    return app
