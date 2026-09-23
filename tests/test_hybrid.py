from smoke_summarizer.hybrid import HybridSummarizer


class _StubHybrid(HybridSummarizer):
    """Override _generate to avoid loading the real model."""

    def _load(self) -> None:
        self._loaded = True

    def _generate(self, text: str) -> str:
        return "Это абстрактное ядро резюме."  # ~5 words


def _make_text(n=40, words=12):
    return " ".join(
        " ".join(f"слово{i}_{j}" for j in range(words)) + "." for i in range(n)
    )


def test_hybrid_fills_to_target():
    h = _StubHybrid()
    text = _make_text(40, 12)  # ~480 words
    out = h.summarize(text, 100, tolerance=0.2)
    wc = len(out.split())
    assert 80 <= wc <= 120  # core (~5) + fill to ~100


def test_hybrid_starts_with_core():
    h = _StubHybrid()
    out = h.summarize(_make_text(30), 80)
    assert out.startswith("Это абстрактное ядро резюме.")


def test_hybrid_core_already_over_target():
    class _LongCore(_StubHybrid):
        def _generate(self, text):
            return " ".join(f"ядро{i}" for i in range(150))

    h = _LongCore()
    out = h.summarize(_make_text(40), 50)
    # core (150) >= target (50) -> return core as-is, no fill
    assert out.startswith("ядро0")
    assert len(out.split()) == 150
