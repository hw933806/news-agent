# The Core — contract for every agent

This repo is a research OS built hub-and-spoke: `companies/<TICKER>/` is the **core**
(the hub) — the canonical, evolving record of what the owner believes and knows about
each name. Agents (the spokes) read the core for context and write back what they learn.
The daily news agent is one spoke; transcript and expert-interview agents plug in the
same way. The core outlives any individual agent.

## Core files per company

| File | Owner | Rules |
|---|---|---|
| `thesis.md` | **Human** | The live investment thesis: pillars, open debates, what-would-change-my-mind, watched metrics. Agents READ it to judge relevance and NEVER rewrite it on their own judgment. Only two write paths: (1) folding the human's own `input.md` notes, (2) edits made with the human in a Claude session. Agents with a thesis-relevant discovery add a `PROPOSAL` to `learnings.md` instead. |
| `input.md` | **Human** (write) / agents (fold) | The inbox. Human drops raw notes anytime. The next agent run that processes the company folds them into the right files (thesis, learnings, or that agent's own config), resets the file to its header, and reports every change in its output ("Config updated"). |
| `learnings.md` | **Agents** (append-only) | Dated one-liners for durable discoveries, each attributed: `- 2026-07-14 [news] CNM earnings consistently move FERG; raised weight.` Judgment calls are `PROPOSAL (date) [agent]:` lines — the human approves via `input.md` or a session. Never edit or delete prior lines. |
| `evidence/` | **Agents** | One markdown file per source or event: `YYYY-MM-DD-<slug>.md`, starting with a few frontmatter lines (`date`, `source`, `agent`, `thesis pillars touched`), then the distilled note. This is the shared evidence base — every agent may read all of it. |
| `news/` | news agent | Spoke-private config: `profile.yaml` (universe), `sources.yaml`, `signal.md`, `state.json` (dedupe). Other spokes keep their own subfolder the same way (e.g. `transcripts/`). |

## Rules for any agent (current or future)

1. **Read `thesis.md` first.** Relevance is judged against the thesis, not in the abstract.
   Anything confirming/threatening a pillar, resolving a debate, or moving a watched
   metric is top-priority output (🎯).
2. **Process `input.md`** if it has notes: fold, clear to header, report changes.
3. **Write durable value to the core**, not just to your own output: evidence notes to
   `evidence/`, discoveries to `learnings.md` (attributed), structural facts (delistings,
   closed M&A) applied to your own config files directly.
4. **Propose, don't impose**, on `thesis.md` and cross-agent judgment calls.
5. **Surgical edits + visible changelog.** Change only what a note or discovery justifies;
   list every config change in your run output. All writes are git commits — reviewable
   and revertible.
6. **Commit and push** with an agent-attributed message (`run 2026-07-14` for the news
   agent; `transcripts: <what>` etc. for others). `git pull --rebase` before pushing.

## Current spokes

| Spoke | Runs | Reads | Writes |
|---|---|---|---|
| **news** (live) | Weekday 8am ET routine | thesis, input, news/ config, macro/ | digest → `output/`, learnings, evidence (major events), news/ config |
| **transcripts** (planned) | On new earnings call / filing | thesis, input | evidence note per transcript, learnings, proposals |
| **expert-calls** (via Claude session) | When the owner runs the expert-call-synthesis skill | thesis | evidence note per interview, thesis edits WITH the human, learnings |
