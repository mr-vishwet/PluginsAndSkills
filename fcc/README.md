# Free Claude Code (FCC)

FCC is a local proxy that exposes free model providers (NVIDIA NIM, OpenRouter)
behind one OpenAI-compatible API. It is what the Qoder provider in
`../qoder/settings.template.json` points at.

Snapshot facts (2026-11-09):

| Item | Value |
| --- | --- |
| Package | `free-claude-code` 6.19.2, installed with `uv tool install` |
| Install root | `%APPDATA%\uv\tools\free-claude-code` (Windows) / `~/.local/share/uv/tools/...` (macOS, Linux) |
| Data home | `~/.fcc` |
| API | `http://127.0.0.1:8082/v1` |
| Admin UI | `http://127.0.0.1:8082/admin` (local only) |
| Local API key | `freecc` (fixed dummy value, not a secret) |
| Default model here | `nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b` |
| Fallback | `open_router/openrouter/free` |

## Install

```bash
uv tool install --force --refresh-package free-claude-code free-claude-code
uv tool update-shell
```

The CLI installs these entries: `fcc-server`, `fcc-desktop`, `fcc-doctor`,
`fcc-claude`, `fcc-codex`, `fcc-opencode`, `fcc-agy`, `fcc-aider`, `fcc-cline`,
`fcc-grok`, plus update helpers. `fcc-desktop` is the tray app; it starts the
server for you.

## Configure

Settings live in `~/.fcc/.env` and the SQLite database `~/.fcc/fcc.db`. Edit
them through the admin UI where possible. Shape of the env file is in
[env.example](env.example); the provider API keys are the only secrets.

## Use from Qoder

Qoder reaches FCC as a custom OpenAI-compatible provider. That block is already
in `../qoder/settings.template.json` under `providers`. It is a local provider,
so `apiKey` stays `freecc`.

The provider ID (`qoder-custom-<uuid>`) is generated per registration. Keep the
snapshot ID if you are restoring in place; Qoder creates a new one if you add
the provider from the UI.

## Use from Antigravity CLI

FCC rewrites the Antigravity CLI settings so the CLI routes through the proxy.
The snapshot of that file is
[antigravity-integration.template.json](antigravity-integration.template.json);
the live copy is `~/.gemini/antigravity-cli/settings.json`. Re-running FCC's
Antigravity integration is safer than editing that file by hand.

## Use from OpenCode

`fcc-opencode` starts OpenCode with a process-local provider:

- provider ID: `free-claude-code`
- API key env var: `FCC_OPENCODE_API_KEY` (set by the launcher)
- model default: `free-claude-code/<default model id>`

Nothing is written to `~/.config/opencode/opencode.json`; the override exists
only for that process, so the `opencode.template.json` snapshot stays FCC-free.

## Verify

```bash
fcc-doctor
curl -s http://127.0.0.1:8082/v1/models -H "Authorization: Bearer freecc"
```

`fcc-doctor` checks the port, database, browser access to the admin UI, and each
provider key.

## Not in this snapshot

`~/.fcc/fcc.db`, `*.log`, `*.lock`, and the real `.env` stay out of the repo.
They hold runtime state and provider keys. Rebuild them by signing in to the
admin UI and pasting the keys from your password manager.
