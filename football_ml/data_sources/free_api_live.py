"""Client for the Free API Live Football Data service via RapidAPI.

Endpoints and field names may vary by provider plan. This module uses
reasonable placeholders patterned after typical RapidAPI responses and
is intended as a starting point.
"""
from __future__ import annotations

import os
from typing import Dict

import pandas as pd
import requests

from football_ml import config

API_BASE = "https://free-api-live-football-data.p.rapidapi.com"


def _headers() -> dict:
    return {
        "X-RapidAPI-Key": config.FREE_API_RAPID_KEY or "",
        "X-RapidAPI-Host": config.FREE_API_HOST,
    }


def get_fixtures_by_league(league_id: int, season: int) -> pd.DataFrame:
    """Fetch fixtures for a given league and season.

    Returns a DataFrame with a normalized column set. Adjust `url` and
    extraction logic to match the real API shape.
    """
    url = f"{API_BASE}/fixtures"
    params = {"league": league_id, "season": season}
    try:
        resp = requests.get(url, headers=_headers(), params=params, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch fixtures for league {league_id}: {exc}") from exc

    data = resp.json()
    fixtures = data.get("response", [])  # TODO: adjust to actual payload
    records = []
    for fx in fixtures:
        teams = fx.get("teams", {})
        goals = fx.get("goals", {})
        fixture_info = fx.get("fixture", {})
        records.append(
            {
                "provider": "free-api-live",
                "league_id": league_id,
                "season": season,
                "utc_date": fixture_info.get("date"),
                "status": fixture_info.get("status", {}).get("long"),
                "home_team": (teams.get("home") or {}).get("name"),
                "away_team": (teams.get("away") or {}).get("name"),
                "home_goals": goals.get("home"),
                "away_goals": goals.get("away"),
                "fixture_id": fixture_info.get("id"),
            }
        )
    return pd.DataFrame(records)


def get_odds_for_fixture(fixture_id: int) -> Dict[str, float] | None:
    """Fetch pre-match odds for a fixture.

    Returns a dict containing home/draw/away odds when available.
    """
    url = f"{API_BASE}/odds"
    params = {"fixture": fixture_id}
    try:
        resp = requests.get(url, headers=_headers(), params=params, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"Warning: failed to fetch odds for fixture {fixture_id}: {exc}")
        return None

    data = resp.json()
    # TODO: adjust to real payload structure. Below is a typical shape.
    bookmakers = data.get("response", [])
    if not bookmakers:
        return None

    # Take first bookmaker/market selection as an example
    markets = bookmakers[0].get("bookmakers", []) if isinstance(bookmakers[0], dict) else []
    if markets:
        bets = markets[0].get("bets", [])
    else:
        bets = bookmakers[0].get("bets", []) if isinstance(bookmakers[0], dict) else []

    odds = {}
    for bet in bets:
        label = bet.get("name", "").lower()
        if "match winner" in label:
            for val in bet.get("values", []):
                outcome = val.get("value", "").lower()
                if outcome in {"home", "1"}:
                    odds["home_odd"] = float(val.get("odd"))
                elif outcome in {"draw", "x"}:
                    odds["draw_odd"] = float(val.get("odd"))
                elif outcome in {"away", "2"}:
                    odds["away_odd"] = float(val.get("odd"))
    return odds or None


if __name__ == "__main__":
    os.makedirs(config.DATA_RAW_DIR, exist_ok=True)
    df_fx = get_fixtures_by_league(config.FREE_API_LEAGUE_ID, max(config.SEASONS))
    output_path = os.path.join(config.DATA_RAW_DIR, "matches_free.csv")
    df_fx.to_csv(output_path, index=False)
    print(f"Saved free-api fixtures to {output_path} ({len(df_fx)} rows)")
