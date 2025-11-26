"""Configuration for API keys and default settings.

This module centralizes configuration such as API tokens and default
competition/league identifiers. Environment variables are preferred so
secrets are not stored in code, but sensible placeholders are provided
for development.
"""
from __future__ import annotations

import os
from typing import List

# API tokens / hosts ---------------------------------------------------------
# football-data.org token. Create a free account and copy your token.
FOOTBALL_DATA_API_TOKEN: str | None = os.environ.get("FOOTBALL_DATA_API_TOKEN", "YOUR_FOOTBALL_DATA_TOKEN")

# RapidAPI credentials for "Free API Live Football Data".
FREE_API_RAPID_KEY: str | None = os.environ.get("FREE_API_RAPID_KEY", "YOUR_RAPID_API_KEY")
FREE_API_HOST: str = os.environ.get("FREE_API_HOST", "free-api-live-football-data.p.rapidapi.com")

# Defaults for fetching data -------------------------------------------------
FD_COMPETITION_CODE: str = os.environ.get("FD_COMPETITION_CODE", "PL")
SEASONS: List[int] = [int(s) for s in os.environ.get("SEASONS", "2021,2022,2023").split(",")]

# Example league id for Premier League on the Free API (adjust as needed)
FREE_API_LEAGUE_ID: int = int(os.environ.get("FREE_API_LEAGUE_ID", 39))

# Paths ----------------------------------------------------------------------
DATA_RAW_DIR = "football_ml/data/raw"
DATA_PROCESSED_DIR = "football_ml/data/processed"
DATA_MODELS_DIR = "football_ml/data/models"

# Model filenames
MODEL_PATH = os.path.join(DATA_MODELS_DIR, "match_model_xgb.pkl")
FEATURE_PATH = os.path.join(DATA_MODELS_DIR, "feature_columns.json")
