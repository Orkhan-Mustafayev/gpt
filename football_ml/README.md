# Football ML Match Prediction

An educational end-to-end machine learning pipeline for predicting football match outcomes (home win / draw / away win). It fetches data from two public APIs, engineers features (including Elo and form), trains a multi-class classifier, and scores upcoming fixtures or bespoke head-to-head matchups.

## Project Structure
```
football_ml/
  config.py                # Configuration and API keys
  data/
    raw/                   # Raw downloads from APIs
    processed/             # Merged datasets and predictions
    models/                # Saved models and feature metadata
  data_sources/
    football_data_org.py   # Client for football-data.org
    free_api_live.py       # Client for Free API Live (RapidAPI)
  pipeline/
    merge_raw.py           # Merge raw datasets and create labels
    build_features_and_train.py  # Feature engineering + model training
    predict_upcoming.py    # Predict probabilities for upcoming fixtures
    predict_match.py       # Predict a single matchup by fetching fixture+odds from APIs
  utils/
    elo.py                 # Elo rating helper
    features.py            # Feature engineering utilities
  requirements.txt         # Python dependencies
```

## Setup
1. Install Python 3.10+ and create a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   The keys are documented in [API.md](API.md).
4. Set environment variables (or create a `.env` and load separately):
   - `FOOTBALL_DATA_API_TOKEN` – token from [football-data.org](https://www.football-data.org/)
   - `FREE_API_RAPID_KEY` – RapidAPI key for "Free API Live Football Data"
   - `FREE_API_HOST` – defaults to `free-api-live-football-data.p.rapidapi.com`
   - Optional overrides: `FD_COMPETITION_CODE`, `SEASONS`, `FREE_API_LEAGUE_ID`

## Usage
1. **Fetch historical results (football-data.org):**
   ```bash
   python -m football_ml.data_sources.football_data_org
   ```
2. **Fetch fixtures & odds (Free API Live):**
   ```bash
   python -m football_ml.data_sources.free_api_live
   ```
3. **Merge raw datasets:**
   ```bash
   python -m football_ml.pipeline.merge_raw
   ```
4. **Build features & train model:**
   ```bash
   python -m football_ml.pipeline.build_features_and_train
   ```
5. **Predict upcoming fixtures:**
   ```bash
   python -m football_ml.pipeline.predict_upcoming
   ```
6. **Predict a specific matchup (API-backed fixture + odds):**
   ```bash
   python -m football_ml.pipeline.predict_match --home "Arsenal" --away "Chelsea"
   ```
   The script pulls the matching fixture (and available odds) from Free API Live, then prints percentage probabilities for home win, draw, and away win plus the model's highest-confidence outcome.

## Notes
- API schemas can differ; adjust field extraction as needed.
- Predictions are grounded in stats pulled from the configured APIs—ensure the fetch steps succeed before scoring matches.
- The project is for experimentation only—no guarantee of betting profitability.
- Time-based splits avoid leakage by training on past seasons and testing on the latest season.
