"""Extractive summarizer: TextRank over Russian sentences.

Deterministic, no LLM. Splits into sentences, builds a similarity graph,
runs PageRank, selects top sentences until the r-target word count.
"""
from __future__ import annotations

import math
import re

RU_STOPWORDS = frozenset(
    """и в во не что он на я с со как а то все она так его да ты к у же вы бы
    было о но если у него её неё меня мне него неё ней ним нами вами ними этот
    эта эти мой моя моё наш наша ваш ваша был были есть будет будут они их
   himself herself тут там где когда для от до при о об во без под над
    уже ещё очень просто тоже даже только чтобы что-то кто чем тем тем
    более менее такой такая такое какие какой между после перед через
    about into over под над про данный которая который которые""".split()
)

SENT_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+")
WORD_RE = re.compile(r"[а-яёa-z]{3,}", re.IGNORECASE)


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    parts = SENT_SPLIT_RE.split(text)
    return [p.strip() for p in parts if len(p.strip()) > 1]


def _tokens(sentence: str) -> set[str]:
    toks = {w.lower() for w in WORD_RE.findall(sentence)}
    return {t for t in toks if t not in RU_STOPWORDS}


def _similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    denom = math.log(len(a) + 1) + math.log(len(b) + 1)
    return inter / denom if denom else 0.0


def textrank(sentences: list[str], damping: float = 0.85, iterations: int = 30) -> list[float]:
    n = len(sentences)
    if n == 0:
        return []
    if n == 1:
        return [1.0]
    tok = [_tokens(s) for s in sentences]
    sim = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            s = _similarity(tok[i], tok[j])
            sim[i][j] = s
            sim[j][i] = s
    scores = [1.0 / n] * n
    for _ in range(iterations):
        new = [0.0] * n
        for i in range(n):
            total = 0.0
            for j in range(n):
                if i == j:
                    continue
                out_sum = sum(sim[j][k] for k in range(n) if k != j)
                if out_sum > 0:
                    total += sim[j][i] / out_sum * scores[j]
            new[i] = (1 - damping) / n + damping * total
        scores = new
    return scores


def summarize_extractive(text: str, target_words: int, tolerance: float = 0.20) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return ""
    scores = textrank(sentences)
    ranked = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)
    sizes = {i: len(sentences[i].split()) for i in range(len(sentences))}
    hi = max(1, int(target_words * (1 + tolerance)))
    # Prefer sentences that can fit the target; fall back to the best overall.
    fitting = [i for i in ranked if sizes[i] <= hi]
    pool = fitting if fitting else ranked[:1]
    selected: list[int] = []
    total = 0
    for idx in pool:
        if total >= target_words:
            break
        if total + sizes[idx] > hi and total >= max(1, int(target_words * 0.6)):
            continue
        selected.append(idx)
        total += sizes[idx]
    if not selected:
        selected = [pool[0]]
    selected.sort()
    return " ".join(sentences[i] for i in selected)
