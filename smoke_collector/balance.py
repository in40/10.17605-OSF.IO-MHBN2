"""Bucket allocation: fixed (genre, bucket) slots per spec length table."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from .config import BUCKET_CAPACITY, SLOTS

log = logging.getLogger(__name__)


@dataclass
class Slot:
    genre: str
    bucket: int
    filled_by: str | None = None

    @property
    def free(self) -> bool:
        return self.filled_by is None


@dataclass
class Balancer:
    slots: list[Slot] = field(default_factory=lambda: [Slot(g, b) for g, b in SLOTS])

    def free_slots(self, genre: str, bucket: int) -> list[Slot]:
        return [s for s in self.slots if s.genre == genre and s.bucket == bucket and s.free]

    def try_assign(self, genre: str, bucket: int, text_id: str) -> Slot | None:
        for s in self.free_slots(genre, bucket):
            s.filled_by = text_id
            log.info("slot filled: %s ~%d -> %s", genre, bucket, text_id)
            return s
        log.info("no free slot for %s ~%d (capacity %d)", genre, bucket, BUCKET_CAPACITY[bucket])
        return None

    def status(self) -> dict[str, int]:
        return {
            f"{s.genre}~{s.bucket}": (1 if s.filled_by else 0) for s in self.slots
        }

    def all_filled(self) -> bool:
        return all(not s.free for s in self.slots)

    def missing(self) -> list[tuple[str, int]]:
        return [(s.genre, s.bucket) for s in self.slots if s.free]
