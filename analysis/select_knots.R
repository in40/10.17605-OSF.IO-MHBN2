#!/usr/bin/env Rscript
# Pilot-time: choose the I-spline knot configuration by model comparison.
#
# Fits the threshold model for each candidate knot set per dimension and
# reports LOO / WAIC so the best (parsimonious + monotone + well-fit) config
# can be selected and FROZEN into the config.
#
# Usage: Rscript select_knots.R <fit_data.csv> <out_dir>

suppressPackageStartupMessages({
  library(brms); library(splines2); library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
data_path <- args[1]
out_dir   <- args[2]
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
dat <- read.csv(data_path, stringsAsFactors = TRUE)

# candidate knot configurations (edit to your pilot grid)
candidates <- list(
  c(0.3, 0.6),
  c(0.2, 0.5, 0.8),
  c(0.15, 0.35, 0.55, 0.75)
)
dims <- c("facts", "logic", "stance", "comprehension")

fit_one <- function(d, knots) {
  B <- as.data.frame(iSpline(d$level_r, knots = knots, outer_ok = TRUE))
  bcols <- paste0("B", seq_len(ncol(B))); names(B) <- bcols
  d <- cbind(d, B)
  f <- as.formula(paste0("pass | trials(m_d) ~ 0 + ",
                         paste(bcols, collapse = " + "),
                         " + (1|text_id) + (1|source) + (1|base_model)"))
  brm(f, data = d, family = binomial(link = "logit"),
      prior = c(set_prior("exponential(1)", class = "b"),
                set_prior("cauchy(0, 1)", class = "sd")),
      chains = 4, cores = 4, iter = 2000, warmup = 500,
      control = list(adapt_delta = 0.9), seed = 42)
}

report <- data.frame()
for (dim in dims) {
  d <- dat[dat$dimension == dim, ]
  if (nrow(d) == 0) next
  for (kn in candidates) {
    cat("dim=", dim, " knots=", paste(kn, collapse=","), "\n")
    fit <- tryCatch(fit_one(d, kn), error = function(e) { cat("  ERR:", conditionMessage(e), "\n"); NULL })
    if (is.null(fit)) next
    L <- loo(fit)
    W <- waic(fit)
    row <- data.frame(dimension = dim,
                     knots = paste(kn, collapse = ","),
                     elpd_loo = L$estimates["ELPD", 1],
                     se_loo = L$estimates["SE", 1],
                     waic = W$estimates["waic", 1])
    report <- rbind(report, row)
    cat(sprintf("  ELPD_loo=%.2f (SE %.2f)  WAIC=%.2f\n",
                row$elpd_loo, row$se_loo, row$waic))
  }
}
write.csv(report, file.path(out_dir, "knot_selection.csv"), row.names = FALSE)
cat("\nKnot selection report ->", file.path(out_dir, "knot_selection.csv"), "\n")
cat("Pick the config with best ELPD_loo that stays parsimonious, then FREEZE it.\n")
