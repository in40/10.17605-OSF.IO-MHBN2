"""OpenAI-compatible chat client with retry + exponential backoff."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import requests

log = logging.getLogger(__name__)


@dataclass
class ChatResult:
    content: str
    reasoning: str
    finish_reason: str
    usage: dict
    raw: dict


class LLMClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: int = 120,
        retries: int = 3,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.retries = retries

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        top_p: float | None = None,
        seed: int | None = None,
        extra: dict | None = None,
    ) -> ChatResult:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if top_p is not None:
            payload["top_p"] = top_p
        if seed is not None:
            payload["seed"] = seed
        if extra:
            payload.update(extra)

        last_exc: Exception | None = None
        for attempt in range(self.retries):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
                if resp.status_code >= 500 or resp.status_code == 429:
                    raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:120]}")
                resp.raise_for_status()
                data = resp.json()
                choice = data["choices"][0]
                msg = choice.get("message", {})
                return ChatResult(
                    content=(msg.get("content") or "").strip(),
                    reasoning=(msg.get("reasoning_content") or "").strip(),
                    finish_reason=choice.get("finish_reason", ""),
                    usage=data.get("usage", {}),
                    raw=data,
                )
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                delay = 2 ** attempt
                log.warning("chat attempt %d failed: %s (retry in %ds)", attempt + 1, exc, delay)
                time.sleep(delay)
        raise RuntimeError(f"chat failed after {self.retries} retries") from last_exc
