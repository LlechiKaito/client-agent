import anthropic

from constants.ai import ANTHROPIC_MODEL
from domain.commons.result import Result, ok
from domain.entities.conversation.message import ConversationMessage


class AnthropicChatClient:
    def __init__(self, api_key: str) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def generate_reply(
        self,
        user_message: str,
        system_prompt: str,
        max_tokens: int,
        history: list[ConversationMessage] | None = None,
    ) -> Result[str, str]:
        messages: list[dict[str, str]] = []
        if history:
            messages.extend(
                {"role": msg.role, "content": msg.content} for msg in history
            )
        messages.append({"role": "user", "content": user_message})

        response = await self._client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
        )
        reply_text = response.content[0].text
        return ok(reply_text)
