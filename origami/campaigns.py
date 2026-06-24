"""
Step 2 — ICP -> ranked campaigns.

Given the ICP, Claude recommends the highest-value engagement campaigns,
best-first, each with the reason it'll land — exactly like Origami's
"What I'd run, best first" table.
"""

from __future__ import annotations

import json

from .claude import ask_json

SYSTEM = """You are a B2B outbound strategist. Recommend engagement-based
campaigns ranked by expected conversion. Each campaign targets a specific,
observable audience behavior (e.g. people engaging with a topic, companies
hiring for a role). Be concrete and honest about why each will land."""


def recommend(icp: dict, n: int = 5) -> list[dict]:
    prompt = f"""ICP and context:
{json.dumps(icp, indent=2)}

Return JSON array of {n} campaigns, best first. Each object:
  rank (int),
  name (the targeting angle, specific),
  audience (who exactly),
  why (one sentence: why this audience is in-market),
  signal (the observable behavior that qualifies someone for this campaign)."""
    return ask_json(prompt, SYSTEM, max_tokens=1800)
