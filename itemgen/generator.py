"""Generate frozen items from an original text via the LLM."""
from __future__ import annotations

import logging

from . import prompts
from .jsonutil import extract_array

log = logging.getLogger(__name__)

KINDS = ("qa", "mcq", "nli", "stance")
NLI_LABELS = {"entailment", "neutral", "contradiction"}
STANCE_LABELS = {"support", "oppose", "neutral"}


def _ask_array(client, cfg, prompt) -> list:
    extra = cfg.chat_extra()
    for _attempt in range(1 + cfg.retries):
        res = client.chat(
            [{"role": "user", "content": prompt}],
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            seed=cfg.seed,
            extra=extra or None,
        )
        arr = extract_array(res.content or res.reasoning)
        if arr:
            return arr
    return []


def generate_qa(client, cfg, source: str) -> list[dict]:
    arr = _ask_array(client, cfg, prompts.QA_GEN.format(n=cfg.n_qa, source=source))
    items = []
    for o in arr:
        if isinstance(o, dict) and o.get("question") and o.get("gold_answer"):
            items.append(
                {
                    "kind": "qa",
                    "question": str(o["question"]).strip(),
                    "gold_answer": str(o["gold_answer"]).strip(),
                }
            )
    return items


def generate_mcq(client, cfg, source: str) -> list[dict]:
    arr = _ask_array(client, cfg, prompts.MCQ_GEN.format(n=cfg.n_mcq, source=source))
    items = []
    for o in arr:
        opts = o.get("options") if isinstance(o, dict) else None
        ci = o.get("correct_index") if isinstance(o, dict) else None
        if (
            isinstance(opts, list)
            and len(opts) == 4
            and isinstance(ci, int)
            and 0 <= ci < 4
            and o.get("question")
        ):
            items.append(
                {
                    "kind": "mcq",
                    "question": str(o["question"]).strip(),
                    "options": [str(x).strip() for x in opts],
                    "correct_index": ci,
                }
            )
    return items


def generate_nli(client, cfg, source: str) -> list[dict]:
    arr = _ask_array(client, cfg, prompts.NLI_GEN.format(n=cfg.n_nli, source=source))
    items = []
    for o in arr:
        lab = str(o.get("label", "")).strip().lower() if isinstance(o, dict) else ""
        if isinstance(o, dict) and o.get("hypothesis") and lab in NLI_LABELS:
            items.append(
                {"kind": "nli", "hypothesis": str(o["hypothesis"]).strip(), "label": lab}
            )
    return items


def generate_stance(client, cfg, source: str) -> list[dict]:
    arr = _ask_array(client, cfg, prompts.STANCE_GEN.format(n=cfg.n_stance, source=source))
    items = []
    for o in arr:
        st = str(o.get("stance", "")).strip().lower() if isinstance(o, dict) else ""
        if isinstance(o, dict) and o.get("claim") and st in STANCE_LABELS:
            items.append({"kind": "stance", "claim": str(o["claim"]).strip(), "stance": st})
    return items


_GENERATORS = {
    "qa": generate_qa,
    "mcq": generate_mcq,
    "nli": generate_nli,
    "stance": generate_stance,
}


def generate_items(client, cfg, source: str, kinds=KINDS) -> dict[str, list[dict]]:
    """Return {kind: [items]} for one source text."""
    out: dict[str, list[dict]] = {}
    for kind in kinds:
        gen = _GENERATORS[kind]
        items = gen(client, cfg, source)
        for i, it in enumerate(items):
            it["id"] = f"{kind}{i + 1:02d}"
        out[kind] = items
        log.info("generated %d %s items", len(items), kind)
    return out
