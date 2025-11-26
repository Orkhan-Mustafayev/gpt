"""Merge raw datasets from football-data.org and Free API Live.

This script builds a unified match dataset with labels for model training.
"""
from __future__ import annotations

import os
import pandas as pd

from football_ml import config


def make_match_key(df: pd.DataFrame) -> pd.Series:
    """Create a deterministic key based on date and team names."""
    return (
        df["utc_date"].astype(str).str.slice(0, 10)
        + "_"
        + df["home_team"].str.lower().str.replace(" ", "", regex=False)
        + "_"
        + df["away_team"].str.lower().str.replace(" ", "", regex=False)
    )


def label_result(row: pd.Series) -> int:
    """Encode match result as 0=home win, 1=draw, 2=away win."""
    if pd.isna(row["home_goals"]) or pd.isna(row["away_goals"]):
        return None
    if row["home_goals"] > row["away_goals"]:
        return 0
    if row["home_goals"] == row["away_goals"]:
        return 1
    return 2


def merge_datasets(fd_path: str, free_path: str) -> pd.DataFrame:
    fd_df = pd.read_csv(fd_path)
    free_df = pd.read_csv(free_path)

    fd_df["match_key"] = make_match_key(fd_df)
    free_df["match_key"] = make_match_key(free_df)

    merged = fd_df.merge(
        free_df,
        on="match_key",
        how="left",
        suffixes=("_fd", "_free"),
    )

    merged["label"] = merged.apply(label_result, axis=1)
    return merged


def main() -> None:
    os.makedirs(config.DATA_PROCESSED_DIR, exist_ok=True)
    fd_path = os.path.join(config.DATA_RAW_DIR, "matches_fd.csv")
    free_path = os.path.join(config.DATA_RAW_DIR, "matches_free.csv")

    merged = merge_datasets(fd_path, free_path)
    output_path = os.path.join(config.DATA_PROCESSED_DIR, "matches_merged.csv")
    merged.to_csv(output_path, index=False)
    print(f"Merged dataset saved to {output_path} ({len(merged)} rows)")


if __name__ == "__main__":
    main()
