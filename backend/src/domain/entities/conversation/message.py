from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationMessage:
    role: str
    content: str
    timestamp: float
