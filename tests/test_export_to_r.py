import csv
import json
from pathlib import Path

from analysis.export_to_r import export, _level_to_r


def test_level_to_r():
    assert _level_to_r("r0p5") == 0.5
    assert _level_to_r("r0p05") == 0.05
    assert _level_to_r("r0p9") == 0.9


def _make_tree(root: Path):
    summ = root / "summaries" / "qwen3.5-122b" / "T1" / "r0p5"
    summ.mkdir(parents=True)
    qa = {
        "text_id": "T1",
        "scores": {
            "qa": {"correct": 7, "total": 10},
            "nli": {"correct": 3, "total": 6},
            "stance": {"correct": 2, "total": 4},
            "mcq": {"correct": 6, "total": 8},
        },
    }
    (summ / "summary_0.qa.json").write_text(json.dumps(qa), encoding="utf-8")
    texts = root / "texts"
    texts.mkdir()
    (texts / "T1.meta.json").write_text(json.dumps({"genre": "news"}), encoding="utf-8")


def test_export_produces_long_rows(tmp_path):
    _make_tree(tmp_path)
    cfg = tmp_path / "cfg.json"
    cfg.write_text(
        json.dumps(
            {
                "dimension_method": {
                    "facts": "qa", "logic": "nli",
                    "stance": "stance", "comprehension": "mcq",
                },
                "lineup": {"sources": [{"system": "qwen3.5-122b", "base_model": "qwen"}]},
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "fit.csv"
    n = export(str(tmp_path / "summaries"), str(cfg), str(out), str(tmp_path / "texts"))
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert n == 4
    by_dim = {r["dimension"]: r for r in rows}
    assert by_dim["facts"]["pass"] == "7" and by_dim["facts"]["m_d"] == "10"
    assert by_dim["logic"]["pass"] == "3"
    assert by_dim["comprehension"]["m_d"] == "8"
    assert rows[0]["base_model"] == "qwen"
    assert rows[0]["genre"] == "news"
    assert float(rows[0]["level_r"]) == 0.5


def test_export_skips_missing_method(tmp_path):
    root = tmp_path
    summ = root / "summaries" / "x" / "T1" / "r0p5"
    summ.mkdir(parents=True)
    (summ / "summary_0.qa.json").write_text(
        json.dumps({"scores": {"qa": {"correct": 1, "total": 2}}}), encoding="utf-8"
    )
    cfg = root / "cfg.json"
    cfg.write_text(
        json.dumps({"dimension_method": {"facts": "qa", "logic": "nli"}, "lineup": {"sources": []}}),
        encoding="utf-8",
    )
    out = root / "fit.csv"
    n = export(str(root / "summaries"), str(cfg), str(out), str(root / "texts"))
    # only facts present (nli missing)
    assert n == 1
