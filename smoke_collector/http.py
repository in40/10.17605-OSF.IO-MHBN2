"""Cached HTTP helper: 30s timeout, 3 retries with exponential backoff, disk cache."""
from __future__ import annotations

import hashlib
import logging
import time
from pathlib import Path

import requests

from . import config

log = logging.getLogger(__name__)

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 smoke_collector/1.0"
)


def _cache_path(key: str, suffix: str = "") -> Path:
    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return config.CACHE_DIR / (hashlib.sha256(key.encode()).hexdigest() + suffix)


def cached_get_bytes(url: str, suffix: str = "", headers: dict | None = None) -> Path:
    path = _cache_path(url, suffix)
    if path.exists() and path.stat().st_size > 0:
        log.debug("cache hit: %s -> %s", url, path)
        return path
    data = fetch_bytes(url, headers)
    path.write_bytes(data)
    log.info("cached: %s -> %s (%d bytes)", url, path, len(data))
    return path


def cached_get_text(url: str, suffix: str = ".html", headers: dict | None = None) -> str:
    return cached_get_bytes(url, suffix, headers).read_text(encoding="utf-8", errors="replace")


def fetch_bytes(url: str, headers: dict | None = None) -> bytes:
    hdrs = {"User-Agent": UA}
    if headers:
        hdrs.update(headers)
    last_exc: Exception | None = None
    for attempt in range(config.HTTP_RETRIES):
        try:
            log.debug("GET %s (attempt %d)", url, attempt + 1)
            resp = requests.get(url, headers=hdrs, timeout=config.HTTP_TIMEOUT)
            resp.raise_for_status()
            return resp.content
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            delay = 2 ** attempt
            log.warning("GET %s failed (%s), retry in %ds", url, exc, delay)
            time.sleep(delay)
    raise RuntimeError(f"GET {url} failed after {config.HTTP_RETRIES} retries") from last_exc
