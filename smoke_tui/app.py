"""Textual TUI: configure, run, and review the smoke-test pipeline."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    ListView,
    ListItem,
    RichLog,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

from . import settings as S

REPO = Path(__file__).resolve().parent.parent
_VENV_PY = REPO / ".venv" / "bin" / "python"
PY = str(_VENV_PY) if _VENV_PY.exists() else sys.executable

COMMON_SUMMARIZER_FIELDS = [
    ("system", "System label", "text"),
    ("levels", "Levels (space-sep ratios)", "text"),
    ("n", "Summaries per cell", "int"),
    ("tolerance", "Tolerance (±frac)", "float"),
    ("regen", "Regen attempts", "int"),
    ("texts_dir", "Texts dir", "text"),
    ("out_dir", "Output dir", "text"),
]

LLM_SUMMARIZER_FIELDS = [
    ("base_url", "Base URL", "text"),
    ("api_key_env", "API key env var", "text"),
    ("model", "Model", "text"),
    ("temperature", "Temperature", "float"),
    ("max_tokens", "Max tokens", "int"),
    ("top_p", "Top-p (blank=off)", "text"),
    ("seed", "Seed", "int"),
    ("no_think", "Disable thinking", "bool"),
]

HYBRID_SUMMARIZER_FIELDS = [
    ("hybrid_model", "RU seq2seq model", "text"),
    ("hybrid_backend", "Backend (transformers/ctranslate2)", "text"),
    ("extractive_scale", "Extractive grounding scale", "float"),
]

# Back-compat alias (tests/imports may reference SUMMARIZER_FIELDS)
SUMMARIZER_FIELDS = COMMON_SUMMARIZER_FIELDS + LLM_SUMMARIZER_FIELDS

JUDGE_FIELDS = [
    ("base_url", "Base URL", "text"),
    ("api_key_env", "API key env var", "text"),
    ("model", "Model", "text"),
    ("mode", "Mode (combined/per_dimension)", "text"),
    ("temperature", "Temperature", "float"),
    ("top_p", "Top-p", "float"),
    ("max_tokens", "Max tokens", "int"),
    ("seed", "Seed", "int"),
    ("retries", "Retries", "int"),
    ("think", "Enable thinking", "bool"),
    ("summaries_dir", "Summaries dir", "text"),
    ("texts_dir", "Texts dir", "text"),
]


class HomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("SUMMARIZATION STUDY", id="title", classes="big")
        with Vertical():
            yield Button("SMOKE  (10 texts · plumbing check)", id="smoke", variant="primary")
            yield Button("PILOT  (50 texts · 2-rater gate)", id="pilot", variant="warning")
            yield Button("MAIN   (400 texts · confirmatory)", id="main", variant="primary")
            yield Button("Web-UI models (Alisa / GigaChat)", id="webui", variant="warning")
            yield Button("View / audit prompts", id="prompts")
            yield Button("Configure", id="config")
            yield Button("Quit", id="quit", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        sid = event.button.id
        if sid == "quit":
            self.app.exit()
        elif sid == "config":
            self.app.push_screen(ConfigScreen())
        elif sid == "webui":
            self.app.push_screen(WebTaskScreen())
        elif sid == "prompts":
            self.app.push_screen(PromptViewerScreen())
        elif sid == "smoke":
            self.app.push_screen(SmokeScreen())
        elif sid == "pilot":
            self.app.push_screen(PilotScreen())
        elif sid == "main":
            self.app.push_screen(MainScreen())


class ConfigScreen(Screen):
    BINDINGS = [("ctrl+s", "save_exit", "Save & Exit"), ("escape", "cancel", "Cancel")]

    def __init__(self, summarizers: list[dict] | None = None) -> None:
        super().__init__()
        import copy

        if summarizers is None:
            summarizers = copy.deepcopy(self.app.settings["summarizers"])
        self.summarizers: list[dict] = summarizers

    def compose(self) -> ComposeResult:
        with TabbedContent(id="cfg-tabs"):
            for i, summ in enumerate(self.summarizers):
                with TabPane(f"Summarizer {i + 1}", id=f"pane_summ{i}"):
                    with VerticalScroll():
                        yield Label("Type", classes="field-label")
                        yield Select(
                            [("LLM", "llm"), ("Extractive (TextRank)", "extractive"),
                             ("Hybrid", "hybrid")],
                            value=summ.get("type", "llm"),
                            id=f"summ{i}_type",
                        )
                        yield from self._fields(f"summ{i}", summ, COMMON_SUMMARIZER_FIELDS)
                        with Vertical(id=f"summ{i}_llmgroup"):
                            yield from self._fields(f"summ{i}", summ, LLM_SUMMARIZER_FIELDS)
                        with Vertical(id=f"summ{i}_hybridgroup"):
                            yield from self._fields(f"summ{i}", summ, HYBRID_SUMMARIZER_FIELDS)
            with TabPane("Judge", id="pane_judge"):
                with VerticalScroll():
                    yield from self._fields("judge", self.app.settings["judge"], JUDGE_FIELDS)
        with Horizontal(id="cfg-actions"):
            yield Button("+ Add Summarizer", id="add_summ")
            yield Button("Remove current", id="remove_current")
            yield Button("Cancel", id="cancel", variant="error")
            yield Button("Save & Exit", id="save", variant="success")

    def _fields(self, prefix: str, vals: dict, fields: list[tuple[str, str, str]]):
        for key, label, ftype in fields:
            yield Label(label, classes="field-label")
            if ftype == "bool":
                yield Checkbox("", id=f"{prefix}_{key}", value=bool(vals.get(key)))
            else:
                yield Input(value=str(vals.get(key, "")), id=f"{prefix}_{key}")

    def _commit(self) -> None:
        for i in range(len(self.summarizers)):
            self._read_into(self.summarizers[i], f"summ{i}", COMMON_SUMMARIZER_FIELDS)
            self._read_into(self.summarizers[i], f"summ{i}", LLM_SUMMARIZER_FIELDS)
            self._read_into(self.summarizers[i], f"summ{i}", HYBRID_SUMMARIZER_FIELDS)
            try:
                self.summarizers[i]["type"] = self.query_one(f"#summ{i}_type").value
            except Exception:  # noqa: BLE001
                pass
        self._read_into(self.app.settings["judge"], "judge", JUDGE_FIELDS)

    def on_mount(self) -> None:
        for i, summ in enumerate(self.summarizers):
            self._apply_type_display(i, summ.get("type", "llm"))

    def _apply_type_display(self, i: int, stype: str) -> None:
        try:
            self.query_one(f"#summ{i}_llmgroup").display = stype == "llm"
            self.query_one(f"#summ{i}_hybridgroup").display = stype == "hybrid"
        except Exception:  # noqa: BLE001
            pass

    def on_select_changed(self, event: Select.Changed) -> None:
        wid = event.select.id or ""
        if wid.startswith("summ") and wid.endswith("_type"):
            i = int(wid[len("summ"):-len("_type")])
            self._apply_type_display(i, str(event.value))

    def _read_into(self, target: dict, prefix: str, fields: list[tuple[str, str, str]]) -> None:
        for key, _label, ftype in fields:
            try:
                w = self.query_one(f"#{prefix}_{key}")
            except Exception:  # noqa: BLE001
                continue
            if ftype == "bool":
                target[key] = bool(w.value)
            elif ftype == "int":
                try:
                    target[key] = int(w.value)
                except ValueError:
                    pass
            elif ftype == "float":
                try:
                    target[key] = float(w.value)
                except ValueError:
                    pass
            else:
                target[key] = w.value

    def action_save_exit(self) -> None:
        self._commit()
        self.app.settings["summarizers"] = self.summarizers
        S.save(self.app.settings)
        self.notify("Settings saved", severity="information")
        self.app.pop_screen()

    def action_cancel(self) -> None:
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "save":
            self.action_save_exit()
        elif bid == "cancel":
            self.action_cancel()
        elif bid == "add_summ":
            self._commit()
            import copy

            self.summarizers.append(copy.deepcopy(S.DEFAULT_SUMMARIZER))
            self.app.switch_screen(ConfigScreen(self.summarizers))
        elif bid == "remove_current":
            self._commit()
            active = self.query_one("#cfg-tabs", TabbedContent).active or ""
            if not active.startswith("pane_summ"):
                self.notify("Switch to a summarizer tab to remove it", severity="warning")
                return
            idx = int(active.replace("pane_summ", ""))
            if len(self.summarizers) > 1:
                self.summarizers.pop(idx)
                self.app.switch_screen(ConfigScreen(self.summarizers))
            else:
                self.notify("At least one summarizer required", severity="warning")


class RunScreen(Screen):
    def __init__(self, title: str, steps: list[tuple[str, list[str]]]) -> None:
        super().__init__()
        self.title_text = title
        self.steps = steps

    def compose(self) -> ComposeResult:
        yield Static(f"Running: {self.title_text}", id="run-title")
        yield RichLog(id="run-log", markup=True)
        yield Button("Close", id="close")

    def on_mount(self) -> None:
        self.run_cmds()

    @work(thread=True)
    def run_cmds(self) -> None:
        log = self.query_one("#run-log", RichLog)
        n = len(self.steps)
        for i, (label, cmd) in enumerate(self.steps, 1):
            if n > 1:
                self.app.call_from_thread(
                    log.write, f"[bold cyan]── round {i}/{n}: {label} ──[/bold cyan]"
                )
            self.app.call_from_thread(log.write, f"[dim]$ {' '.join(cmd)}[/dim]")
            try:
                proc = subprocess.Popen(
                    cmd,
                    cwd=str(REPO),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                assert proc.stdout is not None
                for line in proc.stdout:
                    self.app.call_from_thread(log.write, line.rstrip())
                rc = proc.wait()
                color = "green" if rc == 0 else "red"
                self.app.call_from_thread(log.write, f"[{color}]=== exit {rc} ===[/{color}]")
            except Exception as exc:  # noqa: BLE001
                self.app.call_from_thread(log.write, f"[red]ERROR: {exc}[/red]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.app.pop_screen()


class ResultsScreen(Screen):
    def __init__(
        self, summaries_dir: str | None = None, texts_dir: str | None = None
    ) -> None:
        super().__init__()
        self._summaries_dir = summaries_dir
        self._texts_dir = texts_dir

    def compose(self) -> ComposeResult:
        with Horizontal(id="res-filters"):
            yield Label("System:")
            yield Select([], id="res_system")
            yield Label("Level:")
            yield Select([("all", "all")], id="res_level")
        with Horizontal(id="res-body"):
            with Vertical(id="res-list-pane"):
                yield ListView(id="res-list")
            with VerticalScroll(id="res-detail"):
                yield Static("Select a summary", id="res-detail-text")
        yield Button("Back", id="back")

    def on_mount(self) -> None:
        self.summ_root = REPO / (
            self._summaries_dir or self.app.settings["judge"]["summaries_dir"]
        )
        systems = (
            sorted(d.name for d in self.summ_root.iterdir() if d.is_dir())
            if self.summ_root.exists()
            else []
        )
        sys_sel = self.query_one("#res_system", Select)
        sys_sel.set_options([(s, s) for s in systems])
        if systems:
            sys_sel.value = systems[0]
        self._populate_levels()
        self._rebuild_list()

    def _level_label(self, tag: str) -> str:
        # r0p9 -> 0.9
        return tag[1:].replace("p", ".") if tag.startswith("r") else tag

    def _populate_levels(self) -> None:
        system = self.query_one("#res_system", Select).value
        levels: set[str] = set()
        if system and system != Select.BLANK:
            sys_dir = self.summ_root / str(system)
            if sys_dir.exists():
                for text_dir in sys_dir.iterdir():
                    if text_dir.is_dir():
                        for lvl in text_dir.iterdir():
                            if lvl.is_dir() and lvl.name.startswith("r"):
                                levels.add(lvl.name)
        lev_sel = self.query_one("#res_level", Select)
        lev_sel.set_options(
            [("all", "all")] + [(self._level_label(t), t) for t in sorted(levels)]
        )
        lev_sel.value = "all"

    def _rebuild_list(self) -> None:
        system = self.query_one("#res_system", Select).value
        level = self.query_one("#res_level", Select).value
        self.entries: list[Path] = []
        lv = self.query_one("#res-list", ListView)
        lv.clear()
        if not system or system == Select.BLANK:
            return
        sys_dir = self.summ_root / str(system)
        if not sys_dir.exists():
            return
        for text_dir in sorted(p for p in sys_dir.iterdir() if p.is_dir()):
            for lvl_dir in sorted(p for p in text_dir.iterdir() if p.is_dir()):
                if level != "all" and lvl_dir.name != level:
                    continue
                for sf in sorted(lvl_dir.glob("summary_*.txt")):
                    label = f"{text_dir.name}  ·  r={self._level_label(lvl_dir.name)}  ·  {sf.name}"
                    lv.append(ListItem(Static(label)))
                    self.entries.append(sf)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "res_system":
            self._populate_levels()
            self._rebuild_list()
        elif event.select.id == "res_level":
            self._rebuild_list()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        idx = event.list_view.index
        if idx is None or idx >= len(self.entries):
            return
        sf = self.entries[idx]
        source = self._source_for(sf)
        summary = sf.read_text(encoding="utf-8")
        jf = sf.with_suffix(".judge.json")
        judge = json.loads(jf.read_text(encoding="utf-8")) if jf.exists() else None
        qaf = sf.with_name(sf.stem + ".qa.json")
        qa = json.loads(qaf.read_text(encoding="utf-8")) if qaf.exists() else None
        detail = self.query_one("#res-detail-text", Static)
        parts = [f"[b]SOURCE[/b]\n{source}\n\n[b]SUMMARY[/b]\n{summary}"]
        if judge and judge.get("scores"):
            sc = judge["scores"]
            parts.append(f"[b]JUDGE[/b] ({judge.get('judge_model','')})\n" + "\n".join(
                f"  {k}: {v}" for k, v in sc.items()
            ))
        if qa and qa.get("scores"):
            parts.append(self._format_qa(qa))
        detail.update("\n\n".join(parts))

    @staticmethod
    def _format_qa(qa: dict) -> str:
        s = qa.get("scores", {})
        lines = [f"[b]ITEM-BASED SCORES[/b] (generator: {qa.get('generator_model','')})"]
        if "qa" in s:
            lines.append(
                f"  facts / QA-accuracy: {s['qa']['correct']}/{s['qa']['total']} "
                f"= {s['qa']['accuracy']}"
            )
        if "mcq" in s:
            lines.append(
                f"  comprehension / MCQ: raw {s['mcq']['raw']}, "
                f"chance-corrected {s['mcq']['chance_corrected']}"
            )
        if "nli" in s:
            lines.append(f"  logic / NLI: {s['nli']['accuracy']}")
        if "stance" in s:
            lines.append(f"  stance: {s['stance']['accuracy']}")
        return "\n".join(lines)

    def _source_for(self, sf: Path) -> str:
        text_id = sf.parent.parent.name
        tf = REPO / (self._texts_dir or self.app.settings["judge"]["texts_dir"]) / f"{text_id}.txt"
        return tf.read_text(encoding="utf-8") if tf.exists() else "(no source)"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()


class SmokeScreen(Screen):
    """Smoke = end-to-end plumbing check on 10 texts (2/genre)."""

    TEXTS = "smoke/texts"
    SUMM = "smoke/summaries"
    ITEMS = "smoke/items"

    def compose(self) -> ComposeResult:
        yield Static("SMOKE CORPUS", id="title", classes="big")
        yield Static(
            "Plumbing validation on 10 texts (2/genre). Run this FIRST after any "
            "pipeline change. Smoke is frozen — re-runs must stay byte-identical.",
            id="p_purpose",
        )
        with VerticalScroll(id="pilot-steps"):
            yield Static("1. Collect corpus", classes="step-h")
            with Horizontal(id="s-step1"):
                yield Button("Collect 10 texts", id="s_collect", variant="primary")
            yield Static("2. Validate corpus", classes="step-h")
            with Horizontal(id="s-step2"):
                yield Button("Run 9 checks", id="s_validate", variant="primary")
            yield Static("3. Generate items (from texts)", classes="step-h")
            with Horizontal(id="s-step3"):
                yield Button("Generate QA/MCQ/NLI/stance", id="s_items", variant="primary")
            yield Static("4. Summarize (r-grid)", classes="step-h")
            with Horizontal(id="s-step4"):
                yield Button("Summarize smoke texts", id="s_summ", variant="primary")
            yield Static("5. Score summaries", classes="step-h")
            with Horizontal(id="s-step5"):
                yield Button("Judge (rubric)", id="s_judge", variant="primary")
                yield Button("QA-accuracy (items)", id="s_qa", variant="primary")
            yield Static("6. Browse results", classes="step-h")
            with Horizontal(id="s-step6"):
                yield Button("Browse results", id="s_browse")
        yield Button("Back", id="s_back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "s_back":
            self.app.pop_screen()
        elif bid == "s_collect":
            self.app.push_screen(
                RunScreen("Collect corpus",
                         [("collect 10 texts", [PY, "-m", "smoke_collector.pipeline", "--all"])])
            )
        elif bid == "s_validate":
            self.app.push_screen(
                RunScreen("Validate",
                         [("validate corpus", [PY, "-m", "smoke_collector.validate"])])
            )
        elif bid == "s_items":
            cmd = [PY, "-m", "itemgen", "generate",
                   "--texts-dir", self.TEXTS, "--items-dir", self.ITEMS]
            self.app.push_screen(RunScreen("Generate items", [("generate items", cmd)]))
        elif bid == "s_summ":
            self.app.push_screen(SummarizeScreen(self.TEXTS, self.SUMM))
        elif bid == "s_judge":
            args = S.judge_args(self.app.settings["judge"])
            self.app.push_screen(
                RunScreen("Judge smoke",
                         [(f"judge · {self.app.settings['judge'].get('model','?')}",
                           [PY, "-m", "smoke_judge", *args])])
            )
        elif bid == "s_qa":
            cmd = [PY, "-m", "itemgen", "score",
                   "--items-dir", self.ITEMS, "--summaries-dir", self.SUMM]
            self.app.push_screen(RunScreen("QA-accuracy smoke", [("score QA", cmd)]))
        elif bid == "s_browse":
            self.app.push_screen(ResultsScreen())


class CorpusScreen(Screen):
    """Shared Build -> Rate -> Summarize -> Judge -> Browse pipeline.

    Used by the pilot and main phases; the split + dirs are parameterized so
    the same screen drives either corpus.
    """

    def __init__(
        self,
        phase: str,
        split: str,
        texts_dir: str,
        summ_dir: str,
        items_dir: str,
        default_scale: int,
        purpose: str,
    ) -> None:
        super().__init__()
        self.phase = phase
        self.split = split
        self.texts_dir = texts_dir
        self.summ_dir = summ_dir
        self.items_dir = items_dir
        self.default_scale = str(default_scale)
        self.purpose = purpose

    def compose(self) -> ComposeResult:
        yield Static(f"{self.phase} CORPUS", id="title", classes="big")
        yield Static(self.purpose, id="p_purpose")
        with VerticalScroll(id="pilot-steps"):
            yield Static("1. Build sample", classes="step-h")
            with Horizontal(id="p-step1"):
                yield Label("Split:")
                yield Select(
                    [(self.split, self.split)], id="p_split", allow_blank=False
                )
                yield Label("Seed:")
                yield Input(value="42", id="p_seed")
                yield Label("Scale:")
                yield Input(value=self.default_scale, id="p_scale")
                yield Button("Build", id="p_build", variant="primary")
            yield Static(
                "2. Rate self-containedness  (run once per rater — 2 raters required)",
                classes="step-h",
            )
            with Horizontal(id="p-step2"):
                yield Label("Rater id:")
                yield Input(value="", id="p_rater", placeholder="e.g. alice")
                yield Button("Start rating", id="p_rate", variant="warning")
            yield Static("3. Generate items (from texts)", classes="step-h")
            with Horizontal(id="p-step3"):
                yield Button("Generate QA/MCQ/NLI/stance", id="p_items", variant="primary")
            yield Static("4. Summarize (r-grid)", classes="step-h")
            with Horizontal(id="p-step4"):
                yield Button(
                    f"Summarize {self.phase.lower()} texts", id="p_summ", variant="primary"
                )
            yield Static("5. Score summaries", classes="step-h")
            with Horizontal(id="p-step5"):
                yield Button(
                    f"Judge {self.phase.lower()} (rubric)", id="p_judge", variant="primary"
                )
                yield Button("QA-accuracy (items)", id="p_qa", variant="primary")
            yield Static("6. Browse", classes="step-h")
            with Horizontal(id="p-step6"):
                yield Button("Browse texts", id="p_browse")
                yield Button("Browse results", id="p_bresults")
        with Vertical(id="pilot-status-pane"):
            yield Static("", id="p_status")
        yield Button("Back", id="p_back")

    def on_mount(self) -> None:
        self._refresh_status()

    def _refresh_status(self, full: bool = False) -> None:
        from pilot import raters as R

        texts_dir, ratings_path = R.split_paths(self.split)
        texts = R.load_pilot_texts(texts_dir)
        ratings = R.load_ratings(ratings_path)
        agg = R.aggregate(ratings)
        s = R.summary(agg)
        by_genre: dict[str, int] = {}
        for tid in texts:
            g = tid.split("-")[1] if "-" in tid else "?"
            by_genre[g] = by_genre.get(g, 0) + 1
        summ_dir = REPO / self.summ_dir
        n_summ = len(list(summ_dir.glob("**/*.json"))) if summ_dir.exists() else 0
        n_judg = (
            len(list(summ_dir.glob("**/*.judge.json"))) if summ_dir.exists() else 0
        )
        n_qa = len(list(summ_dir.glob("**/*.qa.json"))) if summ_dir.exists() else 0
        items_dir = REPO / self.items_dir
        n_items = len(list(items_dir.glob("*.items.json"))) if items_dir.exists() else 0
        lines = [f"=== {self.phase} status ==="]
        lines.append(
            f"[1] texts: {len(texts)}   "
            + "  ".join(f"{g}:{c}" for g, c in sorted(by_genre.items()))
        )
        lines.append(
            f"[2] ratings: {len(ratings)}   accept:{s['accept']}  reject:{s['reject']}  "
            f"disagree:{s['disagree']}  incomplete:{s['incomplete']}  "
            f"disagreement rate: {s['disagreement_rate']:.0%}"
        )
        present = sorted({r["rater"] for r in ratings})
        lines.append(f"    raters: {', '.join(present) if present else '(none)'}")
        lines.append(f"[3] items: {n_items}   [4] summaries: {n_summ}")
        lines.append(f"[5] judgments: {n_judg}   [5] QA-scored: {n_qa}")
        if full:
            dis = sorted(t for t, v in agg.items() if v["status"] == "disagree")
            if dis:
                lines.append("\nNEEDS ADJUDICATION:")
                for tid in dis:
                    lines.append(f"  {tid}: {agg[tid]['verdicts']}")
            inc = [t for t, v in agg.items() if v["status"] == "incomplete"]
            if inc:
                lines.append(f"\nIncomplete (need 2nd rater): {len(inc)}")
        self.query_one("#p_status", Static).update("\n".join(lines))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "p_back":
            self.app.pop_screen()
        elif bid == "p_build":
            seed = self.query_one("#p_seed", Input).value or "42"
            scale = self.query_one("#p_scale", Input).value or self.default_scale
            cmd = [PY, "-m", "pilot", "--split", self.split,
                   "--seed", str(seed), "--scale", str(scale)]
            self.app.push_screen(
                RunScreen(f"Build {self.split}", [(f"build {self.split}", cmd)])
            )
        elif bid == "p_rate":
            rater = (self.query_one("#p_rater", Input).value or "").strip()
            if not rater:
                self.notify("Enter a rater id first", severity="warning")
                return
            self.app.push_screen(RaterScreen(rater, split=self.split))
        elif bid == "p_items":
            cmd = [PY, "-m", "itemgen", "generate",
                   "--texts-dir", self.texts_dir, "--items-dir", self.items_dir]
            self.app.push_screen(
                RunScreen(f"Generate {self.phase.lower()} items",
                         [("generate items", cmd)])
            )
        elif bid == "p_summ":
            self.app.push_screen(SummarizeScreen(self.texts_dir, self.summ_dir))
        elif bid == "p_judge":
            cmd = [PY, "-m", "smoke_judge",
                   *S.pilot_judge_args(
                       self.app.settings["judge"], self.summ_dir, self.texts_dir
                    )]
            self.app.push_screen(
                RunScreen(
                    f"Judge {self.phase.lower()}",
                    [(f"judge {self.phase.lower()} summaries", cmd)],
                )
            )
        elif bid == "p_qa":
            cmd = [PY, "-m", "itemgen", "score",
                   "--items-dir", self.items_dir, "--summaries-dir", self.summ_dir]
            self.app.push_screen(
                RunScreen(f"QA-accuracy {self.phase.lower()}",
                         [("score QA", cmd)])
            )
        elif bid == "p_browse":
            from pilot import raters as R

            texts_dir, ratings_path = R.split_paths(self.split)
            self.app.push_screen(
                PilotBrowseScreen(texts_dir=texts_dir, ratings_path=ratings_path)
            )
        elif bid == "p_bresults":
            self.app.push_screen(
                ResultsScreen(summaries_dir=self.summ_dir, texts_dir=self.texts_dir)
            )


class PilotScreen(CorpusScreen):
    def __init__(self) -> None:
        super().__init__(
            phase="PILOT",
            split="pilot",
            texts_dir="pilot_data/texts",
            summ_dir="pilot_data/summaries",
            items_dir="pilot_data/items",
            default_scale=10,
            purpose=(
                "Calibration gate: a larger balanced sample (10/genre) to validate "
                "the sampler, confirm self-containedness with 2 human raters, and "
                "derive power-analysis parameters. Pilot texts are EXCLUDED from "
                "the main corpus."
            ),
        )


class MainScreen(CorpusScreen):
    def __init__(self) -> None:
        super().__init__(
            phase="MAIN",
            split="main",
            texts_dir="pilot_data/main",
            summ_dir="pilot_data/main_summaries",
            items_dir="pilot_data/main_items",
            default_scale=40,
            purpose=(
                "Confirmatory corpus: the real study data (~400 texts). Built by "
                "the same sampler at a larger scale. Disjoint from pilot. Run the "
                "full pipeline here only AFTER the pilot config is frozen."
            ),
        )


class RaterScreen(Screen):
    def __init__(self, rater: str, split: str = "pilot") -> None:
        super().__init__()
        self.rater = rater
        self.split = split
        self.texts: dict[str, str] = {}
        self.ratings: list[dict] = []
        self.ratings_path = None
        self.todo: list[str] = []
        self.pos = 0
        self.rated = 0
        self.skipped = 0

    def compose(self) -> ComposeResult:
        yield Static("", id="r_hdr", classes="big")
        with VerticalScroll(id="r_text_scroll"):
            yield Static("", id="r_text")
        yield Label("Note (optional — required if 'not self-contained'):")
        yield Input(id="r_note")
        with Horizontal(id="r_actions"):
            yield Button("Self-contained (y)", id="r_yes", variant="success")
            yield Button("Not (n)", id="r_no", variant="error")
            yield Button("Skip", id="r_skip")
            yield Button("Back", id="r_back")

    def on_mount(self) -> None:
        from pilot import raters as R

        texts_dir, self.ratings_path = R.split_paths(self.split)
        self.texts = R.load_pilot_texts(texts_dir)
        self.ratings = R.load_ratings(self.ratings_path)
        self.todo = R.unrated_for(self.rater, self.texts, self.ratings)
        self._show()

    def _show(self) -> None:
        hdr = self.query_one("#r_hdr", Static)
        if self.pos >= len(self.todo):
            hdr.update(
                f"Rater '{self.rater}' [{self.split}]: session complete — "
                f"{self.rated} rated, {self.skipped} skipped."
            )
            for b in ("r_yes", "r_no", "r_skip"):
                self.query_one(f"#{b}", Button).disabled = True
            return
        tid = self.todo[self.pos]
        hdr.update(
            f"Rater '{self.rater}' [{self.split}] — {tid}   "
            f"({self.pos + 1}/{len(self.todo)} remaining)"
        )
        self.query_one("#r_text", Static).update(self.texts[tid])
        self.query_one("#r_note", Input).value = ""
        self.query_one("#r_note", Input).focus()

    def _record(self, sc: bool) -> None:
        from pilot import raters as R

        tid = self.todo[self.pos]
        note = self.query_one("#r_note", Input).value.strip()
        if not sc and not note:
            self.notify("Please add a note when rating 'not self-contained'",
                       severity="warning")
            return
        self.ratings = R.record_rating(self.ratings, self.rater, tid, sc, note)
        R.save_ratings(self.ratings, self.ratings_path)
        self.rated += 1
        self.pos += 1
        self._show()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "r_back":
            self.app.pop_screen()
        elif bid == "r_yes":
            self._record(True)
        elif bid == "r_no":
            self._record(False)
        elif bid == "r_skip":
            if self.pos < len(self.todo):
                self.skipped += 1
                self.pos += 1
                self._show()

    def on_key(self, event) -> None:  # keyboard shortcuts
        if self.pos >= len(self.todo):
            return
        if event.key in ("y", "n"):
            self._record(event.key == "y")
            event.stop()
        elif event.key == "s":
            self.skipped += 1
            self.pos += 1
            self._show()
            event.stop()


class PilotBrowseScreen(Screen):
    def __init__(
        self,
        texts_dir=None,
        ratings_path=None,
    ) -> None:
        super().__init__()
        self._texts_dir = texts_dir
        self._ratings_path = ratings_path

    def compose(self) -> ComposeResult:
        with Horizontal(id="res-body"):
            with Vertical(id="res-list-pane"):
                yield ListView(id="pb_list")
            with VerticalScroll(id="res-detail"):
                yield Static("Select a text", id="pb_detail")
        yield Button("Back", id="pb_back")

    def on_mount(self) -> None:
        from pilot import raters as R

        self.texts = R.load_pilot_texts(self._texts_dir)
        self.agg = R.aggregate(R.load_ratings(self._ratings_path))
        self.ids = sorted(self.texts)
        lv = self.query_one("#pb_list", ListView)
        for tid in self.ids:
            wc = len(self.texts[tid].split())
            st = self.agg.get(tid, {}).get("status", "unrated")
            lv.append(ListItem(Static(f"{tid}  {wc}w  [{st}]")))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.index is None:
            return
        tid = self.ids[event.list_view.index]
        self.query_one("#pb_detail", Static).update(self.texts[tid])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "pb_back":
            self.app.pop_screen()


class PromptViewerScreen(Screen):
    """Browse every prompt template in the pipeline with its SHA-256 hash."""

    def compose(self) -> ComposeResult:
        yield Static("PROMPT VIEWER", id="title", classes="big")
        yield Static(
            "All prompt templates (RU). Hash = SHA-256 of the exact string, for "
            "the freeze / OSF manifest.",
            id="p_purpose",
        )
        with Horizontal(id="res-body"):
            with Vertical(id="res-list-pane"):
                yield ListView(id="pv_list")
            with VerticalScroll(id="res-detail"):
                yield Static("Select a prompt", id="pv_detail")
        yield Button("Back", id="pv_back")

    def on_mount(self) -> None:
        from .prompt_registry import collect_prompts

        self.groups = collect_prompts()
        self.items: list[tuple[str, str, str]] = []
        lv = self.query_one("#pv_list", ListView)
        for gname, prompts in self.groups:
            for name, text in prompts:
                self.items.append((gname, name, text))
                lv.append(ListItem(Static(f"{gname} · {name}")))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.index is None:
            return
        from .prompt_registry import prompt_hash

        gname, name, text = self.items[event.list_view.index]
        h = prompt_hash(text)
        self.query_one("#pv_detail", Static).update(
            f"[b]{gname} · {name}[/b]\n"
            f"[dim]SHA-256: {h}  ({len(text)} chars)[/dim]\n\n{text}"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "pv_back":
            self.app.pop_screen()


class SummarizeScreen(Screen):
    """Run summarizers ONE model at a time (endpoint serves one model at a time).

    Shows each configured summarizer with a done/pending status; each Run
    launches a single-model pass. Switch the endpoint model before each pass.
    """

    def __init__(self, texts_dir: str, summ_dir: str) -> None:
        super().__init__()
        self.texts_dir = texts_dir
        self.summ_dir = summ_dir

    def compose(self) -> ComposeResult:
        yield Static("SUMMARIZE — one model per pass", id="title", classes="big")
        yield Static(
            "Only one model is active on the endpoint at a time. Switch the "
            "endpoint to the model, then Run that pass. Passes are resumable — "
            "already-generated summaries are skipped.",
            id="p_purpose",
        )
        with VerticalScroll(id="summ-list"):
            for i, s in enumerate(self.app.settings["summarizers"]):
                with Horizontal(id=f"summ-row{i}"):
                    yield Static(self._row_label(s), id=f"summ_lbl{i}")
                    yield Button("Run", id=f"summ_run{i}", variant="primary")
        with Horizontal(id="summ-foot"):
            yield Button("Refresh status", id="summ_refresh")
            yield Button("Back", id="summ_back")

    def _is_done(self, system: str) -> bool:
        d = REPO / self.summ_dir / str(system)
        return d.exists() and any(d.rglob("summary_*.txt"))

    def _row_label(self, s: dict) -> str:
        stype = s.get("type", "llm")
        sysname = s.get("system", "?")
        model = s.get("model", "")
        mark = "[green]✓ done[/green]" if self._is_done(sysname) else "[dim]— pending[/dim]"
        return f"[b][{stype}][/b] {sysname} · {model}   {mark}"

    def _refresh_status(self, *_args) -> None:
        for i, s in enumerate(self.app.settings["summarizers"]):
            self.query_one(f"#summ_lbl{i}", Static).update(self._row_label(s))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "summ_back":
            self.app.pop_screen()
        elif bid == "summ_refresh":
            self._refresh_status()
        elif bid.startswith("summ_run"):
            i = int(bid[len("summ_run"):])
            s = self.app.settings["summarizers"][i]
            cmd = [PY, "-m", "smoke_summarizer",
                   *S.pilot_summarizer_args(s, self.texts_dir, self.summ_dir)]
            self.app.push_screen(
                RunScreen(
                    f"Summarize · {s.get('system','?')}",
                    [(f"{s.get('system','?')} · {s.get('model','')}", cmd)],
                ),
                callback=self._refresh_status,
            )


class WebTaskScreen(Screen):
    """Export/import task sheets for web-UI-only models (Alisa, GigaChat)."""

    def compose(self) -> ComposeResult:
        yield Static("WEB-UI MODELS", id="title", classes="big")
        yield Static(
            "For models with no API (Alisa / GigaChat): export a self-contained "
            "task sheet, run each prompt in the web UI, paste the answers back "
            "into the sheet, then import. Imported summaries use the standard "
            "layout, so judge + QA score them like any other.",
            id="p_purpose",
        )
        with VerticalScroll(id="wt-body"):
            yield Static("1. Export task sheet", classes="step-h")
            with Horizontal(id="wt-exp"):
                yield Label("System:")
                yield Input(value="alisa", id="wt_system")
                yield Label("Texts dir:")
                yield Input(value="smoke/texts", id="wt_texts")
                yield Label("Levels:")
                yield Input(value="", id="wt_levels", placeholder="blank = r-grid")
                yield Button("Export", id="wt_export", variant="primary")
            yield Static("2. Import the filled sheet", classes="step-h")
            with Horizontal(id="wt-imp"):
                yield Label("Sheet path:")
                yield Input(value="", id="wt_sheet", placeholder="/path/filled.md")
                yield Label("Operator:")
                yield Input(value="", id="wt_op")
                yield Label("Out dir:")
                yield Input(value="smoke/summaries", id="wt_out")
                yield Button("Import", id="wt_import", variant="warning")
        yield Button("Back", id="wt_back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "wt_back":
            self.app.pop_screen()
        elif bid == "wt_export":
            system = (self.query_one("#wt_system", Input).value or "alisa").strip()
            texts = (self.query_one("#wt_texts", Input).value or "smoke/texts").strip()
            levels = (self.query_one("#wt_levels", Input).value or "").strip()
            out = f"{system}_tasks.md"
            cmd = [PY, "-m", "webtask", "export", "--system", system,
                   "--texts-dir", texts, "--out", out]
            if levels:
                cmd += ["--levels", levels]
            self.app.push_screen(
                RunScreen(f"Export {system} sheet", [("export", cmd)])
            )
        elif bid == "wt_import":
            system = (self.query_one("#wt_system", Input).value or "alisa").strip()
            sheet = (self.query_one("#wt_sheet", Input).value or "").strip()
            if not sheet:
                self.notify("Enter the filled sheet path first", severity="warning")
                return
            op = (self.query_one("#wt_op", Input).value or "").strip()
            out = (self.query_one("#wt_out", Input).value or "smoke/summaries").strip()
            cmd = [PY, "-m", "webtask", "import", "--system", system,
                   "--sheet", sheet, "--out-dir", out]
            if op:
                cmd += ["--operator", op]
            self.app.push_screen(
                RunScreen(f"Import {system} sheet", [("import", cmd)])
            )


class SmokeApp(App):
    CSS = """
    #title { text-align: center; text-style: bold; padding: 1 0; }
    .big { text-style: bold; }
    Button { margin: 1 2; }
    #run-log { height: 1fr; }
    #res-list-pane { width: 1fr; }
    #res-detail { width: 2fr; border-left: solid $primary; }
    #res-filters { height: 3; dock: top; align-horizontal: center; }
    #res-filters Label { margin: 0 1 0 2; }
    #res-filters Select { width: 28; margin: 0 1; }
    #res-body { height: 1fr; }
    .field-label { margin-top: 1; }
    #cfg-actions { height: 3; dock: bottom; }
    #cfg-tabs { height: 1fr; }
    #p_purpose { padding: 0 2 1 2; color: $text-muted; }
    #pilot-steps { height: 1fr; }
    .step-h { text-style: bold; margin-top: 1; padding: 0 1; }
    #p-step1, #p-step2, #p-step3, #p-step4, #p-step5, #p-step6 {
        height: 3; align-horizontal: center;
    }
    #s-step1, #s-step2, #s-step3, #s-step4, #s-step5, #s-step6 {
        height: 3; align-horizontal: center;
    }
    #p-step1 Label, #p-step2 Label { margin: 0 1 0 2; }
    #p-step1 Input { width: 10; }
    #p-step1 Select { width: 18; }
    #p-step2 Input { width: 18; }
    #pilot-status-pane { height: 9; dock: bottom; border: round $primary; padding: 0 2; }
    #r_hdr { text-style: bold; padding: 0 1; }
    #r_text_scroll { height: 1fr; border: round $secondary; padding: 1 2; }
    #r_note { width: 100%; }
    #r_actions { height: 3; dock: bottom; align-horizontal: center; }
    #summ-list { height: 1fr; }
    .summ-row, #summ-row0, #summ-row1, #summ-row2, #summ-row3, #summ-row4,
    #summ-row5, #summ-row6, #summ-row7 { height: 3; align-horizontal: left; }
    #summ-foot { height: 3; dock: bottom; align-horizontal: center; }
    #wt-body { height: 1fr; }
    #wt-exp, #wt-imp { height: 3; align-horizontal: center; }
    #wt-exp Label, #wt-imp Label { margin: 0 1 0 2; }
    #wt-exp Input, #wt-imp Input { width: 22; }
    """

    def __init__(self) -> None:
        super().__init__()
        self.settings = S.load()

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())


def main() -> None:
    SmokeApp().run()


if __name__ == "__main__":
    main()
