"""Predict upcoming fixtures using the trained model."""
from __future__ import annotations

import pandas as pd
import joblib

from football_ml import config
from football_ml.api.api_football import APIFootballClient
from football_ml.features import builder
from football_ml.training import dataset
from football_ml.utils import io
from football_ml.utils import logging as log_utils

logger = log_utils.get_logger(__name__)


def load_model_artifacts():
    model = joblib.load(io.model_path("match_model_xgb.pkl"))
    feature_cols = io.read_json(io.model_path("feature_columns.json"))
    return model, feature_cols


def prepare_upcoming(fixtures: pd.DataFrame, history: pd.DataFrame) -> pd.DataFrame:
    if fixtures.empty:
        return fixtures
    fixtures = fixtures.copy()
    fixtures["label"] = -1
    fixtures["home_goals"] = fixtures["home_goals"].fillna(0)
    fixtures["away_goals"] = fixtures["away_goals"].fillna(0)
    combined = pd.concat([history, fixtures], ignore_index=True)
    combined = builder.build_features(combined)
    upcoming_rows = combined[combined["provider"] == "api-football"]
    return upcoming_rows


def main():
    history = dataset.load_processed()
    if history.empty:
        raise SystemExit("No processed data found. Run training first.")

    client = APIFootballClient()
    fixtures = client.get_fixtures(config.API_FOOTBALL_LEAGUE_ID, max(config.SEASONS))
    if fixtures.empty:
        raise SystemExit("No upcoming fixtures found.")
    odds = client.get_odds(fixtures["fixture_id"].dropna().astype(int).tolist())
    if not odds.empty:
        fixtures = fixtures.merge(odds, on="fixture_id", how="left")

    model, feature_cols = load_model_artifacts()
    upcoming = prepare_upcoming(fixtures, history)
    if upcoming.empty:
        raise SystemExit("No upcoming fixtures after preparation.")

    X_upcoming = upcoming[feature_cols]
    proba = model.predict_proba(X_upcoming)
    result = upcoming[["utc_date", "home_team", "away_team", "fixture_id"]].copy()
    result["prob_home"] = proba[:, 0]
    result["prob_draw"] = proba[:, 1]
    result["prob_away"] = proba[:, 2]

    out_path = io.processed_path("upcoming_predictions.csv")
    io.write_csv(result, out_path)
    logger.info("Saved predictions to %s", out_path)
    print(result.head())


if __name__ == "__main__":
    main()
