## 10. Pilot

### 10.1 Design

45–60 texts, 15–20 per confirmatory genre: \(45\text{–}60 \times 7 \times 11 = 3{,}465\text{–}4{,}620\) summaries.

The pilot focuses on the three confirmatory genres. Fiction and dialogue are not used for confirmatory genre exclusion and remain exploratory by design.

Pilot texts are excluded from the main corpus.

A separate 10-text technical smoke test may be conducted to verify pipelines, APIs, hashing, and storage. The smoke test is not the registered pilot and is not used for calibration or confirmatory decisions.

---

### 10.2 Goals

1. Calibrate \(\delta_d\) and integer thresholds \(k_d\).
2. Estimate threshold SEs and expected H3 retention.
3. Estimate distributional summaries of \(C_i^{\pm}\), including \(IQR(C_i^{\pm})\).
4. Check instructions and estimate rating time.
5. Check agreement, Fleiss' κ and ICC.
6. Fix breakpoint \(b_d\).
7. Assess dimension independence.
8. Validate threshold recovery on simulated data.
9. Validate \(C_i^{\pm}\) recovery on simulated data.
10. Validate the implementation and stability of source-adjusted \(C_i^{\text{adj}}\).
11. Estimate the power and stability of the cross-fitted signed conflict check.
12. Estimate the power and stability of the source-adjusted signed conflict check.
13. Estimate the cumulative probability that H2 and H3 remain confirmatory after all pre-specified rules.
14. Pilot-based power analysis.
15. Estimate exclusion rates, human rating time, LLM-human agreement, conflict measure stability.
16. Estimate feasibility of source-matched thresholds for H3.
17. Freeze the minimum valid confirmatory-genre sample size required for H2, not below 180.
18. Determine the primary H3 SE filter threshold based on expected retention.

---

### 10.3 Calibration of \(\delta_d\)

5 experts per dimension: PhD students/faculty in NLP/linguistics, native Russian speakers. Experts are independent from the research team, paid for their time, and blind to \(Q_d\) during rating.

Experts provide independent preserved/not-preserved judgments for 20 summaries covering all compression levels. The calibration model uses these independent judgments only.

The primary calibration model is a logistic model of expert judgment on the LLM-judge dimension score \(Q_d\), with a random intercept for expert where convergence permits:

\[
\text{logit}(P(\text{preserved})) =
\alpha_0 + \alpha_1 Q_d + (1 \mid \text{expert})
\]

If the random-effects model fails to converge, a pooled logistic model will be used. The dimension-specific pass criterion \(\delta_d\) is the value of \(Q_d\) at which the predicted probability of expert "preserved" equals 0.5.

The integer pass threshold \(k_d = \lceil m_d \delta_d \rceil\) is also frozen.

Calibration must be stable across bootstrap resamples, \(SE < 0.05\). If unstable or curve does not cross 0.5: dimension non-calibratable → excluded from core.

Consensus discussion among experts is used only for item acceptance/rejection and item-quality validation. Consensus is not used to alter independent calibration ratings used for \(\delta_d\) estimation.

---

### 10.4 Pilot Freeze

Frozen:
- \(\delta_d\);
- integer thresholds \(k_d\);
- breakpoint \(b_d\);
- validation criteria and decision thresholds;
- genre exclusion decisions;
- fallback rules;
- distributional summaries of \(C_i^{\pm}\) used for fallback rules;
- correlation estimator and shrinkage parameters;
- latent-scale correlation estimation rule;
- monotone spline basis, knots, degrees;
- monotonicity enforcement rule;
- holistic dichotomization rule;
- human rating anchors;
- item-generation pipeline hash;
- item-generation manifest hashes;
- power simulation parameters;
- minimum valid confirmatory-genre sample size for H2, not below 180;
- primary H3 SE filter threshold;
- bootstrap procedure;
- code version hash;
- model-consistency tolerance \(\eta\);
- copula clipping constant \(\epsilon_{\text{clip}}\);
- signed conflict clipping constant;
- seed-stream scheme;
- ICC model for validation;
- human analytic pass/fail rule: mean human rating ≥ 3.5 = pass, mean < 3.5 = fail;
- judge bridge validation rule, if applicable;
- summarizer bridge validation rule, if applicable;
- primary H2 OLS specification;
- permutation p-value computation rule;
- TOST percentile p-value computation rule;
- source-adjusted \(C_i^{\text{adj}}\) residualization algorithm;
- cross-fitted \(C_i^{\pm}\) split rule;
- permutation/bootstrap standardization rule;
- model-name/checkpoint mapping table;
- ethics approval number and approval date.

**Signed decision log:** date, values, decisions, deviations, code hash.

All deferred analysis choices listed in this registration will be finalized in a frozen configuration file before confirmatory data analysis. The frozen configuration file will include parameter values, decision rules, estimator specifications, seed-stream scheme, code version hash, model checkpoint identifiers, and a signed decision log. No confirmatory inferential decisions will be made after inspection of confirmatory outcomes.

---

