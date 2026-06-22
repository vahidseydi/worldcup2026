from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel


class GroupStanding(BaseModel):
    team: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    points: int

    @property
    def goal_diff(self) -> int:
        return self.goals_for - self.goals_against


class TeamProbabilities(BaseModel):
    team: str
    qualify_prob: float                          # P(advance from group stage)
    round_probs: Dict[str, float]                # round id -> P(reach that round)
    win_prob: float                              # P(win tournament)
    opponents: Dict[str, Dict[str, float]] = {} # round -> {team_code -> P(face | reach round)}


class TournamentState(BaseModel):
    group_standings: Dict[str, List[GroupStanding]]   # group -> ordered standings
    team_probs: Dict[str, TeamProbabilities]          # team code -> probabilities
    n_simulations: int
    last_updated: Optional[str] = None
    is_scenario: bool = False
