# Operations Runbook — Smoke · Pilot · Main

Step-by-step for running each corpus phase with the TUI (and CLI where noted).
Read the phase you're in before starting.

---

## The three phases at a glance

| Phase | Size | Purpose | Data dir | Self-containedness |
|---|---|---|---|---|
| **Smoke** | 10 (2/genre) | Validate the whole plumbing end-to-end | `smoke/` | solo judgment |
| **Pilot** | 50 (10/genre) | Calibration + feasibility gate; derive power params | `pilot_data/texts/` | **2 raters + consensus** |
| **Main** | 400 (confirmatory) | The real study corpus | `pilot_data/main/` | see §3 note |

Splits are **disjoint** — no text appears in more than one. Prefixes:
`PLT-` pilot, `VAL-` validation, `MRN-` main.

---

## Phase 0 — Setup (once)

```bash
cd /root/RESEARCH
export SC_KEY="sk-..."          # LLM endpoint key (never committed)
.venv/bin/python -m pytest tests/ -q   # expect all green before you start
```

Open the TUI:

```bash
./run_tui.sh                    # or: .venv/bin/python -m smoke_tui
```

Configure once (**Home → Configure**): summarizer model(s), judge model, dirs.
`ctrl+s` saves to `smoke_tui_settings.json`. The pilot pipeline reuses these
settings but redirects the **directories** to `pilot_data/`.

---

## Phase 1 — SMOKE  (Home → **SMOKE**)

**Goal:** prove collect → validate → items → summarize → score → browse all
work on a tiny corpus before scaling. Do this first, every pipeline change.

1. **Collect corpus** — pulls the 10 smoke texts → `smoke/texts/`.
2. **Validate corpus** — runs the 9 checks. Must print **ALL CHECKS PASSED**.
3. **Generate items** — frozen QA/MCQ/NLI/stance items from the texts
   → `smoke/items/` + `manifest.json`.
4. **Summarize (r-grid)** — runs each configured summarizer across the r-grid
   → `smoke/summaries/<system>/...`.
5. **Score summaries** — **Judge (rubric)** → `.judge.json`;
   **QA-accuracy (items)** → `.qa.json`.
6. **Browse results** — pick a summary → source + summary + judge + item scores.

**Gate before pilot:** smoke passes end-to-end, and the frozen artifacts
(prompts, rubrics, model/checkpoint IDs) are hashed + uploaded to OSF
(see `SMOKE_TEST.md` §8).

> Smoke is **frozen**. Re-running it must stay byte-identical. Scaling for the
> pilot does NOT change smoke defaults.

---

## Phase 2 — PILOT  (Home → **PILOT**)

**Goal:** a larger balanced sample to (a) confirm the sampler, (b) get a
**2-rater self-containedness** check + disagreement rate, (c) freeze the pilot
config and derive power-analysis parameters. Pilot texts are **excluded** from
the main corpus.

### 1. Build sample
Pick **Split = pilot**, **Seed = 42**, **Scale = 10** → **Build**.
Live log shows the run. Result: 50 texts → `pilot_data/texts/` (`PLT-*`).
The status panel shows per-genre counts.

### 2. Rate self-containedness  ← the human gate
**Two raters, independently.** For each rater:
- Enter the rater id (e.g. `alice`) → **Start rating**.
- Read each text fully. Press **y** (self-contained) or **n** (not).
  - **n requires a note** (what's missing/broken).
  - **s** skips for now.
- When alice finishes, run it again as **bob** (a second, independent pass).

Read **`pilot/RATER_INSTRUCTIONS.md`** before rating — it defines the criteria.

### 3. Generate items (from texts)
**Generate QA/MCQ/NLI/stance** — creates the frozen measurement items from the
pilot texts → `pilot_data/items/` + `manifest.json` (SHA-256). Run once per
corpus; items are reused for every summary.

### 4. Summarize (r-grid)
**Summarize pilot texts** — runs the same summarizers as smoke, but on
`pilot_data/texts/` → `pilot_data/summaries/`.

### 5. Score summaries
Two independent scoring methods, both per summary:
- **Judge (rubric)** — holistic 4-dim scores → `.judge.json`.
- **QA-accuracy (items)** — answers the frozen items using ONLY the summary
  → `.qa.json` (QA-accuracy, MCQ chance-corrected, NLI, stance).

### 6. Browse
- **Browse texts** — all pilot texts with word count + rating status.
- **Browse results** — source + summary + judge scores + item-based scores.

**Report / disagreement rate:** the status panel shows accept / reject /
disagree / incomplete + the **disagreement rate** (pre-reg §4.2:54).
`disagree` items need adjudication (third rater). CLI:
```bash
.venv/bin/python -m pilot.raters report
```

**Gate before main:** pilot self-containedness has 2-rater consensus, the
disagreement rate is recorded, and the pilot config (checkpoints) is frozen.

---

## Phase 3 — MAIN  (Home → **MAIN**)

**Goal:** the ~400-text confirmatory corpus. Built by the **same sampler** at a
larger scale. Same pipeline as the pilot, pointed at the main dirs.

> Run this ONLY after the pilot config (checkpoints/prompts/rubrics) is frozen.

### 1. Build sample
**Scale = 40** (default) → **Build**. Result: ~400 texts →
`pilot_data/main/` (`MRN-*`). Or CLI:
```bash
.venv/bin/python -m pilot --split main --seed 42 --scale 40
```

### 2. Rate self-containedness
Same 2-rater flow as the pilot, but writes to a **separate ledger**
(`pilot_data/ratings_main.json`) so it never collides with pilot ratings.
Two raters, independently, per `pilot/RATER_INSTRUCTIONS.md`.

### 3. Generate items (from texts)
**Generate QA/MCQ/NLI/stance** — frozen items from `pilot_data/main/` →
`pilot_data/main_items/` + `manifest.json`.

### 4. Summarize (r-grid)
**Summarize main texts** — same summarizers, on `pilot_data/main/` →
`pilot_data/main_summaries/`.

### 5. Score summaries
- **Judge (rubric)** → `.judge.json`.
- **QA-accuracy (items)** → `.qa.json` (summary-only, per frozen items).

### 6. Browse
**Browse texts** / **Browse results** — both target the main dirs.

CLI equivalents (if you prefer the command line):
```bash
.venv/bin/python -m itemgen generate --texts-dir pilot_data/main --items-dir pilot_data/main_items
.venv/bin/python -m smoke_summarizer --type llm --system <name> \
    --levels 0.9 0.7 0.5 0.3 0.2 0.1 0.05 \
    --texts-dir pilot_data/main --out-dir pilot_data/main_summaries ...
.venv/bin/python -m smoke_judge \
    --summaries-dir pilot_data/main_summaries --texts-dir pilot_data/main ...
.venv/bin/python -m itemgen score --items-dir pilot_data/main_items --summaries-dir pilot_data/main_summaries
.venv/bin/python -m pilot.raters report --split main
```

---

## Quick reference — what produces what

```
smoke/                       <- Phase 1 (Home -> SMOKE)
  texts/                       10 texts
  items/                       frozen QA/MCQ/NLI/stance + manifest.json
  summaries/<system>/          r-grid summaries + .judge.json + .qa.json

pilot_data/                  <- Phase 2 (Home -> PILOT)
  texts/                       50 pilot texts (PLT-*)
  items/                       pilot frozen items + manifest.json
  ratings.json                 pilot 2-rater ledger
  summaries/                   pilot summaries + .judge.json + .qa.json

pilot_data/                  <- Phase 3 (Home -> MAIN)
  main/                        ~400 confirmatory texts (MRN-*)
  main_items/                  main frozen items + manifest.json
  ratings_main.json            main 2-rater ledger (separate from pilot)
  main_summaries/              confirmatory summaries + .judge.json + .qa.json
```

---

## Handling model-access constraints

Two real-world limits shape the summarization step:

### 1. The endpoint serves one model at a time
Summarization runs as **sequential single-model passes**, not all at once.
- In the TUI, **Summarize** opens a per-model screen: each configured
  summarizer is a row with a **✓ done / — pending** status and a **Run** button.
- **Switch the endpoint to that model first**, then hit Run. The pass writes
  only that system's summaries.
- Passes are **resumable** — already-generated summaries are skipped, so a
  crash or a mid-lineup switch just resumes.
- Hit **Refresh status** after a pass to update the checklist.

### 2. Alisa / GigaChat have no API (web-UI only)
These run through a **manual export → human → import** loop
(Home → **Web-UI models**):
1. **Export** a task sheet (`<system>_tasks.md`). Each task is a
   **self-contained** prompt (instruction + target_words + full source text)
   between `---PROMPT---` / `---ENDPROMPT---`, with an empty
   `---RESPONSE---` block.
2. The human copies each PROMPT block into the Alisa/GigaChat web UI and
   pastes the model's answer into the RESPONSE block. (Same pattern as the
   prompt-review task.)
3. **Import** the filled sheet → summaries are written into the standard
   `<out>/<system>/<text_id>/<level>/summary_0.txt` layout, with word-count
   validation (± tolerance) and provenance (`origin=web`, operator).

**Result:** web-UI summaries are indistinguishable from API summaries
downstream — the judge and QA-accuracy score them identically.

CLI equivalents:
```bash
.venv/bin/python -m webtask export --system alisa --texts-dir smoke/texts --out alisa_tasks.md
.venv/bin/python -m webtask import --system alisa --sheet alisa_tasks.md --out-dir smoke/summaries --operator bob
```

---

## Golden rules

1. **Smoke first.** Never scale before smoke passes end-to-end.
2. **Smoke is frozen.** Pilot scaling never changes smoke defaults.
3. **Pilot needs 2 raters.** One rating = `incomplete`, cannot enter corpus.
4. **Splits are disjoint.** Pilot ≠ validation ≠ main. No reuse.
5. **Freeze before you run.** Checkpoints/prompts/rubrics hashed + on OSF
   before the pilot; pilot config frozen before main.
6. **Don't mix dirs.** Smoke = `smoke/`, pilot = `pilot_data/texts/`,
   main = `pilot_data/main/`. The TUI redirects automatically per phase.
