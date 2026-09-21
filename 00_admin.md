# Pre-Registration: Thresholds of Operational Meaning-Preservation in Text Compression
## Testing the Multidimensional Bottleneck Hypothesis

**Author:** Aleksandr Sorokin  
**Registration date:** 21 September 2026  
**Registration stage:** Prior to collection of pilot and confirmatory data  
**Version:** Final Registration, Version 3.4 (Combined)  

**Registration status statement:**  
No pilot, validation, or confirmatory data have been collected at the time of this registration. All pilot-based calibration and fallback decisions will be made before confirmatory hypothesis testing and will be recorded in a signed decision log. There will be no interim analyses of confirmatory data, no optional stopping, and no peeking beyond the pre-specified stopping rules.

---

## 0. OSF Registration Summary

### Study design

This is an observational, correlational, multi-method study of Russian-language text summarization. Compression level and summary source are within-text factors. Genre is a between-text factor. Human holistic and analytic ratings are collected only for the validation subset.

### Unit of analysis and inference

The primary inferential unit for H2 and H3 is the **text**. Summary-level observations are nested within texts and are used for measurement, but confirmatory inferential claims are made at the text level. No summary-level confirmatory claims are made.

### Sample size

The planned non-pilot corpus consists of:

- 400 main-corpus texts;
- 100 validation texts;
- 500 total non-pilot texts.

The primary H2 target population is the confirmatory-genre subset of the main corpus: news, scientific texts, and procedural instructions. The planned target is **240 confirmatory-genre texts before exclusions**.

The pre-specified absolute minimum for H2 to remain confirmatory is **180 valid confirmatory-genre texts**, unless a higher minimum is frozen after pilot power simulation. If the valid confirmatory-genre sample falls below the frozen minimum, H2 will be downgraded to exploratory.

For H3, the minimum valid validation sample is **70 texts**. If fewer than 70 valid validation texts remain under the frozen H3 SE filter, H3 will be downgraded to exploratory.

### Interim analyses

There will be no interim analyses of confirmatory data. There will be no optional stopping, peeking, or hypothesis-driven data collection beyond the pre-specified stopping rules.

### Funding and conflicts of interest

No external funding is declared. The author declares no conflicts of interest. If funding or conflicts arise, they will be disclosed in a registered amendment.

### Author contributions

Aleksandr Sorokin is responsible for conceptualization, registration, data collection oversight, analysis, and final reporting. The registered protocol and frozen configuration files constitute the binding analysis plan.

### Expected timeline

Pilot calibration, data collection, and confirmatory analysis are expected to take approximately 6–9 months after ethics approval and API verification. A provisional target for final confirmatory analysis completion is Q1–Q2 2027, subject to ethics approval, model availability, and API access.

### Ethics approval

Ethics approval has not yet been obtained at the time of registration. No human data will be collected before approval is received. The ethics committee name, approval number, and approval date are preconditions for human data collection and will be recorded in the frozen configuration file.

---

## Plain-Language Summary

This study investigates how much a Russian-language text can be shortened before different aspects of meaning-preservation are lost. We compare four dimensions: factual preservation, logical coherence, author stance, and reader comprehension. We ask whether summaries need extra length not just because some aspects of meaning are hard, but because different aspects of meaning pull in different directions.

We test whether preserving all aspects simultaneously requires more length than would be expected if the dimensions were independent, and whether this extra length is predicted by conflict among the dimensions. We also test whether human holistic judgments of meaning-preservation agree with an analytic, dimension-based threshold when both are evaluated for the same summary source.

---


---

## 11. Other

### 11.1 Confirmatory vs Exploratory

**Confirmatory:** H2, H3 source-matched continuous equivalence.  
**Data integrity check:** H1, not in inferential family.  
**Exploratory:** H4, auxiliary dimensions, oracle, genre interactions, source-specific analyses, full-ensemble H3 comparison, observed-grid H3 comparison, all sensitivity analyses unless explicitly labeled key confirmatory sensitivity.

---

### 11.2 Deviations

All deviations documented as registered amendments on OSF.

---

### 11.3 Limitations

- Russian language and Russian-speaking participants only; generalizability to other languages and cultural contexts is unknown.
- Selected genres and LLM-generated summaries limit generalizability.
- Core metrics may perform poorly for fiction/dialogue.
- LLM judge is a proxy; comprehension proxy may not capture reader-dependent factors.
- Perceived length not fully hidden.
- Floor effects at \(r = 0.05\).
- 0.5 threshold is a standard operationalization; robustness evaluated at 0.6/0.7.
- Aggregate threshold may be undefined if max joint probability <0.5 under independence.
- Oracle may overfit judge.
- Threshold estimation may be unstable for some texts.
- \(\Delta_{\text{excess},i}\) is derived from grid-based thresholds and may be coarse or zero-inflated.
- Primary H2 uses signed conflict derived from the same pass/fail dependence structure used to estimate \(\Delta_{\text{excess},i}\). H2 is therefore an association/model-consistency test, not a fully independent causal test.
- Cross-fitting and source adjustment reduce shared sampling noise but do not fully remove shared functional form between conflict and excess measures.
- The Gaussian copula approximation may not perfectly represent binary pass/fail dependence.
- The primary copula model assumes source-invariant dependence within text. Source-specific dependence is only explored in sensitivity analyses.
- Possible API model drift.
- Human global ratings may not perfectly correspond to LLM item-based scores.
- Dependence on selected summary-source ensemble.
- Non-monotonicity in pass probabilities, constrained in model but may not reflect reality.
- H3 primary comparison is source-matched and uses continuous interpolation to reduce measurement-base and grid-resolution mismatch, but residual differences between human holistic judgment and analytic aggregation remain.
- Full-ensemble H3 comparison remains sensitive to source mismatch and is exploratory.
- The H3 SE filter may select more typical or stable texts.
- Participant education requirement limits generalizability to less-educated populations.
- API providers may not guarantee deterministic generation from fixed seeds.
- Source-adjusted \(C_i^{\text{adj}}\) may still contain residual between-system variance.
- No personal data are transferred outside the Russian Federation; only de-identified text is transmitted to API providers after PII removal.
- Some API providers for LLM summarization and judging may not be directly accessible from the Russian Federation; if access is restricted, model substitutions will be documented as registered amendments.
- The summarizer ensemble is intentionally composed of models that are accessible under the study's technical and legal constraints: Qwen3.7 Plus, DeepSeek-V4, Yandex Alisa, and Sber GigaChat.
- Item-generation model is locally hosted. Hardware constraints, quantization, or inference stack updates could introduce subtle behavioral changes. Frozen manifest hashes and inference configuration mitigate this; any deviation will be documented.
- Two summarizers are Russian-native, Yandex Alisa and Sber GigaChat. Their inclusion improves ecological validity for Russian texts but may limit comparability with prior cross-lingual benchmarks.
- If the judge model or a summarizer model is replaced, bridge validation is required; otherwise confirmatory comparability may be compromised.
- Model names used in this registration are provider labels; exact checkpoints, API endpoints, or local model hashes will be recorded in the frozen configuration file.

---

### 11.4 OSF Materials

- Data dictionary, Appendix B.
- Prompts in Russian.
- Model versions and exact checkpoints.
- API parameters.
- Survey instruments.
- Rubrics.
- Consent forms, Russian and English translations.
- Analysis code, frozen.
- Simulation code.
- Frozen configuration file with signed decision log.
- Exclusion, reliability, and power simulation code.
- Software environment lockfile/Docker image.
- Pilot decision log template.
- Bootstrap dry-run results.
- Compute budget specification.
- Item-generation model manifest: frozen SHA-256 hashes, inference configuration, chat template, and generation config.
- Summarizer checkpoint registry.
- Model-name/checkpoint mapping table.
- Ethics approval status and approval number once obtained.
- Legal review summary for API terms.
- License information for data, code, and materials.

**Data sharing:** De-identified ratings, summary outputs, and derived scores shared where licenses permit. Full texts shared where source licensing permits; otherwise IDs plus sampling instructions. CC-BY 4.0 for derived data. Analysis code will be released under an open-source license specified in the OSF record. No personal data, as defined by ФЗ-152 / FZ-152, are included in shared datasets.

---

### 11.5 Pilot Amendment Policy

Changes after pilot are documented as registered amendments.

---

