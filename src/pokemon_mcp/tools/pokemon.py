from collections.abc import Callable

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from pokemon_mcp.exceptions import PokeAPIError, PokemonTypeNotFound
from pokemon_mcp.models import PokemonTypeListing
from pokemon_mcp.services.pokemon_service import PokemonService


def register_pokemon_tools(
    server: MCPServer,
    get_service: Callable[[], PokemonService],
) -> None:
    """Register Pokemon tools on an MCP server."""

    @server.tool(
        name="get_pokemon_by_type",
        title="Get Pokemon by type",
        description=(
            "List Pokemon that have one elemental type. "
            "Pass a type name such as fire, water, or grass."
        ),
    )
    async def get_pokemon_by_type(pokemon_type: str) -> PokemonTypeListing:
        """List Pokemon of one elemental type.

        Args:
            pokemon_type: Type name such as fire, water, or grass.
        """
        try:
            return await get_service().get_pokemon_by_type(pokemon_type)
        except ValueError as exc:
            raise ToolError(str(exc)) from exc
        except PokemonTypeNotFound as exc:
            raise ToolError(str(exc)) from exc
        except PokeAPIError as exc:
            raise ToolError(str(exc)) from exc
