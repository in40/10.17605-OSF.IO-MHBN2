from smoke_collector.fetcher import Fetcher
from smoke_collector.sources.procedural_pages import split_sections, _is_procedural


def test_backend_order_direct():
    f = Fetcher(backend="direct")
    assert f._backend_order() == ["direct"]


def test_backend_order_mcp_with_key():
    f = Fetcher(backend="mcp", mcp_key="sk-x")
    assert f._backend_order() == ["mcp", "direct"]


def test_backend_order_mcp_no_key_falls_back():
    f = Fetcher(backend="mcp", mcp_key="")
    assert f._backend_order() == ["direct"]


def test_backend_order_auto():
    f = Fetcher(backend="auto", mcp_key="sk-x")
    assert f._backend_order() == ["mcp", "docling", "direct"]
    f2 = Fetcher(backend="auto", mcp_key="")
    assert f2._backend_order() == ["docling", "direct"]


def test_split_sections_by_heading():
    md = "# Intro\n\nsome intro text\n\n## Section A\n\nbody A line1\nbody A line2\n\n## Section B\n\nbody B"
    secs = split_sections(md)
    heads = [h for h, _ in secs]
    assert "Intro" in heads
    assert "Section A" in heads
    a = dict(secs)["Section A"]
    assert "body A line1" in a and "body A line2" in a


def test_is_procedural():
    assert _is_procedural("Как получить справку", "текст")
    assert _is_procedural("Что делать при блокировке", "текст")
    assert _is_procedural("Заголовок", "Сначала выполните шаг 1, затем шаг 2")
    assert not _is_procedural("История банка", "давным-давно было")


def test_html_to_md_headings():
    html = "<html><body><h2>Head</h2><p>Para one.</p><ul><li>item</li></ul></body></html>"
    md = Fetcher._html_to_md(html)
    assert "## Head" in md
    assert "Para one." in md
    assert "- item" in md
