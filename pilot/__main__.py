"""CLI: python -m pilot.runner --split pilot|validation|main|all"""
from __future__ import annotations

import argparse
import logging
import sys

from .runner import run


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="pilot.runner")
    p.add_argument(
        "--split",
        nargs="+",
        choices=["pilot", "validation", "main", "all"],
        default=["pilot"],
        help="which corpus split(s) to build",
    )
    p.add_argument("--seed", type=int, default=None, help="base seed (default 42)")
    p.add_argument("--scale", type=int, default=None, help="pool scale multiplier (default 10)")
    p.add_argument("--log-file", default="pilot.log")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(args.log_file, encoding="utf-8"),
        ],
    )
    splits = (
        ["pilot", "validation", "main"]
        if "all" in args.split
        else args.split
    )
    saved = run(splits, base_seed=args.seed, scale=args.scale)
    total = sum(len(v) for v in saved.values())
    print(f"\nDone: {total} texts across {list(saved)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
