"""Collect prompt templates from the pipeline modules for viewing/auditing.

Auto-discovers uppercase string constants so new prompts show up without
wiring. Each prompt is paired with its SHA-256 (useful for the freeze /
OSF manifest step).
"""
from __future__ import annotations

import hashlib


def prompt_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _module_prompts(mod) -> list[tuple[str, str]]:
    return [
        (n, v)
        for n, v in vars(mod).items()
        if n.isupper() and isinstance(v, str)
    ]


def collect_prompts() -> list[tuple[str, list[tuple[str, str]]]]:
    """Return [(group_label, [(name, text), ...]), ...]."""
    from smoke_judge import rubric as jr
    from smoke_summarizer import prompts as sp
    from itemgen import prompts as ip

    itemgen_all = _module_prompts(ip)
    return [
        ("Summarizer", _module_prompts(sp)),
        ("Judge (rubric)", _module_prompts(jr)),
        ("Itemgen — generate", [(n, v) for n, v in itemgen_all if n.endswith("_GEN")]),
        ("Itemgen — score", [(n, v) for n, v in itemgen_all if not n.endswith("_GEN")]),
    ]
