"""Seeded stratified sampler with per-genre seed-stream separation.

Seed-stream separation: each genre draws from an RNG derived from
(base_seed, genre), so changing one genre's pool size does NOT shift
another genre's selection. Reproducible across runs.

Optional source balancing: within a genre, round-robin across sources so
the sample isn't dominated by one source.
"""
from __future__ import annotations

import hashlib
import random
from typing import Callable


def genre_rng(base_seed: int, genre: str, stream: str = "") -> random.Random:
    """Independent RNG per (genre, stream), derived from base_seed.

    The `stream` dimension lets pilot/validation/main draw from separate
    streams so one split's sampling never shifts another's.
    """
    digest = hashlib.sha256(f"{base_seed}:{genre}:{stream}".encode("utf-8")).hexdigest()
    return random.Random(int(digest[:16], 16))


def _source_of(item, source_key: Callable | None) -> str:
    if source_key is not None:
        return source_key(item)
    return getattr(item, "source_name", None) or getattr(item, "source", "") or ""


def _balanced_sample(pool: list, n: int, rng: random.Random, source_key: Callable | None) -> list:
    """Round-robin across sources (each source's items shuffled), then take n."""
    by_source: dict[str, list] = {}
    for item in pool:
        by_source.setdefault(_source_of(item, source_key), []).append(item)
    for items in by_source.values():
        rng.shuffle(items)
    # interleave sources round-robin
    sources = sorted(by_source)  # stable order
    result: list = []
    idx = 0
    while len(result) < n:
        added = False
        for s in sources:
            items = by_source[s]
            if idx < len(items):
                result.append(items[idx])
                added = True
                if len(result) >= n:
                    break
        if not added:
            break
        idx += 1
    return result[:n]


def sample_genre(
    pool: list,
    n: int,
    base_seed: int,
    genre: str,
    balance_by_source: bool = True,
    source_key: Callable | None = None,
    stream: str = "",
) -> list:
    """Sample n items from a genre pool, reproducibly."""
    rng = genre_rng(base_seed, genre, stream)
    if n >= len(pool):
        return list(pool)
    if balance_by_source:
        return _balanced_sample(pool, n, rng, source_key)
    return rng.sample(pool, n)


def sample_pools(
    pools: dict[str, list],
    targets: dict[str, int],
    base_seed: int,
    balance_by_source: bool = True,
    source_key: Callable | None = None,
    stream: str = "",
) -> dict[str, list]:
    """Sample each genre independently (seed-stream separation)."""
    selected: dict[str, list] = {}
    for genre, n in targets.items():
        pool = pools.get(genre, [])
        selected[genre] = sample_genre(
            pool, n, base_seed, genre, balance_by_source, source_key, stream
        )
    return selected
