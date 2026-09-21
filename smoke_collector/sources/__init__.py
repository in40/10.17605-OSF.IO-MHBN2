"""Source modules: each exposes collect() -> list[Candidate]."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Candidate:
    text: str
    source_url: str
    source_name: str
    genre: str
    title: str = ""
    author: str = ""
    date_published: str = ""
    license: str = ""
    license_proof: str = ""
    topic: str = ""
    notes: str = ""
    extra: dict = field(default_factory=dict)
