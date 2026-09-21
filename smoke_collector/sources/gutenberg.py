"""Fiction source: public-domain Russian classics via ru.wikisource.org API.

Project Gutenberg was checked and lacks Russian-language originals (only
translations), so Wikisource is used as the equivalent PD source.
"""
from __future__ import annotations

import json
import logging
import re
from urllib.parse import quote

from .. import config, http
from . import Candidate

log = logging.getLogger(__name__)

API = "https://ru.wikisource.org/w/api.php"
WORKS = [
    "На святках (Чехов)",
    "Крыжовник (Чехов)",
    "Ионыч (Чехов)",
    "Студент (Чехов)",
    "Душечка (Чехов)",
]

TPL_RE = re.compile(r"\{\{[^{}]*\}\}", re.DOTALL)
REF_RE = re.compile(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", re.DOTALL)
TAG_RE = re.compile(r"</?(?:br|small|center|div|span|noinclude|includeonly)[^>]*>", re.IGNORECASE)
LINK_RE = re.compile(r"\[\[([^\]|]+)\|([^\]]+)\]\]|\[\[([^\]]+)\]\]")
HEADER_RE = re.compile(r"^(={2,6})\s*(.*?)\s*\1\s*$", re.MULTILINE)


def clean_wikitext(raw: str) -> str:
    t = REF_RE.sub("", raw)
    t = TPL_RE.sub("", t)
    t = TAG_RE.sub("\n", t)
    t = LINK_RE.sub(lambda m: m.group(2) or m.group(3) or "", t)
    t = HEADER_RE.sub("", t)
    t = t.replace("&nbsp;", " ").replace("&mdash;", "—").replace("&ndash;", "–")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _fetch_work(title: str) -> str | None:
    url = (
        f"{API}?action=query&prop=revisions&rvprop=content&rvslots=main"
        f"&format=json&utf8=1&titles={quote(title)}"
    )
    raw = http.cached_get_text(url, ".json")
    data = json.loads(raw)
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        revs = page.get("revisions")
        if revs:
            return revs[0]["slots"]["main"]["*"]
    return None


def _scenes(text: str) -> list[str]:
    """Group paragraphs into 300-800 word passages at paragraph boundaries."""
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    passages: list[str] = []
    cur: list[str] = []
    cur_wc = 0
    for p in paras:
        wc = len(p.split())
        if cur_wc + wc > 800 and cur_wc >= 300:
            passages.append("\n\n".join(cur))
            cur = []
            cur_wc = 0
        cur.append(p)
        cur_wc += wc
    if cur_wc >= 300:
        passages.append("\n\n".join(cur))
    return passages


def collect() -> list[Candidate]:
    log.info("fiction: fetching %d PD works from Wikisource", len(WORKS))
    candidates: list[Candidate] = []
    for work in WORKS:
        try:
            raw = _fetch_work(work)
        except Exception as exc:  # noqa: BLE001
            log.warning("fiction: fetch failed %s: %s", work, exc)
            continue
        if not raw:
            continue
        clean = clean_wikitext(raw)
        scenes = _scenes(clean)
        for i, scene in enumerate(scenes):
            wc = len(scene.split())
            if 300 <= wc <= 800:
                candidates.append(
                    Candidate(
                        text=scene,
                        source_url=f"https://ru.wikisource.org/wiki/{quote(work)}",
                        source_name="ru.wikisource.org",
                        genre="fic",
                        title=work,
                        author="А. П. Чехов",
                        date_published="",
                        license=config.LICENSES["fic"],
                        license_proof="https://ru.wikisource.org/wiki/Справка:Авторское_право",
                        topic="художественная литература",
                        notes=f"scene {i} of {len(scenes)}",
                    )
                )
    log.info("fiction: %d candidate scenes", len(candidates))
    return candidates
