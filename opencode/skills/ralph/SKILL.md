---
name: ralph
description: "Ralph autonomous build loop (snarktank/ralph). Turns a feature into a PRD, converts that PRD into prd.json, then loops one user story per iteration against a fresh context until every story passes, using progress.txt as memory. Use when the user says 'ralph', 'run the loop', 'build this PRD autonomously', 'loop until the tests pass', 'keep going until done', or hands over a feature spec to implement unattended. Subcommands: /ralph prd, /ralph convert, /ralph run."
---

# Ralph

Files: `references/create-prd.md` (PRD writer), `references/prd-json.md` (PRD →
`prd.json`), `iteration-prompt.md` (what each iteration does), `ralph.sh`
(external runner), `prd.json.example`. Work happens in the user's project at
`.ralph/prd.json`, `.ralph/progress.txt`, `.ralph/archive/`.

Ralph is a loop, not a single answer: each pass implements **one** story, then
forgets everything and relies on the files. Small stories are the whole game —
if a story cannot be described in 2-3 sentences, split it.

## 1. `/ralph prd <feature idea>`

Follow `references/create-prd.md`: ask 3-5 critical questions with lettered
options, then write `tasks/prd-<feature>.md`. Do not implement anything.

## 2. `/ralph convert <path/to/prd.md>`

Follow `references/prd-json.md` to produce `.ralph/prd.json` — one entry per
story, dependency order (schema → logic → UI), `passes: false`, and a verifiable
acceptance criterion list per story ending with the project's quality gate.
Archive any previous run first (see below).

## 3. `/ralph run [max iterations]` (default 10)

Confirm with the user before starting: branch it will work on, the story count,
and the max. Then loop until every story is `passes: true` or the max is hit.

**Fresh context per iteration (preferred — true Ralph semantics).** Each pass:

1. `mcp__builtin__create_chat_session` with a self-contained prompt: the project
   path, the contents of `iteration-prompt.md`, and the paths to `.ralph/prd.json`
   and `.ralph/progress.txt`. Never forward an instruction to create another
   session; the worker does the story itself.
2. `mcp__builtin__wait_chat_sessions` — one session at a time. This machine has
   8 GB RAM; do not run iterations in parallel, because they commit to the same
   branch and collide.
3. `mcp__builtin__read_chat_session` to check the outcome. Look for
   `<promise>COMPLETE</promise>` in the reply, and verify `prd.json` actually
   flipped the story — a worker claiming success is not evidence.
4. Append the story id to the progress log if the worker skipped it, then start
   the next iteration.

**In-conversation fallback.** If the user wants it in this chat, run
`iteration-prompt.md` directly, one story per pass, re-reading `prd.json` and
`progress.txt` at the top of every pass instead of trusting what is already in
context. Stop and tell the user when context is getting long — a fresh session is
then the right driver.

**External runner.** `.ralph/ralph.sh --tool opencode 10` runs the same loop
outside Qoder. Copy it from this skill directory, put it beside `prd.json`, and
chmod +x. `--tool opencode` is the only headless agent CLI on this machine; edit
the `run_tool` function to point at any other CLI.

## Every pass must

- Work on one story, run the quality gates, and commit as `feat: US-00X - Title`.
- **Append** to `progress.txt`; never rewrite it. Consolidate reusable patterns
  into its `## Codebase Patterns` header block.
- Set `passes: true` only after gates pass.

## Guardrails

- Never push, never open PRs, never force anything. Ralph commits locally only.
- If a story fails twice in a row, stop and report: the story is too big or the
  acceptance criteria are unverifiable. Split it.
- If gates fail, do not commit — leave the tree clean and log why.
- If the working tree is dirty before starting, stop and ask.

## Archiving a previous run

Before writing a new `prd.json`: if one exists with a different `branchName` and
`progress.txt` has content beyond its header, copy both to
`.ralph/archive/YYYY-MM-DD-<feature>/`, then reset `progress.txt` with a fresh
header. `ralph.sh` does this automatically from `prd.json`'s `branchName`.
