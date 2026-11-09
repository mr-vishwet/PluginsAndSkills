# MCP catalog

Everything exposed to the agent in this setup, where it comes from, and what it
needs. Tool counts are from 2026-11-09 and will drift with plugin updates.

## How MCP is wired

Qoder has three sources of MCP servers:

1. **Custom servers** in `~/.qoder/settings.json` under `mcpServers`.
2. **Plugin servers**, registered automatically by an installed plugin.
3. **App-managed servers**, shipped inside Qoder Desktop and not configurable
   from this export.

OpenCode has its own MCP configuration. `opencode.json` has an empty `mcp` block,
while `opencode.jsonc` declares six browser-related servers. Which file OpenCode
loads can depend on version precedence, so treat the jsonc server list as the
intended configuration and merge it into `opencode.json` if the browser tools do
not appear. See the OpenCode section below.

Free Claude Code is not an MCP server. It is an OpenAI-compatible model proxy on
`127.0.0.1:8082`, documented in [../fcc/README.md](../fcc/README.md).

## Registered servers

| Server | Display | Source | Transport | Tools | Auth | Requirement |
| --- | --- | --- | --- | --- | --- | --- |
| `Lunacy` | Lunacy | custom, `settings.json` | stdio | 22 | none | Lunacy desktop app |
| `computer-use` | computer-use | custom, `settings.json` | stdio | 11 | none | `~/.qoder/bin/qoder-computer-use/`, macOS Accessibility and Screen Recording permission |
| `plugin:Presentations:office` | Presentations / office | plugin `Presentations@qoder-marketplace` | stdio | 11 | none | None |
| `plugin:office-excel:office-excel` | Excel / office-excel | plugin `office-excel@qoder-marketplace` | stdio | varies | none | None |
| `plugin:qoder-context:qoder-context` | qoder-context | plugin `qoder-context@qoderapp-bundler` | stdio | 2 | none | None |

## Bundled servers

These appear as plugin MCP providers without an entry in
`installed_plugins_v2.json`.

| Server | Display | Transport | Tools | Requirement |
| --- | --- | --- | --- | --- |
| `plugin:knowledge-center:repowiki` | knowledge-center / repowiki | in-process | 2 | Repository Wiki generated in Qoder |
| `plugin:sites:qoder_sites` | sites | in-process | 47 | Signed-in Qoder account for publishing |
| `plugin:qoder-qmind:qoder-qmind` | qoder-qmind | stdio | 9 | QMind notebooks in the account |

## App-managed servers

These appear in the tool namespace but not in `settings.json` or the plugin
manifest. They come with the desktop app.

| Namespace | Tools | What it does |
| --- | --- | --- |
| `browser-use` | 16 | Navigate, snapshot, click, fill, upload, read console and network |
| `builtin` | 7 | Chat session listing, forking, messaging, scheduling |
| `extension-market` | 2 | Search and install Qoder extensions |
| `node-repl` | 5 | Persistent Node.js REPL |

`computer-use` also appears in the tool namespace because it is a registered
server; it is counted once in the table above.

## OpenCode MCP servers

Declared in `opencode/opencode.jsonc`. These are separate from Qoder's servers
and follow a different schema: `type` is `local` or `remote`, and local commands
are arrays.

| Server | Type | Command or URL | Enabled | Needs |
| --- | --- | --- | --- | --- |
| `composio` | remote | `https://connect.composio.dev/mcp` | default | Composio account and OAuth on first use |
| `firefox-devtools` | local | `npx -y @mozilla/firefox-devtools-mcp --connect-existing --marionette-port 2828` | yes | Firefox running with Marionette on port 2828 |
| `playwright` | local | `npx -y @playwright/mcp@latest` | yes | Node, Playwright browser download |
| `playwright-chrome` | local | `npx -y @playwright/mcp@latest --browser chrome --user-data-dir <chrome profile>` | yes | Chrome installed, profile path updated |
| `playwright-firefox` | local | `npx -y @playwright/mcp@latest --browser firefox` | no | Firefox for Playwright |
| `playwright-headless` | local | `npx -y @playwright/mcp@latest --headless` | yes | Node |

The Playwright Chrome entry points at
`C:/Users/User/AppData/Local/Google/Chrome/User Data` on this machine. Change it
to the Chrome profile on the new machine, or drop that flag to use a clean
Playwright profile.

The browser preference in `opencode/browser_pref.json` is `firefox`, remembered.
OpenCode's `AGENTS.md` maps that preference to the matching `playwright_*` tools,
so keep the two consistent.

## Custom server configuration

From `qoder/settings.template.json`, with `<QODER_HOME>` replaced:

```json
{
  "mcpServers": {
    "Lunacy": {
      "command": "C:/Program Files/Lunacy/Lunacy.exe",
      "args": ["-mcp"]
    },
    "computer-use": {
      "command": "<QODER_HOME>/bin/qoder-computer-use/QoderComputerUse.exe",
      "args": ["mcp"]
    }
  }
}
```

The `computer-use` entry is normally created by installing the plugin or by the
app; add it by hand only if the server is missing. On macOS the Lunacy command is
`/Applications/Lunacy.app/Contents/MacOS/Lunacy`.

To add another stdio server:

```json
"my-server": {
  "command": "/absolute/path/to/launcher",
  "args": ["--mcp"],
  "env": { "SOME_VAR": "value" }
}
```

Use absolute paths. Qoder does not expand `~` or shell variables in `command`.

## Server notes

### Lunacy

A 22-tool design server: read layers, create and update them, export, screenshot,
undo and redo. Requires the Lunacy desktop app to be running with a document open
for most operations. The command is the app binary itself, launched with `-mcp`.

### computer-use

Controls desktop apps through the accessibility tree and screenshots. Eleven
tools: list apps, read app state, click, drag, scroll, type, paste, select text,
set a value, press a key, and run a secondary accessibility action.

Permissions needed on macOS: System Settings, Privacy and Security, Accessibility
and Screen Recording, both enabled for Qoder. Without them the server starts but
`get_app_state` fails.

### Repo Wiki

Two tools: `ListWiki` and `ReadWiki`. They only read a Wiki that Qoder has already
generated for the current repository. `sourceRef` comes from a Wiki reference in
the session.

### Presentations office

Eleven tools for PPTX work: `begin_deck`, `put_page`, `read_slide`, `apply_ops`,
`execute_slide_script`, `check_deck`, `save_document`, and supporting reads. Paths
must be absolute and inside an authorized workspace folder.

### Excel office-excel

The spreadsheet counterpart to the Presentations server. Same plugin runtime
shape: `${QODER_NODE_RUNTIME}` runs `runtime/server.cjs` from the plugin root.

### Qoder Context

Supplies `SearchKnowledge` and `SearchWorkspace`. These are the codebase knowledge
retrieval tools used in ordinary coding sessions. If they are missing, the plugin
is disabled.

### Sites

The largest server at 47 tools: prepare a draft, publish, resume, manage access,
database migrations, storage objects, secrets metadata, deployments, releases, and
analytics. It is in-process and tied to the signed-in Qoder account. Publishing
writes to cloud resources, so treat those tools as external side effects.

### QMind

Nine tools for notebooks and sources: retrieve, list notebooks and sources, read
a source, add a URL or local file, delete, create a directory, and move a leaf
document. Retrieval is scoped to the current chat and account permissions.

## Verify

In Qoder, open the MCP panel and check that each expected server is enabled and
ready. In a session, ask the agent to list its MCP tools.

Programmatically, the in-app MCP control plane can list servers and tools. The
counts in this file can be checked with the discovery tools available to the
agent, but those tools are session-scoped and are not a portable CLI.

## Security

- None of the custom servers use OAuth or API keys. Access is by local process
  and OS permissions.
- Sites and QMind inherit the Qoder account session. Do not copy session files
  between machines.
- Do not add a server from an untrusted marketplace without reading its command.
  A stdio MCP server is arbitrary code running as your user.
