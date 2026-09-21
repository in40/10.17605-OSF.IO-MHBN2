"""News source: Lenta.Ru-News-Dataset v1.1 CSV dump (GitHub release).

License: dataset CC BY-NC 4.0; Lenta.ru RSS export page recorded as proof.
"""
from __future__ import annotations

import bz2
import csv
import io
import logging
import re

from .. import config, http
from . import Candidate

log = logging.getLogger(__name__)

DUMP_URL = (
    "https://github.com/yutkin/Lenta.Ru-News-Dataset/releases/download/"
    "v1.1/lenta-ru-news.csv.bz2"
)
DUMP_SUFFIX = ".csv.bz2"

EXCLUDE_TOPICS = {"Интервью", "Мнения", "Колумнисты", "Город+", "Реки"}
INTERVIEW_RE = re.compile(r"интервью|мнение|колумнист|беседа", re.IGNORECASE)

TARGETS = (300, 500, 800)
TOL = 0.10


def _rows():
    path = http.cached_get_bytes(DUMP_URL, DUMP_SUFFIX)
    with bz2.open(path, "rt", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            yield row


def collect(max_per_target: int = 15) -> list[Candidate]:
    log.info("lenta: loading dump %s", DUMP_URL)
    buckets: dict[int, list[Candidate]] = {t: [] for t in TARGETS}
    scanned = 0
    for row in _rows():
        scanned += 1
        topic = (row.get("topic") or "").strip()
        title = (row.get("title") or "").strip()
        tags = (row.get("tags") or "").strip()
        text = (row.get("text") or "").strip()
        if topic in EXCLUDE_TOPICS or INTERVIEW_RE.search(title) or INTERVIEW_RE.search(tags):
            continue
        wc = len(text.split())
        for t in TARGETS:
            if len(buckets[t]) >= max_per_target:
                continue
            if t * (1 - TOL) <= wc <= t * (1 + TOL):
                buckets[t].append(
                    Candidate(
                        text=text,
                        source_url=(row.get("url") or "").strip(),
                        source_name="Lenta.ru (dump v1.1)",
                        genre="news",
                        title=title,
                        author="",
                        date_published=(row.get("date") or "").strip(),
                        license=config.LICENSES["news"],
                        license_proof="https://lenta.ru/info/posts/export/",
                        topic=topic,
                        notes=f"dump row id={row.get('id')}",
                    )
                )
                break
        if all(len(buckets[t]) >= max_per_target for t in TARGETS):
            break
    log.info("lenta: scanned %d rows, buckets: %s", scanned, {t: len(v) for t, v in buckets.items()})
    out: list[Candidate] = []
    for t in TARGETS:
        out.extend(buckets[t])
    return out
