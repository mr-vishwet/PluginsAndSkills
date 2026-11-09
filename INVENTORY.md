# Inventory

Snapshot refreshed 2026-11-09 from `C:/Users/User`.

## Counts

| Category | Count | Location on the source machine |
| --- | --- | --- |
| Qoder user skills | 20 | `~/.qoder/skills/` |
| OpenCode user skills | 20 | `~/.config/opencode/skills/` |
| Installed Qoder plugins | 4 | `~/.qoder/plugins/installed_plugins_v2.json` |
| Registered MCP servers | 5 custom or plugin-provided | `~/.qoder/settings.json` plus plugin manifests |
| Bundled MCP servers | 3 | shipped with Qoder Desktop |
| App-managed MCP servers | 4 | shipped with Qoder Desktop |
| OpenCode MCP declarations | 6 (5 enabled) | `~/.config/opencode/opencode.jsonc` |
| OpenCode providers | 3 | `~/.config/opencode/opencode.json` |
| OpenCode local plugins | 2 | `~/.config/opencode/plugin/` |
| OpenCode commands | 2 | `~/.config/opencode/command/` |
| FCC proxy providers | 2 | `~/.fcc/.env` |

## Qoder user skills

All copied under `qoder/skills/`. Each folder keeps its own `SKILL.md` and any
scripts, references, and templates.

| Skill | What it does | Runtime needs | Notes |
| --- | --- | --- | --- |
| `app-demo-recorder` | Records an Android walkthrough, de-brands it, adds chapter captions, writes a timecoded session doc | `adb`, `ffmpeg`, Pillow, a pinned `.venv` in the tool | Was a symlink to `Desktop/Vishwet/Experiments/ApkSession/tool`; copied with real contents. Rebuild the venv before first use. |
| `app-store-assets` | Generates Play and App Store banners at exact store sizes | Google Chrome or Chromium, macOS `sips` | HTML templates and `render.sh` included |
| `brand-flow` | Extracts a live site's brand tokens and page flow, then generates screens | Node, Python 3, browser evaluate access | `scripts/extract-brand.js`, `page-flow.py`, `gen-screen.py` |
| `cloudflare-free-deploy` | Scaffolds and deploys Cloudflare Workers, static sites, D1, KV, R2, Queues on the free plan | `wrangler`, Node | New in this snapshot |
| `coding-decisions` | Default rules for code changes: minimal comments, reuse, scope discipline, honest verification | None | Referenced by the global rules |
| `daily-summary` | Daily plan or recap in plain language, grouped by theme | None | |
| `docs-skill` | Builds DOCX and PDF from Markdown with cover, TOC, styled tables, footers | `python-docx`, `reportlab`, optional Pillow | Brand header images in `assets/` |
| `git-to-obsidian` | Maps git changes into the right Obsidian vault notes | Git, access to the vault | Hardcoded vault path, see below |
| `gsd` | Spec-driven planning and execution system | Node, Git | Ships 12 agents and the full workflow set |
| `gsd-map-codebase` | Parallel codebase mapping entry point | Node, Git | Standalone front end for a GSD workflow |
| `gsd-plan-milestone-gaps` | Turns audit gaps into closure phases | Node, Git | Standalone front end |
| `gsd-project-researcher` | Researches domain and ecosystem for a new project | Node, Git, web access | Spawned by `/gsd new-project` |
| `gsd-verify-work` | Conversational UAT for built features | Node, Git | Standalone front end |
| `kill-the-vibecode` | Web UI review and build rules that remove templated AI tells | Bash for `scan-tells.sh`, browser for verification | Loaded by the global rules for web work |
| `kill-the-vibecode-mobile` | The same, for Flutter, SwiftUI, Compose, React Native, and mobile web | Bash for `scan-tells-mobile.sh` | Loaded by the global rules for app UI work |
| `lily-autoresearch` | Overnight experiment loop scored against an Obsidian vault | Python 3, Obsidian vault | Vault path comes from `.envs/lily.env` |
| `mobile-app-ui-design` | Mobile UI/UX guidance with Apple HIG, onboarding, and industry references | None | Reference-only skill |
| `ponytail` | Engineering standards applied to every request | None | Referenced by both `AGENTS.md` files |
| `ralph` | Autonomous PRD to `prd.json` loop, one story per iteration | `jq`, Git, `opencode` or another agent CLI | `ralph.sh` included |
| `rea` | Reverse-engineering workflows and evidence handling | An external REA MCP server for tool-backed work | The skill supplies instructions only, it does not register the MCP |

The five `gsd-*` entries overlap with the sub-skills inside `gsd/skills/`. Keep
both only if you use the standalone slash commands.

## OpenCode user skills

Copied under `opencode/skills/`. This machine keeps the full 20-skill set in
OpenCode as well as Qoder, so `opencode/opencode.json` points `skills.paths` at
`~/.config/opencode/skills`.

A handful of files differ between the two copies because each app rewrote the
bundle root path: `gsd/SKILL.md`, the GSD agents, workflows, sub-skills, and
`kill-the-vibecode`/`mobile` run paths. Copying both sets is harmless. If you
keep only one, keep the Qoder copies and point OpenCode's `skills.paths` at
`~/.qoder/skills`.

## Qoder plugins

Full detail and reinstall steps in [qoder/plugins/PLUGINS.md](qoder/plugins/PLUGINS.md).

| Plugin ID | Version | Adds |
| --- | --- | --- |
| `Presentations@qoder-marketplace` | 0.1.4 | PPTX creation and editing skill plus the `office` MCP server |
| `office-excel@qoder-marketplace` | 0.1.2 | Excel skill plus the `office-excel` MCP server |
| `better-harness@qoder-marketplace` | 0.2.21 | Engineering workflow skill, references, case studies |
| `qoder-context@qoderapp-bundler` | 1.0.91.b22f2d0a | Hidden plugin providing codebase knowledge and workspace search |

Bundled providers that ship with the app rather than this manifest:
`knowledge-center` (Repo Wiki and QMind), `sites`, and the built-in Qoder tools.

## MCP servers

Full catalog, transports, and tool counts in [mcp/MCP-CATALOG.md](mcp/MCP-CATALOG.md).

| Server | Source | Transport | Tools |
| --- | --- | --- | --- |
| `Lunacy` | custom | stdio | 22 |
| `computer-use` | custom | stdio | 11 |
| `plugin:Presentations:office` | plugin | stdio | 11 |
| `plugin:office-excel:office-excel` | plugin | stdio | varies |
| `plugin:qoder-context:qoder-context` | plugin | stdio | 2 |
| `plugin:knowledge-center:repowiki` | bundled | in-process | 2 |
| `plugin:sites:qoder_sites` | bundled | in-process | 47 |
| `plugin:qoder-qmind:qoder-qmind` | bundled | stdio | 9 |
| `browser-use` | app-managed | internal | 16 |
| `builtin` | app-managed | internal | 7 |
| `extension-market` | app-managed | internal | 2 |
| `node-repl` | app-managed | internal | 5 |

OpenCode declares six more servers in `opencode.jsonc`: Composio, Firefox
DevTools, Playwright, Playwright Chrome, Playwright Firefox (disabled), and
Playwright headless. Detail in [opencode/PROVIDERS.md](opencode/PROVIDERS.md#mcp-servers).

## Config files

| Export file | Source | Sanitized |
| --- | --- | --- |
| `qoder/AGENTS.md` | `~/.qoder/AGENTS.md` | No secrets |
| `qoder/settings.template.json` | `~/.qoder/settings.json` | Paths replaced with `<QODER_HOME>`, FCC keys are the fixed local value |
| `qoder/plugins/installed_plugins_v2.template.json` | `~/.qoder/plugins/installed_plugins_v2.json` | Timestamps and absolute paths removed or templated |
| `opencode/AGENTS.md` | `~/.config/opencode/AGENTS.md` | No secrets |
| `opencode/opencode.template.json` | `~/.config/opencode/opencode.json` | Remote keys are env references or placeholders |
| `opencode/opencode.jsonc` | `~/.config/opencode/opencode.jsonc` | No secrets, one machine path rewritten on install |
| `opencode/browser_pref.json` | `~/.config/opencode/browser_pref.json` | No secrets |
| `opencode/pplx-meta.template.json` | Shape of `pplx-meta.json` | Cookie and account values replaced |
| `opencode/scripts/*.py` | `~/.config/opencode/scripts/*.py` | Secrets read at runtime, none embedded |
| `fcc/env.example` | Shape of `~/.fcc/.env` | Provider keys replaced |
| `fcc/antigravity-integration.template.json` | `~/.fcc/antigravity-integration.json` | Home path replaced |

## Machine-specific paths

Update these after copying. `install.sh` rewrites `/Users/appristine` and
`C:/Users/User` to the target home directory, but it cannot know about vaults or
external services.

| Where | Path or value | Action |
| --- | --- | --- |
| `qoder/skills/git-to-obsidian/SKILL.md` | `/Users/appristine/Desktop/Vishwet/Experiments/ObsessionWithObsedian` | Point at the vault on the new machine |
| `qoder/skills/lily-autoresearch` | Vault path in `.envs/lily.env` | Create the env file with the new vault path |
| Both `AGENTS.md` | Absolute skill paths under the Qoder or OpenCode home | Rewritten by the installer if the username differs |
| `qoder/settings.template.json` | `computer-use` launcher path | Replace `<QODER_HOME>` with the real Qoder home |
| `qoder/settings.template.json` | Lunacy path is `C:/Program Files/Lunacy/Lunacy.exe` | Change for the target install prefix |
| `qoder/plugins/*.template.json` | Plugin install paths | Reinstalled plugins get new paths |
| `opencode/opencode.template.json` | `OX_ALPHA` uses a local dummy key; `omniroute` keeps `YOUR_OMNIROUTE_API_KEY`; `explabs` reads `EXPLABS_API_KEY` | Set the env var and the OmniRoute key |
| `opencode/scripts/omnirush-bridge.py` | `~/.omnirush/auth.json` | Run the Omnirush login flow first (script is legacy, no longer in the provider list) |
| `opencode/scripts/pplx-direct.py` | `PERPLEXITY_SESSION_TOKEN` and `pplx-meta.json` | Supply a fresh session cookie (script retained, provider removed) |
| `opencode/scripts/kaggle-proxy.py` | Ephemeral `trycloudflare.com` upstream | Replace with the current tunnel host |
| `opencode/opencode.jsonc` | Playwright Chrome `--user-data-dir` points at the Chrome profile | Point at the Chrome profile on the new machine |
| `fcc/env.example` | `NVIDIA_NIM_API_KEY`, `OPENROUTER_API_KEY` | Fill from the FCC admin UI, not by hand |
| `fcc/antigravity-integration.template.json` | `settings_path` | Re-run FCC's Antigravity integration instead |
| `qoder/skills/app-demo-recorder` | Pinned `.venv` inside the tool | Rebuild it |
| `qoder/skills/docs-skill` | Optional brand assets in `assets/` | Add or remove per project |

## Not copied

`~/.qoder/.auth/`, `mcp-router.json` (contains a live router key), `ipc/`,
`logs/`, `memory/`, `projects/`, `file-history/`, `tasks/`, `tmp/`, `venvs/`,
`plugins/cache/`, `shell-snapshots/`, `skill-usage.json`, `umid-cache.json`,
`~/.fcc/.env`, `~/.fcc/fcc.db`, `~/.fcc/logs/`, `~/.fcc/*.lock`,
`~/.config/opencode/pplx-meta.json`, `~/.config/opencode/service.json`,
`kaggle-proxy.log`, `node_modules/`, `~/.config/opencode/opencode.json.bak*`
(older configs may contain keys), and any `.venv`.

These are runtime state, credentials, or reinstallable artifacts.
