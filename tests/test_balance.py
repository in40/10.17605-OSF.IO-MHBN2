import pytest

from smoke_collector.balance import Balancer
from smoke_collector.config import SLOTS


def test_slots_shape():
    assert len(SLOTS) == 10
    genres = [g for g, _ in SLOTS]
    assert genres.count("news") == 3
    assert genres.count("sci") == 3
    assert genres.count("ins") == 2
    assert genres.count("fic") == 1
    assert genres.count("dia") == 1
    buckets = [b for _, b in SLOTS]
    assert buckets.count(150) == 1
    assert buckets.count(300) == 2
    assert buckets.count(500) == 4
    assert buckets.count(800) == 3


def test_assign_fills_slot():
    b = Balancer()
    s = b.try_assign("news", 300, "SMK-NEWS-01")
    assert s is not None
    assert s.filled_by == "SMK-NEWS-01"
    assert not b.free_slots("news", 300)


def test_capacity_enforced():
    b = Balancer()
    assert b.try_assign("sci", 500, "A")
    assert b.try_assign("sci", 500, "B") is None


def test_wrong_bucket_rejected():
    b = Balancer()
    assert b.try_assign("fic", 150, "X") is None


def test_all_filled():
    b = Balancer()
    for i, (g, bk) in enumerate(SLOTS):
        assert b.try_assign(g, bk, f"ID{i}")
    assert b.all_filled()
    assert b.missing() == []


def test_missing_reports():
    b = Balancer()
    assert len(b.missing()) == 10
    b.try_assign("dia", 800, "D")
    assert ("dia", 800) not in b.missing()
