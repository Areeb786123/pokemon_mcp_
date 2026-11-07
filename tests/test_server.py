from mcp.server.transport_security import TransportSecuritySettings
from starlette.testclient import TestClient

from pokemon_mcp.config import Settings
from pokemon_mcp.server import create_server, http_run_kwargs
from pokemon_mcp.services.pokemon_service import PokemonService
from tests.services.test_pokemon_service import RecordingClient


def test_http_run_kwargs_enable_host_security_when_configured():
    settings = Settings(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        allowed_hosts=("localhost:*",),
        allowed_origins=("http://localhost:*",),
    )

    kwargs = http_run_kwargs(settings)

    assert kwargs["host"] == "0.0.0.0"
    assert kwargs["port"] == 8000
    assert kwargs["stateless_http"] is True
    assert kwargs["json_response"] is True
    security = kwargs["transport_security"]
    assert isinstance(security, TransportSecuritySettings)
    assert security.allowed_hosts == ["localhost:*"]
    assert security.allowed_origins == ["http://localhost:*"]


def test_health_endpoint_returns_ok():
    server = create_server(service=PokemonService(RecordingClient()))
    app = server.streamable_http_app()

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
