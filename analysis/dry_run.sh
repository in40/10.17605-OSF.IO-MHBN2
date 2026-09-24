#!/usr/bin/env bash
# Dry-run of the fitting pipeline on a small slice, BEFORE confirmatory scoring.
# Per PLAN.md:56 — "Bootstrap dry-run (20-50 texts) BEFORE confirmatory scoring;
# document runtime." Purpose: verify brms can impose the non-negative I-spline
# constraint + RE structure (else custom-Stan is needed), and measure runtime.
#
# Usage: ./analysis/dry_run.sh [summaries_dir] [texts_dir]
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PY:-.venv/bin/python}"
SUMM="${1:-smoke/summaries}"
TEXTS="${2:-smoke/texts}"
CFG="analysis/frozen_config.example.json"
OUT="/tmp/analysis_dryrun"
mkdir -p "$OUT"

echo "=== 1. Export scored data -> CSV ==="
"$PY" analysis/export_to_r.py \
    --summaries-dir "$SUMM" --config "$CFG" \
    --out "$OUT/fit_data.csv" --texts-dir "$TEXTS"

echo "=== 2. Fit threshold model (tests brms non-negativity + RE) ==="
Rscript analysis/fit_threshold_model.R "$CFG" "$OUT/fit_data.csv" "$OUT/fit"

echo "=== 3. Knot selection (LOO/WAIC) ==="
Rscript analysis/select_knots.R "$OUT/fit_data.csv" "$OUT/knots"

echo
echo "Done. Inspect $OUT:"
echo "  - fit_data.csv        (long dataframe for R)"
echo "  - fit/*.rds           (brms fits + r_star_results.rds)"
echo "  - knots/knot_selection.csv  (which knots win)"
echo
echo "If brms errored on the non-negative constraint or RE structure ->"
echo "custom-Stan is required (and must be logged per the registration)."
