# Smoke Test Texts — Collection Instructions

**What for:** technical smoke test (10 texts). Data never used for calibration/confirmatory decisions.
**Language:** all texts Russian. **Format:** plain text, UTF-8, no HTML/markup.

---

## Overall requirements (every text)

1. Russian, self-contained: understandable without outside context; no dangling references ("продолжение следует", "как упоминалось выше" to missing parts).
2. Whitespace word count within genre bounds (see below).
3. License permits processing + derived works for research. Save proof (license page URL/screenshot).
4. No PII: names+contacts, phone, address, passport/SNILS/INN, emails. If found — pick another text.
5. Not an excerpt cut mid-scene/mid-thought; natural boundaries.
6. No near-duplicates among the 10 (3-gram overlap < 95%).
7. Save raw as `{text_id}.txt` + metadata `{text_id}.meta.json` (url, date, license, wordcount).

---

## Per-genre spec

### News — 3 texts, 300–800 words
- Straight news articles: reportage, announcements, event coverage.
- Avoid: opinion columns, interviews, listicles, clickbait, breaking-news fragments < 300 w.
- Source: Lenta.ru dump mirror or TASS. Verify license before bulk use.
- Pick 1 short (~300), 1 mid (~500), 1 long (~800).

### Scientific — 3 texts, 150–800 words
- Open-access only, CC BY license (CyberLeninka filter).
- Mix: 1 short abstract-style (~150 w, edge case for r=0.05), 1 structured abstract+ (~400 w), 1 short article section (~700–800 w).
- Avoid: papers with heavy math notation/formulas (tokenizer noise), reference lists, tables.
- Prefer: humanities/social science/life science prose — text-dense, low formula.

### Instruction — 2 texts, 200–600 words
- Single self-contained procedural task: "how to apply for X", "how to fill Y", step-by-step guide.
- Must have: ordered steps or clear procedure; concrete objects/actions.
- Avoid: legal boilerplate, FAQ without procedure, portal navigation text, anything requiring login context.
- Source: gosuslugi-style help pages, ministry/municipal guides.

### Fiction — 1 text, 300–800 words
- Public domain Russian classic (Gutenberg RU, RSL digital).
- Self-contained scene or passage: has setting + action, reads complete.
- Avoid: poetry, chapter openings that only set up later content, very archaic orthography (pre-1918 unless normalized).

### Dialogue — 1 text, 300–800 words
- Open Russian dialogue corpus with verified permissive license.
- Concatenated segment = one conversation or coherent exchange; self-contained topic.
- Avoid: movie subtitles (license risk), chat logs with PII, cross-talk-heavy transcripts.

---

## Length distribution across all 10

| Bucket | n | Why |
|---|---:|---|
| ~150 w | 1 | short-abstract edge, r=0.05 → 7-word summary |
| ~300 w | 2 | floor behavior |
| ~500 w | 4 | mid-range bulk |
| ~800 w | 3 | ceiling; r=0.05 → 40-word summary = hardest case |

---

## Do NOT

- Do not use texts requiring paywall/login.
- Do not use CC BY-NC/ND unless confirmed acceptable for the whole pipeline.
- Do not use machine-translated texts.
- Do not edit texts after saving (trimming = new file + note).
- Do not pick texts from the same author/topic twice.

## Deliverable

10 × (`{text_id}.txt` + `{text_id}.meta.json`), filled §2.5 working log in SMOKE_TEST.md.
Naming: `SMK-{NEWS|SCI|INS|FIC|DIA}-{01..}`.
