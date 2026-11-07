import logging

import httpx

logger = logging.getLogger(__name__)


class PokeAPIClient:
    """Async client for the public PokeAPI."""

    DEFAULT_BASE_URL = "https://pokeapi.co/api/v2"

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout_seconds: float = 10.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._client = client or httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=httpx.Timeout(timeout_seconds, connect=min(5.0, timeout_seconds)),
        )

    async def __aenter__(self) -> PokeAPIClient:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.close()

    async def get_pokemon_by_type(self, pokemon_type: str) -> list[dict[str, object]]:
        path = f"/type/{pokemon_type.lower()}"
        response = await self._client.get(path)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.warning("PokeAPI request failed: %s status=%s", path, response.status_code)
            raise
        data = response.json()
        return [
            {
                "name": item["pokemon"]["name"],
                "url": item["pokemon"]["url"],
                "slot": item["slot"],
            }
            for item in data.get("pokemon", [])
        ]

    async def close(self) -> None:
        await self._client.aclose()
