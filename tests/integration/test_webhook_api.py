import base64
import hashlib
import hmac
import importlib
import json
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from constants.http import HTTP_STATUS_BAD_REQUEST, HTTP_STATUS_OK

CHANNEL_SECRET = "test-channel-secret"
CHANNEL_ACCESS_TOKEN = "test-channel-access-token"
ANTHROPIC_API_KEY = "test-anthropic-api-key"


def _generate_signature(body: str, secret: str) -> str:
    hash_value = hmac.new(
        secret.encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(hash_value).decode("utf-8")


def _build_text_message_event(reply_token: str, text: str) -> dict:
    return {
        "replyToken": reply_token,
        "type": "message",
        "mode": "active",
        "timestamp": 1234567890123,
        "source": {"type": "user", "userId": "U1234567890abcdef"},
        "webhookEventId": "event-id-123",
        "deliveryContext": {"isRedelivery": False},
        "message": {
            "type": "text",
            "id": "msg-id-123",
            "text": text,
            "quoteToken": "quote-token-123",
        },
    }


def _build_webhook_body(events: list[dict]) -> str:
    return json.dumps({"destination": "U1234567890", "events": events})


@pytest.fixture
def app():
    with patch.dict(
        "os.environ",
        {
            "APP_HOST": "0.0.0.0",
            "APP_PORT": "8000",
            "APP_ENV": "test",
            "FRONTEND_URL": "http://localhost:5173",
            "LINE_CHANNEL_SECRET": CHANNEL_SECRET,
            "LINE_CHANNEL_ACCESS_TOKEN": CHANNEL_ACCESS_TOKEN,
            "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
        },
    ):
        import config.settings as settings_module
        import container.container as container_module

        importlib.reload(settings_module)
        importlib.reload(container_module)

        yield container_module.create_app()


@pytest.mark.anyio
async def test_callback_returns_ok_and_sends_thinking_reply(app) -> None:
    body = _build_webhook_body([
        _build_text_message_event("reply-token-1", "hello"),
    ])
    signature = _generate_signature(body, CHANNEL_SECRET)

    mock_service = AsyncMock()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch(
            "presentation.routes.webhook_routes._webhook_service",
            mock_service,
        ):
            res = await client.post(
                "/callback",
                content=body,
                headers={"X-Line-Signature": signature},
            )

    assert res.status_code == HTTP_STATUS_OK
    mock_service.send_thinking_reply.assert_called_once_with(
        reply_token="reply-token-1",
    )


@pytest.mark.anyio
async def test_callback_returns_400_with_invalid_signature(app) -> None:
    body = _build_webhook_body([
        _build_text_message_event("reply-token-1", "hello"),
    ])

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/callback",
            content=body,
            headers={"X-Line-Signature": "invalid-signature"},
        )

    assert res.status_code == HTTP_STATUS_BAD_REQUEST
    response_body = res.json()
    assert response_body["is_success"] is False
    assert response_body["code"] == "INVALID_SIGNATURE"


@pytest.mark.anyio
async def test_callback_returns_400_without_signature(app) -> None:
    body = _build_webhook_body([])

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/callback", content=body)

    assert res.status_code == HTTP_STATUS_BAD_REQUEST
