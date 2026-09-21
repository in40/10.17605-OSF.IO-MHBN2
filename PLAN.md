# Action Plan — Meaning-Preservation Thresholds Study (v3.4)

Walkthrough of each registration block: what it is for → what actions it forces.

---

## Block-by-block

### 00_admin — registration identity & compliance
**For:** study identity, sample-size floors, no-peeking rules, funding/COI, timeline, ethics status.
**Actions:**
- Start signed decision log NOW (template); every future choice gets date + rationale + code hash.
- On ethics approval: record committee name, number, date in frozen config + OSF metadata.
- Any funding/COI arising → registered amendment.
- Track: H2 floor 180 valid confirmatory-genre texts; H3 floor 70 valid validation texts.

### 01_conceptual — constructs
**For:** Construct A (holistic human) vs B (analytic 4-dim aggregate); descriptive gap Δ_all vs confirmatory excess Δ_excess.
**Actions:**
- None direct — but all code naming must follow: `r_hol`, `r_all`, `r_all_ind`, `r_all_match`, `C_pm`.
- Write one-page operationalization memo tying constructs to implemented variables (for paper + reviewers).

### 02_math — notation, threshold defs, core dims, oracle, H2 dataset
**For:** formal estimands: r*_d = smallest r with P(preserved)≥0.5; k_d = ceil(m_d·δ_d); 4 core dims (Facts 10 items, Logic 8, Stance 5, Comprehension 8); oracle system; primary H2 dataset eligibility.
**Actions:**
- Build item-generation pipeline per dimension (QA for facts, NLI for logic, stance items, comprehension items) — local Qwen3.8 Flash Next; freeze SHA-256 manifest.
- Implement oracle summary system (human-expert extract at each r).
- Implement threshold estimators matching definitions exactly; censoring codes (CENS_RIGHT/LEFT).
- Encode H2 primary-dataset eligibility rules as filter flags.

### 03_hypotheses — RQs + H1–H4 decision rules
**For:** H1 integrity check (r_all* ≥ max r_d*); H2 primary: OLS excess ~ C± + controls, one-sided β1>0, Holm, BCa CI LB ≥ 0.15, all 4 criteria; H3 TOST equivalence r_hol vs r_all_match with SE filter; H4 exploratory.
**Actions:**
- Write analysis code skeleton NOW with exact criteria as assertions (Holm set = {H2, H3}).
- Implement H1 as hard check; H2 four-criteria gate; H3 TOST + percentile p; H4 descriptives.
- Pre-freeze: OLS spec, permutation p-rule, TOST percentile rule.

### 04_sampling — corpus, sources, power, stopping
**For:** 10 smoke + 45–60 pilot + 100 validation + 400 main = 500 non-pilot; 7 levels × 11 sources = 38,500 summaries; genre allocations; stop/downgrade rules.
**Actions:**
- Select source corpora per genre (news, scientific, procedural, fiction, dialogue); check licenses (share_text/share_summary flags).
- PII screening pipeline before any API call.
- Pick 11 summarizer systems (10 real + oracle); freeze checkpoint registry + model-name mapping.
- Run power simulation during pilot; freeze min valid N (≥180) and H3 SE filter.

### 05_design — variables, blinding, technical checks
**For:** IV/DV table; blinding of raters to source/level; technical check list.
**Actions:**
- Implement: SHA-256 summary hashes, length-deviation checks + regeneration flags, judge refusal/parse-failure monitors, attention checks, source-balance assignment of s_i for validation texts.
- Blinding: rater UI hides system_id, target_r, genre.

### 06_analysis — full statistical plan
**For:** hierarchical Bayesian threshold models (brms/Stan, monotone spline, text RE, source RE, base-model RE); bootstrap 2,000; 33 sensitivity analyses.
**Actions:**
- Build brms models; monotone spline basis frozen in pilot; custom Stan only if needed (log it).
- Bootstrap dry-run (20–50 texts) BEFORE confirmatory scoring; document runtime.
- Implement all 33 sensitivity analyses as parameterized runs.
- Docker image / lockfile; code version hash into frozen config.

### 07_llm_judge — judge registration + validation
**For:** Qwen 3.8 Max, temp 0, 154,000 calls; bias checks; validation gates ICC ≥ 0.7, κ ≥ 0.6; deprecation fallback + bridge validation.
**Actions:**
- Freeze Russian prompts + rubrics + JSON schema in OSF.
- Legal review of API terms (research use, no-training opt-out, retention, cross-border) — document before first call.
- Run judge-vs-human validation on 100 validation texts; gate: ICC/κ per dim; freeze decision before H2.
- Pre-register fallback judge + bridge validation rule.

### 08_human_sample — participants, tasks, ethics
**For:** 120 participants (40 holistic + 80 analytic), Toloka, RF residents, 3×45min sessions + 30min training; consent, FZ-152, attention checks, 5-yr retention.
**Actions:**
- **Ethics application — critical path, start first.** No human data before approval.
- Build survey instruments in Russian (consent, PIS, rating UI, attention checks); freeze.
- Toloka campaign setup: screening (RF + secondary-specialized+ education), compensation above-minimum (exact rate → frozen config), quality bonuses.
- Separate storage: platform IDs ≠ rating data.

### 09_pilot — calibration + freeze
**For:** 45–60 texts; 18 goals; δ_d calibration (5 experts/dim × 20 summaries, logistic w/ expert RE, SE<0.05); full freeze list (~35 items).
**Actions:**
- Recruit 20 experts (PhD/faculty NLP/linguistics, native RU, blind to Q_d); pay.
- Run pilot generation + scoring; calibration; power sims; agreement (Fleiss κ, ICC); dimension-independence check.
- Produce frozen configuration file + signed decision log covering entire freeze list.
- **Gate: no confirmatory analysis before freeze.**

### 10_appendices — budget + data dictionary
**For:** ~$9,000–11,500 + 20% contingency ≈ **$11K–14K total**; ~197K–230K API calls; ~8 weeks; full variable schema.
**Actions:**
- Secure funding (~$14K with buffer) — biggest external dependency.
- Implement DB/parquet schema per Appendix B (all codes + analysis flags).
- Data-sharing plan: CC-BY 4.0 derived, license-gated texts, no FZ-152 personal data.

---

## Phased execution

**Phase 0 — now, pre-data (parallel):**
1. Ethics application (blocks all human work)
2. Budget securing
3. API legal review + judge prompt/rubric freeze
4. Item-generation pipeline + manifest hashes
5. Summarizer checkpoint freeze (11 systems)
6. Code skeleton: estimators, H1–H4 gates, schema, Docker
7. Smoke test: 10 texts, pipeline-only verification

**Phase 1 — pilot (after ethics for human parts):**
8. Pilot 45–60 texts: generate, score, calibrate δ_d/k_d (20 experts)
9. Power sims → freeze min-N (≥180), H3 SE filter, spline knots, all freeze-list items
10. Frozen config + signed decision log

**Phase 2 — validation (after ethics):**
11. 100 validation texts: human ratings (120 Ss, Toloka)
12. LLM-judge validation: ICC ≥0.7, κ ≥0.6 per dim → freeze before H2
13. Dimension retention decision (fail → reduced-core rules)

**Phase 3 — confirmatory data (no peeking):**
14. Generate + score 400 main-corpus texts (28,000 summaries, 112K judge calls)
15. Apply exclusion rules mechanically; count valid confirmatory-genre texts vs frozen floor

**Phase 4 — analysis (frozen plan only):**
16. H1 check → H2 four-criteria gate → H3 TOST → H4 descriptives
17. 33 sensitivity analyses; labels per B.9

**Phase 5 — reporting:**
18. Upload all OSF materials (11.4 list); release code + de-identified data

**Critical path:** ethics → pilot freeze → judge validation gate → main corpus → analysis.
**Biggest risks:** ethics delay, Qwen Max deprecation (bridge rule ready), budget, H2 floor breach.
