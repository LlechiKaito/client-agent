from constants.ai import (
    CHAT_LOG_PREFIX,
    LOG_FETCH_DAYS,
    MAIL_FETCH_DAYS,
    MAIL_FETCH_MAX,
    MAIL_LOG_PREFIX,
    MAX_CONTEXT_CHARS,
    SUMMARY_MAX_TOKENS,
    SUMMARY_NO_DATA_ERROR,
    SUMMARY_SYSTEM_PROMPT,
)
from domain.commons.result import Result, fail
from domain.repositories.ai_chat.ai_chat_repository import AiChatRepository
from domain.repositories.chat_log.chat_log_repository import ChatLogRepository
from domain.repositories.mail_log.mail_log_repository import MailLogRepository
from utils.text import truncate


class GenerateSummaryUseCase:
    def __init__(
        self,
        ai_chat_repository: AiChatRepository,
        chat_log_repository: ChatLogRepository,
        mail_log_repository: MailLogRepository,
    ) -> None:
        self._ai_chat_repository = ai_chat_repository
        self._chat_log_repository = chat_log_repository
        self._mail_log_repository = mail_log_repository

    async def execute(self) -> Result[str, str]:
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

        if not context_parts:
            return fail(SUMMARY_NO_DATA_ERROR)

        enriched_message = "\n\n".join(context_parts)

        return await self._ai_chat_repository.generate_reply(
            enriched_message, SUMMARY_SYSTEM_PROMPT, SUMMARY_MAX_TOKENS,
        )
