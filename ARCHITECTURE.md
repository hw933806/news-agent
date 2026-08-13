# Architecture — Research OS (v3, 2026-08-13)

## Principle
**One folder per company is the brain.** `companies/<TICKER>/` holds everything known about
a name. You drop raw files in `sources/`; agents synthesize them into a single living
`knowledge.md`; `thesis.md` is your view on top. Agents are spokes — each reads the core,
does its job, writes cited knowledge back. The core compounds; agents are replaceable. The
full contract is `CORE.md`.

(v2 was a heavier hub-and-spoke with a per-source `evidence/` archive + `learnings.md` — it
was never used in practice, so v3 collapses synthesis into one `knowledge.md` and gives raw
files a real home in `sources/`. v1 was news-agent-centric with per-stock config under `stocks/`.)

## Layout
```
CORE.md                      # the agent contract — read this first
INGEST.md                    # how a new sources/ file becomes cited knowledge
companies/<TICKER>/          # THE BRAIN, one folder per name
│   ├── sources/             #   raw diligence: memos, models, expert calls, filings.
│   │                        #     LOCAL-ONLY (git-ignored) — the repo is public.
│   ├── knowledge.md         #   single living synthesis (Synthesis + append-only Log),
│   │                        #     every claim cited to a source or a news date
│   ├── thesis.md            #   human-owned live thesis — every agent ranks against it
│   ├── input.md             #   human inbox — folded & cleared by the next agent run
│   └── news/                #   news-spoke config: profile.yaml, sources.yaml,
│                            #     signal.md, state.json (dedupe cache)
engine/                      # news-spoke plumbing (Python = plumbing; Claude = judgment)
│   ├── daily_run.md         #   playbook mirrored by the routine prompt
│   ├── state.py             #   dedupe fingerprints (companies/<T>/news/state.json)
│   └── deliver.py           #   legacy email path (manual/local use only)
macro/macro.yaml             # cross-name EXTERNAL signals (rates, tariffs…) → names moved
                             #   (company-to-company read-throughs cross-post into knowledge.md)
output/                      # daily digest archive (audit trail)
config.yaml                  # enabled tickers, lookback windows
RUNBOOK.md                   # operations: deployment, schedule, failure modes
```

## Spokes
- **news** (live): weekday 8am ET cloud routine. Sweeps each company's universe + macro,
  ranks by thesis relevance (🎯) then signal rules, delivers an in-app digest with push
  notification, folds the inbox, writes cited discoveries to `knowledge.md`. Runs only on
  committed files — it never sees `sources/`.
- **ingest** (local session): whenever a new file lands in `sources/`. Reads it, distills
  thesis-relevant facts into `knowledge.md` (cited), proposes thesis edits, commits only the
  synthesis. See `INGEST.md`.
- **expert-calls** (session-based): the expert-call-synthesis skill runs on a folder of
  transcripts under `sources/`; its outputs get folded into `knowledge.md` + thesis with the
  human in the loop.

## The compounding loop
Raw files (memos, models, calls) → `sources/` → ingest distills → `knowledge.md` +
`thesis.md` → every agent's judgment shifts → agents surface thesis-relevant signal + write
more cited knowledge → richer core → better judgment. The synthesis is all git history:
reviewable, revertible, auditable. The raw files stay local and private.

**Cross-company read-throughs** don't get lost: a claim surfaced for one name that bears on
another is cross-posted (cited) into the other name's `knowledge.md`, so each company's file
is the complete view of what's relevant to it. External macro drivers live in `macro/`.

## To add a company
`cp -r` an existing `companies/<T>` folder, edit `news/` configs, blank `thesis.md` /
`knowledge.md` / `input.md`, empty `sources/` (keep its README), add the ticker to
`config.yaml`, push. Zero engine changes. Web-verify time-sensitive facts when building
`news/profile.yaml` — training-data staleness is the main defect.

## To add an agent (spoke)
Follow `CORE.md`: read thesis then knowledge first, write cited knowledge back, propose
rather than impose, surgical edits with a changelog, never commit `sources/`, commit + push.
Keep spoke-private config in `companies/<T>/<spoke>/`.
