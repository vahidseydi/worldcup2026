"""
Polling client for football-data.org v4 API.
Fetches live match results for the WC 2026 competition.
"""

import os
import logging
import asyncio
from typing import Callable, Awaitable, List

import httpx

from backend.services.config import load_settings
from backend.models.match import Match, MatchStage, MatchResult

logger = logging.getLogger(__name__)

# football-data.org is inconsistent with some TLAs across requests.
# Normalise known aliases to the code used in prior_sources.yaml.
_TLA_ALIASES: dict[str, str] = {
    "URY": "URU",  # Uruguay: ISO 3166 alpha-3 vs football convention
}

_STAGE_MAP = {
    "GROUP_STAGE": MatchStage.GROUP,
    "LAST_32": MatchStage.R32,
    "ROUND_OF_32": MatchStage.R32,
    "LAST_16": MatchStage.R16,
    "ROUND_OF_16": MatchStage.R16,
    "QUARTER_FINALS": MatchStage.QF,
    "SEMI_FINALS": MatchStage.SF,
    "FINAL": MatchStage.FINAL,
}


def _parse_result(score: dict, stage: MatchStage) -> tuple[MatchResult | None, int | None, int | None]:
    full = score.get("fullTime", {})
    home_score = full.get("home")
    away_score = full.get("away")
    if home_score is None or away_score is None:
        return None, None, None
    if home_score > away_score:
        return MatchResult.HOME_WIN, home_score, away_score
    if away_score > home_score:
        return MatchResult.AWAY_WIN, home_score, away_score
    return MatchResult.DRAW, home_score, away_score


def _parse_match(raw: dict) -> Match | None:
    try:
        stage_str = raw.get("stage", "")
        stage = _STAGE_MAP.get(stage_str)
        if stage is None:
            return None

        result, home_score, away_score = _parse_result(raw.get("score", {}), stage)
        status = raw.get("status", "")
        is_confirmed = status == "FINISHED"

        raw_group = raw.get("group")
        group = raw_group.removeprefix("GROUP_") if raw_group else None

        home_tla = raw["homeTeam"].get("tla")
        away_tla = raw["awayTeam"].get("tla")
        if not home_tla or not away_tla:
            return None  # placeholder slot — teams not yet determined
        home_tla = _TLA_ALIASES.get(home_tla, home_tla)
        away_tla = _TLA_ALIASES.get(away_tla, away_tla)

        return Match(
            id=raw["id"],
            stage=stage,
            group=group,
            home_team=home_tla,
            away_team=away_tla,
            scheduled_at=raw.get("utcDate"),
            result=result,
            home_score=home_score,
            away_score=away_score,
            is_confirmed=is_confirmed,
        )
    except (KeyError, TypeError) as exc:
        logger.warning("Failed to parse match %s: %s", raw.get("id"), exc)
        return None


class FootballAPIClient:
    def __init__(self) -> None:
        cfg = load_settings()["football_api"]
        self._base_url: str = cfg["base_url"]
        self._competition_id: int = cfg["competition_id"]
        self._poll_interval: int = cfg["poll_interval_seconds"]
        self._timeout: int = cfg["timeout_seconds"]
        api_key = os.environ.get("FOOTBALL_DATA_API_KEY", "")
        if not api_key:
            logger.warning("FOOTBALL_DATA_API_KEY not set — live polling disabled")
        self._api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"X-Auth-Token": self._api_key},
            timeout=self._timeout,
        )

    async def fetch_matches(self) -> List[Match]:
        url = f"/competitions/{self._competition_id}/matches"
        try:
            resp = await self._client.get(url)
            resp.raise_for_status()
            raw_matches = resp.json().get("matches", [])
            parsed = [_parse_match(m) for m in raw_matches]
            return [m for m in parsed if m is not None]
        except httpx.HTTPError as exc:
            logger.error("API request failed: %s", exc)
            return []

    def _adaptive_interval(self, matches: List[Match]) -> int:
        """Return the next poll interval based on match activity.

        Live match present      → 60 s  (catch goals in near-real-time)
        Match finishing within 3 h → 2 min (match imminent or just ended)
        Otherwise               → 10 min (nothing happening)
        """
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)

        live_statuses = {"IN_PLAY", "PAUSED", "HALFTIME"}
        for m in matches:
            # is_confirmed=False but result is set → recently finished, stay alert
            if not m.is_confirmed and m.result is not None:
                return 120
            if m.scheduled_at:
                try:
                    kickoff = datetime.fromisoformat(m.scheduled_at.replace("Z", "+00:00"))
                    delta = (kickoff - now).total_seconds()
                    # Within 30 min before or 2 h after kickoff — could be live
                    if -7200 < delta < 1800:
                        return 60
                except ValueError:
                    pass

        # No live or imminent match → slow polling
        return 600

    async def poll(self, on_update: Callable[[List[Match]], Awaitable[None]]) -> None:
        """Poll adaptively: fast during live matches, slow otherwise."""
        if not self._api_key:
            logger.warning("Polling skipped — no API key configured")
            return
        while True:
            matches = await self.fetch_matches()
            if matches:
                await on_update(matches)
                interval = self._adaptive_interval(matches)
            else:
                interval = self._poll_interval  # fallback to config default on error
            if interval != self._poll_interval:
                logger.info("Adaptive poll interval: %ds", interval)
            await asyncio.sleep(interval)

    async def close(self) -> None:
        await self._client.aclose()
