"""Score a summary by answering frozen items using ONLY the summary."""
from __future__ import annotations

import logging

from . import prompts
from .jsonutil import extract_object

log = logging.getLogger(__name__)

NOT_STATED = "NOT_STATED"


def _ask_obj(client, cfg, prompt) -> dict:
    extra = cfg.chat_extra()
    for _attempt in range(1 + cfg.retries):
        res = client.chat(
            [{"role": "user", "content": prompt}],
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            seed=cfg.seed,
            extra=extra or None,
        )
        obj = extract_object(res.content or res.reasoning)
        if obj:
            return obj
    return {}


def answer_qa(client, cfg, question: str, summary: str) -> str:
    obj = _ask_obj(client, cfg, prompts.QA_ANSWER.format(question=question, summary=summary))
    return str(obj.get("answer", "")).strip()


def judge_qa_correct(client, cfg, question: str, gold: str, answer: str) -> bool:
    if not answer or answer.strip().upper().startswith(NOT_STATED):
        return False
    obj = _ask_obj(
        client,
        cfg,
        prompts.QA_JUDGE.format(question=question, gold=gold, answer=answer),
    )
    return bool(obj.get("correct"))


def qa_accuracy(client, cfg, items: list[dict], summary: str) -> dict:
    per = []
    correct = 0
    for it in items:
        ans = answer_qa(client, cfg, it["question"], summary)
        ok = judge_qa_correct(client, cfg, it["question"], it["gold_answer"], ans)
        correct += int(ok)
        per.append({"id": it["id"], "answer": ans, "correct": ok})
    total = len(items)
    return {
        "correct": correct,
        "total": total,
        "accuracy": round(correct / total, 4) if total else 0.0,
        "per_item": per,
    }


def answer_mcq(client, cfg, item: dict, summary: str) -> int:
    opts = "\n".join(f"{i}: {o}" for i, o in enumerate(item["options"]))
    obj = _ask_obj(
        client, cfg, prompts.MCQ_ANSWER.format(question=item["question"], options=opts, summary=summary)
    )
    try:
        return int(obj.get("choice", -1))
    except (TypeError, ValueError):
        return -1


def mcq_accuracy(client, cfg, items: list[dict], summary: str, chance: float = 0.25) -> dict:
    per = []
    correct = 0
    for it in items:
        ch = answer_mcq(client, cfg, it, summary)
        ok = ch == it["correct_index"]
        correct += int(ok)
        per.append({"id": it["id"], "choice": ch, "correct": ok})
    total = len(items)
    raw = correct / total if total else 0.0
    corrected = (raw - chance) / (1 - chance) if total else 0.0
    return {
        "correct": correct,
        "total": total,
        "raw": round(raw, 4),
        "chance_corrected": round(max(0.0, corrected), 4),
        "per_item": per,
    }


def answer_nli(client, cfg, item: dict, summary: str) -> str:
    obj = _ask_obj(
        client, cfg, prompts.NLI_ANSWER.format(hypothesis=item["hypothesis"], summary=summary)
    )
    return str(obj.get("label", "")).strip().lower()


def nli_accuracy(client, cfg, items: list[dict], summary: str) -> dict:
    per = []
    correct = 0
    for it in items:
        lab = answer_nli(client, cfg, it, summary)
        ok = lab == it["label"]
        correct += int(ok)
        per.append({"id": it["id"], "label": lab, "correct": ok})
    total = len(items)
    return {
        "correct": correct,
        "total": total,
        "accuracy": round(correct / total, 4) if total else 0.0,
        "per_item": per,
    }


def answer_stance(client, cfg, item: dict, summary: str) -> str:
    obj = _ask_obj(
        client, cfg, prompts.STANCE_ANSWER.format(claim=item["claim"], summary=summary)
    )
    return str(obj.get("stance", "")).strip().lower()


def stance_accuracy(client, cfg, items: list[dict], summary: str) -> dict:
    per = []
    correct = 0
    for it in items:
        st = answer_stance(client, cfg, it, summary)
        ok = st == it["stance"]
        correct += int(ok)
        per.append({"id": it["id"], "stance": st, "correct": ok})
    total = len(items)
    return {
        "correct": correct,
        "total": total,
        "accuracy": round(correct / total, 4) if total else 0.0,
        "per_item": per,
    }


def score_summary(client, cfg, items_by_kind: dict[str, list[dict]], summary: str) -> dict:
    """Score one summary against all item kinds."""
    out: dict = {}
    if items_by_kind.get("qa"):
        out["qa"] = qa_accuracy(client, cfg, items_by_kind["qa"], summary)
    if items_by_kind.get("mcq"):
        out["mcq"] = mcq_accuracy(client, cfg, items_by_kind["mcq"], summary)
    if items_by_kind.get("nli"):
        out["nli"] = nli_accuracy(client, cfg, items_by_kind["nli"], summary)
    if items_by_kind.get("stance"):
        out["stance"] = stance_accuracy(client, cfg, items_by_kind["stance"], summary)
    return out
