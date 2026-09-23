"""Instruction source: URL-list-driven procedural-page scraper.

Reads a curated list of URLs, fetches each via the configurable Fetcher
(direct / docling / mcp-playwright), splits the returned markdown into
heading-delimited sections, and keeps procedural sections in the word range.

Works with NO external service (default backend = direct). Set FETCH_BACKEND
=docling or =mcp (+ MCP_API_KEY) to use the remote render services.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

from .. import config
from ..fetcher import Fetcher
from . import Candidate

log = logging.getLogger(__name__)

DEFAULT_URLS = Path(__file__).resolve().parent.parent / "data" / "procedural_urls.txt"

STEP_MARKER_RE = re.compile(
    r"шаг\s*\d|во-первых|сначала|затем|после\s+этого|далее|первый\s+шаг",
    re.IGNORECASE,
)
PROC_TITLE_RE = re.compile(r"^(как|что\s+делать|каким\s+образом|какие\s+шаги|порядок)", re.IGNORECASE)
BROAD_PROC_RE = re.compile(
    r"шаг\s*\d|во-первых|сначала|затем|после\s+этого|далее|необходимо|следует|"
    r"для\s+этого|порядок|как\s+|что\s+делать|чтобы",
    re.IGNORECASE,
)
HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")


def _is_procedural(title: str, body: str, broad: bool = False) -> bool:
    if PROC_TITLE_RE.search(title) or STEP_MARKER_RE.search(body):
        return True
    if broad:
        return bool(BROAD_PROC_RE.search(body))
    return False


def load_urls(path: Path | None = None) -> list[str]:
    p = path or DEFAULT_URLS
    if not p.exists():
        log.warning("procedural url list not found: %s", p)
        return []
    urls: list[str] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            urls.append(s)
    return urls


def split_sections(markdown: str) -> list[tuple[str, str]]:
    """Split markdown into (heading, body) sections at # headings."""
    sections: list[tuple[str, str]] = []
    head = ""
    buf: list[str] = []
    for line in markdown.splitlines():
        m = HEADING_RE.match(line.strip())
        if m:
            if buf:
                sections.append((head, "\n".join(buf).strip()))
                buf = []
            head = m.group(2).strip()
        else:
            buf.append(line)
    if buf:
        sections.append((head, "\n".join(buf).strip()))
    return sections


def collect(
    url_list_file: str | None = None,
    backend: str | None = None,
    min_words: int = 200,
    max_words: int = 600,
    broad: bool = False,
) -> list[Candidate]:
    path = Path(url_list_file) if url_list_file else DEFAULT_URLS
    urls = load_urls(path)
    log.info(
        "procedural_pages: %d URLs, backend=%s, broad=%s", len(urls), backend or "default", broad
    )
    fetcher = Fetcher(backend=backend)
    candidates: list[Candidate] = []
    for url in urls:
        try:
            md = fetcher.fetch_markdown(url)
        except Exception as exc:  # noqa: BLE001
            log.warning("procedural_pages: fetch failed %s: %s", url, exc)
            continue
        for head, body in split_sections(md):
            wc = len(body.split())
            if not (min_words <= wc <= max_words):
                continue
            if not _is_procedural(head, body, broad=broad):
                continue
            candidates.append(
                Candidate(
                    text=body,
                    source_url=url,
                    source_name="Процедурная страница (gov)",
                    genre="ins",
                    title=head[:120] if head else url,
                    author="",
                    date_published="",
                    license=config.LICENSES["ins"],
                    license_proof=url,
                    topic=head[:80] if head else "государственные услуги",
                    notes="procedural_pages scraper",
                )
            )
    log.info("procedural_pages: %d candidates", len(candidates))
    return candidates
