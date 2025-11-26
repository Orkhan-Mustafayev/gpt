"""football_ml package metadata and convenience exports."""
from __future__ import annotations

try:  # pragma: no cover - metadata lookup
    from importlib.metadata import version as _version
    __version__ = _version("football-ml")
except Exception:  # pragma: no cover - fallback when package not installed
    __version__ = "0.0.0"

__all__ = ["__version__"]
