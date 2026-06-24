"""
Webhook server — accepts CSV/JSON drops and triggers the pipeline.

POST /import?campaign_id=1   multipart CSV  → ingest + qualify + (optional) export
GET  /health                                 → {"status":"ok"}
GET  /status?campaign_id=1                   → People table counts by status

Run locally:
  ANTHROPIC_API_KEY=... python -m origami.webhook

On Render: add a Web Service pointing to this, same repo, same disk as the cron.
"""
from __future__ import annotations

import io
import json
import os
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from .store import Store
from . import ingest as ing_mod, qualify as qual_mod, sequence as seq_mod

DB      = os.environ.get("ORIGAMI_DB", "origami.db")
ICP_FILE = os.environ.get("ORIGAMI_ICP", "icp.json")
PORT    = int(os.environ.get("PORT", 8080))


def _load_icp() -> dict:
    import pathlib, sys
    p = pathlib.Path(ICP_FILE)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _counts(store: Store, campaign_id: int) -> dict:
    rows = store.people(campaign_id)
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    return counts


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(fmt % args)

    def _json(self, code: int, body: dict):
        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path == "/health":
            self._json(200, {"status": "ok"})

        elif parsed.path == "/status":
            cid = int(qs.get("campaign_id", ["1"])[0])
            store = Store(DB)
            self._json(200, {"campaign_id": cid, "counts": _counts(store, cid)})

        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path != "/import":
            self._json(404, {"error": "not found"})
            return

        try:
            cid        = int(qs.get("campaign_id", ["1"])[0])
            auto_qual  = qs.get("qualify",  ["1"])[0] == "1"
            auto_export= qs.get("export",   ["0"])[0] == "1"
            length     = int(self.headers.get("Content-Length", 0))
            raw        = self.rfile.read(length).decode("utf-8")

            # accept JSON body or CSV body
            if self.headers.get("Content-Type", "").startswith("application/json"):
                rows = ing_mod.from_json_str(raw)
            else:
                rows = ing_mod.from_csv_str(raw)

            store  = Store(DB)
            counts = ing_mod.ingest(store, cid, rows)
            result = {"imported": counts}

            if auto_qual:
                icp   = _load_icp()
                tally = qual_mod.qualify_campaign(store, cid, icp)
                result["qualified"] = tally

            if auto_export:
                n = seq_mod.export_qualified(store, cid, f"export_campaign_{cid}.csv")
                result["exported"] = n

            self._json(200, result)

        except Exception:
            self._json(500, {"error": traceback.format_exc()})


def run():
    print(f"Origami webhook listening on :{PORT}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    run()
