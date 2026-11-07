import pytest
from mcp.server.mcpserver.exceptions import ToolError

from pokemon_mcp.server import create_server
from pokemon_mcp.services.pokemon_service import PokemonService
from tests.services.test_pokemon_service import CHARMANDER, RecordingClient, http_status_error


@pytest.mark.asyncio
async def test_server_lists_pokemon_tool():
    server = create_server(service=PokemonService(RecordingClient()))

    tools = await server.list_tools()

    assert [tool.name for tool in tools] == ["get_pokemon_by_type"]
    assert tools[0].description


@pytest.mark.asyncio
async def test_get_pokemon_by_type_tool_returns_listing():
    server = create_server(service=PokemonService(RecordingClient(payload=[CHARMANDER])))

    result = await server.call_tool("get_pokemon_by_type", {"pokemon_type": "Fire"})

    assert result.is_error is False
    assert result.structured_content == {
        "pokemon_type": "fire",
        "count": 1,
        "pokemon": [
            {
                "name": "charmander",
                "url": "https://pokeapi.co/api/v2/pokemon/4/",
                "slot": 1,
            }
        ],
    }


@pytest.mark.asyncio
async def test_get_pokemon_by_type_tool_reports_blank_type():
    server = create_server(service=PokemonService(RecordingClient()))

    with pytest.raises(ToolError, match="cannot be empty"):
        await server.call_tool("get_pokemon_by_type", {"pokemon_type": " "})


@pytest.mark.asyncio
async def test_get_pokemon_by_type_tool_reports_unknown_type():
    server = create_server(service=PokemonService(RecordingClient(error=http_status_error(404))))

    with pytest.raises(ToolError, match="Unknown Pokemon type: missing"):
        await server.call_tool("get_pokemon_by_type", {"pokemon_type": "missing"})


@pytest.mark.asyncio
async def test_tool_reports_when_service_is_not_started():
    server = create_server()

    with pytest.raises(ToolError, match="unavailable"):
        await server.call_tool("get_pokemon_by_type", {"pokemon_type": "fire"})
