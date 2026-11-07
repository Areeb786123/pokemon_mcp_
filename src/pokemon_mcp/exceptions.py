class PokemonMCPError(Exception):
    """Base error for Pokemon MCP domain failures."""


class PokemonTypeNotFound(PokemonMCPError):
    """The requested elemental type does not exist in PokeAPI."""

    def __init__(self, pokemon_type: str) -> None:
        self.pokemon_type = pokemon_type
        super().__init__(f"Unknown Pokemon type: {pokemon_type}")


class PokeAPIError(PokemonMCPError):
    """PokeAPI could not be reached or returned an unexpected error."""
