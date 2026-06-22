import logging
from math import lgamma
from typing import Dict, List, Optional
import numpy as np
from backend.services.config import load_settings

logger = logging.getLogger(__name__)


class ParticleFilter:
    """
    Each particle is a log-strength vector over all teams.
    Weights are updated via BT+Davidson likelihood on observed results,
    then resampled with jitter when ESS drops below threshold.
    """

    def __init__(self, team_codes: List[str], prior_strengths: Dict[str, float]):
        cfg = load_settings()["simulation"]
        self.n_particles: int = cfg["n_particles"]
        self.jitter_sigma: float = cfg["jitter_sigma"]
        self.ess_threshold: float = cfg["resample_ess_threshold"]
        self.theta: float = cfg["draw_tendency"]
        self.init_sigma: float = cfg["strength_init_sigma"]
        self.mu_goals: float = float(cfg.get("mean_goals_per_match", 2.7))

        self.team_codes = team_codes
        self.team_idx: Dict[str, int] = {c: i for i, c in enumerate(team_codes)}

        rng = np.random.default_rng(cfg["random_seed"])
        mean_strength = float(np.mean(list(prior_strengths.values()))) if prior_strengths else 1.0
        unknown = [t for t in team_codes if t not in prior_strengths]
        if unknown:
            logger.warning("Unknown team codes — using mean prior: %s", unknown)
        log_prior = np.log([prior_strengths.get(t, mean_strength) for t in team_codes])
        self.particles: np.ndarray = rng.normal(
            loc=log_prior,
            scale=self.init_sigma,
            size=(self.n_particles, len(team_codes)),
        )
        self.weights: np.ndarray = np.full(self.n_particles, 1.0 / self.n_particles)
        self._rng = rng

    # ------------------------------------------------------------------
    def update(
        self,
        home: str,
        away: str,
        result: str,
        home_goals: Optional[int] = None,
        away_goals: Optional[int] = None,
    ) -> None:
        """
        Reweight particles given one confirmed or predicted result.

        When scores are known (confirmed API matches), uses a Poisson goal-scoring
        likelihood which is far more informative than the BT outcome alone.
        When only the outcome is known (user predictions), falls back to BT+Davidson.
        """
        i, j = self.team_idx[home], self.team_idx[away]
        lam_i = np.exp(self.particles[:, i])
        lam_j = np.exp(self.particles[:, j])

        if home_goals is not None and away_goals is not None:
            log_w = self._score_log_likelihood_vec(lam_i, lam_j, home_goals, away_goals)
        else:
            log_w = self._outcome_log_likelihood_vec(lam_i, lam_j, result)

        log_w -= log_w.max()
        self.weights *= np.exp(log_w)
        self.weights /= self.weights.sum()

        if self._ess() < self.n_particles * self.ess_threshold:
            self._resample()

    def _outcome_log_likelihood_vec(
        self, lam_i: np.ndarray, lam_j: np.ndarray, result: str
    ) -> np.ndarray:
        """Vectorised BT+Davidson log likelihood over all particles."""
        sqrt_ij = np.sqrt(lam_i * lam_j)
        denom = lam_i + self.theta * sqrt_ij + lam_j
        eps = 1e-15
        if result == "home_win":
            return np.log(lam_i / denom + eps)
        if result == "draw":
            return np.log(self.theta * sqrt_ij / denom + eps)
        return np.log(lam_j / denom + eps)

    def _score_log_likelihood_vec(
        self,
        lam_i: np.ndarray,
        lam_j: np.ndarray,
        home_goals: int,
        away_goals: int,
    ) -> np.ndarray:
        """Vectorised Poisson goal-scoring log likelihood over all particles."""
        total = lam_i + lam_j
        mu_i = lam_i / total * self.mu_goals
        mu_j = lam_j / total * self.mu_goals
        eps = 1e-15
        log_fact_i = lgamma(home_goals + 1)
        log_fact_j = lgamma(away_goals + 1)
        log_p_i = home_goals * np.log(mu_i + eps) - mu_i - log_fact_i
        log_p_j = away_goals * np.log(mu_j + eps) - mu_j - log_fact_j
        return log_p_i + log_p_j

    def _ess(self) -> float:
        return float(1.0 / np.sum(self.weights ** 2))

    def _resample(self) -> None:
        idx = self._rng.choice(self.n_particles, size=self.n_particles, p=self.weights)
        self.particles = self.particles[idx].copy()
        self.particles += self._rng.normal(0.0, self.jitter_sigma, self.particles.shape)
        self.weights = np.full(self.n_particles, 1.0 / self.n_particles)

    # ------------------------------------------------------------------
    def mean_strengths(self) -> Dict[str, float]:
        """Posterior mean strength per team (exp-space)."""
        mean_log = np.average(self.particles, weights=self.weights, axis=0)
        return {c: float(np.exp(mean_log[i])) for i, c in enumerate(self.team_codes)}

    def sample_strength_vectors(self, n: int) -> np.ndarray:
        """Draw n strength vectors (shape: n × n_teams) for Monte Carlo."""
        idx = self._rng.choice(self.n_particles, size=n, p=self.weights)
        return np.exp(self.particles[idx])
