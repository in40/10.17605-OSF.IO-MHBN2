"""Dialogue source: inkoziev/Conversations (CC BY 4.0 per dataset README).

Streamed directly from HuggingFace with early stop (the full file is 600MB+
and disk is tight); selected raw lines are cached for reproducibility.
"""
from __future__ import annotations

import gzip
import json
import logging
import re

from .. import config, http
from . import Candidate

CITE_RE = re.compile(r"§|\bs\.\s*\d|\d+\s*с\.|[IVX]+,")

log = logging.getLogger(__name__)

STREAM_URL = (
    "https://huggingface.co/datasets/inkoziev/Conversations/resolve/main/"
    "conversations.jsonl.gz"
)
SELECTED_CACHE = ".dialogues_selected.jsonl"
MAX_LINES = 320000
TARGET_MIN, TARGET_MAX = 300, 800


def _iter_stream_lines():
    # Cache-first: use the downloaded file if present, else fetch+cache it.
    path = http.cached_get_bytes(STREAM_URL, ".jsonl.gz")
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        yield from fh


def collect(max_candidates: int = 400) -> list[Candidate]:
    log.info("dialogues: streaming %s", STREAM_URL)
    candidates: list[Candidate] = []
    lines_read = 0
    gen = _iter_stream_lines()
    try:
        for i, line in enumerate(gen):
            lines_read = i + 1
            if i >= MAX_LINES or len(candidates) >= max_candidates:
                break
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            conv = (obj.get("conversation") or "").strip()
            if not conv:
                continue
            wc = len(conv.split())
            if CITE_RE.search(conv) or conv.count("—") < 6:
                continue
            if TARGET_MIN <= wc <= TARGET_MAX:
                candidates.append(
                    Candidate(
                        text=conv,
                        source_url="https://huggingface.co/datasets/inkoziev/Conversations",
                        source_name="inkoziev/Conversations (RLDD)",
                        genre="dia",
                        title="",
                        author="",
                        date_published="",
                        license=config.LICENSES["dia"],
                        license_proof="https://huggingface.co/datasets/inkoziev/Conversations/blob/main/README.md",
                        topic=obj.get("domain", ""),
                        notes=f"jsonl line {i}",
                    )
                )
    finally:
        gen.close()
    log.info("dialogues: %d candidates from %d lines", len(candidates), lines_read)
    return candidates
