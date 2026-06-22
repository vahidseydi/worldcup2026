from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class MatchStage(str, Enum):
    GROUP = "group"
    R32 = "r32"
    R16 = "r16"
    QF = "qf"
    SF = "sf"
    FINAL = "final"


class MatchResult(str, Enum):
    HOME_WIN = "home_win"
    DRAW = "draw"
    AWAY_WIN = "away_win"


class Match(BaseModel):
    id: int
    stage: MatchStage
    group: Optional[str] = None         # set for group-stage matches
    home_team: str                       # team code
    away_team: str
    scheduled_at: Optional[datetime] = None
    result: Optional[MatchResult] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    is_confirmed: bool = False           # True = result from official API
