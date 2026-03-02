import anthropic

from constants.ai import ANTHROPIC_MAX_TOKENS, ANTHROPIC_MODEL, SECRETARY_SYSTEM_PROMPT
from domain.commons.result import Result, ok


class AnthropicChatClient:
    def __init__(self, api_key: str) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def generate_reply(self, user_message: str) -> Result[str, str]:
        response = await self._client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=ANTHROPIC_MAX_TOKENS,
            system=SECRETARY_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        reply_text = response.content[0].text
        return ok(reply_text)
