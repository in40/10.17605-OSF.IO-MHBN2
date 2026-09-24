"""Lexical extractive-maximin oracle (exploratory upper bound).

For a text + target word count, greedily selects sentences to maximize
``min(coverage, coherence)`` — a no-model upper bound on extractive quality.

- Faithfulness / fluency are ~1 by construction (verbatim extraction), so the
  binding dimensions are coverage and coherence.
- Coverage = share of the source's frequency-weighted content terms covered.
- Coherence = mean lexical similarity between consecutive selected sentences.

Per the pre-reg this is EXPLORATORY ONLY — excluded from all primary estimators.
"""
from __future__ import annotations

from collections import Counter

from .extractive import _similarity, _tokens, split_sentences


def _source_weights(sentences: list[str]) -> Counter:
    c: Counter = Counter()
    for s in sentences:
        c.update(_tokens(s))
    return c


def _coverage(trial_tokens: set[str], source_weights: Counter) -> float:
    total = sum(source_weights.values())
    if total == 0:
        return 1.0
    return sum(source_weights[t] for t in trial_tokens) / total


def _coherence(sel_sentences: list[str]) -> float:
    if len(sel_sentences) < 2:
        return 1.0
    toks = [_tokens(s) for s in sel_sentences]
    sims = [_similarity(toks[i], toks[i + 1]) for i in range(len(toks) - 1)]
    return sum(sims) / len(sims) if sims else 1.0


def _score(sel: list[int], sentences: list[str], source_weights: Counter) -> tuple[float, float, float]:
    trial_tokens: set[str] = set()
    for i in sel:
        trial_tokens |= _tokens(sentences[i])
    cov = _coverage(trial_tokens, source_weights)
    coh = _coherence([sentences[i] for i in sel])
    return min(cov, coh), cov, coh


def oracle_select(text: str, target_words: int, tolerance: float = 0.20) -> dict:
    """Greedy maximin selection. Returns indices + scores for diagnostics."""
    sentences = split_sentences(text)
    if not sentences:
        return {"indices": [], "coverage": 0.0, "coherence": 0.0, "maximin": 0.0, "wordcount": 0}
    sizes = [len(s.split()) for s in sentences]
    source_weights = _source_weights(sentences)
    hi = max(1, int(target_words * (1 + tolerance)))

    selected: list[int] = []
    total = 0
    remaining = set(range(len(sentences)))
    while remaining:
        best_idx = None
        best_key = None  # (maximin, coverage)
        for c in remaining:
            if total + sizes[c] > hi:
                continue
            trial = sorted(selected + [c])
            maximin, cov, _ = _score(trial, sentences, source_weights)
            key = (maximin, cov)
            if best_key is None or key > best_key:
                best_key = key
                best_idx = c
        if best_idx is None:
            break
        selected.append(best_idx)
        total += sizes[best_idx]
        remaining.discard(best_idx)
        if total >= target_words:
            break

    if not selected:
        fitting = [i for i in range(len(sentences)) if sizes[i] <= hi]
        selected = [fitting[0] if fitting else 0]

    selected.sort()
    maximin, cov, coh = _score(selected, sentences, source_weights)
    return {
        "indices": selected,
        "coverage": round(cov, 4),
        "coherence": round(coh, 4),
        "maximin": round(maximin, 4),
        "wordcount": sum(sizes[i] for i in selected),
    }


def oracle_extractive(text: str, target_words: int, tolerance: float = 0.20) -> str:
    sel = oracle_select(text, target_words, tolerance)
    sentences = split_sentences(text)
    return " ".join(sentences[i] for i in sel["indices"])
