# OpenCode mirror

This folder mirrors `~/.config/opencode`. It holds the agent rules, the model
providers, 20 skills, two commands, two local plugins, browser MCP servers,
and the local bridge scripts.

| Here | Target | Purpose |
| --- | --- | --- |
| `AGENTS.md` | `~/.config/opencode/AGENTS.md` | Global engineering rules and browser selection |
| `opencode.template.json` | `~/.config/opencode/opencode.json` | Models, providers, skills path, plugins, empty MCP block |
| `opencode.jsonc` | `~/.config/opencode/opencode.jsonc` | Six browser MCP servers |
| `browser_pref.json` | `~/.config/opencode/browser_pref.json` | Remembered browser choice |
| `pplx-meta.template.json` | `~/.config/opencode/pplx-meta.json` | Shape for Perplexity cookies, values removed |
| `skills/` | `~/.config/opencode/skills/` | The same 20 skills as the Qoder tree |
| `command/` | `~/.config/opencode/command/` | `archify.md`, `docs-skill/customize.md` |
| `plugin/` | `~/.config/opencode/plugin/` | `oxalpha-chat.ts`, `browser-chooser.ts` |
| `scripts/` | `~/.config/opencode/scripts/` | Five local OpenAI-compatible bridges |

## Config layout

The snapshot config has these top-level keys:

| Key | Value |
| --- | --- |
| `model` | `opencode/big-pickle` |
| `small_model` | `opencode/mimo-v2.5-free` |
| `provider` | 3 providers, see [PROVIDERS.md](PROVIDERS.md) |
| `skills.paths` | `["~/.config/opencode/skills"]` |
| `plugin` | `@dietrichgebert/ponytail`, `./plugin/oxalpha-chat.ts` |
| `mcp` | empty in `opencode.json`; six servers live in `opencode.jsonc` |

`opencode.json` is stored as a template. `omniroute` keeps a placeholder key and
`explabs` reads `EXPLABS_API_KEY` from the environment; only the local
`ox-alpha` key is a fixed dummy.

## Skills

This machine keeps the full 20-skill set under `~/.config/opencode/skills/`, the
same list as [../qoder/skills/INDEX.md](../qoder/skills/INDEX.md). A handful of
files differ only by the bundle root path that each app rewrote.

OpenCode reads `skills.paths` from the config. If you would rather keep one copy,
change the path to `~/.qoder/skills` and drop `opencode/skills/`. Keep
`docs-skill`'s assets with whichever copy you use. `docs-skill` also carries the
`appristine` brand header in this copy.

## Commands

| Command | Purpose |
| --- | --- |
| `command/archify.md` | Slash command for the Archify diagram workflow |
| `command/docs-skill/customize.md` | Sub-command for customizing docs-skill output |

## Plugins

| Plugin | Source | Purpose |
| --- | --- | --- |
| `@dietrichgebert/ponytail` | npm | Ponytail standards as an OpenCode plugin |
| `./plugin/oxalpha-chat.ts` | local | Chat integration for the `ox-alpha` provider on port 3900 |
| `./plugin/browser-chooser.ts` | local | Browser selection helper; copied but not in the active `plugin` array |

The npm plugin installs on OpenCode startup. The two TypeScript files must exist
at the relative paths in the `plugin` array, so keep the folder name `plugin/`.
Add `./plugin/browser-chooser.ts` to the array if you want it loaded.

## Browser MCP

`opencode.jsonc` declares Composio, Firefox DevTools, Playwright, Playwright
Chrome, Playwright Firefox (disabled), and Playwright headless. Table and
requirements: [../mcp/MCP-CATALOG.md](../mcp/MCP-CATALOG.md#opencode-mcp-servers).

`browser_pref.json` says Firefox, remembered. The rules in `AGENTS.md` tell the
agent to read that file and use only the matching tools. If you change the
browser, update both.

## AGENTS.md

The OpenCode rules cover:

- Ponytail planning, architecture, Flutter, state management, performance,
  security, and self-review rules.
- The `PONYTAIL-EXCLUDE` escape keyword.
- The response tag `[PONYTAIL ACTIVE]`.
- Browser selection and remembering the choice.

It is more verbose than the Qoder `AGENTS.md` but expresses the same standards.

## Free Claude Code

Free Claude Code (FCC) is not listed in `opencode.json` on purpose. The
`fcc-opencode` launcher starts OpenCode with a process-local provider
(`free-claude-code`) that points at `http://127.0.0.1:8082/v1`, so the saved
config stays clean. See [../fcc/README.md](../fcc/README.md).

## Restore

The root `install.sh` copies everything in this folder. Manual equivalent:

```bash
mkdir -p ~/.config/opencode/{skills,command,plugin,scripts}
cp -R skills/* ~/.config/opencode/skills/
cp -R command/* ~/.config/opencode/command/
cp -R plugin/* ~/.config/opencode/plugin/
cp -R scripts/* ~/.config/opencode/scripts/
cp AGENTS.md ~/.config/opencode/AGENTS.md
cp browser_pref.json ~/.config/opencode/browser_pref.json
cp opencode.template.json ~/.config/opencode/opencode.json
cp opencode.jsonc ~/.config/opencode/opencode.jsonc
chmod 600 ~/.config/opencode/opencode.json
```

Then fill the keys and start the bridges you need.

## Verify

```bash
python3 -m json.tool ~/.config/opencode/opencode.json > /dev/null && echo json-ok
opencode --version
opencode run 'list the skills you can see'
```

If the Playwright tools are missing, merge the `mcp` block from `opencode.jsonc`
into the active `opencode.json` and restart OpenCode.

## Excluded

`opencode.json.bak*` is excluded because older backups contain credentials.
`service.json` contains a password. `pplx-meta.json` contains live cookies. The
`node_modules/` folder and `kaggle-proxy.log` are reinstallable or disposable.
