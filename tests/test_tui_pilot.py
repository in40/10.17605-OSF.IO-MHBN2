import asyncio

from textual.widgets import Static

from smoke_tui import settings as S
from smoke_tui.app import (
    HomeScreen,
    MainScreen,
    PilotScreen,
    PromptViewerScreen,
    RaterScreen,
    SmokeScreen,
    SmokeApp,
    SummarizeScreen,
    WebTaskScreen,
)


def test_summarize_screen_lists_summarizers(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)

    async def drive():
        app = SmokeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            scr = SummarizeScreen("smoke/texts", "smoke/summaries")
            app.push_screen(scr)
            await pilot.pause()
            assert isinstance(app.screen, SummarizeScreen)
            n = len(app.settings["summarizers"])
            assert n >= 1
            assert scr.query_one("#summ_run0")
            assert scr.query_one("#summ_refresh")

    asyncio.run(drive())


def test_summarize_done_status(tmp_path):
    # summ_dir as an absolute path overrides REPO join in _is_done
    scr = SummarizeScreen("smoke/texts", str(tmp_path))
    assert scr._is_done("nope") is False
    d = tmp_path / "qwen-sys" / "SMK-NEWS-01" / "r0p5"
    d.mkdir(parents=True)
    (d / "summary_0.txt").write_text("x", encoding="utf-8")
    assert scr._is_done("qwen-sys") is True


def test_webtask_screen_mounts(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)

    async def drive():
        app = SmokeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            scr = WebTaskScreen()
            app.push_screen(scr)
            await pilot.pause()
            assert isinstance(app.screen, WebTaskScreen)
            assert scr.query_one("#wt_export")
            assert scr.query_one("#wt_import")
            assert scr.query_one("#wt_sheet")

    asyncio.run(drive())


def test_collect_prompts_groups():
    from smoke_tui.prompt_registry import collect_prompts

    groups = dict(collect_prompts())
    assert set(groups) == {
        "Summarizer",
        "Judge (rubric)",
        "Itemgen — generate",
        "Itemgen — score",
    }
    assert "DEFAULT_BASE" in dict(groups["Summarizer"])
    assert "COMBINED_PROMPT_RU" in dict(groups["Judge (rubric)"])
    assert "QA_GEN" in dict(groups["Itemgen — generate"])
    assert "QA_JUDGE" in dict(groups["Itemgen — score"])


def test_prompt_hash_deterministic():
    from smoke_tui.prompt_registry import prompt_hash

    assert prompt_hash("abc") == prompt_hash("abc")
    assert len(prompt_hash("abc")) == 64
    assert prompt_hash("abc") != prompt_hash("abd")


def test_prompt_viewer_mounts(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)

    async def drive():
        app = SmokeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            scr = PromptViewerScreen()
            app.push_screen(scr)
            await pilot.pause()
            assert isinstance(app.screen, PromptViewerScreen)
            assert len(scr.items) >= 13  # all prompts collected

    asyncio.run(drive())


def test_prompt_viewer_select_shows_text_and_hash(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)

    async def drive():
        app = SmokeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            scr = PromptViewerScreen()
            app.push_screen(scr)
            await pilot.pause()
            gname, name, text = scr.items[0]

            class _Ev:
                class list_view:
                    index = 0

            scr.on_list_view_selected(_Ev())
            await pilot.pause()
            detail = str(scr.query_one("#pv_detail", Static).render())
            assert name in detail
            assert "SHA-256" in detail
            assert text[:20] in detail

    asyncio.run(drive())


def test_home_is_three_section_hub(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)

    async def drive():
        app = SmokeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            assert isinstance(app.screen, HomeScreen)
            for bid in ("smoke", "pilot", "main"):
                assert app.screen.query_one(f"#{bid}")

    asyncio.run(drive())


def test_smoke_screen_mounts(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)

    async def drive():
        app = SmokeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            scr = SmokeScreen()
            app.push_screen(scr)
            await pilot.pause()
            assert isinstance(app.screen, SmokeScreen)
            assert scr.query_one("#s_collect")
            assert scr.query_one("#s_browse")

    asyncio.run(drive())


def test_main_screen_mounts(monkeypatch, tmp_path):
    from pilot import config as pcfg

    main_dir = tmp_path / "main"
    main_dir.mkdir()
    (main_dir / "MRN-NEWS-01.txt").write_text("One main text.", encoding="utf-8")
    (main_dir / "MRN-SCI-01.txt").write_text("Two main text.", encoding="utf-8")
    monkeypatch.setattr(pcfg, "PILOT_DIR", tmp_path)
    monkeypatch.setattr(pcfg, "MAIN_TEXTS", main_dir)

    async def drive():
        app = SmokeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            scr = MainScreen()
            app.push_screen(scr)
            await pilot.pause()
            assert isinstance(app.screen, MainScreen)
            assert scr.split == "main"
            assert "MAIN status" in str(scr.query_one("#p_status", Static).render())
            assert "texts: 2" in str(scr.query_one("#p_status", Static).render())

    asyncio.run(drive())


def test_rater_main_split_writes_main_ledger(monkeypatch, tmp_path):
    from pilot import config as pcfg
    from pilot import raters as R

    main_dir = tmp_path / "main"
    main_dir.mkdir()
    (main_dir / "MRN-NEWS-01.txt").write_text("A complete main text.", encoding="utf-8")
    monkeypatch.setattr(pcfg, "PILOT_DIR", tmp_path)
    monkeypatch.setattr(pcfg, "MAIN_TEXTS", main_dir)
    monkeypatch.setattr(R, "RATINGS_PATH", tmp_path / "ratings.json")

    async def drive():
        app = SmokeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            scr = RaterScreen("erin", split="main")
            app.push_screen(scr)
            await pilot.pause()
            await pilot.click("#r_yes")
            await pilot.pause()
            # pilot ledger untouched; main ledger has the rating
            assert R.load_ratings(tmp_path / "ratings.json") == []
            main_ratings = R.load_ratings(tmp_path / "ratings_main.json")
            assert len(main_ratings) == 1
            assert main_ratings[0]["text_id"] == "MRN-NEWS-01"

    asyncio.run(drive())


def test_pilot_summarizer_args_override_dirs():
    s = dict(S.DEFAULT_SUMMARIZER)
    s["texts_dir"] = "smoke/texts"
    s["out_dir"] = "smoke/summaries"
    args = S.pilot_summarizer_args(s, "pilot_data/texts", "pilot_data/summaries")
    assert "--texts-dir" in args
    assert args[args.index("--texts-dir") + 1] == "pilot_data/texts"
    assert args[args.index("--out-dir") + 1] == "pilot_data/summaries"
    # original settings untouched
    assert s["texts_dir"] == "smoke/texts"


def test_pilot_judge_args_override_dirs():
    j = {
        "base_url": "http://x", "api_key_env": "K", "model": "m", "mode": "combined",
        "temperature": 0.0, "top_p": 1.0, "max_tokens": 512, "seed": 42,
        "retries": 3, "summaries_dir": "smoke/summaries", "texts_dir": "smoke/texts",
    }
    args = S.pilot_judge_args(j, "pilot_data/summaries", "pilot_data/texts")
    assert args[args.index("--summaries-dir") + 1] == "pilot_data/summaries"
    assert args[args.index("--texts-dir") + 1] == "pilot_data/texts"
    assert j["summaries_dir"] == "smoke/summaries"


def _setup(monkeypatch, tmp_path):
    texts_dir = tmp_path / "texts"
    texts_dir.mkdir()
    (texts_dir / "PLT-NEWS-01.txt").write_text("A complete news article.", encoding="utf-8")
    (texts_dir / "PLT-SCI-01.txt").write_text("A complete science article.", encoding="utf-8")
    from pilot import config as pcfg
    from pilot import raters as R

    monkeypatch.setattr(pcfg, "PILOT_TEXTS", texts_dir)
    monkeypatch.setattr(R, "RATINGS_PATH", tmp_path / "ratings.json")
    return R


def test_pilot_screen_mounts(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)

    async def drive():
        app = SmokeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            assert isinstance(app.screen, HomeScreen)
            scr = PilotScreen()
            app.push_screen(scr)
            await pilot.pause()
            assert isinstance(app.screen, PilotScreen)
            status = scr.query_one("#p_status", Static)
            assert "texts: 2" in str(status.render())

    asyncio.run(drive())


def test_rater_records_yes(monkeypatch, tmp_path):
    R = _setup(monkeypatch, tmp_path)

    async def drive():
        app = SmokeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            scr = RaterScreen("alice")
            app.push_screen(scr)
            await pilot.pause()
            assert isinstance(app.screen, RaterScreen)
            await pilot.click("#r_yes")
            await pilot.pause()
            ratings = R.load_ratings()
            assert len(ratings) == 1
            assert ratings[0]["rater"] == "alice"
            assert ratings[0]["self_contained"] is True

    asyncio.run(drive())


def test_rater_no_without_note_blocked(monkeypatch, tmp_path):
    R = _setup(monkeypatch, tmp_path)

    async def drive():
        app = SmokeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            scr = RaterScreen("bob")
            app.push_screen(scr)
            await pilot.pause()
            await pilot.click("#r_no")  # empty note -> guard blocks
            await pilot.pause()
            assert R.load_ratings() == []
            assert scr.pos == 0  # did not advance

    asyncio.run(drive())


def test_rater_no_with_note_records(monkeypatch, tmp_path):
    R = _setup(monkeypatch, tmp_path)

    async def drive():
        app = SmokeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            scr = RaterScreen("dave")
            app.push_screen(scr)
            await pilot.pause()
            scr.query_one("#r_note").value = "dangling reference"
            await pilot.click("#r_no")
            await pilot.pause()
            ratings = R.load_ratings()
            assert len(ratings) == 1
            assert ratings[0]["self_contained"] is False
            assert ratings[0]["note"] == "dangling reference"

    asyncio.run(drive())


def test_smoke_screen_has_itemgen_buttons(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)

    async def drive():
        app = SmokeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            scr = SmokeScreen()
            app.push_screen(scr)
            await pilot.pause()
            assert scr.query_one("#s_items")
            assert scr.query_one("#s_qa")

    asyncio.run(drive())


def test_corpus_screen_has_itemgen_buttons(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path)

    async def drive():
        app = SmokeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            scr = PilotScreen()
            app.push_screen(scr)
            await pilot.pause()
            assert scr.query_one("#p_items")
            assert scr.query_one("#p_qa")
            assert scr.items_dir == "pilot_data/items"

    asyncio.run(drive())


def test_results_format_qa():
    from smoke_tui.app import ResultsScreen

    qa = {
        "generator_model": "qwen3.5-122b",
        "scores": {
            "qa": {"correct": 2, "total": 3, "accuracy": 0.6667},
            "mcq": {"raw": 0.5, "chance_corrected": 0.3333},
            "nli": {"accuracy": 0.5},
            "stance": {"accuracy": 0.25},
        },
    }
    out = ResultsScreen._format_qa(qa)
    assert "QA-accuracy" in out
    assert "2/3" in out
    assert "chance-corrected 0.3333" in out
    assert "NLI: 0.5" in out
    assert "stance: 0.25" in out


def test_rater_skip_records_nothing(monkeypatch, tmp_path):
    R = _setup(monkeypatch, tmp_path)

    async def drive():
        app = SmokeApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            scr = RaterScreen("carol")
            app.push_screen(scr)
            await pilot.pause()
            await pilot.click("#r_skip")
            await pilot.pause()
            assert R.load_ratings() == []
            assert scr.skipped == 1

    asyncio.run(drive())
