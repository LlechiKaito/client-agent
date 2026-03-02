from application.usecases.webhook.generate_reply_use_case import GenerateReplyUseCase
from domain.commons.result import Result, fail
from domain.repositories.message.message_repository import MessageRepository


class WebhookApplicationService:
    def __init__(
        self,
        generate_reply_use_case: GenerateReplyUseCase,
        message_repository: MessageRepository,
    ) -> None:
        self._generate_reply_use_case = generate_reply_use_case
        self._message_repository = message_repository

    async def handle_text_message(self, reply_token: str, text: str) -> Result[None, str]:
        ai_result = await self._generate_reply_use_case.execute(text)
        if not ai_result.is_success:
            return fail(ai_result.error)
        return await self._message_repository.reply_text(reply_token, ai_result.data)
