import pytest
from httpx import ASGITransport, AsyncClient

from constants.http import HTTP_STATUS_OK
from container.container import create_app

app = create_app()


@pytest.mark.anyio
async def test_health_endpoint_returns_200() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
    assert res.status_code == HTTP_STATUS_OK


@pytest.mark.anyio
async def test_health_endpoint_returns_healthy_status() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
    body = res.json()
    assert body["is_success"] is True
    assert body["data"]["status"] == "healthy"
