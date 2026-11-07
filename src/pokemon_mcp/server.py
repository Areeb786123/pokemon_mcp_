from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import JSONResponse

from pokemon_mcp import __version__
from pokemon_mcp.clients.pokeapi_client import PokeAPIClient
from pokemon_mcp.config import Settings
from pokemon_mcp.services.pokemon_service import PokemonService
from pokemon_mcp.tools.pokemon import register_pokemon_tools


@dataclass
class _Runtime:
    service: PokemonService | None = None


def create_server(
    settings: Settings | None = None,
    *,
    service: PokemonService | None = None,
) -> MCPServer:
    """Build the Pokemon MCP server.

    Pass ``service`` in tests. When it is omitted, the server opens a PokeAPI
    client for the process lifetime.
    """
    settings = settings or Settings()
    runtime = _Runtime(service=service)

    @asynccontextmanager
    async def lifespan(_server: MCPServer) -> AsyncIterator[None]:
        if runtime.service is not None:
            yield None
            return
        async with PokeAPIClient(
            base_url=settings.pokeapi_base_url,
            timeout_seconds=settings.pokeapi_timeout_seconds,
        ) as client:
            runtime.service = PokemonService(client)
            try:
                yield None
            finally:
                runtime.service = None

    def get_service() -> PokemonService:
        if runtime.service is None:
            raise ToolError("Pokemon service is unavailable")
        return runtime.service

    server = MCPServer(
        name="pokemon",
        title="Pokemon",
        description="Look up Pokemon from the PokeAPI.",
        instructions=(
            "Use get_pokemon_by_type to list Pokemon of one elemental type. "
            "Pass a type name such as fire, water, or grass."
        ),
        version=__version__,
        lifespan=lifespan,
        log_level=settings.log_level,
    )
    register_pokemon_tools(server, get_service)
    _register_health_route(server)
    return server


def http_run_kwargs(settings: Settings) -> dict[str, object]:
    """Arguments for the streamable HTTP transport."""
    kwargs: dict[str, object] = {
        "host": settings.host,
        "port": settings.port,
        "stateless_http": True,
        "json_response": True,
    }
    if settings.allowed_hosts or settings.allowed_origins:
        kwargs["transport_security"] = TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=list(settings.allowed_hosts),
            allowed_origins=list(settings.allowed_origins),
        )
    return kwargs


def main() -> None:
    """Run the server on stdio or streamable HTTP."""
    load_dotenv()
    settings = Settings.from_env()
    server = create_server(settings)
    if settings.transport == "stdio":
        server.run(transport="stdio")
        return
    server.run(transport="streamable-http", **http_run_kwargs(settings))


def _register_health_route(server: MCPServer) -> None:
    @server.custom_route("/health", methods=["GET"], include_in_schema=False)
    async def health(_request: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})
