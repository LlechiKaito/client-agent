from unittest.mock import AsyncMock, MagicMock

import pytest

from application.usecases.webhook.generate_reply_use_case import GenerateReplyUseCase
from constants.ai import (
    ANTHROPIC_MAX_TOKENS,
    CHAT_LOG_PREFIX,
    MAIL_LOG_PREFIX,
    MAX_CONTEXT_CHARS,
    SECRETARY_SYSTEM_PROMPT,
)
from domain.commons.result import fail, ok

USER_ID = "U1234567890"


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
def mock_conversation_memory() -> MagicMock:
    repo = MagicMock()
    repo.get_history.return_value = []
    return repo


@pytest.fixture
def generate_reply_use_case(
    mock_ai_chat_repository: AsyncMock,
    mock_chat_log_repository: AsyncMock,
    mock_mail_log_repository: AsyncMock,
    mock_conversation_memory: MagicMock,
) -> GenerateReplyUseCase:
    return GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_chat_log_repository,
        mail_log_repository=mock_mail_log_repository,
        conversation_memory_repository=mock_conversation_memory,
    )


async def test_should_include_chat_logs_in_message(
    generate_reply_use_case: GenerateReplyUseCase,
    mock_ai_chat_repository: AsyncMock,
    mock_chat_log_repository: AsyncMock,
) -> None:
    result = await generate_reply_use_case.execute(USER_ID, "何が話されてますか？")

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
    result = await generate_reply_use_case.execute(USER_ID, "メールの内容を教えて")

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
    result = await generate_reply_use_case.execute(USER_ID, "状況を教えて")

    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert CHAT_LOG_PREFIX in called_message
    assert MAIL_LOG_PREFIX in called_message
    assert "状況を教えて" in called_message
    assert result.is_success is True


async def test_should_send_only_user_message_when_logs_fail(
    mock_ai_chat_repository: AsyncMock,
    mock_conversation_memory: MagicMock,
) -> None:
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = fail("GAS error")
    mock_mail_repo = AsyncMock()
    mock_mail_repo.fetch_mails.return_value = fail("GAS Mail error")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
        mail_log_repository=mock_mail_repo,
        conversation_memory_repository=mock_conversation_memory,
    )

    result = await use_case.execute(USER_ID, "テスト")

    mock_ai_chat_repository.generate_reply.assert_called_once_with(
        "テスト", SECRETARY_SYSTEM_PROMPT, ANTHROPIC_MAX_TOKENS,
        history=[],
    )
    assert result.is_success is True


async def test_should_send_only_user_message_when_logs_empty(
    mock_ai_chat_repository: AsyncMock,
    mock_conversation_memory: MagicMock,
) -> None:
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = ok("")
    mock_mail_repo = AsyncMock()
    mock_mail_repo.fetch_mails.return_value = ok("")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
        mail_log_repository=mock_mail_repo,
        conversation_memory_repository=mock_conversation_memory,
    )

    result = await use_case.execute(USER_ID, "テスト")

    mock_ai_chat_repository.generate_reply.assert_called_once_with(
        "テスト", SECRETARY_SYSTEM_PROMPT, ANTHROPIC_MAX_TOKENS,
        history=[],
    )
    assert result.is_success is True


async def test_should_include_only_mails_when_chat_logs_fail(
    mock_ai_chat_repository: AsyncMock,
    mock_mail_log_repository: AsyncMock,
    mock_conversation_memory: MagicMock,
) -> None:
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = fail("GAS error")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
        mail_log_repository=mock_mail_log_repository,
        conversation_memory_repository=mock_conversation_memory,
    )

    result = await use_case.execute(USER_ID, "テスト")

    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert CHAT_LOG_PREFIX not in called_message
    assert MAIL_LOG_PREFIX in called_message
    assert "テスト" in called_message
    assert result.is_success is True


async def test_should_include_only_chat_logs_when_mails_fail(
    mock_ai_chat_repository: AsyncMock,
    mock_chat_log_repository: AsyncMock,
    mock_conversation_memory: MagicMock,
) -> None:
    mock_mail_repo = AsyncMock()
    mock_mail_repo.fetch_mails.return_value = fail("GAS Mail error")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_chat_log_repository,
        mail_log_repository=mock_mail_repo,
        conversation_memory_repository=mock_conversation_memory,
    )

    result = await use_case.execute(USER_ID, "テスト")

    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert CHAT_LOG_PREFIX in called_message
    assert MAIL_LOG_PREFIX not in called_message
    assert "テスト" in called_message
    assert result.is_success is True


async def test_should_truncate_long_chat_logs(
    mock_ai_chat_repository: AsyncMock,
    mock_conversation_memory: MagicMock,
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
        conversation_memory_repository=mock_conversation_memory,
    )

    await use_case.execute(USER_ID, "テスト")

    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert "...(以降省略)" in called_message
    assert len(called_message) < per_source_limit + 1000


async def test_should_truncate_long_mail_logs(
    mock_ai_chat_repository: AsyncMock,
    mock_conversation_memory: MagicMock,
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
        conversation_memory_repository=mock_conversation_memory,
    )

    await use_case.execute(USER_ID, "テスト")

    called_message = mock_ai_chat_repository.generate_reply.call_args[0][0]
    assert "...(以降省略)" in called_message
    assert len(called_message) < per_source_limit + 1000


async def test_should_return_failure_when_ai_fails(
    mock_ai_chat_repository: AsyncMock,
    mock_chat_log_repository: AsyncMock,
    mock_mail_log_repository: AsyncMock,
    mock_conversation_memory: MagicMock,
) -> None:
    mock_ai_chat_repository.generate_reply.return_value = fail("API error")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_chat_log_repository,
        mail_log_repository=mock_mail_log_repository,
        conversation_memory_repository=mock_conversation_memory,
    )

    result = await use_case.execute(USER_ID, "テスト")

    assert result.is_success is False
    assert result.error == "API error"


async def test_should_pass_conversation_history_to_ai(
    mock_ai_chat_repository: AsyncMock,
    mock_conversation_memory: MagicMock,
) -> None:
    from domain.entities.conversation.message import ConversationMessage

    history = [
        ConversationMessage(role="user", content="前の質問", timestamp=1000.0),
        ConversationMessage(role="assistant", content="前の回答", timestamp=1001.0),
    ]
    mock_conversation_memory.get_history.return_value = history
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = fail("skip")
    mock_mail_repo = AsyncMock()
    mock_mail_repo.fetch_mails.return_value = fail("skip")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
        mail_log_repository=mock_mail_repo,
        conversation_memory_repository=mock_conversation_memory,
    )

    await use_case.execute(USER_ID, "続きを教えて")

    call_kwargs = mock_ai_chat_repository.generate_reply.call_args
    assert call_kwargs.kwargs["history"] == history


async def test_should_store_user_and_assistant_messages(
    mock_ai_chat_repository: AsyncMock,
    mock_conversation_memory: MagicMock,
) -> None:
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = fail("skip")
    mock_mail_repo = AsyncMock()
    mock_mail_repo.fetch_mails.return_value = fail("skip")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
        mail_log_repository=mock_mail_repo,
        conversation_memory_repository=mock_conversation_memory,
    )

    await use_case.execute(USER_ID, "テスト")

    calls = mock_conversation_memory.add_message.call_args_list
    assert len(calls) == 2
    assert calls[0].args[0] == USER_ID
    assert calls[0].args[1].role == "user"
    assert calls[0].args[1].content == "テスト"
    assert calls[1].args[0] == USER_ID
    assert calls[1].args[1].role == "assistant"
    assert calls[1].args[1].content == "返信案：承知いたしました。"


async def test_should_not_store_assistant_message_on_failure(
    mock_ai_chat_repository: AsyncMock,
    mock_conversation_memory: MagicMock,
) -> None:
    mock_ai_chat_repository.generate_reply.return_value = fail("API error")
    mock_log_repo = AsyncMock()
    mock_log_repo.fetch_logs.return_value = fail("skip")
    mock_mail_repo = AsyncMock()
    mock_mail_repo.fetch_mails.return_value = fail("skip")
    use_case = GenerateReplyUseCase(
        ai_chat_repository=mock_ai_chat_repository,
        chat_log_repository=mock_log_repo,
        mail_log_repository=mock_mail_repo,
        conversation_memory_repository=mock_conversation_memory,
    )

    await use_case.execute(USER_ID, "テスト")

    calls = mock_conversation_memory.add_message.call_args_list
    assert len(calls) == 1
    assert calls[0].args[1].role == "user"
