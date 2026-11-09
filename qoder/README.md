# Qoder mirror

This folder mirrors the user-scope Qoder home. Copy it onto `~/.qoder` with
`install.sh`, or merge individual pieces by hand.

| Here | Target | Purpose |
| --- | --- | --- |
| `AGENTS.md` | `~/.qoder/AGENTS.md` | Global rules loaded into every Qoder session |
| `settings.template.json` | `~/.qoder/settings.json` | Enabled plugins, custom MCP servers, and the FCC model provider |
| `skills/` | `~/.qoder/skills/` | 20 user skills, each a folder with `SKILL.md` |
| `plugins/installed_plugins_v2.template.json` | `~/.qoder/plugins/installed_plugins_v2.json` | Installed plugin versions, for reference |
| `plugins/PLUGINS.md` | not applicable | Reinstall guide for the four plugins |

## How Qoder finds a skill

A skill is a folder under `~/.qoder/skills/` whose `SKILL.md` starts with YAML
frontmatter containing at least `name` and `description`. The description is what
the agent matches against a request. Supporting scripts, references, and
templates stay inside the same folder and are referenced relatively.

Rules that matter when adding a new one:

- The folder name and the `name` field should match.
- Keep `SKILL.md` at the folder root, not one level deeper.
- Use lowercase, hyphenated names.
- Do not add a nested `skills/` folder unless the parent skill is an orchestrator
  like `gsd`, which deliberately ships its own sub-skills.

## AGENTS.md

`AGENTS.md` is the always-on layer. This snapshot's version does three things:

1. Activates Ponytail standards on every coding request and appends
   `[PONYTAIL ACTIVE]`.
2. Activates the matching Kill The VibeCode skill for web or mobile UI work.
3. Defines the `PONYTAIL-EXCLUDE` escape keyword.

It references skills by absolute path, so the installer rewrites
`/Users/appristine` and `C:/Users/User` to the new home directory. If you copy
files manually, update those paths yourself.

## Settings and MCP

Qoder stores MCP servers in `settings.json` under `mcpServers`. The template has
the two custom entries, `Lunacy` and `computer-use`. Plugin-provided MCP servers
appear automatically when their plugin is installed; they do not need entries in
`settings.json`. See [../mcp/MCP-CATALOG.md](../mcp/MCP-CATALOG.md).

The `providers` block points Qoder at a local OpenAI-compatible server:
Free Claude Code on `http://127.0.0.1:8082/v1`, key `freecc`. Start the FCC
tray app before using it; setup notes are in [../fcc/README.md](../fcc/README.md).
The provider key `qoder-custom-<uuid>` is generated per registration, so Qoder
may create a different one when you add it from the UI.

## Plugins

Plugin binaries live in `~/.qoder/plugins/cache/` and are not part of this export.
Reinstall them from the Qoder marketplace. The manifest here is for checking
versions, not for copying into place.

## Verify

```bash
ls ~/.qoder/skills | wc -l
grep -L '^name:' ~/.qoder/skills/*/SKILL.md
python3 -m json.tool ~/.qoder/settings.json > /dev/null && echo settings-ok
```

The second command should print nothing. Any file it prints is missing
frontmatter and will not load as a skill.
