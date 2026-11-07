"""Pokemon MCP server."""

__version__ = "0.1.0"


def main() -> None:
    """Console-script entry point."""
    from pokemon_mcp.server import main as serve

    serve()
