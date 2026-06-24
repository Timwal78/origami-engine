"""
LLM backend — wraps Anthropic Claude.
Reads ANTHROPIC_API_KEY from environment.
Swap out `_call_anthropic` if you want OpenAI-compat later.
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error

MODEL   = "claude-sonnet-4-6"
API_URL = "https://api.anthropic.com/v1/messages"


def complete(prompt: str, system: str = "", max_tokens: int = 1500,
             json_mode: bool = False) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    body = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system

    data = json.dumps(body).encode()
    req  = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "x-api-key":         key,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Anthropic API error {e.code}: {e.read().decode()}") from e

    return resp["content"][0]["text"]
