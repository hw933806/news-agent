# News Agent — Daily Run Playbook

This is the prompt the scheduled Claude agent follows every morning (~9am ET).
Working dir: the `News Agent/` folder. Goal: a 1-page, high-signal email, grouped by
stock, ranked highest→lowest within each stock. If nothing new for a stock, omit it.

## Steps

1. **Determine the window.** Use the last `run.lookback_hours` (24h) from `config.yaml`.
   Note today's date in ET for the subject line.

2. **For each ticker in `config.yaml -> enabled`:**
   a. Read `stocks/<TICKER>/profile.yaml` (universe + weights + macro_focus),
      `stocks/<TICKER>/sources.yaml` (tiered sources + custom feeds), and
      `stocks/<TICKER>/signal.md` (what counts as signal).
   b. Gather news from the last 24h across the **whole universe** (the name itself +
      competitors, suppliers, partners, demand read-throughs) and the macro signals in
      `macro/macro.yaml` that list this ticker. Prefer higher-tier sources; use
      WebSearch/WebFetch. Capture {title, url, source, date, one-line summary} per item.
   c. **Dedupe:** write the gathered items to a temp JSON and run
      `python engine/state.py filter <TICKER>` to drop anything already emailed.
   d. **Judge signal** using `signal.md`: keep HIGH and (if room) MEDIUM; drop LOW/excluded.
      Weight by the universe `weight` and macro relevance. Be strict — empty is fine.
   e. **Rank** the survivors highest→lowest signal. Write 1 tight bullet each:
      `**[Company]** — what happened + why it matters. ([source](url))`

3. **Compose** one email body in markdown (see template below). Omit any stock with no
   new high-signal items. If ALL stocks are empty and `skip_email_if_all_empty: true`,
   do not send — just log "no signal today".

4. **Save** the body to `output/<YYYY-MM-DD>.md` (audit trail).

5. **Deliver in-app.** The cloud sandbox blocks outbound SMTP, so we do NOT send email.
   Instead, the run's **final message IS the digest** — the reader opens it in the Claude
   routines view (same as the other monitor agents). `deliver.py` is retained only for
   manual/local use. If no stock has signal, the final message simply says "no signal today".

6. **Record seen:** mark the delivered items as seen so they never repeat:
   `python engine/state.py mark <TICKER> <YYYY-MM-DD> < emailed_items.json` (per stock).

7. **Persist state (remote runs only).** The cloud sandbox is ephemeral — commit the updated
   dedupe cache and audit file back to the repo so tomorrow's run remembers what was shown:
   `git add stocks/*/state.json output/ && git commit -m "run <YYYY-MM-DD>" && git push`.
   If nothing changed (empty day) or push fails, log it and continue.

## Email template
```
# Daily Stock News — {date_et}

## FERG — Ferguson
- **[Company]** — one-line what + why it matters. ([source](url))
- ...

## RKT — Rocket Companies
- ...

_(stocks with no new signal are omitted)_
```

## Quality bar
- High signal only. A short or empty email is a SUCCESS, not a failure.
- One line per item. No price-action noise, no syndicated PR, no listicles.
- Lead each stock with its single most important item.
- Never repeat an item already sent (that's what state.py enforces).
