## 4. Sampling Plan

### 4.1 Registration Structure

Four registered components:

1. **Smoke test**: 10 texts, technical verification only. Not used for calibration or confirmatory decisions.
2. **Pilot**: 45–60 texts, feasibility and calibration. Separate from confirmatory data. Registered prior to pilot data collection.
3. **Validation subset**: 100 texts, drawn only from the three confirmatory genres and additional to the 400-text main corpus. Used for LLM-judge validation and H3. Excluded from primary H2.
4. **Confirmatory main corpus**: 400 texts post-freeze.

**Total non-pilot texts:** 500.  
**Total summaries:**

\[
500 \times 7 \times 11 = 38{,}500
\]

**Primary H2 corpus:** the confirmatory-genre subset of the 400-text main corpus, consisting of news, scientific, and procedural texts. Target size before exclusions: **240 texts**.

The full 400-text main corpus includes fiction and dialogue texts. The full corpus is used for exploratory/descriptive analyses, genre-stability checks, and attrition/replacement planning.

**Validation genre allocation:** approximately 33 news, 33 scientific, 34 procedural, or proportional to the main confirmatory corpus. Fiction and dialogue are not included in the primary validation subset.

**Pilot texts are excluded from the main corpus.** No overlap.

---

### 4.2 Text Sources and Selection Units

**Language:** All texts and summaries are in Russian. This study is conducted on Russian-language corpora with Russian-speaking participants.

| Source | Unit | Genre |
|---|---|---|
| Lenta.ru / TASS news corpus | Full articles, 300–800 words | News |
| eLIBRARY.RU and CyberLeninka | Abstracts and short articles, 150–800 words; lower bound relaxed for scientific texts | Scientific |
| Open instructional texts from federal/municipal portals and other permissively licensed Russian instructional sources | Single self-contained procedural task/section | Instructions |
| Russian State Library digital collection and Project Gutenberg, Russian translations and originals in the public domain | Self-contained excerpts, scene/passage | Fiction |
| Named open Russian dialogue corpora with verified permissive licenses | Concatenated dialogue segments meeting length and self-containedness criteria | Dialogue |

The exact dialogue datasets, versions, and licenses will be recorded in the frozen configuration file before data collection.

Dialogue segments will be concatenated only if the resulting segment forms a self-contained conversational task or topic. Self-containedness will be judged by two team members using the same consensus rule as other genres.

**Validation texts** follow the same inclusion criteria and source families as the main corpus for the three confirmatory genres, but are non-overlapping with the main corpus. Fiction and dialogue are not included in the primary validation subset.

---

#### Preprocessing

- Whitespace tokenization for word count.
- For de-duplication: lowercase, whitespace-tokenize, then compute 3-gram overlap.
- De-duplication threshold: 95% 3-gram overlap.
- Self-containedness judged by 2 team members; consensus required; initial disagreement rate reported.
- Random seed 42, with frozen seed-stream separation.

---

#### PII screening

Regex patterns adapted for Russian personal data formats, including: ФИО; phone numbers; addresses; passport patterns; SNILS; INN. Plus manual check.

---

#### Inclusion criteria

- Scientific texts: 150–800 words.
- Other genres: 300–800 words.
- Self-contained.
- No duplicates.
- No PII.
- Licensing permits research use and derived-data redistribution where sharing is planned.

---

#### Corpus size

5 genres × 80 texts = 400 main-corpus texts.  
Validation subset = 100 confirmatory-genre texts.  
Total = 500 texts.

---

#### Short scientific abstracts

For short scientific abstracts, thresholds at \(r = 0.05\) may be unstable. Sensitivity analyses excluding \(r = 0.05\) are pre-specified.

---

#### Licensing and redistribution

Source licensing checked; only sources permitting research use and derived-data redistribution are included. For eLIBRARY.RU and CyberLeninka, only open-access items with permissive licenses are used.

Where full-text sharing is not permitted, IDs plus sampling instructions are shared instead.

Summary outputs will be shared only where source-text license and API terms permit redistribution of derived outputs. If a source text cannot be shared but summary redistribution is permitted, the summary will be shared with a reference to the source ID and sampling instructions. If summary redistribution is not permitted, only derived numeric scores and metadata will be shared.

---

### 4.3 Summary Generation

**10 non-oracle systems:**

| # | System | Temperature | Base-model family |
|---:|---|---:|---|
| 1 | Qwen3.7 Plus / API label: Qwen3.7Plus | 0 | qwen |
| 2 | Qwen3.7 Plus / API label: Qwen3.7Plus | 0.8 | qwen |
| 3 | DeepSeek-V4 | 0 | deepseek |
| 4 | DeepSeek-V4 | 0.8 | deepseek |
| 5 | Yandex Alisa | 0 | alisa |
| 6 | Yandex Alisa | 0.8 | alisa |
| 7 | Sber GigaChat | 0 | gigachat |
| 8 | Hybrid TextRank + BART | 0 | hybrid |
| 9 | Hybrid TextRank + BART | 0.8 | hybrid |
| 10 | Pure extractive TextRank baseline | — | textrank |

Sber GigaChat is included at temperature 0 only due to access/stability constraints. This asymmetry is acknowledged as a limitation of the source ensemble.

Model family names are provider labels. Exact provider endpoints, API versions, checkpoint identifiers, or local model hashes will be recorded in the frozen configuration file before data collection. If public names differ from the names used here, a mapping table will be included in the OSF materials. If a named model is not yet publicly verifiable or becomes unavailable, data collection will pause and a registered amendment will specify the exact replacement checkpoint and validation plan.

**1 oracle:** Extractive maximin over core scores, length-constrained to target \(r\). Exploratory only.

**Total:** \(11 \text{ systems} \times 500 \text{ texts} \times 7 \text{ levels} = 38{,}500 \text{ summaries}\).

---

#### Base-model correlation

Systems sharing the same underlying base model may exhibit correlated behavior. A base-model random effect is included in threshold models as a sensitivity analysis to account for correlated behavior among systems sharing the same base-model family.

---

#### Generation protocol

- Exact prompts frozen.
- Length instructions included.
- Random seeds fixed for stochastic systems.
- Each system × text × level has at most two usable generation attempts: one initial attempt and one length-regeneration attempt.
- API transmission retries are allowed once per attempt and do not count as content-generation attempts.
- Outputs hashed and archived.
- Where API providers do not guarantee deterministic generation from fixed seeds, outputs will be archived and hashed, and any non-determinism will be documented.

---

#### Seed management

A frozen seed-management scheme will be used. Separate seed streams will be generated from the master seed for: text sampling; summary generation; validation-source assignment; permutation tests; bootstrap resampling; power simulations; and cross-fitting. The seed scheme will be recorded in the frozen configuration file.

---

#### Model deprecation fallback

- Qwen3.7 Plus family → next Qwen version.
- DeepSeek-V4 → next DeepSeek version.
- Yandex Alisa → next Alisa version.
- Sber GigaChat → next GigaChat version.
- Qwen 3.8 Max judge → next Qwen Max version.

If no acceptable fallback exists, pause and file a registered amendment.

If a summarizer model must be replaced after generation has begun, the replacement will be treated as a new summary source unless a bridge analysis demonstrates acceptable equivalence. If equivalence cannot be demonstrated, outputs from the replaced model will be excluded or analyzed separately, and the change will be documented as a registered amendment.

The exact model checkpoints for all summarizers, the judge, and the item generator will be recorded in the frozen pilot configuration file before any generation begins.

---

#### API access and legal checklist

Before main data collection, the following will be verified for each summarizer and judge API: API access from the operating location; research-use permission; data-retention terms; training-use opt-out where applicable; cross-border transfer conditions; and redistribution rights for derived outputs.

A brief legal review of API terms, data-retention policy, training opt-out, and cross-border transfer conditions for non-PII text will be documented before API calls begin.

If any required API is inaccessible or prohibits the intended research use, a registered amendment will specify the replacement system and its validation plan.

---

#### Length control

Deviation:

\[
\text{Deviation} = \frac{|r_{\text{actual}} - r_{\text{target}}|}{r_{\text{target}}}
\]

Rules:

- Deviation > 20% after the initial generation: regenerate once.
- Final deviation > 20% and ≤ 30%: exclude from primary analysis; include only in the pre-specified length-deviation sensitivity analysis.
- Final deviation > 30%: exclude from all summary-based analyses except technical failure reporting.

Primary analyses use target \(r\) for retained summaries.

---

### 4.4 Power Simulation

After pilot freeze, simulation-based power analysis using pilot-derived parameters.

Scenarios:
- confirmatory genres only, \(N = 240\);
- full main corpus, \(N = 400\), for exploratory and attrition planning;
- reduced core, 3 dimensions;
- censoring, 20% and 30%;
- worst-case genre exclusion;
- primary H2 N after main-corpus exclusions;
- H3 source-matched equivalence with expected validation losses.

Outcomes:
- power for H2;
- power for H3;
- probability H3 not informative;
- expected censoring;
- expected exclusions;
- stability of \(C_i^{\pm}\);
- expected ICC/Fleiss κ;
- expected power and stability of the cross-fitted signed conflict check;
- expected power and stability of the source-adjusted signed conflict check;
- cumulative probability that H2 and H3 remain confirmatory after all pre-specified exclusion, reliability, retention, censoring, and stability rules are applied.

1,000 simulation replications, seed 42.

**Decision rule:** If power <80% for H2 or H3, increase sample size or downgrade before main collection. Decision recorded as registered amendment.

**Sample size justification:** The primary confirmatory H2 analysis is based on the three confirmatory genres: news, scientific, and procedural. The target confirmatory-genre sample is therefore **240 main-corpus texts before exclusions**.

The absolute minimum for H2 to remain confirmatory is **180 valid confirmatory-genre texts**, unless a higher minimum is frozen after pilot power simulation. If the number of valid confirmatory-genre texts falls below the frozen minimum, H2 will be downgraded to exploratory.

The full 400-text main corpus includes fiction and dialogue texts and supports descriptive/exploratory analyses, genre-stability checks, and replacement/attrition planning. It is not the primary H2 sample.

The planned human sample of 120 participants corresponds to the planned 100 validation texts. If pilot simulations indicate that H3 requires more validation texts, the validation subset and corresponding participant capacity may be increased only before confirmatory human data collection and only through a registered amendment. If such an increase is not feasible, H3 will be downgraded to exploratory rather than analyzed post hoc with insufficient precision.

---

### 4.5 Stopping Rule

- 38,500 summaries.
- 7,000 human ratings on validation texts.
- 120 participants.
- LLM judge on all 38,500 summaries.

**Valid main-corpus text:**
- ≥8 valid non-oracle summaries per level across ≥6 of 7 levels;
- valid \(C_i^{\pm}\);
- ≥1 valid threshold per core dimension.

**Valid validation text:**
- selected source \(s_i\) has valid summaries across ≥6 of 7 levels;
- valid human holistic ratings;
- valid source-matched LLM-judge scores;
- valid source-matched aggregate threshold or recorded censoring/exclusion reason.

A valid main-corpus text is necessary but not sufficient for primary H2 eligibility. Primary H2 eligibility additionally requires the criteria in §1.8.

**Targets:** 400 valid main-corpus texts overall, including at least the frozen minimum number of valid confirmatory-genre texts required for H2, with a planned target of 240 confirmatory-genre texts before exclusions; and 100 valid validation texts.

If fewer than 360 valid main-corpus texts are obtained, continue collection. If fewer than 360 valid main-corpus texts are obtained after all feasible collection attempts, H2 will be downgraded to exploratory, and this change will be documented as a registered amendment.

**Confirmatory-genre minimum:** H2 requires the minimum valid confirmatory-genre sample size frozen in the pilot power simulation, with an absolute floor of 180. If the number of valid confirmatory-genre texts falls below that pre-specified minimum, H2 will be downgraded to exploratory, even if the total main-corpus sample exceeds 360 texts.

If fewer than 100 valid validation texts are obtained, H3 and LLM-judge validation may be downgraded or the validation sample may be extended, documented as a registered amendment, subject to the H3 rule for 70–100 texts.

---

