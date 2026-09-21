## 2. Research Questions

**RQ1.** What is the minimum length ratio \(r_{\text{hol},i}^*\) at which holistic meaning-preservation remains ≥ \(\tau_{\text{hol}}\)?  
RQ1 is estimated on the 100 validation texts only, since holistic human ratings are collected only for those texts.

**RQ2a.** How large is the descriptive aggregate gap \(\Delta_{\text{all},i}\)?

**RQ2b.** Does signed conflict \(C_i^{\pm}\) predict the excess bottleneck \(\Delta_{\text{excess},i}\) beyond marginal difficulty?

**RQ3.** Do holistic thresholds and source-matched analytic aggregate thresholds coincide within practical equivalence?

**Target population:** Confirmatory genre set: news, scientific, procedural. Fiction and dialogue are descriptive. Validation texts are excluded from primary H2.

### RQ ↔ Hypothesis mapping

| Research question | Related hypothesis | Status |
|---|---|---|
| RQ1: Holistic threshold | H3 threshold estimation | Descriptive/secondary |
| RQ2a: Descriptive aggregate gap | None directly | Descriptive |
| RQ2b: Conflict predicts excess gap | H2 | Primary confirmatory |
| RQ3: Holistic vs analytic equivalence | H3 | Secondary confirmatory |
| — | H1 | Data integrity check |
| — | H4 | Exploratory |

---

## 3. Hypotheses

### H1 — Data Integrity Check

\[
r_{\text{all,raw},i}^* \ge \max_{d \in \text{core}} r_{d,\text{raw},i}^*
\]

**Raw threshold definitions:**

\[
r_{d,\text{raw},i}^* = \min \{ r : \exists S, Q_{d,i}(S) \ge \delta_d \}
\]

\[
r_{\text{all,raw},i}^* = \min \{ r : \exists S, Q_{d,i}(S) \ge \delta_d \ \forall d \}
\]

**Rules:**

- If no summary passes dimension \(d\), set \(r_{d,\text{raw},i}^* = +\infty\).
- If no summary passes all dimensions, set \(r_{\text{all,raw},i}^* = +\infty\).
- If any raw dimension threshold is undefined, the raw aggregate threshold must also be undefined. If \(r_{\text{all,raw},i}^*\) is finite while any raw dimension threshold is undefined, this is a coding error.
- Oracle excluded.
- Missing dimension scores are treated as non-passing for the raw check.

**Status:** Logical consequence. Violation = coding error. Not part of the confirmatory family.

---

### H2 — Primary Analytic Bottleneck, Confirmatory

**Model:**

\[
\Delta_{\text{excess},i} =
\beta_0
+
\beta_1 C_i^{\pm}
+
\beta_2 r_{\max,i}
+
\beta_3 \overline{p}_i
+
\beta_4 \text{tie}_i
+
\text{genre}_i
+
u_i
\]

where

\[
r_{\max,i} = \max_d r_{d,i}^*
\]

Genre will be coded using treatment contrasts with news as the reference category. The exact coding scheme will be recorded in the frozen configuration file.

The primary H2 point model will be fitted as a Gaussian linear model using ordinary least squares. Because \(\Delta_{\text{excess},i}\) is derived from grid-based thresholds and may be coarse or zero-inflated, OLS is used for interpretability. Primary confirmatory inference uses the permutation test and bootstrap practical-effect CI. HC3 robust standard errors will be reported descriptively only; they are not the confirmatory inferential engine. Robust regression, Tobit, and ordinal-threshold models are pre-specified sensitivity analyses.

**Definition of \(\overline{p}_i\):** Let

\[
d_{\max} = \arg\max_{d \in \text{core}} r_{d,i}^*
\]

Let

\[
d_{\text{non}} = \text{core} \setminus d_{\max}
\]

If \(d_{\text{non}}\) is non-empty:

\[
\overline{p}_i =
\frac{1}{|d_{\text{non}}|}
\sum_{d \in d_{\text{non}}}
\hat{P}(Q_{d,i} \ge \delta_d \mid r = r_{\max,i}, i)
\]

averaged over non-oracle sources.

If all dimensions tie for maximum, \(\overline{p}_i\) is computed as the mean pass probability across all core dimensions at \(r_{\max,i}\), and \(\text{tie}_i = 1\). Otherwise \(\text{tie}_i = 0\).

**One-sided test:**

\[
H_0: \beta_1 \le 0
\]

versus

\[
H_A: \beta_1 > 0
\]

H2 and H3 will be tested at a family-wise error rate of \(\alpha = 0.05\) using the Holm-Bonferroni procedure.

---

#### Primary signed conflict measure

The primary conflict predictor is a signed, margin-invariant negative log odds-ratio measure.

For each text \(i\), compression level \(r\), and dimension pair \((d,j)\), define the 2×2 table across non-oracle summaries:

| | \(j\) pass | \(j\) fail |
|---|---:|---:|
| \(d\) pass | \(a\) | \(b\) |
| \(d\) fail | \(c\) | \(e\) |

with \(n = a+b+c+e\).

The smoothed odds ratio is:

\[
OR_{ij}(r) =
\frac{(a+1)(e+1)}{(b+1)(c+1)}
\]

The pair-level signed conflict is:

\[
C_{ij}^{\pm}(r) = -\log OR_{ij}(r)
\]

Positive values indicate conflict/negative dependence. Negative values indicate synergy/positive dependence.

Pair-level signed conflict values are clipped to \([-3, 3]\). The clipping constant is frozen in the pilot configuration.

**Pair estimability:** \(n_{ijr} \ge 5\).

**Text-level signed conflict:**

\[
C_i^{\pm} =
\frac{
\sum_{r \in \mathcal{R}_i}
\sum_{(d,j) \in \mathcal{P}_i(r)}
n_{ijr} C_{ij}^{\pm}(r)
}{
\sum_{r \in \mathcal{R}_i}
\sum_{(d,j) \in \mathcal{P}_i(r)}
n_{ijr}
}
\]

where \(\mathcal{R}_i\) is the set of compression levels included in \(C_i^{\pm}\) for text \(i\), and \(\mathcal{P}_i(r)\) is the set of estimable dimension pairs at level \(r\).

If fewer than 50% of core pairs are estimable across all levels, \(C_i^{\pm}\) is undefined and the text is excluded from H2.

The descriptive nonnegative deficit conflict measure \(C_i^{+}\) is retained only as a sensitivity/descriptive measure:

\[
C_{ij}^{+}(r) =
\max\left(
0,
\frac{n p_d p_j - a}{n p_d p_j + 1}
\right)
\]

This measure is bounded below at zero and is not margin-invariant. It is not the primary predictor.

---

#### Primary practical-effect metric

The primary standardized practical-effect metric is:

\[
PE_{\text{IQR}} = \hat{\beta}_1 \cdot IQR(C_i^{\pm})
\]

where \(IQR(C_i^{\pm})\) is computed from the final primary H2 dataset after all inclusion/exclusion criteria have been applied.

The primary practical-effect criterion is:

\[
PE_{\text{IQR}} \ge 0.10
\]

This criterion is expressed in length-ratio units and represents the predicted change in the excess bottleneck associated with an interquartile-range increase in signed conflict. A change of 0.10 in \(\Delta_{\text{excess}}\) is treated as the primary practically meaningful threshold.

The practical-effect criterion is evaluable only if:

\[
IQR(C_i^{\pm}) \ge 0.05
\]

If \(IQR(C_i^{\pm}) < 0.05\), H2 is classified as inconclusive rather than supported.

For bootstrap and permutation inference, \(IQR(C_i^{\pm})\) is treated as a fixed constant computed from the final primary H2 dataset.

Sensitivity analyses will also report:

- the descriptive nonnegative conflict measure \(C_i^{+}\);
- a fixed 0.10 length-ratio practical-effect criterion applied to alternative standardizers;
- global marginal-difficulty covariates.

---

#### Primary H2 p-value

The primary confirmatory p-value for H2 is the one-sided permutation p-value for \(PE_{\text{IQR}}\):

\[
p_{\text{H2,perm}} =
\frac{
1 + \#\{PE_{\text{IQR}}^{(b)} \ge PE_{\text{IQR,obs}}\}
}{
B + 1
}
\]

The OLS model-based Wald p-value and the bootstrap p-value for \(\beta_1\) are reported descriptively but are not used as the primary confirmatory p-value.

---

#### H2 decision rule

H2 will be considered supported only if all of the following criteria are met.

1. The Holm-adjusted one-sided permutation p-value for \(PE_{\text{IQR}}\) is less than 0.05.

2. The lower bound of the one-sided 95% BCa bootstrap CI for \(PE_{\text{IQR}}\) is at least 0.10.

3. The key sensitivity checks both pass:

   - cross-fitted signed conflict \(C_i^{\pm}\);
   - source-adjusted signed conflict \(C_i^{\text{adj}}\).

   In each key sensitivity, \(\hat{\beta}_1 > 0\) and the one-sided 95% BCa bootstrap lower bound for \(\beta_1\) is greater than zero. If either key check fails, H2 is classified as inconclusive.

4. Additional robustness checks are reported:

   - exclusion of \(r=0.05\);
   - interpolated thresholds;
   - source fixed effects;
   - descriptive nonnegative conflict \(C_i^{+}\);
   - interval-censored sensitivity model;
   - global marginal-difficulty covariate.

   If criteria 1–3 pass but one or more additional robustness checks fail, H2 may be labeled **supported but specification-sensitive**. If criteria 1–3 fail, H2 is inconclusive or exploratory according to the downgrade rules.

---

#### Circularity safeguards

- **Primary \(C_i^{\pm}\):** computed from full non-oracle data, all 10 summaries per level.
- Because the primary conflict measure and the correlation structure used for \(\Delta_{\text{excess},i}\) are both derived from pass/fail dependence, the primary full-data H2 analysis is potentially susceptible to circularity.
- H2 is an association/model-consistency test, not a causal test. Confirmatory interpretation of H2 is conditional on the permutation test and the pre-specified key sensitivity checks.
- Therefore, confirmatory support for H2 requires that the following key sensitivity analyses remain directionally positive:
  - cross-fitted \(C_i^{\pm}\);
  - source-adjusted \(C_i^{\text{adj}}\).
- If full-data \(C_i^{\pm}\) supports H2 but either cross-fitted \(C_i^{\pm}\) or source-adjusted \(C_i^{\text{adj}}\) does not, H2 is classified as inconclusive.

---

#### Permutation null, explicit algorithm

For each text \(i\) and compression level \(r\):

1. Take the observed binary pass/fail matrix across the 10 non-oracle summaries and 4 dimensions.
2. For each dimension separately, randomly permute its binary vector across the 10 summaries.
3. This preserves the marginal number of passes for each dimension within that text × level.
4. It breaks the observed dependence between dimensions.
5. Recompute \(C_i^{\pm}\) from the permuted tables.
6. Use the permuted \(C_i^{\pm}\) values. Keep \(\Delta_{\text{excess},i}\), covariates, genre, and all threshold estimates fixed.
7. Refit the same H2 regression model using the permuted \(C_i^{\pm}\) values.
8. Compute the permutation practical-effect statistic using the observed \(IQR(C_i^{\pm})\):
   \[
   PE_{\text{IQR}}^{(b)} = \hat{\beta}_1^{(b)} \cdot IQR_{\text{obs}}(C_i^{\pm})
   \]
9. Repeat 1,000 times.

This null preserves marginal pass rates and breaks the association between \(C_i^{\pm}\) and \(\Delta_{\text{excess},i}\). The copula correlation structure is not held fixed during permutation, because permutation is intended to break dependence. Measurement models are not refit.

---

#### Interpretive note

\(C_i^{\pm}\) captures a mixture of within-summary semantic trade-offs and between-system specialization. H2 should be interpreted as testing whether negative dependence among pass/fail patterns predicts excess bottleneck, without claiming that this dependence is purely semantic. \(C_i^{\pm}\) is a pre-registered association measure, not a causal estimate.

---

#### Primary dataset and censoring

**Primary dataset:** As defined in §1.8. Validation texts excluded. Only confirmatory genres. Primary H2 uses only texts with finite thresholds. Censored texts are not in the primary dataset.

**Censoring rules:**

- The primary H2 analysis uses only texts with finite \(r_{\text{all,model},i}^*\) and finite \(r_{\text{all,ind},i}^*\).
- If \(r_{\text{all,model},i}^*\) or \(r_{\text{all,ind},i}^*\) does not reach 0.5 by \(r = 0.9\), it is treated as right-censored at 0.9.
- If it already reaches 0.5 at \(r = 0.05\), it is treated as left-censored at 0.05.
- An interval-censored sensitivity model will be fitted whenever computationally feasible, regardless of the observed censoring proportion.
- If more than 20% of otherwise eligible texts have any censored threshold required for \(\Delta_{\text{excess},i}\), the interval-censored sensitivity becomes a key robustness check.
- The interval-censored sensitivity model is considered to materially change inference if any of the following occur:
  1. the sign of \(\hat{\beta}_1\) reverses;
  2. the Holm-adjusted permutation p-value changes from significant to non-significant or vice versa;
  3. the practical-effect criterion changes from met to not met or vice versa;
  4. key sensitivity criterion 3 fails.
- If any of these occur, H2 will be classified as inconclusive or exploratory rather than supported.
- If more than 50% of otherwise eligible texts are censored, H2 is downgraded to exploratory.

---

#### Bootstrap

- 2,000 full-chain iterations.
- Stratified by genre.
- BCa CIs.
- Seed 42, with the frozen seed-stream scheme.
- Parallelized across 8 cores.

**Pre-specified compute budget and dry-run thresholds:** A bootstrap dry run on 20–50 texts will determine expected full-chain runtime. The full-chain bootstrap must complete with at least 1,000 valid iterations and failure rate ≤5% within the pre-specified compute budget. If the full-chain bootstrap cannot meet this standard, H2 is downgraded to exploratory. Approximate bootstrap, fixing measurement-model parameters, may be reported as sensitivity but cannot support confirmatory H2.

**Bootstrap dry run:** A bootstrap dry run will be performed on 20–50 texts before full confirmatory analysis. Monte Carlo error of bootstrap CIs will be reported. The computational burden of the text-level parametric SE bootstrap, 500 iterations, will also be tested during the bootstrap dry run. If infeasible, posterior-draw-based SE estimates will be used as a pre-specified fallback.

**Fallbacks:**  
- Fewer than 2 genres: H2 exploratory.  
- Fewer than 2 core dimensions: H2 and H3 exploratory.

---

### H3 — Holistic–Source-Matched Aggregate Equivalence, Secondary Confirmatory

#### Validation source assignment and replacement

For each validation text, one non-oracle source \(s_i\) is assigned before human rating collection. The assignment is balanced across sources and genres using blocked randomization with a frozen seed.

The assigned source must have valid summaries for all seven compression levels. Validity for this assignment decision is based only on:

- successful generation;
- archive/hash integrity;
- length deviation within the allowed rules;
- completion of the single allowed length-regeneration attempt.

No summary quality scores, pass/fail outcomes, LLM-judge scores, or human ratings may be inspected when deciding source replacement.

If the initially assigned source lacks a valid summary at any compression level, it is replaced by the eligible non-oracle source with the fewest current validation-text assignments within the same genre. If tied, the replacement source is selected using the frozen random seed.

If no eligible source has valid summaries for all seven compression levels, the validation text is replaced by a reserved validation text from the same genre. The replacement text is selected using the frozen random seed.

Source or text replacement must occur before human rating collection and before confirmatory threshold estimation. If a summary later fails due to LLM-judge refusal, parsing failure, or missing core scores, the text is excluded from primary H3 rather than replaced, unless the failure is documented as a technical processing error unrelated to content and replacement was approved before outcome inspection.

All replacements are logged in the decision log with: `text_id`; original source or text; replacement source or text; reason; stage of replacement; date; and confirmation that no outcome data were inspected.

---

#### Decision flow

1. Start with the 100 validation texts.
2. Estimate continuous \(r_{\text{hol},i}^*\) and continuous \(r_{\text{all,match},i}^*\).
3. Exclude texts with censored \(r_{\text{hol},i}^*\) or censored \(r_{\text{all,match},i}^*\).
4. Exclude texts where either \(SE(r_{\text{hol},i}^*) > 0.15\) or \(SE(r_{\text{all,match},i}^*) > 0.15\).
5. If fewer than 70 valid texts remain, H3 is downgraded to exploratory.
6. Apply the primary H3 SE filter.
7. If fewer than 70 texts remain, H3 is downgraded to exploratory.
8. Otherwise, proceed.

**Rule for 70–100 valid validation texts:** If fewer than 100 but at least 70 valid validation texts are obtained, H3 may proceed with the available validation texts, documented as a deviation. If fewer than 70 valid validation texts are obtained, H3 is downgraded to exploratory.

---

#### H3 SE filter and pilot retention rule

H3 is confirmatory conditional on pilot calibration. The primary equivalence margin is fixed in this registration. The primary H3 SE filter is not fixed to a single numeric value in this registration because it depends on pilot-based retention estimates. The filter will be frozen after the pilot dry-run according to the pre-specified rule and before confirmatory human data collection. No confirmatory H3 decision will be made before this freeze.

The planned primary H3 SE filter is:

\[
SE_i \le 0.05
\]

where \(SE_i = SE(r_{\text{hol},i}^* - r_{\text{all,match},i}^*)\) is estimated by paired bootstrap.

During the pilot dry-run, expected H3 retention under this filter will be estimated. The pilot will report expected retention under \(SE_i \le 0.05\), \(SE_i \le 0.075\), and \(SE_i \le 0.10\).

The primary H3 SE filter will be frozen after pilot as the strictest filter among these three that is projected to retain at least 70 valid validation texts.

If the pilot projects fewer than 70 valid texts even under \(SE_i \le 0.10\), then one of the following pre-data-collection actions will be taken:
1. increase the validation subset before confirmatory human data collection, subject to budget, participant capacity, and registered amendment; or
2. downgrade H3 to exploratory.

If, after confirmatory data collection, fewer than 70 valid validation texts remain under the frozen primary SE filter, H3 is downgraded to exploratory.

---

#### Hypotheses

Let

\[
D_i = r_{\text{hol},i}^* - r_{\text{all,match},i}^*
\]

where, for primary H3, both thresholds are model-interpolated continuous thresholds as defined in §7.1. Let \(\bar{D}\) be the mean paired difference.

\[
H_0: |\bar{D}| \ge \varepsilon
\]

versus

\[
H_1: |\bar{D}| < \varepsilon
\]

---

#### Equivalence margin

The primary population equivalence margin is fixed:

\[
\varepsilon = 0.10
\]

This corresponds to a maximum practically meaningful difference of 0.10 in the continuous length-ratio threshold between the holistic and source-matched analytic aggregate thresholds. The fixed margin is used to avoid making the primary equivalence criterion dependent on pilot-derived threshold estimates.

The following equivalence margins will be reported as sensitivity analyses:

1. conservative \(r_{\max,\text{match},i}\)-based margin:

\[
\varepsilon_i^{r_{\max}} =
\min(0.10, \max(0.01, 0.1 \cdot r_{\max,\text{match},i}))
\]

2. aggregate-threshold-based margin:

\[
\varepsilon_i^{\text{all}} =
\min(0.10, \max(0.01, 0.1 \cdot r_{\text{all,match},i}^*))
\]

Because primary H3 uses continuous interpolated thresholds, equivalence is not reduced to exact equality on the observed compression grid.

---

#### Standard error and bootstrap

The paired bootstrap directly estimates the SE of \(r_{\text{hol},i}^* - r_{\text{all,match},i}^*\) and is preferred.

An additive formula,

\[
SE_i = \sqrt{SE(r_{\text{hol},i}^*)^2 + SE(r_{\text{all,match},i}^*)^2}
\]

is used only when paired bootstrap is unavailable, and its independence assumption is reported. Covariance is estimated in the full-chain bootstrap when available.

---

#### TOST and primary decision

The TOST p-values are computed using the full-chain bootstrap distribution of \(\bar D\). The primary p-values are percentile bootstrap p-values:

\[
p_{\text{lower}} =
\frac{
1 + \sum_{b=1}^{B} I(\bar D^{*(b)} \le -\varepsilon)
}{
B+1
}
\]

\[
p_{\text{upper}} =
\frac{
1 + \sum_{b=1}^{B} I(\bar D^{*(b)} \ge +\varepsilon)
}{
B+1
}
\]

\[
p_{\text{H3}} = \max(p_{\text{lower}}, p_{\text{upper}})
\]

The raw \(p_{\text{H3}}\) is Holm-adjusted together with the H2 permutation p-value.

**Primary decision rule:** H3 equivalence will be considered supported only if BOTH:

1. the Holm-adjusted TOST p-value \(p_{\text{H3}}\) is less than 0.05; and  
2. the entire 95% BCa bootstrap CI for \(\bar{D}\) lies within \((-\varepsilon, +\varepsilon)\).

If only one criterion is met, H3 will be classified as inconclusive rather than supported.

---

#### Multiplicity and mixed nulls

H2 tests a directional association; H3 tests equivalence. Because these are different null structures, Holm-Bonferroni is applied to the confirmatory p-values to control family-wise error at 0.05. The bootstrap CI for H3 is a fixed practical consistency check and is not itself the multiplicity-adjustment device.

---

#### Full-chain bootstrap

The primary 95% BCa CI for \(\bar{D}\) is computed using the full-chain bootstrap, propagating uncertainty in both \(r_{\text{hol},i}^*\) and \(r_{\text{all,match},i}^*\).

If the full-chain bootstrap is computationally infeasible under the pre-specified compute budget, H3 is downgraded to exploratory. A text-level inverse-variance bootstrap may be reported as a sensitivity analysis but cannot support confirmatory equivalence.

---

#### Sensitivity analyses

- Observed-grid H3: compare grid-based \(r_{\text{hol},i,\text{grid}}^*\) with grid-based \(r_{\text{all,match},i,\text{grid}}^*\).
- Full-ensemble H3: compare continuous \(r_{\text{hol},i}^*\) with continuous full-ensemble \(r_{\text{all},i}^*\).
- Random-effects meta-analytic model: \(D_i \sim N(\mu, \tau^2 + SE_i^2)\). Report prediction interval for text-level differences. Population equivalence ≠ text-level equivalence.
- Conservative \(r_{\max,\text{match},i}\)-based equivalence margin.
- Aggregate-threshold-based equivalence margin.
- Source-effect sensitivity for holistic ratings, with the explicit identification limitation noted.
- Reduced-core H3, if the core dimension set is reduced after validation.
- Rater repetition sensitivity.

---

#### Reduced-core H3

If the core dimension set is reduced after validation, H3 based on the reduced-core aggregate threshold will be treated under the same confirmatory/exploratory rule as H2. If the reduced core is exploratory, H3 is also exploratory.

---

#### Note on SE filters

The H3 SE filter (e.g., \(SE_i \le 0.05\)) is stricter than the H2 stability filter (\(SE \le 0.15\)), because equivalence testing requires more precise estimates than regression-based association.

The H3 SE filter selects texts for which the paired difference between holistic and source-matched analytic thresholds can be estimated precisely. This may favor more typical or stable texts. The excluded texts will be described descriptively by genre, threshold distribution, and censoring status.

---

### H4 — Exploratory

Holistic threshold versus source-matched maximum core threshold. Direction and magnitude are exploratory. Human-evaluated subset only.

---

