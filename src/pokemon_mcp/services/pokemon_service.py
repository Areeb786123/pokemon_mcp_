from typing import Protocol

import httpx

from pokemon_mcp.exceptions import PokeAPIError, PokemonTypeNotFound
from pokemon_mcp.models import PokemonSummary, PokemonTypeListing


class PokemonTypeReader(Protocol):
    """Client capability required by PokemonService."""

    async def get_pokemon_by_type(self, pokemon_type: str) -> list[dict[str, object]]: ...


class PokemonService:
    """Application service for Pokemon type lookups."""

    def __init__(self, pokemon_client: PokemonTypeReader) -> None:
        self._pokemon_client = pokemon_client

    async def get_pokemon_by_type(self, pokemon_type: str) -> PokemonTypeListing:
        normalized = pokemon_type.strip().lower()
        if not normalized:
            raise ValueError("Pokemon type cannot be empty")

        try:
            raw_pokemon = await self._pokemon_client.get_pokemon_by_type(normalized)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise PokemonTypeNotFound(normalized) from exc
            raise PokeAPIError(
                f"PokeAPI request failed with status {exc.response.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            raise PokeAPIError("PokeAPI request failed") from exc

        pokemon = [PokemonSummary.model_validate(item) for item in raw_pokemon]
        return PokemonTypeListing(
            pokemon_type=normalized,
            count=len(pokemon),
            pokemon=pokemon,
        )
