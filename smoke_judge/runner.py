"""Judge runner: score each saved summary on the 4 dimensions."""
from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from smoke_summarizer.client import LLMClient

from .rubric import DIMENSIONS, render_combined, render_per_dim

log = logging.getLogger(__name__)

JSON_RE = re.compile(r"\{.*?\}", re.DOTALL)


@dataclass
class JudgeConfig:
    base_url: str = "https://chat.sorokinonline.com/v1"
    api_key: str = ""
    model: str = "qwen3.5-122b"
    mode: str = "combined"  # combined | per_dimension
    temperature: float = 0.0
    top_p: float = 0.95
    max_tokens: int = 256
    seed: int | None = 42
    retries: int = 1
    no_think: bool = True
    summaries_dir: str = "smoke/summaries"
    texts_dir: str = "smoke/texts"
    extra: dict = field(default_factory=dict)


def parse_scores(text: str, mode: str) -> dict | None:
    """Extract dimension scores from judge JSON output."""
    m = JSON_RE.search(text)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    if mode == "combined":
        if all(d in obj for d in DIMENSIONS):
            try:
                return {d: float(obj[d]) for d in DIMENSIONS}
            except (TypeError, ValueError):
                return None
        return None
    if "score" in obj:
        try:
            return {"score": float(obj["score"])}
        except (TypeError, ValueError):
            return None
    return None


def _hash(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def judge_summary(
    client: LLMClient, cfg: JudgeConfig, source: str, summary: str
) -> tuple[dict | None, str, int]:
    """Return (scores, status, attempts)."""
    if cfg.mode == "combined":
        prompt = render_combined(source, summary)
        for attempt in range(1 + cfg.retries):
            res = client.chat(
                [{"role": "user", "content": prompt}],
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                top_p=cfg.top_p,
                seed=cfg.seed,
                extra=cfg.extra or None,
            )
            scores = parse_scores(res.content or res.reasoning, cfg.mode)
            if scores is not None:
                return scores, "ok", attempt + 1
            log.warning("parse fail (combined), attempt %d", attempt + 1)
        return None, "missing", 1 + cfg.retries
    scores: dict = {}
    for dim in DIMENSIONS:
        prompt = render_per_dim(source, summary, dim)
        got = None
        for attempt in range(1 + cfg.retries):
            res = client.chat(
                [{"role": "user", "content": prompt}],
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                top_p=cfg.top_p,
                seed=cfg.seed,
                extra=cfg.extra or None,
            )
            parsed = parse_scores(res.content or res.reasoning, "per_dimension")
            if parsed is not None:
                got = parsed["score"]
                break
            log.warning("parse fail dim=%s attempt %d", dim, attempt + 1)
        if got is None:
            return None, "missing", 1 + cfg.retries
        scores[dim] = got
    return scores, "ok", 1 + cfg.retries


def run(cfg: JudgeConfig) -> list[dict]:
    client = LLMClient(cfg.base_url, cfg.api_key, cfg.model)
    texts: dict[str, str] = {}
    for f in Path(cfg.texts_dir).glob("*.txt"):
        texts[f.stem] = f.read_text(encoding="utf-8")
    records: list[dict] = []
    summ_root = Path(cfg.summaries_dir)
    for sfile in sorted(summ_root.rglob("summary_*.txt")):
        jfile = sfile.with_suffix(".judge.json")
        if jfile.exists():
            continue
        summary = sfile.read_text(encoding="utf-8")
        text_id = sfile.parent.parent.name
        source = texts.get(text_id, "")
        if not source:
            log.warning("no source for %s", text_id)
            continue
        scores, status, attempts = judge_summary(client, cfg, source, summary)
        rec = {
            "text_id": text_id,
            "summary_path": str(sfile),
            "judge_model": cfg.model,
            "mode": cfg.mode,
            "scores": scores,
            "status": status,
            "attempts": attempts,
            "judged_at": datetime.now(timezone.utc).isoformat(),
            "hash": _hash(cfg.model, source, summary),
        }
        jfile.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        records.append(rec)
        log.info("judged %s -> %s", sfile.relative_to(summ_root), status)
    return records
