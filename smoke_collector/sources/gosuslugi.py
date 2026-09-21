"""Instruction source: procedural help pages from government portals.

gosuslugi.ru is a JS SPA (no server-rendered content) and playwright cannot
be installed here (disk space), so we use statically-rendered procedural
pages from the Bank of Russia (cbr.ru) FAQ — a federal public portal whose
reference material is freely citable.
"""
from __future__ import annotations

import logging
import re

from bs4 import BeautifulSoup

from .. import config, http
from . import Candidate

log = logging.getLogger(__name__)

PAGES = [
    "https://cbr.ru/faq/credit_h/",
    "https://cbr.ru/faq/information_security/blokirovka-kart/",
    "https://cbr.ru/faq/pnp/",
]
STEP_MARKER_RE = re.compile(
    r"шаг\s*\d|во-первых|во-первых|сначала|затем|после\s+этого|далее|первый\s+шаг",
    re.IGNORECASE,
)


def _extract_sections(html: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    sections: list[tuple[str, str]] = []
    current_head = ""
    buf: list[str] = []
    for el in soup.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        txt = el.get_text(" ", strip=True)
        if not txt or len(txt) < 30:
            continue
        if el.name in ("h1", "h2", "h3", "h4"):
            if buf:
                sections.append((current_head, " ".join(buf)))
                buf = []
            current_head = txt
        else:
            buf.append(txt)
    if buf:
        sections.append((current_head, " ".join(buf)))
    return sections


def collect() -> list[Candidate]:
    log.info("instructions: fetching %d static gov pages", len(PAGES))
    candidates: list[Candidate] = []
    for url in PAGES:
        try:
            html = http.cached_get_text(url, ".html")
        except Exception as exc:  # noqa: BLE001
            log.warning("instructions: fetch failed %s: %s", url, exc)
            continue
        title_el = BeautifulSoup(html, "lxml").find("title")
        page_title = title_el.get_text(strip=True) if title_el else url
        for head, body in _extract_sections(html):
            wc = len(body.split())
            if not (200 <= wc <= 600):
                continue
            if not STEP_MARKER_RE.search(body):
                continue
            candidates.append(
                Candidate(
                    text=body,
                    source_url=url,
                    source_name="Банк России (cbr.ru)",
                    genre="ins",
                    title=head or page_title,
                    author="",
                    date_published="",
                    license=config.LICENSES["ins"],
                    license_proof=url,
                    topic="государственные услуги / финансовые процедуры",
                    notes="static procedural section",
                )
            )
    log.info("instructions: %d candidates", len(candidates))
    return candidates
