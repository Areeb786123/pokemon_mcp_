# Pokemon MCP

MCP server that lists Pokémon of one elemental type from the [PokéAPI](https://pokeapi.co/).

The server exposes one tool, `get_pokemon_by_type`. Local clients use stdio. A hosted deployment uses streamable HTTP on port 8000, with a `/health` check.

## Layout

```text
src/pokemon_mcp/
  server.py            process entry and transport selection
  config.py            environment settings
  models.py            response models
  exceptions.py        domain errors
  clients/             PokéAPI HTTP client
  services/            type lookup rules
  tools/               MCP tool registration
tests/                 client, service, tool, and server tests
```

## Setup

Requires Python 3.14 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env
```

## Run locally

stdio, for Cursor or another MCP client:

```bash
uv run pokemon-mcp
```

Cursor config:

```json
{
  "mcpServers": {
    "pokemon": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/pokemon_mcp", "pokemon-mcp"]
    }
  }
}
```

Host over HTTP:

```bash
MCP_TRANSPORT=streamable-http uv run pokemon-mcp
```

The MCP endpoint is `http://127.0.0.1:8000/mcp`. Health is `http://127.0.0.1:8000/health`.

## Docker

```bash
docker build -t pokemon-mcp .
docker run --rm -p 8000:8000 pokemon-mcp
```

Set `MCP_ALLOWED_HOSTS` and `MCP_ALLOWED_ORIGINS` when the HTTP server is reachable beyond localhost. See `.env.example`.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `MCP_TRANSPORT` | `stdio` | `stdio` or `streamable-http` |
| `MCP_HOST` | `0.0.0.0` | HTTP bind address |
| `MCP_PORT` | `8000` | HTTP port |
| `LOG_LEVEL` | `INFO` | Server log level |
| `POKEAPI_BASE_URL` | `https://pokeapi.co/api/v2` | Upstream API |
| `POKEAPI_TIMEOUT_SECONDS` | `10` | Upstream timeout |
| `MCP_ALLOWED_HOSTS` | empty | Comma-separated Host allow list |
| `MCP_ALLOWED_ORIGINS` | empty | Comma-separated Origin allow list |

## Tests

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```
