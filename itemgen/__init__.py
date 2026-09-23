"""Item-generation pipeline for the pre-registered measurement model.

Implements the item-based dimensions from `02_math.md`:
  - Facts        -> QA-accuracy   (10 QA pairs; answered from the summary only)
  - Comprehension-> MCQ quiz      (8 items, 4 options, chance = 0.25)
  - Logic        -> NLI items     (entailment / neutral / contradiction)
  - Stance       -> stance items  (support / oppose / neutral)

Items are generated ONCE from the original text, frozen with a SHA-256
manifest, then reused to score every summary. The scorer answers each item
using ONLY the summary (never the source), so accuracy measures what the
summary preserved.
"""
from .config import ItemGenConfig
from .generator import generate_items
from .scorer import score_summary
from .manifest import build_manifest, hash_item

__all__ = [
    "ItemGenConfig",
    "generate_items",
    "score_summary",
    "build_manifest",
    "hash_item",
]
