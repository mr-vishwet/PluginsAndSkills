---
name: gsd
description: "Get Shit Done — spec-driven planning and execution system for software projects. Use for new-project initialization, codebase mapping, requirements, roadmaps, phase planning, autonomous phase execution, UAT verification, milestone audits, or when the user says 'gsd', 'plan this project', 'break this into phases', 'execute the phase', or 'verify the work'. Invoked as /gsd <command> [args]."
---

# Get Shit Done

Bundle root: `C:/Users/User/.config/opencode/skills/gsd` (referred to as `$ROOT`).
Every command is a prompt file under `$ROOT/skills/`, driven by workflows under
`$ROOT/get-shit-done/`. Follow them literally — they are operational prompts,
not documentation.

## Running a command

`/gsd <command> [args]` maps to `$ROOT/skills/gsd-<command>.md`.

1. Read that file. Its `<execution_context>` lists `@path` files — Read **all**
   of them before doing anything else. They are required context.
2. Replace `$ARGUMENTS` with the args the user passed.
3. Execute the workflow end to end, preserving every gate it defines
   (validation, approval, commits, routing to the next command).
4. Report using the XML/markdown shapes the workflow specifies.

If `/gsd <command>` matches a skill installed separately
(`gsd-map-codebase`, `gsd-verify-work`, `gsd-plan-milestone-gaps`,
`gsd-project-researcher`), that skill is the same command — use either.

## Available commands

`new-project` `new-milestone` `map-codebase` `research-phase` `discuss-phase`
`plan-phase` `execute-phase` `verify-work` `add-tests` `code-review`-via-`health`
`quick` `progress` `pause-work` `resume-work` `debug` `health` `settings`
`set-profile` `add-phase` `insert-phase` `remove-phase` `add-todo` `check-todos`
`audit-milestone` `complete-milestone` `plan-milestone-gaps` `cleanup`
`list-phase-assumptions` `reapply-patches` `update` `help`

Typical flow: `map-codebase` (brownfield) → `new-project` → `plan-phase 1` →
`execute-phase 1` → `verify-work` → `complete-milestone`.

## Project state

All GSD state lives in the current project's `.planning/` directory
(`PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, `config.json`,
`codebase/`, `research/`, `phases/`). Load `.planning/STATE.md` when it exists
instead of re-deriving context.

Helper CLI (dependency-free Node; `run` it from the project directory so
`.planning/` resolves):

```
node $ROOT/get-shit-done/bin/gsd-tools.cjs <command> [args] [--raw]
```

Commands: `state load|get|update|json`, `resolve-model`, `find-phase`, `commit`,
`verify-summary`, `verify`, `frontmatter`, `template`, `generate-slug`,
`current-timestamp`, `list-todos`, `verify-path-exists`,
`config-ensure-section`, `phase`, `roadmap`, `milestone`, `validate`,
`progress`, `requirements`, `history-digest`, `init`. Its own header comment
lists every subcommand; read `$ROOT/get-shit-done/bin/gsd-tools.cjs` before
inventing an invocation.

## Tool mapping (Qoder, not Claude Code)

| Command file says | Do this |
| --- | --- |
| `Task` / spawn `gsd-<role>` agent | `Agent` tool: `Explore` for read-only research/mapping, `general-purpose` when the role must write files. Paste the role brief from `$ROOT/agents/gsd-<role>.md` into the delegation prompt, plus the file paths it must read. |
| `AskUserQuestion` | Use the `AskUserQuestion` tool. |
| Slash-command syntax `/gsd-foo` | `/gsd foo`. |
| `allowed-tools:` frontmatter | Ignore; it is Claude Code metadata. |

Parallel agent caps: this machine has 8 GB RAM. Spawn at most 4 agents at a
time, and prefer fewer when a workflow asks for fan-out.

## Rules

- Never skip a workflow gate to move faster; ask the user when a gate blocks.
- Do not implement features during planning commands — planning commands plan.
- Keep `.planning/` committed as the workflows instruct.
