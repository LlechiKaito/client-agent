import importlib
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from constants.http import HTTP_STATUS_OK


@pytest.fixture
def app():
    with patch.dict(
        "os.environ",
        {
            "APP_HOST": "0.0.0.0",
            "APP_PORT": "8000",
            "APP_ENV": "test",
            "LINE_CHANNEL_SECRET": "test-secret",
            "LINE_CHANNEL_ACCESS_TOKEN": "test-token",
            "ANTHROPIC_API_KEY": "test-key",
            "GAS_WEBAPP_URL": "https://script.google.com/test",
            "GAS_MAIL_WEBAPP_URL": "https://script.google.com/test-mail",
        },
    ):
        import config.settings as settings_module
        import container.container as container_module

        importlib.reload(settings_module)
        importlib.reload(container_module)

        yield container_module.create_app()


@pytest.mark.anyio
async def test_health_endpoint_returns_200(app) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
    assert res.status_code == HTTP_STATUS_OK


@pytest.mark.anyio
async def test_health_endpoint_returns_healthy_status(app) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
    body = res.json()
    assert body["is_success"] is True
    assert body["data"]["status"] == "healthy"
