from fastapi import APIRouter, BackgroundTasks, Request
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhook import WebhookParser
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from application.errors.application_error import ValidationError
from application.services.webhook.webhook_application_service import WebhookApplicationService
from constants.http import HTTP_STATUS_OK
from constants.line import LINE_SIGNATURE_HEADER, WEBHOOK_RESPONSE_OK
from domain.errors.domain_error import DOMAIN_ERRORS

router = APIRouter()

_webhook_parser: WebhookParser | None = None
_webhook_service: WebhookApplicationService | None = None


def init_webhook_routes(
    webhook_parser: WebhookParser,
    webhook_service: WebhookApplicationService,
) -> None:
    global _webhook_parser, _webhook_service
    _webhook_parser = webhook_parser
    _webhook_service = webhook_service


@router.post("/callback", status_code=HTTP_STATUS_OK)
async def handle_callback(request: Request, background_tasks: BackgroundTasks) -> str:
    signature = request.headers.get(LINE_SIGNATURE_HEADER, "")
    body = await request.body()
    body_text = body.decode()

    assert _webhook_parser is not None
    assert _webhook_service is not None

    try:
        events = _webhook_parser.parse(body_text, signature)
    except InvalidSignatureError as exc:
        raise ValidationError(
            message=DOMAIN_ERRORS["INVALID_SIGNATURE"].message,
            code=DOMAIN_ERRORS["INVALID_SIGNATURE"].code,
        ) from exc

    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessageContent):
            continue

        user_id = event.source.user_id
        await _webhook_service.send_thinking_reply(reply_token=event.reply_token)
        background_tasks.add_task(
            _webhook_service.generate_and_push_reply,
            user_id=user_id,
            text=event.message.text,
        )

    return WEBHOOK_RESPONSE_OK
