"""Disjoint splits: pilot / validation / main drawn from the same pools
without overlap. Validation uses confirmatory genres only.

Order: pilot first, then validation from the remainder, then main from the
remainder. Each split uses its own seed-stream so draws are independent
and reproducible.
"""
from __future__ import annotations

import hashlib
from typing import Callable

from .config import CONFIRMATORY_GENRES
from .sampler import sample_pools


def _default_key(item) -> str:
    text = getattr(item, "text", None)
    if text:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    return getattr(item, "source_url", None) or str(item)


def _remove(pool: list, keys: set, key_fn: Callable) -> list:
    return [i for i in pool if key_fn(i) not in keys]


def disjoint_split(
    pools: dict[str, list],
    pilot_targets: dict[str, int],
    validation_targets: dict[str, int],
    main_targets: dict[str, int],
    base_seed: int,
    balance_by_source: bool = True,
    source_key: Callable | None = None,
    key_fn: Callable | None = None,
) -> dict[str, dict[str, list]]:
    """Return {'pilot': {...}, 'validation': {...}, 'main': {...}} — all disjoint."""
    key_fn = key_fn or _default_key
    remaining: dict[str, list] = {g: list(p) for g, p in pools.items()}

    pilot = sample_pools(
        remaining, pilot_targets, base_seed, balance_by_source, source_key, stream="pilot"
    )
    pilot_keys = {key_fn(i) for items in pilot.values() for i in items}
    for g in remaining:
        remaining[g] = _remove(remaining[g], pilot_keys, key_fn)

    val_targets = {
        g: n for g, n in validation_targets.items() if g in CONFIRMATORY_GENRES
    }
    validation = sample_pools(
        remaining, val_targets, base_seed, balance_by_source, source_key, stream="validation"
    )
    val_keys = {key_fn(i) for items in validation.values() for i in items}
    for g in remaining:
        remaining[g] = _remove(remaining[g], val_keys, key_fn)

    main = sample_pools(
        remaining, main_targets, base_seed, balance_by_source, source_key, stream="main"
    )

    return {"pilot": pilot, "validation": validation, "main": main}
