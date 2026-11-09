---
name: coding-decisions
description: Default coding decision rules for all code-writing and code-modifying tasks — minimal comments, reuse existing project patterns, scope discipline, reversible deprecation, honest verification. Apply on every task that writes, changes, or reviews code.
---

# Coding decisions

## Overview

Standing decisions to follow on every coding task unless the user overrides
them in the current request. When two rules conflict, the user's live request
wins, then the project's existing style.

## Comments

- Default: write no comments. Well-named code explains itself.
- Comment only when the WHY is non-obvious: a hidden constraint, a subtle
  invariant, a workaround for a specific bug, behaviour that would surprise a
  reader.
- Never write what-the-code-does narration (`// set the loader`, `// return
  the list`).
- Never task-referencing comments (`// added for X flow`, `// removed per
  ticket 123`, `// fix for the crash`) — that belongs in the commit message.
- One short line max. No multi-paragraph or multi-line comment blocks, no
  docstrings unless the project already documents that API.
- A disabled-reference marker is allowed when commenting-out code: state the
  restore step, nothing else.

## Reuse the project's own patterns

- Before writing a new widget, helper, screen, service, or endpoint call, find
  how the codebase already does this and copy that shape — same components,
  same naming, same folder, same loading/toast/validator conventions.
- Prefer editing an existing file over creating a new one.
- Put user-facing text in the project's central strings/constants file. Never
  hardcode it in the widget, and never split a label across files.

## Scope discipline

- Do exactly what was asked. No adjacent refactors, no new abstractions for a
  hypothetical second caller, no features inferred from the task.
- Three similar lines beat a premature helper. Add the helper when the third
  real duplication appears.
- No error handling, fallbacks, or validation for states that cannot happen.
  Validate at system boundaries only (user input, external APIs, network).
- No compatibility shims, renamed leftovers, or `// removed` stubs. If
  something is genuinely unused, delete it (see reversibility below).

## Reversible deprecation

- When the user says "comment it out / we may need it later", preserve
  verbatim: comment the old code in place, or keep the old file untouched and
  add the new one. Never delete the reference.
- Make the swap one-line reversible — repoint the caller (import + call site)
  so restoring the old path is a single edit.
- Ordinary unused code the user did not ask to keep: delete it cleanly instead.

## Verification and honesty

- Before reporting code as working, run the project's real checks (analyze,
  build, tests) and fix what they surface.
- Report only what was actually run, and say plainly which parts still need a
  device, simulator, console, or backend check. Never claim a UI or flow was
  tested when only static analysis ran.
- Do not state a remembered menu path, API field, or vendor step as fact
  without checking the current docs or the actual code.

## Secrets and shared state

- Never paste, print, commit, or transmit credentials, keystores, tokens, or
  private keys — not in code, docs, commit messages, or chat.
- Confirm before actions that affect shared or external state (push, publish,
  store/console changes, migrations); local edits and test runs need no
  confirmation.

## Working order

- For non-trivial changes, give the plan first when the user asks for one;
  otherwise state in one line what is about to change, do it, then report
  what changed and what remains. Keep end-of-turn summaries to one or two
  sentences.
