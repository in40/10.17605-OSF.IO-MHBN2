"""CLI: export a web-UI task sheet, and import the filled sheet back.

  python -m webtask export --system alisa --texts-dir smoke/texts \
      --out smoke/alisa_tasks.md
  python -m webtask import --system alisa --sheet smoke/alisa_tasks.md \
      --out-dir smoke/summaries --operator bob
"""
from __future__ import annotations

import argparse
import logging
import sys

from smoke_summarizer.runner import DEFAULT_LEVELS

from .export import export_sheet
from .import_ import import_sheet, summary_report


def _parse_levels(s: str) -> tuple[float, ...]:
    if not s:
        return DEFAULT_LEVELS
    return tuple(float(x) for x in s.split(",") if x)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="webtask")
    sub = p.add_subparsers(dest="cmd", required=True)

    pe = sub.add_parser("export", help="generate a web-UI task sheet")
    pe.add_argument("--system", required=True, help="e.g. alisa, gigachat")
    pe.add_argument("--texts-dir", default="smoke/texts")
    pe.add_argument("--out", required=True, help="output .md worksheet path")
    pe.add_argument("--levels", default="", help="comma-sep ratios (default r-grid)")
    pe.add_argument("--log-file", default="webtask.log")

    pi = sub.add_parser("import", help="import a filled task sheet")
    pi.add_argument("--system", required=True)
    pi.add_argument("--sheet", required=True, help="filled .md worksheet path")
    pi.add_argument("--out-dir", default="smoke/summaries")
    pi.add_argument("--tolerance", type=float, default=0.20)
    pi.add_argument("--operator", default="")
    pi.add_argument("--log-file", default="webtask.log")

    args = p.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(args.log_file, encoding="utf-8"),
        ],
    )

    if args.cmd == "export":
        n = export_sheet(
            args.system, args.texts_dir, args.out, levels=_parse_levels(args.levels)
        )
        print(f"Exported {n} tasks -> {args.out}")
        return 0
    if args.cmd == "import":
        recs = import_sheet(
            args.sheet,
            args.system,
            args.out_dir,
            tolerance=args.tolerance,
            operator=args.operator,
        )
        print(summary_report(recs))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
