"""Final validation of the 10 collected text pairs."""
from __future__ import annotations

import json
import sys

from . import config
from .filters import (
    check_duplicate,
    find_pii,
    find_stop_phrases,
    length_ok,
    trigrams,
    word_count,
)
from .config import SLOTS


def _load_pairs() -> tuple[dict[str, str], dict[str, dict], list[str]]:
    texts: dict[str, str] = {}
    metas: dict[str, dict] = {}
    errors: list[str] = []
    if not config.OUTPUT_DIR.exists():
        return texts, metas, ["output dir missing"]
    for txt_file in sorted(config.OUTPUT_DIR.glob("*.txt")):
        tid = txt_file.stem
        meta_file = config.OUTPUT_DIR / f"{tid}.meta.json"
        if not meta_file.exists():
            errors.append(f"{tid}: meta.json missing")
            continue
        texts[tid] = txt_file.read_text(encoding="utf-8")
        metas[tid] = json.loads(meta_file.read_text(encoding="utf-8"))
    for meta_file in config.OUTPUT_DIR.glob("*.meta.json"):
        tid = meta_file.stem.replace(".meta", "")
        if tid not in texts:
            errors.append(f"{tid}: .txt missing")
    return texts, metas, errors


def validate() -> bool:
    texts, metas, errors = _load_pairs()
    results: list[tuple[str, bool, str]] = []

    # 1. count
    n = len(texts)
    results.append(("count == 10", n == 10, f"found {n} pairs" + (f"; {errors}" if errors else "")))

    # 2. wordcount matches meta + genre range
    ok = True
    detail = []
    for tid, txt in texts.items():
        wc = word_count(txt)
        meta_wc = metas[tid].get("wordcount")
        genre = metas[tid].get("genre", "")
        if wc != meta_wc:
            ok = False
            detail.append(f"{tid}: meta wc={meta_wc} actual={wc}")
        if genre and not length_ok(wc, genre):
            ok = False
            detail.append(f"{tid}: wc={wc} outside {genre} range")
    results.append(("wordcount consistent + in genre range", ok, "; ".join(detail) or "all ok"))

    # 3. PII
    ok = True
    detail = []
    for tid, txt in texts.items():
        pii = find_pii(txt)
        if pii:
            ok = False
            detail.append(f"{tid}: {pii[:2]}")
    results.append(("no PII", ok, "; ".join(detail) or "all clean"))

    # 4. duplicates
    ok = True
    detail = []
    tgs = {tid: trigrams(t) for tid, t in texts.items()}
    ids = sorted(tgs)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            from .filters import jaccard

            ov = jaccard(tgs[a], tgs[b])
            if ov >= config.DUP_REJECT_THRESHOLD:
                ok = False
                detail.append(f"{a}/{b}: {ov:.2%}")
    results.append(("pairwise 3-gram overlap < 95%", ok, "; ".join(detail) or "all ok"))

    # 5. self-containment
    ok = True
    detail = []
    for tid, txt in texts.items():
        sp = find_stop_phrases(txt)
        if sp:
            ok = False
            detail.append(f"{tid}: {sp[:2]}")
    results.append(("no stop phrases", ok, "; ".join(detail) or "all ok"))

    # 6. license fields
    ok = True
    detail = []
    for tid, meta in metas.items():
        if not meta.get("license") or not meta.get("license_proof"):
            ok = False
            detail.append(f"{tid}: license/license_proof empty")
    results.append(("license + license_proof filled", ok, "; ".join(detail) or "all ok"))

    # 7. genre counts
    counts: dict[str, int] = {}
    for meta in metas.values():
        counts[meta.get("genre", "?")] = counts.get(meta.get("genre", "?"), 0) + 1
    expected = {"news": 3, "sci": 3, "ins": 2, "fic": 1, "dia": 1}
    ok = counts == expected
    results.append(("genre counts 3/3/2/1/1", ok, f"got {counts}"))

    # 8. author/topic uniqueness
    ok = True
    detail = []
    authors: dict[str, list[str]] = {}
    topics: dict[str, list[str]] = {}
    for tid, meta in metas.items():
        a = meta.get("author") or ""
        if a:
            authors.setdefault(a, []).append(tid)
        t = meta.get("topic") or ""
        if t:
            topics.setdefault(t, []).append(tid)
    for a, tids in authors.items():
        if len(tids) > 1:
            ok = False
            detail.append(f"author '{a}' in {tids}")
    for t, tids in topics.items():
        if len(tids) > 1:
            ok = False
            detail.append(f"topic '{t}' in {tids}")
    results.append(("unique authors/topics", ok, "; ".join(detail) or "all unique"))

    # 9. working log
    log_ok = False
    try:
        content = config.SMOKE_TEST_MD.read_text(encoding="utf-8")
        log_ok = "text_id" in content and "| ~" in content or "SMK-" in content
    except OSError:
        log_ok = False
    results.append(("SMOKE_TEST.md log table filled", log_ok, ""))

    all_ok = all(ok for _, ok, _ in results)
    print("=" * 60)
    for name, ok, detail in results:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    print("=" * 60)
    print("ALL CHECKS PASSED" if all_ok else "VALIDATION FAILED")
    return all_ok


def main() -> int:
    return 0 if validate() else 1


if __name__ == "__main__":
    sys.exit(main())
