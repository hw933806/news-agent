# Architecture — Research OS (v2, 2026-07-13)

## Principle
**Hub-and-spoke.** The core knowledge layer (`companies/<TICKER>/` — thesis, inbox,
learnings, evidence) is the center of gravity. Agents are spokes: each reads the core
for context, does its specialized job, and writes what it learned back into the core.
The core compounds; agents are replaceable. The full contract lives in `CORE.md`.

(v1 was news-agent-centric with per-stock config under `stocks/`. Inverted 2026-07-13.)

## Layout
```
CORE.md                      # the hub-and-spoke contract — read this first
companies/<TICKER>/          # THE CORE (hub), one folder per name
│   ├── thesis.md            #   human-owned live thesis — every agent ranks against it
│   ├── input.md             #   human inbox — folded & cleared by the next agent run
│   ├── learnings.md         #   append-only agent discoveries + proposals (attributed)
│   ├── evidence/            #   dated distilled notes from any agent/source
│   └── news/                #   news-spoke config: profile.yaml, sources.yaml,
│                            #     signal.md, state.json (dedupe cache)
engine/                      # news-spoke plumbing (Python = plumbing; Claude = judgment)
│   ├── daily_run.md         #   playbook mirrored by the routine prompt
│   ├── state.py             #   dedupe fingerprints (companies/<T>/news/state.json)
│   └── deliver.py           #   legacy email path (manual/local use only)
macro/macro.yaml             # shared macro signals mapped to the names they move
output/                      # daily digest archive (audit trail)
config.yaml                  # enabled tickers, lookback windows
RUNBOOK.md                   # operations: deployment, schedule, failure modes
```

## Spokes
- **news** (live): weekday 8am ET cloud routine. Sweeps each company's universe +
  macro, ranks by thesis relevance (🎯) then signal rules, delivers an in-app digest
  with push notification, folds the inbox, appends learnings, pushes state back.
- **transcripts** (planned): per earnings call/filing — distill vs. the thesis into
  `evidence/`, flag pillar-relevant surprises.
- **expert-calls** (session-based): the expert-call-synthesis skill's outputs get
  distilled into `evidence/` + thesis updates with the human in the loop.

## The compounding loop
Human work (memos, models, calls) → thesis.md / input.md → every agent's judgment
shifts → agents surface thesis-relevant signal + write evidence/learnings → richer
core → better judgment. All of it is git history: reviewable, revertible, auditable.

## To add a company
`cp -r` an existing `companies/<T>` folder, edit `news/` configs + blank the core files,
add the ticker to `config.yaml`, push. Zero engine changes. Web-verify time-sensitive
facts when building `news/profile.yaml` — training-data staleness is the main defect.

## To add an agent (spoke)
Follow `CORE.md`: read thesis first, write evidence/learnings back, propose rather than
impose, surgical edits with a changelog, commit+push. Keep spoke-private config in
`companies/<T>/<spoke>/`.
