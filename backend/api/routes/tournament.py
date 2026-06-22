from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from backend.models.tournament import TournamentState
from backend.models.match import Match
from typing import List

router = APIRouter(prefix="/tournament", tags=["tournament"])

_manager = None  # injected at startup via app state


def get_manager():
    from backend.api.app import app
    return app.state.manager


@router.get("/state", include_in_schema=False)
async def state_redirect():
    """Redirect stale clients that hit /state instead of /state/actual."""
    return RedirectResponse(url="/api/tournament/state/actual", status_code=301)


@router.get("/state/actual", response_model=TournamentState)
async def get_actual_state():
    state = get_manager().get_actual_state()
    if state is None:
        raise HTTPException(503, "State not yet computed — waiting for match data")
    return state


@router.get("/state/scenario", response_model=TournamentState)
async def get_scenario_state():
    state = get_manager().get_scenario_state()
    if state is None:
        raise HTTPException(503, "State not yet computed — waiting for match data")
    return state


@router.get("/matches", response_model=List[Match])
async def get_matches():
    return get_manager().get_all_matches()
