from unittest.mock import AsyncMock

import pytest

from application.usecases.webhook.echo_message_use_case import EchoMessageUseCase
from domain.commons.result import ok


@pytest.fixture
def mock_message_repository() -> AsyncMock:
    repo = AsyncMock()
    repo.reply_text.return_value = ok(None)
    return repo


@pytest.fixture
def echo_use_case(mock_message_repository: AsyncMock) -> EchoMessageUseCase:
    return EchoMessageUseCase(message_repository=mock_message_repository)


async def test_should_call_reply_text_with_same_message(
    echo_use_case: EchoMessageUseCase,
    mock_message_repository: AsyncMock,
) -> None:
    result = await echo_use_case.execute(reply_token="token-123", text="hello")

    mock_message_repository.reply_text.assert_called_once_with("token-123", "hello")
    assert result.is_success is True


async def test_should_echo_empty_string(
    echo_use_case: EchoMessageUseCase,
    mock_message_repository: AsyncMock,
) -> None:
    result = await echo_use_case.execute(reply_token="token-456", text="")

    mock_message_repository.reply_text.assert_called_once_with("token-456", "")
    assert result.is_success is True


async def test_should_echo_unicode_message(
    echo_use_case: EchoMessageUseCase,
    mock_message_repository: AsyncMock,
) -> None:
    result = await echo_use_case.execute(reply_token="token-789", text="こんにちは")

    mock_message_repository.reply_text.assert_called_once_with("token-789", "こんにちは")
    assert result.is_success is True
