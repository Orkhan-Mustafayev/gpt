"""I/O helpers and common paths."""
from __future__ import annotations

from pathlib import Path
from typing import Optional
import json
import pandas as pd
from football_ml.utils import logging as log_utils
from football_ml import config

logger = log_utils.get_logger(__name__)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def raw_path(filename: str) -> Path:
    ensure_dir(config.RAW_DIR)
    return config.RAW_DIR / filename


def processed_path(filename: str) -> Path:
    ensure_dir(config.PROCESSED_DIR)
    return config.PROCESSED_DIR / filename


def model_path(filename: str) -> Path:
    ensure_dir(config.MODELS_DIR)
    return config.MODELS_DIR / filename


def read_csv(path: Path, **kwargs) -> pd.DataFrame:
    logger.info("Loading %s", path)
    return pd.read_csv(path, **kwargs)


def write_csv(df: pd.DataFrame, path: Path, index: bool = False, **kwargs) -> None:
    ensure_dir(path.parent)
    logger.info("Writing %s", path)
    df.to_csv(path, index=index, **kwargs)


def write_json(obj: object, path: Path, **kwargs) -> None:
    ensure_dir(path.parent)
    logger.info("Writing %s", path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, **kwargs)


def read_json(path: Path, **kwargs):
    logger.info("Loading %s", path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f, **kwargs)
