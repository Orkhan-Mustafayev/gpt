"""Detect tweet deletions between two snapshots."""
from __future__ import annotations

from typing import List, Dict


def detect_deleted_tweets(previous_tweets: List[Dict], current_tweets: List[Dict]) -> List[Dict]:
    """Return tweets that disappeared between snapshots.

    Args:
        previous_tweets: Tweets seen in the last poll.
        current_tweets: Tweets retrieved in the current poll.

    Returns:
        A list of tweet dicts representing deletions.
    """

    current_ids = {tweet["id"] for tweet in current_tweets}
    deleted = [tweet for tweet in previous_tweets if tweet.get("id") not in current_ids]
    return deleted
