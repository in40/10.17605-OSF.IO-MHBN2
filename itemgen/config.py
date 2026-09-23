"""Configuration for item generation + scoring."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ItemGenConfig:
    base_url: str = "https://chat.sorokinonline.com/v1"
    api_key: str = ""
    model: str = "qwen3.5-122b"
    seed: int = 42
    temperature: float = 0.3
    max_tokens: int = 4096
    retries: int = 2
    no_think: bool = True
    # per-text item counts (pre-reg defaults)
    n_qa: int = 10
    n_mcq: int = 8
    n_nli: int = 6
    n_stance: int = 4
    # dirs
    texts_dir: str = "smoke/texts"
    items_dir: str = "smoke/items"
    summaries_dir: str = "smoke/summaries"
    extra: dict = field(default_factory=dict)

    def chat_extra(self) -> dict:
        extra = dict(self.extra or {})
        if self.no_think:
            ctk = dict(extra.get("chat_template_kwargs", {}))
            ctk["enable_thinking"] = False
            extra["chat_template_kwargs"] = ctk
        return extra
