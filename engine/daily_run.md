# News Agent — Daily Run Playbook

This mirrors the prompt the scheduled Claude agent follows every weekday (~8am ET).
Working dir: the repo root. Goal: a 1-page, high-signal digest grouped by company,
ranked by thesis relevance then signal. Delivery is IN-APP (the run's final message).
The authoritative agent contract is `CORE.md`; this file covers the news spoke.

## Steps

1. **Window.** Read `config.yaml -> run`: `monday_lookback_hours` on Mondays (ET),
   else `lookback_hours`. Windows don't overlap between runs — that's the primary dedupe.

2. **For each ticker in `config.yaml -> enabled`:**
   a. Read the CORE — `companies/<T>/thesis.md`, `companies/<T>/input.md` — and the
      news config: `companies/<T>/news/{profile.yaml, sources.yaml, signal.md}`.
   b. **Inbox:** fold any `input.md` notes into the right files (thesis points →
      thesis.md; companies/weights → news/profile.yaml; rules → news/signal.md;
      sources → news/sources.yaml), clear to header, record for the changelog.
   c. **Gather** news in-window across the whole universe + mapped `macro/macro.yaml`
      signals. Verify publication DATES; discard out-of-window items ruthlessly.
   d. **Dedupe (2nd layer):** `python engine/state.py filter <T>` if state.json has data.
   e. **Judge:** thesis-relevant items (pillar confirmed/threatened, debate moved,
      watched metric) are auto-HIGH with 🎯 + which pillar. Then signal.md HIGH,
      MEDIUM if room. Strict — empty is a SUCCESS.
   f. **Learnings:** durable discoveries → append attributed line to
      `companies/<T>/learnings.md`; mechanical facts auto-applied to news/profile.yaml;
      judgment calls as PROPOSAL lines. Most days: skip.

3. **Compose** one digest (`# Daily Stock News — <date_et>`, `## TICKER — Name` sections,
   🎯 items first, one tight bullet per item, omit empty companies). End with a
   `_Config updated:_` section if any files changed.

4. **Save** to `output/<YYYY-MM-DD>.md`.

5. **Deliver in-app:** final message = `📈 Daily Stock News — <Day> <Mon> <D>: <N>
   item(s) — <tickers or 'no signal today'>.` + blank line + full digest.

6. **Persist (best-effort):** `state.py mark` per delivered ticker, then
   `git pull --rebase` + `git add companies/ output/` + commit `run <date>` + push.
   On push failure append `[state push FAILED: <reason>]` to the final message.

## Quality bar
High signal only; one line per item; no price-action noise, syndicated PR, or listicles;
lead each company with its most important item; never repeat an item already shown;
config edits surgical, always changelogged. Short or empty digest = SUCCESS.
