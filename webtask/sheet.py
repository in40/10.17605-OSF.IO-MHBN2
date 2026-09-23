"""Web-UI summarization task sheets: export prompts for manual run, import results.

For models with no API (Alisa, GigaChat), a human copies each self-contained
prompt into the web UI and pastes the model's answer back into the sheet.
The importer writes the answers into the SAME summary layout the API path uses
(`<out>/<system>/<text_id>/<level>/summary_0.txt`), so judge + QA score them
identically.
"""
from __future__ import annotations

TASK_PREFIX = "===TASK "
PROMPT_START = "---PROMPT---"
PROMPT_END = "---ENDPROMPT---"
RESP_START = "---RESPONSE---"
RESP_END = "---ENDRESPONSE---"

HEADER = (
    "# Web-UI Summarization Tasks — {system}\n"
    "#\n"
    "# For each TASK block:\n"
    "#   1. Copy everything between {ps} and {pe} into the {system} web UI.\n"
    "#   2. Paste the model's summary between {rs} and {re}.\n"
    "# Leave RESPONSE empty to skip a task. Do NOT edit the ===TASK=== line.\n"
)


def render_header(system: str) -> str:
    return HEADER.format(
        system=system, ps=PROMPT_START, pe=PROMPT_END, rs=RESP_START, re=RESP_END
    )


def format_task(text_id: str, level_tag: str, target: int, prompt: str) -> str:
    return (
        f"{TASK_PREFIX}{text_id} {level_tag} {target}===\n"
        f"{PROMPT_START}\n{prompt}\n{PROMPT_END}\n"
        f"{RESP_START}\n\n{RESP_END}\n"
    )


def parse_sheet(text: str) -> list[dict]:
    """Parse a (possibly human-filled) worksheet into task dicts."""
    tasks: list[dict] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(TASK_PREFIX):
            parts = line[len(TASK_PREFIX):].replace("===", "").split()
            text_id, level, target = parts[0], parts[1], int(parts[2])
            prompt, i = _collect_block(lines, i, PROMPT_START, PROMPT_END)
            response, i = _collect_block(lines, i, RESP_START, RESP_END)
            tasks.append(
                {
                    "text_id": text_id,
                    "level": level,
                    "target": target,
                    "prompt": prompt,
                    "response": response,
                }
            )
        else:
            i += 1
    return tasks


def _collect_block(lines: list[str], start: int, marker: str, end: str) -> tuple[str, int]:
    # advance to the marker line
    j = start
    while j < len(lines) and lines[j].strip() != marker:
        j += 1
    j += 1  # past the marker
    body: list[str] = []
    while j < len(lines) and lines[j].strip() != end:
        body.append(lines[j])
        j += 1
    return "\n".join(body).strip(), j + 1
