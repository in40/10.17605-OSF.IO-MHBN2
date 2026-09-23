from pilot import raters


def _r(rater, tid, sc):
    return {"rater": rater, "text_id": tid, "self_contained": sc, "note": ""}


def test_aggregate_accept_both_yes():
    agg = raters.aggregate([_r("a", "T1", True), _r("b", "T1", True)])
    assert agg["T1"]["status"] == "accept"


def test_aggregate_reject_both_no():
    agg = raters.aggregate([_r("a", "T1", False), _r("b", "T1", False)])
    assert agg["T1"]["status"] == "reject"


def test_aggregate_disagree_mixed():
    agg = raters.aggregate([_r("a", "T1", True), _r("b", "T1", False)])
    assert agg["T1"]["status"] == "disagree"


def test_aggregate_incomplete_one_rater():
    agg = raters.aggregate([_r("a", "T1", True)])
    assert agg["T1"]["status"] == "incomplete"


def test_summary_counts_and_rate():
    ratings = [
        _r("a", "T1", True), _r("b", "T1", True),   # accept
        _r("a", "T2", False), _r("b", "T2", False),  # reject
        _r("a", "T3", True), _r("b", "T3", False),   # disagree
        _r("a", "T4", True),                          # incomplete
    ]
    s = raters.summary(raters.aggregate(ratings))
    assert s["accept"] == 1
    assert s["reject"] == 1
    assert s["disagree"] == 1
    assert s["incomplete"] == 1
    assert s["disagreement_rate"] == round(1 / 3, 3)


def test_record_replaces_same_rater_same_text():
    ratings = [_r("a", "T1", True)]
    ratings = raters.record_rating(ratings, "a", "T1", False, "changed mind")
    assert len(ratings) == 1
    assert ratings[0]["self_contained"] is False
    assert ratings[0]["note"] == "changed mind"


def test_unrated_for_skips_done():
    texts = {"T1": "x", "T2": "y", "T3": "z"}
    ratings = [_r("a", "T1", True)]
    assert raters.unrated_for("a", texts, ratings) == ["T2", "T3"]
    assert raters.unrated_for("b", texts, ratings) == ["T1", "T2", "T3"]


def test_split_paths_per_split():
    from pilot import config as pcfg

    t_p, r_p = raters.split_paths("pilot")
    t_m, r_m = raters.split_paths("main")
    t_v, r_v = raters.split_paths("validation")
    assert t_p == pcfg.PILOT_TEXTS
    assert t_m == pcfg.MAIN_TEXTS
    assert t_v == pcfg.VALIDATION_TEXTS
    assert r_p == raters.RATINGS_PATH
    assert r_m != r_p and r_m.name == "ratings_main.json"
    assert r_v != r_p and r_v.name == "ratings_validation.json"


def test_split_paths_unknown_raises():
    import pytest

    with pytest.raises(ValueError):
        raters.split_paths("bogus")


def test_interactive_rate_records(monkeypatch, tmp_path):
    monkeypatch.setattr(raters, "RATINGS_PATH", tmp_path / "ratings.json")
    texts_dir = tmp_path / "texts"
    texts_dir.mkdir()
    (texts_dir / "PLT-NEWS-01.txt").write_text("A complete article.", encoding="utf-8")
    monkeypatch.setattr(raters.pcfg, "PILOT_TEXTS", texts_dir)

    answers = iter(["y", ""])
    raters.interactive_rate("alice", input_fn=lambda _=None: next(answers))
    saved = raters.load_ratings(tmp_path / "ratings.json")
    assert len(saved) == 1
    assert saved[0]["rater"] == "alice"
    assert saved[0]["self_contained"] is True


def test_interactive_rate_skip(monkeypatch, tmp_path):
    monkeypatch.setattr(raters, "RATINGS_PATH", tmp_path / "ratings.json")
    texts_dir = tmp_path / "texts"
    texts_dir.mkdir()
    (texts_dir / "PLT-NEWS-01.txt").write_text("x", encoding="utf-8")
    monkeypatch.setattr(raters.pcfg, "PILOT_TEXTS", texts_dir)

    answers = iter(["s"])
    raters.interactive_rate("bob", input_fn=lambda _=None: next(answers))
    assert raters.load_ratings(tmp_path / "ratings.json") == []
