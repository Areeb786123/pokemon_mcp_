import httpx
import pytest
import respx

from pokemon_mcp.clients.pokeapi_client import PokeAPIClient

BASE_URL = "https://pokeapi.co/api/v2"


@pytest.mark.asyncio
@respx.mock
async def test_get_pokemon_by_type_success():
    # Arrange: Mock successful PokéAPI response
    respx.get(f"{BASE_URL}/type/fire").mock(
        return_value=httpx.Response(
            200,
            json={
                "pokemon": [
                    {
                        "pokemon": {
                            "name": "charmander",
                            "url": "https://pokeapi.co/api/v2/pokemon/4/",
                        },
                        "slot": 1,
                    },
                    {
                        "pokemon": {
                            "name": "charizard",
                            "url": "https://pokeapi.co/api/v2/pokemon/6/",
                        },
                        "slot": 2,
                    },
                ]
            },
        )
    )

    client = PokeAPIClient()

    try:
        # Act
        result = await client.get_pokemon_by_type("fire")

        # Assert
        assert len(result) == 2
        assert result[0]["name"] == "charmander"
        assert result[1]["name"] == "charizard"
        assert result[0]["slot"] == 1
        assert result[1]["slot"] == 2

    finally:
        await client.close()


@pytest.mark.asyncio
async def test_close_closes_the_http_client():
    http_client = httpx.AsyncClient(base_url=BASE_URL)
    client = PokeAPIClient(client=http_client)

    await client.close()

    assert http_client.is_closed


@pytest.mark.asyncio
async def test_context_manager_closes_the_http_client():
    http_client = httpx.AsyncClient(base_url=BASE_URL)

    async with PokeAPIClient(client=http_client):
        assert http_client.is_closed is False

    assert http_client.is_closed


@pytest.mark.asyncio
@respx.mock
async def test_get_pokemon_by_type_case_insensitive():
    # Arrange
    route = respx.get(f"{BASE_URL}/type/fire").mock(
        return_value=httpx.Response(
            200,
            json={"pokemon": []},
        )
    )

    client = PokeAPIClient()

    try:
        # Act
        result = await client.get_pokemon_by_type("FIRE")

        # Assert
        assert result == []
        assert route.called

    finally:
        await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_get_pokemon_by_type_empty_response():
    # Arrange
    respx.get(f"{BASE_URL}/type/fire").mock(
        return_value=httpx.Response(
            200,
            json={},
        )
    )

    client = PokeAPIClient()

    try:
        # Act
        result = await client.get_pokemon_by_type("fire")

        # Assert
        assert result == []

    finally:
        await client.close()


@pytest.mark.asyncio
@respx.mock
async def test_get_pokemon_by_type_api_error():
    # Arrange
    respx.get(f"{BASE_URL}/type/fire").mock(return_value=httpx.Response(500))

    client = PokeAPIClient()

    try:
        # Act & Assert
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_pokemon_by_type("fire")

    finally:
        await client.close()
