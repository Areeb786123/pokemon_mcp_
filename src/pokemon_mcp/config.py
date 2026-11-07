import os
from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Transport = Literal["stdio", "streamable-http"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseModel):
    """Runtime settings loaded from the environment."""

    model_config = ConfigDict(frozen=True)

    pokeapi_base_url: str = "https://pokeapi.co/api/v2"
    pokeapi_timeout_seconds: float = Field(default=10.0, gt=0)
    transport: Transport = "stdio"
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    log_level: LogLevel = "INFO"
    allowed_hosts: tuple[str, ...] = ()
    allowed_origins: tuple[str, ...] = ()

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        source = os.environ if env is None else env
        data: dict[str, object] = {}
        if value := source.get("POKEAPI_BASE_URL"):
            data["pokeapi_base_url"] = value
        if value := source.get("POKEAPI_TIMEOUT_SECONDS"):
            data["pokeapi_timeout_seconds"] = value
        if value := source.get("MCP_TRANSPORT"):
            data["transport"] = value
        if value := source.get("MCP_HOST"):
            data["host"] = value
        if value := source.get("MCP_PORT"):
            data["port"] = value
        if value := source.get("LOG_LEVEL"):
            data["log_level"] = value.upper()
        if value := source.get("MCP_ALLOWED_HOSTS"):
            data["allowed_hosts"] = _split_csv(value)
        if value := source.get("MCP_ALLOWED_ORIGINS"):
            data["allowed_origins"] = _split_csv(value)
        return cls.model_validate(data)


def _split_csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())
