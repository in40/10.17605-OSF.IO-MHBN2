"""Export a web-UI task sheet from a texts dir + r-grid."""
from __future__ import annotations

import logging
from pathlib import Path

from smoke_summarizer.prompts import DEFAULT_BASE, render_base
from smoke_summarizer.runner import DEFAULT_LEVELS, _level_tag, load_texts, target_words

from .sheet import format_task, render_header

log = logging.getLogger(__name__)


def build_sheet(system: str, texts_dir: str, levels=DEFAULT_LEVELS, template: str = DEFAULT_BASE) -> str:
    texts = load_texts(texts_dir)
    out = [render_header(system)]
    n = 0
    for tid in sorted(texts):
        text = texts[tid]
        wc = len(text.split())
        for r in levels:
            target = target_words(wc, r)
            prompt = render_base(template, target, text)
            out.append(format_task(tid, _level_tag(r), target, prompt))
            n += 1
    log.info("built %d tasks for system=%s", n, system)
    return "\n".join(out) + "\n"


def export_sheet(system: str, texts_dir: str, out_file: str, levels=DEFAULT_LEVELS, template: str = DEFAULT_BASE) -> int:
    sheet = build_sheet(system, texts_dir, levels=levels, template=template)
    p = Path(out_file)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(sheet, encoding="utf-8")
    log.info("wrote task sheet -> %s", p)
    return len(parse_count(sheet))


def parse_count(sheet: str) -> list[str]:
    from .sheet import parse_sheet

    return [t["text_id"] for t in parse_sheet(sheet)]
