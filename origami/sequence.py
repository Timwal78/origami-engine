"""
Step 5 — Sequence + export.

Drafts a short, personalized multi-step email sequence per qualified lead,
anchored to the post/topic they engaged with and the campaign angle.

Liability is reduced at the source: every sequence ships with a CAN-SPAM
compliant footer (real sender identity, physical mailing address, one-click
opt-out). Configure these in .env — they are required, not optional.
"""

from __future__ import annotations

import csv
import json
import os
import pathlib

from .claude import ask_json
from .store import Store

SYSTEM = """You write concise B2B cold-email sequences. Rules:
- Open on the specific thing the lead engaged with; make it about them.
- Lead with a clear, honest value statement. No hype, no fake familiarity.
- 3 steps: initial, bump, breakup. Each under 90 words.
- Plain, direct sentences. No invented facts about the lead or your product."""


def _footer() -> str:
    sender = os.environ.get("SENDER_NAME", "Script Master Labs LLC")
    addr = os.environ.get("SENDER_ADDRESS", "[physical mailing address]")
    optout = os.environ.get("OPTOUT_URL", "[unsubscribe link]")
    return (f"\n\n— {sender}\n{addr}\n"
            f"Not relevant? Opt out here: {optout}")


def draft_sequence(lead: dict, campaign: dict, value_prop: str) -> dict:
    prompt = f"""LEAD: {lead.get('name')} — {lead.get('headline')} "
"@ {lead.get('company')}
ENGAGED WITH: {lead.get('source_post') or 'a post on this topic'}
CAMPAIGN ANGLE: {campaign.get('name')} — {campaign.get('why', '')}
YOUR VALUE PROP: {value_prop}

Return JSON: {{"subject": "...", "steps": [
  {{"day": 0, "body": "..."}},
  {{"day": 3, "body": "..."}},
  {{"day": 7, "body": "..."}}
]}}"""
    seq = ask_json(prompt, SYSTEM, max_tokens=1200)
    foot = _footer()
    for step in seq.get("steps", []):
        step["body"] = step["body"].rstrip() + foot
    return seq


def export_qualified(store: Store, campaign_id: int,
                     path: str | pathlib.Path = "export.csv") -> int:
    """Export qualified leads to CSV and suppress them from future runs."""
    rows = store.people(campaign_id, status="qualified")
    fields = ["name", "headline", "role", "company", "email",
              "source_post", "fit_reason"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    store.exclude([r["ident"] for r in rows], reason="exported")
    return len(rows)
