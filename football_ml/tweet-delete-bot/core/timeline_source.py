"""Utilities for retrieving timelines via the Twitter client."""
from __future__ import annotations

import logging
from typing import Dict, List

from .twitter_client import TwitterClient

logger = logging.getLogger(__name__)


def fetch_user_timeline(client: TwitterClient, user_id: str, limit: int = 50) -> List[Dict]:
    """Fetch the latest tweets for a user id, handling errors gracefully."""
    try:
        return client.get_latest_tweets(user_id=user_id, limit=limit)
    except Exception:  # pragma: no cover - defensive logging
        logger.exception("Failed to fetch timeline for user %s", user_id)
        return []
