from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

router = APIRouter(prefix="/simulation", tags=["simulation"])


def get_manager():
    from backend.api.app import app
    return app.state.manager


@router.get("/team/{team_code}")
async def team_probabilities(team_code: str):
    """Return probability breakdown for one team across both actual and scenario states."""
    actual = get_manager().get_actual_state()
    scenario = get_manager().get_scenario_state()

    if actual is None:
        raise HTTPException(503, "State not yet computed")

    team_code = team_code.upper()
    if team_code not in actual.team_probs:
        raise HTTPException(404, f"Team {team_code!r} not found")

    result: Dict = {"team": team_code, "actual": actual.team_probs[team_code].model_dump()}
    if scenario and team_code in scenario.team_probs:
        result["scenario"] = scenario.team_probs[team_code].model_dump()

    return result


@router.get("/summary")
async def simulation_summary():
    """Top-level snapshot: win probabilities for all teams, both states."""
    actual = get_manager().get_actual_state()
    scenario = get_manager().get_scenario_state()

    if actual is None:
        raise HTTPException(503, "State not yet computed")

    def extract_wins(state) -> Dict[str, float]:
        return {t: p.win_prob for t, p in state.team_probs.items()}

    result = {
        "n_simulations": actual.n_simulations,
        "last_updated": actual.last_updated,
        "actual_win_probs": extract_wins(actual),
    }
    if scenario:
        result["scenario_win_probs"] = extract_wins(scenario)
    return result
