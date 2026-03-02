from unittest.mock import AsyncMock

import pytest

from application.usecases.webhook.generate_reply_use_case import GenerateReplyUseCase
from constants.ai import CHAT_LOG_PREFIX, MAIL_LOG_PREFIX, MAX_CONTEXT_CHARS
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
def mock_mail_log_repository() -> AsyncMock:
    repo = AsyncMock()
    repo.fetch_mails.return_value = ok("From: client@example.com\nSubject: 会議の件")
    return repo


@pytest.fixture
def generate_reply_use_case(
    mock_ai_chat_repository: AsyncMock,
    mock_chat_log_repository: AsyncMock,
    mock_mail_log_repository: AsyncMock,
) -> GenerateReplyUseCase:
    return GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_chat_log_repository,
        mail_log_repository=mock_mail_log_repository,
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


async def test_should_include_mail_logs_in_message(
    generate_reply_use_case: GenerateReplyUseCase,
    mock_ai_chat_repository: AsyncMock,
    mock_mail_log_repository: AsyncMock,
) -> None:
    result = await generate_reply_use_case.execute("メールの内容を教えて")

    mock_mail_log_repository.fetch_mails.assert_called_once_with(3, 50)
    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert MAIL_LOG_PREFIX in called_message
    assert "From: client@example.com" in called_message
    assert "メールの内容を教えて" in called_message
    assert result.is_success is True


async def test_should_include_both_logs_and_mails(
    generate_reply_use_case: GenerateReplyUseCase,
    mock_ai_chat_repository: AsyncMock,
) -> None:
    result = await generate_reply_use_case.execute("状況を教えて")

    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert CHAT_LOG_PREFIX in called_message
    assert MAIL_LOG_PREFIX in called_message
    assert "状況を教えて" in called_message
    assert result.is_success is True


async def test_should_send_only_user_message_when_logs_fail(
    mock_ai_chat_repository: AsyncMock,
) -> None:
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = fail("GAS error")
    mock_mail_repo = AsyncMock()
    mock_mail_repo.fetch_mails.return_value = fail("GAS Mail error")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
        mail_log_repository=mock_mail_repo,
    )

    result = await use_case.execute("テスト")

    mock_ai_chat_repository.generate_reply.assert_called_once_with("テスト")
    assert result.is_success is True


async def test_should_send_only_user_message_when_logs_empty(
    mock_ai_chat_repository: AsyncMock,
) -> None:
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = ok("")
    mock_mail_repo = AsyncMock()
    mock_mail_repo.fetch_mails.return_value = ok("")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
        mail_log_repository=mock_mail_repo,
    )

    result = await use_case.execute("テスト")

    mock_ai_chat_repository.generate_reply.assert_called_once_with("テスト")
    assert result.is_success is True


async def test_should_include_only_mails_when_chat_logs_fail(
    mock_ai_chat_repository: AsyncMock,
    mock_mail_log_repository: AsyncMock,
) -> None:
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = fail("GAS error")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
        mail_log_repository=mock_mail_log_repository,
    )

    result = await use_case.execute("テスト")

    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert CHAT_LOG_PREFIX not in called_message
    assert MAIL_LOG_PREFIX in called_message
    assert "テスト" in called_message
    assert result.is_success is True


async def test_should_include_only_chat_logs_when_mails_fail(
    mock_ai_chat_repository: AsyncMock,
    mock_chat_log_repository: AsyncMock,
) -> None:
    mock_mail_repo = AsyncMock()
    mock_mail_repo.fetch_mails.return_value = fail("GAS Mail error")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_chat_log_repository,
        mail_log_repository=mock_mail_repo,
    )

    result = await use_case.execute("テスト")

    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert CHAT_LOG_PREFIX in called_message
    assert MAIL_LOG_PREFIX not in called_message
    assert "テスト" in called_message
    assert result.is_success is True


async def test_should_truncate_long_chat_logs(
    mock_ai_chat_repository: AsyncMock,
) -> None:
    per_source_limit = MAX_CONTEXT_CHARS // 2
    long_log = "A" * (per_source_limit + 1000)
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = ok(long_log)
    mock_mail_repo = AsyncMock()
    mock_mail_repo.fetch_mails.return_value = fail("skip")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
        mail_log_repository=mock_mail_repo,
    )

    await use_case.execute("テスト")

    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert "...(以降省略)" in called_message
    assert len(called_message) < per_source_limit + 1000


async def test_should_truncate_long_mail_logs(
    mock_ai_chat_repository: AsyncMock,
) -> None:
    per_source_limit = MAX_CONTEXT_CHARS // 2
    long_mail = "B" * (per_source_limit + 1000)
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = fail("skip")
    mock_mail_repo = AsyncMock()
    mock_mail_repo.fetch_mails.return_value = ok(long_mail)
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
        mail_log_repository=mock_mail_repo,
    )

    await use_case.execute("テスト")

    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert "...(以降省略)" in called_message
    assert len(called_message) < per_source_limit + 1000


async def test_should_return_failure_when_ai_fails(
    mock_ai_chat_repository: AsyncMock,
    mock_chat_log_repository: AsyncMock,
    mock_mail_log_repository: AsyncMock,
) -> None:
    mock_ai_chat_repository.generate_reply.return_value = fail("API error")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_chat_log_repository,
        mail_log_repository=mock_mail_log_repository,
    )

    result = await use_case.execute("テスト")

    assert result.is_success is False
    assert result.error == "API error"
