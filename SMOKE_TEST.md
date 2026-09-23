# SMOKE TEST — Working Document

**Purpose:** technical verification of pipeline, APIs, hashing, storage. 10 texts.
**Exclusion rule:** smoke-test data is NOT used for calibration, pilot, or any confirmatory decision (§4.1).
**Exit criterion:** prompts/rubrics/schemas/checkpoints frozen (hashed + uploaded to OSF) before pilot starts.
**Linked registration:** 10.17605/OSF.IO/MHBN2 · blocks: 04_sampling, 07_llm_judge, 09_pilot

---

## 0. Status

| Field | Value |
|---|---|
| Phase | not started |
| Started | — |
| Frozen | — |
| Code hash | — |

---

## 1. Models & endpoints

Record exact IDs/terms as verified. Nothing enters pilot unfrozen.

| Role | Model | Endpoint / API label | Checkpoint ID | Terms: training use | Retention | Verified (date) |
|---|---|---|---|---|---|---|
| Item gen | Qwen3.8 Flash Next (local) | local | w4b hash: `9c116bbc…` | n/a (local) | n/a | — |
| Judge | Qwen 3.8 Max | TODO | TODO | TODO | TODO | — |
| Summarizer | Qwen3.7 Plus | TODO | TODO | TODO | TODO | — |
| Summarizer | DeepSeek-V4 | TODO | TODO | TODO | TODO | — |
| Summarizer | Yandex Alisa | TODO | TODO | TODO | TODO | — |
| Summarizer | Sber GigaChat | TODO | TODO | TODO | TODO | — |
| Hybrid | TextRank + BART (local) | local | TODO hash | n/a | n/a | — |
| Extractive | TextRank (local) | local | TODO hash | n/a | n/a | — |

**Smoke scope:** 10 texts × 11 systems × 7 levels = 770 summaries + item-gen + judge calls (~3,080 judge calls at 4 dims).

---

## 2. Smoke texts (10)

Goal: exercise every source family + length boundary. Smoke texts need NOT be a balanced sample — coverage beats sampling rigor here.

### 2.1 Allocation

| Genre | n | Source family | How to obtain | License status |
|---|---:|---|---|---|
| News | 3 | Lenta.ru / TASS | Lenta.ru full dump (HF/Kaggle mirror) or direct scrape; pick 3 articles 300–800 words | TODO verify (dump mirrors often CC BY-NC — check; TASS ToS) |
| Scientific | 3 | CyberLeninka OA | Filter OA + CC BY, 150–800 words; include 1 short (~150 w) abstract to test r=0.05 instability | CC BY — high confidence, record per-item |
| Instruction | 2 | Federal/municipal portals | Self-contained procedural sections (gosuslugi-style help, ministry guides) | TODO verify per source |
| Fiction | 1 | Public domain (Gutenberg RU / RSL) | Self-contained scene/passage, 300–800 words | PD — safe |
| Dialogue | 1 | Open RU dialogue corpus | Verified permissive-license corpus only; concatenated self-contained segment | TODO identify + verify |

### 2.2 Length coverage (stress the r-grid)

- 2× ~300 words (floor), 4× ~500 words (mid), 3× ~800 words (ceiling), 1× ~150 words scientific (short-abstract edge case)
- At r=0.05: 800-word text → 40-word summary — hardest case, must be present
- (corrected 2026-09-21 to match SMOKE_TEXTS_SPEC.md length table: 1/2/4/3)

### 2.3 Per-text checklist (repeat for each of 10)

- [ ] Raw text saved unmodified (UTF-8), source URL + retrieval date recorded
- [ ] License snapshot/proof saved (screenshot or license field)
- [ ] Word count via whitespace tokenization; within genre bounds
- [ ] Self-containedness check (solo judgment for smoke; 2-rater consensus rule applies from pilot)
- [ ] Dedup: 3-gram overlap < 95% vs other smoke texts
- [ ] PII screen: regex (ФИО, phone, address, passport, SNILS, INN) + manual pass
- [ ] Assigned text_id: `SMK-{genre_code}-{nn}` (e.g. `SMK-SCI-01`)

### 2.4 Storage

```
smoke/texts/{text_id}.txt          # raw
smoke/texts/{text_id}.meta.json    # url, license, wordcount, pii_check, hashes
```

### 2.5 Working log

<!-- smoke_collector:table:start -->
| text_id | жанр | источник | wordcount | корзина | лицензия | PII | дубликаты | самодостаточность |
|---|---|---|---|---|---|---|---|---|
| SMK-DIA-01 | dia | inkoziev/Conversations (RLDD) | 750 | ~800 | CC BY 4.0 (inkoziev/Conversations, per d | ok | ok | ok |
| SMK-FIC-01 | fic | ru.wikisource.org | 464 | ~500 | Public domain (Project Gutenberg) | ok | ok | ok |
| SMK-INS-01 | ins | Процедурная страница (gov) | 297 | ~300 | Public government reference material (fr | ok | ok | ok |
| SMK-INS-02 | ins | Процедурная страница (gov) | 471 | ~500 | Public government reference material (fr | ok | ok | ok |
| SMK-NEWS-01 | news | Lenta.ru (dump v1.1) | 302 | ~300 | CC BY-NC 4.0 (Lenta.Ru-News-Dataset v1.1 | ok | ok | ok |
| SMK-NEWS-02 | news | Lenta.ru (dump v1.1) | 451 | ~500 | CC BY-NC 4.0 (Lenta.Ru-News-Dataset v1.1 | ok | ok | ok |
| SMK-NEWS-03 | news | Lenta.ru (dump v1.1) | 731 | ~800 | CC BY-NC 4.0 (Lenta.Ru-News-Dataset v1.1 | ok | ok | ok |
| SMK-SCI-01 | sci | CyberLeninka | 170 | ~150 | CC BY 4.0 | ok | ok | ok |
| SMK-SCI-02 | sci | CyberLeninka | 508 | ~500 | CC BY 4.0 | ok | ok | ok |
| SMK-SCI-03 | sci | CyberLeninka | 766 | ~800 | CC BY 4.0 | ok | ok | ok |
<!-- smoke_collector:table:end -->

---

## 3. Prompts

Iterate freely here during smoke test. On freeze: hash + OSF upload, no edits during confirmatory phase.

### 3.1 Item-generation prompt (Qwen3.8 Flash Next, RU)
```
TODO — paste working version here, version-stamp each iteration
```
- v0.1 (date): initial
- changelog:

### 3.2 Judge prompt (Qwen 3.8 Max, RU)
```
TODO — one call per summary per dimension, items batched
```
- v0.1 (date): initial
- changelog:

### 3.3 Summarization prompts (per system, RU, length instruction per level)
```
TODO — shared template + per-system adaptations
```
- v0.1 (date): initial
- changelog:

---

## 4. JSON schemas

### 4.1 Item-gen output schema
```json
TODO
```

### 4.2 Judge output schema
```json
TODO
```
Parsing: retry once → mark missing. Refusals: retry once → mark missing. Log refusal rate by genre/level/source.

---

## 5. Pipeline

- [ ] Hashing scheme (algo, what's hashed: raw output, normalized, prompt+params)
- [ ] Storage layout (dir structure, naming: text_id/system/level)
- [ ] Retry logic: 1 API retry per attempt; max 2 content-generation attempts (1 + 1 length-regen)
- [ ] Seeds: fixed per stochastic system; seed streams recorded
- [ ] Non-determinism documentation
- [ ] Refusal/missing tracking

---

## 6. Run log

Append dated entries: what ran, what broke, what changed.

- (date) — TODO: first entry

---

## 7. Issues / findings

| # | Found | Component | Description | Resolution | Status |
|---|---|---|---|---|---|
| | | | | | |

---

## 8. Freeze checklist (exit)

- [ ] All checkpoint IDs pinned + recorded (§1 complete)
- [ ] Terms verified for all API models (§1 complete)
- [ ] Prompts final, version-stamped (§3)
- [ ] Schemas final (§4)
- [ ] Pipeline passes: 770 summaries generated, hashed, stored
- [ ] Refusal/parse-failure rates acceptable
- [ ] All artifacts hashed; hashes in decision log
- [ ] Uploaded to OSF as supplementary materials
- [ ] Decision log entry signed + dated
