from __future__ import annotations

from typing import Protocol

from domain.commons.result import Result
from domain.entities.conversation.message import ConversationMessage


class AiChatRepository(Protocol):
    async def generate_reply(
        self,
        user_message: str,
        system_prompt: str,
        max_tokens: int,
        history: list[ConversationMessage] | None = None,
    ) -> Result[str, str]: ...
