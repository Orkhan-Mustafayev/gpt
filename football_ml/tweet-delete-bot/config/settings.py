"""Application configuration for the Tweet Delete Tracker bot."""
from __future__ import annotations

import os
import warnings
from dataclasses import dataclass, field
from typing import List


@dataclass
class Settings:
    """Environment-driven settings for the bot."""

    api_key: str = field(default_factory=lambda: os.getenv("X_API_KEY", ""))
    api_secret: str = field(default_factory=lambda: os.getenv("X_API_SECRET", ""))
    access_token: str = field(default_factory=lambda: os.getenv("X_ACCESS_TOKEN", ""))
    access_secret: str = field(default_factory=lambda: os.getenv("X_ACCESS_SECRET", ""))
    bearer_token: str = field(default_factory=lambda: os.getenv("X_BEARER_TOKEN", ""))

    tracked_handles: List[str] = field(
        default_factory=lambda: os.getenv("TRACKED_HANDLES", "").split(",")
        if os.getenv("TRACKED_HANDLES")
        else []
    )
    poll_interval_seconds: int = field(
        default_factory=lambda: int(os.getenv("POLL_INTERVAL_SECONDS", "120"))
    )

    def __post_init__(self) -> None:
        missing = [
            name
            for name, value in {
                "X_API_KEY": self.api_key,
                "X_API_SECRET": self.api_secret,
                "X_ACCESS_TOKEN": self.access_token,
                "X_ACCESS_SECRET": self.access_secret,
            }.items()
            if not value
        ]
        if missing:
            warnings.warn(
                "Missing Twitter API credentials for: " + ", ".join(missing)
            )

        if not self.tracked_handles:
            warnings.warn(
                "TRACKED_HANDLES is empty. Add comma-separated handles to monitor deletions."
            )


settings = Settings()
