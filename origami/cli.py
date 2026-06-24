"""
Origami Engine CLI — runs the full workflow.

  origami icp <url>                          site -> ICP (saved to icp.json)
  origami campaigns                          ICP -> ranked campaigns
  origami new-campaign "<name>" "<angle>"    create a campaign
  origami import <campaign_id> <file.csv>    compliant lead intake
  origami qualify <campaign_id>              AI-classify new leads vs ICP
  origami list <campaign_id> [status]        show the People table
  origami sequence <campaign_id>             draft sequences for qualified
  origami export <campaign_id>               export qualified + suppress
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

from .store import Store
from . import icp as icp_mod, campaigns as camp_mod, ingest as ing_mod
from . import qualify as qual_mod, sequence as seq_mod

DB = os.environ.get("ORIGAMI_DB", "origami.db")
ICP_FILE = pathlib.Path(os.environ.get("ORIGAMI_ICP", "icp.json"))
VALUE_PROP = os.environ.get(
    "ORIGAMI_VALUE_PROP",
    "x402 lets autonomous agents pay per-call for tools — no subscriptions, "
    "no API keys, no human in the loop.")


def _load_icp() -> dict:
    if not ICP_FILE.exists():
        sys.exit("No icp.json yet — run: origami icp <url>")
    return json.loads(ICP_FILE.read_text())


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="origami")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("icp"); a.add_argument("url")
    sub.add_parser("campaigns")
    nc = sub.add_parser("new-campaign"); nc.add_argument("name"); nc.add_argument("angle", nargs="?", default="")
    im = sub.add_parser("import"); im.add_argument("campaign_id", type=int); im.add_argument("file")
    q = sub.add_parser("qualify"); q.add_argument("campaign_id", type=int)
    ls = sub.add_parser("list"); ls.add_argument("campaign_id", type=int); ls.add_argument("status", nargs="?")
    sq = sub.add_parser("sequence"); sq.add_argument("campaign_id", type=int)
    ex = sub.add_parser("export"); ex.add_argument("campaign_id", type=int); ex.add_argument("--out", default="export.csv")

    args = p.parse_args(argv)
    store = Store(DB)

    if args.cmd == "icp":
        icp = icp_mod.build_icp(args.url)
        ICP_FILE.write_text(json.dumps(icp, indent=2))
        print(json.dumps(icp, indent=2))
        print(f"\nsaved -> {ICP_FILE}")

    elif args.cmd == "campaigns":
        recs = camp_mod.recommend(_load_icp())
        print(json.dumps(recs, indent=2))

    elif args.cmd == "new-campaign":
        cid = store.add_campaign(args.name, args.angle)
        print(f"campaign #{cid}: {args.name}")

    elif args.cmd == "import":
        path = args.file
        rows = ing_mod.from_json(path) if path.endswith(".json") else ing_mod.from_csv(path)
        counts = ing_mod.ingest(store, args.campaign_id, rows)
        print(json.dumps(counts, indent=2))

    elif args.cmd == "qualify":
        tally = qual_mod.qualify_campaign(store, args.campaign_id, _load_icp())
        print(json.dumps(tally, indent=2))

    elif args.cmd == "list":
        for r in store.people(args.campaign_id, args.status):
            print(f"[{r['status']:9}] {r['name']} — {r['headline']} "
                  f"({r.get('fit_reason') or ''})")

    elif args.cmd == "sequence":
        camps = {c["id"]: c for c in store.campaigns()}
        camp = camps.get(args.campaign_id, {"name": "campaign", "why": ""})
        for lead in store.people(args.campaign_id, status="qualified"):
            seq = seq_mod.draft_sequence(lead, camp, VALUE_PROP)
            print(f"\n=== {lead['name']} | {seq.get('subject')} ===")
            for s in seq.get("steps", []):
                print(f"\n-- Day {s['day']} --\n{s['body']}")

    elif args.cmd == "export":
        n = seq_mod.export_qualified(store, args.campaign_id, args.out)
        print(f"exported {n} qualified leads -> {args.out} (now suppressed)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
