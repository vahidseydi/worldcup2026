"""
Manages two independent tournament states:
  - actual_state  : updated only from confirmed API results
  - scenario_state: starts from actual_state, extended by user predictions

Both share the same ParticleFilter + MonteCarloSimulator pipeline.
"""

from __future__ import annotations
import asyncio
import copy
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.core.monte_carlo import Fixture, MonteCarloSimulator
from backend.core.particle_filter import ParticleFilter
from backend.core.prior import compute_prior
from backend.models.match import Match, MatchResult, MatchStage
from backend.models.tournament import GroupStanding, TeamProbabilities, TournamentState
from backend.services.config import load_settings

logger = logging.getLogger(__name__)

_ROUND_IDS = ["qualify", "r32", "r16", "qf", "sf", "final", "winner"]


def _result_str(result: MatchResult) -> str:
    return result.value


def _build_fixtures(matches: List[Match]) -> List[Fixture]:
    return [
        Fixture(
            home=m.home_team,
            away=m.away_team,
            group=m.group,
            result=_result_str(m.result) if m.result else None,
            match_id=m.id,
            stage=m.stage.value,
            home_score=m.home_score,
            away_score=m.away_score,
        )
        for m in matches
    ]


def _build_groups(matches: List[Match]) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {}
    for m in matches:
        if m.stage == MatchStage.GROUP and m.group:
            # API returns "GROUP_A" — normalise to "A"
            grp = m.group.removeprefix("GROUP_")
            if grp not in groups:
                groups[grp] = []
            for t in (m.home_team, m.away_team):
                if t not in groups[grp]:
                    groups[grp].append(t)
    return groups


def _probs_to_model(team: str, probs: dict) -> TeamProbabilities:
    return TeamProbabilities(
        team=team,
        qualify_prob=probs.get("qualify", 0.0),
        round_probs={r: probs.get(r, 0.0) for r in _ROUND_IDS[1:]},
        win_prob=probs.get("winner", 0.0),
        opponents=probs.get("opponents", {}),
    )


class _State:
    def __init__(self, prior_sources: List[str], team_codes: List[str]) -> None:
        prior = compute_prior(prior_sources)
        self.pf = ParticleFilter(team_codes, prior)
        self.confirmed_results: List[Match] = []
        self.predicted_results: List[Match] = []
        self.last_tournament_state: Optional[TournamentState] = None

    def apply_result(self, match: Match) -> None:
        assert match.result is not None
        self.pf.update(
            match.home_team,
            match.away_team,
            _result_str(match.result),
            home_goals=match.home_score,
            away_goals=match.away_score,
        )

    def all_matches(self) -> List[Match]:
        return self.confirmed_results + self.predicted_results


class StateManager:
    def __init__(self) -> None:
        cfg = load_settings()
        self._prior_sources: List[str] = cfg["prior"]["default_sources"]
        self._simulator = MonteCarloSimulator()
        self._lock = asyncio.Lock()

        self._all_matches: List[Match] = []
        self._team_codes: List[str] = []
        self._groups: Dict[str, List[str]] = {}

        self._actual = _State(self._prior_sources, [])
        self._scenario = _State(self._prior_sources, [])
        self._scenario_predictions: List[Match] = []

    # ------------------------------------------------------------------
    # Called by the API poller whenever new matches arrive
    # ------------------------------------------------------------------

    async def ingest_api_matches(self, matches: List[Match]) -> None:
        async with self._lock:
            self._all_matches = matches
            new_groups = _build_groups(matches)
            if new_groups != self._groups:
                self._groups = new_groups
                team_codes = sorted({t for grp in new_groups.values() for t in grp})
                self._team_codes = team_codes
                self._actual = _State(self._prior_sources, team_codes)
                self._scenario = _State(self._prior_sources, team_codes)

            # replay all confirmed results onto actual state
            confirmed = [m for m in matches if m.is_confirmed and m.result]
            known_ids = {m.id for m in self._actual.confirmed_results}
            new_confirmed = [m for m in confirmed if m.id not in known_ids]
            for m in new_confirmed:
                self._actual.apply_result(m)
            self._actual.confirmed_results = confirmed

            # rebuild scenario from actual + user predictions
            await self._rebuild_scenario()
            await self._recompute_both()

    # ------------------------------------------------------------------
    # User predictions
    # ------------------------------------------------------------------

    async def add_prediction(self, match: Match) -> None:
        async with self._lock:
            self._scenario_predictions = [
                p for p in self._scenario_predictions if p.id != match.id
            ]
            self._scenario_predictions.append(match)
            await self._rebuild_scenario()
            await self._recompute_scenario()

    async def clear_predictions(self) -> None:
        async with self._lock:
            self._scenario_predictions = []
            await self._rebuild_scenario()
            await self._recompute_scenario()

    # ------------------------------------------------------------------
    # Prior source switching
    # ------------------------------------------------------------------

    async def set_prior_sources(self, sources: List[str]) -> None:
        async with self._lock:
            self._prior_sources = sources
            if self._team_codes:
                old_confirmed = list(self._actual.confirmed_results)
                self._actual = _State(sources, self._team_codes)
                for m in old_confirmed:
                    self._actual.apply_result(m)
                self._actual.confirmed_results = old_confirmed
                await self._rebuild_scenario()
                await self._recompute_both()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _rebuild_scenario(self) -> None:
        """Replay actual confirmed results + user predictions onto scenario PF."""
        if not self._team_codes:
            return
        self._scenario = _State(self._prior_sources, self._team_codes)
        for m in self._actual.confirmed_results:
            self._scenario.apply_result(m)
        self._scenario.confirmed_results = list(self._actual.confirmed_results)
        for m in self._scenario_predictions:
            self._scenario.apply_result(m)
            self._scenario.predicted_results.append(m)

    async def _recompute_both(self) -> None:
        await self._recompute_actual()
        await self._recompute_scenario()

    async def _recompute_actual(self) -> None:
        if not self._groups:
            return
        # Use ALL API matches as fixtures:
        # confirmed matches have result locked in; future matches (result=None) are simulated.
        fixtures = _build_fixtures(self._all_matches)
        vectors = self._actual.pf.sample_strength_vectors(self._simulator.n_mc)
        probs = self._simulator.run(self._groups, fixtures, vectors, self._team_codes)
        self._actual.last_tournament_state = _make_tournament_state(
            probs, self._groups, self._actual.confirmed_results, self._simulator.n_mc, is_scenario=False
        )
        logger.info("Actual state recomputed")

    async def _recompute_scenario(self) -> None:
        if not self._groups:
            return
        # Overlay user predictions on top of all API matches.
        # Predictions override the scheduled match's result for the MC simulation.
        pred_by_id = {m.id: m for m in self._scenario_predictions}
        merged = [pred_by_id.get(m.id, m) for m in self._all_matches]
        fixtures = _build_fixtures(merged)
        vectors = self._scenario.pf.sample_strength_vectors(self._simulator.n_mc)
        probs = self._simulator.run(self._groups, fixtures, vectors, self._team_codes)
        self._scenario.last_tournament_state = _make_tournament_state(
            probs, self._groups, self._scenario.all_matches(), self._simulator.n_mc, is_scenario=True
        )
        logger.info("Scenario state recomputed")

    # ------------------------------------------------------------------
    # Public read accessors
    # ------------------------------------------------------------------

    def get_actual_state(self) -> Optional[TournamentState]:
        return self._actual.last_tournament_state

    def get_scenario_state(self) -> Optional[TournamentState]:
        return self._scenario.last_tournament_state

    def get_all_matches(self) -> List[Match]:
        return list(self._all_matches)

    def get_predictions(self) -> List[Match]:
        return list(self._scenario_predictions)

    def get_prior_sources(self) -> List[str]:
        return list(self._prior_sources)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _compute_group_standings(
    groups: Dict[str, List[str]],
    matches: List[Match],
) -> Dict[str, List[GroupStanding]]:
    """Build W/D/L/Pts/GF/GA from confirmed group-stage matches."""
    rows: Dict[str, Dict[str, GroupStanding]] = {
        g: {
            t: GroupStanding(team=t, played=0, won=0, drawn=0, lost=0, goals_for=0, goals_against=0, points=0)
            for t in teams
        }
        for g, teams in groups.items()
    }

    for m in matches:
        if m.stage != MatchStage.GROUP or not m.group or not m.result:
            continue
        grp = m.group
        if grp not in rows or m.home_team not in rows[grp] or m.away_team not in rows[grp]:
            continue

        h = rows[grp][m.home_team]
        a = rows[grp][m.away_team]
        hg = m.home_score or 0
        ag = m.away_score or 0

        h.played += 1;  a.played += 1
        h.goals_for += hg;  h.goals_against += ag
        a.goals_for += ag;  a.goals_against += hg

        if m.result == MatchResult.HOME_WIN:
            h.won += 1;  h.points += 3;  a.lost += 1
        elif m.result == MatchResult.AWAY_WIN:
            a.won += 1;  a.points += 3;  h.lost += 1
        else:
            h.drawn += 1;  h.points += 1
            a.drawn += 1;  a.points += 1

    return {
        g: sorted(
            team_dict.values(),
            key=lambda s: (-s.points, -(s.goals_for - s.goals_against), -s.goals_for),
        )
        for g, team_dict in rows.items()
    }


def _make_tournament_state(
    probs: Dict[str, Dict[str, float]],
    groups: Dict[str, List[str]],
    confirmed_matches: List[Match],
    n_sim: int,
    is_scenario: bool,
) -> TournamentState:
    team_probs = {t: _probs_to_model(t, p) for t, p in probs.items()}
    group_standings = _compute_group_standings(groups, confirmed_matches)
    return TournamentState(
        group_standings=group_standings,
        team_probs=team_probs,
        n_simulations=n_sim,
        last_updated=datetime.now(timezone.utc).isoformat(),
        is_scenario=is_scenario,
    )
