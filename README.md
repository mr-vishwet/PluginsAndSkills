# Plugins and Skills

Portable snapshot of the Qoder and OpenCode setup on this Windows machine,
refreshed 2026-11-09. The goal is to rebuild the same working environment on
another computer without guessing which skills, plugins, or MCP servers were
installed.

## What is inside

| Folder | Mirrors | Contains |
| --- | --- | --- |
| `qoder/` | `~/.qoder` | Global `AGENTS.md`, sanitized `settings.json`, all 20 user skills, installed plugin manifest |
| `opencode/` | `~/.config/opencode` | `AGENTS.md`, sanitized `opencode.json`, `opencode.jsonc` with six browser MCP servers, 20 skills, 2 commands, 2 local plugins, 5 local bridge scripts, browser preference |
| `fcc/` | `~/.fcc` | Shape of the Free Claude Code proxy config: env template, Antigravity integration, ports and CLIs |
| `mcp/` | no single folder | Full MCP server catalog: source, transport, tool count, requirements |

Start with [INVENTORY.md](INVENTORY.md) for the master list, then
[INSTALL.md](INSTALL.md) for the rebuild sequence.

## Quick start on the new machine

```bash
cd PluginsAndSkills
./install.sh --dry-run     # show what would be copied
./install.sh               # copy skills, commands, plugins, AGENTS.md (never overwrites silently)
```

Then:

1. Install the four Qoder plugins from the Qoder marketplace (see `qoder/plugins/PLUGINS.md`).
2. Add the two custom MCP servers in Qoder Settings, or merge `qoder/settings.template.json`.
3. Reinstall Free Claude Code if you use the `freecc` provider (see `fcc/README.md`).
4. Fill the model-provider keys in `opencode/opencode.template.json` and save it as `~/.config/opencode/opencode.json`.
5. Update the machine-specific paths listed in [INVENTORY.md](INVENTORY.md#machine-specific-paths).

## What is deliberately not included

- API keys, OAuth tokens, cookies, session tokens, and passwords.
  `opencode.json` is stored as a template, and `fcc/.env` is represented by
  `fcc/env.example` with `REPLACE_ME_*` placeholders.
- `~/.fcc/.env`, `fcc.db`, `*.log`, and `*.lock` (runtime state and provider keys).
- `~/.qoder/.auth/`, `~/.qoder/mcp-router.json` (runtime key), `~/.qoder/ipc/`, logs, caches,
  `file-history/`, `tasks/`, and `projects/`.
- `~/.config/opencode/pplx-meta.json` (live Perplexity cookies) and `service.json`.
  A shape-only template is provided as `opencode/pplx-meta.template.json`.
- Plugin binaries under `~/.qoder/plugins/cache/` and bundled app skills. Those are
  reinstalled by Qoder and its plugin marketplace, not copied.
- Python virtual environments. Rebuild them from each skill's instructions.

## Snapshot facts

- Qoder user skills: 20
- OpenCode user skills: 20 (mirrored from the Qoder set, plus `cloudflare-free-deploy`)
- Installed Qoder plugins: 4
- Registered MCP servers: 5 custom or plugin-provided, plus 4 app-managed servers
- OpenCode MCP declarations: 6 (5 enabled, 1 disabled) in `opencode.jsonc`
- OpenCode model providers: 3 (`ox-alpha`, `omniroute`, `explabs`)
- Free Claude Code proxy: 1 local provider on port 8082
- Export size: about 8 MB

Counts and versions are a point-in-time fact. Re-check them after a Qoder or
OpenCode upgrade before trusting the catalog.
