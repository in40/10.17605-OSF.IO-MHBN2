from smoke_summarizer.extractive import (
    split_sentences,
    summarize_extractive,
    textrank,
)


def _make_text(n_sentences: int, words_per: int = 12) -> str:
    sents = []
    for i in range(n_sentences):
        words = [f"слово{i}_{j}" for j in range(words_per)]
        # add some shared vocabulary to create graph edges
        if i % 2 == 0:
            words.append("общаятема")
        sents.append(" ".join(words) + ".")
    return " ".join(sents)


def test_split_sentences():
    s = split_sentences("Первое предложение. Второе предложение! Третье?")
    assert len(s) == 3


def test_textrank_scores_length():
    sents = split_sentences(_make_text(5))
    scores = textrank(sents)
    assert len(scores) == len(sents)
    assert all(s >= 0 for s in scores)


def test_textrank_single():
    assert textrank(["только одно"]) == [1.0]
    assert textrank([]) == []


def test_summarize_hits_target():
    text = _make_text(30, 12)  # ~360 words
    out = summarize_extractive(text, 60, tolerance=0.20)
    wc = len(out.split())
    assert 48 <= wc <= 72  # within +/-20% of 60


def test_summarize_deterministic():
    text = _make_text(20)
    a = summarize_extractive(text, 50)
    b = summarize_extractive(text, 50)
    assert a == b


def test_summarize_empty():
    assert summarize_extractive("", 10) == ""


def test_summarize_small_target_picks_short_sentence():
    text = "Короткая фраза. " * 5 + "Очень длинное предложение " * 20 + "."
    out = summarize_extractive(text, 3, tolerance=0.5)
    assert len(out.split()) <= 8  # should not pick the huge sentence
