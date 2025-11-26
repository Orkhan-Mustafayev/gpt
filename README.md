# football-ml

Lightweight package for fetching football data, building features (Elo, form, odds), training an XGBoost model, and predicting match outcomes.

## Installation
```bash
pip install -e .
```

## Training
```bash
python -m football_ml.training.train_xgb
```

## Predictions
```bash
python -m football_ml.prediction.predict_upcoming
```

For Colab instructions see `RUNBOOK_COLAB.md`.
