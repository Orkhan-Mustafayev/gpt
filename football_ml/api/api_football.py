"""Client for API-FOOTBALL (api-sports.io) fixtures and odds."""
from __future__ import annotations

from typing import Any, Dict, List
import pandas as pd

from football_ml import config
from football_ml.api.base_client import BaseAPIClient


class APIFootballClient(BaseAPIClient):
    def __init__(self) -> None:
        super().__init__(
            base_url=f"https://{config.API_FOOTBALL_HOST}",
            headers={
                "x-apisports-key": config.API_FOOTBALL_KEY,
                "x-rapidapi-key": config.API_FOOTBALL_KEY,
            },
        )

    def get_fixtures(self, league_id: int, season: int) -> pd.DataFrame:
        payload = self.get("fixtures", params={"league": league_id, "season": season})
        fixtures = payload.get("response", []) if isinstance(payload, dict) else []
        records: List[Dict[str, Any]] = []
        for fx in fixtures:
            fixture_info = fx.get("fixture", {})
            teams = fx.get("teams", {})
            goals = fx.get("goals", {})
            records.append(
                {
                    "provider": "api-football",
                    "season": season,
                    "league_id": league_id,
                    "utc_date": fixture_info.get("date"),
                    "status": (fixture_info.get("status") or {}).get("short"),
                    "matchday": fixture_info.get("round"),
                    "home_team": (teams.get("home") or {}).get("name"),
                    "away_team": (teams.get("away") or {}).get("name"),
                    "home_goals": goals.get("home"),
                    "away_goals": goals.get("away"),
                    "fixture_id": fixture_info.get("id"),
                }
            )
        return pd.DataFrame(records)

    def get_odds(self, fixture_ids: List[int]) -> pd.DataFrame:
        odds_records: List[Dict[str, Any]] = []
        for fx_id in fixture_ids:
            payload = self.get("odds", params={"fixture": fx_id})
            response = payload.get("response", []) if isinstance(payload, dict) else []
            if not response:
                continue
            bookmakers = response[0].get("bookmakers", []) if response else []
            if not bookmakers:
                continue
            bets = bookmakers[0].get("bets", [])
            outcomes = (bets[0].get("values") if bets else []) if bets else []
            home_odd = _extract_outcome(outcomes, "Home")
            draw_odd = _extract_outcome(outcomes, "Draw")
            away_odd = _extract_outcome(outcomes, "Away")
            odds_records.append(
                {
                    "fixture_id": fx_id,
                    "home_odd": home_odd,
                    "draw_odd": draw_odd,
                    "away_odd": away_odd,
                }
            )
        return pd.DataFrame(odds_records)


def _extract_outcome(outcomes: List[Dict[str, Any]], label: str):
    for outcome in outcomes:
        if outcome.get("value") == label:
            return outcome.get("odd")
    return None
