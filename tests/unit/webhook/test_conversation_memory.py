import time
from unittest.mock import patch

from domain.entities.conversation.message import ConversationMessage
from infrastructure.memory.in_memory_conversation_store import InMemoryConversationStore

USER_A = "Uaaa"
USER_B = "Ubbb"


def _msg(role: str, content: str, ts: float = 0.0) -> ConversationMessage:
    return ConversationMessage(role=role, content=content, timestamp=ts)


def test_should_store_and_retrieve_messages() -> None:
    store = InMemoryConversationStore()

    store.add_message(USER_A, _msg("user", "こんにちは"))
    store.add_message(USER_A, _msg("assistant", "お疲れ様です"))

    history = store.get_history(USER_A)
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[1].role == "assistant"


def test_should_isolate_users() -> None:
    store = InMemoryConversationStore()

    store.add_message(USER_A, _msg("user", "Aのメッセージ"))
    store.add_message(USER_B, _msg("user", "Bのメッセージ"))

    assert len(store.get_history(USER_A)) == 1
    assert len(store.get_history(USER_B)) == 1
    assert store.get_history(USER_A)[0].content == "Aのメッセージ"
    assert store.get_history(USER_B)[0].content == "Bのメッセージ"


def test_should_return_empty_for_unknown_user() -> None:
    store = InMemoryConversationStore()

    assert store.get_history("unknown") == []


def test_should_limit_to_max_turns() -> None:
    store = InMemoryConversationStore()

    for i in range(12):
        role = "user" if i % 2 == 0 else "assistant"
        store.add_message(USER_A, _msg(role, f"msg-{i}"))

    history = store.get_history(USER_A)
    assert len(history) == 10
    assert history[0].content == "msg-2"
    assert history[-1].content == "msg-11"


def test_should_clear_user_history() -> None:
    store = InMemoryConversationStore()

    store.add_message(USER_A, _msg("user", "テスト"))
    store.clear(USER_A)

    assert store.get_history(USER_A) == []


def test_should_evict_expired_entries() -> None:
    store = InMemoryConversationStore()
    now = time.time()

    with patch("infrastructure.memory.in_memory_conversation_store.time") as mock_time:
        mock_time.time.return_value = now
        store.add_message(USER_A, _msg("user", "古いメッセージ"))

        mock_time.time.return_value = now + 3601
        store.add_message(USER_B, _msg("user", "新しいメッセージ"))

        assert store.get_history(USER_A) == []
        assert len(store.get_history(USER_B)) == 1


def test_should_not_evict_within_ttl() -> None:
    store = InMemoryConversationStore()
    now = time.time()

    with patch("infrastructure.memory.in_memory_conversation_store.time") as mock_time:
        mock_time.time.return_value = now
        store.add_message(USER_A, _msg("user", "まだ有効"))

        mock_time.time.return_value = now + 3500
        history = store.get_history(USER_A)

        assert len(history) == 1
