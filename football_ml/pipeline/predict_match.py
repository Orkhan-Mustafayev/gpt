"""Predict a single matchup using fixture and odds data fetched from APIs.

This script reuses the trained model and historical feature pipeline to
produce probability percentages for a user-specified fixture. Predictions are
anchored to fixtures pulled from Free API Live so they are always based on
API-fetched stats rather than manual placeholders.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from typing import List

import joblib
import pandas as pd

from football_ml import config
from football_ml.data_sources.free_api_live import get_fixtures_by_league, get_odds_for_fixture
from football_ml.utils import elo, features


def load_model_and_features():
    """Load the trained model and feature column order."""
    model = joblib.load(config.MODEL_PATH)
    with open(config.FEATURE_PATH, "r", encoding="utf-8") as f:
        feature_cols: List[str] = json.load(f)
    return model, feature_cols


def load_historical() -> pd.DataFrame:
    """Load merged historical matches for feature context."""
    path = os.path.join(config.DATA_PROCESSED_DIR, "matches_merged.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            "Merged historical data not found. Run pipeline.merge_raw first."
        )
    df = pd.read_csv(path)
    return df.rename(
        columns={
            "provider_fd": "provider",
            "home_team_fd": "home_team",
            "away_team_fd": "away_team",
            "home_goals_fd": "home_goals",
            "away_goals_fd": "away_goals",
            "utc_date_fd": "utc_date",
            "season_fd": "season",
            "matchday_fd": "matchday",
        }
    )


def normalize_team(name: str) -> str:
    """Normalize team names for matching across APIs."""
    return name.lower().replace(" ", "")


def fetch_fixture_row(
    home_team: str,
    away_team: str,
    league_id: int,
    season: int,
) -> pd.DataFrame:
    """Fetch a fixture row (with odds when available) from Free API Live.

    This ensures predictions are grounded in API-fetched stats/metadata rather
    than manual placeholders.
    """

    fixtures = get_fixtures_by_league(league_id, season)
    if fixtures.empty:
        raise ValueError(
            "No fixtures returned from Free API Live. Ensure API keys are set and data is available."
        )

    home_norm = normalize_team(home_team)
    away_norm = normalize_team(away_team)

    fixtures["home_norm"] = fixtures["home_team"].apply(normalize_team)
    fixtures["away_norm"] = fixtures["away_team"].apply(normalize_team)

    candidates = fixtures[
        (fixtures["home_norm"] == home_norm) & (fixtures["away_norm"] == away_norm)
    ].sort_values("utc_date")

    if candidates.empty:
        raise ValueError(
            f"No matching fixture found for {home_team} vs {away_team} in league {league_id} season {season}."
        )

    fixture = candidates.iloc[0].to_dict()
    odds = get_odds_for_fixture(int(fixture["fixture_id"]))
    if odds:
        fixture.update(odds)

    row = {
        "provider": "free-api-live",
        "utc_date": fixture.get("utc_date") or datetime.utcnow().strftime("%Y-%m-%d"),
        "home_team": fixture.get("home_team", home_team),
        "away_team": fixture.get("away_team", away_team),
        "home_goals": 0,
        "away_goals": 0,
        "season": season,
        "matchday": fixture.get("matchday") or 0,
        "home_odd": fixture.get("home_odd"),
        "draw_odd": fixture.get("draw_odd"),
        "away_odd": fixture.get("away_odd"),
    }
    return pd.DataFrame([row])


def build_features(df_hist: pd.DataFrame, target_row: pd.DataFrame) -> pd.DataFrame:
    """Combine historical data and compute features without leakage."""
    combined = pd.concat([df_hist, target_row], ignore_index=True, sort=False)
    combined = combined.sort_values("utc_date")

    combined = elo.compute_elo_ratings(combined)
    combined = features.add_form_features(combined)
    combined = features.add_implied_prob_features(combined)
    return combined


def select_feature_matrix(df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
    """Select feature columns, filling any missing ones with NA."""
    for col in feature_cols:
        if col not in df:
            df[col] = pd.NA
    return df[feature_cols]


def pretty_print_prediction(
    home_team: str, away_team: str, proba: List[float]
) -> None:
    """Print a user-friendly summary of the probabilities."""
    labels = ["Home Win", "Draw", "Away Win"]
    best_idx = int(pd.Series(proba).idxmax())
    confidence = proba[best_idx]
    print(f"Prediction for {home_team} vs {away_team}")
    for label, prob in zip(labels, proba):
        print(f"  {label}: {prob:.2%}")
    print(f"Model confidence (highest probability): {confidence:.2%}")
    print(
        "Note: Percentages are model outputs based on historical form/ratings and any provided odds."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict a single football match")
    parser.add_argument("--home", required=True, help="Home team name")
    parser.add_argument("--away", required=True, help="Away team name")
    parser.add_argument(
        "--season",
        type=int,
        default=max(config.SEASONS),
        help="Season to tag for the upcoming fixture (default: latest configured season)",
    )
    parser.add_argument(
        "--league-id",
        type=int,
        default=config.FREE_API_LEAGUE_ID,
        help="League ID to query fixtures from Free API Live (default from config)",
    )
    args = parser.parse_args()

    model, feature_cols = load_model_and_features()
    df_hist = load_historical()

    target_row = fetch_fixture_row(
        home_team=args.home,
        away_team=args.away,
        league_id=args.league_id,
        season=args.season,
    )

    combined = build_features(df_hist, target_row)
    fixture_row = combined[combined["provider"] == "free-api-live"]
    if fixture_row.empty:
        raise ValueError(
            "Fixture row was not found after feature computation. Check that the API returned data."
        )
    X_pred = select_feature_matrix(fixture_row, feature_cols)

    proba = model.predict_proba(X_pred)[0]
    pretty_print_prediction(args.home, args.away, proba)


if __name__ == "__main__":
    main()
