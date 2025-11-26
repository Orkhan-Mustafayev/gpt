# API Guide

This project relies on two public football data providers. Use this guide to obtain credentials, understand the endpoints being called, and see where each API is referenced in the codebase.

## 1) football-data.org (historical results)
- **Purpose:** Clean historical match results used to build training labels and baseline stats.
- **Sign-up:** Create a free account at https://www.football-data.org/ and generate a v4 API token.
- **Credential:** `FOOTBALL_DATA_API_TOKEN` (set as an environment variable or via `.env`).
- **Endpoint pattern:** `https://api.football-data.org/v4/competitions/{competition_code}/matches?season={season}`.
- **Headers:** `X-Auth-Token: <FOOTBALL_DATA_API_TOKEN>`.
- **Code reference:**
  - `data_sources/football_data_org.py` → `fetch_matches` and `fetch_multi_season` handle retrieval and CSV export to `data/raw/matches_fd.csv`.
- **Config knobs:**
  - `FD_COMPETITION_CODE` (e.g., `PL` for Premier League) and `SEASONS` in `config.py`.

## 2) Free API Live Football Data via RapidAPI (fixtures + odds)
- **Purpose:** Upcoming fixtures and pre-match odds that feed the merged dataset and live predictions.
- **Sign-up:** Create a RapidAPI account at https://rapidapi.com/ and subscribe to the "Free API Live Football Data" API.
- **Credentials:**
  - `FREE_API_RAPID_KEY` (RapidAPI key)
  - `FREE_API_HOST` (usually `free-api-live-football-data.p.rapidapi.com`)
- **Endpoint patterns (adjust per provider docs):**
  - Fixtures: `https://{FREE_API_HOST}/fixtures?league={league_id}&season={season}`
  - Odds: `https://{FREE_API_HOST}/odds?fixture={fixture_id}`
- **Headers:**
  - `X-RapidAPI-Key: <FREE_API_RAPID_KEY>`
  - `X-RapidAPI-Host: <FREE_API_HOST>`
- **Code reference:**
  - `data_sources/free_api_live.py` → `get_fixtures_by_league` and `get_odds_for_fixture` export to `data/raw/matches_free.csv`.
  - `pipeline/predict_match.py` and `pipeline/predict_upcoming.py` fetch fixtures/odds to build prediction rows.
- **Config knobs:**
  - `FREE_API_LEAGUE_ID` (league numeric ID) and `SEASONS` in `config.py`.

## Where credentials are loaded
- Environment variables are read in `config.py`, which provides defaults and propagates into the data source and pipeline scripts.
- Start by copying `.env.example` to `.env` and filling your keys, or export variables before running any fetch or prediction commands, e.g.:
  ```bash
  export FOOTBALL_DATA_API_TOKEN="<your_fd_token>"
  export FREE_API_RAPID_KEY="<your_rapid_key>"
  export FREE_API_HOST="free-api-live-football-data.p.rapidapi.com"
  ```

## When each API is used in the project
- **Historical ingestion:** `python -m football_ml.data_sources.football_data_org` writes `data/raw/matches_fd.csv`.
- **Fixtures & odds ingestion:** `python -m football_ml.data_sources.free_api_live` writes `data/raw/matches_free.csv`.
- **Merging & labeling:** `python -m football_ml.pipeline.merge_raw` combines both CSVs to build `data/processed/matches_merged.csv` with match outcomes.
- **Model training:** `python -m football_ml.pipeline.build_features_and_train` consumes the merged dataset and saves the model + feature metadata to `data/models/`.
- **Predictions:** `python -m football_ml.pipeline.predict_upcoming` and `python -m football_ml.pipeline.predict_match` both fetch fixtures/odds from RapidAPI, then apply the trained model to generate probabilities.

## Quick checklist before running
1. Obtain both API keys (football-data.org token and RapidAPI key).
2. Export them as environment variables (or place in `.env`).
3. Run the football-data.org fetch, then the RapidAPI fetch, before merging and training.
4. For predictions, ensure recent fixtures/odds have been fetched so the model can build features from fresh API data.
