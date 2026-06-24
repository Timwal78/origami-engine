"""
Step 1 — Site -> ICP.

Scrapes a domain you own (or any public page) and has Claude extract:
what you do, the pain points you solve, your proof points, and a sharp
Ideal Customer Profile. Mirrors Origami's opening move.
"""

from __future__ import annotations

import re
import urllib.request

from .claude import ask_json

SYSTEM = """You are a B2B go-to-market strategist. Read the scraped site content
and produce a precise Ideal Customer Profile. Be specific about WHO feels the
pain and WHY. Use only what the site supports — do not invent claims."""


def scrape(url: str, max_chars: int = 12000) -> str:
    req = urllib.request.Request(url, headers={"user-agent": "origami-engine"})
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", "ignore")
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def build_icp(url: str) -> dict:
    content = scrape(url)
    prompt = f"""Site: {url}

SCRAPED CONTENT:
{content}

Return JSON with keys:
  what_we_do (1 sentence),
  pain_points (array of strings),
  proof_points (array of strings),
  icp (1-2 sentence sharp profile of the buyer),
  buyer_titles (array),
  buying_signals (array of observable signals that someone is in-market)."""
    return ask_json(prompt, SYSTEM, max_tokens=1500)
