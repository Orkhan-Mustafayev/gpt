"""Predict probabilities for upcoming fixtures using the trained model.

This is for educational/experimental purposes and not betting advice.
"""
from __future__ import annotations

import json
import os
from typing import List

import joblib
import pandas as pd

from football_ml import config
from football_ml.data_sources.free_api_live import get_fixtures_by_league, get_odds_for_fixture
from football_ml.utils import elo, features


def load_model_and_features():
    model = joblib.load(config.MODEL_PATH)
    with open(config.FEATURE_PATH, "r", encoding="utf-8") as f:
        feature_cols = json.load(f)
    return model, feature_cols


def prepare_historical_data() -> pd.DataFrame:
    path = os.path.join(config.DATA_PROCESSED_DIR, "matches_merged.csv")
    if not os.path.exists(path):
        raise FileNotFoundError("Merged historical data not found. Run merge_raw.py first.")
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


def build_features(df_hist: pd.DataFrame, upcoming_df: pd.DataFrame) -> pd.DataFrame:
    # Combine historical and upcoming for consistent feature computation
    combined = pd.concat([df_hist, upcoming_df], ignore_index=True, sort=False)
    combined = combined.sort_values("utc_date")

    combined = elo.compute_elo_ratings(combined)
    combined = features.add_form_features(combined)
    combined = features.add_implied_prob_features(combined)
    return combined


def select_feature_matrix(df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
    for col in feature_cols:
        if col not in df:
            df[col] = pd.NA
    return df[feature_cols]


def fetch_upcoming_with_odds(league_id: int, season: int) -> pd.DataFrame:
    fixtures = get_fixtures_by_league(league_id, season)
    records = []
    for _, row in fixtures.iterrows():
        odds = get_odds_for_fixture(row["fixture_id"])
        record = row.to_dict()
        if odds:
            record.update(odds)
        records.append(record)
    df = pd.DataFrame(records)
    if not df.empty:
        df["provider"] = "free-api-live"
        df.rename(columns={"matchday": "matchday"}, inplace=True)
    return df


def main() -> None:
    model, feature_cols = load_model_and_features()
    df_hist = prepare_historical_data()

    df_upcoming = fetch_upcoming_with_odds(config.FREE_API_LEAGUE_ID, max(config.SEASONS))
    df_upcoming["home_goals"] = 0
    df_upcoming["away_goals"] = 0
    df_upcoming["season"] = max(config.SEASONS)

    combined = build_features(df_hist, df_upcoming)

    upcoming_only = combined[combined["provider"] == "free-api-live"]
    X_upcoming = select_feature_matrix(upcoming_only, feature_cols)
    proba = model.predict_proba(X_upcoming)

    result_df = pd.DataFrame(
        {
            "utc_date": upcoming_only["utc_date"],
            "home_team": upcoming_only["home_team"],
            "away_team": upcoming_only["away_team"],
            "prob_home": proba[:, 0],
            "prob_draw": proba[:, 1],
            "prob_away": proba[:, 2],
        }
    )

    os.makedirs(config.DATA_PROCESSED_DIR, exist_ok=True)
    output_path = os.path.join(config.DATA_PROCESSED_DIR, "upcoming_predictions.csv")
    result_df.to_csv(output_path, index=False)
    print(result_df)
    print(f"Saved predictions to {output_path}")


if __name__ == "__main__":
    main()
