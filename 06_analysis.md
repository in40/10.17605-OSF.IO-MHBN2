## 7. Analysis Plan

### 7.1 Threshold Estimation

**Model:** Hierarchical Bayesian with partial pooling. Threshold models will be fitted using Stan via brms in R. Custom Stan code will be used only if brms cannot accommodate the monotone spline basis or the required random-effects structure. Any use of custom Stan code will be documented in the pilot decision log before confirmatory analysis.

For binomial dimension models, the link function is logit:

\[
\text{logit}(\mu_{d,i,j,s}) =
\beta_{0d}
+
u_{0di}
+
f_d(r_{i,j}; b_d)
+
v_{ds}
+
v_{d,\text{base}(s)}
\]

- \(i\): text.
- \(s\): non-oracle summary source.
- \(j\): summary observation within text \(i\), source \(s\), and compression level \(r\).
- \(u_{0di}\): text-specific random intercept.
- \(f_d\): monotone spline with dimension-specific breakpoint \(b_d\), fixed in pilot.
- \(v_{ds}\): source random effect.
- \(v_{d,\text{base}(s)}\): base-model random effect for the base-model family of source \(s\).

**Monotonicity:** enforced within model via monotone spline basis, not post-hoc. The primary threshold model uses a monotone population-level function of \(r\) plus text-specific random intercepts. Text-specific random slopes are not used in the primary model. Random-slope models are reported as sensitivity analyses only, with a frozen isotonic projection applied if posterior text-specific curves are non-monotone.

---

#### Model families per dimension

| Dimension | Items \(m_d\) | Integer pass threshold \(k_d\) | Primary model | Pass probability |
|---|---:|---:|---|---|
| Facts | 10 | \(\lceil 10 \delta_{\text{facts}} \rceil\) | Binomial(10) | \(P(X \ge k_{\text{facts}})\) |
| Logic | 8 | \(\lceil 8 \delta_{\text{logic}} \rceil\) | Binomial(8) | \(P(X \ge k_{\text{logic}})\) |
| Stance | 5 | \(\lceil 5 \delta_{\text{stance}} \rceil\) | Binomial(5) | \(P(X \ge k_{\text{stance}})\) |
| Comprehension | 8 | \(\lceil 8 \delta_{\text{comprehension}} \rceil\) | Binomial(8) | \(P(X \ge k_{\text{comprehension}})\) |

The integer thresholds \(k_d\) are frozen after pilot. All primary analyses use \(k_d\). Sensitivity analyses use rounding alternatives and continuous beta-binomial models.

---

#### Sensitivity models

- Beta-binomial for overdispersion.
- Item-level random effects.
- Base-model random effect.

For beta-binomial sensitivity models, the outcome is modeled as the number of successes out of \(m_d\) trials; no proportion transformation is applied. No ordinal or zero-one-inflated beta model in primary analysis.

---

#### Priors

Weakly informative:
\(\beta_{0d} \sim N(0, 2)\), \(u_{0di} \sim N(0, \sigma_{0d})\), \(\sigma_{0d} \sim \text{Half-Cauchy}(0, 1)\), \(v_{ds} \sim N(0, \sigma_{sd})\), \(\sigma_{sd} \sim \text{Half-Cauchy}(0, 0.5)\), \(v_{d,\text{base}(s)} \sim N(0, \sigma_{bd})\), \(\sigma_{bd} \sim \text{Half-Cauchy}(0, 0.5)\).

Breakpoint: \(b_d \sim \text{Uniform}(0.1, 0.8)\) in pilot; fixed after pilot freeze.

All remaining fixed-effect coefficients receive weakly informative normal priors, \(N(0, 2)\), unless otherwise noted. All remaining scale parameters receive half-Cauchy priors, Half-Cauchy(0, 1), unless otherwise noted. Correlation matrices are regularized using LKJ or equivalent shrinkage priors, with exact specification frozen after pilot.

---

#### Convergence

- \(\hat{R} < 1.01\).
- Effective sample size > 400.
- No divergent transitions.

---

#### Convergence failure rules, pre-specified sequence

1. Increase warmup/iterations.
2. Increase adapt_delta.
3. Simplify the random-effects structure by replacing text-specific random intercepts with genre-level random intercepts, consistent with the random-intercept-only primary model.
4. Use penalized frequentist fallback: a logistic mixed-effects model with ridge regularization, implemented in glmmTMB with penalization, or an equivalent penalized logistic mixed-effects model, with the exact implementation frozen in the analysis configuration. If the penalized fallback cannot directly accommodate the monotone spline basis, predicted probabilities will be monotonized using the frozen isotonic projection rule before threshold extraction.
5. If still failing, mark text/dimension unstable and exclude from primary H2.

---

#### Boundary handling

For binomial models, exact 0/1 boundaries do not require transformation. For beta-binomial sensitivity, no proportion transformation is applied.

---

#### Threshold Extraction for H2 and H3

Two threshold estimators are pre-specified.

**A. Primary H2 thresholds: observed-grid thresholds**

For primary H2, model-based thresholds are extracted on the observed compression grid: \(r \in \{0.9, 0.7, 0.5, 0.3, 0.2, 0.1, 0.05\}\).

1. Compute predicted pass probabilities separately for each non-oracle source using posterior predictive draws with source-specific random effects.
2. Average predicted probabilities with equal weights across the 10 non-oracle sources for full-ensemble thresholds.
3. Primary observed-grid threshold = smallest observed \(r\) where probability ≥ 0.5, interval-censored.
4. Right-censored at 0.9 if never reaches 0.5.
5. Left-censored at 0.05 if ≥0.5 at \(r=0.05\).

For source-matched thresholds, use the source-specific predicted probabilities for the validation source \(s_i\), without averaging across sources.

Dimension thresholds and aggregate joint-probability thresholds are distinct. Dimension thresholds are extracted from marginal dimension models. Aggregate joint-probability thresholds are computed using the copula procedure in §7.2.

**B. Primary H3 thresholds: model-interpolated continuous thresholds**

For primary H3, thresholds are model-interpolated continuous thresholds. This is pre-specified because equivalence testing on a coarse grid can reduce equivalence to exact grid equality.

For any fitted monotone probability curve \(p(r)\), the continuous threshold is defined as the solution to \(p(r) = 0.5\) within the interval \([0.05, 0.9]\).

- If \(p(0.05) \ge 0.5\), the threshold is left-censored at 0.05.
- If \(p(0.9) < 0.5\), the threshold is right-censored at 0.9.
- If the fitted curve is flat over an interval containing 0.5, the threshold is the midpoint of that interval.

The interpolation/inversion procedure will be deterministic and frozen. If numerical non-monotonicity occurs, the frozen isotonic projection rule will be applied before inversion. If inversion still fails, the text is excluded from primary H3 and the failure is logged.

**C. Relationship between the two estimators**

In H3, unless explicitly marked with subscript `grid`, all threshold symbols refer to the model-interpolated continuous thresholds. The corresponding observed-grid versions are reported as sensitivity analyses.

For H2, the primary thresholds remain the observed-grid thresholds. Model-interpolated H2 thresholds are a pre-specified sensitivity analysis.

---

#### Text-level SEs

Parametric bootstrap, 500 iterations. Texts with \(SE(r_{d,i}^*) > 0.15\) for \(r_{\max,i}\) or \(r_{\text{all},i}^*\) are excluded from primary H2.

For primary H3, texts with \(SE(r_{\text{hol},i}^*) > 0.15\) or \(SE(r_{\text{all,match},i}^*) > 0.15\) are excluded before applying the paired H3 SE filter.

If the parametric bootstrap is infeasible under the dry-run budget, posterior-draw-based SE estimates will be used as a pre-specified fallback.

**Software:** Stan via brms in R. Custom Stan for copula simulation if required and documented in the pilot decision log. Versions frozen. Analysis code tested on simulated data and frozen.

---

### 7.2 Aggregate Threshold and Independence Baseline

#### Full-ensemble latent-threshold algorithm

For each text \(i\), level \(r\), source \(s\):

1. Fit marginal models and obtain pass probabilities \(p_{d,i,s}(r)\).
2. Clip probabilities: \(p_{d,i,s}^{\text{clip}}(r) = \text{clip}(p_{d,i,s}(r), \epsilon_{\text{clip}}, 1 - \epsilon_{\text{clip}})\) with \(\epsilon_{\text{clip}} = \frac{1}{4 m_d}\) per dimension.
3. Define latent thresholds: \(t_{d,i,s}(r) = \Phi^{-1}(1 - p_{d,i,s}^{\text{clip}}(r))\).
4. Estimate text-specific latent Gaussian copula correlation matrices \(\mathbf{R}_i\), with hierarchical shrinkage toward the corresponding genre-level correlation matrix \(\mathbf{R}_{\text{genre}(i)}\). Correlations are estimated on the latent probit scale, using tetrachoric/polychoric correlations or pseudo-likelihood Gaussian-copula estimation where feasible, after accounting for compression level, source effects, and dimension-specific marginal probabilities. The estimator, shrinkage prior, approximation assumptions, and fallback rules are frozen after pilot.
5. Draw 2,000 latent multivariate-normal draws: \(Z \sim N(0, \mathbf{R}_i)\) per text × compression level. Source-specific thresholds are then applied to the same latent draws to obtain source-specific joint pass probabilities. Shared latent draws across sources are used as a variance-reduction device.
6. Set: \(Y_d = 1\) if \(Z_d > t_{d,i,s}(r)\).
7. Joint pass probability = simulated proportion of draws where all \(Y_d = 1\).
8. For full-ensemble thresholds, average joint pass probabilities across the 10 non-oracle sources.
9. Threshold: \(r_{\text{all,model},i}^* = \min \{ r : \overline{P}_{\text{all}}(r,i) \ge 0.5 \}\).

For source-matched thresholds, use only the joint pass probability for source \(s_i\): \(r_{\text{all,match},i}^* = \min \{ r : P_{\text{all},s_i}(r,i) \ge 0.5 \}\).

**Source-invariant copula assumption:** The primary copula model assumes a source-invariant dependence structure within text \(i\): the same correlation matrix \(\mathbf{R}_i\) is applied to all non-oracle sources. Source-specific joint pass probabilities differ because source-specific marginal probabilities differ, not because source-specific correlation matrices are used in the primary model. A source-specific or genre×source copula sensitivity will be reported if computationally feasible.

---

#### Minimum-information rule for correlation matrices

If the text-specific correlation estimate is based on fewer than 20 valid summary-level pass/fail observations after residualization, the text will use the genre-level correlation matrix. If the genre-level matrix is also non-positive-definite or unstable, the text will be excluded from aggregate-threshold estimation and reported in the exclusion log.

---

#### Model-consistency check

Theoretically, \(P(\text{all pass}) \le P(d \text{ pass})\) for each \(d\), so \(r_{\text{all},i}^* \ge r_{\max,i}\) should hold. Due to estimation error, copula approximation, and numerical issues, this may be violated.

Any text with \(r_{\text{all,model},i}^* < r_{\max,i} - \eta\) is flagged. The tolerance \(\eta = 0.01\) is fixed in the frozen configuration file. Flagged texts are excluded from primary H2 or analyzed in a sensitivity model with constrained thresholds.

The same consistency check is applied to source-matched thresholds: \(r_{\text{all,match},i}^* \ge r_{\max,\text{match},i} - \eta\). Violations are logged and handled by the same rule.

---

#### Positive-definiteness

If a correlation matrix is not positive definite, apply nearest positive-definite projection using the Higham algorithm or eigenvalue clipping with a minimum eigenvalue of \(10^{-6}\), as frozen in the pilot configuration. If projection fails, fall back to genre-level \(\mathbf{R}_{\text{genre}(i)}\) for that text. If that fails, exclude the text from aggregate-threshold analysis and report the exclusion reason. Simulation failures are recorded and reported.

---

#### Independence baseline

Source-conditioned. For each non-oracle source \(s\):

\[
P_{\text{ind},s}(\text{all pass} \mid r, i) = \prod_{d \in \text{core}} p_{d,i,s}(r)
\]

Average across sources:

\[
\overline{P}_{\text{ind}}(\text{all pass} \mid r, i) = \frac{1}{10} \sum_{s=1}^{10} P_{\text{ind},s}
\]

Threshold: \(r_{\text{all,ind},i}^* = \min \{ r : \overline{P}_{\text{ind}} \ge 0.5 \}\).

If \(\overline{P}_{\text{ind}}\) does not reach 0.5 by \(r = 0.9\), \(r_{\text{all,ind},i}^*\) is right-censored at 0.9 and excluded from the primary finite-threshold H2 analysis. If it reaches 0.5 at \(r = 0.05\), it is left-censored at 0.05. Censored baselines are handled in the interval-censored sensitivity analysis.

**Note:** The independence baseline is a counterfactual reference that assumes no residual dependence among dimensions after conditioning on source. Positive dependence among dimensions will generally make the dependent aggregate threshold smaller than the independence threshold, producing negative \(\Delta_{\text{excess}}\); negative dependence will produce positive \(\Delta_{\text{excess}}\). \(\Delta_{\text{excess},i}\) is a model-based excess relative to conditional independence, not a direct empirical quantity.

---

### 7.3 Holistic Threshold

Holistic ratings are made on a 1–5 Likert scale. The primary dichotomization is: ratings 4–5 = "yes"; ratings 1–3 = "no". A sensitivity analysis uses 5-only = "yes".

The holistic question is: *"Передаёт ли данное резюме смысл исходного текста?"* ("Does this summary convey the meaning of the original text?"). The exact wording and response anchors will be frozen.

**Model:**

\[
\text{logit}(P(\text{"yes"})) = f_{\text{hol}}(r) + \text{genre} + (1 \mid \text{text}) + (1 \mid \text{evaluator}) + (1 \mid \text{text:level})
\]

Because there is one rated summary per validation text × compression level, the summary-level random intercept is represented by \((1 \mid \text{text:level})\).

**Sensitivity:** ordinal cumulative-link model; 5-only = "yes"; source effect sensitivity, with the explicit identification limitation noted in §3 H3.

---

### 7.4 Conflict Measures

#### Primary signed conflict \(C_i^{\pm}\)

The primary conflict predictor is the signed negative log odds-ratio measure defined in §3 H2.

Interpretation:

- \(C_{ij}^{\pm}(r) > 0\): conflict/negative dependence;
- \(C_{ij}^{\pm}(r) = 0\): independence under the smoothed odds ratio;
- \(C_{ij}^{\pm}(r) < 0\): synergy/positive dependence.

This measure is signed and margin-invariant under the odds-ratio parameterization.

---

#### Source-adjusted signed conflict

The source-adjusted signed conflict measure \(C_i^{\text{adj}}\) is a key sensitivity analysis intended to remove global source and compression-level effects from pass/fail dependence.

The primary planned algorithm is:

1. For each core dimension \(d\), fit a linear probability model to non-oracle pass indicators in the primary analysis dataset:

\[
\text{Pass}_{d,i,s,r} = \alpha_0 + \alpha_s + \alpha_r + \alpha_{\text{genre}(i)} + \varepsilon^{\text{LPM}}
\]

where summary source \(s\) and target length ratio \(r\) are treated as categorical fixed effects, and genre is included as a fixed effect.

2. Extract residuals \(e_{d,i,s,r}\).

3. For each text \(i\) and dimension pair \((d,j)\), compute the Pearson correlation \(\rho_{ij}\) of residuals \(e_d\) and \(e_j\) across all non-missing summary-level observations for that pair within text \(i\).

4. Pairwise source-adjusted signed conflict is:

\[
C_{ij}^{\text{adj}} = -\rho_{ij}
\]

5. Text-level \(C_i^{\text{adj}}\) is the weighted average of estimable pairwise signed conflicts, weighted by the number of pairwise non-missing residual observations.

6. A pair is estimable if it has at least 20 pairwise non-missing residual observations. If fewer than 50% of core pairs are estimable, \(C_i^{\text{adj}}\) is undefined.

The exact residualization implementation, handling of zero-variance pairs, and fallback rules will be frozen in the pilot decision log before confirmatory analysis. If \(C_i^{\text{adj}}\) cannot be computed reliably in pilot, H2 will be treated as inconclusive under the key-sensitivity rule or downgraded to exploratory, depending on the frozen pilot decision.

If full-data \(C_i^{\pm}\) supports H2 but source-adjusted \(C_i^{\text{adj}}\) does not, H2 is classified as inconclusive.

---

#### Cross-fitted signed conflict

Cross-fitted \(C_i^{\pm}\) is computed by split-half resampling within each text and compression level. For each text \(i\) and level \(r\), the 10 non-oracle summaries are randomly divided into two halves of five summaries using the frozen seed stream. A split-specific signed conflict measure is computed for each half using the same signed negative log odds-ratio formula, with the minimum number of summaries per pair reduced from five to three for split-half estimability. The cross-fitted text-level conflict is the average of the two split-specific conflict estimates. If either half has fewer than 50% estimable core pairs, cross-fitted \(C_i^{\pm}\) is undefined.

---

#### \(n\)-dependence

Signed log odds ratios can still be unstable at small \(n\). The clipping rule and estimability thresholds are intended to reduce small-sample instability. If some text × level cells have \(n=10\) and others have \(n=5\) or \(n=6\), \(C_i^{\pm}\) may still be affected by the number of valid summaries. This is tested via sensitivity metrics.

---

#### Interpretation

\(C_i^{\pm}\) measures signed dependence in pass/fail patterns across summaries. This reflects a mixture of within-summary semantic trade-offs and between-system specialization. \(C_i^{\pm}\) is a pre-registered association measure, not a causal estimate.

---

#### Validation

In pilot, validate \(C_i^{\pm}\) recovery on simulated data with known conflict structure.

---

#### Sensitivity: alternative conflict measures

- Descriptive nonnegative deficit conflict \(C_i^{+}\).
- Margin-adjusted deficit conflict.
- Negative tetrachoric correlation.
- Negative Matthews correlation coefficient.
- Residual negative correlation after adjusting for source and level.
- Level-stratified conflict summaries.
- Exploratory split-half circularity sensitivity, where feasible, in which \(C_i^{\pm}\) and the correlation structure used for \(\Delta_{\text{excess},i}\) are estimated from non-overlapping halves of the non-oracle summaries.

---

### 7.5 Inference Criteria

- \(\alpha = 0.05\) family-wise.
- Confirmatory family: H2 and H3 only.
- H2 primary p-value: permutation p-value for \(PE_{\text{IQR}}\).
- H3 primary p-value: TOST percentile bootstrap p-value.
- Holm-Bonferroni applied to the H2 permutation p-value and H3 TOST p-value.
- H1: data-integrity check, not in family.
- H4, auxiliary dimensions, oracle, genre/source interactions, full-ensemble H3 comparison, observed-grid H3 comparison, and all sensitivity analyses: exploratory.
- If H3 is not informative/downgraded, family = {H2 only}.

Holm procedure: raw p-values in the confirmatory family are ordered from smallest to largest and compared sequentially to \(\alpha/m\), \(\alpha/(m-1)\), etc., where \(m\) is the number of p-values in the confirmatory family.

Because H2 tests a directional association and H3 tests equivalence, the two hypotheses involve different null structures. Holm-Bonferroni is applied to the confirmatory p-values to control family-wise error at 0.05. The bootstrap CI for H3 is a fixed practical consistency check and is not itself the multiplicity-adjustment device.

---

### 7.6 Inter-Rater Reliability

**Design:** One summary per validation text × compression level item. All raters for a given item rate the same summary.

**Estimator:** Because raters are randomly assigned to items, Fleiss' κ and Gwet's AC1 will be reported as descriptive chance-corrected agreement indices for dichotomized holistic ratings. The primary reliability estimate for holistic ratings will be obtained from a mixed-effects logistic model with random intercepts for item and rater.

For analytic ratings, dimension-specific mixed models will be used to estimate absolute-agreement ICCs with rater and text/item random effects.

**Thresholds:**
- Holistic: Fleiss' κ ≥ 0.6, dichotomized ratings. Also report Gwet's AC1.
- Analytic: absolute-agreement ICC ≥ 0.7 per dimension. Also report Krippendorff's α.

For analytic validation, the ICC type will be specified in the frozen analysis configuration as an absolute-agreement ICC appropriate for the rating design. Where conventional notation applies, ICC(A,1) or ICC(3,1) will be used for agreement between the LLM-judge score and the mean human analytic score, with the exact model frozen before validation.

**Note on κ variants:** Cohen's κ is used for LLM-human pass/fail agreement in §8.2. Fleiss' κ, Cohen-type κ, and Gwet's AC1 in this section refer to human rater agreement, not LLM-human agreement.

---

### 7.7 Data Exclusion

**Evaluators:**
- >1 failed attention check in a session → excluded from that session.
- A participant is excluded from further participation if two or more sessions fail attention checks.

**Summaries:** per length deviation rules.

**Texts:** >30% invalid summaries → excluded.

**Invalid summary:** length deviation >30%, judge refusal, parsing failure, or missing core scores.

The valid main-corpus text definition in §4.5 is the collection-level stopping rule. The exclusion rules in this section are applied during analysis. A text must satisfy both the §4.5 validity criteria and the analysis exclusion rules to be included in primary analyses. If the rules conflict, the stricter rule applies.

Exclusion rates reported by genre, source, level.

No additional manual outlier removal will be performed unless documented as a registered amendment.

---

### 7.8 Missing Data

- MAR handled by mixed models where appropriate.
- If >5% of summary-level auxiliary variables are missing, MICE with \(m=20\) may be used.
- MICE will be used only for missing summary-level covariates or auxiliary variables.
- Core dimension scores, thresholds, and censored estimands will not be imputed for primary analysis.
- Any imputation of core dimension scores is exploratory and will not affect primary confirmatory conclusions.
- Undefined \(C_i^{\pm}\): excluded from H2.
- If missingness exceeds 5% in core dimension scores, sensitivity analyses will compare complete-case, model-based missingness assumptions, and exploratory imputation scenarios.

---

### 7.9 Sensitivity Analyses

#### Key confirmatory sensitivities

1. Cross-fitted signed conflict \(C_i^{\pm}\).
2. Source-adjusted signed conflict \(C_i^{\text{adj}}\).

#### Secondary robustness sensitivities

3. Exclude \(r = 0.05\).
4. Interpolated thresholds for H2.
5. Source fixed effects.
6. Interval-censored H2 model.
7. Global marginal-difficulty covariate in H2.
8. Descriptive nonnegative conflict \(C_i^{+}\).
9. Margin-adjusted deficit conflict.
10. Level-stratified conflict summaries.
11. Robust regression for H2.
12. Tobit or ordinal-threshold H2 models.
13. Source-specific or genre×source copula sensitivity, if computationally feasible.
14. H3 conservative \(r_{\max}\)-based equivalence margin.
15. H3 aggregate-threshold-based equivalence margin.
16. Observed-grid H3 comparison.
17. Full-ensemble H3 comparison.
18. Length-deviation sensitivity band summaries.
19. Chance-corrected comprehension score.
20. Stance neutral omission treated as neutral.
21. Thresholds at 0.6/0.7.
22. Include validation texts in H2.

#### Exploratory sensitivities

23. Oracle analyses.
24. Auxiliary dimensions.
25. Genre/source interactions.
26. Exclude one genre/source at a time.
27. Random-slope threshold model with isotonic projection.
28. Holistic source effect sensitivity.
29. Rater repetition sensitivity for H3.
30. Judge replacement bridge comparison, if applicable.
31. Summarizer replacement bridge comparison, if applicable.
32. Reduced-core H2/H3, if applicable.
33. Split-half circularity sensitivity with separated conflict and correlation estimation, if feasible.

---

