"""Dataset fetching, normalization, merging, and labeling."""
from __future__ import annotations

from typing import List
import pandas as pd

from football_ml import config
from football_ml.api.football_data_org import FootballDataOrgClient
from football_ml.api.api_football import APIFootballClient
from football_ml.utils import io
from football_ml.utils import logging as log_utils

logger = log_utils.get_logger(__name__)


def fetch_fd_history(competition_code: str, seasons: List[int]) -> pd.DataFrame:
    client = FootballDataOrgClient()
    df = client.fetch_multi_season(competition_code, seasons)
    if not df.empty:
        io.write_csv(df, io.raw_path("matches_fd.csv"))
    return df


def fetch_api_football(league_id: int, season: int) -> pd.DataFrame:
    client = APIFootballClient()
    fixtures = client.get_fixtures(league_id, season)
    if fixtures.empty:
        return fixtures
    odds = client.get_odds(fixtures["fixture_id"].dropna().astype(int).tolist())
    if not odds.empty:
        fixtures = fixtures.merge(odds, on="fixture_id", how="left")
    io.write_csv(fixtures, io.raw_path("matches_api_football.csv"))
    return fixtures


def make_match_key(df: pd.DataFrame) -> pd.Series:
    return (
        pd.to_datetime(df["utc_date"]).dt.date.astype(str)
        + "_"
        + df["home_team"].str.lower().str.replace(" ", "", regex=False)
        + "_"
        + df["away_team"].str.lower().str.replace(" ", "", regex=False)
    )


def merge_sources(fd_df: pd.DataFrame, api_df: pd.DataFrame) -> pd.DataFrame:
    if fd_df.empty or api_df.empty:
        return pd.DataFrame()
    fd_df = fd_df.copy()
    api_df = api_df.copy()
    fd_df["match_key"] = make_match_key(fd_df)
    api_df["match_key"] = make_match_key(api_df)
    merged = fd_df.merge(
        api_df[
            [
                "match_key",
                "fixture_id",
                "home_odd",
                "draw_odd",
                "away_odd",
                "league_id",
            ]
        ],
        on="match_key",
        how="left",
    )
    merged["label"] = merged.apply(_label_outcome, axis=1)
    io.write_csv(merged, io.processed_path("matches_merged.csv"))
    return merged


def _label_outcome(row: pd.Series) -> int:
    if pd.isna(row.home_goals) or pd.isna(row.away_goals):
        return -1
    if row.home_goals > row.away_goals:
        return 0
    if row.home_goals < row.away_goals:
        return 2
    return 1


def load_processed() -> pd.DataFrame:
    path = io.processed_path("matches_merged.csv")
    if path.exists():
        return io.read_csv(path)
    return pd.DataFrame()
