from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    PushMessageRequest,
    ReplyMessageRequest,
    TextMessage,
)

from constants.line import LINE_MESSAGE_MAX_CHARS
from domain.commons.result import Result, ok


def _split_message(text: str) -> list[str]:
    if len(text) <= LINE_MESSAGE_MAX_CHARS:
        return [text]
    chunks: list[str] = []
    while text:
        if len(text) <= LINE_MESSAGE_MAX_CHARS:
            chunks.append(text)
            break
        split_pos = text.rfind("\n", 0, LINE_MESSAGE_MAX_CHARS)
        if split_pos == -1:
            split_pos = LINE_MESSAGE_MAX_CHARS
        chunks.append(text[:split_pos])
        text = text[split_pos:].lstrip("\n")
    return chunks


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

    async def push_text(self, user_id: str, text: str) -> Result[None, str]:
        api = self._get_api()
        await api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=text)],
            )
        )
        return ok(None)

    async def push_long_text(
        self, user_id: str, text: str,
    ) -> Result[None, str]:
        api = self._get_api()
        chunks = _split_message(text)
        for chunk in chunks:
            await api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=[TextMessage(text=chunk)],
                )
            )
        return ok(None)
