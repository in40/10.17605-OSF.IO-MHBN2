## 9. Human Sample

### 9.1 Design

Human ratings are collected for the 100 validation texts. These texts are additional to the 400-text main corpus and are excluded from primary H2.

The 100 validation texts × 7 compression levels yield 700 text × level items. Each item receives 5 holistic ratings and 5 analytic ratings, for a total of 7,000 summary-level ratings and 14,000 dimension-level judgments for the analytic group.

For each validation text, one non-oracle source \(s_i\) is randomly selected before human rating collection, balanced across sources. The human-rated summary at every compression level for that text is drawn from the same source \(s_i\). All raters for a given item rate the same summary.

| Group | Items | Raters/item | Summary-level ratings | Dimension-level judgments | Participants | Items/participant | Time/item | Total time | Sessions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Holistic | 700 | 5 | 3,500 | 3,500 | 40 | ~88 | 1.5 min | ~132 min | 3 × 45 min |
| Analytic | 700 | 5 | 3,500 | 14,000 | 80 | ~44 | 3 min | ~132 min | 3 × 45 min |

**Total participants: 120.** Analytic sessions spread over 2–3 weeks. The 30-minute training session is separate from the three 45-minute rating sessions.

Session-length estimates exclude consent, instructions, training, breaks, and attention-check overhead. Pilot testing will verify feasibility.

---

### 9.2 Analytic Task

Each analytic rater rates all 4 dimensions per summary on a 1–5 scale:

| Dimension | Human task | Time |
|---|---|---|
| Facts | Rate fact preservation, 1–5 | ~45s |
| Logic | Rate logical coherence, 1–5 | ~45s |
| Author stance | Rate stance preservation, 1–5 | ~45s |
| Comprehension | Rate comprehensibility, 1–5 | ~45s |

Total: ~3 minutes per summary. Humans do not answer full QA/NLI/comprehension batteries. Global dimension ratings validate LLM-judge scores and are used in sensitivity analyses.

Human ratings are validation-only. Primary \(Q_d\) for H2 is LLM-judge.

---

### 9.3 Recruitment and Ethics

**Platform:** Russian crowdsourcing platforms — Yandex Toloka as primary, YouDo for supplementary one-off tasks, or university participant pools. Prolific is not used, as it is not a standard platform for mass cognitive ratings in the Russian Federation.

**Participant eligibility:** Residents of the Russian Federation with at least secondary specialized or higher education, equivalent to at least two years college-equivalent. Rationale: ensures ability to engage with complex texts; noted as a generalizability limitation.

**Language:** All materials — consent, instructions, rating tasks, attention checks — are provided in Russian, the native language of participants.

**Compensation:** The human-rating budget includes participant compensation, platform fees, taxes, training time, attention-check overhead, quality bonuses, and contingency. The study intentionally pays above the minimum crowdworking rate to support careful cognitive rating. The exact participant payment rate, platform fee structure, and total compensation calculation will be recorded in the frozen configuration file before data collection.

**Consent:** Electronic informed consent obtained in Russian. Explicitly states that anonymized data will be shared on OSF under CC-BY 4.0. Right to withdraw before anonymization is preserved. Consent form and participant information sheet are frozen and included in supplementary materials.

**Ethical review:** Ethics approval has not yet been obtained at the time of registration. No human data will be collected before approval is received from the relevant institutional ethics committee or equivalent local IRB. The ethics committee name, approval number, and approval date will be recorded in the frozen configuration file and OSF metadata. Ethics approval is a hard precondition for human data collection.

**Attention checks:** 3 per session, instruction-based plus obvious quality. A failed attention check excludes that session. A participant is excluded from further participation if two or more sessions fail attention checks.

**Data retention:** 5 years, then destroyed. Platform IDs stored separately from rating data.

**Personal data protection, ФЗ-152 / FZ-152:** Processing of personal data complies with Russian Federal Law No. 152-FZ "On Personal Data." The data controller is identified in the consent form; for this registration, the responsible contact is the principal investigator, Aleksandr Sorokin, unless the consent form identifies a host institution. Legal basis: informed consent. No personal data are transferred outside the Russian Federation. Only de-identified text and summary content, after PII removal, are transmitted to API providers for LLM scoring. Platform IDs are stored separately and are not included in shared datasets. No special categories of personal data are processed.

---

