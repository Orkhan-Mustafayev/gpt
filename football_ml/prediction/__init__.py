"""Prediction entrypoints."""
from football_ml.prediction.predict_match import main as predict_match
from football_ml.prediction.predict_upcoming import main as predict_upcoming

__all__ = ["predict_match", "predict_upcoming"]
