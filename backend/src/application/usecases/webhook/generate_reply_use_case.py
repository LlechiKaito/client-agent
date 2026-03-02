from domain.commons.result import Result
from domain.repositories.ai_chat.ai_chat_repository import AiChatRepository


class GenerateReplyUseCase:
    def __init__(self, ai_chat_repository: AiChatRepository) -> None:
        self._ai_chat_repository = ai_chat_repository

    async def execute(self, user_message: str) -> Result[str, str]:
        return await self._ai_chat_repository.generate_reply(user_message)
