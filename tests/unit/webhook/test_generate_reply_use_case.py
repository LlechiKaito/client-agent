from unittest.mock import AsyncMock

import pytest

from application.usecases.webhook.generate_reply_use_case import GenerateReplyUseCase
from constants.ai import CHAT_LOG_PREFIX
from domain.commons.result import fail, ok


@pytest.fixture
def mock_ai_chat_repository() -> AsyncMock:
    repo = AsyncMock()
    repo.generate_reply.return_value = ok("返信案：承知いたしました。")
    return repo


@pytest.fixture
def mock_chat_log_repository() -> AsyncMock:
    repo = AsyncMock()
    repo.fetch_logs.return_value = ok("田中: 明日の会議は10時からです\n鈴木: 承知しました")
    return repo


@pytest.fixture
def generate_reply_use_case(
    mock_ai_chat_repository: AsyncMock,
    mock_chat_log_repository: AsyncMock,
) -> GenerateReplyUseCase:
    return GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_chat_log_repository,
    )


async def test_should_include_chat_logs_in_message(
    generate_reply_use_case: GenerateReplyUseCase,
    mock_ai_chat_repository: AsyncMock,
    mock_chat_log_repository: AsyncMock,
) -> None:
    result = await generate_reply_use_case.execute("何が話されてますか？")

    mock_chat_log_repository.fetch_logs.assert_called_once_with(3)
    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert CHAT_LOG_PREFIX in called_message
    assert "田中: 明日の会議は10時からです" in called_message
    assert "何が話されてますか？" in called_message
    assert result.is_success is True


async def test_should_send_only_user_message_when_logs_fail(
    mock_ai_chat_repository: AsyncMock,
) -> None:
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = fail("GAS error")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
    )

    result = await use_case.execute("テスト")

    mock_ai_chat_repository.generate_reply.assert_called_once_with("テスト")
    assert result.is_success is True


async def test_should_send_only_user_message_when_logs_empty(
    mock_ai_chat_repository: AsyncMock,
) -> None:
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = ok("")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
    )

    result = await use_case.execute("テスト")

    mock_ai_chat_repository.generate_reply.assert_called_once_with("テスト")
    assert result.is_success is True


async def test_should_return_failure_when_ai_fails(
    mock_ai_chat_repository: AsyncMock,
    mock_chat_log_repository: AsyncMock,
) -> None:
    mock_ai_chat_repository.generate_reply.return_value = fail("API error")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_chat_log_repository,
    )

    result = await use_case.execute("テスト")

    assert result.is_success is False
    assert result.error == "API error"
