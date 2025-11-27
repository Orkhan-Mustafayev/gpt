"""Polling loop for tracking tweet deletions."""
from __future__ import annotations

import logging
import time
from typing import Dict

from bot.announcer import announce_deletion
from config.settings import settings
from core.delete_detector import detect_deleted_tweets
from core.timeline_source import fetch_user_timeline
from core.twitter_client import TwitterClient
from storage.state_store import load_state, save_state

logger = logging.getLogger(__name__)


class Poller:
    """Background poller that checks timelines for deletions."""

    def __init__(self, client: TwitterClient) -> None:
        self.client = client
        self.handle_to_id: Dict[str, str] = {}

    def _resolve_user_id(self, handle: str) -> str | None:
        if handle in self.handle_to_id:
            return self.handle_to_id[handle]
        try:
            user_id = self.client.get_user_id_by_handle(handle)
            self.handle_to_id[handle] = user_id
            logger.debug("Resolved handle %s to id %s", handle, user_id)
            return user_id
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Could not resolve handle %s", handle)
            return None

    def run(self) -> None:
        logger.info("Starting poller for handles: %s", ", ".join(settings.tracked_handles))
        state = load_state()

        while True:
            for handle in settings.tracked_handles:
                user_id = self._resolve_user_id(handle)
                if not user_id:
                    continue

                user_state = state.setdefault("users", {}).setdefault(user_id, {"handle": handle, "tweets": []})
                previous_tweets = user_state.get("tweets", [])
                current_tweets = fetch_user_timeline(self.client, user_id)

                deleted = detect_deleted_tweets(previous_tweets, current_tweets)
                for tweet in deleted:
                    announce_deletion(self.client, handle, tweet)

                user_state["tweets"] = current_tweets
                state["users"][user_id] = user_state

            save_state(state)
            try:
                time.sleep(settings.poll_interval_seconds)
            except KeyboardInterrupt:
                logger.info("Poller interrupted by user; exiting.")
                break
            except Exception:  # pragma: no cover - defensive logging
                logger.exception("Unexpected error during sleep phase")
