"""Training utilities and dataset preparation."""
from football_ml.training.dataset import (
    fetch_api_football,
    fetch_fd_history,
    load_processed,
    merge_sources,
)
from football_ml.training.train_xgb import main as train_xgb

__all__ = [
    "fetch_api_football",
    "fetch_fd_history",
    "load_processed",
    "merge_sources",
    "train_xgb",
]
