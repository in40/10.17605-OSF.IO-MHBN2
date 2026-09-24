# Model Licenses Record

License status for every model in the summary-source ensemble. **Verify the
exact pinned version's license before freezing** — several versions below are
forward-looking; the licenses listed are the family-standard and must be
confirmed against the actual released model card.

Legend: ✅ cleared for research + output redistribution · ⚠️ verify · ❓ unknown

---

## Summarizer models (open weights)

- **gpt-oss 120b** — **Apache 2.0** (confirmed via HF model card).
  Research ✅ · redistribution ✅ · attribution required.

- **Nemotron 3 Super 120b** — **NVIDIA Open Model License** (confirmed via HF).
  Research ✅ · redistribution ✅ · trustworthy-AI clause (no misuse).

- **Qwen3.8 27b** — **Apache 2.0** (Qwen3 family, confirmed). ⚠️ verify exact version.
  Research ✅ · redistribution ✅.

- **Qwen3.6 35b** — **Apache 2.0** (Qwen family). ⚠️ verify exact version.
  Research ✅ · redistribution ✅.

- **DeepSeek 4.1** — **MIT** (family-stable). ⚠️ verify exact version.
  Research ✅ · redistribution ✅.

- **Gemma 4 31b** — **Gemma Terms of Use** (permissive-with-conditions, NOT OSI-approved).
  Research ✅ · outputs are yours · Acceptable Use Policy applies (study content is fine).
  ⚠️ verify exact version + read current ToU.

- **hybrid (IlyaGusev/rut5_base_sum_gazeta)** — **Apache 2.0** (known).
  Research ✅ · redistribution ✅.

## Judge & item-generator

- **qwen3.8 next flash** (Judge) — **Apache 2.0** (Qwen family). ⚠️ verify exact version.
- **qwen3.8 next flash** (Item generator, same as Judge) — **Apache 2.0**.
  Note: judge ≠ summarizer constraint satisfied as long as qwen3.8-next-flash is
  not also a summarizer in the lineup.

## Web-UI-only models (consumer services — ToS, not a model license)

- **Alisa (Yandex)** — ⚠️ **consumer Terms of Service**, not open weights.
  - Manual copy-paste use: acceptable.
  - **Automated access / scraping: typically prohibited** — do not automate.
  - **Output redistribution in a published study: VERIFY against Yandex ToS.**
  - Action: read Yandex Alisa/Alice ToS; confirm research + redistribution terms.

- **GigaChat (Sber)** — ⚠️ has BOTH open weights AND a web service.
  - **Open weights** → Sber's permissive license (clean for research + redistribution).
  - **Web UI** → Sber's web ToS (redistribution ambiguity).
  - **Recommendation: use GigaChat OPEN WEIGHTS, not the web UI**, to remove the
    web-ToS redistribution risk. If web UI is unavoidable, verify the ToS.

---

## Verify-before-freeze checklist

For each model, before the pilot freeze, record:
- [ ] Exact model name + version + checkpoint hash
- [ ] Exact license (from the actual model card, not the family assumption)
- [ ] License URL / source
- [ ] Output-redistribution permitted for the published study? (esp. Alisa/GigaChat)
- [ ] Attribution text for the paper

## Where this goes

- This record → attached to the **frozen pilot configuration** (alongside the
  checkpoint hashes from `02_math.md` / `04_sampling.md`).
- Summarized in the **AI Use Disclosure** (`AI_USE_DISCLOSURE.md`).
- Cited in the paper's methods + model-attribution section.
