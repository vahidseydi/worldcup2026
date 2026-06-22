import numpy as np
from math import lgamma


def match_probs(
    lambda_i: float, lambda_j: float, theta: float
) -> tuple[float, float, float]:
    """P(i wins), P(draw), P(j wins) — Davidson extension of Bradley-Terry."""
    sqrt_ij = np.sqrt(lambda_i * lambda_j)
    denom = lambda_i + theta * sqrt_ij + lambda_j
    return (
        float(lambda_i / denom),
        float(theta * sqrt_ij / denom),
        float(lambda_j / denom),
    )


def log_likelihood(
    lambda_i: float, lambda_j: float, theta: float, result: str
) -> float:
    """Log P(result) for a single match. result in {'home_win','draw','away_win'}."""
    p_win, p_draw, p_loss = match_probs(lambda_i, lambda_j, theta)
    eps = 1e-15
    if result == "home_win":
        return float(np.log(p_win + eps))
    if result == "draw":
        return float(np.log(p_draw + eps))
    return float(np.log(p_loss + eps))


def score_log_likelihood(
    lambda_i: float,
    lambda_j: float,
    home_goals: int,
    away_goals: int,
    mu_total: float = 2.7,
) -> float:
    """
    Log P(scoreline) using an independent Poisson goal model.

    Expected goals are split proportionally to team strengths:
      E[home goals] = lambda_i / (lambda_i + lambda_j) * mu_total
      E[away goals] = lambda_j / (lambda_i + lambda_j) * mu_total

    This is more informative than the BT outcome alone because a 2-2 scoreline
    carries much stronger evidence about relative team strength than just 'draw'.
    """
    total = lambda_i + lambda_j
    mu_i = lambda_i / total * mu_total
    mu_j = lambda_j / total * mu_total
    eps = 1e-15

    def poisson_log_pmf(k: int, mu: float) -> float:
        return k * np.log(mu + eps) - mu - lgamma(k + 1)

    return float(poisson_log_pmf(home_goals, mu_i) + poisson_log_pmf(away_goals, mu_j))


def knockout_win_prob(lambda_i: float, lambda_j: float) -> float:
    """P(i beats j) in a knockout match — no draw possible."""
    return float(lambda_i / (lambda_i + lambda_j))
