from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.models.match import Match, MatchResult, MatchStage

router = APIRouter(prefix="/predictions", tags=["predictions"])


def get_manager():
    from backend.api.app import app
    return app.state.manager


class PredictionRequest(BaseModel):
    match_id: int
    home_team: str
    away_team: str
    result: MatchResult
    stage: MatchStage = MatchStage.GROUP
    group: Optional[str] = None


@router.get("/", response_model=List[Match])
async def list_predictions():
    return get_manager().get_predictions()


@router.post("/")
async def add_prediction(body: PredictionRequest):
    match = Match(
        id=body.match_id,
        stage=body.stage,
        group=body.group,
        home_team=body.home_team,
        away_team=body.away_team,
        result=body.result,
        is_confirmed=False,
    )
    await get_manager().add_prediction(match)
    return {"status": "ok", "match_id": body.match_id}


@router.delete("/")
async def clear_predictions():
    await get_manager().clear_predictions()
    return {"status": "cleared"}


@router.delete("/{match_id}")
async def remove_prediction(match_id: int):
    predictions = get_manager().get_predictions()
    remaining = [p for p in predictions if p.id != match_id]
    if len(remaining) == len(predictions):
        raise HTTPException(404, f"Prediction {match_id} not found")
    await get_manager().clear_predictions()
    for p in remaining:
        await get_manager().add_prediction(p)
    return {"status": "removed", "match_id": match_id}
