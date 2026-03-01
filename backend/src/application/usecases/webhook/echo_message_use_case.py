from domain.commons.result import Result
from domain.repositories.message.message_repository import MessageRepository


class EchoMessageUseCase:
    def __init__(self, message_repository: MessageRepository) -> None:
        self._message_repository = message_repository

    async def execute(self, reply_token: str, text: str) -> Result[None, str]:
        return await self._message_repository.reply_text(reply_token, text)
