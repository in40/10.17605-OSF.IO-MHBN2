"""Configurable URL fetcher with multiple backends + caching + graceful fallback.

Backends:
  - "direct"  : plain requests + BeautifulSoup -> simple markdown (NO external service)
  - "docling" : Docling Serve (static fetch, clean markdown, no auth)
  - "mcp"     : playwright MCP fetch_url (renders JS, needs X-API-Key)
  - "auto"    : mcp (if key) -> docling -> direct

Default backend is "direct", so the pipeline works with NO external service.
If a configured backend fails, it falls back down the chain.
Override via env: FETCH_BACKEND, MCP_FETCH_URL, MCP_API_KEY, DOCLING_URL.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os

import requests
from bs4 import BeautifulSoup

from . import config

log = logging.getLogger(__name__)

DEFAULT_MCP_URL = "http://45.145.191.144:8094/mcp"
DEFAULT_DOCLING_URL = "http://45.145.191.144:5012"


class Fetcher:
    def __init__(
        self,
        backend: str | None = None,
        mcp_url: str | None = None,
        mcp_key: str | None = None,
        docling_url: str | None = None,
        timeout: int = 60,
        retries: int = 2,
    ) -> None:
        self.backend = (backend or os.environ.get("FETCH_BACKEND", "direct")).lower()
        self.mcp_url = mcp_url or os.environ.get("MCP_FETCH_URL", DEFAULT_MCP_URL)
        self.mcp_key = mcp_key or os.environ.get("MCP_API_KEY", "")
        self.docling_url = docling_url or os.environ.get("DOCLING_URL", DEFAULT_DOCLING_URL)
        self.timeout = timeout
        self.retries = retries

    # ---- public ----
    def fetch_markdown(self, url: str) -> str:
        cached = self._cache_get(url)
        if cached is not None:
            log.debug("fetch cache hit: %s", url)
            return cached
        md = self._fetch_live(url)
        self._cache_put(url, md)
        return md

    # ---- backend dispatch with fallback ----
    def _backend_order(self) -> list[str]:
        if self.backend == "auto":
            order = []
            if self.mcp_key:
                order.append("mcp")
            order += ["docling", "direct"]
            return order
        if self.backend == "mcp":
            return ["mcp", "direct"] if self.mcp_key else ["direct"]
        if self.backend == "docling":
            return ["docling", "direct"]
        return ["direct"]

    def _fetch_live(self, url: str) -> str:
        last: Exception | None = None
        for backend in self._backend_order():
            try:
                fn = {"mcp": self._mcp, "docling": self._docling, "direct": self._direct}[backend]
                md = fn(url)
                if md and md.strip():
                    log.info("fetched via %s: %s (%d chars)", backend, url, len(md))
                    return md
                raise RuntimeError("empty result")
            except Exception as exc:  # noqa: BLE001
                last = exc
                log.warning("fetch backend '%s' failed for %s: %s", backend, url, exc)
        raise RuntimeError(f"all fetch backends failed for {url}") from last

    # ---- backends ----
    def _mcp(self, url: str) -> str:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "fetch_url", "arguments": {"url": url}},
        }
        resp = requests.post(
            self.mcp_url,
            headers={"Content-Type": "application/json", "X-API-Key": self.mcp_key},
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"mcp error: {data['error']}")
        text = "".join(c.get("text", "") for c in data.get("result", {}).get("content", []))
        try:
            obj = json.loads(text)
            return obj.get("content", text)
        except json.JSONDecodeError:
            return text

    def _docling(self, url: str) -> str:
        payload = {"sources": [{"kind": "http", "url": url}], "to_formats": ["md"]}
        resp = requests.post(
            f"{self.docling_url.rstrip('/')}/v1/convert/source",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return (data.get("document") or {}).get("md_content", "")

    def _direct(self, url: str) -> str:
        resp = requests.get(
            url, headers={"User-Agent": config.UA if hasattr(config, "UA") else "Mozilla/5.0"},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return self._html_to_md(resp.text)

    @staticmethod
    def _html_to_md(html: str) -> str:
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        out: list[str] = []
        for el in soup.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
            txt = el.get_text(" ", strip=True)
            if not txt:
                continue
            if el.name in ("h1", "h2", "h3", "h4"):
                out.append("#" * int(el.name[1]) + " " + txt)
            elif el.name == "li":
                out.append("- " + txt)
            else:
                out.append(txt)
        return "\n\n".join(out)

    # ---- cache ----
    def _cache_path(self, url: str) -> "os.PathLike":
        config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        return config.CACHE_DIR / ("fetch_" + hashlib.sha256(url.encode()).hexdigest() + ".md")

    def _cache_get(self, url: str) -> str | None:
        p = self._cache_path(url)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return open(p, encoding="utf-8").read()
        return None

    def _cache_put(self, url: str, md: str) -> None:
        open(self._cache_path(url), "w", encoding="utf-8").write(md)
