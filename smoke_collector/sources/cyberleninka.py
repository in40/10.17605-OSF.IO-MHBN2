"""Scientific source: CyberLeninka OA articles with CC BY license.

BFS crawl from seed article slugs (article pages are server-rendered and
robots-allowed; /search and /api are disallowed and not used).
License verified per-item from the CC label on each article page.
"""
from __future__ import annotations

import logging
import re
import time
from collections import deque
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .. import config, http
from . import Candidate

log = logging.getLogger(__name__)

BASE = "https://cyberleninka.ru"
SEEDS = [
    "/article/n/ponyatie-ekonomicheskoy-bezopasnosti-predpriyatiya",
    "/article/n/infrastruktura-otkrytoy-nauki",
    "/article/n/otkrytyy-dostup-k-nauke-mify-i-realnost",
    "/article/n/vozmozhnye-puti-razvitiya-otkrytoy-nauki-v-rossii",
]
MAX_PAGES = 60
RATE_DELAY = 1.5
MATH_SYMBOLS = re.compile(r"[∑∫√≤≥≠≈±×÷∞∂∇∈∪∩⊂⊃⇒⇔]|\\frac|\\sum|\\int|\\alpha|\\beta|\\gamma")
H1_SUFFIX_RE = re.compile(r"\s*Текст научной статьи по специальности\s*«([^»]+)».*$", re.DOTALL)


def _passages(text: str, target: int, tol: float = 0.10) -> list[str]:
    lo, hi = target * (1 - tol), target * (1 + tol)
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    out: list[str] = []
    cur: list[str] = []
    wc = 0
    for p in paras:
        pw = len(p.split())
        if wc + pw > hi and wc >= lo:
            out.append("\n\n".join(cur))
            cur = []
            wc = 0
        cur.append(p)
        wc += pw
    if lo <= wc <= hi:
        out.append("\n\n".join(cur))
    return out


def _extract_abstract(text: str) -> str:
    m = re.search(r"Аннотация[.:]?\s*(.+?)(?:Ключевые\s+слова|Ключевые\s+слова|Abstract)", text, re.DOTALL)
    if not m:
        return ""
    abstract = m.group(1).strip()
    return abstract if len(abstract.split()) >= 80 else ""


def _parse_article(html: str, url: str) -> dict | None:
    soup = BeautifulSoup(html, "lxml")
    h1 = soup.find("h1")
    if not h1:
        return None
    raw_title = h1.get_text(" ", strip=True)
    m = H1_SUFFIX_RE.search(raw_title)
    specialty = m.group(1) if m else ""
    title = H1_SUFFIX_RE.sub("", raw_title).strip()
    lic_el = soup.find(class_="label-cc")
    lic_text = lic_el.get_text(" ", strip=True) if lic_el else ""
    body = soup.select_one("div.full div.ocr") or soup.find(class_="ocr")
    if not body:
        return None
    paras = [p.get_text(" ", strip=True) for p in body.find_all("p")]
    text = "\n\n".join(p for p in paras if p)
    links = [a.get("href") for a in soup.find_all("a", href=re.compile(r"^/article/n/"))]
    return {
        "title": title,
        "specialty": specialty,
        "license": lic_text,
        "text": text,
        "links": links,
    }


def collect() -> list[Candidate]:
    log.info("cyberleninka: BFS crawl from %d seeds", len(SEEDS))
    seen: set[str] = set()
    queue: deque[str] = deque(SEEDS)
    candidates: list[Candidate] = []
    fetched = 0
    while queue and fetched < MAX_PAGES:
        path = queue.popleft()
        if path in seen:
            continue
        seen.add(path)
        url = urljoin(BASE, path)
        try:
            html = http.cached_get_text(url, ".html")
        except Exception as exc:  # noqa: BLE001
            log.warning("cyberleninka: fetch failed %s: %s", url, exc)
            continue
        fetched += 1
        art = _parse_article(html, url)
        if not art:
            continue
        for link in art["links"]:
            if link not in seen:
                queue.append(link)
        if "CC BY" not in art["license"]:
            log.debug("cyberleninka: skip non-CC-BY %s (%s)", url, art["license"])
            continue
        text = art["text"]
        math_hits = len(MATH_SYMBOLS.findall(text))
        if math_hits > 3:
            log.debug("cyberleninka: skip math-heavy %s (%d hits)", url, math_hits)
            continue
        candidates.append(
            Candidate(
                text=text,
                source_url=url,
                source_name="CyberLeninka",
                genre="sci",
                title=art["title"],
                author="",
                date_published="",
                license="CC BY 4.0",
                license_proof=url,
                topic=art["specialty"],
                notes=f"math_symbols={math_hits}",
            )
        )
        abstract = _extract_abstract(text)
        if abstract:
            candidates.append(
                Candidate(
                    text=abstract,
                    source_url=url,
                    source_name="CyberLeninka",
                    genre="sci",
                    title=f"{art['title']} (аннотация)",
                    author="",
                    date_published="",
                    license="CC BY 4.0",
                    license_proof=url,
                    topic=art["specialty"],
                    notes=f"abstract; math_symbols={math_hits}",
                )
            )
        for target in (500, 800):
            for passage in _passages(text, target):
                candidates.append(
                    Candidate(
                        text=passage,
                        source_url=url,
                        source_name="CyberLeninka",
                        genre="sci",
                        title=f"{art['title']} (фрагмент)",
                        author="",
                        date_published="",
                        license="CC BY 4.0",
                        license_proof=url,
                        topic=art["specialty"],
                        notes=f"passage~{target}; math_symbols={math_hits}",
                    )
                )
        time.sleep(RATE_DELAY)
    log.info("cyberleninka: fetched %d pages, %d CC-BY candidates", fetched, len(candidates))
    return candidates
