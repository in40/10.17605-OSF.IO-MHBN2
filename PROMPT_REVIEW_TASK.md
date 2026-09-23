# Task: Rewrite pipeline prompts into professional Russian

## Context (for the reviewer / external LLM)

We run a **summarization research study** on Russian texts. A pipeline uses
LLM prompts to (a) summarize texts at controlled lengths, (b) generate
evaluation items (QA / multiple-choice / NLI / stance), and (c) score
summaries. The prompts below are currently in **rough Russian** with
grammatical errors. We need them rewritten into **native, professional,
grammatically-correct Russian** while preserving their exact function.

## Hard constraints (MUST NOT change)

1. **Placeholders stay byte-identical.** Every `{name}` (e.g. `{target_words}`,
   `{text}`, `{source}`, `{n}`, `{question}`, `{gold}`, `{answer}`,
   `{options}`, `{hypothesis}`, `{claim}`, `{summary}`, `{min_words}`,
   `{max_words}`, `{dim}`, `{desc}`) must remain exactly as written.
   Do not rename, translate, or remove them.
2. **JSON output format stays identical.** The required JSON keys and shapes
   (e.g. `{"answer": "..."}`, `{"correct": true}`, `{"choice": 0}`,
   `{"label": "entailment"}`, `{"stance": "support"}`,
   `{"question": "...", "gold_answer": "..."}`,
   `{"options": [...], "correct_index": 0}`) must be preserved exactly.
   The literal `{{` / `}}` are escaped braces for Python `.format()` — keep them.
3. **Semantic intent unchanged.** Rewrite the LANGUAGE only. Do not change what
   is being asked, the number of items, the scoring scale (0–1), the label
   sets (entailment/neutral/contradiction, support/oppose/neutral), or the
   "answer using ONLY the summary" rule.
4. **English technical tokens stay English** where they are JSON keys or fixed
   labels (`NOT_STATED`, `correct`, `choice`, `label`, `stance`,
   `entailment`, etc.). The surrounding instruction is Russian.
5. **Tone:** formal, precise, imperative (as is normal for Russian task
   instructions). No colloquialisms.

## Known issues to fix (non-exhaustive — find the rest)

- Judge: `Оцени резюме по четырёх измерениям` → **`по четырём измерениям`**
  (dative after «по»).
- MCQ_GEN: `у каждого 4 варианта ответа` → `у каждого — по 4 варианта ответа`
  (or rephrase); `но не верны` → **`но неверны`** (one word).
- QA_JUDGE: `допускается перефраз` → **`допускается перефразирование`** /
  `пересказ` («перефраз» is not standard).
- DEFAULT_REGEN: `не попало в нужный объём` → **`не уложилось в требуемый
  объём`** (more professional).
- Numeral agreement: `{n} слов` / `{target_words} слов` — Russian agrees
  (1 слово, 2–4 слова, 5+ слов). Since the number is a placeholder, prefer a
  phrasing that avoids the agreement problem (e.g. `объёмом примерно
  {target_words} слов` is acceptable as a generic template, but flag if a
  cleaner construction exists).

## Deliverable format

For each prompt, return:

```
### <PROMPT_NAME>
<rewritten Russian text, with placeholders and JSON format preserved>
```

Return all 13. Do not merge or reorder them.

---

## The prompts (current text — rewrite each)

### DEFAULT_BASE  (summarizer, main)
Сожми следующий текст, сохранив основной смысл, ключевые факты и логику изложения. Целевой объём резюме — примерно {target_words} слов. Пиши связным текстом без списков, заголовков и пояснений о задаче.

Текст:
{text}

### DEFAULT_REGEN  (summarizer, length re-attempt)
Предыдущее резюме не попало в нужный объём. Перепиши резюме текста, строго удержавшись в пределах {min_words}–{max_words} слов и сохранив основной смысл и ключевые факты. Пиши связным текстом без списков и пояснений.

Текст:
{text}

### COMBINED_PROMPT_RU  (judge, all dimensions at once)
Ты — строгий эксперт-оценщик автоматических резюме. Оцени резюме по четырёх измерениям, каждое — числом от 0 до 1 (1 = идеально, 0 = плохо).

Измерения:
- faithfulness: резюме не противоречит оригиналу, без выдуманных фактов
- coverage: покрыты ключевые факты и смысл оригинала
- coherence: логичная, связная структура без разрывов
- fluency: грамотный, естественный русский язык

Оценивай только по приведённому исходному тексту. Не добавляй пояснений.
Ответь СТРОГО одним JSON-объектом вида:
{"faithfulness": 0.0, "coverage": 0.0, "coherence": 0.0, "fluency": 0.0}

Исходный текст:
{source}

Резюме:
{summary}

### PER_DIM_PROMPT_RU  (judge, one dimension)
Ты — строгий эксперт-оценщик резюме. Оцени, насколько резюме соответствует критерию «{dim}» ({desc}) по шкале от 0 до 1 (1 = полностью соответствует).
Ответь СТРОГО одним JSON-объектом: {"score": 0.0}

Исходный текст:
{source}

Резюме:
{summary}

### QA_GEN  (itemgen, generate fact QA pairs)
Прочитай текст. Составь {n} фактических вопросов с короткими ответами.
Правила:
- каждый ответ должен быть явно подтверждён текстом (дословно или перефразированно);
- вопросы проверяемые, не требуют внешних знаний;
- не включай вопросов, ответа на которые нет в тексте.
Ответь СТРОГО JSON-массивом вида:
[{"question": "...", "gold_answer": "..."}]

Текст:
{source}

### MCQ_GEN  (itemgen, generate multiple-choice)
Прочитай текст. Составь {n} вопросов на понимание, у каждого 4 варианта ответа, ровно один верный. Неверные варианты должны быть правдоподобны, но не верны.
Ответь СТРОГО JSON-массивом вида:
[{"question": "...", "options": ["...", "...", "...", "..."], "correct_index": 0}]

Текст:
{source}

### NLI_GEN  (itemgen, generate logic items)
Прочитай текст. Составь {n} утверждений-гипотез к тексту. Для каждого укажи метку: entailment (следует из текста), neutral (не следует и не противоречит), contradiction (противоречит тексту).
Ответь СТРОГО JSON-массивом вида:
[{"hypothesis": "...", "label": "entailment"}]

Текст:
{source}

### STANCE_GEN  (itemgen, generate stance items)
Прочитай текст. Выдели {n} значимых утверждений и позицию текста по каждому: support (текст поддерживает), oppose (текст отвергает), neutral (без явной позиции).
Ответь СТРОГО JSON-массивом вида:
[{"claim": "...", "stance": "support"}]

Текст:
{source}

### QA_ANSWER  (itemgen, answer QA from summary only)
Ответь на вопрос ИСПОЛЬЗУЯ ТОЛЬКО приведённое резюме. Если ответа нет в резюме, верни строку "NOT_STATED". Не используй внешние знания.
Ответь СТРОГО JSON-объектом: {"answer": "..."}

Вопрос: {question}

Резюме:
{summary}

### QA_JUDGE  (itemgen, grade answer vs gold)
Сопоставь ответ с эталоном по смыслу. Верни correct=true если ответ передаёт тот же факт, что эталон (допускается перефраз); иначе correct=false.
Ответь СТРОГО JSON-объектом: {"correct": true}

Вопрос: {question}
Эталон: {gold}
Ответ: {answer}

### MCQ_ANSWER  (itemgen, answer MCQ from summary only)
Выбери один верный вариант ИСПОЛЬЗУЯ ТОЛЬКО резюме. Если ответа нет в резюме, верни choice=-1. Ответь СТРОГО JSON-объектом: {"choice": 0}

Вопрос: {question}
Варианты:
{options}

Резюме:
{summary}

### NLI_ANSWER  (itemgen, judge NLI from summary only)
Определи отношение гипотезы к резюме (ИСПОЛЬЗУЯ ТОЛЬКО резюме): entailment / neutral / contradiction.
Ответь СТРОГО JSON-объектом: {"label": "entailment"}

Гипотеза: {hypothesis}

Резюме:
{summary}

### STANCE_ANSWER  (itemgen, judge stance from summary only)
Определи позицию резюме по утверждению (ИСПОЛЬЗУЯ ТОЛЬКО резюме): support / oppose / neutral.
Ответь СТРОГО JSON-объектом: {"stance": "support"}

Утверждение: {claim}

Резюме:
{summary}

---

## After you return the rewrites

We will paste them back into the three Python modules
(`smoke_summarizer/prompts.py`, `smoke_judge/rubric.py`,
`itemgen/prompts.py`), re-run the test suite, and re-hash the prompts
(SHA-256) for the frozen OSF manifest.
