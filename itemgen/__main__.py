"""CLI: generate frozen items from texts, and score summaries against them.

  python -m itemgen generate --texts-dir smoke/texts --items-dir smoke/items
  python -m itemgen score   --items-dir smoke/items --summaries-dir smoke/summaries
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from smoke_summarizer.client import LLMClient

from .config import ItemGenConfig
from .generator import generate_items, KINDS
from .manifest import build_manifest, manifest_digest
from .scorer import score_summary

log = logging.getLogger("itemgen")


def _make_client(cfg: ItemGenConfig) -> LLMClient:
    key = cfg.api_key or os.environ.get("SC_KEY", "")
    return LLMClient(cfg.base_url, key, cfg.model)


def cmd_generate(args) -> int:
    cfg = ItemGenConfig(
        model=args.model,
        seed=args.seed,
        n_qa=args.n_qa,
        n_mcq=args.n_mcq,
        n_nli=args.n_nli,
        n_stance=args.n_stance,
        texts_dir=args.texts_dir,
        items_dir=args.items_dir,
    )
    client = _make_client(cfg)
    kinds = args.kinds.split(",") if args.kinds else list(KINDS)
    texts_dir = Path(cfg.texts_dir)
    items_dir = Path(cfg.items_dir)
    items_dir.mkdir(parents=True, exist_ok=True)

    all_items: dict[str, dict] = {}
    for tf in sorted(texts_dir.glob("*.txt")):
        tid = tf.stem
        source = tf.read_text(encoding="utf-8")
        items = generate_items(client, cfg, source, kinds=kinds)
        all_items[tid] = items
        out = items_dir / f"{tid}.items.json"
        out.write_text(
            json.dumps({"text_id": tid, "model": cfg.model, "seed": cfg.seed, "items": items},
                      ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        log.info("wrote %s", out)

    manifest = build_manifest(all_items)
    (items_dir / "manifest.json").write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "model": cfg.model,
                "seed": cfg.seed,
                "digest": manifest_digest(manifest),
                "items": manifest,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Generated items for {len(all_items)} texts -> {items_dir}")
    print(f"Manifest digest: {manifest_digest(manifest)}")
    return 0


def cmd_score(args) -> int:
    cfg = ItemGenConfig(
        model=args.model,
        seed=args.seed,
        items_dir=args.items_dir,
        summaries_dir=args.summaries_dir,
    )
    client = _make_client(cfg)
    items_dir = Path(cfg.items_dir)
    summ_root = Path(cfg.summaries_dir)

    n = 0
    for sfile in sorted(summ_root.rglob("summary_*.txt")):
        text_id = sfile.parent.parent.name
        ifile = items_dir / f"{text_id}.items.json"
        if not ifile.exists():
            log.warning("no items for %s", text_id)
            continue
        items_by_kind = json.loads(ifile.read_text(encoding="utf-8"))["items"]
        summary = sfile.read_text(encoding="utf-8")
        result = score_summary(client, cfg, items_by_kind, summary)
        jfile = sfile.with_name(sfile.stem + ".qa.json")
        jfile.write_text(
            json.dumps(
                {
                    "text_id": text_id,
                    "summary_path": str(sfile),
                    "generator_model": cfg.model,
                    "scored_at": datetime.now(timezone.utc).isoformat(),
                    "scores": result,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        n += 1
        log.info("scored %s", sfile.relative_to(summ_root))
    print(f"Scored {n} summaries -> {summ_root}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="itemgen")
    sub = p.add_subparsers(dest="cmd", required=True)

    pg = sub.add_parser("generate", help="generate frozen items from texts")
    pg.add_argument("--texts-dir", default="smoke/texts")
    pg.add_argument("--items-dir", default="smoke/items")
    pg.add_argument("--model", default="qwen3.5-122b")
    pg.add_argument("--seed", type=int, default=42)
    pg.add_argument("--kinds", default="", help="comma-sep: qa,mcq,nli,stance")
    pg.add_argument("--n-qa", type=int, default=10)
    pg.add_argument("--n-mcq", type=int, default=8)
    pg.add_argument("--n-nli", type=int, default=6)
    pg.add_argument("--n-stance", type=int, default=4)
    pg.add_argument("--log-file", default="itemgen.log")

    ps = sub.add_parser("score", help="score summaries against frozen items")
    ps.add_argument("--items-dir", default="smoke/items")
    ps.add_argument("--summaries-dir", default="smoke/summaries")
    ps.add_argument("--model", default="qwen3.5-122b")
    ps.add_argument("--seed", type=int, default=42)
    ps.add_argument("--log-file", default="itemgen.log")

    args = p.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(args.log_file, encoding="utf-8"),
        ],
    )
    if args.cmd == "generate":
        return cmd_generate(args)
    if args.cmd == "score":
        return cmd_score(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
