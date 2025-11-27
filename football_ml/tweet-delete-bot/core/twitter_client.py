"""Lightweight wrapper around the X (Twitter) API."""
from __future__ import annotations

import logging
from typing import List

import tweepy

logger = logging.getLogger(__name__)


class TwitterClient:
    """Wrapper around Tweepy for basic operations used by the bot.

    This implementation assumes access to the X API v2 with read/write permissions.
    Depending on your API tier you might need to adjust endpoints or rate limits.
    """

    def __init__(self, api_key: str, api_secret: str, access_token: str, access_secret: str, bearer_token: str | None = None) -> None:
        # TODO: Ensure that your X API access level allows timeline lookups and tweet posting.
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        self._api = tweepy.API(auth)
        self._client_v2 = (
            tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret,
            )
            if bearer_token
            else None
        )

    def get_user_id_by_handle(self, handle: str) -> str:
        """Resolve a handle (without @) to a numeric user id."""
        logger.debug("Resolving user id for handle %s", handle)
        user = self._api.get_user(screen_name=handle)
        return str(user.id)

    def get_latest_tweets(self, user_id: str, limit: int = 50) -> List[dict]:
        """Fetch recent tweets for a user.

        Uses the v2 client if a bearer token is configured, otherwise falls back to
        the v1.1 timeline which might be subject to stricter limits.
        """
        logger.debug("Fetching up to %s tweets for user %s", limit, user_id)
        if self._client_v2:
            tweets = self._client_v2.get_users_tweets(
                id=user_id, max_results=min(limit, 100), tweet_fields=["created_at"], exclude=["retweets", "replies"]
            )
            data = tweets.data or []
            return [
                {"id": str(tweet.id), "text": tweet.text, "created_at": tweet.created_at.isoformat() if tweet.created_at else ""}
                for tweet in data
            ]

        timeline = self._api.user_timeline(user_id=user_id, count=limit, tweet_mode="extended", exclude_replies=True, include_rts=False)
        return [
            {"id": str(status.id), "text": status.full_text, "created_at": status.created_at.isoformat()}
            for status in timeline
        ]

    def post_tweet(self, text: str) -> None:
        """Post a tweet from the authenticated account."""
        logger.info("Posting announcement tweet")
        if self._client_v2:
            self._client_v2.create_tweet(text=text)
            return
        self._api.update_status(status=text)
