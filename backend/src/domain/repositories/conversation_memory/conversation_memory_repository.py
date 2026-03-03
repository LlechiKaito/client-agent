from __future__ import annotations

from typing import Protocol

from domain.entities.conversation.message import ConversationMessage


class ConversationMemoryRepository(Protocol):
    def add_message(self, user_id: str, message: ConversationMessage) -> None: ...

    def get_history(self, user_id: str) -> list[ConversationMessage]: ...

    def clear(self, user_id: str) -> None: ...
