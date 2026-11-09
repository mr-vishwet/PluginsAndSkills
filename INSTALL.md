# Install on another computer

The snapshot was refreshed on Windows; the installer is bash and also runs on
macOS and Linux (git-bash on Windows works if `rsync` and `perl` are on `PATH`).
Paths below use `~`, which is `C:/Users/<name>` on Windows and `/Users/<name>`
on macOS.

## 0. Prerequisites

Install these first, then reopen the terminal:

| Tool | Why | Check |
| --- | --- | --- |
| Qoder Desktop | Runs the Qoder skills and plugins | `ls ~/.qoder` |
| OpenCode | Runs the OpenCode skills and providers | `opencode --version` |
| Node.js 20 or newer | GSD tools, brand-flow, OpenCode plugins | `node -v` |
| Python 3.11 or newer | docs-skill, lily, app-demo-recorder | `python3 -V` |
| Git and jq | GSD, Ralph, git-to-obsidian | `git --version && jq --version` |
| Google Chrome | app-store-assets, browser work | Chrome installed |
| Android platform tools | app-demo-recorder only | `adb version` |
| `uv` | Free Claude Code install and updates | `uv --version` |
| Lunacy | Optional, for the Lunacy MCP | <https://lunacy.docs.icons8.com/> |
| `wrangler` | `cloudflare-free-deploy` only | `npx wrangler --version` |

## 1. Copy the folder

Copy `PluginsAndSkills` anywhere on the new machine, then:

```bash
cd PluginsAndSkills
chmod +x install.sh
./install.sh --dry-run
```

The dry run prints every copy and rewrite. If the paths look right:

```bash
./install.sh
```

What the installer does:

- Copies `qoder/skills/*` to `~/.qoder/skills/`, skipping any skill that already exists.
- Copies `opencode/skills/*`, `opencode/command/*`, and `opencode/plugin/*` to the matching folders.
- Copies both `AGENTS.md` files. If a target file already exists it writes
  `AGENTS.md.pluginsandskills` next to it instead of overwriting.
- Rewrites `/Users/appristine` and `C:/Users/User` to the target home directory
  in every copied text file.
- Writes `opencode/opencode.template.json` to `~/.config/opencode/opencode.json`
  only if no config exists. Otherwise it writes `opencode.template.json` alongside.
- Prints the remaining manual steps.

Nothing is overwritten without `--force`. With `--force`, existing files are
first copied to `~/.pluginsandskills-backup-<timestamp>/`.

Custom homes:

```bash
QODER_HOME=~/work/.qoder OPENCODE_HOME=~/work/opencode ./install.sh
```

## 2. Qoder plugins

Open Qoder Desktop, go to the plugin or extension marketplace, and install these
by name. Versions are from the snapshot; take the current version.

1. Presentations
2. Excel (`office-excel`)
3. Better Harness
4. Qoder Context, usually bundled and hidden

After install, verify the same four entries appear in
`~/.qoder/plugins/installed_plugins_v2.json`. Detail and what each one adds:
[qoder/plugins/PLUGINS.md](qoder/plugins/PLUGINS.md).

## 3. MCP servers

**Lunacy** needs the desktop app. **Computer Use** needs the launcher under
`~/.qoder/bin/qoder-computer-use/`; on macOS grant Accessibility and Screen
Recording permission to Qoder.

Use Qoder Settings, MCP Servers, and add the two custom servers, or merge the
`mcpServers` block from `qoder/settings.template.json` into `~/.qoder/settings.json`
after replacing `<QODER_HOME>` with the real path. Do not replace the whole
settings file if the new machine already has its own settings.

Tool counts and every plugin-provided server are documented in
[mcp/MCP-CATALOG.md](mcp/MCP-CATALOG.md).

## 4. Skill dependencies

| Skill | Command or edit |
| --- | --- |
| `docs-skill` | `python3 -m pip install python-docx reportlab` (Pillow optional) |
| `app-demo-recorder` | Rebuild the pinned venv as described in its `SKILL.md`; then run its `doctor` check with `adb` and `ffmpeg` available |
| `cloudflare-free-deploy` | `npm i -g wrangler`, then `wrangler login` |
| `ralph` | Install `jq` if missing; keep `opencode` on `PATH` |
| `gsd` | Node must run `node ~/.qoder/skills/gsd/get-shit-done/bin/gsd-tools.cjs`. No npm install needed unless the skill says so |
| `lily-autoresearch` | Create `.envs/lily.env` at the project root with `VAULT_PATH=/path/to/vault` |
| `git-to-obsidian` | Edit the vault path near the top of `~/.qoder/skills/git-to-obsidian/SKILL.md` |
| `app-store-assets` | Chrome, plus macOS `sips` on a Mac |
| `rea` | Register an REA MCP server if you want tool-backed reverse engineering |

## 5. OpenCode

1. Copy the template:

   ```bash
   cp opencode/opencode.template.json ~/.config/opencode/opencode.json
   chmod 600 ~/.config/opencode/opencode.json
   ```

   If the file already exists, merge the `provider`, `skills`, and `plugin`
   sections instead of replacing it.

2. Set the keys for the three providers in the template:

   - `ox-alpha` — local service on port 3900, dummy key `oxalpha-chat`
   - `omniroute` — replace `YOUR_OMNIROUTE_API_KEY`, local service on port 20128
   - `explabs` — export `EXPLABS_API_KEY`; the config reads it with `{env:...}`

   Detail in [opencode/PROVIDERS.md](opencode/PROVIDERS.md).

3. The npm plugin `@dietrichgebert/ponytail` is declared in the `plugin` array and
   installs when OpenCode starts. The two local plugins are already copied.

4. The bridge scripts under `opencode/scripts/` are kept for reference. The
   current provider list no longer starts them; only run the ones you add back
   to `opencode.json`.

5. Perplexity cookies: copy `opencode/pplx-meta.template.json` to
   `~/.config/opencode/pplx-meta.json`, then fill the cookie and account fields
   from a logged-in Perplexity session. Export `PERPLEXITY_SESSION_TOKEN` before
   starting `pplx-direct.py`.

6. Browser preference is copied as `~/.config/opencode/browser_pref.json`. Edit
   it if the new machine has a different default browser.

## 6. Free Claude Code

FCC supplies the `freecc` provider in `qoder/settings.template.json`.

```bash
uv tool install --force --refresh-package free-claude-code free-claude-code
uv tool update-shell
fcc-desktop        # starts the tray app and the proxy on 127.0.0.1:8082
```

Open `http://127.0.0.1:8082/admin`, add the provider keys, and pick the default
model. Then run `fcc-doctor`. Full notes: [fcc/README.md](fcc/README.md).

## 7. Verify

Run these checks on the new machine.

```bash
# Skills are present and readable
find ~/.qoder/skills -maxdepth 2 -name SKILL.md | wc -l            # expect 20
find ~/.config/opencode/skills -maxdepth 2 -name SKILL.md | wc -l  # expect 20

# No stale source-home paths in copied skills
grep -rl "/Users/appristine" ~/.qoder/skills ~/.config/opencode | grep -v __pycache__
grep -rl "C:/Users/User" ~/.qoder/skills ~/.config/opencode | grep -v __pycache__

# Configs parse
python3 -m json.tool ~/.config/opencode/opencode.json > /dev/null && echo opencode-ok
python3 -m json.tool ~/.qoder/settings.json > /dev/null && echo qoder-ok

# Plugin manifest lists four plugins
python3 -c "import json;print(len(json.load(open('$HOME/.qoder/plugins/installed_plugins_v2.json'))['plugins']))"

# FCC is up and can list models
curl -s http://127.0.0.1:8082/v1/models -H "Authorization: Bearer freecc"
```

The grep checks only print paths if the installer missed a rewrite.

Then open a fresh Qoder session and a fresh OpenCode session. Ask each to list
its skills and MCP tools. A skill that does not appear is usually a missing
frontmatter block or a folder that is nested one level too deep.

## 8. Known drift

- Plugin and MCP tool counts change with app updates.
- The `computer-use` launcher and Lunacy paths differ per OS and install prefix.
- `kaggle-proxy.py` points at an ephemeral `trycloudflare.com` host and will need
  the current tunnel.
- The bundled skills visible inside Qoder, such as canvas, sites, QMind, Repo Wiki,
  and collaboration, are not in this export. They ship with the app.
