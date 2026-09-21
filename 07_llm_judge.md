## 8. LLM-as-Judge

### 8.1 Registration

**Judge model:** Qwen 3.8 Max. Not among summarizers, to avoid self-preference bias.

- Temperature: 0.
- Top-p: 0.95.
- Prompt granularity: one call per summary per dimension, with all items for that dimension batched into a single structured prompt.

Total judge calls: \(38{,}500 \times 4 = 154{,}000\).

Prompts are provided in Russian; the judge model is instructed to respond in a structured format independent of language.

Structured JSON output. Parsing failures: retry once; if still failed, mark missing. Refusals: retry once; if still refused, mark missing. Report refusal rates by genre, level, source.

Prompts, rubrics, response schemas: frozen in supplementary materials.

---

#### Bias checks

Source-specific bias tests. Length bias checks by actual length, level, and fluency proxies.

Source bias will be assessed by comparing mean LLM-judge dimension scores against mean human analytic dimension scores on the validation subset. A source will be flagged for systematic bias if its mean difference exceeds 0.10 in absolute value on the 0–1 scale for any core dimension, or if the difference is statistically robust under bootstrap. Flagged sources will be examined in sensitivity analyses; exclusion from primary analysis will occur only if the bias is confirmed and documented.

---

#### API data handling

- PII removed before API calls.
- API terms checked for research use and redistribution permissions.
- Outputs stored locally.
- Data not used for model training by provider, verified per API terms.
- Provider data retention policies documented.
- A brief legal review of API terms, data-retention policy, training opt-out, and cross-border transfer conditions for non-PII text will be documented before API calls begin.

---

#### Model deprecation and fallback

If Qwen 3.8 Max is unavailable or deprecated before scoring, the fallback judge will be the current stable Qwen Max model in the same or next generation. The exact fallback checkpoint will be frozen before scoring.

A bridge validation must be completed before confirmatory scoring, and the fallback judge must meet the same validation criteria or pre-specified equivalence criteria. If it does not, scoring pauses and a registered amendment is filed.

Leave-one-source-out judging is exploratory sensitivity.

---

### 8.2 Validation

**Validation sample:** The 100 validation texts, additional to main corpus, stratified across confirmatory genres.

**Metrics:** For each dimension, LLM-judge validation will use summary-level scores from the validation texts. The primary validation metric is an absolute-agreement ICC computed across validation summaries between the LLM-judge dimension score and the mean human analytic rating for that dimension.

The exact ICC model will be frozen before validation. The planned model is an absolute-agreement ICC, ICC(A,1) or ICC(3,1), treating the LLM judge and the mean human composite as the specific measurement procedures of interest. The reliability of the mean human rating will also be reported.

**Scale harmonization:** Human 1–5 ratings are linearly mapped to [0, 1] using \(\frac{\text{rating} - 1}{4}\) before computing ICC with LLM proportion scores. The exact mapping is frozen before validation.

**Cohen's κ:** Computed on pass/fail classifications using the frozen \(k_d\) for LLM scores and the frozen human dichotomization rule: mean human rating ≥ 3.5 = pass; mean human rating < 3.5 = fail.

**Thresholds:**
- ICC ≥ 0.7 per dimension.
- Cohen's κ ≥ 0.6.

Freeze decision before H2.

---

#### Dimension retention

If a core dimension fails validation in the validation subset, the reduced-core H2 will be treated as confirmatory only if the dimension had already been flagged as at-risk in the pilot freeze. Otherwise, the reduced-core H2 is exploratory, and the original four-dimension H2 is reported as a sensitivity analysis. If two or more dimensions fail, H2 is exploratory.

If the core dimension set is reduced after validation, H3 based on the reduced-core aggregate threshold will be treated under the same confirmatory/exploratory rule as H2. If the reduced core is exploratory, H3 is also exploratory.

Validation texts are excluded from primary H2.

**Note:** Human analytic ratings are global 1–5 dimension ratings, while LLM scores are item-based proportions. Method variance may reduce ICC. A small item-level human validation subset, e.g. QA/NLI items answered by humans, is included as exploratory validation.

---

