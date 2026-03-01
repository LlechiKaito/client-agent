from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage,
)

from domain.commons.result import Result, ok


class LineMessagingClient:
    def __init__(self, channel_access_token: str) -> None:
        self._configuration = Configuration(access_token=channel_access_token)
        self._line_bot_api: AsyncMessagingApi | None = None

    def _get_api(self) -> AsyncMessagingApi:
        if self._line_bot_api is None:
            async_api_client = AsyncApiClient(self._configuration)
            self._line_bot_api = AsyncMessagingApi(async_api_client)
        return self._line_bot_api

    async def reply_text(self, reply_token: str, text: str) -> Result[None, str]:
        api = self._get_api()
        await api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)],
            )
        )
        return ok(None)
