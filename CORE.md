# The Core — contract for every agent

This repo is a research OS. `companies/<TICKER>/` is the **core**: one folder per name
holding everything known about it. You drop raw files in, agents synthesize them into a
living memory, and every agent — the daily news spoke, ingest, future spokes — reads that
memory for context and writes back what it learns. The core outlives any individual agent.

The mental model is simple: **raw in `sources/`, synthesis in `knowledge.md`, the human's
view in `thesis.md`.** Everything else is plumbing.

## Core files per company

| File | Owner | Rules |
|---|---|---|
| `sources/` | **Human** (drop) / agents (read) | Raw diligence: memos, Excel models, expert-call PDFs/transcripts, filings, screenshots. Drop anything, anytime. **Git-ignored — local only** (this repo is public). Agents read these on ingest and cite them; they never live in git. |
| `knowledge.md` | **Agents** | The single living synthesis — the distilled memory built from `sources/` + daily news. A **Synthesis** section (rewritten freely to stay current, grouped by theme) and an append-only **Log** (dated, attributed, one line per ingested file or durable discovery). Every claim cites its origin: `[sources/<file>]` or `[news YYYY-MM-DD]`. **May hold cross-refs from other names** (see below) — a company's `knowledge.md` is the complete view of what's relevant to it, wherever the fact came from. Replaces the old `evidence/` archive and `learnings.md`. |
| `thesis.md` | **Human** | The live investment thesis: pillars, open debates, what-would-change-my-mind, watched metrics. Agents READ it to judge relevance and never rewrite it on their own judgment. Two write paths only: (1) folding the human's `input.md`, (2) edits made with the human in a session. A thesis-relevant discovery becomes a `PROPOSAL` line in `knowledge.md`'s Log — the human approves it. |
| `input.md` | **Human** (write) / agents (fold) | The inbox. Drop raw notes anytime (GitHub app works from a phone). The next agent run that touches the company folds them into the right files, resets the file to its header, and reports every change in its output. |
| `news/` | news agent | Spoke-private config: `profile.yaml` (universe), `sources.yaml`, `signal.md`, `state.json` (dedupe). Future spokes keep their own subfolder the same way. |

## Ingesting a new file (the core loop)

"Just ingest whenever a new file comes in." When a file lands in `companies/<T>/sources/`,
run the ingest flow (`INGEST.md`): read it, distill thesis-relevant facts into
`knowledge.md` (cited back to the file), propose any `thesis.md` changes, apply mechanical
config facts to `news/`, and commit **only the synthesis** (raw files stay git-ignored).
Ingest is a local Claude session — it's judgment-heavy and needs the raw files, which the
cloud routine never sees.

## Cross-company relevance (the read-through layer)

A fact surfaced for one name is often material to another — a comp's pricing in a FERG
expert call that reads through to RKT, a Coupang logistics data point that bears on AUR.
Two kinds of cross-name link, two homes:

- **External signals** (rates, tariffs, housing, freight, FX) → `macro/macro.yaml`, which
  maps each signal to the names it moves. Config the news agent already ranks by.
- **A claim from one company's material that bears on another** → **cross-post it.** Write a
  *cited* note into the other name's `knowledge.md` Log so that file stays the complete view
  of what's relevant to it. The note must carry the actual fact (raw `sources/` are
  local-only), tag its origin, and cite the originating file:
  `- 2026-08-13 [ingest←FERG] CNM (FERG's closest comp) guided H2 price deflation ~mid-single
  digits — read-through to RKT purchase-mortgage demand. [FERG/sources/expert-call-2026-08.pdf]`
  Tags: `[ingest←<TICKER>]` when it came from ingesting that name's file, `[news→<TICKER>]`
  when the daily agent spots one name's item moving another. Fold it into the target's
  Synthesis too if it's durable. Judge relevance against the **target's** thesis — cross-post
  only real read-throughs, not everything tangentially related.

## Rules for any agent (current or future)

1. **Read `thesis.md` first, then `knowledge.md`.** Relevance is judged against the thesis,
   not in the abstract. Anything confirming/threatening a pillar, resolving a debate, or
   moving a watched metric is top-priority output (🎯).
2. **Process `input.md`** if it has notes: fold, clear to header, report changes.
3. **Write durable value to `knowledge.md`**, not just to your own output — cited. Keep the
   Synthesis current and non-redundant; append to the Log, never rewrite it.
   **Cross-post** any read-through to another name into *that* name's `knowledge.md` (see
   "Cross-company relevance"), judged against the target's thesis.
4. **Propose, don't impose**, on `thesis.md` and cross-agent judgment calls (`PROPOSAL` lines).
5. **Surgical edits + visible changelog.** Change only what a note or discovery justifies;
   list every change in your run output. Commits are the audit trail — reviewable, revertible.
6. **Never commit `sources/`** (it's git-ignored) and never put raw diligence in a tracked
   file — the repo is public.
7. **Commit and push** with an attributed message (`run 2026-07-14` for news; `ingest <T>:
   <what>` for ingest; etc.). `git pull --rebase` before pushing.

## Current spokes

| Spoke | Runs | Reads | Writes |
|---|---|---|---|
| **news** (live) | Weekday 8am ET routine | thesis, knowledge, input, news/ config, macro/ | digest → `output/`, knowledge.md, news/ config |
| **ingest** (local session) | Whenever a new file lands in `sources/` | thesis, knowledge, the new file(s) | knowledge.md synthesis + log, thesis proposals, news/ config |
| **expert-calls** (via the expert-call-synthesis skill) | When the owner runs the skill on a `sources/` transcript folder | thesis | knowledge.md + thesis edits with the human |
