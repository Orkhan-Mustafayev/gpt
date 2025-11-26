"""Odds-based implied probability features."""
from __future__ import annotations

import pandas as pd


def add_implied_probabilities(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col_src, col_dst in [
        ("home_odd", "implied_prob_home"),
        ("draw_odd", "implied_prob_draw"),
        ("away_odd", "implied_prob_away"),
    ]:
        df[col_dst] = 1 / df[col_src].astype(float)
    df["odds_margin"] = df[["implied_prob_home", "implied_prob_draw", "implied_prob_away"]].sum(axis=1)
    return df
