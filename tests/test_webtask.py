from pathlib import Path

from webtask.export import build_sheet, export_sheet
from webtask.import_ import import_sheet, summary_report
from webtask.sheet import format_task, parse_sheet


def test_format_task_roundtrip():
    block = format_task("T1", "r0p5", 50, "PROMPT TEXT")
    tasks = parse_sheet(block)
    assert len(tasks) == 1
    t = tasks[0]
    assert t["text_id"] == "T1"
    assert t["level"] == "r0p5"
    assert t["target"] == 50
    assert t["prompt"] == "PROMPT TEXT"
    assert t["response"] == ""


def test_parse_filled_response():
    filled = (
        "===TASK T1 r0p5 50===\n"
        "---PROMPT---\nhello\n---ENDPROMPT---\n"
        "---RESPONSE---\nthis is the model summary\n---ENDRESPONSE---\n"
    )
    tasks = parse_sheet(filled)
    assert tasks[0]["response"] == "this is the model summary"


def test_build_sheet_targets(tmp_path):
    texts = tmp_path / "texts"
    texts.mkdir()
    (texts / "T1.txt").write_text(" ".join(["word"] * 100), encoding="utf-8")
    sheet = build_sheet("alisa", str(texts), levels=(0.5, 0.2))
    tasks = parse_sheet(sheet)
    assert len(tasks) == 2
    targets = {t["level"]: t["target"] for t in tasks}
    assert targets["r0p5"] == 50
    assert targets["r0p2"] == 20
    # prompt is self-contained: includes the source text
    assert "word word" in tasks[0]["prompt"]


def test_export_writes_file(tmp_path):
    texts = tmp_path / "texts"
    texts.mkdir()
    (texts / "T1.txt").write_text(" ".join(["w"] * 40), encoding="utf-8")
    out = tmp_path / "sheet.md"
    n = export_sheet("gigachat", str(texts), str(out), levels=(0.5,))
    assert n == 1
    assert out.exists()
    assert "gigachat" in out.read_text(encoding="utf-8")


def test_import_writes_standard_layout(tmp_path):
    filled = (
        "===TASK T1 r0p5 10===\n"
        "---PROMPT---\nsrc\n---ENDPROMPT---\n"
        "---RESPONSE---\n" + " ".join(["s"] * 10) + "\n---ENDRESPONSE---\n"
    )
    sheet = tmp_path / "filled.md"
    sheet.write_text(filled, encoding="utf-8")
    out = tmp_path / "summaries"
    recs = import_sheet(str(sheet), "alisa", str(out), tolerance=0.2, operator="bob")
    assert len(recs) == 1
    f = out / "alisa" / "T1" / "r0p5" / "summary_0.txt"
    assert f.exists()
    assert f.read_text(encoding="utf-8") == " ".join(["s"] * 10)
    meta = out / "alisa" / "T1" / "r0p5" / "summary_0.json"
    assert meta.exists()
    import json

    rec = json.loads(meta.read_text(encoding="utf-8"))
    assert rec["origin"] == "web"
    assert rec["operator"] == "bob"
    assert rec["length_ok"] is True


def test_import_skips_empty_response(tmp_path):
    filled = (
        "===TASK T1 r0p5 10===\n"
        "---PROMPT---\nsrc\n---ENDPROMPT---\n"
        "---RESPONSE---\n\n---ENDRESPONSE---\n"
    )
    sheet = tmp_path / "filled.md"
    sheet.write_text(filled, encoding="utf-8")
    out = tmp_path / "summaries"
    recs = import_sheet(str(sheet), "alisa", str(out))
    assert recs == []
    assert not (out / "alisa" / "T1" / "r0p5").exists()


def test_import_flags_length_fail(tmp_path):
    filled = (
        "===TASK T1 r0p5 10===\n"
        "---PROMPT---\nsrc\n---ENDPROMPT---\n"
        "---RESPONSE---\n" + " ".join(["s"] * 50) + "\n---ENDRESPONSE---\n"
    )
    sheet = tmp_path / "filled.md"
    sheet.write_text(filled, encoding="utf-8")
    out = tmp_path / "summaries"
    recs = import_sheet(str(sheet), "alisa", str(out), tolerance=0.2)
    assert len(recs) == 1
    assert recs[0]["length_ok"] is False
    assert "length_fail" in summary_report(recs)
