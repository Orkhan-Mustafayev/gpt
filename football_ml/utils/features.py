"""Feature engineering helpers."""
from __future__ import annotations

import pandas as pd


def _compute_team_form(df: pd.DataFrame, window: int) -> pd.DataFrame:
    # Convert match outcome to points
    df = df.copy()
    df["points_home"] = (df["home_goals"] > df["away_goals"]) * 3 + (df["home_goals"] == df["away_goals"]) * 1
    df["points_away"] = (df["away_goals"] > df["home_goals"]) * 3 + (df["home_goals"] == df["away_goals"]) * 1

    home_form = (
        df.sort_values("utc_date")
        .groupby("home_team")
        .apply(
            lambda g: g.assign(
                points_lastN=g["points_home"].shift(1).rolling(window).sum(),
                goals_for_lastN=g["home_goals"].shift(1).rolling(window).sum(),
                goals_against_lastN=g["away_goals"].shift(1).rolling(window).sum(),
                goal_diff_lastN=g["home_goals"].shift(1).rolling(window).sum()
                - g["away_goals"].shift(1).rolling(window).sum(),
            )
        )
        .reset_index(drop=True)
    )

    away_form = (
        df.sort_values("utc_date")
        .groupby("away_team")
        .apply(
            lambda g: g.assign(
                points_lastN=g["points_away"].shift(1).rolling(window).sum(),
                goals_for_lastN=g["away_goals"].shift(1).rolling(window).sum(),
                goals_against_lastN=g["home_goals"].shift(1).rolling(window).sum(),
                goal_diff_lastN=g["away_goals"].shift(1).rolling(window).sum()
                - g["home_goals"].shift(1).rolling(window).sum(),
            )
        )
        .reset_index(drop=True)
    )

    # Merge back keeping home/away suffixes
    merged = df.merge(
        home_form[["utc_date", "home_team", "points_lastN", "goal_diff_lastN"]],
        on=["utc_date", "home_team"],
        how="left",
        suffixes=("", "_homeform"),
    )
    merged = merged.merge(
        away_form[["utc_date", "away_team", "points_lastN", "goal_diff_lastN"]],
        on=["utc_date", "away_team"],
        how="left",
        suffixes=("", "_awayform"),
    )
    merged.rename(
        columns={
            "points_lastN_homeform": "home_points_lastN",
            "goal_diff_lastN_homeform": "home_goal_diff_lastN",
            "points_lastN_awayform": "away_points_lastN",
            "goal_diff_lastN_awayform": "away_goal_diff_lastN",
        },
        inplace=True,
    )
    return merged


def add_form_features(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Add rolling form features for each team using the previous `window` matches."""
    return _compute_team_form(df, window)


def add_implied_prob_features(df: pd.DataFrame) -> pd.DataFrame:
    """Convert odds to implied probabilities."""
    df = df.copy()
    for col, new_col in [("home_odd", "implied_prob_home"), ("draw_odd", "implied_prob_draw"), ("away_odd", "implied_prob_away")]:
        if col in df:
            df[new_col] = 1 / df[col]
    return df
