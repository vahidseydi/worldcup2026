"""
Admin endpoints for seeding tournament state without a live API key.
Useful for local dev, demos, and testing.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Optional

from backend.models.match import Match, MatchStage, MatchResult

router = APIRouter(prefix="/admin", tags=["admin"])


def get_manager():
    from backend.api.app import app
    return app.state.manager


class FixtureInput(BaseModel):
    match_id: int
    home_team: str
    away_team: str
    group: Optional[str] = None
    stage: MatchStage = MatchStage.GROUP
    result: Optional[MatchResult] = None
    is_confirmed: bool = False


class SeedRequest(BaseModel):
    fixtures: List[FixtureInput]


@router.post("/seed")
async def seed_tournament(body: SeedRequest):
    """
    Seed the tournament state from a list of fixtures.
    Group structure is derived from fixtures that have a group field.
    Confirmed fixtures (is_confirmed=True) update the actual state;
    all fixtures establish the group/team structure.
    """
    matches = [
        Match(
            id=f.match_id,
            stage=f.stage,
            group=f.group,
            home_team=f.home_team,
            away_team=f.away_team,
            result=f.result,
            is_confirmed=f.is_confirmed,
        )
        for f in body.fixtures
    ]
    await get_manager().ingest_api_matches(matches)
    return {"status": "seeded", "fixture_count": len(matches)}
