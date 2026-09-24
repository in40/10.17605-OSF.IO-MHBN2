"""CLI: python -m smoke_summarizer [options]"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys

from .runner import SummConfig, load_config, load_texts, run


def setup_logging(logfile: str | None = None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if logfile:
        handlers.append(logging.FileHandler(logfile, encoding="utf-8"))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="smoke_summarizer")
    p.add_argument("--config", help="JSON config file (defaults, overridden by CLI)")
    p.add_argument("--type", choices=["llm", "extractive", "hybrid", "oracle"], default=None)
    p.add_argument("--base-url", default=None)
    p.add_argument("--api-key", default=None, help="API key literal")
    p.add_argument("--api-key-env", default="SC_KEY", help="env var holding the key")
    p.add_argument("--model", default=None)
    p.add_argument("--system", default=None, help="system label for output dir")
    p.add_argument(
        "--levels",
        nargs="+",
        type=float,
        default=None,
        help="compression ratios, e.g. 0.9 0.5 0.05",
    )
    p.add_argument("--n", type=int, default=None, help="summaries per (text, level)")
    p.add_argument("--temperature", type=float, default=None)
    p.add_argument("--max-tokens", type=int, default=None)
    p.add_argument("--top-p", type=float, default=None)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--tolerance", type=float, default=None, help="±fraction of target")
    p.add_argument("--regen", type=int, default=None, help="regen attempts on length miss")
    p.add_argument("--hybrid-backend", choices=["transformers", "ctranslate2"], default=None)
    p.add_argument("--hybrid-model", default=None, help="RU seq2seq model for hybrid (default rut5_base_sum_gazeta)")
    p.add_argument("--extractive-scale", type=float, default=None, help="hybrid grounding subset = target * scale")
    p.add_argument("--hybrid-online", action="store_true", help="allow HuggingFace network for hybrid (one-time model download); default is offline")
    p.add_argument("--force", action="store_true", help="regenerate even if summary files already exist (default: resume/skip)")
    p.add_argument("--texts-dir", default=None)
    p.add_argument("--out-dir", default=None)
    p.add_argument("--prompt-base", default=None, help="path to base prompt template file")
    p.add_argument("--prompt-regen", default=None, help="path to regen prompt template file")
    p.add_argument("--log-file", default="smoke_summarizer.log")
    p.add_argument("--limit", type=int, default=None, help="max texts (for quick tests)")
    p.add_argument(
        "--no-think",
        action="store_true",
        help="disable reasoning tokens (chat_template_kwargs.enable_thinking=false)",
    )
    args = p.parse_args(argv)

    setup_logging(args.log_file)
    cfg: SummConfig = load_config(args.config)

    if args.type:
        cfg.type = args.type
    if args.base_url:
        cfg.base_url = args.base_url
    cfg.api_key = args.api_key or os.environ.get(args.api_key_env, "")
    if args.model:
        cfg.model = args.model
    if args.system:
        cfg.system = args.system
    if args.levels:
        cfg.levels = tuple(args.levels)
    if args.n is not None:
        cfg.n_summaries = args.n
    if args.temperature is not None:
        cfg.temperature = args.temperature
    if args.max_tokens is not None:
        cfg.max_tokens = args.max_tokens
    if args.top_p is not None:
        cfg.top_p = args.top_p
    if args.seed is not None:
        cfg.seed = args.seed
    if args.tolerance is not None:
        cfg.tolerance = args.tolerance
    if args.regen is not None:
        cfg.regen_attempts = args.regen
    if args.hybrid_backend:
        cfg.hybrid_backend = args.hybrid_backend
    if args.hybrid_model:
        cfg.hybrid_model = args.hybrid_model
    if args.hybrid_online:
        cfg.hybrid_offline = False
    if args.force:
        cfg.force = True
    if args.extractive_scale is not None:
        cfg.extractive_scale = args.extractive_scale
    if args.texts_dir:
        cfg.texts_dir = args.texts_dir
    if args.out_dir:
        cfg.out_dir = args.out_dir
    if args.prompt_base:
        cfg.prompt_base = open(args.prompt_base, encoding="utf-8").read()
    if args.prompt_regen:
        cfg.prompt_regen = open(args.prompt_regen, encoding="utf-8").read()
    if args.no_think:
        ctk = cfg.extra.setdefault("chat_template_kwargs", {})
        ctk["enable_thinking"] = False

    if not cfg.api_key and cfg.type not in ("extractive", "hybrid", "oracle"):
        print(f"ERROR: no API key (set --api-key or env {args.api_key_env})", file=sys.stderr)
        return 2

    texts = load_texts(cfg.texts_dir)
    if not texts:
        print(f"ERROR: no .txt files in {cfg.texts_dir}", file=sys.stderr)
        return 2
    if args.limit:
        texts = dict(list(texts.items())[: args.limit])

    logging.info(
        "running %d texts x %d levels x %d summaries [%s] on %s",
        len(texts), len(cfg.levels), cfg.n_summaries, cfg.type,
        cfg.model if cfg.type != "extractive" else "TextRank",
    )
    records = run(cfg, texts)
    ok = sum(1 for r in records if r["status"] == "ok")
    print(f"\nDone: {len(records)} summaries, {ok} on-target, "
          f"{len(records) - ok} length_fail")
    print(f"Output: {cfg.out_dir}/{cfg.system_label}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
