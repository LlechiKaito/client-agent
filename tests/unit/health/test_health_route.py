from constants.http import HTTP_STATUS_OK
from presentation.routes.health_routes import router


def test_health_router_has_health_endpoint() -> None:
    routes = [route.path for route in router.routes]
    assert "/health" in routes


def test_http_status_ok_is_200() -> None:
    assert HTTP_STATUS_OK == 200
