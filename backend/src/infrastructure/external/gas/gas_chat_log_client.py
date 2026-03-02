import httpx

from domain.commons.result import Result, fail, ok


class GasChatLogClient:
    def __init__(self, webapp_url: str) -> None:
        self._webapp_url = webapp_url

    async def fetch_logs(self, days: int) -> Result[str, str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self._webapp_url,
                params={"days": days},
                follow_redirects=True,
            )
        if response.status_code != httpx.codes.OK:
            return fail(f"GAS WebApp returned status {response.status_code}")
        return ok(response.text)
