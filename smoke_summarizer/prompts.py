"""Prompt templates (RU) for length-constrained summarization."""
from __future__ import annotations

DEFAULT_BASE = (
    "Сожми следующий текст, сохранив основной смысл, ключевые факты и логику "
    "изложения. Целевой объём резюме — примерно {target_words} слов. "
    "Пиши связным текстом без списков, заголовков и пояснений о задаче.\n\n"
    "Текст:\n{text}"
)

DEFAULT_REGEN = (
    "Предыдущее резюме не попало в нужный объём. Перепиши резюме текста, "
    "строго удержавшись в пределах {min_words}–{max_words} слов и сохранив "
    "основной смысл и ключевые факты. Пиши связным текстом без списков и "
    "пояснений.\n\nТекст:\n{text}"
)


def render_base(template: str, target_words: int, text: str) -> str:
    return template.format(target_words=target_words, text=text)


def render_regen(template: str, min_words: int, max_words: int, text: str) -> str:
    return template.format(min_words=min_words, max_words=max_words, text=text)
