"""Deterministic text filters: PII, self-containment, duplicates, length."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .config import (
    BUCKET_TARGETS,
    BUCKET_TOLERANCE,
    DUP_REJECT_THRESHOLD,
    DUP_WARN_THRESHOLD,
    GENRES,
    PII_PATTERNS,
    STOP_PHRASES,
)

TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def word_count(text: str) -> int:
    return len(text.split())


def find_pii(text: str) -> list[str]:
    hits: list[str] = []
    for kind, pat in PII_PATTERNS.items():
        for m in pat.finditer(text):
            hits.append(f"{kind}:{m.group(0)[:40]}")
    return hits


def find_stop_phrases(text: str) -> list[str]:
    return [m.group(0) for pat in STOP_PHRASES for m in pat.finditer(text)]


def trigrams(text: str) -> set[tuple[str, str, str]]:
    toks = TOKEN_RE.findall(text.lower())
    return {(toks[i], toks[i + 1], toks[i + 2]) for i in range(len(toks) - 2)}


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def length_ok(wordcount: int, genre: str) -> bool:
    g = GENRES[genre]
    return g["min"] <= wordcount <= g["max"]


def bucket_for(wordcount: int) -> int:
    return min(BUCKET_TARGETS, key=lambda t: abs(t - wordcount))


def in_bucket_target(wordcount: int, bucket: int) -> bool:
    lo = bucket * (1 - BUCKET_TOLERANCE)
    hi = bucket * (1 + BUCKET_TOLERANCE)
    return lo <= wordcount <= hi


@dataclass
class FilterResult:
    ok: bool
    reasons: list[str] = field(default_factory=list)
    pii: list[str] = field(default_factory=list)
    stop_phrases: list[str] = field(default_factory=list)
    wordcount: int = 0


def check_text(text: str, genre: str) -> FilterResult:
    wc = word_count(text)
    res = FilterResult(ok=True, wordcount=wc)
    res.pii = find_pii(text)
    if res.pii:
        res.ok = False
        res.reasons.append(f"PII found: {res.pii[:3]}")
    res.stop_phrases = find_stop_phrases(text)
    if res.stop_phrases:
        res.ok = False
        res.reasons.append(f"stop phrases: {res.stop_phrases[:3]}")
    if not length_ok(wc, genre):
        res.ok = False
        res.reasons.append(f"length {wc} outside {GENRES[genre]['min']}-{GENRES[genre]['max']}")
    return res


def check_duplicate(text: str, existing: dict[str, set]) -> tuple[bool, list[str]]:
    """Return (ok, messages). Reject if any overlap >= 0.95; warn above 0.50."""
    tg = trigrams(text)
    msgs: list[str] = []
    ok = True
    for other_id, other_tg in existing.items():
        ov = jaccard(tg, other_tg)
        if ov >= DUP_REJECT_THRESHOLD:
            ok = False
            msgs.append(f"near-duplicate of {other_id}: {ov:.2%}")
        elif ov > DUP_WARN_THRESHOLD:
            msgs.append(f"WARN overlap with {other_id}: {ov:.2%}")
    return ok, msgs
