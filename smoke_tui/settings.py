"""Persistent settings for the TUI, mapped to each stage's CLI args."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SETTINGS_PATH = Path(__file__).resolve().parent.parent / "smoke_tui_settings.json"

DEFAULT_SUMMARIZER: dict[str, Any] = {
    "type": "llm",
    "base_url": "https://chat.sorokinonline.com/v1",
    "api_key_env": "SC_KEY",
    "model": "qwen3.5-122b",
    "system": "qwen3.5-122b",
    "levels": "0.9 0.7 0.5 0.3 0.2 0.1 0.05",
    "n": 1,
    "temperature": 0.3,
    "max_tokens": 2048,
    "top_p": "",
    "seed": 42,
    "tolerance": 0.20,
    "regen": 1,
    "no_think": True,
    "hybrid_model": "IlyaGusev/rut5_base_sum_gazeta",
    "hybrid_backend": "transformers",
    "extractive_scale": 2.0,
    "texts_dir": "smoke/texts",
    "out_dir": "smoke/summaries",
}

DEFAULT_JUDGE: dict[str, Any] = {
    "base_url": "https://chat.sorokinonline.com/v1",
    "api_key_env": "SC_KEY",
    "model": "qwen3.5-122b",
    "mode": "combined",
    "temperature": 0.0,
    "top_p": 0.95,
    "max_tokens": 256,
    "seed": 42,
    "retries": 1,
    "think": False,
    "summaries_dir": "smoke/summaries",
    "texts_dir": "smoke/texts",
}

DEFAULTS: dict[str, Any] = {
    "collector": {"all": True},
    "summarizers": [dict(DEFAULT_SUMMARIZER)],
    "judge": dict(DEFAULT_JUDGE),
}


def load() -> dict[str, Any]:
    settings: dict[str, Any] = {
        "collector": dict(DEFAULTS["collector"]),
        "summarizers": [dict(DEFAULT_SUMMARIZER)],
        "judge": dict(DEFAULT_JUDGE),
    }
    if SETTINGS_PATH.exists():
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return settings
        # migrate legacy single "summarizer" -> "summarizers" list
        if "summarizer" in data and "summarizers" not in data:
            data["summarizers"] = [data.pop("summarizer")]
        if "collector" in data:
            settings["collector"].update(data["collector"])
        if "judge" in data:
            settings["judge"].update(data["judge"])
        if isinstance(data.get("summarizers"), list) and data["summarizers"]:
            settings["summarizers"] = [
                {**DEFAULT_SUMMARIZER, **s} for s in data["summarizers"]
            ]
    return settings


def save(settings: dict[str, Any]) -> None:
    SETTINGS_PATH.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")


def summarizer_args(s: dict[str, Any]) -> list[str]:
    stype = s.get("type", "llm")
    args = [
        "--type", stype,
        "--system", str(s["system"]),
        "--levels", *[x for x in str(s["levels"]).split() if x],
        "--n", str(s["n"]),
        "--tolerance", str(s["tolerance"]),
        "--regen", str(s["regen"]),
        "--texts-dir", str(s["texts_dir"]),
        "--out-dir", str(s["out_dir"]),
    ]
    if stype == "llm":
        args += [
            "--base-url", str(s["base_url"]),
            "--api-key-env", str(s["api_key_env"]),
            "--model", str(s["model"]),
            "--temperature", str(s["temperature"]),
            "--max-tokens", str(s["max_tokens"]),
            "--seed", str(s["seed"]),
        ]
        if s.get("top_p") not in ("", None):
            args += ["--top-p", str(s["top_p"])]
        if s.get("no_think"):
            args.append("--no-think")
    if stype == "hybrid":
        args += [
            "--hybrid-model", str(s.get("hybrid_model", "IlyaGusev/rut5_base_sum_gazeta")),
            "--hybrid-backend", str(s.get("hybrid_backend", "transformers")),
            "--extractive-scale", str(s.get("extractive_scale", 2.0)),
        ]
    return args


def judge_args(s: dict[str, Any]) -> list[str]:
    args = [
        "--base-url", str(s["base_url"]),
        "--api-key-env", str(s["api_key_env"]),
        "--model", str(s["model"]),
        "--mode", str(s["mode"]),
        "--temperature", str(s["temperature"]),
        "--top-p", str(s["top_p"]),
        "--max-tokens", str(s["max_tokens"]),
        "--seed", str(s["seed"]),
        "--retries", str(s["retries"]),
        "--summaries-dir", str(s["summaries_dir"]),
        "--texts-dir", str(s["texts_dir"]),
    ]
    if s.get("think"):
        args.append("--think")
    return args


def pilot_summarizer_args(s: dict[str, Any], texts_dir: str, out_dir: str) -> list[str]:
    s2 = dict(s)
    s2["texts_dir"] = str(texts_dir)
    s2["out_dir"] = str(out_dir)
    return summarizer_args(s2)


def pilot_judge_args(s: dict[str, Any], summaries_dir: str, texts_dir: str) -> list[str]:
    s2 = dict(s)
    s2["summaries_dir"] = str(summaries_dir)
    s2["texts_dir"] = str(texts_dir)
    return judge_args(s2)
