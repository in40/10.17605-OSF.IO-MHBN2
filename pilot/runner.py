"""Pilot orchestrator: assemble an acceptable corpus from the built bricks.

Flow:  sources -> filters -> disjoint_split -> save.
Reuses the smoke collection engine (sources/, filters.py, fetcher.py) and the
pilot sampler/splits. Produces disjoint pilot / validation / main sets.
"""
from __future__ import annotations

import importlib
import json
import logging
from datetime import date
from pathlib import Path

from smoke_collector.config import GENRES
from smoke_collector.filters import check_text

from . import config as pcfg
from .splits import disjoint_split

log = logging.getLogger(__name__)

SOURCE_MAP = {
    "news": "smoke_collector.sources.lenta",
    "sci": "smoke_collector.sources.cyberleninka",
    "ins": "smoke_collector.sources.procedural_pages",
    "fic": "smoke_collector.sources.gutenberg",
    "dia": "smoke_collector.sources.dialogues",
}

SPLIT_PREFIX = {"pilot": "PLT", "validation": "VAL", "main": "MRN"}
SPLIT_DIRS = {
    "pilot": pcfg.PILOT_TEXTS,
    "validation": pcfg.VALIDATION_TEXTS,
    "main": pcfg.MAIN_TEXTS,
}
SPLIT_TARGETS = {
    "pilot": pcfg.PILOT_TARGETS,
    "validation": pcfg.VALIDATION_TARGETS,
    "main": pcfg.MAIN_TARGETS,
}


def _load_source(genre: str, scale: int = 1) -> list:
    mod = importlib.import_module(SOURCE_MAP[genre])
    if genre == "news":
        return mod.collect(max_per_target=15 * scale)
    if genre == "fic":
        from smoke_collector.sources.gutenberg import EXTENDED_WORKS

        return mod.collect(works=EXTENDED_WORKS if scale > 1 else None)
    if genre == "ins":
        return mod.collect(
            url_list_file=str(pcfg.PILOT_PROCEDURAL_URLS) if scale > 1 else None,
            min_words=150,
            max_words=700,
            broad=True,
        )
    return mod.collect()


def load_pools(genres: list[str], scale: int = 1) -> dict[str, list]:
    pools: dict[str, list] = {}
    for g in genres:
        try:
            cands = _load_source(g, scale)
        except Exception as exc:  # noqa: BLE001
            log.error("pool load failed for %s: %s", g, exc)
            cands = []
        pools[g] = cands
        log.info("pool %s: %d raw candidates", g, len(cands))
    return pools


def filter_pools(pools: dict[str, list]) -> dict[str, list]:
    """Keep only candidates passing the genre's text filters."""
    filtered: dict[str, list] = {}
    for g, cands in pools.items():
        ok = [c for c in cands if check_text(c.text, g).ok]
        log.info("pool %s: %d -> %d after filters", g, len(cands), len(ok))
        filtered[g] = ok
    return filtered


def _save_item(cand, text_id: str, split: str) -> dict:
    out_dir = SPLIT_DIRS[split]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{text_id}.txt").write_text(cand.text, encoding="utf-8")
    meta = {
        "text_id": text_id,
        "split": split,
        "genre": cand.genre,
        "source_url": cand.source_url,
        "source_name": cand.source_name,
        "author": cand.author,
        "title": cand.title,
        "date_accessed": date.today().isoformat(),
        "date_published": cand.date_published,
        "license": cand.license,
        "license_proof": cand.license_proof,
        "wordcount": len(cand.text.split()),
        "language": "ru",
        "topic": cand.topic,
        "notes": cand.notes,
    }
    (out_dir / f"{text_id}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return meta


def save_split(selection: dict[str, list], split: str) -> list[dict]:
    records: list[dict] = []
    for genre, items in selection.items():
        code = GENRES[genre]["code"]
        for n, cand in enumerate(items, 1):
            text_id = f"{SPLIT_PREFIX[split]}-{code}-{n:02d}"
            records.append(_save_item(cand, text_id, split))
    log.info("saved %d %s texts -> %s", len(records), split, SPLIT_DIRS[split])
    return records


def coverage_report(selection: dict[str, list], targets: dict[str, int]) -> list[str]:
    lines: list[str] = []
    for genre, target in targets.items():
        got = len(selection.get(genre, []))
        status = "OK" if got >= target else f"UNDER-FILL ({got}/{target})"
        lines.append(f"  {genre}: {status}")
    return lines


def run(splits: list[str], base_seed: int | None = None, scale: int | None = None) -> dict:
    base_seed = base_seed if base_seed is not None else pcfg.BASE_SEED
    scale = scale if scale is not None else pcfg.POOL_SCALE
    genres = list(SOURCE_MAP)
    pools = filter_pools(load_pools(genres, scale))
    result = disjoint_split(
        pools,
        pcfg.PILOT_TARGETS,
        pcfg.VALIDATION_TARGETS,
        pcfg.MAIN_TARGETS,
        base_seed,
    )
    saved: dict = {}
    for split in splits:
        sel = result.get(split, {})
        print(f"\n=== {split} coverage ===")
        for line in coverage_report(sel, SPLIT_TARGETS[split]):
            print(line)
        saved[split] = save_split(sel, split)
    return saved
