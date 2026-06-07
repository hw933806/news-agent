# News Agent — Operations Runbook

How this system is deployed and run in production. (Design lives in `ARCHITECTURE.md`;
the daily agent's instructions live in `engine/daily_run.md`.)

_Last updated: 2026-06-07._

## What it does
Every weekday at **9:00am ET**, a remote Claude agent gathers the last 24h of news across
each enabled stock's universe + mapped macro signals, judges signal, dedupes against what
was already sent, and emails a one-page digest to **hw933806@gmail.com**. A short or empty
email is a success — noise is the enemy.

## Deployment (the moving parts)

| Piece | Where | Notes |
|---|---|---|
| Code + config | GitHub: **hw933806/news-agent** (private) | Cloud agent clones this each run. |
| Schedule | claude.ai routine **`trig_01BBa7EH3oW4Cq8xbD6nFg3D`** | Manage: https://claude.ai/code/routines/trig_01BBa7EH3oW4Cq8xbD6nFg3D |
| Cron | `0 13 * * 1-5` (UTC) | = 9am ET **during EDT**. See DST note below. |
| Model | Opus 4.8 | Judgment-heavy task. |
| Runtime | Anthropic cloud (CCR) | Ephemeral sandbox — nothing local persists; state is pushed back to the repo. |

### Secrets (two of them, both stored in the cloud routine config)
There is **no secure secret channel** for routines, so both secrets live in the routine
config at the URL above. Accepted tradeoff. Both are revocable.
1. **Gmail App Password** — pasted into the routine *prompt* (step 7), replacing the
   `__REPLACE_…__` placeholder. Generate at https://myaccount.google.com/apppasswords.
   Never commit it to the repo.
2. **GitHub fine-grained PAT** — embedded in the clone URL in the routine's `sources`
   (`https://x-access-token:<PAT>@github.com/...`). Scope: `news-agent` only, Contents
   read/write (read = clone, write = push state back). Manage/rotate at
   https://github.com/settings/personal-access-tokens.

> **Why a PAT and not the claude.ai GitHub link?** The web-chat GitHub OAuth connection does
> **not** carry over to scheduled cloud agents (confirmed 2026-06-07: it still returned
> `github_repo_access_denied`). A token is also required regardless, because the daily
> state push-back needs write auth. The `authorization_token` field is rejected by the API;
> embedding the token in the clone URL is what works.

### DST caveat
Cron is fixed in **UTC**. `0 13` = 9am ET only while New York is on EDT (Mar–Nov). When
clocks fall back (early Nov), update the routine to `0 14 * * 1-5` to stay at 9am ET.

## Daily flow (what the agent does)
See `engine/daily_run.md` for the authoritative steps. In short: read config → for each
enabled ticker, fetch 24h news across its universe + macro → `state.py filter` (dedupe) →
judge with `signal.md` → compose → save to `output/<date>.md` → send via `deliver.py` →
`state.py mark` → **commit + push `state.json` + `output/`** so tomorrow remembers.

## Operations

**Run it now (test):** trigger the routine via the routines UI ("Run"), or ask Claude to
`RemoteTrigger run`. Success signal: a new `run <date>` commit appears on `main` AND the
email arrives. On weekends/quiet days an empty result (no email, no commit) is normal.

**Add a stock:** `cp -r stocks/FERG stocks/<TICKER>`, edit the 3 files
(`profile.yaml`, `sources.yaml`, `signal.md`), uncomment the ticker under
`config.yaml -> enabled`, commit + push. Zero engine/routine changes. Research drafts for
RKT / AUR / WRBY / CPNG are in `companies-and-sources.md`.

**Tune FERG:** edit `stocks/FERG/FERG-input.md` (the human scratch sheet), then fold changes
into the 3 machine-read files. Commit + push.

**Rotate a secret:** regenerate the Gmail password or GitHub PAT, then update the routine
config (prompt for the password, clone URL for the PAT) and push nothing — secrets are not
in the repo.

## Status (2026-06-07)
- ✅ Engine, FERG profile, repo, routine, both secrets wired in.
- ✅ Repo access from the cloud agent (PAT-in-URL) — run accepted, no longer denied.
- ⏳ **Unverified end-to-end:** the email *send* and the state *push-back* only exercise when
  there's real news; first test was triggered on a Sunday (likely empty). Confirm on the
  first weekday run (Mon 2026-06-08) that (a) the email arrives and (b) a `run` commit lands.
- ⛔ Stocks RKT / AUR / WRBY / CPNG: not yet configured (commented out in `config.yaml`).
