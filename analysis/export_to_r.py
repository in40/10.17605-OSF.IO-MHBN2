"""Export scored summaries (judge + QA) into a long dataframe for R/brms fitting.

Reads the summaries tree:
    <summaries_dir>/<system>/<text_id>/<level>/summary_*.qa.json
and emits one row per (text, source, level, dimension):
    text_id, genre, source, base_model, level_r, dimension, pass, m_d

`pass` = items correct, `m_d` = items total, for the item method feeding each
core dimension (facts<-qa, logic<-nli, stance<-stance, comprehension<-mcq).
The source->base_model mapping + dimension->method map come from the frozen
config.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

DIM_METHOD_FALLBACK = {
    "facts": "qa",
    "logic": "nli",
    "stance": "stance",
    "comprehension": "mcq",
}


def _level_to_r(tag: str) -> float:
    # r0p5 -> 0.5
    return float(tag.lstrip("r").replace("p", "."))


def _load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _source_base_map(cfg: dict) -> dict:
    return {
        s["system"]: s.get("base_model", s["system"])
        for s in cfg.get("lineup", {}).get("sources", [])
    }


def _genre_for(texts_dir: Path, text_id: str) -> str:
    meta = texts_dir / f"{text_id}.meta.json"
    if meta.exists():
        try:
            return json.loads(meta.read_text(encoding="utf-8")).get("genre", "")
        except (json.JSONDecodeError, OSError):
            return ""
    return ""


def export(summaries_dir: str, config_path: str, out_csv: str, texts_dir: str | None = None) -> int:
    cfg = _load_config(config_path)
    dim_method = cfg.get("dimension_method", DIM_METHOD_FALLBACK)
    base_map = _source_base_map(cfg)
    summ = Path(summaries_dir)
    tdir = Path(texts_dir) if texts_dir else summ.parent / "texts"

    rows = []
    for qa_file in sorted(summ.glob("*/*/*/summary_*.qa.json")):
        try:
            data = json.loads(qa_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        scores = data.get("scores", {})
        level_tag = qa_file.parent.name
        text_id = qa_file.parent.parent.name
        source = qa_file.parent.parent.parent.name
        try:
            level_r = _level_to_r(level_tag)
        except ValueError:
            continue
        genre = _genre_for(tdir, text_id)
        base_model = base_map.get(source, source)
        for dim, method in dim_method.items():
            sc = scores.get(method)
            if not sc or "total" not in sc:
                continue
            rows.append(
                {
                    "text_id": text_id,
                    "genre": genre,
                    "source": source,
                    "base_model": base_model,
                    "level_r": level_r,
                    "dimension": dim,
                    "pass": int(sc.get("correct", 0)),
                    "m_d": int(sc.get("total", 0)),
                }
            )

    out = Path(out_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "text_id", "genre", "source", "base_model",
                "level_r", "dimension", "pass", "m_d",
            ],
        )
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="export_to_r")
    p.add_argument("--summaries-dir", required=True)
    p.add_argument("--config", required=True, help="frozen config JSON")
    p.add_argument("--out", required=True, help="output CSV for R")
    p.add_argument("--texts-dir", default=None, help="for genre lookup (default: <summaries>/../texts)")
    args = p.parse_args(argv)
    n = export(args.summaries_dir, args.config, args.out, args.texts_dir)
    print(f"Exported {n} rows -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
