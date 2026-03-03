from unittest.mock import AsyncMock

import pytest

from application.usecases.webhook.generate_summary_use_case import (
    GenerateSummaryUseCase,
)
from constants.ai import (
    CHAT_LOG_PREFIX,
    MAIL_LOG_PREFIX,
    MAX_CONTEXT_CHARS,
    SUMMARY_MAX_TOKENS,
    SUMMARY_NO_DATA_ERROR,
    SUMMARY_SYSTEM_PROMPT,
)
from domain.commons.result import fail, ok


@pytest.fixture
def mock_ai_chat_repository() -> AsyncMock:
    repo = AsyncMock()
    repo.generate_reply.return_value = ok("【状況レポート】\nクライアントA...")
    return repo


@pytest.fixture
def mock_chat_log_repository() -> AsyncMock:
    repo = AsyncMock()
    repo.fetch_logs.return_value = ok("田中: 明日の会議は10時からです")
    return repo


@pytest.fixture
def mock_mail_log_repository() -> AsyncMock:
    repo = AsyncMock()
    repo.fetch_mails.return_value = ok("From: client@example.com\nSubject: 会議の件")
    return repo


@pytest.fixture
def generate_summary_use_case(
    mock_ai_chat_repository: AsyncMock,
    mock_chat_log_repository: AsyncMock,
    mock_mail_log_repository: AsyncMock,
) -> GenerateSummaryUseCase:
    return GenerateSummaryUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_chat_log_repository,
        mail_log_repository=mock_mail_log_repository,
    )


async def test_should_include_both_logs_and_mails(
    generate_summary_use_case: GenerateSummaryUseCase,
    mock_ai_chat_repository: AsyncMock,
) -> None:
    result = await generate_summary_use_case.execute()

    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert CHAT_LOG_PREFIX in called_message
    assert MAIL_LOG_PREFIX in called_message
    assert result.is_success is True


async def test_should_use_summary_system_prompt_and_max_tokens(
    generate_summary_use_case: GenerateSummaryUseCase,
    mock_ai_chat_repository: AsyncMock,
) -> None:
    await generate_summary_use_case.execute()

    call_args = mock_ai_chat_repository.generate_reply.call_args[0]
    assert call_args[1] == SUMMARY_SYSTEM_PROMPT
    assert call_args[2] == SUMMARY_MAX_TOKENS


async def test_should_return_failure_when_no_data_available(
    mock_ai_chat_repository: AsyncMock,
) -> None:
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = fail("GAS error")
    mock_mail_repo = AsyncMock()
    mock_mail_repo.fetch_mails.return_value = fail("GAS Mail error")
    use_case = GenerateSummaryUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
        mail_log_repository=mock_mail_repo,
    )

    result = await use_case.execute()

    assert result.is_success is False
    assert result.error == SUMMARY_NO_DATA_ERROR
    mock_ai_chat_repository.generate_reply.assert_not_called()


async def test_should_work_with_only_chat_logs(
    mock_ai_chat_repository: AsyncMock,
    mock_chat_log_repository: AsyncMock,
) -> None:
    mock_mail_repo = AsyncMock()
    mock_mail_repo.fetch_mails.return_value = fail("GAS Mail error")
    use_case = GenerateSummaryUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_chat_log_repository,
        mail_log_repository=mock_mail_repo,
    )

    result = await use_case.execute()

    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert CHAT_LOG_PREFIX in called_message
    assert MAIL_LOG_PREFIX not in called_message
    assert result.is_success is True


async def test_should_work_with_only_mail_logs(
    mock_ai_chat_repository: AsyncMock,
    mock_mail_log_repository: AsyncMock,
) -> None:
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = fail("GAS error")
    use_case = GenerateSummaryUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
        mail_log_repository=mock_mail_log_repository,
    )

    result = await use_case.execute()

    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert CHAT_LOG_PREFIX not in called_message
    assert MAIL_LOG_PREFIX in called_message
    assert result.is_success is True


async def test_should_return_failure_when_empty_data(
    mock_ai_chat_repository: AsyncMock,
) -> None:
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = ok("")
    mock_mail_repo = AsyncMock()
    mock_mail_repo.fetch_mails.return_value = ok("")
    use_case = GenerateSummaryUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
        mail_log_repository=mock_mail_repo,
    )

    result = await use_case.execute()

    assert result.is_success is False
    mock_ai_chat_repository.generate_reply.assert_not_called()


async def test_should_truncate_long_data(
    mock_ai_chat_repository: AsyncMock,
) -> None:
    per_source_limit = MAX_CONTEXT_CHARS // 2
    long_log = "A" * (per_source_limit + 1000)
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = ok(long_log)
    mock_mail_repo = AsyncMock()
    mock_mail_repo.fetch_mails.return_value = fail("skip")
    use_case = GenerateSummaryUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
        mail_log_repository=mock_mail_repo,
    )

    await use_case.execute()

    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert "...(以降省略)" in called_message


async def test_should_return_failure_when_ai_fails(
    mock_chat_log_repository: AsyncMock,
    mock_mail_log_repository: AsyncMock,
) -> None:
    mock_ai = AsyncMock()
    mock_ai.generate_reply.return_value = fail("API error")
    use_case = GenerateSummaryUseCase(
        ai_chat_repository=mock_ai,
        chat_log_repository=mock_chat_log_repository,
        mail_log_repository=mock_mail_log_repository,
    )

    result = await use_case.execute()

    assert result.is_success is False
    assert result.error == "API error"


async def test_should_not_include_user_message_in_context(
    generate_summary_use_case: GenerateSummaryUseCase,
    mock_ai_chat_repository: AsyncMock,
) -> None:
    await generate_summary_use_case.execute()

    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert "まとめ" not in called_message
