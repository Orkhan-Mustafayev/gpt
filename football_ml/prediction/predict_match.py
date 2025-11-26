"""Predict a single match using the trained model."""
from __future__ import annotations

import argparse
import joblib
import pandas as pd

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


def find_fixture(fixtures: pd.DataFrame, home: str, away: str) -> pd.DataFrame:
    if fixtures.empty:
        return pd.DataFrame()
    norm = fixtures.copy()
    norm["home_norm"] = norm["home_team"].str.lower().str.strip()
    norm["away_norm"] = norm["away_team"].str.lower().str.strip()
    mask = (norm["home_norm"] == home.lower().strip()) & (norm["away_norm"] == away.lower().strip())
    return norm[mask]


def main():
    parser = argparse.ArgumentParser(description="Predict a single match")
    parser.add_argument("--home", required=True)
    parser.add_argument("--away", required=True)
    args = parser.parse_args()

    history = dataset.load_processed()
    if history.empty:
        raise SystemExit("No processed data found. Run training first.")

    client = APIFootballClient()
    fixtures = client.get_fixtures(config.API_FOOTBALL_LEAGUE_ID, max(config.SEASONS))
    target = find_fixture(fixtures, args.home, args.away)
    if target.empty:
        raise SystemExit("Fixture not found for provided teams.")

    odds = client.get_odds(target["fixture_id"].dropna().astype(int).tolist())
    if not odds.empty:
        target = target.merge(odds, on="fixture_id", how="left")

    model, feature_cols = load_model_artifacts()
    target["label"] = -1
    target["home_goals"] = target["home_goals"].fillna(0)
    target["away_goals"] = target["away_goals"].fillna(0)
    combined = pd.concat([history, target], ignore_index=True)
    combined = builder.build_features(combined)
    upcoming = combined[combined["provider"] == "api-football"]

    X = upcoming[feature_cols]
    proba = model.predict_proba(X)[0]
    print(
        {
            "home_team": args.home,
            "away_team": args.away,
            "prob_home": proba[0],
            "prob_draw": proba[1],
            "prob_away": proba[2],
        }
    )


if __name__ == "__main__":
    main()
