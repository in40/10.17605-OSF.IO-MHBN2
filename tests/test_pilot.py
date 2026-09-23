from pilot.sampler import genre_rng, sample_genre, sample_pools
from pilot.splits import disjoint_split


class Item:
    def __init__(self, text, source_name):
        self.text = text
        self.source_name = source_name


def _pool(genre, n, sources=("A", "B")):
    return [Item(f"{genre}-{i}", sources[i % len(sources)]) for i in range(n)]


def test_reproducible_same_seed():
    pool = _pool("news", 20)
    a = sample_genre(pool, 5, 42, "news")
    b = sample_genre(pool, 5, 42, "news")
    assert [x.text for x in a] == [x.text for x in b]


def test_different_seed_different_result():
    pool = _pool("news", 20)
    a = sample_genre(pool, 5, 42, "news")
    b = sample_genre(pool, 5, 99, "news")
    assert [x.text for x in a] != [x.text for x in b]


def test_seed_stream_separation_genres():
    # changing sci pool size must NOT change news selection
    news_pool = _pool("news", 20)
    sci_pool_small = _pool("sci", 15)
    sci_pool_big = _pool("sci", 50)
    sel1 = sample_pools({"news": news_pool, "sci": sci_pool_small}, {"news": 5, "sci": 5}, 42)
    sel2 = sample_pools({"news": news_pool, "sci": sci_pool_big}, {"news": 5, "sci": 5}, 42)
    assert [x.text for x in sel1["news"]] == [x.text for x in sel2["news"]]


def test_seed_stream_separation_splits():
    # pilot and validation draw from independent streams (different selections)
    pool = _pool("news", 30)
    r1 = sample_pools({"news": pool}, {"news": 5}, 42, stream="pilot")
    r2 = sample_pools({"news": pool}, {"news": 5}, 42, stream="validation")
    assert {x.text for x in r1["news"]} != {x.text for x in r2["news"]}


def test_source_balance():
    pool = _pool("ins", 20, sources=("A", "B", "C"))
    sel = sample_genre(pool, 6, 42, "ins", balance_by_source=True)
    srcs = [x.source_name for x in sel]
    # round-robin should spread across sources, not all one
    assert len(set(srcs)) >= 2


def test_n_exceeds_pool_returns_all():
    pool = _pool("fic", 3)
    sel = sample_genre(pool, 10, 42, "fic")
    assert len(sel) == 3


def test_disjoint_split_no_overlap():
    pools = {
        "news": _pool("news", 50),
        "sci": _pool("sci", 50),
        "ins": _pool("ins", 50),
        "fic": _pool("fic", 50),
        "dia": _pool("dia", 50),
    }
    res = disjoint_split(
        pools,
        pilot_targets={"news": 5, "sci": 5, "ins": 5, "fic": 5, "dia": 5},
        validation_targets={"news": 5, "sci": 5, "ins": 5},
        main_targets={"news": 5, "sci": 5, "ins": 5, "fic": 5, "dia": 5},
        base_seed=42,
    )
    pilot_keys = {i.text for items in res["pilot"].values() for i in items}
    val_keys = {i.text for items in res["validation"].values() for i in items}
    main_keys = {i.text for items in res["main"].values() for i in items}
    assert not (pilot_keys & val_keys)
    assert not (pilot_keys & main_keys)
    assert not (val_keys & main_keys)


def test_validation_confirmatory_only():
    pools = {
        "news": _pool("news", 30),
        "sci": _pool("sci", 30),
        "ins": _pool("ins", 30),
        "fic": _pool("fic", 30),
        "dia": _pool("dia", 30),
    }
    res = disjoint_split(
        pools,
        pilot_targets={"news": 2, "sci": 2, "ins": 2, "fic": 2, "dia": 2},
        validation_targets={"news": 3, "sci": 3, "ins": 3, "fic": 3, "dia": 3},
        main_targets={"news": 2, "sci": 2, "ins": 2, "fic": 2, "dia": 2},
        base_seed=42,
    )
    assert "fic" not in res["validation"]
    assert "dia" not in res["validation"]
    assert set(res["validation"]) == {"news", "sci", "ins"}
