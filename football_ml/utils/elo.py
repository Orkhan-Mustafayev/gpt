"""Elo rating helper utilities."""
from __future__ import annotations

import pandas as pd
from typing import Dict


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1 + 10 ** (-(rating_a - rating_b) / 400))


def compute_elo_ratings(matches_df: pd.DataFrame, k: float = 20.0) -> pd.DataFrame:
    """Compute Elo ratings chronologically and attach to the DataFrame.

    Args:
        matches_df: DataFrame with columns home_team, away_team, home_goals,
            away_goals, utc_date.
        k: Elo K-factor.

    Returns:
        DataFrame with added columns elo_home, elo_away, elo_diff.
    """
    df = matches_df.sort_values("utc_date").copy()
    ratings: Dict[str, float] = {}
    elo_home_list = []
    elo_away_list = []

    for _, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        ratings.setdefault(home, 1500.0)
        ratings.setdefault(away, 1500.0)

        r_home = ratings[home]
        r_away = ratings[away]
        elo_home_list.append(r_home)
        elo_away_list.append(r_away)

        # Determine outcome score
        if row["home_goals"] > row["away_goals"]:
            score_home, score_away = 1.0, 0.0
        elif row["home_goals"] == row["away_goals"]:
            score_home, score_away = 0.5, 0.5
        else:
            score_home, score_away = 0.0, 1.0

        exp_home = expected_score(r_home, r_away)
        exp_away = expected_score(r_away, r_home)

        ratings[home] = r_home + k * (score_home - exp_home)
        ratings[away] = r_away + k * (score_away - exp_away)

    df["elo_home"] = elo_home_list
    df["elo_away"] = elo_away_list
    df["elo_diff"] = df["elo_home"] - df["elo_away"]
    return df
