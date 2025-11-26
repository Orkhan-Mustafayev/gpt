"""Build features and train a multiclass classifier for match outcomes."""
from __future__ import annotations

import json
import os
from typing import List

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, log_loss
from xgboost import XGBClassifier

from football_ml import config
from football_ml.utils import elo, features


FEATURE_COLUMNS = [
    "elo_home",
    "elo_away",
    "elo_diff",
    "home_points_lastN",
    "away_points_lastN",
    "home_goal_diff_lastN",
    "away_goal_diff_lastN",
    "implied_prob_home",
    "implied_prob_draw",
    "implied_prob_away",
    "matchday",
]


def train_test_split_by_season(df: pd.DataFrame, seasons: List[int]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split into train/test by season to avoid leakage."""
    if len(seasons) < 2:
        raise ValueError("Need at least two seasons to create train/test split")
    last_season = max(seasons)
    train_df = df[df["season"] < last_season]
    test_df = df[df["season"] == last_season]
    return train_df, test_df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Run feature engineering steps (Elo, form, implied probabilities)."""
    df = df.rename(
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

    df = df.sort_values("utc_date")
    df = elo.compute_elo_ratings(df)
    df = features.add_form_features(df)
    df = features.add_implied_prob_features(df)
    return df


def select_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    for col in FEATURE_COLUMNS:
        if col not in df:
            df[col] = pd.NA
    return df[FEATURE_COLUMNS]


def main() -> None:
    merged_path = os.path.join(config.DATA_PROCESSED_DIR, "matches_merged.csv")
    df = pd.read_csv(merged_path)

    # Build features
    df_feat = build_features(df)

    # Prepare splits
    train_df, test_df = train_test_split_by_season(df_feat, df_feat["season"].dropna().unique().tolist())

    X_train = select_feature_matrix(train_df)
    y_train = train_df["label"]
    X_test = select_feature_matrix(test_df)
    y_test = test_df["label"]

    model = XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
        learning_rate=0.1,
        max_depth=4,
        n_estimators=200,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Log Loss:", log_loss(y_test, y_proba))
    print(classification_report(y_test, y_pred))

    os.makedirs(config.DATA_MODELS_DIR, exist_ok=True)
    joblib.dump(model, config.MODEL_PATH)
    with open(config.FEATURE_PATH, "w", encoding="utf-8") as f:
        json.dump(FEATURE_COLUMNS, f)
    print(f"Saved model to {config.MODEL_PATH}")
    print(f"Saved feature list to {config.FEATURE_PATH}")


if __name__ == "__main__":
    main()
