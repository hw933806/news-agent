# News Agent — Architecture (DRAFT v1)

## Principle
**Stock-agnostic engine + per-stock profile.** Adding a stock = drop a new folder under
`stocks/`. The engine never changes. No rewriting to scale.

## Layout
```
News Agent/
├── config.yaml              # global: email recipient, schedule, enabled stocks
├── engine/                  # shared, stock-agnostic — written ONCE
│   ├── daily_run.md         #   PLAYBOOK: the prompt the scheduled Claude agent follows
│   ├── deliver.py           #   send email via Gmail SMTP (stdlib only)
│   └── state.py             #   dedupe: fingerprint + track already-seen items per stock
#
# Reasoning (fetch via WebSearch/WebFetch, judge signal, rank, compose) is done by
# Claude during the scheduled run — NOT by Python. Python = plumbing only.
├── macro/
│   └── macro.yaml           # shared macro signals + which stocks each moves
├── stocks/                  # THE MODULAR PART — one folder per stock
│   ├── FERG/
│   │   ├── profile.yaml     #   universe: self, competitors, partners, suppliers, read-throughs
│   │   ├── sources.yaml     #   ranked sources (IR, trade press, regulators…)
│   │   ├── signal.md        #   what counts as high vs low signal for THIS name
│   │   └── state.json       #   seen-news cache (auto-managed) → enables "nothing new = nothing sent"
│   ├── RKT/  … (same files)
│   ├── AUR/  …
│   ├── WRBY/ …
│   └── CPNG/ …
└── output/                  # archive of each day's email (audit trail)
```

## How a daily run works
1. `run.py` reads `config.yaml` → list of enabled stocks.
2. For each stock: load `profile.yaml` + `sources.yaml`, fetch last 24h news across its universe.
3. Pull relevant `macro/` signals (only those mapped to that stock).
4. `dedupe.py` drops anything already in `state.json`.
5. `rank.py` scores each item by signal using `signal.md` rules.
6. `compose.py` merges all stocks into ONE 1-page email, highest→lowest signal.
7. `deliver.py` sends at 9am ET. Empty sections are omitted entirely.

## To add a 6th stock later
`cp -r stocks/FERG stocks/NEWTICKER`, edit the 3 yaml/md files, add ticker to `config.yaml`.
Done — zero engine changes.

## Decisions (LOCKED)
1. **Profile format:** YAML config per stock (no code to add a stock).
2. **Email layout:** Grouped by stock; items ranked highest→lowest signal within each block.
   Stocks with no news omitted entirely.
3. **Language/runtime:** Python.

## Plumbing (LOCKED)
- **Delivery:** Gmail SMTP + App Password (credential kept local, out of repo).
- **Runtime:** Remote scheduled agent (cron), fires 9am ET regardless of laptop state.
- **Recipient:** hw933806@gmail.com

## Still open
- **Source curation** — fold in the feeds/analysts you already read before locking profiles.
