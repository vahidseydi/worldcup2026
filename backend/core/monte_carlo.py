"""
Vectorised Monte Carlo tournament simulator for WC 2026.

All n_mc simulations run simultaneously as NumPy array operations —
no Python loop over simulations. Typical runtime: <0.3 s for n_mc=10,000.

Format:
  - 12 groups (A–L), 4 teams each, 6 matches per group
  - Top 2 per group (24) + best 8 third-place teams (8) = 32 advance
  - Knockout: R32 → R16 → QF → SF → Final → Winner
  - No draws in knockout (extra time / penalties modelled via BT win prob)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np
from backend.services.config import load_settings

# FIFA WC 2026 R32 bracket — sourced from the official tournament draw.
# Each value: (home_pos, away_pos) where pos = (kind, group_letter)
#   'W' = group winner, 'R' = runner-up, 'T' = 3rd place of that group,
#   'B' = best-8 third-place (variable; filled in slot order across 4 such matches).
# Groups with a pre-assigned 3rd-place slot: D→slot1, B→slot13, F→slot19, I→slot23.
_R32_BRACKET: dict = {
    537415: (("W", "E"), ("T", "D")),   # GER vs PAR
    537416: (("R", "E"), ("R", "I")),   # CIV vs NOR
    537417: (("R", "A"), ("R", "B")),   # RSA vs CAN
    537418: (("W", "F"), ("R", "C")),   # NED vs MAR
    537419: (("W", "H"), ("R", "J")),   # ESP vs 2J
    537420: (("R", "K"), ("R", "L")),   # 2K vs 2L
    537421: (("W", "D"), ("T", "B")),   # USA vs BIH
    537422: (("W", "G"), ("B", "")),    # BEL vs best-8 3rd
    537423: (("W", "C"), ("R", "F")),   # BRA vs JPN
    537424: (("W", "I"), ("T", "F")),   # FRA vs SWE
    537425: (("W", "A"), ("B", "")),    # MEX vs best-8 3rd
    537426: (("W", "L"), ("T", "I")),   # ENG vs SEN
    537427: (("W", "J"), ("R", "H")),   # ARG vs CPV
    537428: (("R", "D"), ("R", "G")),   # AUS vs 2G
    537429: (("W", "B"), ("B", "")),    # SUI vs best-8 3rd
    537430: (("W", "K"), ("B", "")),    # 1K vs best-8 3rd
}


@dataclass
class Fixture:
    home: str
    away: str
    group: Optional[str] = None      # None for knockout
    result: Optional[str] = None     # 'home_win' | 'draw' | 'away_win'; None = TBD
    match_id: int = 0
    stage: str = "group"
    home_score: Optional[int] = None
    away_score: Optional[int] = None


# Encode results as integers for fast array arithmetic
_HOME_WIN = 0
_DRAW = 1
_AWAY_WIN = 2

# Round index → round_id string (used in return dict)
_ROUND_IDS = ["r32", "r16", "qf", "sf", "final", "winner"]


class MonteCarloSimulator:
    def __init__(self) -> None:
        cfg = load_settings()["simulation"]
        self.n_mc: int = cfg["n_monte_carlo"]
        self.theta: float = cfg["draw_tendency"]
        self._rng = np.random.default_rng(cfg["random_seed"] + 1)

    def run(
        self,
        groups: Dict[str, List[str]],
        fixtures: List[Fixture],
        strength_vectors: np.ndarray,   # shape: (n_mc, n_teams)
        team_codes: List[str],
    ) -> Dict[str, Dict[str, float]]:
        """
        Return dict: team -> {round_id -> probability}.
        Round ids: 'qualify', 'r32', 'r16', 'qf', 'sf', 'final', 'winner'.
        """
        n = min(self.n_mc, len(strength_vectors))
        sv = strength_vectors[:n]                  # (n, n_teams)
        team_idx = {c: i for i, c in enumerate(team_codes)}
        group_list = list(groups.items())
        n_groups = len(group_list)

        # ── Group stage ────────────────────────────────────────────────────
        # For each group, maintain (n, 4) arrays of pts / goal-diff / goals-for.
        # All n simulations are updated simultaneously per fixture.
        group_pts = [np.zeros((n, 4), dtype=np.int32) for _ in range(n_groups)]
        group_gd  = [np.zeros((n, 4), dtype=np.int32) for _ in range(n_groups)]
        group_gf  = [np.zeros((n, 4), dtype=np.int32) for _ in range(n_groups)]

        # Pre-build group → (group_array_idx, team → local_col) maps
        grp_meta: Dict[str, tuple] = {}
        for gi, (g, teams) in enumerate(group_list):
            grp_meta[g] = (gi, {t: li for li, t in enumerate(teams)})

        for fix in fixtures:
            if fix.group is None:
                continue
            gi, local_map = grp_meta[fix.group]
            hl = local_map[fix.home]
            al = local_map[fix.away]

            if fix.result is not None:
                # Confirmed result — use actual scores for precise tiebreakers
                res = fix.result
                hg = fix.home_score or 0
                ag = fix.away_score or 0
                diff = hg - ag
                group_gf[gi][:, hl] += hg
                group_gf[gi][:, al] += ag
                group_gd[gi][:, hl] += diff
                group_gd[gi][:, al] -= diff
                if res == "home_win":
                    group_pts[gi][:, hl] += 3
                elif res == "away_win":
                    group_pts[gi][:, al] += 3
                else:  # draw
                    group_pts[gi][:, hl] += 1
                    group_pts[gi][:, al] += 1
            else:
                # Simulate all n outcomes at once
                hg = team_idx[fix.home]
                ag = team_idx[fix.away]
                lam_h = sv[:, hg]                          # (n,)
                lam_a = sv[:, ag]                          # (n,)
                sqrt_ha = np.sqrt(lam_h * lam_a)
                denom = lam_h + self.theta * sqrt_ha + lam_a
                p_hw = lam_h / denom
                p_d  = self.theta * sqrt_ha / denom

                r = self._rng.random(n)
                hw = (r < p_hw).astype(np.int32)
                aw = (r >= p_hw + p_d).astype(np.int32)
                d  = (1 - hw - aw)

                group_pts[gi][:, hl] += 3 * hw + d
                group_pts[gi][:, al] += 3 * aw + d
                group_gd[gi][:, hl]  += hw - aw
                group_gd[gi][:, al]  += aw - hw
                group_gf[gi][:, hl]  += hw
                group_gf[gi][:, al]  += aw

        # ── Determine qualifiers ───────────────────────────────────────────
        # For each group, rank 4 teams simultaneously across all n simulations.
        # Sort key: pts×10000 + gd×100 + gf  (descending = rank 1 first)
        first_g  = np.empty((n, n_groups), dtype=np.int32)
        second_g = np.empty((n, n_groups), dtype=np.int32)
        third_g  = np.empty((n, n_groups), dtype=np.int32)
        third_key = np.empty((n, n_groups), dtype=np.int32)

        arange_n = np.arange(n)

        for gi, (g, teams) in enumerate(group_list):
            global_idxs = np.array([team_idx[t] for t in teams], dtype=np.int32)
            key = group_pts[gi] * 10000 + group_gd[gi] * 100 + group_gf[gi]  # (n,4)
            ranks = np.argsort(-key, axis=1)                                   # (n,4)

            first_g[:, gi]  = global_idxs[ranks[:, 0]]
            second_g[:, gi] = global_idxs[ranks[:, 1]]
            third_g[:, gi]  = global_idxs[ranks[:, 2]]
            # Third-place tiebreaker key (for best-8 selection)
            third_key[:, gi] = key[arange_n, ranks[:, 2]]

        # Best 8 third-place teams (by pts/gd/gf) — vectorised across n sims
        third_ranks = np.argsort(-third_key, axis=1)          # (n, n_groups)
        best8_cols  = third_ranks[:, :8]                       # (n, 8)
        best8       = third_g[arange_n[:, None], best8_cols]  # (n, 8)

        # ── Build R32 bracket ────────────────────────────────────────────
        # Use hardcoded FIFA WC 2026 bracket draw (_R32_BRACKET).
        # For each slot: use confirmed API team if known, else compute from
        # the simulation (group winner/runner/3rd as specified by the draw).
        r32_fixtures = sorted(
            [f for f in fixtures if f.stage == "r32" and f.match_id > 0],
            key=lambda f: f.match_id,
        )

        bracket = np.empty((n, 32), dtype=np.int32)

        if len(r32_fixtures) >= 16:
            grp_gi = {g: gi for gi, (g, _) in enumerate(group_list)}

            # Best-8 thirds NOT from the groups with pre-assigned 'T' slots
            _fixed_T = {"D", "B", "F", "I"}
            _rem_gis = [gi for gi, (g, _) in enumerate(group_list) if g not in _fixed_T]
            if _rem_gis:
                _rem_keys  = third_key[:, _rem_gis]
                _rem_teams = third_g[:, _rem_gis]
                _rem_ranks = np.argsort(-_rem_keys, axis=1)
                _best_B = _rem_teams[arange_n[:, None], _rem_ranks[:, :4]]
            else:
                _best_B = np.empty((n, 0), dtype=np.int32)

            _b_idx = 0

            def _fill(slot: int, kind: str, grp: str) -> None:
                nonlocal _b_idx
                gi = grp_gi.get(grp)
                if kind == "W" and gi is not None:
                    bracket[:, slot] = first_g[:, gi]
                elif kind == "R" and gi is not None:
                    bracket[:, slot] = second_g[:, gi]
                elif kind == "T" and gi is not None:
                    bracket[:, slot] = third_g[:, gi]
                elif kind == "B" and _b_idx < _best_B.shape[1]:
                    bracket[:, slot] = _best_B[:, _b_idx]
                    _b_idx += 1

            for slot_pair, fix in enumerate(r32_fixtures[:16]):
                hs  = 2 * slot_pair
                as_ = 2 * slot_pair + 1
                info = _R32_BRACKET.get(fix.match_id)

                if fix.home in team_idx:
                    bracket[:, hs] = team_idx[fix.home]
                elif info:
                    _fill(hs, *info[0])

                if fix.away in team_idx:
                    bracket[:, as_] = team_idx[fix.away]
                elif info:
                    _fill(as_, *info[1])
        else:
            # No R32 fixtures from API yet — rotation heuristic
            for i in range(n_groups):
                bracket[:, 2 * i]     = first_g[:, i]
                bracket[:, 2 * i + 1] = second_g[:, (i + 1) % n_groups]
            for j in range(8):
                bracket[:, 24 + j] = best8[:, j]

        qualified = bracket

        # ── Track reach ────────────────────────────────────────────────────
        # reach[sim, team] = highest round index reached (-1 = group out)
        # Round index: 0=r32, 1=r16, 2=qf, 3=sf, 4=final, 5=winner
        n_teams = len(team_codes)
        reach = np.full((n, n_teams), -1, dtype=np.int8)

        # All 32 qualified teams reached r32
        reach[arange_n[:, None], qualified] = 0

        # ── Knockout rounds ────────────────────────────────────────────────
        current = qualified   # (n, 32) → (n, 16) → … → (n, 1)

        # matchup_records[i] = (round_label, home_t, away_t) for round i
        # round_i=1 → r32 matches, round_i=2 → r16, …, round_i=5 → final
        matchup_records = []

        for round_i in range(1, 6):   # 1=r16, 2=qf, 3=sf, 4=final, 5=winner
            n_pairs = current.shape[1] // 2
            home_t = current[:, 0::2]           # (n, n_pairs)
            away_t = current[:, 1::2]           # (n, n_pairs)

            matchup_records.append((_ROUND_IDS[round_i - 1], home_t.copy(), away_t.copy()))

            lam_h = sv[arange_n[:, None], home_t]   # (n, n_pairs)
            lam_a = sv[arange_n[:, None], away_t]   # (n, n_pairs)
            p_hw  = lam_h / (lam_h + lam_a)

            hw = self._rng.random((n, n_pairs)) < p_hw   # (n, n_pairs) bool
            winners = np.where(hw, home_t, away_t)        # (n, n_pairs)

            reach[arange_n[:, None], winners] = round_i
            current = winners

        # ── Aggregate to probabilities ─────────────────────────────────────
        all_teams = [t for _, teams in group_list for t in teams]
        n_teams = len(team_codes)
        result: Dict = {}

        for team in all_teams:
            ti = team_idx[team]
            r  = reach[:, ti]          # (n,) of int8, -1 means group out
            qualify = float(np.mean(r >= 0))
            result[team] = {
                "qualify": qualify,
                **{_ROUND_IDS[k]: float(np.mean(r >= k)) for k in range(6)},
                "opponents": self._compute_opponents(
                    ti, matchup_records, n, n_teams, team_codes
                ),
            }

        return result

    def _compute_opponents(
        self,
        ti: int,
        matchup_records: list,
        n: int,
        n_teams: int,
        team_codes: list,
    ) -> dict:
        """Return conditional opponent probabilities per round.

        P(face team X in round R | team reaches round R), only for X where prob >= 0.5%.
        """
        opponents: dict = {}
        for round_label, home_arr, away_arr in matchup_records:
            # (n, n_pairs) → find where team ti appears
            as_home = home_arr == ti
            as_away = away_arr == ti
            opp = np.where(as_home, away_arr, np.where(as_away, home_arr, -1))
            sim_opp = opp.max(axis=1)   # (n,) — opponent index, or -1 if absent

            appeared = sim_opp >= 0
            n_appeared = int(appeared.sum())
            if n_appeared == 0:
                continue

            counts = np.bincount(sim_opp[appeared], minlength=n_teams)
            cond_probs = counts / n_appeared
            opponents[round_label] = {
                team_codes[j]: float(cond_probs[j])
                for j in np.where(cond_probs >= 0.005)[0]
                if team_codes[j] != team_codes[ti]
            }
        return opponents
