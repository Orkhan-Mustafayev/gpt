"""Client for football-data.org historical matches."""
from __future__ import annotations

from typing import List
import pandas as pd

from football_ml import config
from football_ml.utils import logging as log_utils
from football_ml.api.base_client import BaseAPIClient


class FootballDataOrgClient(BaseAPIClient):
    def __init__(self) -> None:
        super().__init__(
            base_url="https://api.football-data.org/v4",
            headers={"X-Auth-Token": config.FOOTBALL_DATA_API_TOKEN},
        )

    def fetch_matches(self, competition_code: str, season: int) -> pd.DataFrame:
        self.logger.info("Fetching %s season %s", competition_code, season)
        payload = self.get(
            f"competitions/{competition_code}/matches",
            params={"season": season},
        )
        matches = payload.get("matches", []) if isinstance(payload, dict) else []
        records = []
        for m in matches:
            records.append(
                {
                    "provider": "football-data.org",
                    "season": season,
                    "utc_date": m.get("utcDate"),
                    "status": m.get("status"),
                    "matchday": m.get("matchday"),
                    "home_team": (m.get("homeTeam") or {}).get("name"),
                    "away_team": (m.get("awayTeam") or {}).get("name"),
                    "home_goals": (m.get("score") or {}).get("fullTime", {}).get("home"),
                    "away_goals": (m.get("score") or {}).get("fullTime", {}).get("away"),
                    "competition_code": competition_code,
                    "match_id": m.get("id"),
                }
            )
        return pd.DataFrame(records)

    def fetch_multi_season(self, competition_code: str, seasons: List[int]) -> pd.DataFrame:
        frames = [self.fetch_matches(competition_code, s) for s in seasons]
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
