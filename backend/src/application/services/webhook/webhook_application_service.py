from application.usecases.webhook.generate_reply_use_case import GenerateReplyUseCase
from constants.line import THINKING_MESSAGE
from domain.commons.result import Result
from domain.repositories.message.message_repository import MessageRepository


class WebhookApplicationService:
    def __init__(
        self,
        generate_reply_use_case: GenerateReplyUseCase,
        message_repository: MessageRepository,
    ) -> None:
        self._generate_reply_use_case = generate_reply_use_case
        self._message_repository = message_repository

    async def send_thinking_reply(self, reply_token: str) -> Result[None, str]:
        return await self._message_repository.reply_text(reply_token, THINKING_MESSAGE)

    async def generate_and_push_reply(self, user_id: str, text: str) -> Result[None, str]:
        ai_result = await self._generate_reply_use_case.execute(text)
        if not ai_result.is_success:
            return ai_result
        return await self._message_repository.push_text(user_id, ai_result.data)
