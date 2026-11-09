# Qoder plugins

Plugins are installed by Qoder, not copied. This file records what was installed
on 2026-11-09 and how to get the same set back.

## Marketplace

The only configured marketplace is the Qoder plugin catalog:

| Field | Value |
| --- | --- |
| ID | `qoder-plugins` |
| URL | `https://qoder.com/apphub/api/v1/marketplace/marketplace.json` |
| Auto update | on |
| Local cache | `~/.qoder/plugins/marketplaces/qoder-plugins` |

## Installed set

| Plugin ID | Display name | Version | Source | What it adds |
| --- | --- | --- | --- | --- |
| `Presentations@qoder-marketplace` | PPT | 0.1.4 | marketplace | `pptx` skill and the 11-tool `office` MCP server for creating and editing PPTX files |
| `office-excel@qoder-marketplace` | Excel | 0.1.2 | marketplace | Excel skill and the `office-excel` MCP server |
| `better-harness@qoder-marketplace` | Better Harness | 0.2.21 | marketplace | `better-harness` skill, references, and case studies for safe agent delivery |
| `qoder-context@qoderapp-bundler` | Qoder Context | 1.0.91.b22f2d0a | app bundler | Hidden plugin. Provides `SearchKnowledge` and `SearchWorkspace`, plus hooks |

Enablement is stored in `~/.qoder/settings.json` under `enabledPlugins`. All four
are enabled in the snapshot; the sanitized copy is `settings.template.json`.

Computer Use, Qoder Create Plugin, and Qoder Security were in the previous
snapshot and are no longer installed. The `computer-use` MCP entry is still in
`settings.json` because it points at the app-provided launcher under
`~/.qoder/bin/qoder-computer-use/`.

## Bundled, not in the manifest

These ship with Qoder Desktop and appear as plugin MCP providers without an entry
in `installed_plugins_v2.json`:

| Provider | Adds |
| --- | --- |
| `qoder.knowledge.center` | Repo Wiki (`ListWiki`, `ReadWiki`) and QMind (`qmind` server, 9 tools) |
| `qoder.sites` | 47-tool Sites server for preparing, publishing, and managing Qoder Sites |

The always-visible desktop tools, `browser-use`, `builtin`, `extension-market`,
and `node-repl`, are app-managed as well. They are not installable from this
export and their availability depends on the Qoder build.

## Reinstall on the new machine

1. Sign in to Qoder with the same account.
2. Open the plugin or extension marketplace.
3. Install by display name: Presentations, Excel, Better Harness.
4. Qoder Context normally installs itself and stays hidden. Confirm it is present
   by checking that `SearchKnowledge` and `SearchWorkspace` are available.
5. Check the manifest:

   ```bash
   python3 - <<'PY'
   import json, os
   p = os.path.expanduser('~/.qoder/plugins/installed_plugins_v2.json')
   for name, entries in json.load(open(p))['plugins'].items():
       print(name, entries[0].get('version'))
   PY
   ```

   Expect four lines.

6. Confirm the `enabledPlugins` block in `~/.qoder/settings.json` matches
   `settings.template.json`. If an entry is missing, enable the plugin in the UI
   instead of hand-editing if possible.

## What is not portable

- `~/.qoder/plugins/cache/` contains plugin code and binaries. It is versioned,
  large, and update-managed. Reinstall instead of copying.
- Plugin hooks (security scanning, context capture) are registered by the plugin
  and come back with it.
- `known_marketplaces.json` is recreated by Qoder when you open the marketplace.

## Plugin-supplied skills

These are not in `~/.qoder/skills/` because the plugin owns them:

| Plugin | Skill |
| --- | --- |
| Presentations | `pptx` |
| Excel | `excel` |
| Better Harness | `better-harness` |

They appear and disappear with their plugin, so do not copy them into the user
skills folder.
