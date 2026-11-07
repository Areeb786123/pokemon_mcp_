import httpx
import pytest

from pokemon_mcp.exceptions import PokeAPIError, PokemonTypeNotFound
from pokemon_mcp.services.pokemon_service import PokemonService

CHARMANDER = {
    "name": "charmander",
    "url": "https://pokeapi.co/api/v2/pokemon/4/",
    "slot": 1,
}


class RecordingClient:
    def __init__(
        self,
        payload: list[dict[str, object]] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.payload = payload or []
        self.error = error
        self.types: list[str] = []

    async def get_pokemon_by_type(self, pokemon_type: str) -> list[dict[str, object]]:
        self.types.append(pokemon_type)
        if self.error is not None:
            raise self.error
        return self.payload


def http_status_error(status_code: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://pokeapi.co/api/v2/type/fire")
    response = httpx.Response(status_code, request=request)
    return httpx.HTTPStatusError("request failed", request=request, response=response)


@pytest.mark.asyncio
async def test_get_pokemon_by_type_normalizes_input_and_maps_results():
    client = RecordingClient(payload=[CHARMANDER])
    service = PokemonService(client)

    listing = await service.get_pokemon_by_type("  Fire  ")

    assert client.types == ["fire"]
    assert listing.pokemon_type == "fire"
    assert listing.count == 1
    assert listing.pokemon[0].name == "charmander"
    assert listing.pokemon[0].slot == 1


@pytest.mark.asyncio
async def test_get_pokemon_by_type_rejects_blank_input():
    service = PokemonService(RecordingClient())

    with pytest.raises(ValueError, match="cannot be empty"):
        await service.get_pokemon_by_type("   ")


@pytest.mark.asyncio
async def test_get_pokemon_by_type_maps_not_found():
    service = PokemonService(RecordingClient(error=http_status_error(404)))

    with pytest.raises(PokemonTypeNotFound, match="not-a-type"):
        await service.get_pokemon_by_type("Not-A-Type")


@pytest.mark.asyncio
async def test_get_pokemon_by_type_maps_upstream_status():
    service = PokemonService(RecordingClient(error=http_status_error(500)))

    with pytest.raises(PokeAPIError, match="status 500"):
        await service.get_pokemon_by_type("fire")


@pytest.mark.asyncio
async def test_get_pokemon_by_type_maps_transport_errors():
    request = httpx.Request("GET", "https://pokeapi.co/api/v2/type/fire")
    service = PokemonService(RecordingClient(error=httpx.ConnectError("down", request=request)))

    with pytest.raises(PokeAPIError, match="request failed"):
        await service.get_pokemon_by_type("fire")
