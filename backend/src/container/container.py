from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from linebot.v3.webhook import WebhookParser

from application.errors.application_error import ApplicationError
from application.services.webhook.webhook_application_service import WebhookApplicationService
from application.usecases.webhook.generate_reply_use_case import GenerateReplyUseCase
from application.usecases.webhook.generate_summary_use_case import (
    GenerateSummaryUseCase,
)
from config.settings import (
    ANTHROPIC_API_KEY,
    FRONTEND_URL,
    GAS_MAIL_WEBAPP_URL,
    GAS_WEBAPP_URL,
    LINE_CHANNEL_ACCESS_TOKEN,
    LINE_CHANNEL_SECRET,
)
from infrastructure.external.anthropic.anthropic_chat_client import AnthropicChatClient
from infrastructure.external.gas.gas_chat_log_client import GasChatLogClient
from infrastructure.external.gas.gas_mail_client import GasMailClient
from infrastructure.external.line.line_messaging_client import LineMessagingClient
from infrastructure.memory.in_memory_conversation_store import InMemoryConversationStore
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
    anthropic_chat_client = AnthropicChatClient(
        api_key=ANTHROPIC_API_KEY,
    )
    gas_chat_log_client = GasChatLogClient(
        webapp_url=GAS_WEBAPP_URL,
    )
    gas_mail_client = GasMailClient(
        webapp_url=GAS_MAIL_WEBAPP_URL,
    )
    conversation_store = InMemoryConversationStore()
    generate_reply_use_case = GenerateReplyUseCase(
        ai_chat_repository=anthropic_chat_client,
        chat_log_repository=gas_chat_log_client,
        mail_log_repository=gas_mail_client,
        conversation_memory_repository=conversation_store,
    )
    generate_summary_use_case = GenerateSummaryUseCase(
        ai_chat_repository=anthropic_chat_client,
        chat_log_repository=gas_chat_log_client,
        mail_log_repository=gas_mail_client,
    )
    webhook_service = WebhookApplicationService(
        generate_reply_use_case=generate_reply_use_case,
        generate_summary_use_case=generate_summary_use_case,
        message_repository=line_messaging_client,
    )
    webhook_parser = WebhookParser(channel_secret=LINE_CHANNEL_SECRET)

    init_webhook_routes(
        webhook_parser=webhook_parser,
        webhook_service=webhook_service,
    )

    app.include_router(health_router, prefix="/api")
    app.include_router(webhook_router)

    return app
