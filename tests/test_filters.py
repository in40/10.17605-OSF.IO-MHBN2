import pytest

from smoke_collector.filters import (
    bucket_for,
    check_duplicate,
    check_text,
    find_pii,
    find_stop_phrases,
    in_bucket_target,
    jaccard,
    trigrams,
    word_count,
)


def test_word_count():
    assert word_count("раз два   три\nчетыре") == 4
    assert word_count("") == 0


def test_pii_phone():
    assert find_pii("позвоните +7 916 123-45-67")
    assert find_pii("8 916 123-45-67")
    assert not find_pii("в 2024 году рост составил 7 процентов")


def test_pii_email():
    assert find_pii("почта ivanov@example.com тут")
    assert not find_pii("нет почты")


def test_pii_inn_snils_passport():
    assert find_pii("ИНН 7707083893")
    assert find_pii("СНИЛС 112-233-445 55")
    assert find_pii("паспорт 45 09 123456")


def test_pii_address():
    assert find_pii("г. Москва, ул. Ленина, д. 5")
    assert find_pii("кв. 12")
    assert not find_pii("в деревне было хорошо")


def test_stop_phrases():
    assert find_stop_phrases("Продолжение следует...")
    assert find_stop_phrases("как упоминалось выше, вопрос сложный")
    assert find_stop_phrases("окончание следует")
    assert not find_stop_phrases("обычный текст без отсылок")


def test_trigrams_jaccard():
    a = trigrams("один два три четыре")
    b = trigrams("один два три четыре")
    c = trigrams("пять шесть семь восемь")
    assert jaccard(a, b) == 1.0
    assert jaccard(a, c) == 0.0


def test_check_duplicate_reject_and_warn():
    base = " ".join(f"слово{i}" for i in range(100))
    near = " ".join(f"слово{i}" for i in range(99)) + " другое"
    far = " ".join(f"иное{i}" for i in range(100))
    existing = {"A": trigrams(base)}
    ok, msgs = check_duplicate(near, existing)
    assert not ok
    ok2, msgs2 = check_duplicate(far, existing)
    assert ok2 and not msgs2


def test_check_text_news_length_bounds():
    good = " ".join(["текст"] * 400)
    assert check_text(good, "news").ok
    short = " ".join(["текст"] * 100)
    r = check_text(short, "news")
    assert not r.ok and any("length" in x for x in r.reasons)


def test_check_text_sci_allows_150():
    t = " ".join(["наука"] * 150)
    assert check_text(t, "sci").ok


def test_bucket_for():
    assert bucket_for(148) == 150
    assert bucket_for(320) == 300
    assert bucket_for(460) == 500
    assert bucket_for(790) == 800


def test_in_bucket_target():
    assert in_bucket_target(460, 500)
    assert in_bucket_target(540, 500)
    assert not in_bucket_target(400, 500)
    assert not in_bucket_target(560, 500)
