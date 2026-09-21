### 1.3 Notation

| Symbol | Definition | Role | Interpretation |
|---|---|---|---|
| \(T\) | Original text | — | — |
| \(S\) | Summary | — | — |
| \(r = |S| / |T|\) | Summary length ratio, using whitespace tokenization | — | Smaller = stronger compression |
| \(m_d\) | Number of items for dimension \(d\) | — | 10, 8, 5, 8 |
| \(k_d\) | Integer pass threshold for dimension \(d\) | Frozen | \(k_d = \lceil m_d \delta_d \rceil\) |
| \(s_i\) | Rated non-oracle summary source for validation text \(i\) | H3 | Fixed per validation text |
| \(r_{d,i}^*\) | Text-specific full-ensemble threshold for dimension \(d\), text \(i\) | Core estimand | Smallest \(r\) where dimension \(d\) is preserved with probability ≥ 0.5 |
| \(r_d^*\) | Population-level threshold for dimension \(d\) | Descriptive | — |
| \(r_{\text{hol},i}^*\) | Holistic threshold for validation text \(i\), rated source \(s_i\) | H3 estimand | Smallest \(r\) where holistic "yes" probability ≥ 0.5 |
| \(r_{\text{all},i}^*\) | Full-ensemble aggregate threshold | H2 core estimand | Smallest \(r\) where all core dimensions are simultaneously preserved with probability ≥ 0.5, averaged over the 10 non-oracle sources |
| \(r_{\text{all,model},i}^*\) | Model-based estimate of \(r_{\text{all},i}^*\) | Estimator | — |
| \(r_{\text{all,raw},i}^*\) | Raw empirical aggregate threshold | H1 only | — |
| \(r_{\text{all,ind},i}^*\) | Full-ensemble aggregate threshold under conditional independence | H2 baseline | — |
| \(r_{d,\text{match},i}^*\) | Source-matched dimension threshold for validation source \(s_i\) | H3 | Dimension threshold for the same source used in human holistic ratings |
| \(r_{\max,\text{match},i}\) | \(\max_d r_{d,\text{match},i}^*\) | H3 sensitivity | Most fragile source-matched dimension |
| \(r_{\text{all,match},i}^*\) | Source-matched aggregate threshold for validation source \(s_i\) | H3 primary analytic comparator | Smallest \(r\) where all dimensions are simultaneously preserved for source \(s_i\) with probability ≥ 0.5 |
| \(r_{\max,i}\) | \(\max_d r_{d,i}^*\) | H2 covariate | Most fragile full-ensemble dimension |
| \(\Delta_{\text{all},i}\) | Descriptive aggregate gap | Descriptive | \(r_{\text{all},i}^* - \max_d r_{d,i}^*\) |
| \(\Delta_{\text{excess},i}\) | Excess bottleneck beyond independence | **H2 outcome** | \(r_{\text{all},i}^* - r_{\text{all,ind},i}^*\) |
| \(D_i\) | H3 paired difference | H3 outcome | \(r_{\text{hol},i}^* - r_{\text{all,match},i}^*\) |
| \(C_i^{\pm}\) | Primary signed conflict measure | H2 predictor | Positive = conflict/negative dependence; negative = synergy/positive dependence |
| \(C_i^{+}\) | Descriptive nonnegative deficit conflict measure | Descriptive/sensitivity | Larger values indicate negative dependence; zero pools no-conflict and synergy |
| \(C_i^{\text{adj}}\) | Source-adjusted signed conflict measure | Key sensitivity | Signed negative dependence after removing source and compression-level effects |
| \(PE_{\text{IQR}}\) | Primary practical-effect metric | H2 decision metric | \(\hat{\beta}_1 \cdot IQR(C_i^{\pm})\) |
| \(\varepsilon\) | Population-level equivalence tolerance | H3 primary | Fixed at 0.10 |
| \(\varepsilon_i^{r_{\max}}\) | Text-level conservative equivalence margin | H3 sensitivity | Based on \(r_{\max,\text{match},i}\) |
| \(\varepsilon_i^{\text{all}}\) | Text-level aggregate-based equivalence margin | H3 sensitivity | Based on \(r_{\text{all,match},i}^*\) |
| \(\delta_d\) | Dimension-specific pass criterion | Core | Calibrated in pilot |
| \(\tau_{\text{hol}}\) | Holistic probability threshold | Core | 0.5 |
| \(Q_{d,i}(S)\) | Quality score of summary \(S\) for text \(i\), dimension \(d\) | Core | 0–1 |
| \(SE_i\) | Bootstrap SE of paired H3 difference | H3 filter | SE of \(r_{\text{hol},i}^* - r_{\text{all,match},i}^*\) |
| \(\mathcal{P}_i(r)\) | Set of estimable dimension pairs for text \(i\) at level \(r\) | — | — |
| \(\mathcal{R}_i\) | Set of compression levels included in \(C_i^{\pm}\) for text \(i\) | — | Levels with at least one estimable dimension pair |
| \(n_{ijr}\) | Number of summaries with non-missing pass/fail for pair \((d,j)\) at level \(r\) | — | — |
| \(\overline{p}_i\) | Mean non-bottleneck pass probability | H2 covariate | Averaged over non-max dimensions |
| \(\text{tie}_i\) | All dimensions tied for max threshold | H2 covariate | Binary indicator |
| \(\mathbf{R}_i\) | Text-specific latent Gaussian copula correlation matrix | Copula | Shrunk toward genre-level \(\mathbf{R}_{\text{genre}(i)}\) |
| \(u_i\) | H2 regression residual | H2 model | — |
| \(\eta\) | Model consistency tolerance | Safeguard | Fixed in frozen config |
| \(\epsilon_{\text{clip}}\) | Copula probability clipping constant | Safeguard | \(1/(4 m_d)\) per dimension |

**Direction:** Smaller \(r\) = stronger compression. Larger \(r_{d,i}^*\) = more fragile dimension.

**Terminology note:** \(r\) is a **length retention ratio**, not a compression ratio. We use "length ratio" throughout. We use "summary source" consistently to refer to the 11 summary generation systems: 10 non-oracle systems plus 1 oracle system.

---

### 1.4 Threshold Definitions

§1.4 states the **estimands** — the population quantities the study targets. §7.1 defines the **primary estimators** used to compute them, including observed-grid extraction for H2 and model-interpolated continuous thresholds for H3.

#### Full-ensemble dimension threshold

\[
r_{d,i}^* = \inf \{ r : P(Q_{d,i}(S) \ge \delta_d \mid r, i) \ge 0.5 \}
\]

where \(S\) is drawn from the summary distribution at length ratio \(r\) for text \(i\), with equal weighting across the 10 non-oracle summary sources. Results are conditional on this source ensemble.

#### Holistic threshold

For validation texts only:

\[
r_{\text{hol},i}^* = \inf \{ r : P(\text{"yes"} \mid r, i, s_i) \ge \tau_{\text{hol}} \}
\]

where \(s_i\) is the non-oracle source selected for human holistic ratings for validation text \(i\), and \(\tau_{\text{hol}} = 0.5\).

#### Full-ensemble aggregate threshold

\[
r_{\text{all},i}^* = \inf \{ r : P(\text{all core dimensions preserved} \mid r, i) \ge 0.5 \}
\]

with equal weighting across the 10 non-oracle sources.

#### Source-matched aggregate threshold

\[
r_{\text{all,match},i}^* = \inf \{ r : P(\text{all core dimensions preserved} \mid r, i, s_i) \ge 0.5 \}
\]

where \(s_i\) is the same non-oracle source used for the human holistic ratings of validation text \(i\).

#### Integer pass threshold

Because binomial pass probabilities are discrete, we freeze not only \(\delta_d\) but also the integer pass threshold:

\[
k_d = \lceil m_d \delta_d \rceil
\]

All primary analyses use \(k_d\). Sensitivity analyses use rounding alternatives and continuous beta-binomial models. The \(\delta_d\) calibration accounts for discreteness.

---

### 1.5 Two Constructs of the Overall Threshold

**Construct A: Holistic threshold \(r_{\text{hol},i}^*\)** — integral human judgment: "Does this summary convey the meaning of the original?"

**Construct B: Aggregate threshold** — threshold for simultaneous preservation of all core dimensions. For H2, the aggregate threshold is the full-ensemble threshold \(r_{\text{all},i}^*\). For H3, the primary analytic comparator is the source-matched threshold \(r_{\text{all,match},i}^*\), because human ratings are collected for a single rated source per validation text.

**Key decision:** \(\Delta_{\text{all},i}\) is a **descriptive** aggregate gap. \(\Delta_{\text{excess},i}\) is the **primary confirmatory estimand** for H2. For H3, the primary confirmatory equivalence comparison is between \(r_{\text{hol},i}^*\) and \(r_{\text{all,match},i}^*\). The comparison between \(r_{\text{hol},i}^*\) and the full-ensemble \(r_{\text{all},i}^*\) is a sensitivity analysis.

---

### 1.6 Core Dimensions

| Dimension | Metric | Items | Scoring | Source |
|---|---|---:|---|---|
| Facts | QA-accuracy | 10 QA pairs | Proportion correct, 0–1 | LLM judge + human validation |
| Logic | Bidirectional NLI | 8 premise-hypothesis pairs | Proportion entailment, 0–1 | LLM judge + human validation |
| Author stance | Stance detection | 5 key claims | Proportion agreement, 0–1 | LLM judge + human validation |
| Comprehension | MCQ quiz | 8 questions | Proportion correct, 0–1 | LLM judge + human validation |

#### Item generation and validation

**Item-generation model:** Qwen3.8 Flash Next, locally hosted.

The authoritative model specification is the frozen SHA-256 manifest, inference configuration, chat template, and generation configuration. Architecture details are recorded in the frozen configuration file where verifiable. If any architecture or checkpoint detail cannot be verified, it will not be treated as authoritative.

This model is not included among the 10 non-oracle summarizers or the LLM judge in the primary analysis.

All generated items are human-validated by two team members before pilot use. Each item is independently accepted or rejected by two validators. Acceptance requires consensus. Disagreements are resolved by discussion; if consensus cannot be reached, the item is discarded. The initial agreement rate and final item retention rate will be recorded in the pilot log.

If the checkpoint or hosting environment becomes unavailable, data collection pauses and a registered amendment is filed.

#### Frozen model manifest, SHA-256

| File | SHA-256 |
|---|---|
| `qwen38-flash-next-w4b.hgn` | `9c116bbc01f77b7a15464c1a124eb3325b286089b8a2a6f2856c9b246a235bd6` |
| `qwen38-flash-next-w4b.overlay.hgn` | `737d6bdaef274d3cc22de5bc265b390b89db5fb1e709f58db75287fdc35bb276` |
| `qwen38-flash-next-w4b.overlay-speed.hgn` | `113d77358107549fa22e06643ae3a524908aa7ea011afaebec69fc5f1991c370` |
| `qwen38-flash-next-vision.hgn` | `d62e0ae553fe88afd3833733d4a4c669f34d20fd8dfce4b9610525bed2134b10` |
| `chat_template.jinja` | `c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041` |
| `generation_config.json` | `e70c136c1b78ddc1fb0905bac8e733a4dc448d4f852a5dd75143fffc70be550e` |
| `merges.txt` | `a9d356d7bdf1ef4949e3e748e95b8e10ad9d4e2e838eddc38a0a7b6b94d1db8d` |
| `tokenizer_config.json` | `b11349aafa7cdc6a320767cf7ceb29ed82f7eda5d65e8e0819e76f0ce947bf27` |
| `tokenizer.json` | `0997f410c57a1f4e53b09e4be8f4a172d90edd9564368fb0847030937229b9f3` |
| `vocab.json` | `ce99b4cb2983d118806ce0a8b777a35b093e2000a503ebde25853284c9dfa003` |

The prompt hash used for item generation is recorded in the frozen pilot configuration file before item generation begins. The full manifest and prompts are archived in the OSF materials.

#### Facts

10 factoid QA pairs are generated from the original text. Gold answers must be supported by the original. The QA system answers using only the summary. Correct = matches gold or accepted paraphrase. Frozen after pilot validation.

#### Logic

8 bidirectional NLI pairs:

- Original → Summary: premise from original, hypothesis from summary, measuring faithfulness.
- Summary → Original: key claims from original tested against summary, measuring coverage.

NLI score = proportion classified as entailment. Contradiction and neutral are both scored as 0. This measures informational sufficiency for inference, not purely logical coherence.

#### Author stance

5 key claims are identified from the original by LLM plus human validation. Gold stance labels are support, oppose, or neutral. Summary stance is scored by LLM judge. Score = proportion matching.

**Omission rule:** omission of a support/oppose claim = mismatch; omission of a neutral claim = mismatch.  
**Sensitivity:** omission of neutral claims treated as neutral rather than mismatch.

For procedural texts where stance is less relevant, this dimension may show ceiling effects; this will be monitored in pilot.

#### Comprehension

8 MCQ questions test inference, coherence, and main idea, not just factual recall. There are 4 answer options per question, so chance = 0.25. Distractors are generated systematically by LLM. Questions must be answerable from the summary alone with respect to the original. Validated in pilot.

**Chance correction:** raw proportion correct is primary. The chance-corrected score

\[
Q_{\text{corrected}} = \max\left(0, \frac{Q_{\text{raw}} - 0.25}{0.75}\right)
\]

is reported as a sensitivity analysis.

LLM-judged comprehension is a proxy for reader comprehension and may not capture reader-dependent factors.

#### Auxiliary dimensions

Auxiliary dimensions are exploratory: style, argumentative structure, formality. They are not operationalized in this protocol and are listed for future work.

#### Operational definition

Core dimensions are treated as operational necessary conditions. The pass criterion \(\delta_d\) is calibrated such that the probability of expert judgment "dimension preserved" equals 0.5 at \(Q_d = \delta_d\).

The 0.5 threshold is a standard operationalization: more likely preserved than not. Robustness evaluated at 0.6 and 0.7 for both holistic and analytic thresholds.

#### Dimension independence

In pilot, pairwise correlations of text-level thresholds are assessed. If two dimensions show correlation > 0.85 at the text-threshold level, the dimension with lower pilot reliability is treated as auxiliary. If tied, the dimension with lower theoretical priority is dropped. The priority ranking is fixed before pilot:

\[
\text{facts} > \text{comprehension} > \text{logic} > \text{stance}
\]

The decision rule is fixed before main data collection.

#### Genre applicability

Confirmatory genre set: news, scientific texts, procedural instructions.  
Exploratory genres: fiction, dialogue.

#### Genre exclusion criteria

A genre is excluded if, in pilot:

- Fleiss' κ < 0.4 for holistic ratings;
- ICC < 0.5 for any core metric;
- more than 50% of texts have censored thresholds for at least two core dimensions.

ICC between 0.5 and 0.7 is treated as cautionary: reported but not automatically excluded.

If fewer than two confirmatory genres remain, H2 is downgraded to exploratory.

Pilot holistic reliability will be assessed using at least two trained raters per pilot item. With two raters, Fleiss' κ reduces to Cohen-type κ; Gwet's AC1 will also be reported. If more than two raters are used, Fleiss' κ will be reported.

#### Relationship between genre exclusion and dimension validation

Genre-level reliability criteria and dimension-level LLM-judge validation criteria operate independently. A genre may be retained even if a dimension later fails LLM-judge validation; in that case, dimension retention rules apply. A dimension may pass validation even if a genre is excluded; in that case, genre exclusion rules apply. If fewer than two confirmatory genres or fewer than two core dimensions remain, H2 and H3 are downgraded to exploratory according to the pre-specified rules.

#### Pilot genre coverage

The pilot focuses on the three confirmatory genres. Fiction and dialogue are not used for confirmatory genre exclusion and remain exploratory by design.

#### Validation subset re-stratification

If a confirmatory genre is excluded after pilot, the validation subset is re-stratified across the remaining confirmatory genres, preserving total \(N = 100\) where feasible.

---

### 1.7 Oracle Summary System

**The oracle summary system is strictly reserved for exploratory analyses and upper-bound benchmarks.** It is excluded from all primary estimators, including \(r_{d,i}^*\), \(r_{\text{all},i}^*\), \(C_i^{\pm}\), \(\Delta_{\text{excess},i}\), H2, and H3.

The oracle is an extractive maximin system over core scores.

**Candidate construction:** Candidate extractive summaries are formed from subsets of source sentences whose total length is closest to the target \(r\) under the frozen length rule.

**Objective:** maximize the minimum normalized core score among candidate summaries.

**Normalization:** core scores are normalized within text and compression level using z-scores across candidate extractive summaries; the exact normalization rule is frozen.

**Ties:** broken by original sentence position.

The oracle is length-constrained to the same target \(r\) as all other systems.

---

### 1.8 Primary Dataset Definition for H2

The **primary H2 corpus** is the confirmatory-genre subset of the 400-text main corpus. The confirmatory genres are news, scientific texts, and procedural instructions. The target primary H2 corpus is therefore **240 texts before exclusions**.

The **primary dataset for H2** consists of texts in this confirmatory-genre subset that satisfy all of the following:

- finite \(r_{\text{all,model},i}^*\);
- finite \(r_{\text{all,ind},i}^*\);
- finite \(r_{\max,i}\);
- stable thresholds, \(SE \le 0.15\);
- valid \(C_i^{\pm}\);
- model-consistency check passed;
- no censored threshold required for computing \(\Delta_{\text{excess},i}\).

Validation texts are excluded from primary H2.

Texts with censored thresholds required for computing \(\Delta_{\text{excess},i}\) are excluded from the primary H2 dataset. Censoring rules are reported for descriptive purposes and used in the pre-specified interval-censored sensitivity analysis.

A valid main-corpus text is necessary but not sufficient for inclusion in the primary H2 dataset. Primary H2 eligibility additionally requires all criteria in this section.

The full 400-text main corpus includes fiction and dialogue texts. Those genres are not part of the primary H2 target population. They are used for descriptive and exploratory analyses, genre-stability checks, and attrition/replacement planning.

---

