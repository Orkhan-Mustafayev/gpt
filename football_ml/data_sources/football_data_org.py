"""Client for fetching match data from football-data.org.

This module provides convenience wrappers to pull historical matches using
the v4 football-data.org API. It focuses on league competitions and keeps
only a subset of fields needed for the ML pipeline.
"""
from __future__ import annotations

import json
import os
from typing import List

import pandas as pd
import requests

from football_ml import config

API_BASE = "https://api.football-data.org/v4"


def _headers() -> dict:
    return {"X-Auth-Token": config.FOOTBALL_DATA_API_TOKEN or ""}


def fetch_matches(competition_code: str, season: int) -> pd.DataFrame:
    """Fetch all matches for a given competition and season.

    Returns a DataFrame with normalized columns.
    """
    url = f"{API_BASE}/competitions/{competition_code}/matches"
    params = {"season": season}
    try:
        resp = requests.get(url, headers=_headers(), params=params, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch matches for {competition_code} {season}: {exc}") from exc

    payload = resp.json()
    matches = payload.get("matches", [])
    records = []
    for m in matches:
        record = {
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
            "fd_id": m.get("id"),
        }
        records.append(record)
    return pd.DataFrame(records)


def fetch_multi_season(competition_code: str, seasons: List[int]) -> pd.DataFrame:
    """Fetch multiple seasons and concatenate the result."""
    frames = []
    for season in seasons:
        print(f"Fetching {competition_code} season {season}...")
        frames.append(fetch_matches(competition_code, season))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


if __name__ == "__main__":
    os.makedirs(config.DATA_RAW_DIR, exist_ok=True)
    df_all = fetch_multi_season(config.FD_COMPETITION_CODE, config.SEASONS)
    output_path = os.path.join(config.DATA_RAW_DIR, "matches_fd.csv")
    df_all.to_csv(output_path, index=False)
    print(f"Saved football-data.org matches to {output_path} ({len(df_all)} rows)")
