import pytest

from smoke_summarizer.runner import (
    _level_tag,
    length_ok,
    target_words,
    word_count,
)


def test_target_words():
    assert target_words(800, 0.5) == 400
    assert target_words(800, 0.05) == 40
    assert target_words(300, 0.9) == 270
    assert target_words(10, 0.05) == 1  # floor at 1


def test_length_ok_within_tolerance():
    assert length_ok(400, 400, 0.2)
    assert length_ok(480, 400, 0.2)
    assert length_ok(320, 400, 0.2)
    assert not length_ok(481, 400, 0.2)
    assert not length_ok(319, 400, 0.2)


def test_length_ok_zero_target():
    assert length_ok(0, 0, 0.2)
    assert length_ok(5, 0, 0.2)


def test_word_count():
    assert word_count("раз два три") == 3
    assert word_count("") == 0


def test_level_tag():
    assert _level_tag(0.05) == "r0p05"
    assert _level_tag(0.9) == "r0p9"
    assert _level_tag(0.5) == "r0p5"
