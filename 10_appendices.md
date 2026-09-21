# Appendix A: Feasibility Estimates

Appendix A estimates the non-pilot main and validation stages. Pilot costs are estimated separately and are covered by the contingency budget. Costs are reported in USD for comparability; local currency equivalents and platform-specific fee structures will be recorded in the frozen pilot configuration file.

| Component | Units | Est. calls | Est. cost | Est. runtime |
|---|---:|---:|---:|---:|
| Summary generation | 38,500 | ~38,500 | ~$800–1,500 | 3–5 days |
| LLM-judge scoring | 38,500 × 4 dim | ~154,000 | ~$1,000–2,000 | 4–7 days |
| Item generation, Qwen3.8 Flash Next, local | 500 texts | ~15,500 item-level calls or ~2,000 batched calls | compute only; electricity/hardware amortization estimated in frozen budget | ~24h |
| Human ratings, 120 participants, including compensation, platform fees, training, quality bonuses, taxes, and buffer | 7,000 | — | ~$7,000–7,500 | 2–3 weeks |
| Bootstrap, 2,000 iter; dry run required | — | — | compute | 72h+ |
| **Total** | | **~197,000–230,000** | **~$9,000–11,500** | **~8 weeks** |

Total call estimates include primary calls, one retry for refusals/parsing failures, validation calls, and anticipated re-runs. The exact number of calls may vary depending on API failures and regeneration attempts.

The 10-text dry run referenced in planning is a technical smoke test only. It is not the registered pilot.

Contingency: 20% budget buffer. Bootstrap dry-run on 20–50 texts. All fallback decisions are made before inspecting H2/H3 results and are recorded in the decision log.

Because the item generator is hosted locally, the cost is compute/hardware rather than API cost. The estimated API-call count and token usage will be recorded in the frozen configuration file. If local hosting proves infeasible, a registered amendment will specify an alternative local-compatible model with equivalent capacity and no overlap with summarizers/judge.

---

# Appendix B: Data Dictionary

This appendix defines the principal variables, missingness codes, and derived fields in the shared analysis dataset.

## B.1 Text-level identifiers and sampling

| Variable | Definition | Type | Allowed values / format | Missing code |
|---|---|---|---|---|
| `text_id` | Unique pseudonymized text identifier | string | `T0001`–`T0500` | — |
| `corpus_part` | Whether text is pilot, main, or validation | categorical | `pilot`, `main`, `validation` | — |
| `genre` | Text genre | categorical | `news`, `scientific`, `procedural`, `fiction`, `dialogue` | — |
| `confirmatory_genre` | Whether genre is confirmatory | binary | 0/1 | — |
| `source_corpus` | Source corpus or dataset | string | controlled vocabulary | `unknown` |
| `word_count` | Whitespace token count | integer | ≥1 | `NA` |
| `pii_screened` | PII screening completed | binary | 0/1 | — |
| `license_ok_share_text` | Full text may be shared | binary | 0/1 | `unknown` |
| `license_ok_share_summary` | Summary output may be shared | binary | 0/1 | `unknown` |

---

## B.2 Summary-level generation variables

| Variable | Definition | Type | Allowed values / format | Missing code |
|---|---|---|---|---|
| `summary_id` | Unique summary identifier | string | `S_...` | — |
| `text_id` | Parent text | string | — | — |
| `system_id` | Summary system ID | categorical | 1–11 | — |
| `system_name` | Summary system name | string | controlled vocabulary | — |
| `oracle_flag` | Oracle system indicator | binary | 0/1 | — |
| `target_r` | Target length ratio | numeric | 0.9, 0.7, 0.5, 0.3, 0.2, 0.1, 0.05 | — |
| `actual_r` | Observed length ratio | numeric | >0 | `NA` |
| `length_deviation` | Relative length deviation | numeric | ≥0 | `NA` |
| `regeneration_flag` | Length regeneration occurred | binary | 0/1 | — |
| `generation_attempt` | Content generation attempt number | integer | 1/2 | — |
| `api_retry_flag` | API transmission retry occurred | binary | 0/1 | — |
| `summary_hash` | SHA-256 hash of summary file | string | hexadecimal | `NA` |
| `generation_seed_stream` | Seed stream identifier | string | controlled vocabulary | — |
| `non_determinism_flag` | Non-deterministic generation documented | binary | 0/1 | — |
| `summary_valid` | Summary valid under exclusion rules | binary | 0/1 | — |
| `invalid_reason` | Reason if invalid | categorical | `length`, `judge_refusal`, `parse_failure`, `missing_core`, `other` | `NA` |

---

## B.3 LLM-judge dimension scores

| Variable | Definition | Type | Allowed values / format | Missing code |
|---|---|---|---|---|
| `judge_model` | Judge model version | string | controlled vocabulary | — |
| `judge_call_id` | Unique judge call ID | string | — | — |
| `judge_refusal` | Judge refused | binary | 0/1 | — |
| `judge_parse_failure` | JSON parsing failed | binary | 0/1 | — |
| `facts_score_raw` | Facts proportion correct | numeric | 0–1 | `NA` |
| `logic_score_raw` | Logic proportion entailment | numeric | 0–1 | `NA` |
| `stance_score_raw` | Stance proportion agreement | numeric | 0–1 | `NA` |
| `comprehension_score_raw` | Comprehension proportion correct | numeric | 0–1 | `NA` |
| `facts_item_count_pass` | Number of facts items passed | integer | 0–10 | `NA` |
| `logic_item_count_pass` | Number of logic items passed | integer | 0–8 | `NA` |
| `stance_item_count_pass` | Number of stance items passed | integer | 0–5 | `NA` |
| `comprehension_item_count_pass` | Number of comprehension items passed | integer | 0–8 | `NA` |
| `facts_pass` | Facts pass under frozen \(k_d\) | binary | 0/1 | `NA` |
| `logic_pass` | Logic pass under frozen \(k_d\) | binary | 0/1 | `NA` |
| `stance_pass` | Stance pass under frozen \(k_d\) | binary | 0/1 | `NA` |
| `comprehension_pass` | Comprehension pass under frozen \(k_d\) | binary | 0/1 | `NA` |
| `comprehension_score_corrected` | Chance-corrected comprehension score | numeric | 0–1 | `NA` |

---

## B.4 Human validation ratings

| Variable | Definition | Type | Allowed values / format | Missing code |
|---|---|---|---|---|
| `rater_id` | Pseudonymized rater ID | string | — | — |
| `rater_group` | Holistic or analytic | categorical | `holistic`, `analytic` | — |
| `session_id` | Session identifier | string | — | — |
| `item_id` | Validation text × level item | string | — | — |
| `rated_source` | Source of rated summary | categorical | non-oracle source names | — |
| `holistic_rating` | Holistic rating | integer | 1–5 | `NA` |
| `holistic_yes_4_5` | Dichotomized holistic rating | binary | 0/1 | `NA` |
| `holistic_yes_5_only` | Sensitivity dichotomization | binary | 0/1 | `NA` |
| `analytic_facts_rating` | Human analytic facts rating | integer | 1–5 | `NA` |
| `analytic_logic_rating` | Human analytic logic rating | integer | 1–5 | `NA` |
| `analytic_stance_rating` | Human analytic stance rating | integer | 1–5 | `NA` |
| `analytic_comprehension_rating` | Human analytic comprehension rating | integer | 1–5 | `NA` |
| `attention_check_failed` | Attention check failed in session | binary | 0/1 | — |
| `time_on_page_sec` | Time on item | numeric | ≥0 | `NA` |
| `rating_order` | Order of item in session | integer | ≥1 | `NA` |

---

## B.5 Derived threshold variables (H2 Primary: Observed-Grid)

| Variable | Definition | Type | Allowed values / format | Missing code |
|---|---|---|---|---|
| `r_facts_star_grid` | Facts threshold (grid) | numeric | 0.05–0.9 | `CENS_RIGHT`, `CENS_LEFT`, `UNDEF` |
| `r_logic_star_grid` | Logic threshold (grid) | numeric | 0.05–0.9 | `CENS_RIGHT`, `CENS_LEFT`, `UNDEF` |
| `r_stance_star_grid` | Stance threshold (grid) | numeric | 0.05–0.9 | `CENS_RIGHT`, `CENS_LEFT`, `UNDEF` |
| `r_comprehension_star_grid` | Comprehension threshold (grid) | numeric | 0.05–0.9 | `CENS_RIGHT`, `CENS_LEFT`, `UNDEF` |
| `r_max_grid` | Max full-ensemble dimension threshold (grid) | numeric | 0.05–0.9 | `UNDEF` |
| `r_all_model_star_grid` | Full-ensemble aggregate threshold (grid) | numeric | 0.05–0.9 | `CENS_RIGHT`, `CENS_LEFT`, `UNDEF` |
| `r_all_ind_star_grid` | Independence-baseline threshold (grid) | numeric | 0.05–0.9 | `CENS_RIGHT`, `CENS_LEFT`, `UNDEF` |
| `delta_all_grid` | Descriptive aggregate gap (grid) | numeric | real | `UNDEF` |
| `delta_excess_grid` | Excess bottleneck (grid) | numeric | real | `UNDEF` |
| `threshold_se_r_max` | SE of \(r_{\max,i}\) | numeric | ≥0 | `NA` |
| `threshold_se_r_all` | SE of \(r_{\text{all},i}\) | numeric | ≥0 | `NA` |
| `stable_threshold_flag` | Stability filter passed | binary | 0/1 | — |
| `model_consistency_flag` | Model consistency check passed | binary | 0/1 | — |
| `primary_h2_eligible` | Eligible for primary H2 | binary | 0/1 | — |
| `pe_iqr_obs` | Observed primary practical-effect metric | numeric | real | `UNDEF` |
| `h2_p_perm_raw` | Raw one-sided permutation p-value for H2 | numeric | 0–1 | `NA` |
| `h2_p_perm_holm` | Holm-adjusted permutation p-value for H2 | numeric | 0–1 | `NA` |
| `pe_iqr_ci_lower` | One-sided 95% BCa lower bound for \(PE_{\text{IQR}}\) | numeric | real | `NA` |

---

## B.6 H3 Derived threshold variables (Primary: Continuous Interpolated)

| Variable | Definition | Type | Allowed values / format | Missing code |
|---|---|---|---|---|
| `validation_text_flag` | Text is validation text | binary | 0/1 | — |
| `rated_source` | Selected validation source | categorical | non-oracle source names | — |
| `r_facts_match_star` | Source-matched facts threshold (cont.) | numeric | 0.05–0.9 | `CENS_RIGHT`, `CENS_LEFT`, `UNDEF` |
| `r_logic_match_star` | Source-matched logic threshold (cont.) | numeric | 0.05–0.9 | `CENS_RIGHT`, `CENS_LEFT`, `UNDEF` |
| `r_stance_match_star` | Source-matched stance threshold (cont.) | numeric | 0.05–0.9 | `CENS_RIGHT`, `CENS_LEFT`, `UNDEF` |
| `r_comprehension_match_star` | Source-matched comprehension threshold (cont.) | numeric | 0.05–0.9 | `CENS_RIGHT`, `CENS_LEFT`, `UNDEF` |
| `r_max_match` | Max source-matched dimension threshold (cont.) | numeric | 0.05–0.9 | `UNDEF` |
| `r_all_match_star` | Source-matched aggregate threshold (cont.) | numeric | 0.05–0.9 | `CENS_RIGHT`, `CENS_LEFT`, `UNDEF` |
| `r_hol_star` | Holistic threshold (cont.) | numeric | 0.05–0.9 | `CENS_RIGHT`, `CENS_LEFT`, `UNDEF` |
| `r_hol_star_se` | SE of holistic threshold | numeric | ≥0 | `NA` |
| `r_all_match_star_se` | SE of source-matched aggregate threshold | numeric | ≥0 | `NA` |
| `h3_difference` | \(r_{\text{hol}}^* - r_{\text{all,match}}^*\) (cont.) | numeric | real | `UNDEF` |
| `h3_pair_se` | Paired SE of H3 difference | numeric | ≥0 | `NA` |
| `h3_eligible` | Eligible for primary H3 | binary | 0/1 | — |
| `h3_p_lower` | Lower one-sided TOST percentile p-value | numeric | 0–1 | `NA` |
| `h3_p_upper` | Upper one-sided TOST percentile p-value | numeric | 0–1 | `NA` |
| `h3_p_raw` | Raw combined TOST p-value | numeric | 0–1 | `NA` |
| `h3_p_holm` | Holm-adjusted TOST p-value | numeric | 0–1 | `NA` |
| `h3_ci_lower` | Lower bound of 95% BCa CI for \(\bar D\) | numeric | real | `NA` |
| `h3_ci_upper` | Upper bound of 95% BCa CI for \(\bar D\) | numeric | real | `NA` |

---

## B.7 Conflict variables

| Variable | Definition | Type | Allowed values / format | Missing code |
|---|---|---|---|---|
| `C_signed` | Primary signed negative log odds-ratio conflict | numeric | real, clipped | `UNDEF` |
| `C_signed_adj` | Source-adjusted signed conflict | numeric | real | `UNDEF` |
| `C_signed_crossfit` | Cross-fitted signed conflict | numeric | real | `UNDEF` |
| `C_deficit_positive` | Descriptive nonnegative deficit conflict | numeric | ≥0 | `UNDEF` |
| `C_pair_estimable_frac` | Fraction of estimable dimension-level pairs for signed conflict | numeric | 0–1 | `NA` |
| `C_adj_estimable_frac` | Fraction of estimable source-adjusted pairs | numeric | 0–1 | `NA` |
| `C_crossfit_estimable_frac` | Fraction of estimable cross-fitted pairs | numeric | 0–1 | `NA` |
| `mean_pass_all` | Mean pass probability across core dimensions and levels included in conflict | numeric | 0–1 | `NA` |

---

## B.8 Exclusion and missingness codes

| Code | Meaning |
|---|---|
| `NA` | Missing value |
| `CENS_RIGHT` | Right-censored at 0.9 |
| `CENS_LEFT` | Left-censored at 0.05 |
| `UNDEF` | Undefined because of insufficient estimability or model failure |
| `EXCL_INVALID_SUMMARY` | Excluded due to invalid summary |
| `EXCL_UNSTABLE_SE` | Excluded due to threshold SE > 0.15 |
| `EXCL_MODEL_CONSISTENCY` | Excluded due to model-consistency failure |
| `EXCL_UNDEFINED_C` | Excluded due to undefined conflict measure |
| `EXCL_ATTENTION` | Human session excluded due to attention-check failure |
| `EXCL_LICENSE` | Excluded due to licensing restriction |
| `EXCL_PII` | Excluded due to PII concern |
| `EXCL_JUDGE` | Excluded due to judge failure or bias flag |
| `EXCL_H3_SE_FILTER` | Excluded from H3 due to SE filter |
| `EXCL_INTERPOLATION_FAILURE` | Excluded due to interpolated-threshold inversion failure |
| `EXCL_OTHER` | Excluded for another documented reason |

---

## B.9 Analysis flags

| Variable | Definition | Type | Allowed values |
|---|---|---|---|
| `analysis_set_h2` | Included in primary H2 | binary | 0/1 |
| `analysis_set_h3` | Included in primary H3 | binary | 0/1 |
| `analysis_set_descriptive` | Included in descriptive analyses | binary | 0/1 |
| `analysis_set_exploratory` | Included in exploratory analyses | binary | 0/1 |
| `sensitivity_flag` | Used in sensitivity analysis only | binary | 0/1 |
| `h2_support_label` | H2 outcome label | categorical | `supported`, `supported_spec_sensitive`, `inconclusive`, `exploratory`, `not_evaluated` |
| `h3_support_label` | H3 outcome label | categorical | `supported`, `inconclusive`, `exploratory`, `not_evaluated` |

---

**End of pre-registration. Version 3.4 (Combined).**
