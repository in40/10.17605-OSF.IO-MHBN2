"""Hybrid summarizer: TextRank extractive grounding -> rut5 abstractive rewrite.

Stage 1: TextRank (extractive.py) selects the most salient sentences, giving a
grounded subset (reduces hallucination vs free abstractive).
Stage 2: a RU seq2seq model (IlyaGusev/rut5_base_sum_gazeta, Apache-2.0)
rewrites the grounded subset abstractively.

Backends: "transformers" (default, matches model card) or "ctranslate2"
(CPU-optimized; requires a converted model dir).
"""
from __future__ import annotations

import logging
import re

from .extractive import RU_STOPWORDS, split_sentences, summarize_extractive, textrank

log = logging.getLogger(__name__)

DEFAULT_MODEL = "IlyaGusev/rut5_base_sum_gazeta"
_WORD_RE = re.compile(r"[а-яёa-z]{3,}", re.IGNORECASE)


def _content_tokens(text: str) -> set[str]:
    toks = {w.lower() for w in _WORD_RE.findall(text)}
    return {t for t in toks if t not in RU_STOPWORDS}


def _overlap(sentence: str, core_tokens: set[str]) -> float:
    st = _content_tokens(sentence)
    if not st:
        return 1.0
    return len(st & core_tokens) / len(st)


class HybridSummarizer:
    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        backend: str = "transformers",
        device: str = "cpu",
        extractive_scale: float = 2.0,
        no_repeat_ngram_size: int = 4,
        max_input_tokens: int = 600,
        max_new_tokens: int = 256,
    ) -> None:
        self.model_name = model_name
        self.backend = backend
        self.device = device
        self.extractive_scale = extractive_scale
        self.no_repeat_ngram_size = no_repeat_ngram_size
        self.max_input_tokens = max_input_tokens
        self.max_new_tokens = max_new_tokens
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        if self.backend == "ctranslate2":
            self._load_ct2()
        else:
            self._load_transformers()
        self._loaded = True

    def _load_transformers(self) -> None:
        import torch
        from transformers import AutoTokenizer, T5ForConditionalGeneration

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()
        self._torch = torch

    def _load_ct2(self) -> None:
        import ctranslate2
        import sentencepiece as spm

        self.translator = ctranslate2.Translator(self.model_name, device=self.device)
        self.sp = spm.SentencePieceProcessor()
        self.sp.load(f"{self.model_name}/sentencepiece.model")

    def _generate(self, text: str) -> str:
        if self.backend == "ctranslate2":
            toks = self.sp.encode(text, out_type=str)
            out = self.translator.translate([toks], max_batching_tokens=self.max_new_tokens)
            return self.sp.decode(out[0][0])
        enc = self.tokenizer(
            [text],
            max_length=self.max_input_tokens,
            add_special_tokens=True,
            padding="longest",
            truncation=True,
            return_tensors="pt",
        ).to(self.device)
        with self._torch.no_grad():
            out_ids = self.model.generate(
                **enc,
                no_repeat_ngram_size=self.no_repeat_ngram_size,
                max_new_tokens=self.max_new_tokens,
                max_length=None,
            )
        return self.tokenizer.decode(out_ids[0], skip_special_tokens=True).strip()

    def summarize(self, text: str, target_words: int, tolerance: float = 0.20) -> str:
        self._load()
        # 1. Abstractive core: rut5 rewrites a TextRank-grounded subset.
        grounding_words = max(target_words, int(target_words * self.extractive_scale))
        grounded = summarize_extractive(text, grounding_words, tolerance=0.5)
        core = self._generate(grounded) if grounded else ""
        core_wc = len(core.split())

        if core_wc >= target_words:
            return core

        # 2. Fill to target with TextRank-selected sentences not covered by the core.
        remaining = target_words - core_wc
        sentences = split_sentences(text)
        scores = textrank(sentences)
        core_tokens = _content_tokens(core)
        ranked = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)
        fill: list[tuple[int, str]] = []
        fill_wc = 0
        for idx in ranked:
            if fill_wc >= remaining:
                break
            sent = sentences[idx]
            if _overlap(sent, core_tokens) > 0.6:
                continue
            fill.append((idx, sent))
            fill_wc += len(sent.split())
        fill.sort(key=lambda x: x[0])
        parts = [core] + [s for _, s in fill]
        return " ".join(p for p in parts if p).strip()
