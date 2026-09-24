"""Runner: compression-ratio grid x n summaries, length-regen, hashing, save."""
from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .client import LLMClient
from .prompts import DEFAULT_BASE, DEFAULT_REGEN, render_base, render_regen

log = logging.getLogger(__name__)

DEFAULT_LEVELS = (0.9, 0.7, 0.5, 0.3, 0.2, 0.1, 0.05)


@dataclass
class SummConfig:
    type: str = "llm"  # llm | extractive | hybrid
    base_url: str = "https://chat.sorokinonline.com/v1"
    api_key: str = ""
    model: str = "qwen3.5-122b"
    system: str = ""
    levels: tuple[float, ...] = DEFAULT_LEVELS
    n_summaries: int = 1
    temperature: float = 0.3
    max_tokens: int = 4096
    top_p: float | None = None
    seed: int | None = 42
    tolerance: float = 0.20
    regen_attempts: int = 1
    hybrid_backend: str = "transformers"
    hybrid_model: str = "IlyaGusev/rut5_base_sum_gazeta"
    hybrid_offline: bool = True
    force: bool = False
    extractive_scale: float = 2.0
    texts_dir: str = "smoke/texts"
    out_dir: str = "smoke/summaries"
    prompt_base: str = DEFAULT_BASE
    prompt_regen: str = DEFAULT_REGEN
    extra: dict = field(default_factory=dict)

    @property
    def system_label(self) -> str:
        return self.system or self.model


def load_config(path: str | None) -> SummConfig:
    cfg = SummConfig()
    if path:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for k, v in data.items():
            if k == "levels":
                cfg.levels = tuple(v)
            elif hasattr(cfg, k):
                setattr(cfg, k, v)
    return cfg


def target_words(source_wc: int, r: float) -> int:
    return max(1, round(r * source_wc))


def length_ok(actual: int, target: int, tol: float) -> bool:
    if target <= 0:
        return actual >= 0
    return abs(actual - target) / target <= tol


def word_count(text: str) -> int:
    return len(text.split())


def _hash(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def _level_tag(r: float) -> str:
    return f"r{str(r).replace('.', 'p')}"


def generate_one(
    client: LLMClient | None, cfg: SummConfig, text: str, target: int
) -> tuple[str, int, int, str, dict]:
    """Return (summary, attempts, regen_used, status, extra).

    `extra` carries type-specific diagnostics (e.g. oracle coverage/coherence/
    maximin); empty dict for other types.
    """
    if cfg.type == "extractive":
        from .extractive import summarize_extractive

        summary = summarize_extractive(text, target, cfg.tolerance)
        wc = word_count(summary)
        status = "ok" if length_ok(wc, target, cfg.tolerance) else "length_fail"
        return summary, 1, 0, status, {}

    if cfg.type == "oracle":
        from .extractive import split_sentences
        from .oracle import oracle_select

        sel = oracle_select(text, target, cfg.tolerance)
        sentences = split_sentences(text)
        summary = " ".join(sentences[i] for i in sel["indices"])
        wc = word_count(summary)
        status = "ok" if length_ok(wc, target, cfg.tolerance) else "length_fail"
        extra = {
            "coverage": sel["coverage"],
            "coherence": sel["coherence"],
            "maximin": sel["maximin"],
        }
        return summary, 1, 0, status, extra

    if cfg.type == "hybrid":
        from .hybrid import HybridSummarizer

        if not hasattr(cfg, "_hybrid"):
            cfg._hybrid = HybridSummarizer(
                model_name=cfg.hybrid_model,
                backend=getattr(cfg, "hybrid_backend", "transformers"),
                extractive_scale=getattr(cfg, "extractive_scale", 2.0),
                offline=getattr(cfg, "hybrid_offline", True),
            )
        summary = cfg._hybrid.summarize(text, target, cfg.tolerance)
        wc = word_count(summary)
        status = "ok" if length_ok(wc, target, cfg.tolerance) else "length_fail"
        return summary, 1, 0, status, {}

    prompt = render_base(cfg.prompt_base, target, text)
    attempts = 0
    regen_used = 0
    last_content = ""
    for attempt in range(1 + cfg.regen_attempts):
        attempts += 1
        res = client.chat(
            [{"role": "user", "content": prompt}],
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            top_p=cfg.top_p,
            seed=cfg.seed,
            extra=cfg.extra or None,
        )
        content = res.content
        if not content and res.reasoning:
            log.warning("empty content (reasoning-only, finish=%s)", res.finish_reason)
        last_content = content
        wc = word_count(content)
        if length_ok(wc, target, cfg.tolerance):
            return content, attempts, regen_used, "ok", {}
        if attempt < cfg.regen_attempts:
            regen_used += 1
            lo = int(target * (1 - cfg.tolerance))
            hi = int(target * (1 + cfg.tolerance))
            prompt = render_regen(cfg.prompt_regen, max(1, lo), hi, text)
            log.info("length miss (wc=%d target=%d) -> regen", wc, target)
    return last_content, attempts, regen_used, "length_fail", {}


def run(cfg: SummConfig, texts: dict[str, str]) -> list[dict]:
    client = (
        None
        if cfg.type in ("extractive", "hybrid", "oracle")
        else LLMClient(cfg.base_url, cfg.api_key, cfg.model)
    )
    out_root = Path(cfg.out_dir) / cfg.system_label
    records: list[dict] = []
    skipped = 0
    for text_id, text in sorted(texts.items()):
        src_wc = word_count(text)
        for r in cfg.levels:
            tgt = target_words(src_wc, r)
            for i in range(cfg.n_summaries):
                d = out_root / text_id / _level_tag(r)
                summary_file = d / f"summary_{i}.txt"
                if summary_file.exists() and not cfg.force:
                    skipped += 1
                    continue
                log.info("%s r=%.2f target=%d summary#%d", text_id, r, tgt, i)
                summary, attempts, regen_used, status, extra = generate_one(
                    client, cfg, text, tgt
                )
                rec = {
                    "text_id": text_id,
                    "system": cfg.system_label,
                    "model": cfg.model,
                    "level_r": r,
                    "target_words": tgt,
                    "actual_words": word_count(summary),
                    "status": status,
                    "attempts": attempts,
                    "regen_used": regen_used,
                    "temperature": cfg.temperature,
                    "max_tokens": cfg.max_tokens,
                    "top_p": cfg.top_p,
                    "seed": cfg.seed,
                    "source_wc": src_wc,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "content_hash": _hash(cfg.model, cfg.prompt_base, text, summary),
                }
                if extra:
                    rec["oracle"] = extra
                d.mkdir(parents=True, exist_ok=True)
                summary_file.write_text(summary, encoding="utf-8")
                (d / f"summary_{i}.json").write_text(
                    json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                records.append(rec)
    if skipped:
        log.info("resumed: skipped %d already-generated summaries (use --force to redo)", skipped)
    return records


def load_texts(texts_dir: str) -> dict[str, str]:
    d = Path(texts_dir)
    texts: dict[str, str] = {}
    for f in sorted(d.glob("*.txt")):
        texts[f.stem] = f.read_text(encoding="utf-8")
    return texts
