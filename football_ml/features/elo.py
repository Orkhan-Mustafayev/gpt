"""Elo rating computation."""
from __future__ import annotations

import pandas as pd


def compute_elo_ratings(matches_df: pd.DataFrame, k: float = 20.0) -> pd.DataFrame:
    df = matches_df.copy()
    df = df.sort_values("utc_date")
    ratings: dict[str, float] = {}
    elo_home_list = []
    elo_away_list = []

    for _, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        ratings.setdefault(home, 1500.0)
        ratings.setdefault(away, 1500.0)
        rating_home = ratings[home]
        rating_away = ratings[away]
        elo_home_list.append(rating_home)
        elo_away_list.append(rating_away)

        diff = rating_home - rating_away
        expected_home = 1 / (1 + 10 ** (-diff / 400))
        expected_away = 1 - expected_home

        home_goals = row.get("home_goals")
        away_goals = row.get("away_goals")
        if pd.isna(home_goals) or pd.isna(away_goals):
            continue
        if home_goals > away_goals:
            score_home, score_away = 1, 0
        elif home_goals < away_goals:
            score_home, score_away = 0, 1
        else:
            score_home = score_away = 0.5

        ratings[home] = rating_home + k * (score_home - expected_home)
        ratings[away] = rating_away + k * (score_away - expected_away)

    df["elo_home"] = elo_home_list
    df["elo_away"] = elo_away_list
    df["elo_diff"] = df["elo_home"] - df["elo_away"]
    return df
