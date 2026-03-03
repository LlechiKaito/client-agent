import time

from constants.ai import (
    ANTHROPIC_MAX_TOKENS,
    CHAT_LOG_PREFIX,
    LOG_FETCH_DAYS,
    MAIL_FETCH_DAYS,
    MAIL_FETCH_MAX,
    MAIL_LOG_PREFIX,
    MAX_CONTEXT_CHARS,
    SECRETARY_SYSTEM_PROMPT,
)
from domain.commons.result import Result
from domain.entities.conversation.message import ConversationMessage
from domain.repositories.ai_chat.ai_chat_repository import AiChatRepository
from domain.repositories.chat_log.chat_log_repository import ChatLogRepository
from domain.repositories.conversation_memory.conversation_memory_repository import (
    ConversationMemoryRepository,
)
from domain.repositories.mail_log.mail_log_repository import MailLogRepository
from utils.text import truncate


class GenerateReplyUseCase:
    def __init__(
        self,
        ai_chat_repository: AiChatRepository,
        chat_log_repository: ChatLogRepository,
        mail_log_repository: MailLogRepository,
        conversation_memory_repository: ConversationMemoryRepository,
    ) -> None:
        self._ai_chat_repository = ai_chat_repository
        self._chat_log_repository = chat_log_repository
        self._mail_log_repository = mail_log_repository
        self._conversation_memory = conversation_memory_repository

    async def execute(self, user_id: str, user_message: str) -> Result[str, str]:
        context_parts: list[str] = []
        per_source_limit = MAX_CONTEXT_CHARS // 2

        log_result = await self._chat_log_repository.fetch_logs(LOG_FETCH_DAYS)
        if log_result.is_success and log_result.data:
            truncated = truncate(log_result.data, per_source_limit)
            context_parts.append(f"{CHAT_LOG_PREFIX}\n\n{truncated}")

        mail_result = await self._mail_log_repository.fetch_mails(
            MAIL_FETCH_DAYS, MAIL_FETCH_MAX,
        )
        if mail_result.is_success and mail_result.data:
            truncated = truncate(mail_result.data, per_source_limit)
            context_parts.append(f"{MAIL_LOG_PREFIX}\n\n{truncated}")

        if context_parts:
            enriched_message = "\n\n".join([*context_parts, user_message])
        else:
            enriched_message = user_message

        history = self._conversation_memory.get_history(user_id)

        self._conversation_memory.add_message(
            user_id,
            ConversationMessage(role="user", content=enriched_message, timestamp=time.time()),
        )

        ai_result = await self._ai_chat_repository.generate_reply(
            enriched_message, SECRETARY_SYSTEM_PROMPT, ANTHROPIC_MAX_TOKENS,
            history=history,
        )

        if ai_result.is_success:
            self._conversation_memory.add_message(
                user_id,
                ConversationMessage(
                    role="assistant", content=ai_result.data, timestamp=time.time(),
                ),
            )

        return ai_result
