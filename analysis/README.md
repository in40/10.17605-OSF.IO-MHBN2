# Analysis — threshold-model fitting (06_analysis)

Parameterized fitting of the registered hierarchical Bayesian threshold model
(`02_math.md`, `PLAN.md:53-55`). Code is written now; the **values** (knots,
δ_d, lineup) are produced + frozen in the pilot.

## Components

- **`frozen_config.example.json`** — the FROZEN config contract: spline type +
  knots, per-dimension `delta_d`, dimension→method map, lineup (source→base_model),
  priors, convergence thresholds. The pilot fills the values; the main phase reads them.
- **`export_to_r.py`** — Python→R export. Walks the summaries tree
  (`<summaries>/<system>/<text>/<level>/summary_*.qa.json`) and emits a long CSV:
  `text_id, genre, source, base_model, level_r, dimension, pass, m_d`.
  Dimensions: facts←qa, logic←nli, stance←stance, comprehension←mcq.
- **`fit_threshold_model.R`** — brms fit per dimension: I-spline basis (monotone
  via non-negative coefficients) + RE (text, source, base_model), `binomial(logit)`,
  outcome `pass | trials(m_d)`. Checks convergence, extracts `r*` (where P crosses 0.5).
- **`select_knots.R`** — pilot-time knot selection: fits candidate knot sets,
  reports LOO/WAIC so the best parsimonious monotone config is chosen + frozen.
- **`dry_run.sh`** — runs export + a quick fit + knot selection on a small slice
  (per `PLAN.md:56`), to verify brms can impose the constraint + measure runtime.

## Workflow

1. **Now:** code + config schema exist.
2. **Pilot:** run `select_knots.R` → pick knots; calibrate `delta_d`; write both
   into the FROZEN config (+ hash). Run `dry_run.sh` to confirm brms-vs-custom-Stan.
3. **Main:** `export_to_r.py` → `fit_threshold_model.R` reading the frozen config.

## Key facts

- **I-spline is compliant:** the registration says generic "monotone spline"
  (`PLAN.md:53`), not I-spline specifically → I-spline satisfies it, **no amendment**.
- **Non-negativity = monotonicity:** the I-spline curve is monotone only if the
  coefficients are ≥ 0; imposed via a truncated/exponential prior in brms.
- **Custom Stan only if needed (log it):** if brms can't express the constraint or
  the RE structure, write custom Stan and document it.
- **Oracle excluded:** `role=oracle` sources are excluded from all primary estimators.

## Requirements (R side)

R 4.x + Rtools/Xcode/build-essential + `rstan`, `brms`, `splines2`, `jsonlite`.
See the install steps in the shared setup notes.
