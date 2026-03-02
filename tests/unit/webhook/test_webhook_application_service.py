from unittest.mock import AsyncMock

import pytest

from application.services.webhook.webhook_application_service import WebhookApplicationService
from domain.commons.result import fail, ok


@pytest.fixture
def mock_generate_reply_use_case() -> AsyncMock:
    use_case = AsyncMock()
    use_case.execute.return_value = ok("返信案：承知いたしました。")
    return use_case


@pytest.fixture
def mock_message_repository() -> AsyncMock:
    repo = AsyncMock()
    repo.reply_text.return_value = ok(None)
    return repo


@pytest.fixture
def webhook_service(
    mock_generate_reply_use_case: AsyncMock,
    mock_message_repository: AsyncMock,
) -> WebhookApplicationService:
    return WebhookApplicationService(
        generate_reply_use_case=mock_generate_reply_use_case,
        message_repository=mock_message_repository,
    )


async def test_should_generate_reply_and_send_via_line(
    webhook_service: WebhookApplicationService,
    mock_generate_reply_use_case: AsyncMock,
    mock_message_repository: AsyncMock,
) -> None:
    result = await webhook_service.handle_text_message(
        reply_token="token-abc",
        text="会議の日程を調整してください",
    )

    mock_generate_reply_use_case.execute.assert_called_once_with(
        "会議の日程を調整してください"
    )
    mock_message_repository.reply_text.assert_called_once_with(
        "token-abc",
        "返信案：承知いたしました。",
    )
    assert result.is_success is True


async def test_should_return_failure_when_ai_fails(
    mock_generate_reply_use_case: AsyncMock,
    mock_message_repository: AsyncMock,
) -> None:
    mock_generate_reply_use_case.execute.return_value = fail("AI error")
    service = WebhookApplicationService(
        generate_reply_use_case=mock_generate_reply_use_case,
        message_repository=mock_message_repository,
    )

    result = await service.handle_text_message(
        reply_token="token-abc",
        text="テスト",
    )

    assert result.is_success is False
    assert result.error == "AI error"
    mock_message_repository.reply_text.assert_not_called()
