from unittest.mock import AsyncMock

import pytest

from application.services.webhook.webhook_application_service import WebhookApplicationService
from domain.commons.result import ok


@pytest.fixture
def mock_echo_use_case() -> AsyncMock:
    use_case = AsyncMock()
    use_case.execute.return_value = ok(None)
    return use_case


@pytest.fixture
def webhook_service(mock_echo_use_case: AsyncMock) -> WebhookApplicationService:
    return WebhookApplicationService(echo_message_use_case=mock_echo_use_case)


async def test_should_delegate_to_echo_use_case(
    webhook_service: WebhookApplicationService,
    mock_echo_use_case: AsyncMock,
) -> None:
    result = await webhook_service.handle_text_message(
        reply_token="token-abc",
        text="test message",
    )

    mock_echo_use_case.execute.assert_called_once_with("token-abc", "test message")
    assert result.is_success is True
