"""
Persistent store for the Origami engine.

Mirrors the workspace structure: a Posts table and a People table per
campaign, plus a global exclusion/suppression list so you never re-contact
someone already in the pipeline.

SQLite — single file, zero infra, runs anywhere (including a Render disk).
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import pathlib
import sqlite3
from typing import Any, Iterable

SCHEMA = """
CREATE TABLE IF NOT EXISTS campaigns (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  angle TEXT,
  status TEXT DEFAULT 'active',
  created TEXT
);
CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY,
  campaign_id INTEGER,
  author TEXT,
  headline TEXT,
  url TEXT UNIQUE,
  reactions INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  note TEXT,
  FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
);
CREATE TABLE IF NOT EXISTS people (
  id INTEGER PRIMARY KEY,
  campaign_id INTEGER,
  ident TEXT,                       -- dedupe key (email or profile url)
  name TEXT,
  headline TEXT,
  role TEXT,
  company TEXT,
  email TEXT,
  source_post TEXT,
  status TEXT DEFAULT 'new',        -- new|qualified|unsure|rejected|excluded
  fit_reason TEXT,
  created TEXT,
  UNIQUE(campaign_id, ident),
  FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
);
CREATE TABLE IF NOT EXISTS exclusions (
  ident TEXT PRIMARY KEY,           -- suppressed forever (contacted/optout)
  reason TEXT,
  created TEXT
);
"""


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def ident_for(email: str = "", profile_url: str = "") -> str:
    raw = (email or profile_url).strip().lower()
    return hashlib.sha256(raw.encode()).hexdigest()[:16] if raw else ""


class Store:
    def __init__(self, path: str | pathlib.Path = "origami.db"):
        self.db = sqlite3.connect(str(path))
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.db.commit()

    # campaigns ---------------------------------------------------------
    def add_campaign(self, name: str, angle: str = "") -> int:
        cur = self.db.execute(
            "INSERT INTO campaigns(name,angle,created) VALUES(?,?,?)",
            (name, angle, _now()),
        )
        self.db.commit()
        return cur.lastrowid

    def campaigns(self) -> list[dict]:
        return [dict(r) for r in self.db.execute("SELECT * FROM campaigns")]

    # posts -------------------------------------------------------------
    def add_post(self, campaign_id: int, **f) -> int:
        cur = self.db.execute(
            "INSERT OR IGNORE INTO posts"
            "(campaign_id,author,headline,url,reactions,comments,note)"
            " VALUES(?,?,?,?,?,?,?)",
            (campaign_id, f.get("author"), f.get("headline"), f.get("url"),
             f.get("reactions", 0), f.get("comments", 0), f.get("note")),
        )
        self.db.commit()
        return cur.lastrowid

    def posts(self, campaign_id: int) -> list[dict]:
        return [dict(r) for r in self.db.execute(
            "SELECT * FROM posts WHERE campaign_id=? ORDER BY reactions DESC",
            (campaign_id,))]

    # people ------------------------------------------------------------
    def is_excluded(self, ident: str) -> bool:
        if not ident:
            return False
        return self.db.execute(
            "SELECT 1 FROM exclusions WHERE ident=?", (ident,)
        ).fetchone() is not None

    def add_person(self, campaign_id: int, person: dict) -> str:
        """Insert a lead unless excluded or duplicate. Returns status."""
        ident = person.get("ident") or ident_for(
            person.get("email", ""), person.get("source_post", ""))
        if not ident:
            ident = ident_for(profile_url=person.get("name", "") + person.get("company", ""))
        if self.is_excluded(ident):
            return "excluded"
        try:
            self.db.execute(
                "INSERT INTO people(campaign_id,ident,name,headline,role,"
                "company,email,source_post,status,created)"
                " VALUES(?,?,?,?,?,?,?,?,?,?)",
                (campaign_id, ident, person.get("name"), person.get("headline"),
                 person.get("role"), person.get("company"), person.get("email"),
                 person.get("source_post"), "new", _now()),
            )
            self.db.commit()
            return "new"
        except sqlite3.IntegrityError:
            return "duplicate"

    def people(self, campaign_id: int, status: str | None = None) -> list[dict]:
        q = "SELECT * FROM people WHERE campaign_id=?"
        args: list[Any] = [campaign_id]
        if status:
            q += " AND status=?"
            args.append(status)
        return [dict(r) for r in self.db.execute(q, args)]

    def set_fit(self, person_id: int, status: str, reason: str) -> None:
        self.db.execute(
            "UPDATE people SET status=?,fit_reason=? WHERE id=?",
            (status, reason, person_id))
        self.db.commit()

    # exclusions --------------------------------------------------------
    def exclude(self, idents: Iterable[str], reason: str = "contacted") -> int:
        n = 0
        for i in idents:
            if not i:
                continue
            self.db.execute(
                "INSERT OR IGNORE INTO exclusions(ident,reason,created)"
                " VALUES(?,?,?)", (i, reason, _now()))
            n += 1
        self.db.commit()
        return n
