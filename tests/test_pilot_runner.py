import tempfile
from pathlib import Path

from pilot import runner
from smoke_collector.sources import Candidate


def _cand(genre, i):
    return Candidate(
        text=" ".join([f"{genre}word{i}"] * 350),
        source_url=f"https://example.com/{genre}/{i}",
        source_name="TestSrc",
        genre=genre,
        title=f"{genre} title {i}",
        license="CC BY 4.0",
        license_proof="x",
        topic=f"{genre} topic",
    )


def test_save_split_writes_files(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "SPLIT_DIRS", {k: tmp_path / k for k in runner.SPLIT_DIRS})
    sel = {"news": [_cand("news", 1), _cand("news", 2)]}
    recs = runner.save_split(sel, "pilot")
    assert len(recs) == 2
    assert (tmp_path / "pilot" / "PLT-NEWS-01.txt").exists()
    assert (tmp_path / "pilot" / "PLT-NEWS-02.meta.json").exists()
    assert recs[0]["split"] == "pilot"


def test_coverage_report_flags_underfill():
    sel = {"news": [_cand("news", 1)]}
    lines = runner.coverage_report(sel, {"news": 5, "sci": 2})
    joined = "\n".join(lines)
    assert "UNDER-FILL (1/5)" in joined
    assert "UNDER-FILL (0/2)" in joined


def test_coverage_report_ok():
    sel = {"news": [_cand("news", i) for i in range(5)]}
    lines = runner.coverage_report(sel, {"news": 5})
    assert "OK" in "\n".join(lines)
