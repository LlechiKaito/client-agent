from __future__ import annotations

from typing import Protocol

from domain.commons.result import Result


class MailLogRepository(Protocol):
    async def fetch_mails(self, days: int, max_count: int) -> Result[str, str]: ...
