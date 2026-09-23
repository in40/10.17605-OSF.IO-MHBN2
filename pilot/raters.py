"""2-rater self-containedness workflow for the pilot corpus.

Per pre-reg §4.2:54 — pilot self-containedness is judged by 2 team members
with consensus required; the initial disagreement rate is reported.

Flow:
  1. `rate`   — a rater walks the unrated pilot texts, records yes/no + note.
  2. (repeat with a second, independent rater)
  3. `report` — aggregate verdicts -> accept / reject / disagree / incomplete,
                compute disagreement rate, list items needing adjudication.

Ratings are stored in pilot_data/ratings.json (append-only ledger).
See pilot/RATER_INSTRUCTIONS.md for what is required of raters.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from . import config as pcfg

log = logging.getLogger(__name__)

RATINGS_PATH = pcfg.PILOT_DIR / "ratings.json"


def split_paths(split: str) -> tuple[Path, Path]:
    """Return (texts_dir, ratings_path) for a corpus split."""
    if split == "pilot":
        return pcfg.PILOT_TEXTS, RATINGS_PATH
    if split == "main":
        return pcfg.MAIN_TEXTS, pcfg.PILOT_DIR / "ratings_main.json"
    if split == "validation":
        return pcfg.VALIDATION_TEXTS, pcfg.PILOT_DIR / "ratings_validation.json"
    raise ValueError(f"unknown split: {split}")


def load_ratings(path: Path | None = None) -> list[dict]:
    p = path or RATINGS_PATH
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_ratings(ratings: list[dict], path: Path | None = None) -> None:
    p = path or RATINGS_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ratings, ensure_ascii=False, indent=2), encoding="utf-8")


def load_pilot_texts(pilot_dir: Path | None = None) -> dict[str, str]:
    d = pilot_dir or pcfg.PILOT_TEXTS
    texts: dict[str, str] = {}
    if d.exists():
        for f in sorted(d.glob("*.txt")):
            texts[f.stem] = f.read_text(encoding="utf-8")
    return texts


def record_rating(
    ratings: list[dict], rater: str, text_id: str, self_contained: bool, note: str = ""
) -> list[dict]:
    ratings = [
        r for r in ratings if not (r["rater"] == rater and r["text_id"] == text_id)
    ]
    ratings.append(
        {
            "text_id": text_id,
            "rater": rater,
            "self_contained": bool(self_contained),
            "note": note,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    return ratings


def aggregate(ratings: list[dict]) -> dict[str, dict]:
    """Group verdicts per text and decide consensus.

    status: accept (all yes) | reject (all no) | disagree (mixed) | incomplete (<2 raters)
    """
    by_text: dict[str, dict[str, bool]] = {}
    for r in ratings:
        by_text.setdefault(r["text_id"], {})[r["rater"]] = bool(r["self_contained"])
    result: dict[str, dict] = {}
    for tid, verdicts in by_text.items():
        vals = list(verdicts.values())
        if len(vals) < 2:
            status = "incomplete"
        elif all(vals):
            status = "accept"
        elif not any(vals):
            status = "reject"
        else:
            status = "disagree"
        result[tid] = {"verdicts": verdicts, "status": status}
    return result


def summary(agg: dict[str, dict]) -> dict[str, int]:
    counts = {"accept": 0, "reject": 0, "disagree": 0, "incomplete": 0}
    for v in agg.values():
        counts[v["status"]] += 1
    decided = counts["accept"] + counts["reject"] + counts["disagree"]
    counts["disagreement_rate"] = (
        round(counts["disagree"] / decided, 3) if decided else 0.0
    )
    return counts


def unrated_for(rater: str, texts: dict[str, str], ratings: list[dict]) -> list[str]:
    done = {r["text_id"] for r in ratings if r["rater"] == rater}
    return [tid for tid in texts if tid not in done]


def interactive_rate(
    rater: str,
    split: str = "pilot",
    input_fn=input,
    output_fn=print,
) -> None:
    texts_dir, ratings_path = split_paths(split)
    texts = load_pilot_texts(texts_dir)
    ratings = load_ratings(ratings_path)
    todo = unrated_for(rater, texts, ratings)
    if not todo:
        output_fn(f"No unrated texts for rater '{rater}' ({split}).")
        return
    output_fn(f"Rater '{rater}' [{split}]: {len(todo)} texts to rate.\n")
    for tid in todo:
        output_fn("=" * 70)
        output_fn(f"[{tid}]")
        output_fn(texts[tid])
        output_fn("-" * 70)
        ans = input_fn("Self-contained? (y/n/s=skip): ").strip().lower()
        if ans in ("y", "n"):
            note = input_fn("Note (optional, esp. if 'n'): ").strip()
            ratings = record_rating(ratings, rater, tid, ans == "y", note)
            save_ratings(ratings, ratings_path)
            output_fn("Recorded.\n")
        else:
            output_fn("Skipped.\n")
    output_fn(f"\nDone. Ratings saved to {ratings_path}")


def print_report(split: str = "pilot", output_fn=print) -> None:
    _, ratings_path = split_paths(split)
    ratings = load_ratings(ratings_path)
    if not ratings:
        output_fn(f"No ratings recorded yet ({split}).")
        return
    agg = aggregate(ratings)
    s = summary(agg)
    output_fn(f"=== Self-containedness rater report [{split}] ===")
    output_fn(f"  accept:     {s['accept']}")
    output_fn(f"  reject:     {s['reject']}")
    output_fn(f"  disagree:   {s['disagree']}")
    output_fn(f"  incomplete: {s['incomplete']}")
    output_fn(f"  disagreement rate: {s['disagreement_rate']:.1%}")
    dis = [tid for tid, v in agg.items() if v["status"] == "disagree"]
    if dis:
        output_fn("\n  NEEDS ADJUDICATION (disagreement):")
        for tid in sorted(dis):
            output_fn(f"    {tid}: {agg[tid]['verdicts']}")
    inc = [tid for tid, v in agg.items() if v["status"] == "incomplete"]
    if inc:
        output_fn(f"\n  Incomplete (need 2nd rater): {len(inc)} texts")


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(
        prog="pilot.raters",
        description="2-rater self-containedness workflow (see RATER_INSTRUCTIONS.md)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("rate", help="interactive rating session for one rater")
    pr.add_argument("--rater", required=True, help="rater id (e.g. alice)")
    pr.add_argument("--split", default="pilot", choices=["pilot", "main", "validation"])

    prep = sub.add_parser("report", help="aggregate verdicts + disagreement report")
    prep.add_argument("--split", default="pilot", choices=["pilot", "main", "validation"])

    pw = sub.add_parser("todo", help="show unrated texts for a rater")
    pw.add_argument("--rater", required=True)
    pw.add_argument("--split", default="pilot", choices=["pilot", "main", "validation"])

    args = p.parse_args(argv)
    if args.cmd == "rate":
        interactive_rate(args.rater, split=args.split)
    elif args.cmd == "report":
        print_report(split=args.split)
    elif args.cmd == "todo":
        texts_dir, ratings_path = split_paths(args.split)
        texts = load_pilot_texts(texts_dir)
        todo = unrated_for(args.rater, texts, load_ratings(ratings_path))
        print(f"{args.rater} [{args.split}]: {len(todo)} unrated of {len(texts)}")
        for tid in todo:
            print(f"  {tid}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
