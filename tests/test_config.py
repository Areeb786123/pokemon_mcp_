import pytest
from pydantic import ValidationError

from pokemon_mcp.config import Settings


def test_settings_defaults_are_local_stdio():
    settings = Settings()

    assert settings.transport == "stdio"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.pokeapi_base_url == "https://pokeapi.co/api/v2"
    assert settings.pokeapi_timeout_seconds == 10.0
    assert settings.log_level == "INFO"
    assert settings.allowed_hosts == ()


def test_settings_from_env_reads_host_values():
    settings = Settings.from_env(
        {
            "POKEAPI_BASE_URL": "https://example.test/api/v2",
            "POKEAPI_TIMEOUT_SECONDS": "3.5",
            "MCP_TRANSPORT": "streamable-http",
            "MCP_HOST": "127.0.0.1",
            "MCP_PORT": "9000",
            "LOG_LEVEL": "debug",
            "MCP_ALLOWED_HOSTS": "localhost:*, 127.0.0.1:*",
            "MCP_ALLOWED_ORIGINS": "http://localhost:*",
        }
    )

    assert settings.pokeapi_base_url == "https://example.test/api/v2"
    assert settings.pokeapi_timeout_seconds == 3.5
    assert settings.transport == "streamable-http"
    assert settings.host == "127.0.0.1"
    assert settings.port == 9000
    assert settings.log_level == "DEBUG"
    assert settings.allowed_hosts == ("localhost:*", "127.0.0.1:*")
    assert settings.allowed_origins == ("http://localhost:*",)


def test_settings_reject_unknown_transport():
    with pytest.raises(ValidationError):
        Settings.from_env({"MCP_TRANSPORT": "websocket"})
