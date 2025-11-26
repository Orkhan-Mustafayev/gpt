"""Feature assembly pipeline."""
from __future__ import annotations

import pandas as pd

from football_ml import config
from football_ml.features import elo, form, odds


FEATURE_COLUMNS = [
    "elo_home",
    "elo_away",
    "elo_diff",
    "home_points_last{w}".format(w=config.FORM_WINDOW),
    "away_points_last{w}".format(w=config.FORM_WINDOW),
    "home_goal_diff_last{w}".format(w=config.FORM_WINDOW),
    "away_goal_diff_last{w}".format(w=config.FORM_WINDOW),
    "implied_prob_home",
    "implied_prob_draw",
    "implied_prob_away",
    "odds_margin",
]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Elo, form, and odds features on a match-level DataFrame."""
    features_df = elo.compute_elo_ratings(df, k=config.ELO_K)
    features_df = form.add_form_features(features_df, window=config.FORM_WINDOW)
    if {"home_odd", "draw_odd", "away_odd"}.issubset(features_df.columns):
        features_df = odds.add_implied_probabilities(features_df)
    for col in FEATURE_COLUMNS:
        if col not in features_df.columns:
            features_df[col] = pd.NA
    return features_df
