"""Shared LLM helper — now provider-agnostic via llm.complete()."""

from __future__ import annotations

import json

from .llm import complete


def ask(prompt: str, system: str = "", max_tokens: int = 1500) -> str:
    return complete(prompt, system, max_tokens)


def ask_json(prompt: str, system: str = "", max_tokens: int = 1500):
    """Ask and parse JSON, stripping any code fences. Works on every provider;
    json_mode is requested on OpenAI-compatible backends for reliability."""
    raw = complete(prompt,
                   system + "\nReturn ONLY valid JSON, no prose, no fences.",
                   max_tokens, json_mode=True)
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)
