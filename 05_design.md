## 5. Variables

### 5.1 Independent Variables

| Variable | Levels | Type |
|---|---:|---|
| Genre | 5 | Between-text |
| Length ratio \(r\) | 7: {0.9, 0.7, 0.5, 0.3, 0.2, 0.1, 0.05} | Within-text |
| Summary source | 11 systems | Within-text, within-\(r\) |
| Evaluation method | Holistic / Analytic | Between-evaluator |
| Validation rated source \(s_i\) | 1 per validation text | H3 design variable |

---

### 5.2 Dependent Variables

- **Holistic:** \(r_{\text{hol},i}^*\) at \(\tau_{\text{hol}} = 0.5\).
- **Analytic:** \(r_{d,i}^*\), text-specific; \(r_d^*\), population, descriptive.
- **Aggregate H2:** \(r_{\text{all},i}^*\), full-ensemble estimand; \(r_{\text{all,model},i}^*\), estimator.
- **Aggregate H3:** \(r_{\text{all,match},i}^*\), source-matched analytic comparator.
- **Conflict:** \(C_i^{\pm}\), primary signed conflict; \(C_i^{\text{adj}}\), source-adjusted signed conflict; \(C_i^{+}\), descriptive nonnegative deficit conflict.
- **Gaps:** \(\Delta_{\text{all},i}\), descriptive; \(\Delta_{\text{excess},i}\), confirmatory H2; \(D_i = r_{\text{hol},i}^* - r_{\text{all,match},i}^*\), H3 paired difference.

---

### 5.3 Additional Measured Variables

Actual length ratio, length deviation, regeneration indicator, judge refusal indicator, parsing failure indicator, text-level censoring indicators, validation subset indicator, validation source indicator, exclusion reasons, seed-stream identifiers.

---

## 6. Design Plan

### 6.1 Blinding

- Holistic evaluators unaware of analytic dimensions.
- Analytic evaluators: instructions do not mention holistic meaning-preservation.
- LLM-judge prompts contain no hypotheses.
- Analyst receives coded IDs.
- Dimension order randomized for analytic raters.
- Source labels and compression level hidden from raters.
- Presentation order of validation items randomized within rater sessions according to the frozen seed scheme.

---

### 6.2 Presentation

The interface displays the original text and the summary side by side. The original appears in the left pane and the summary in the right pane. Raters may scroll both texts and use search. Original text length is not displayed.

- Time on page recorded.
- Raters can change answers before submitting.
- Raters cannot see other ratings.
- Raters may encounter multiple compression levels of the same validation text; presentation order is randomized. Potential repetition effects will be examined descriptively.

Session-length estimates exclude consent, instructions, training, breaks, and attention-check overhead. The pilot will assess actual session duration. If pilot session duration exceeds the planned budget or fatigues raters, the number of items per session will be reduced or sessions will be restructured before confirmatory human data collection.

---

### 6.3 Manipulation and technical checks

Manipulation and technical checks include:

- length-deviation checks;
- regeneration flags;
- SHA-256 summary hashes;
- attention checks;
- judge refusal rates;
- JSON parsing failure rates;
- item-validation agreement;
- model-consistency checks (\(r_{\text{all}}^* \ge r_{\max}^* - \eta\));
- source-balance checks in validation assignment.

---

