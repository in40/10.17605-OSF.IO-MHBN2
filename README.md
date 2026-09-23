# 10.17605-OSF.IO-MHBN2

Smoke-test text corpus + pipeline tooling for the summarization-compression study.

This repo contains four Python packages that automate the smoke-test workflow:

| Package | Purpose |
|---|---|
| `smoke_collector` | Collect + filter the 10 smoke texts (news/sci/ins/fic/dia) per `SMOKE_TEXTS_SPEC.md` |
| `smoke_summarizer` | Run an LLM over the corpus across the compression-ratio (r) grid |
| `smoke_judge` | LLM-as-judge scoring of summaries on 4 quality dimensions |
| `smoke_tui` | Terminal UI to configure, run, and review all of the above |

---

## 1. Requirements

- **Python ≥ 3.10** (developed on 3.13)
- `git`
- Network access to: GitHub (Lenta dump), cyberleninka.ru, ru.wikisource.org, cbr.ru, huggingface.co, and your LLM endpoint
- An **OpenAI-compatible** chat-completions endpoint (local vLLM/llama.cpp or hosted)

---

## 2. Setup

```bash
git clone <your-repo-url> RESEARCH
cd RESEARCH

# Create a virtualenv AT THIS PATH (the TUI expects ./.venv)
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Optional: for tests
.venv/bin/pip install pytest
```

> **Important — venv location.** The TUI runs each stage as a subprocess using
> `./.venv/bin/python` (falling back to the launching interpreter only if `.venv`
> is missing). If you move/rename the repo or use a different venv path, the
> subprocesses may lose dependencies (e.g. `bs4`). Always create the venv at
> `<repo>/.venv`, or edit `smoke_tui/app.py` (`_VENV_PY`).

### API key

The key is **never stored in config files**. Export it in the environment:

```bash
export SC_KEY="sk-..."      # name configurable via --api-key-env / TUI settings
```

---

## 3. Run the pipeline (CLI)

### 3.1 Collect the corpus (10 texts)

```bash
.venv/bin/python -m smoke_collector.pipeline --all
```

Output: `smoke/texts/{SMK-XXX-NN}.txt` + `.meta.json`.
Prior runs are auto-archived to `smoke/archive/<timestamp>/`.

### 3.2 Validate the corpus

```bash
.venv/bin/python -m smoke_collector.validate        # expect: ALL CHECKS PASSED
```

Run this immediately after collecting, before summarizing.

### 3.3 Summarize (r-grid)

```bash
.venv/bin/python -m smoke_summarizer \
  --base-url https://chat.sorokinonline.com/v1 \
  --model qwen3.5-122b --system qwen3.5-122b \
  --levels 0.9 0.7 0.5 0.3 0.2 0.1 0.05 \
  --n 1 --temperature 0.3 --max-tokens 2048 \
  --tolerance 0.20 --regen 1 --seed 42 --no-think \
  --texts-dir smoke/texts --out-dir smoke/summaries
```

Output: `smoke/summaries/{system}/{text_id}/r{level}/summary_{i}.txt` + `.json`.

> **`--no-think`**: for reasoning/thinking models, this sets
> `chat_template_kwargs.enable_thinking=false` so output is clean and not
> truncated by reasoning tokens. Use it unless you specifically want reasoning.

### 3.4 Judge

```bash
.venv/bin/python -m smoke_judge \
  --base-url https://chat.sorokinonline.com/v1 \
  --model qwen3.5-122b \
  --mode combined --temperature 0.0 --top-p 0.95 --max-tokens 256 --seed 42
```

Output: `summary_{i}.judge.json` beside each summary (4 dimension scores).
Resume-safe: already-judged files are skipped.

---

## 4. Run the TUI (recommended for researchers)

```bash
export SC_KEY="sk-..."
.venv/bin/python -m smoke_tui
```

- **Home**: Collect / Summarize / Judge / Validate / Browse / Configure
- **Configure**: tabbed forms for Summarizer + Judge; `ctrl+s` saves to `smoke_tui_settings.json`
- **Run**: live log of the actual subprocess
- **Browse**: pick a summary → see source + summary + judge scores
- **Pilot**: full pilot pipeline (Build → Rate → Summarize → Judge → Browse)

> **Step-by-step for each phase (smoke / pilot / main): see [`OPERATIONS.md`](OPERATIONS.md).**

---

## 5. Tests

```bash
.venv/bin/python -m pytest tests/ -q
```

Covers: PII/length/duplicate/stop-phrase filters, bucket balance, r-grid target/
tolerance logic, judge JSON parsing, and TUI navigation (headless pilot).

---

## 6. Docker (optional)

```bash
docker build -t smoke .
docker run --rm -e SC_KEY="$SC_KEY" -v "$PWD/smoke:/app/smoke" smoke
```

---

## 7. Data locations

| Path | Contents |
|---|---|
| `smoke/texts/` | current 10-text corpus |
| `smoke/archive/<ts>/` | previous corpus runs |
| `smoke/summaries/<system>/...` | generated summaries + provenance |
| `~/.cache/smoke_collector/` | downloaded raw sources (Lenta dump, HTML, JSON) |
| `smoke_tui_settings.json` | TUI settings (no secrets) |
| `*.log` | per-package logs (DEBUG) |

---

## 8. Reproduction notes / caveats

- **Model identity**: for the real study the judge must NOT be the same model as
  the summarizers (self-preference bias). The default `qwen3.5-122b` for both is
  for plumbing only — swap the judge to a distinct model before pilot.
- **Licenses**: corpus licenses are recorded per-item in each `.meta.json`
  (CC BY / CC BY-NC / public domain / gov reference). Verify before redistribution.
- **Thinking models**: pass `--no-think` (or set in TUI) for Qwen3-class models.
- **Extreme r-levels** (0.05 on short texts, 0.9) may exceed the length tolerance
  and be marked `length_fail` — this is expected model behavior, not an error.
- **Frozen artifacts**: prompts, rubrics, schemas, and model/checkpoint IDs must be
  hashed + uploaded to OSF before the pilot (see `SMOKE_TEST.md` §8).
