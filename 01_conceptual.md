## Conceptual Overview

We operationalize meaning preservation in two ways:

- **Construct A:** a holistic human judgment of whether a summary conveys the original meaning;
- **Construct B:** an analytic aggregate threshold requiring simultaneous preservation of four core dimensions.

The **descriptive** bottleneck gap is:

\[
\Delta_{\text{all},i} = r_{\text{all},i}^* - \max_d r_{d,i}^*
\]

This asks whether preserving all dimensions simultaneously requires more length than the single most fragile dimension. This quantity is reported descriptively.

The **primary confirmatory** bottleneck outcome is the **excess** gap:

\[
\Delta_{\text{excess},i} = r_{\text{all},i}^* - r_{\text{all,ind},i}^*
\]

This asks whether the aggregate threshold exceeds what would be expected if the dimensions were conditionally independent given source. This isolates the conflict-related component of the bottleneck.

H2 tests whether signed negative dependence, or conflict, predicts \(\Delta_{\text{excess},i}\). H3 tests whether the holistic threshold and the source-matched analytic aggregate threshold are practically equivalent within a fixed tolerance.

**Note on refinement:** This is a refinement of the original bottleneck hypothesis. The confirmatory test is not simply whether \(r_{\text{all}}^*\) exceeds \(\max_d r_d^*\); that descriptive gap is reported separately as \(\Delta_{\text{all}}\). The primary confirmatory hypothesis concerns the excess beyond a conditional-independence baseline.

**Note on H3 alignment:** Because human holistic ratings are collected for one summary source per validation text, the primary H3 comparison uses a **source-matched analytic aggregate threshold**. To avoid reducing equivalence to exact equality on a coarse compression grid, primary H3 uses **model-interpolated continuous thresholds**.

**Note on H2 association:** H2 is an association/model-consistency test, not a causal test. Because the conflict measure and the aggregate-threshold model are both based on pass/fail dependence, confirmatory interpretation of H2 is conditional on the pre-specified permutation test and key sensitivity checks.

---

## Abbreviations

| Abbreviation | Meaning |
|---|---|
| AC1 | Gwet's Agreement Coefficient 1 |
| API | Application Programming Interface |
| BCa | Bias-Corrected and Accelerated |
| CC-BY | Creative Commons Attribution |
| CI | Confidence Interval |
| FWER | Family-Wise Error Rate |
| HC3 | Heteroskedasticity-Consistent standard errors (MacKinnon-White) |
| ICC | Intraclass Correlation Coefficient |
| IQR | Interquartile Range |
| IRB | Institutional Review Board |
| JSON | JavaScript Object Notation |
| LLM | Large Language Model |
| LPM | Linear Probability Model |
| MAR | Missing at Random |
| MCQ | Multiple-Choice Question |
| MICE | Multiple Imputation by Chained Equations |
| NLI | Natural Language Inference |
| NLP | Natural Language Processing |
| OLS | Ordinary Least Squares |
| OR | Odds Ratio |
| OSF | Open Science Framework |
| PE | Practical-Effect Metric |
| PII | Personally Identifiable Information |
| QA | Question Answering |
| SD | Standard Deviation |
| SE | Standard Error |
| TOST | Two One-Sided Tests |
| FZ-152 | Russian Federal Law No. 152-FZ on Personal Data |

---

## 1. Study Information

### 1.1 The Bottleneck Hypothesis

**The Bottleneck Hypothesis states that preserving all core dimensions simultaneously requires a larger summary-length threshold than preserving the most fragile single dimension, and that the excess beyond an independence baseline is predicted by negative dependence, or conflict, among dimensions.**

The confirmatory bottleneck test is not simply whether \(r_{\text{all}}^*\) exceeds \(\max_d r_d^*\). That descriptive gap, \(\Delta_{\text{all}}\), is reported separately. The primary confirmatory hypothesis concerns the excess aggregate threshold beyond a conditional-independence baseline, \(\Delta_{\text{excess}}\), and whether this excess is predicted by signed conflict.

---

### 1.2 Construct Validity Note

> This study tests a multidimensional operationalization of meaning-preservation. The four core dimensions are treated as measurable proxies, not as an exhaustive theory of meaning. Findings are conditional on this operationalization and the selected summary-source ensemble. "Meaning-preservation" in this protocol refers to operational scores on these four dimensions, not to a philosophical claim about meaning.

---

