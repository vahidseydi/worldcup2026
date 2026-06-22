from pydantic import BaseModel


class Team(BaseModel):
    code: str       # ISO 3166-1 alpha-3, matches football-data.org
    name: str
    group: str      # "A" … "L"
    strength: float = 1.0   # current mean posterior strength
