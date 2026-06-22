from typing import Dict, List
import numpy as np
from backend.services.config import load_prior_sources


def _normalise(strengths: Dict[str, float]) -> Dict[str, float]:
    values = np.array(list(strengths.values()), dtype=float)
    normed = values / values.mean()
    return dict(zip(strengths.keys(), normed.tolist()))


def _fifa_strengths(teams: Dict[str, int]) -> Dict[str, float]:
    # Scale by the total number of teams so prior spread is proportional to rank gap.
    # Using max_rank instead of a hardcoded 20 reduces the ARG:CUW ratio from 11x to ~2.7x,
    # letting actual goal scores dominate the posterior after a few matches.
    n = max(teams.values()) if teams else 48
    return {code: float(np.exp(-rank / n)) for code, rank in teams.items()}


def _elo_strengths(teams: Dict[str, float]) -> Dict[str, float]:
    values = np.array(list(teams.values()), dtype=float)
    lo, hi = values.min(), values.max()
    normed = (values - lo) / (hi - lo) + 0.1   # shift off zero
    return dict(zip(teams.keys(), normed.tolist()))


def _odds_strengths(teams: Dict[str, float]) -> Dict[str, float]:
    values = np.array(list(teams.values()), dtype=float)
    normed = values / values.sum()
    return dict(zip(teams.keys(), normed.tolist()))


def _flat_strengths(team_codes: List[str]) -> Dict[str, float]:
    return {code: 1.0 for code in team_codes}


_BUILDERS = {
    "fifa": lambda data: _normalise(_fifa_strengths(data["fifa"]["teams"])),
    "elo": lambda data: _normalise(_elo_strengths(data["elo"]["teams"])),
    "odds": lambda data: _normalise(_odds_strengths(data["odds"]["teams"])),
    "flat": lambda data: _normalise(_flat_strengths(list(data["fifa"]["teams"].keys()))),
}


def compute_prior(sources: List[str]) -> Dict[str, float]:
    """Return normalised strength dict blended from the requested sources."""
    if not sources:
        raise ValueError("At least one prior source is required")

    data = load_prior_sources()
    blended: Dict[str, float] = {}

    for source in sources:
        if source not in _BUILDERS:
            raise ValueError(f"Unknown prior source: {source!r}")
        for team, strength in _BUILDERS[source](data).items():
            blended[team] = blended.get(team, 0.0) + strength

    n = len(sources)
    averaged = {t: v / n for t, v in blended.items()}
    return _normalise(averaged)
