"""Orchestration: source -> filter -> balance -> save. CLI entry point."""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
import time
from datetime import date
from pathlib import Path

from . import config
from .balance import Balancer
from .filters import check_duplicate, check_text, in_bucket_target, trigrams
from .sources import Candidate

log = logging.getLogger(__name__)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

SOURCE_MAP = {
    "news": "smoke_collector.sources.lenta",
    "sci": "smoke_collector.sources.cyberleninka",
    "ins": "smoke_collector.sources.procedural_pages",
    "fic": "smoke_collector.sources.gutenberg",
    "dia": "smoke_collector.sources.dialogues",
    # legacy alternative for "ins": smoke_collector.sources.gosuslugi
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


def collect_genre(
    genre: str,
    balancer: Balancer,
    selected: dict[str, str],
    pools: dict[str, list[dict]] | None = None,
) -> list[dict]:
    """Fill all slots of one genre. Returns saved-text records."""
    slots = [(g, b) for g, b in config.SLOTS if g == genre]
    if not slots:
        log.error("unknown genre %s", genre)
        return []
    candidates = _load_source(genre)
    log.info("%s: %d raw candidates", genre, len(candidates))
    if pools is not None:
        pools[genre] = [
            {
                "source_url": c.source_url,
                "content_hash": _sha(c.text),
                "wordcount": len(c.text.split()),
            }
            for c in candidates
        ]
    records: list[dict] = []
    used_ids: set[str] = set(selected)
    existing_trigrams: dict[str, set] = {
        rid: trigrams(txt) for rid, txt in selected.items()
    }
    used_topics: set[str] = set()
    for _g, bucket in slots:
        filled = False
        for prefer_new_topic in (True, False):
            if filled:
                break
            for cand in candidates:
                if prefer_new_topic and cand.topic and cand.topic in used_topics:
                    continue
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
                if cand.topic:
                    used_topics.add(cand.topic)
                rec = _save(cand, text_id, bucket, fr.wordcount)
                selected[text_id] = cand.text
                existing_trigrams[text_id] = trigrams(cand.text)
                records.append(rec)
                filled = True
                break
        if not filled:
            if balancer.free_slots(genre, bucket):
                log.warning("%s: no candidate for bucket ~%d", genre, bucket)
            else:
                log.info("%s: bucket ~%d already filled (skipped)", genre, bucket)
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
        "topic": cand.topic,
        "notes": cand.notes,
    }
    (config.OUTPUT_DIR / f"{text_id}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log.info("saved %s (%d words, ~%d) <- %s", text_id, wordcount, bucket, cand.source_url)
    return meta


def _preload() -> dict[str, str]:
    selected: dict[str, str] = {}
    if config.OUTPUT_DIR.exists():
        for txt_file in config.OUTPUT_DIR.glob("*.txt"):
            selected[txt_file.stem] = txt_file.read_text(encoding="utf-8")
    return selected


def run(genres: list[str], fresh: bool = False) -> list[dict]:
    balancer = Balancer()
    if fresh:
        selected: dict[str, str] = {}
        if config.OUTPUT_DIR.exists():
            existing = list(config.OUTPUT_DIR.glob("SMK-*"))
            if existing:
                stamp = date.today().isoformat() + "-" + time.strftime("%H%M%S")
                archive = config.ARCHIVE_DIR / stamp
                archive.mkdir(parents=True, exist_ok=True)
                for f in existing:
                    f.rename(archive / f.name)
                log.info("archived %d prior files -> %s", len(existing), archive)
    else:
        selected = _preload()
        for meta_file in config.OUTPUT_DIR.glob("*.meta.json") if config.OUTPUT_DIR.exists() else []:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            bucket = int(meta["target_bucket"].lstrip("~"))
            balancer.try_assign(meta["genre"], bucket, meta["text_id"])
    records: list[dict] = []
    pools: dict[str, list[dict]] = {}
    for genre in genres:
        try:
            records.extend(collect_genre(genre, balancer, selected, pools))
        except Exception as exc:  # noqa: BLE001
            log.error("genre %s failed: %s", genre, exc)
            pools.setdefault(genre, [])
    write_manifest(pools, records)
    write_log_table(records)
    missing = balancer.missing()
    if missing:
        log.error("UNFILLED slots: %s", missing)
    else:
        log.info("all 10 slots filled")
    return records


def write_manifest(pools: dict[str, list[dict]], records: list[dict]) -> None:
    """Save the candidate-pool content-hash manifest and report drift vs the previous run."""
    previous: dict = {}
    if config.MANIFEST_PATH.exists():
        try:
            previous = json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            previous = {}
    manifest = {
        "run_date": date.today().isoformat(),
        "selected": sorted(r["text_id"] for r in records),
        "pools": pools,
    }
    config.MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    config.MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log.info("wrote candidate-pool manifest: %s", config.MANIFEST_PATH)
    if previous.get("pools"):
        drift = _diff_pools(previous["pools"], pools)
        if drift:
            for line in drift:
                log.warning("DRIFT: %s", line)
        else:
            log.info("no candidate-pool drift vs previous run")


def _diff_pools(old: dict, new: dict) -> list[str]:
    """Compare candidate pools by source_url -> content_hash; report changes."""
    out: list[str] = []
    for genre in sorted(set(old) | set(new)):
        o = {c["source_url"]: c["content_hash"] for c in old.get(genre, [])}
        n = {c["source_url"]: c["content_hash"] for c in new.get(genre, [])}
        added = set(n) - set(o)
        removed = set(o) - set(n)
        changed = {u for u in set(o) & set(n) if o[u] != n[u]}
        if added:
            out.append(f"{genre}: +{len(added)} new candidates")
        if removed:
            out.append(f"{genre}: -{len(removed)} candidates gone")
        if changed:
            out.append(f"{genre}: {len(changed)} candidates changed content")
    return out


LOG_TABLE_START = "<!-- smoke_collector:table:start -->"
LOG_TABLE_END = "<!-- smoke_collector:table:end -->"


def write_log_table(records: list[dict]) -> None:
    all_records: dict[str, dict] = {}
    if config.OUTPUT_DIR.exists():
        for meta_file in config.OUTPUT_DIR.glob("*.meta.json"):
            m = json.loads(meta_file.read_text(encoding="utf-8"))
            all_records[m["text_id"]] = m
    for r in records:
        all_records[r["text_id"]] = r
    lines = [
        "| text_id | жанр | источник | wordcount | корзина | лицензия | PII | дубликаты | самодостаточность |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in sorted(all_records.values(), key=lambda x: x["text_id"]):
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
    records = run(genres, fresh=args.all)
    return 0 if len(records) == len(config.SLOTS) else 1


if __name__ == "__main__":
    sys.exit(main())
