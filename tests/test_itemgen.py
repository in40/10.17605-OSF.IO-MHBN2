import json

from itemgen import prompts
from itemgen.config import ItemGenConfig
from itemgen.generator import generate_items, generate_mcq, generate_qa
from itemgen.jsonutil import extract_array, extract_object
from itemgen.manifest import build_manifest, hash_item, manifest_digest
from itemgen.scorer import (
    mcq_accuracy,
    qa_accuracy,
    score_summary,
)


class FakeResult:
    def __init__(self, content):
        self.content = content
        self.reasoning = ""
        self.finish_reason = "stop"
        self.usage = {}
        self.raw = {}


class FakeClient:
    def __init__(self, responder):
        self.responder = responder
        self.calls = []

    def chat(self, messages, **kw):
        prompt = messages[-1]["content"]
        self.calls.append(prompt)
        return FakeResult(self.responder(prompt))


def _cfg(**kw):
    return ItemGenConfig(**kw)


# ---- jsonutil ----

def test_extract_array_plain():
    assert extract_array('x [{"a":1}] y') == [{"a": 1}]


def test_extract_array_fenced():
    assert extract_array('```json\n[{"a": 1}]\n```') == [{"a": 1}]


def test_extract_object():
    assert extract_object('blah {"correct": true} blah') == {"correct": True}


def test_extract_none():
    assert extract_array("no json here") == []


# ---- generation ----

def test_generate_qa_basic():
    def resp(p):
        return '[{"question":"Q1?","gold_answer":"A1"},{"question":"Q2?","gold_answer":"A2"}]'

    items = generate_qa(FakeClient(resp), _cfg(), "src")
    assert len(items) == 2
    assert items[0]["gold_answer"] == "A1"
    assert items[0]["kind"] == "qa"


def test_generate_mcq_drops_malformed():
    def resp(p):
        return json.dumps([
            {"question": "ok?", "options": ["a", "b", "c", "d"], "correct_index": 2},
            {"question": "bad opts", "options": ["a", "b"], "correct_index": 0},
            {"question": "bad idx", "options": ["a", "b", "c", "d"], "correct_index": 9},
        ])

    items = generate_mcq(FakeClient(resp), _cfg(), "src")
    assert len(items) == 1
    assert items[0]["correct_index"] == 2


def test_generate_items_assigns_ids():
    def resp(p):
        if "фактических вопросов" in p:
            return '[{"question":"Q1?","gold_answer":"A1"},{"question":"Q2?","gold_answer":"A2"}]'
        if "на понимание" in p:
            return '[{"question":"M1?","options":["a","b","c","d"],"correct_index":0}]'
        if "гипотез" in p:
            return '[{"hypothesis":"H1","label":"entailment"},{"hypothesis":"Hbad","label":"wrong"}]'
        if "позицию текста" in p:
            return '[{"claim":"C1","stance":"support"}]'
        return "[]"

    out = generate_items(FakeClient(resp), _cfg(), "src")
    assert [i["id"] for i in out["qa"]] == ["qa01", "qa02"]
    assert out["mcq"][0]["id"] == "mcq01"
    assert len(out["nli"]) == 1  # invalid label dropped
    assert out["nli"][0]["label"] == "entailment"
    assert out["stance"][0]["stance"] == "support"


# ---- scoring ----

def _qa_items():
    return [
        {"id": "qa01", "kind": "qa", "question": "Q1?", "gold_answer": "A1"},
        {"id": "qa02", "kind": "qa", "question": "Q2?", "gold_answer": "A2"},
    ]


def test_qa_accuracy_half_correct():
    def resp(p):
        if "Вопрос: Q1?" in p and "answer" in p:
            return '{"answer": "A1"}'
        if "Вопрос: Q2?" in p and "answer" in p:
            return '{"answer": "wrong"}'
        if "Эталон: A1" in p:
            return '{"correct": true}'
        if "Эталон: A2" in p:
            return '{"correct": false}'
        return "{}"

    res = qa_accuracy(FakeClient(resp), _cfg(), _qa_items(), "summary")
    assert res["correct"] == 1
    assert res["total"] == 2
    assert res["accuracy"] == 0.5


def test_qa_not_stated_is_incorrect():
    def resp(p):
        if "answer" in p:
            return '{"answer": "NOT_STATED"}'
        return '{"correct": true}'  # should never be consulted

    res = qa_accuracy(FakeClient(resp), _cfg(), _qa_items(), "summary")
    assert res["correct"] == 0


def test_mcq_chance_correction():
    items = [
        {"id": "mcq01", "kind": "mcq", "question": "M1?", "options": ["a", "b", "c", "d"], "correct_index": 0},
        {"id": "mcq02", "kind": "mcq", "question": "M2?", "options": ["a", "b", "c", "d"], "correct_index": 1},
    ]

    def resp(p):
        if "M1?" in p:
            return '{"choice": 0}'  # correct
        if "M2?" in p:
            return '{"choice": 0}'  # wrong (gold=1)
        return "{}"

    res = mcq_accuracy(FakeClient(resp), _cfg(), items, "summary")
    assert res["correct"] == 1
    assert res["raw"] == 0.5
    assert res["chance_corrected"] == round((0.5 - 0.25) / 0.75, 4)


def test_score_summary_integrates_kinds():
    items_by_kind = {
        "qa": _qa_items(),
        "mcq": [
            {"id": "mcq01", "kind": "mcq", "question": "M1?", "options": ["a", "b", "c", "d"], "correct_index": 0}
        ],
    }

    def resp(p):
        if "Вопрос: Q1?" in p and "answer" in p:
            return '{"answer": "A1"}'
        if "Вопрос: Q2?" in p and "answer" in p:
            return '{"answer": "A2"}'
        if "Эталон" in p:
            return '{"correct": true}'
        if "M1?" in p:
            return '{"choice": 0}'
        return "{}"

    out = score_summary(FakeClient(resp), _cfg(), items_by_kind, "summary")
    assert out["qa"]["accuracy"] == 1.0
    assert out["mcq"]["raw"] == 1.0
    assert "nli" not in out  # no nli items provided


# ---- manifest ----

def test_hash_item_stable_and_order_independent():
    a = hash_item({"x": 1, "y": 2})
    b = hash_item({"y": 2, "x": 1})
    assert a == b
    assert a != hash_item({"x": 1, "y": 3})


def test_build_manifest_structure():
    items = {
        "T1": {"qa": [{"id": "qa01", "kind": "qa", "question": "Q", "gold_answer": "A"}]},
    }
    man = build_manifest(items)
    assert "qa" in man["T1"]
    assert len(man["T1"]["qa"]) == 1
    assert "combined" in man["T1"]


def test_manifest_digest_deterministic():
    items = {"T1": {"qa": [{"id": "qa01", "kind": "qa", "question": "Q", "gold_answer": "A"}]}}
    assert manifest_digest(build_manifest(items)) == manifest_digest(build_manifest(items))
