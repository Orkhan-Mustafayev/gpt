"""Announce tweet deletions."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
MAX_TWEET_LENGTH = 280


def _truncate(text: str, max_length: int) -> str:
    return text if len(text) <= max_length else text[: max_length - 1] + "…"


def announce_deletion(client, handle: str, deleted_tweet: dict) -> None:
    """Post a tweet announcing a deletion."""
    base_message = f"🧨 @{handle} bir tweet sildi:\n\nEski tweet: \"{deleted_tweet.get('text', '')}\""
    announcement = _truncate(base_message, MAX_TWEET_LENGTH)

    logger.info("Announcing deletion for @%s", handle)
    try:
        client.post_tweet(announcement)
    except Exception:  # pragma: no cover - defensive logging
        logger.exception("Failed to post announcement for @%s", handle)
