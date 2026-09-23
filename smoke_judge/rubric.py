"""Judge rubric: 4 dimensions + RU prompt templates."""
from __future__ import annotations

DIMENSIONS = ("faithfulness", "coverage", "coherence", "fluency")

DIM_DESCRIPTIONS_RU = {
    "faithfulness": "резюме не противоречит оригиналу, без выдуманных фактов",
    "coverage": "покрыты ключевые факты и смысл оригинала",
    "coherence": "логичная, связная структура без разрывов",
    "fluency": "грамотный, естественный русский язык",
}

COMBINED_PROMPT_RU = (
    "Ты — строгий эксперт-оценщик автоматических резюме. Оцени резюме по "
    "четырём измерениям, каждое — числом от 0 до 1 (1 — идеально, "
    "0 — неудовлетворительно).\n\n"
    "Измерения:\n"
    "- faithfulness: резюме не противоречит оригиналу и не содержит выдуманных фактов\n"
    "- coverage: ключевые факты и смысл оригинала отражены в резюме\n"
    "- coherence: логичная, связная структура без разрывов\n"
    "- fluency: грамотный, естественный русский язык\n\n"
    "Оценивай только по приведённому исходному тексту. Не добавляй пояснений.\n"
    "Ответь СТРОГО одним JSON-объектом вида:\n"
    '{{"faithfulness": 0.0, "coverage": 0.0, "coherence": 0.0, "fluency": 0.0}}\n\n'
    "Исходный текст:\n{source}\n\n"
    "Резюме:\n{summary}"
)

PER_DIM_PROMPT_RU = (
    "Ты — строгий эксперт-оценщик резюме. Оцени, насколько резюме соответствует "
    "критерию «{dim}» ({desc}), по шкале от 0 до 1 (1 — полностью соответствует).\n"
    'Ответь СТРОГО одним JSON-объектом: {{"score": 0.0}}\n\n'
    "Исходный текст:\n{source}\n\n"
    "Резюме:\n{summary}"
)


def render_combined(source: str, summary: str) -> str:
    return COMBINED_PROMPT_RU.format(
        faithfulness=DIM_DESCRIPTIONS_RU["faithfulness"],
        coverage=DIM_DESCRIPTIONS_RU["coverage"],
        coherence=DIM_DESCRIPTIONS_RU["coherence"],
        fluency=DIM_DESCRIPTIONS_RU["fluency"],
        source=source,
        summary=summary,
    )


def render_per_dim(source: str, summary: str, dim: str) -> str:
    return PER_DIM_PROMPT_RU.format(
        dim=dim, desc=DIM_DESCRIPTIONS_RU[dim], source=source, summary=summary
    )
