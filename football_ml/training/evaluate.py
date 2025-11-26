"""Evaluation helpers."""
from __future__ import annotations

from typing import Dict
import numpy as np
from sklearn.metrics import accuracy_score, log_loss, classification_report


def evaluate_predictions(y_true, proba) -> Dict[str, float]:
    preds = np.argmax(proba, axis=1)
    metrics = {
        "accuracy": float(accuracy_score(y_true, preds)),
        "log_loss": float(log_loss(y_true, proba)),
    }
    metrics["classification_report"] = classification_report(y_true, preds)
    return metrics
