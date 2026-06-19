# News Agent — Operations Runbook

How this system is deployed and run in production. (Design lives in `ARCHITECTURE.md`;
the daily agent's instructions live in `engine/daily_run.md`.)

_Last updated: 2026-06-19._

## What it does
Every weekday at **9:00am ET**, a remote Claude agent gathers the trailing news window across
each enabled stock's universe + mapped macro signals, judges signal, dedupes against what was
already shown, and produces a one-page digest. **Delivery is in-app** — you read the digest as
the run's output in the Claude routines view (same pattern as the AI Frontier Monitor agents).
A short or empty digest is a success — noise is the enemy.

## Deployment (the moving parts)

| Piece | Where | Notes |
|---|---|---|
| Code + config | GitHub: **hw933806/news-agent** (PUBLIC) | Cloud agent clones this each run. Public so clone needs no creds (see "why" below). No secrets in the repo. |
| Schedule | claude.ai routine **`trig_01BBa7EH3oW4Cq8xbD6nFg3D`** | Manage/read output: https://claude.ai/code/routines/trig_01BBa7EH3oW4Cq8xbD6nFg3D |
| Cron | `0 13 * * 1-5` (UTC) | = 9am ET **during EDT**. See DST note below. |
| Model | Opus 4.8 | Judgment-heavy task. |
| Runtime | Anthropic cloud (CCR) | Ephemeral sandbox — nothing local persists; state is pushed back to the repo. Outbound **SMTP is blocked** (HTTPS is allowed). |
| Delivery | In-app (run output) | The agent's final message IS the digest. No email. `deliver.py` retained for manual/local use only. |

### The one secret: GitHub PAT (for state push-back only)
The repo is public, so cloning needs nothing. But the agent **pushes `state.json` + `output/`
back** each run, and pushing needs write auth. That's done with a GitHub fine-grained PAT used
**only in the runtime `git push` command** inside the routine prompt
(`git push https://x-access-token:<PAT>@github.com/...`). Scope: `news-agent` only, Contents
read/write. Revocable/rotatable at https://github.com/settings/personal-access-tokens.

> **Hard-won lessons (why it's built this way):**
> - **Private repos don't work** for scheduled routines: the claude.ai web-chat GitHub OAuth
>   link does NOT reach cloud agents (`github_repo_access_denied`); the `authorization_token`
>   field is rejected; and an **embedded-credential clone URL passes create-time validation but
>   is rejected at run time** (`session_config_rejected`) — which silently **auto-disabled** the
>   routine for ~9 days. → Repo made **public**; PAT used only in the runtime push command.
> - **Email doesn't work from the sandbox:** outbound SMTP is blocked. → Delivery is **in-app**.

### DST caveat
Cron is fixed in **UTC**. `0 13` = 9am ET only while New York is on EDT (Mar–Nov). When
clocks fall back (early Nov), update the routine to `0 14 * * 1-5` to stay at 9am ET.

## Daily flow (what the agent does)
See `engine/daily_run.md` for the authoritative steps. In short: read config → for each
enabled ticker, fetch news over `lookback_hours` across its universe + macro → `state.py filter`
(dedupe) → judge with `signal.md` → compose → save to `output/<date>.md` → **emit the digest as
the run's final message (in-app delivery)** → `state.py mark` → **commit + push `state.json` +
`output/`** so tomorrow dedupes.

## Operations

**Read the digest:** open the routine at the URL above → latest run → its final output is the
digest. (Quiet days legitimately say "no signal today".)

**Run it now (test):** trigger via the routines UI ("Run") or `RemoteTrigger run`. Success
signal: a new `run <date>` commit on `main` + a digest in the run output.

**Add a stock:** `cp -r stocks/FERG stocks/<TICKER>`, edit the 3 files
(`profile.yaml`, `sources.yaml`, `signal.md`), uncomment the ticker under
`config.yaml -> enabled`, commit + push. Zero engine/routine changes. Research drafts for
RKT / AUR / WRBY / CPNG are in `companies-and-sources.md`.

**Tune FERG:** edit `stocks/FERG/FERG-input.md` (the human scratch sheet), then fold changes
into the 3 machine-read files. Commit + push.

**Rotate the PAT:** regenerate the fine-grained token at github.com/settings/personal-access-tokens,
then `RemoteTrigger update` the routine prompt's `git push` URL with the new token. Nothing in
the repo to change.

## Status (2026-06-19) — WORKING
- ✅ End-to-end verified: clone (public repo) → research → signal judgment → in-app digest →
  state push-back + dedupe. Lookback is config-driven (72h, covers weekend gap).
- ✅ FERG live on the weekday 9am ET schedule. Next run Mon 2026-06-22.
- ℹ️ Email was abandoned: the sandbox blocks SMTP. Delivery is in-app (see lessons above).
- ⛔ Stocks RKT / AUR / WRBY / CPNG: not yet configured (commented out in `config.yaml`).
