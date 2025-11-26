"""Rolling form features."""
from __future__ import annotations

import pandas as pd


def _result_points(home_goals: float, away_goals: float) -> tuple[int, int]:
    if home_goals > away_goals:
        return 3, 0
    if home_goals < away_goals:
        return 0, 3
    return 1, 1


def add_form_features(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    df = df.sort_values("utc_date").copy()
    df["home_points"] = df.apply(lambda r: _result_points(r.home_goals, r.away_goals)[0], axis=1)
    df["away_points"] = df.apply(lambda r: _result_points(r.home_goals, r.away_goals)[1], axis=1)

    for role, team_col, points_col, gf_col, ga_col in [
        ("home", "home_team", "home_points", "home_goals", "away_goals"),
        ("away", "away_team", "away_points", "away_goals", "home_goals"),
    ]:
        grouped = df.groupby(team_col)
        df[f"{role}_points_last{window}"] = grouped[points_col].shift(1).rolling(window).sum()
        df[f"{role}_goals_for_last{window}"] = grouped[gf_col].shift(1).rolling(window).sum()
        df[f"{role}_goals_against_last{window}"] = grouped[ga_col].shift(1).rolling(window).sum()
        df[f"{role}_goal_diff_last{window}"] = df[f"{role}_goals_for_last{window}"] - df[f"{role}_goals_against_last{window}"]

    df.drop(columns=["home_points", "away_points"], inplace=True)
    return df
