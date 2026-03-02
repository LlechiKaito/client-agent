from __future__ import annotations

from typing import Protocol

from domain.commons.result import Result


class ChatLogRepository(Protocol):
    async def fetch_logs(self, days: int) -> Result[str, str]: ...
