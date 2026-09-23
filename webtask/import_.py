"""Import a filled web-UI task sheet into the standard summary layout."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from smoke_summarizer.runner import length_ok

from .sheet import parse_sheet

log = logging.getLogger(__name__)


def import_sheet(
    sheet_file: str,
    system: str,
    out_dir: str,
    tolerance: float = 0.20,
    operator: str = "",
) -> list[dict]:
    """Parse the filled sheet, write each non-empty response as a summary.

    Returns the list of written records (skips empty responses).
    """
    text = Path(sheet_file).read_text(encoding="utf-8")
    tasks = parse_sheet(text)
    written: list[dict] = []
    skipped = 0
    for t in tasks:
        resp = (t.get("response") or "").strip()
        if not resp:
            skipped += 1
            continue
        wc = len(resp.split())
        ok = length_ok(wc, t["target"], tolerance)
        d = Path(out_dir) / system / t["text_id"] / t["level"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "summary_0.txt").write_text(resp, encoding="utf-8")
        rec = {
            "text_id": t["text_id"],
            "system": system,
            "origin": "web",
            "model": system,
            "operator": operator,
            "level": t["level"],
            "target_words": t["target"],
            "wordcount": wc,
            "length_ok": ok,
            "tolerance": tolerance,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        (d / "summary_0.json").write_text(
            json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        written.append(rec)
        if not ok:
            log.warning("length_fail %s %s: %dw vs target %dw", t["text_id"], t["level"], wc, t["target"])
    log.info(
        "imported %d summaries (%d empty/skipped) for system=%s",
        len(written),
        skipped,
        system,
    )
    return written


def summary_report(records: list[dict]) -> str:
    total = len(records)
    ok = sum(1 for r in records if r["length_ok"])
    return f"imported {total} summaries: {ok} in tolerance, {total - ok} length_fail"
