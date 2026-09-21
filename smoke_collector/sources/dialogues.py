"""Dialogue source: inkoziev/Conversations (CC BY 4.0 per dataset README).

Streamed directly from HuggingFace with early stop (the full file is 600MB+
and disk is tight); selected raw lines are cached for reproducibility.
"""
from __future__ import annotations

import gzip
import json
import logging

import requests

from .. import config, http
from . import Candidate

log = logging.getLogger(__name__)

STREAM_URL = (
    "https://huggingface.co/datasets/inkoziev/Conversations/resolve/main/"
    "conversations.jsonl.gz"
)
SELECTED_CACHE = ".dialogues_selected.jsonl"
MAX_LINES = 40000
TARGET_MIN, TARGET_MAX = 300, 800


def _iter_stream_lines():
    resp = requests.get(STREAM_URL, headers={"User-Agent": http.UA}, stream=True, timeout=120)
    resp.raise_for_status()
    with gzip.open(resp.raw, "rt", encoding="utf-8", errors="replace") as fh:
        yield from fh


def collect(max_candidates: int = 25) -> list[Candidate]:
    log.info("dialogues: streaming %s", STREAM_URL)
    candidates: list[Candidate] = []
    lines_read = 0
    for i, line in enumerate(_iter_stream_lines()):
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
    log.info("dialogues: %d candidates from %d lines", len(candidates), lines_read)
    return candidates
