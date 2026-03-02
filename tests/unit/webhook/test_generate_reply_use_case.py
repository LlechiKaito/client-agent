from unittest.mock import AsyncMock

import pytest

from application.usecases.webhook.generate_reply_use_case import GenerateReplyUseCase
from domain.commons.result import fail, ok


@pytest.fixture
def mock_ai_chat_repository() -> AsyncMock:
    repo = AsyncMock()
    repo.generate_reply.return_value = ok("返信案：承知いたしました。")
    return repo


@pytest.fixture
def generate_reply_use_case(mock_ai_chat_repository: AsyncMock) -> GenerateReplyUseCase:
    return GenerateReplyUseCase(ai_chat_repository=mock_ai_chat_repository)


async def test_should_call_generate_reply_with_user_message(
    generate_reply_use_case: GenerateReplyUseCase,
    mock_ai_chat_repository: AsyncMock,
) -> None:
    result = await generate_reply_use_case.execute("会議の日程を調整してください")

    mock_ai_chat_repository.generate_reply.assert_called_once_with(
        "会議の日程を調整してください"
    )
    assert result.is_success is True
    assert result.data == "返信案：承知いたしました。"


async def test_should_return_failure_when_ai_fails(
    mock_ai_chat_repository: AsyncMock,
) -> None:
    mock_ai_chat_repository.generate_reply.return_value = fail("API error")
    use_case = GenerateReplyUseCase(ai_chat_repository=mock_ai_chat_repository)

    result = await use_case.execute("テスト")

    assert result.is_success is False
    assert result.error == "API error"
