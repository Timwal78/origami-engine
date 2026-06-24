# Origami Engine — Script Master Labs edition

An AI outbound flywheel you own outright. Mirrors the Origami workflow:

```
  site -> ICP -> campaigns -> intake -> qualify -> sequence -> export
                                                        ^            |
                                                        +-- exclusion map
```

| Step | Module | What it does |
|------|--------|--------------|
| 1 | `icp.py` | Scrapes your domain, Claude extracts what you do, pains, proof, and a sharp ICP |
| 2 | `campaigns.py` | ICP → ranked campaigns, best-first, each with why it lands |
| 3 | `ingest.py` | **Compliant** lead intake (CSV / JSON), flexible column mapping, dedupe |
| 4 | `qualify.py` | Claude classifies each lead vs ICP: qualified / unsure / rejected + reason |
| 5 | `sequence.py` | Personalized 3-step sequences with CAN-SPAM footer; export + suppress |

`store.py` is the SQLite Posts + People tables and the global **exclusion map**
— exported/contacted leads are permanently suppressed, so nobody is contacted
twice even across re-imports.

## The one deliberate design choice

Origami auto-scrapes LinkedIn reactions/comments to harvest people. This clone
**does not** — that scraping is what creates the liability (LinkedIn ToS bans,
plus GDPR/CAN-SPAM exposure on harvested personal data), and it's not where the
value is. Instead you feed leads from sources you legitimately hold:

- a **Sales Navigator CSV export** you ran yourself, or
- a **data-provider API pull** (Apollo, Clay, etc.), or
- any structured list.

The engine's value — ICP, AI qualification, sequencing, suppression — runs the
same on legitimately-sourced leads. And the CAN-SPAM footer means the outreach
itself *reduces* your liability instead of adding it.

## Setup

```bash
cp .env.example .env     # add ANTHROPIC_API_KEY + sender identity
# no pip install needed — pure standard library
```

## Run

```bash
origami icp https://www.scriptmasterlabs.com         # -> icp.json
origami campaigns                                     # ranked campaigns
origami new-campaign "C2 - Agent Payments" "subscription waste -> agent commerce"
origami import 1 sales_nav_export.csv                 # compliant intake
origami qualify 1                                     # AI fit vs ICP
origami list 1 qualified                              # review the People table
origami sequence 1                                    # draft personalized sequences
origami export 1                                      # export qualified + suppress
```

(Invoke as `python -m origami.cli ...` if not installed on PATH.)

## Notes
- Strict truth rule throughout: the qualifier and writer use only real lead
  fields — no invented employment, seniority, intent, or metrics.
- `import` accepts `.csv` or `.json`. Column aliases (Name/Title/Company/Email/
  Source and common variants) map automatically.
- Re-running `import` after `export` is safe: suppressed leads come back as
  `excluded`, never re-added.
