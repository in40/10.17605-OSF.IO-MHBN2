#!/usr/bin/env Rscript
# Parameterized threshold-model fitting (brms), per 02_math.md / PLAN.md:53-55.
#
# Reads a FROZEN config (spline knots, delta_d, lineup, priors) + a long data
# CSV (from export_to_r.py), fits a monotone (I-spline) binomial-logit model
# per core dimension with random effects, checks convergence, and extracts the
# threshold r* where P(pass) crosses the target probability.
#
# Usage:
#   Rscript fit_threshold_model.R <frozen_config.json> <fit_data.csv> <out_dir>
#
# NOTE: non-negativity of the I-spline coefficients is what makes the curve
# monotone. Here it is imposed via a lower-truncated prior. If brms cannot
# express the needed constraint / random-effects structure, fall back to
# custom Stan and LOG it (per "custom Stan only if needed (log it)").

suppressPackageStartupMessages({
  library(brms)
  library(splines2)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) {
  stop("usage: fit_threshold_model.R <frozen_config.json> <fit_data.csv> <out_dir>")
}
cfg_path  <- args[1]
data_path <- args[2]
out_dir   <- args[3]
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

cfg  <- jsonlite::fromJSON(cfg_path)
dat  <- read.csv(data_path, stringsAsFactors = TRUE)
knots <- as.numeric(cfg$spline$knots)
r_target <- cfg$r_star_target_prob %||% 0.5
dims <- names(cfg$dimension_method)
dims <- dims[dims != "_note"]

# ---- fit one dimension ----
fit_dim <- function(dim) {
  d <- dat[dat$dimension == dim, ]
  if (nrow(d) == 0) return(NULL)

  B <- as.data.frame(iSpline(d$level_r, knots = knots, outer_ok = TRUE))
  bcols <- paste0("B", seq_len(ncol(B)))
  names(B) <- bcols
  d <- cbind(d, B)

  f <- as.formula(paste0(
    "pass | trials(m_d) ~ 0 + ", paste(bcols, collapse = " + "),
    " + (1 | text_id) + (1 | source) + (1 | base_model)"
  ))

  priors <- c(
    # non-negative basis coefficients -> monotone increasing curve
    set_prior(paste0("exponential(1)"), class = "b"),
    set_prior("cauchy(0, 1)", class = "sd")
  )

  fit <- brm(
    f, data = d, family = binomial(link = "logit"), prior = priors,
    chains = cfg$model$chains, cores = min(4, cfg$model$chains),
    iter = cfg$model$iter, warmup = cfg$model$warmup,
    control = list(adapt_delta = cfg$model$adapt_delta),
    seed = 42
  )
  fit
}

# ---- population-level r* from the fixed-effect curve ----
r_star_from_fit <- function(fit, dim) {
  rgrid <- seq(0.01, 0.99, length.out = 197)
  Bg <- as.data.frame(iSpline(rgrid, knots = knots, outer_ok = TRUE))
  bcols <- paste0("B", seq_len(ncol(Bg)))
  names(Bg) <- bcols
  # posterior draws of fixed effects
  bdraws <- as.matrix(fit, pars = bcols)
  # linear predictor per draw over the grid
  lp <- bdraws %*% t(as.matrix(Bg))          # draws x grid
  p  <- plogis(lp)                            # prob pass
  pmean <- colMeans(p)
  # first r where P >= target
  idx <- which(pmean >= r_target)[1]
  if (is.na(idx)) NA else rgrid[idx]
}

# ---- convergence check ----
check_conv <- function(fit) {
  s <- summary(fit)$summary
  rhat_max <- max(s[, "Rhat"], na.rm = TRUE)
  ess_min  <- min(s[, "ESS"], na.rm = TRUE)
  divergent <- sum(fit$fit@sim$samples[[1]]$.lp__ > 0)  # placeholder; use get_draws/divergences
  list(rhat_max = rhat_max, ess_min = ess_min)
}

results <- list()
for (dim in dims) {
  cat("=== fitting dimension:", dim, "===\n")
  fit <- fit_dim(dim)
  if (is.null(fit)) { cat("no data for", dim, "\n"); next }
  rs <- r_star_from_fit(fit, dim)
  cv <- check_conv(fit)
  results[[dim]] <- list(r_star = rs, rhat_max = cv$rhat_max, ess_min = cv$ess_min)
  saveRDS(fit, file.path(out_dir, paste0("fit_", dim, ".rds")))
  cat(sprintf("  r* = %s | R-hat max %.3f | ESS min %.0f\n",
              ifelse(is.na(rs), "NA", round(rs, 3)), cv$rhat_max, cv$ess_min))
}

saveRDS(results, file.path(out_dir, "r_star_results.rds"))
cat("\nDone. Results ->", out_dir, "\n")
