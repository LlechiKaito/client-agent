from __future__ import annotations

from typing import Protocol

from domain.commons.result import Result


class MessageRepository(Protocol):
    async def reply_text(self, reply_token: str, text: str) -> Result[None, str]:
        ...
