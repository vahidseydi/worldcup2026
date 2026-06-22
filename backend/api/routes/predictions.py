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
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    result: Optional[MatchResult] = None   # auto-derived from scores when omitted
    stage: MatchStage = MatchStage.GROUP
    group: Optional[str] = None


@router.get("/", response_model=List[Match])
async def list_predictions():
    return get_manager().get_predictions()


@router.post("/")
async def add_prediction(body: PredictionRequest):
    result = body.result
    if result is None:
        if body.home_score is None or body.away_score is None:
            raise HTTPException(422, "Provide either result or both home_score and away_score")
        if body.home_score > body.away_score:
            result = MatchResult.HOME_WIN
        elif body.home_score < body.away_score:
            result = MatchResult.AWAY_WIN
        else:
            result = MatchResult.DRAW

    match = Match(
        id=body.match_id,
        stage=body.stage,
        group=body.group,
        home_team=body.home_team,
        away_team=body.away_team,
        home_score=body.home_score,
        away_score=body.away_score,
        result=result,
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
