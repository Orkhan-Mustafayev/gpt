"""Train an XGBoost classifier on merged football data."""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
from xgboost import XGBClassifier
import joblib

from football_ml import config
from football_ml.features import builder
from football_ml.training import dataset
from football_ml.training.evaluate import evaluate_predictions
from football_ml.utils import io
from football_ml.utils import logging as log_utils

logger = log_utils.get_logger(__name__)


def _load_or_fetch() -> pd.DataFrame:
    processed = dataset.load_processed()
    if not processed.empty:
        logger.info("Loaded processed dataset with %d rows", len(processed))
        return processed
    fd_df = dataset.fetch_fd_history(config.FD_COMPETITION_CODE, config.SEASONS)
    api_df = dataset.fetch_api_football(config.API_FOOTBALL_LEAGUE_ID, max(config.SEASONS))
    merged = dataset.merge_sources(fd_df, api_df)
    return merged


def _time_split(df: pd.DataFrame):
    df = df.sort_values(["season", "utc_date"]).reset_index(drop=True)
    seasons = sorted([s for s in df["season"].unique() if pd.notna(s)])
    if len(seasons) < 2:
        split_season = seasons[-1]
        train_df = df[df["season"] == split_season]
        test_df = train_df
    else:
        split_season = seasons[-1]
        train_df = df[df["season"] != split_season]
        test_df = df[df["season"] == split_season]
    return train_df, test_df


def main():
    df = _load_or_fetch()
    if df.empty:
        raise SystemExit("No data available. Fetch raw data first.")

    df = df[df["label"] >= 0]
    df_features = builder.build_features(df)
    df_features = df_features.dropna(subset=builder.FEATURE_COLUMNS)

    X_train_df, X_test_df = _time_split(df_features)
    y_train = X_train_df["label"]
    y_test = X_test_df["label"]
    X_train = X_train_df[builder.FEATURE_COLUMNS]
    X_test = X_test_df[builder.FEATURE_COLUMNS]

    model = XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
        learning_rate=0.1,
        max_depth=5,
        n_estimators=200,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
    )
    logger.info("Training model on %d rows", len(X_train))
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)
    metrics = evaluate_predictions(y_test, proba)
    logger.info("Accuracy: %.3f | LogLoss: %.3f", metrics["accuracy"], metrics["log_loss"])
    logger.info("Classification report:\n%s", metrics["classification_report"])

    model_file = io.model_path("match_model_xgb.pkl")
    joblib.dump(model, model_file)
    io.write_json(builder.FEATURE_COLUMNS, io.model_path("feature_columns.json"), indent=2)
    logger.info("Saved model to %s", model_file)


if __name__ == "__main__":
    main()
