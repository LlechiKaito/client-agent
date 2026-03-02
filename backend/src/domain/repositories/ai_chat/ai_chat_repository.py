from __future__ import annotations

from typing import Protocol

from domain.commons.result import Result


class AiChatRepository(Protocol):
    async def generate_reply(
        self, user_message: str, system_prompt: str, max_tokens: int,
    ) -> Result[str, str]: ...
