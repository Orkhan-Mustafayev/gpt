"""Shared HTTP client with retry, backoff, and simple rate-limit pacing."""
from __future__ import annotations

import time
from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from football_ml import config
from football_ml.utils import logging as log_utils


class BaseAPIClient:
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = config.TIMEOUT,
        max_retries: int = config.MAX_RETRIES,
        backoff_factor: float = config.BACKOFF_FACTOR,
        rate_limit_per_min: int = config.RATE_LIMIT_PER_MIN,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = headers or {}
        self.logger = log_utils.get_logger(self.__class__.__name__)
        self._min_interval = 60.0 / rate_limit_per_min if rate_limit_per_min > 0 else 0
        self._last_request_ts: float = 0.0

        retry_config = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_config)
        session = requests.Session()
        session.headers.update(self.headers)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        self.session = session

    def _respect_rate_limit(self) -> None:
        if self._min_interval <= 0:
            return
        elapsed = time.time() - self._last_request_ts
        sleep_for = self._min_interval - elapsed
        if sleep_for > 0:
            self.logger.debug("Sleeping %.2fs for rate limit", sleep_for)
            time.sleep(sleep_for)

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        self._respect_rate_limit()
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
        self._last_request_ts = time.time()
        if resp.status_code >= 400:
            self.logger.warning("HTTP %s %s -> %s %s", method, url, resp.status_code, resp.text)
        resp.raise_for_status()
        return resp

    def get(self, path: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        resp = self._request("GET", path, params=params, **kwargs)
        return resp.json()

    def paginate(self, path: str, params: Optional[Dict[str, Any]] = None, items_key: str = "data") -> list:
        """Simple pagination helper expecting 'page' and 'pageSize' params."""
        params = params.copy() if params else {}
        page = 1
        all_items = []
        while True:
            params.update({"page": page})
            payload = self.get(path, params=params)
            chunk = payload.get(items_key, []) if isinstance(payload, dict) else []
            all_items.extend(chunk)
            paging = payload.get("paging") if isinstance(payload, dict) else None
            total_pages = paging.get("total") if paging else None
            if total_pages and page >= int(total_pages):
                break
            if not chunk:
                break
            page += 1
        return all_items
