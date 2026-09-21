"""Configuration: genre specs, length buckets, PII patterns, stop phrases, paths."""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "smoke" / "texts"
SMOKE_TEST_MD = REPO_ROOT / "SMOKE_TEST.md"
CACHE_DIR = Path.home() / ".cache" / "smoke_collector"
LOG_FILE = REPO_ROOT / "smoke_collector.log"

HTTP_TIMEOUT = 30
HTTP_RETRIES = 3

GENRES = {
    "news": {"code": "NEWS", "min": 300, "max": 800},
    "sci": {"code": "SCI", "min": 150, "max": 800},
    "ins": {"code": "INS", "min": 200, "max": 600},
    "fic": {"code": "FIC", "min": 300, "max": 800},
    "dia": {"code": "DIA", "min": 300, "max": 800},
}

BUCKET_TARGETS = (150, 300, 500, 800)
BUCKET_CAPACITY = {150: 1, 300: 2, 500: 4, 800: 3}
BUCKET_TOLERANCE = 0.10

# Required (genre, bucket) slots per SMOKE_TEXTS_SPEC.md length table.
SLOTS: tuple[tuple[str, int], ...] = (
    ("sci", 150),
    ("news", 300),
    ("ins", 300),
    ("news", 500),
    ("sci", 500),
    ("ins", 500),
    ("fic", 500),
    ("news", 800),
    ("sci", 800),
    ("dia", 800),
)

DUP_REJECT_THRESHOLD = 0.95
DUP_WARN_THRESHOLD = 0.50

PII_PATTERNS: dict[str, re.Pattern] = {
    "phone": re.compile(r"(?<!\d)(?:\+7|8)[\s(]?\d{3}[\s)]?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}(?!\d)"),
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "inn": re.compile(r"(?<!\d)\d{10}(?!\d)|(?<!\d)\d{12}(?!\d)"),
    "snils": re.compile(r"(?<!\d)\d{3}-\d{3}-\d{3}\s\d{2}(?!\d)"),
    "passport": re.compile(r"(?<!\d)\d{2}\s\d{2}\s\d{6}(?!\d)"),
    "address": re.compile(
        r"(?:ул\.|просп\.|пр\.|пер\.|ш\.|б-р|бульвар)\s*[^\s,.]{2,30}[,.]?\s*(?:д\.|дом)\s*\d+"
        r"|кв\.\s*\d+"
    ),
}

STOP_PHRASES: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"продолжение\s+следует",
        r"продолжение\s+в\s+следующей\s+главе",
        r"как\s+упоминалось\s+выше",
        r"как\s+было\s+сказано\s+ранее",
        r"см\.\s*выше",
        r"см\.\s*ниже",
        r"окончание\s+следует",
        r"читайте\s+в\s+следующем\s+номере",
    )
]

LICENSES = {
    "news": "CC BY-NC 4.0 (Lenta.Ru-News-Dataset v1.1); Lenta.ru RSS export: https://lenta.ru/info/posts/export/",
    "sci": "CC BY 4.0 (per-item, verified on CyberLeninka article page)",
    "ins": "Public government reference material (free citation); access date recorded",
    "fic": "Public domain (Project Gutenberg)",
    "dia": "CC BY 4.0 (inkoziev/Conversations, per dataset README)",
}
