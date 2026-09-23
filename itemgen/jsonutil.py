"""Robust JSON extraction from LLM output (handles fences, prose, reasoning)."""
from __future__ import annotations

import json
import re

_ARR_RE = re.compile(r"\[.*\]", re.DOTALL)
_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)
_FENCE_RE = re.compile(r"```(?:json|python)?", re.IGNORECASE)


def _loads(s: str):
    try:
        return json.loads(s)
    except (json.JSONDecodeError, ValueError):
        return None


def extract_json(text: str):
    """Return the first JSON array or object found in text, else None."""
    if not text:
        return None
    cleaned = _FENCE_RE.sub("", text)
    m = _ARR_RE.search(cleaned)
    if m:
        val = _loads(m.group(0))
        if val is not None:
            return val
    m = _OBJ_RE.search(cleaned)
    if m:
        val = _loads(m.group(0))
        if val is not None:
            return val
    return None


def extract_array(text: str) -> list:
    val = extract_json(text)
    return val if isinstance(val, list) else []


def extract_object(text: str) -> dict:
    val = extract_json(text)
    return val if isinstance(val, dict) else {}
