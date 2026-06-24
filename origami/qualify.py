"""
Step 4 — AI qualification.

For each lead, Claude classifies fit against the ICP: qualified / unsure /
rejected, with a one-line reason — the same enrich-and-classify pass Origami
runs. Strict rule: judge ONLY on the real fields present. If data is thin,
return "unsure" rather than inventing a reason to qualify.
"""

from __future__ import annotations

import json

from .claude import ask_json
from .store import Store

SYSTEM = """You qualify B2B leads against an Ideal Customer Profile.
Use ONLY the real fields provided (name, headline, role, company). Never
invent employment, seniority, or intent. If the data is insufficient to
judge, return "unsure". Output strict labels."""


def classify(icp: dict, person: dict) -> dict:
    prompt = f"""ICP:
{json.dumps(icp, indent=2)}

LEAD (real data only):
  name: {person.get('name')}
  headline: {person.get('headline')}
  role: {person.get('role')}
  company: {person.get('company')}

Return JSON: {{"fit": "qualified|unsure|rejected", "reason": "<=15 words"}}"""
    return ask_json(prompt, SYSTEM, max_tokens=300)


def qualify_campaign(store: Store, campaign_id: int, icp: dict) -> dict:
    """Classify every 'new' lead in a campaign. Returns tallies."""
    tally = {"qualified": 0, "unsure": 0, "rejected": 0}
    for p in store.people(campaign_id, status="new"):
        res = classify(icp, p)
        fit = res.get("fit", "unsure")
        if fit not in tally:
            fit = "unsure"
        store.set_fit(p["id"], fit, res.get("reason", ""))
        tally[fit] += 1
    return tally
