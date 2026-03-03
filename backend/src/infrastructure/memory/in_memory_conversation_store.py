import time

from constants.ai import CONVERSATION_MAX_TURNS, CONVERSATION_TTL_SECONDS
from domain.entities.conversation.message import ConversationMessage


class InMemoryConversationStore:
    def __init__(self) -> None:
        self._store: dict[str, list[ConversationMessage]] = {}
        self._last_access: dict[str, float] = {}

    def add_message(self, user_id: str, message: ConversationMessage) -> None:
        self._evict_expired()
        if user_id not in self._store:
            self._store[user_id] = []
        self._store[user_id].append(message)
        max_messages = CONVERSATION_MAX_TURNS * 2
        if len(self._store[user_id]) > max_messages:
            self._store[user_id] = self._store[user_id][-max_messages:]
        self._last_access[user_id] = time.time()

    def get_history(self, user_id: str) -> list[ConversationMessage]:
        self._evict_expired()
        return list(self._store.get(user_id, []))

    def clear(self, user_id: str) -> None:
        self._store.pop(user_id, None)
        self._last_access.pop(user_id, None)

    def _evict_expired(self) -> None:
        now = time.time()
        expired_users = [
            uid for uid, last in self._last_access.items()
            if now - last > CONVERSATION_TTL_SECONDS
        ]
        for uid in expired_users:
            self._store.pop(uid, None)
            self._last_access.pop(uid, None)
