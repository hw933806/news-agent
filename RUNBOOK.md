# News Agent — Operations Runbook

How this system is deployed and run in production. (Design lives in `ARCHITECTURE.md`;
the daily agent's instructions live in `engine/daily_run.md`.)

_Last updated: 2026-07-10._

## What it does
Every weekday at **8:00am ET**, a remote Claude agent gathers the trailing news window across
each enabled stock's universe + mapped macro signals, judges signal, dedupes against what was
already shown, and produces a one-page digest. **Delivery is in-app** — you read the digest as
the run's output in the Claude routines view (same pattern as the AI Frontier Monitor agents).
A short or empty digest is a success — noise is the enemy.

## Deployment (the moving parts)

| Piece | Where | Notes |
|---|---|---|
| Code + config | GitHub: **hw933806/news-agent** (PUBLIC) | Cloud agent clones this each run. Public so clone needs no creds (see "why" below). No secrets in the repo. |
| Schedule | claude.ai routine **`trig_01BBa7EH3oW4Cq8xbD6nFg3D`** | Manage/read output: https://claude.ai/code/routines/trig_01BBa7EH3oW4Cq8xbD6nFg3D |
| Cron | `0 12 * * 1-5` (UTC) | = 8am ET **during EDT**. See DST note below. |
| Model | Opus 4.8 | Judgment-heavy task. |
| Runtime | Anthropic cloud (CCR) | Ephemeral sandbox — nothing local persists; state is pushed back to the repo. Outbound **SMTP is blocked** (HTTPS is allowed). |
| Delivery | In-app (run output) | The agent's final message IS the digest. No email. `deliver.py` retained for manual/local use only. |

### The one secret: GitHub PAT (for state push-back only — now BEST-EFFORT)
The repo is public, so cloning needs nothing. The agent **tries** to push `state.json` +
`output/` back each run using a GitHub fine-grained PAT **only in the runtime `git push`
command** inside the routine prompt (`git push https://x-access-token:<PAT>@github.com/...`).
Scope: `news-agent` only, Contents read/write; rotate at
https://github.com/settings/personal-access-tokens (current token expires ~Oct 2026).

**⚠️ Since 2026-07-10 sandbox pushes FAIL** even with a fresh, locally-verified token (a
minimal clone→commit→push diagnostic run also failed; last successful push was 2026-07-09).
Suspected platform-side change in credential handling. Because of this, dedupe no longer
depends on the push — see "Dedupe design" below. If a run's digest ends with
`[state push FAILED: ...]`, that is expected for now and harmless.

> **Hard-won lessons (why it's built this way):**
> - **Private repos don't work** for scheduled routines: the claude.ai web-chat GitHub OAuth
>   link does NOT reach cloud agents (`github_repo_access_denied`); the `authorization_token`
>   field is rejected; and an **embedded-credential clone URL passes create-time validation but
>   is rejected at run time** (`session_config_rejected`) — which silently **auto-disabled** the
>   routine for ~9 days. → Repo made **public**; PAT used only in the runtime push command.
> - **Email doesn't work from the sandbox:** outbound SMTP is blocked. → Delivery is **in-app**.

### Dedupe design (works without push-back)
Windows don't overlap, so repeats are structurally impossible even with zero state:
**Tue–Fri lookback = 24h** (`run.lookback_hours`), **Monday = 72h**
(`run.monday_lookback_hours`, covers the weekend). `state.py filter` still runs as a
belt-and-braces layer whenever `state.json` has data, and the push is attempted each run so
state resumes automatically if the platform re-allows it.

### Notifications
Push notifications are ON for this routine (`notifications.channel.push: true`, set
2026-07-10 via `RemoteTrigger update`). Note: routines created without a `notifications`
field get push by default; this one had all channels explicitly false — that's why early
digests never notified.

### DST caveat
Cron is fixed in **UTC**. `0 12` = 8am ET only while New York is on EDT (Mar–Nov). When
clocks fall back (early Nov), update the routine to `0 13 * * 1-5` to stay at 8am ET.

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

**Add a company:** `cp -r companies/FERG companies/<TICKER>`, edit the `news/` configs
(`profile.yaml`, `sources.yaml`, `signal.md`), blank the core files, add the ticker under
`config.yaml -> enabled`, commit + push. Zero engine/routine changes. Web-verify any
time-sensitive facts first — training-data staleness (dead tickers, closed M&A) was the
main defect found when RKT/AUR/WRBY/CPNG were built on 2026-07-10.

**Evolve a company (the compounding core, since 2026-07-13 — full contract in `CORE.md`):**
`companies/<T>/` is the hub shared by all agents:
- `thesis.md` — the live investment thesis (human-owned). Every agent ranks by relevance
  to it; thesis-relevant items are auto-HIGH and marked 🎯.
- `input.md` — the inbox. Drop raw notes anytime (GitHub app works from a phone); the next
  agent run folds them into thesis/config files, clears the inbox, and lists the changes
  in a `_Config updated:_` section of its output.
- `learnings.md` — append-only, agent-attributed discoveries; judgment calls as
  `PROPOSAL:` lines — approve/reject via the inbox.
- `evidence/` — dated distilled notes from any agent (news events, transcripts, expert calls).
- `news/` — the news spoke's private config.
All edits are git commits: reviewable and revertible.

**Rotate the PAT:** regenerate the fine-grained token at github.com/settings/personal-access-tokens,
then `RemoteTrigger update` the routine prompt's `git push` URL with the new token. Nothing in
the repo to change.

## Status (2026-07-10)
- ✅ **All 5 stocks live**: FERG, RKT, AUR, WRBY, CPNG configured and enabled. The 4 new
  configs were built from web-verified July 2026 facts (not the June draft in
  `companies-and-sources.md`, which is now historical).
- ✅ Routine renamed **"Daily Stock News"**; prompt covers every enabled ticker, rebases
  before push, and flags push failures visibly in the digest.
- ✅ Push notifications enabled (see above).
- ⚠️ **Sandbox git push broken since 2026-07-10** (see PAT section). Dedupe switched to
  non-overlapping date windows (24h / 72h Mon) so it doesn't matter operationally. Retest
  occasionally; delete the one-shot "TEMP git push diagnostic" routine when done.
- ℹ️ Email was abandoned long ago: the sandbox blocks SMTP. Delivery is in-app.
