# Ingest — folding a new raw file into a company's knowledge

The core loop: **a file lands in `companies/<T>/sources/`, and it becomes cited knowledge.**
Run this in a local Claude session (ingest needs the raw files, which are git-ignored and
never reach the cloud routine). Trigger it by saying *"ingest the new FERG files"* or
*"ingest `<path>`"*.

## Steps

0. **Load context.** Read `companies/<T>/thesis.md` + `knowledge.md`, **and skim every other
   enabled name's `thesis.md`** (`config.yaml -> enabled`; they're short). You need the other
   theses to spot read-throughs — a claim in this file that bears on RKT is invisible unless
   you know RKT's thesis.

1. **Find what's new.** Diff the files in `companies/<T>/sources/` against what
   `knowledge.md`'s Log already cites. Anything uncited is new (or changed — re-ingest if a
   model/memo was updated).

2. **Read each file with the right tool.** PDFs/transcripts → read directly. Excel models →
   the `kpi-excel-generator` skill or read the sheets. A folder of expert calls → the
   `expert-call-synthesis` skill, then fold its outputs in here. Big files: extract the
   thesis-relevant parts, don't transcribe everything.

3. **Distill into `knowledge.md`.**
   - **Synthesis section:** integrate the new facts where they belong by theme. Rewrite for
     currency and non-redundancy — this is a living document, not an append log. Cite every
     claim `[sources/<filename>]`.
   - **Log section:** append one dated, attributed line — `- 2026-08-13 [ingest] Ferguson
     Q3 model: gross-margin bridge shows... [sources/FERG-model-2026Q3.xlsx]`.

4. **Cross-post read-throughs.** For each claim material to *another* enabled name's thesis
   (from step 0), append a cited note to *that* name's `knowledge.md` Log — tagged
   `[ingest←<T>]`, carrying the fact itself, cited `[<T>/sources/<file>]` (the note lives in
   the target's file; the raw source stays under `<T>`). Fold into the target's Synthesis if
   durable. If it's really a recurring *external* signal, add/adjust it in `macro/macro.yaml`
   instead. Only real read-throughs — judge against the target's thesis, not loose association.

5. **Touch `thesis.md` only by proposal.** If a file confirms/threatens a pillar or resolves
   a debate, add a `PROPOSAL (date) [ingest]:` line to the Log and surface it in your output.
   Apply a direct thesis edit only when working with the human in the session.

6. **Apply mechanical facts to `news/` config** (new universe members, a source to watch, a
   signal rule) — surgically, changelogged.

7. **Commit the synthesis only.** `git add` the `knowledge.md` of **every** name you touched
   (the ingested one *and* any cross-posted targets), plus `thesis.md` / `news/` / `macro/`
   as edited (raw `sources/` is git-ignored — verify `git status` shows no raw files).
   Message: `ingest <T>: <what>`. `git pull --rebase` before push.

## Guardrails
- **Never commit a raw file.** The repo is public. If `git status` ever lists something under
  `sources/`, stop — the `.gitignore` rule is `companies/*/sources/*`.
- Synthesis is judgment: prefer fewer, load-bearing, cited claims over a wall of quotes.
- One file can legitimately add nothing new to the thesis — that's a valid outcome; still log it.
