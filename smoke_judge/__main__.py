"""CLI: python -m smoke_judge [options]"""
from __future__ import annotations

import argparse
import logging
import os
import sys

from .runner import JudgeConfig, run


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="smoke_judge")
    p.add_argument("--base-url", default="https://chat.sorokinonline.com/v1")
    p.add_argument("--api-key", default=None)
    p.add_argument("--api-key-env", default="SC_KEY")
    p.add_argument("--model", default="qwen3.5-122b")
    p.add_argument("--mode", choices=["combined", "per_dimension"], default="combined")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--top-p", type=float, default=0.95)
    p.add_argument("--max-tokens", type=int, default=256)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--retries", type=int, default=1)
    p.add_argument("--think", action="store_true", help="enable reasoning (default off)")
    p.add_argument("--summaries-dir", default="smoke/summaries")
    p.add_argument("--texts-dir", default="smoke/texts")
    p.add_argument("--log-file", default="smoke_judge.log")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(args.log_file, encoding="utf-8"),
        ],
    )
    cfg = JudgeConfig(
        base_url=args.base_url,
        api_key=args.api_key or os.environ.get(args.api_key_env, ""),
        model=args.model,
        mode=args.mode,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        seed=args.seed,
        retries=args.retries,
        no_think=not args.think,
        summaries_dir=args.summaries_dir,
        texts_dir=args.texts_dir,
    )
    if not cfg.no_think:
        pass
    else:
        cfg.extra.setdefault("chat_template_kwargs", {})["enable_thinking"] = False

    if not cfg.api_key:
        print(f"ERROR: no API key (set --api-key or env {args.api_key_env})", file=sys.stderr)
        return 2

    records = run(cfg)
    ok = sum(1 for r in records if r["status"] == "ok")
    print(f"\nDone: {len(records)} judged, {ok} ok, {len(records) - ok} missing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
