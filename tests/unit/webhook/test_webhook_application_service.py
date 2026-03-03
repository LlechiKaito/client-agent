from unittest.mock import AsyncMock

import pytest

from application.services.webhook.webhook_application_service import WebhookApplicationService
from constants.line import THINKING_MESSAGE
from domain.commons.result import fail, ok


@pytest.fixture
def mock_generate_reply_use_case() -> AsyncMock:
    use_case = AsyncMock()
    use_case.execute.return_value = ok("返信案：承知いたしました。")
    return use_case


@pytest.fixture
def mock_generate_summary_use_case() -> AsyncMock:
    use_case = AsyncMock()
    use_case.execute.return_value = ok("【状況レポート】\nクライアントA...")
    return use_case


@pytest.fixture
def mock_message_repository() -> AsyncMock:
    repo = AsyncMock()
    repo.reply_text.return_value = ok(None)
    repo.push_text.return_value = ok(None)
    repo.push_long_text.return_value = ok(None)
    return repo


@pytest.fixture
def webhook_service(
    mock_generate_reply_use_case: AsyncMock,
    mock_generate_summary_use_case: AsyncMock,
    mock_message_repository: AsyncMock,
) -> WebhookApplicationService:
    return WebhookApplicationService(
        generate_reply_use_case=mock_generate_reply_use_case,
        generate_summary_use_case=mock_generate_summary_use_case,
        message_repository=mock_message_repository,
    )


async def test_send_thinking_reply_calls_reply_text(
    webhook_service: WebhookApplicationService,
    mock_message_repository: AsyncMock,
) -> None:
    result = await webhook_service.send_thinking_reply(reply_token="token-abc")

    mock_message_repository.reply_text.assert_called_once_with("token-abc", THINKING_MESSAGE)
    assert result.is_success is True


async def test_generate_and_push_reply_sends_ai_response(
    webhook_service: WebhookApplicationService,
    mock_generate_reply_use_case: AsyncMock,
    mock_message_repository: AsyncMock,
) -> None:
    result = await webhook_service.generate_and_push_reply(
        user_id="U1234567890",
        text="会議の日程を調整してください",
    )

    mock_generate_reply_use_case.execute.assert_called_once_with(
        "U1234567890", "会議の日程を調整してください",
    )
    mock_message_repository.push_text.assert_called_once_with(
        "U1234567890",
        "返信案：承知いたしました。",
    )
    assert result.is_success is True


async def test_generate_and_push_reply_returns_failure_when_ai_fails(
    mock_generate_reply_use_case: AsyncMock,
    mock_generate_summary_use_case: AsyncMock,
    mock_message_repository: AsyncMock,
) -> None:
    mock_generate_reply_use_case.execute.return_value = fail("AI error")
    service = WebhookApplicationService(
        generate_reply_use_case=mock_generate_reply_use_case,
        generate_summary_use_case=mock_generate_summary_use_case,
        message_repository=mock_message_repository,
    )

    result = await service.generate_and_push_reply(
        user_id="U1234567890",
        text="テスト",
    )

    assert result.is_success is False
    assert result.error == "AI error"
    mock_message_repository.push_text.assert_not_called()


async def test_generate_and_push_summary_sends_report(
    webhook_service: WebhookApplicationService,
    mock_generate_summary_use_case: AsyncMock,
    mock_message_repository: AsyncMock,
) -> None:
    result = await webhook_service.generate_and_push_summary(
        user_id="U1234567890",
    )

    mock_generate_summary_use_case.execute.assert_called_once()
    mock_message_repository.push_long_text.assert_called_once_with(
        "U1234567890",
        "【状況レポート】\nクライアントA...",
    )
    assert result.is_success is True


async def test_generate_and_push_summary_returns_failure_when_ai_fails(
    mock_generate_reply_use_case: AsyncMock,
    mock_generate_summary_use_case: AsyncMock,
    mock_message_repository: AsyncMock,
) -> None:
    mock_generate_summary_use_case.execute.return_value = fail("API error")
    service = WebhookApplicationService(
        generate_reply_use_case=mock_generate_reply_use_case,
        generate_summary_use_case=mock_generate_summary_use_case,
        message_repository=mock_message_repository,
    )

    result = await service.generate_and_push_summary(user_id="U1234567890")

    assert result.is_success is False
    assert result.error == "API error"
    mock_message_repository.push_long_text.assert_not_called()
