from pydantic import BaseModel, Field


class PokemonSummary(BaseModel):
    """One Pokemon that belongs to a type."""

    name: str
    url: str
    slot: int


class PokemonTypeListing(BaseModel):
    """Pokemon that share one elemental type."""

    pokemon_type: str
    count: int = Field(ge=0)
    pokemon: list[PokemonSummary]
