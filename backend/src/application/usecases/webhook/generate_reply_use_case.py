from constants.ai import CHAT_LOG_PREFIX, LOG_FETCH_DAYS
from domain.commons.result import Result
from domain.repositories.ai_chat.ai_chat_repository import AiChatRepository
from domain.repositories.chat_log.chat_log_repository import ChatLogRepository


class GenerateReplyUseCase:
    def __init__(
        self,
        ai_chat_repository: AiChatRepository,
        chat_log_repository: ChatLogRepository,
    ) -> None:
        self._ai_chat_repository = ai_chat_repository
        self._chat_log_repository = chat_log_repository

    async def execute(self, user_message: str) -> Result[str, str]:
        log_result = await self._chat_log_repository.fetch_logs(LOG_FETCH_DAYS)

        if log_result.is_success and log_result.data:
            enriched_message = (
                f"{CHAT_LOG_PREFIX}\n\n{log_result.data}\n\n{user_message}"
            )
        else:
            enriched_message = user_message

        return await self._ai_chat_repository.generate_reply(enriched_message)
