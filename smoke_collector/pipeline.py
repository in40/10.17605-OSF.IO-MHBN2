"""Orchestration: source -> filter -> balance -> save. CLI entry point."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path

from . import config
from .balance import Balancer
from .filters import check_duplicate, check_text, in_bucket_target, trigrams
from .sources import Candidate

log = logging.getLogger(__name__)

SOURCE_MAP = {
    "news": "smoke_collector.sources.lenta",
    "sci": "smoke_collector.sources.cyberleninka",
    "ins": "smoke_collector.sources.gosuslugi",
    "fic": "smoke_collector.sources.gutenberg",
    "dia": "smoke_collector.sources.dialogues",
}


def setup_logging() -> None:
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    fh = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger("smoke_collector")
    root.handlers = [ch, fh]
    root.setLevel(logging.DEBUG)


def _load_source(genre: str):
    import importlib

    mod = importlib.import_module(SOURCE_MAP[genre])
    return mod.collect()


def _next_text_id(genre: str, used: set[str]) -> str:
    code = config.GENRES[genre]["code"]
    n = 1
    while f"SMK-{code}-{n:02d}" in used:
        n += 1
    return f"SMK-{code}-{n:02d}"


def collect_genre(genre: str, balancer: Balancer, selected: dict[str, str]) -> list[dict]:
    """Fill all slots of one genre. Returns saved-text records."""
    slots = [(g, b) for g, b in config.SLOTS if g == genre]
    if not slots:
        log.error("unknown genre %s", genre)
        return []
    candidates = _load_source(genre)
    log.info("%s: %d raw candidates", genre, len(candidates))
    records: list[dict] = []
    used_ids: set[str] = set(selected)
    existing_trigrams: dict[str, set] = {
        rid: trigrams(txt) for rid, txt in selected.items()
    }
    for _g, bucket in slots:
        filled = False
        for cand in candidates:
            fr = check_text(cand.text, genre)
            if not fr.ok:
                log.debug("reject %s: %s", cand.source_url, fr.reasons)
                continue
            if not in_bucket_target(fr.wordcount, bucket):
                continue
            dup_ok, dup_msgs = check_duplicate(cand.text, existing_trigrams)
            for m in dup_msgs:
                log.info("dedup: %s", m)
            if not dup_ok:
                continue
            text_id = _next_text_id(genre, used_ids)
            if balancer.try_assign(genre, bucket, text_id) is None:
                continue
            used_ids.add(text_id)
            rec = _save(cand, text_id, bucket, fr.wordcount)
            selected[text_id] = cand.text
            existing_trigrams[text_id] = trigrams(cand.text)
            records.append(rec)
            filled = True
            break
        if not filled:
            log.warning("%s: no candidate for bucket ~%d", genre, bucket)
    return records


def _save(cand: Candidate, text_id: str, bucket: int, wordcount: int) -> dict:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    txt_path = config.OUTPUT_DIR / f"{text_id}.txt"
    txt_path.write_text(cand.text, encoding="utf-8")
    meta = {
        "text_id": text_id,
        "genre": cand.genre,
        "source_url": cand.source_url,
        "source_name": cand.source_name,
        "author": cand.author,
        "title": cand.title,
        "date_accessed": date.today().isoformat(),
        "date_published": cand.date_published,
        "license": cand.license,
        "license_proof": cand.license_proof,
        "wordcount": wordcount,
        "target_bucket": f"~{bucket}",
        "language": "ru",
        "notes": cand.notes,
    }
    (config.OUTPUT_DIR / f"{text_id}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log.info("saved %s (%d words, ~%d) <- %s", text_id, wordcount, bucket, cand.source_url)
    return meta


def run(genres: list[str]) -> list[dict]:
    balancer = Balancer()
    selected: dict[str, str] = {}
    records: list[dict] = []
    for genre in genres:
        records.extend(collect_genre(genre, balancer, selected))
    write_log_table(records)
    missing = balancer.missing()
    if missing:
        log.error("UNFILLED slots: %s", missing)
    else:
        log.info("all 10 slots filled")
    return records


LOG_TABLE_START = "<!-- smoke_collector:table:start -->"
LOG_TABLE_END = "<!-- smoke_collector:table:end -->"


def write_log_table(records: list[dict]) -> None:
    lines = [
        "| text_id | жанр | источник | wordcount | корзина | лицензия | PII | дубликаты | самодостаточность |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in sorted(records, key=lambda x: x["text_id"]):
        lines.append(
            f"| {r['text_id']} | {r['genre']} | {r['source_name']} | {r['wordcount']} "
            f"| {r['target_bucket']} | {r['license'][:40]} | ok | ok | ok |"
        )
    table = LOG_TABLE_START + "\n" + "\n".join(lines) + "\n" + LOG_TABLE_END
    md = config.SMOKE_TEST_MD
    content = md.read_text(encoding="utf-8")
    if LOG_TABLE_START in content and LOG_TABLE_END in content:
        pre = content.split(LOG_TABLE_START)[0]
        post = content.split(LOG_TABLE_END)[1]
        content = pre + table + post
    else:
        content = content.rstrip() + "\n\n" + table + "\n"
    md.write_text(content, encoding="utf-8")
    log.info("updated %s working log table", md)


def print_status() -> None:
    balancer = Balancer()
    if config.OUTPUT_DIR.exists():
        for meta_file in sorted(config.OUTPUT_DIR.glob("*.meta.json")):
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            bucket = int(meta["target_bucket"].lstrip("~"))
            balancer.try_assign(meta["genre"], bucket, meta["text_id"])
    print("Bucket status:")
    for key, val in balancer.status().items():
        print(f"  {key}: {'FILLED' if val else 'empty'}")
    missing = balancer.missing()
    print(f"Missing: {missing if missing else 'none'}")


def main(argv: list[str] | None = None) -> int:
    setup_logging()
    parser = argparse.ArgumentParser(prog="smoke_collector.pipeline")
    parser.add_argument("--all", action="store_true", help="collect all genres")
    parser.add_argument("--genre", choices=list(config.GENRES), help="collect one genre")
    parser.add_argument("--status", action="store_true", help="show bucket status")
    args = parser.parse_args(argv)
    if args.status:
        print_status()
        return 0
    genres = list(config.GENRES) if args.all else ([args.genre] if args.genre else [])
    if not genres:
        parser.print_help()
        return 1
    records = run(genres)
    return 0 if len(records) == len(config.SLOTS) else 1


if __name__ == "__main__":
    sys.exit(main())
