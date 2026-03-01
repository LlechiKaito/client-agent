from application.usecases.webhook.echo_message_use_case import EchoMessageUseCase
from domain.commons.result import Result


class WebhookApplicationService:
    def __init__(self, echo_message_use_case: EchoMessageUseCase) -> None:
        self._echo_message_use_case = echo_message_use_case

    async def handle_text_message(self, reply_token: str, text: str) -> Result[None, str]:
        return await self._echo_message_use_case.execute(reply_token, text)
