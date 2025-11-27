"""Entrypoint for the Tweet Delete Tracker bot."""
from __future__ import annotations

import logging

from config.settings import settings
from core.twitter_client import TwitterClient
from scheduler.poller import Poller

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s")


def main() -> None:
    client = TwitterClient(
        api_key=settings.api_key,
        api_secret=settings.api_secret,
        access_token=settings.access_token,
        access_secret=settings.access_secret,
        bearer_token=settings.bearer_token,
    )
    poller = Poller(client)
    poller.run()


if __name__ == "__main__":
    main()
