"""Project configuration for football_ml.

Reads API credentials and defaults from environment variables with sensible fallbacks.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"

# API credentials
FOOTBALL_DATA_API_TOKEN = os.getenv("FOOTBALL_DATA_API_TOKEN", "")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "")
API_FOOTBALL_HOST = os.getenv("API_FOOTBALL_HOST", "v3.football.api-sports.io")

# Competition defaults
FD_COMPETITION_CODE = os.getenv("FD_COMPETITION_CODE", "PL")
API_FOOTBALL_LEAGUE_ID = int(os.getenv("API_FOOTBALL_LEAGUE_ID", "39"))
SEASONS: List[int] = [int(s) for s in os.getenv("SEASONS", "2022,2023").split(",") if s.strip()]

# Rate limit controls (simple safeguards)
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "50"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
BACKOFF_FACTOR = float(os.getenv("BACKOFF_FACTOR", "0.5"))
TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "30"))

# Feature defaults
FORM_WINDOW = int(os.getenv("FORM_WINDOW", "5"))
ELO_K = float(os.getenv("ELO_K", "20.0"))
