"""Local JSON-based state storage."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
STATE_FILE = DATA_DIR / "state.json"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> Dict[str, Any]:
    """Load state from disk, returning an empty structure if missing."""
    _ensure_data_dir()
    if not STATE_FILE.exists():
        return {"users": {}}

    try:
        with STATE_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # pragma: no cover - defensive logging
        logger.exception("Failed to read state file; starting fresh")
        return {"users": {}}


def save_state(state: Dict[str, Any]) -> None:
    """Persist state atomically to disk."""
    _ensure_data_dir()
    tmp_file = STATE_FILE.with_suffix(".tmp")
    with tmp_file.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    tmp_file.replace(STATE_FILE)
    logger.debug("State saved to %s", STATE_FILE)
