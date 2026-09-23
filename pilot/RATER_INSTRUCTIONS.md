# Rater Instructions — Pilot Self-Containedness

**Purpose.** Before pilot texts enter the corpus, each must be confirmed
**self-contained** by **two independent raters** with consensus (pre-reg
`04_sampling.md` §4.2:54). Smoke used solo judgment; the pilot requires two.

You are a rater. Your job is to read each text and decide: **can a reader
understand this text on its own, with no outside context?**

---

## What "self-contained" means

A text is **self-contained (YES)** if a reader with no other material can
follow it start to finish. Check against the genre criteria:

- **Instruction** — one complete procedural task ("how to apply for X",
  "how to fill Y"). Steps are present and ordered. The reader is not sent
  to a missing page for the actual procedure.
- **Fiction** — a scene/passage with setting + action that **reads complete**.
  Not cut mid-sentence, mid-scene, or mid-thought.
- **Dialogue** — a coherent exchange on one topic. Not a fragment that
  references a prior/next conversation.
- **News / Science** — the article stands alone; no "continued tomorrow",
  no reliance on a prior article to make sense.

## Red flags → rate **NO**

- Dangling references: «продолжение следует», «как упоминалось выше»,
  «об этом в следующей главе», «см. часть 1» — pointing to **missing** parts.
- Abrupt ending: cut mid-sentence, mid-scene, mid-list, mid-thought.
- Missing setup: opens mid-action/mid-argument with no context to ground it.
- Broken references: «этот», «данный», «вышеуказанный» with no antecedent
  present in the text.
- Placeholder / navigation junk: menus, breadcrumbs, "read more", cookie
  banners, image captions with no body.
- Truncated tables/lists that stop without resolution.

## Borderline — use judgment, but **note it**

- A text that is *mostly* complete but has one weak dangling reference →
  lean **NO** and write the note.
- A text whose completeness depends on a figure/table not included → **NO**.
- If you are unsure, **NO** is the safer call (protects corpus quality).

---

## The rules

1. **Rate independently.** Do **not** discuss texts with the other rater
   before both have submitted. Independent ratings are what make the
   disagreement rate meaningful.
2. **Both raters rate every text.** A text with only one rating is
   `incomplete` and cannot enter the corpus.
3. **Consensus required.** Both YES → `accept`. Both NO → `reject`.
   Mixed → `disagree` → goes to adjudication (third rater / team decision).
4. **Always add a note when you rate NO** — say what is missing/broken.
   This is what makes disagreements resolvable.
5. **Judge the text as given.** Do not fix it, do not assume content that
   is not there.

---

## How to run it

```bash
# Rater 1 (e.g. alice) — walks the unrated pilot texts, prompts y/n + note
python -m pilot.raters rate --rater alice

# Rater 2 (e.g. bob) — same, independently
python -m pilot.raters rate --rater bob

# See what's left for you
python -m pilot.raters todo --rater bob

# Aggregate: accept / reject / disagree / incomplete + disagreement rate
python -m pilot.raters report
```

Ratings are stored append-only in `pilot_data/ratings.json`. Re-rating the
same text replaces your previous verdict (last write wins per rater).

---

## What the report gives you

- **accept** — both raters said self-contained → enters corpus.
- **reject** — both said not → excluded.
- **disagree** — mixed → **needs adjudication** (listed with each rater's
  verdict + notes).
- **incomplete** — fewer than 2 raters → needs a second rating.
- **disagreement rate** — the initial rate reported per pre-reg §4.2:54.
  A high rate means the criteria are ambiguous → tighten the rubric.

---

## Adjudicating disagreements

For each `disagree` item:
1. Read the text + both notes.
2. A third rater (or the team) makes the final call.
3. Record the final verdict by adding a rating from the adjudicator id —
   majority of 3 decides (2–1 accept/reject; 3-way split stays flagged).

---

## Time budget

~1–2 min per text. 50 pilot texts × 2 raters ≈ 1.5–3 hours total.
Read the whole text before deciding; do not skim.
