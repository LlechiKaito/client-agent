import anthropic

from constants.ai import ANTHROPIC_MODEL
from domain.commons.result import Result, ok


class AnthropicChatClient:
    def __init__(self, api_key: str) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def generate_reply(
        self, user_message: str, system_prompt: str, max_tokens: int,
    ) -> Result[str, str]:
        response = await self._client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        reply_text = response.content[0].text
        return ok(reply_text)
