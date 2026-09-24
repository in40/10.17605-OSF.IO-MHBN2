from smoke_summarizer.oracle import oracle_extractive, oracle_select

TEXT = (
    "Кошки — популярные домашние животные. Они независимы и ласковы одновременно. "
    "Многие люди держат кошек в квартирах. Кошки требуют минимального ухода. "
    "Ветеринары рекомендуют стерилизовать животных без породы. "
    "Кошки спят по шестнадцать часов в сутки. Это объясняется их хищной природой. "
    "Игры важны для физического здоровья кошки. Владельцы должны уделять время питомцу."
)


def test_oracle_select_scores_in_range():
    sel = oracle_select(TEXT, 30)
    assert 0.0 <= sel["coverage"] <= 1.0
    assert 0.0 <= sel["coherence"] <= 1.0
    assert sel["maximin"] == round(min(sel["coverage"], sel["coherence"]), 4)
    assert sel["indices"]


def test_oracle_extractive_wordcount_near_target():
    out = oracle_extractive(TEXT, 30, tolerance=0.5)
    wc = len(out.split())
    assert wc > 0
    assert wc <= 30 * 1.5 + 5  # within a loose budget


def test_oracle_is_extractive_verbatim():
    # every selected sentence must be a substring of the source (verbatim extraction)
    out = oracle_extractive(TEXT, 25)
    assert out in TEXT or all(
        part.strip() in TEXT for part in out.split(". ") if part.strip()
    )


def test_oracle_empty_text():
    sel = oracle_select("", 10)
    assert sel["indices"] == []
    assert oracle_extractive("", 10) == ""


def test_oracle_single_sentence():
    one = "Это единственное предложение в тексте про тестирование."
    sel = oracle_select(one, 5)
    assert sel["coherence"] == 1.0  # vacuous for <2 sentences
    assert len(sel["indices"]) >= 1


def test_oracle_deterministic():
    a = oracle_select(TEXT, 30)
    b = oracle_select(TEXT, 30)
    assert a["indices"] == b["indices"]
    assert a["maximin"] == b["maximin"]


def test_generate_one_oracle_persists_scores():
    from smoke_summarizer.runner import SummConfig, generate_one

    cfg = SummConfig(type="oracle", system="oracle", tolerance=0.2)
    summary, attempts, regen, status, extra = generate_one(None, cfg, TEXT, 30)
    assert "coverage" in extra and "coherence" in extra and "maximin" in extra
    assert extra["maximin"] == round(min(extra["coverage"], extra["coherence"]), 4)


def test_generate_one_extractive_has_empty_extra():
    from smoke_summarizer.runner import SummConfig, generate_one

    cfg = SummConfig(type="extractive", system="tr", tolerance=0.2)
    summary, attempts, regen, status, extra = generate_one(None, cfg, TEXT, 30)
    assert extra == {}
