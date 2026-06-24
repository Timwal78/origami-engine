"""
Step 3 — Lead intake (the compliant ingestion layer).

This is the deliberate boundary: instead of bot-scraping LinkedIn behind its
login (ToS ban + GDPR/CAN-SPAM exposure), you feed leads from sources you
legitimately have — a Sales Navigator CSV export, a data-provider API pull,
or any structured list. The engine then dedupes, applies the exclusion map,
and fans rows into the People table.

Column mapping is flexible so any export drops in.
"""

from __future__ import annotations

import csv
import json
import pathlib
from typing import Iterable

from .store import Store, ident_for

# common header aliases -> canonical field
ALIASES = {
    "name": {"name", "full name", "fullname", "full_name", "contact"},
    "headline": {"headline", "title", "summary", "bio"},
    "role": {"role", "job title", "position", "job_title"},
    "company": {"company", "organization", "org", "company name"},
    "email": {"email", "email address", "work email", "e-mail"},
    "source_post": {"source", "post", "source_post", "post url", "origin"},
}


def _canon(header: str) -> str | None:
    h = header.strip().lower()
    for field, names in ALIASES.items():
        if h in names:
            return field
    return None


def _map_row(row: dict) -> dict:
    out: dict[str, str] = {}
    for k, v in row.items():
        c = _canon(k)
        if c and v:
            out[c] = v.strip()
    return out


def from_csv(path: str | pathlib.Path) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for raw in csv.DictReader(f):
            mapped = _map_row(raw)
            if mapped.get("name") or mapped.get("email"):
                rows.append(mapped)
    return rows


def from_json(path: str | pathlib.Path) -> list[dict]:
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return [r for r in data if r.get("name") or r.get("email")]


def ingest(store: Store, campaign_id: int, rows: Iterable[dict]) -> dict:
    """Insert rows -> People table. Returns counts by outcome."""
    counts = {"new": 0, "duplicate": 0, "excluded": 0}
    for r in rows:
        r["ident"] = ident_for(r.get("email", ""), r.get("source_post", ""))
        status = store.add_person(campaign_id, r)
        counts[status] = counts.get(status, 0) + 1
    return counts


def from_csv_str(raw: str) -> list[dict]:
    """Parse CSV from a raw string (for webhook use)."""
    import io
    rows = []
    for r in csv.DictReader(io.StringIO(raw)):
        mapped = _map_row(r)
        if mapped.get("name") or mapped.get("email"):
            rows.append(mapped)
    return rows


def from_json_str(raw: str) -> list[dict]:
    """Parse JSON from a raw string (for webhook use)."""
    import json
    data = json.loads(raw)
    return data if isinstance(data, list) else [data]
