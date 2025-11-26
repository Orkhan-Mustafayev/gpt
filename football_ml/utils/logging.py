"""Logging utilities for the project."""
from __future__ import annotations

import logging
import os
from typing import Optional


_LOGGER_CACHE: dict[str, logging.Logger] = {}


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Return a configured logger with a simple console handler."""
    if name in _LOGGER_CACHE:
        return _LOGGER_CACHE[name]

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    env_level = level or os.getenv("LOG_LEVEL", "INFO")
    logger.setLevel(env_level)
    logger.propagate = False
    _LOGGER_CACHE[name] = logger
    return logger
