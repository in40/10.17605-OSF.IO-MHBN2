"""Pilot configuration: sizes, genre allocation, seed, output dirs.

Sizes per SMOKE_TEST.md / 04_sampling.md §4.1:
  pilot 45-60 (all genres) | validation 100 (3 confirmatory) | main 400.
Per-genre pilot allocation is a configurable default (~10/genre = 50).
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PILOT_DIR = REPO_ROOT / "pilot_data"
PILOT_TEXTS = PILOT_DIR / "texts"
VALIDATION_TEXTS = PILOT_DIR / "validation"
MAIN_TEXTS = PILOT_DIR / "main"

BASE_SEED = 42

# Pilot/main-scale instruction URL list (superset of smoke's default).
PILOT_PROCEDURAL_URLS = (
    REPO_ROOT / "smoke_collector" / "data" / "procedural_urls_pilot.txt"
)

# Pool scale: multiply smoke caps to give sampling headroom.
POOL_SCALE = 10

CONFIRMATORY_GENRES = ("news", "sci", "ins")

# Pilot: ~50 texts across all 5 genres (within the 45-60 band).
PILOT_TARGETS: dict[str, int] = {
    "news": 10,
    "sci": 10,
    "ins": 10,
    "fic": 10,
    "dia": 10,
}

# Validation: 100 texts, 3 confirmatory genres only (~33/33/34).
VALIDATION_TARGETS: dict[str, int] = {
    "news": 33,
    "sci": 33,
    "ins": 34,
}

# Main confirmatory corpus: 400 total; H2 subset = 240 (news/sci/ins).
MAIN_TARGETS: dict[str, int] = {
    "news": 80,
    "sci": 80,
    "ins": 80,
    "fic": 80,
    "dia": 80,
}
