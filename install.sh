#!/usr/bin/env bash
# Copy the PluginsAndSkills snapshot into the local Qoder and OpenCode config trees.
# Safe by default: existing files are never replaced unless --force is passed.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QODER_HOME="${QODER_HOME:-$HOME/.qoder}"
OPENCODE_HOME="${OPENCODE_HOME:-$HOME/.config/opencode}"
FORCE=0
DRY=0

usage() {
  cat <<'EOF'
Usage: ./install.sh [--dry-run] [--force]

  --dry-run   print the actions without writing to the config trees
  --force     replace files that already exist, after backing them up

Environment:
  QODER_HOME       default: $HOME/.qoder
  OPENCODE_HOME    default: $HOME/.config/opencode
EOF
}

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    --force) FORCE=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $arg" >&2; usage; exit 2 ;;
  esac
done

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$HOME/.pluginsandskills-backup-$STAMP"
STAGE="$(mktemp -d "${TMPDIR:-/tmp}/pluginsandskills.XXXXXX")"
trap 'rm -rf "$STAGE"' EXIT

say() { printf '%s\n' "$*"; }
act() {
  if [ "$DRY" = 1 ]; then
    printf '  would: %s\n' "$*"
  else
    "$@"
  fi
}

# ---------- stage a clean, path-adjusted copy ----------

stage_tree() {
  local src="$1" dst="$2"
  mkdir -p "$dst"
  rsync -a --exclude '.DS_Store' --exclude '__pycache__' --exclude '*.pyc' "$src/" "$dst/"
}

say "Staging from $ROOT"
stage_tree "$ROOT/qoder/skills" "$STAGE/qoder-skills"
stage_tree "$ROOT/opencode/skills" "$STAGE/opencode-skills"
stage_tree "$ROOT/opencode/command" "$STAGE/opencode-command"
stage_tree "$ROOT/opencode/plugin" "$STAGE/opencode-plugin"
stage_tree "$ROOT/opencode/scripts" "$STAGE/opencode-scripts"
cp "$ROOT/qoder/AGENTS.md" "$STAGE/qoder-AGENTS.md"
cp "$ROOT/opencode/AGENTS.md" "$STAGE/opencode-AGENTS.md"
cp "$ROOT/opencode/browser_pref.json" "$STAGE/browser_pref.json"
cp "$ROOT/opencode/opencode.jsonc" "$STAGE/opencode.jsonc"

# Rewrite the source machine's home path only inside the staged copy, so files
# that already exist on this machine are never touched. The snapshot was taken
# on macOS (/Users/appristine) and later on Windows (C:/Users/User).
if [ "$HOME" != "/Users/appristine" ]; then
  say "Rewriting source home paths to $HOME in staged files"
  TARGET_HOME="$HOME" find "$STAGE" -type f \
    \( -name '*.md' -o -name '*.json' -o -name '*.jsonc' -o -name '*.sh' -o -name '*.py' \
       -o -name '*.ts' -o -name '*.js' -o -name '*.cjs' -o -name '*.txt' \) \
    -exec perl -pi -e 's{\Q/Users/appristine\E}{$ENV{TARGET_HOME}}g; s{\QC:/Users/User\E}{$ENV{TARGET_HOME}}g' {} +
fi
find "$STAGE" -name '*.sh' -exec chmod +x {} +

# ---------- copy helpers ----------

copy_dir() {
  local src="$1" dst="$2" label="$3"
  say "$label -> $dst"
  [ "$DRY" = 1 ] || mkdir -p "$dst"
  if [ "$FORCE" = 1 ]; then
    [ "$DRY" = 1 ] || mkdir -p "$BACKUP/$label"
    act rsync -a --backup --backup-dir="$BACKUP/$label" "$src/" "$dst/"
  else
    act rsync -a --ignore-existing "$src/" "$dst/"
  fi
}

copy_file_if_absent() {
  local src="$1" dst="$2" label="$3"
  if [ -e "$dst" ]; then
    say "$label exists, left unchanged: $dst"
  else
    say "$label -> $dst"
    [ "$DRY" = 1 ] || mkdir -p "$(dirname "$dst")"
    act cp "$src" "$dst"
  fi
}

copy_agents() {
  local src="$1" dst="$2" label="$3"
  if [ ! -e "$dst" ]; then
    say "$label -> $dst"
    [ "$DRY" = 1 ] || mkdir -p "$(dirname "$dst")"
    act cp "$src" "$dst"
  elif cmp -s "$src" "$dst"; then
    say "$label already current: $dst"
  elif [ "$FORCE" = 1 ]; then
    say "$label replaced, backup in $BACKUP/$label"
    [ "$DRY" = 1 ] || mkdir -p "$BACKUP/$label" "$(dirname "$dst")"
    act cp "$dst" "$BACKUP/$label/$(basename "$dst")"
    act cp "$src" "$dst"
  else
    say "$label differs, wrote a merge candidate: $dst.pluginsandskills"
    act cp "$src" "$dst.pluginsandskills"
  fi
}

# ---------- Qoder ----------

say ""
say "Qoder: $QODER_HOME"
copy_dir "$STAGE/qoder-skills" "$QODER_HOME/skills" "qoder-skills"
copy_agents "$STAGE/qoder-AGENTS.md" "$QODER_HOME/AGENTS.md" "qoder/AGENTS.md"

if [ ! -e "$QODER_HOME/settings.json" ]; then
  say "settings.json absent, writing from template"
  if [ "$DRY" = 1 ]; then
    say "  would write: $QODER_HOME/settings.json"
  else
    mkdir -p "$QODER_HOME"
    sed "s|<QODER_HOME>|$QODER_HOME|g" "$ROOT/qoder/settings.template.json" > "$QODER_HOME/settings.json"
  fi
else
  say "settings.json exists, wrote a merge preview: $QODER_HOME/settings.pluginsandskills.json"
  if [ "$DRY" = 1 ]; then
    say "  would write: $QODER_HOME/settings.pluginsandskills.json"
  else
    sed "s|<QODER_HOME>|$QODER_HOME|g" "$ROOT/qoder/settings.template.json" > "$QODER_HOME/settings.pluginsandskills.json"
  fi
fi

# ---------- OpenCode ----------

say ""
say "OpenCode: $OPENCODE_HOME"
copy_dir "$STAGE/opencode-skills" "$OPENCODE_HOME/skills" "opencode-skills"
copy_dir "$STAGE/opencode-command" "$OPENCODE_HOME/command" "opencode-command"
copy_dir "$STAGE/opencode-plugin" "$OPENCODE_HOME/plugin" "opencode-plugin"
copy_dir "$STAGE/opencode-scripts" "$OPENCODE_HOME/scripts" "opencode-scripts"
copy_file_if_absent "$STAGE/browser_pref.json" "$OPENCODE_HOME/browser_pref.json" "browser_pref.json"
copy_file_if_absent "$STAGE/opencode.jsonc" "$OPENCODE_HOME/opencode.jsonc" "opencode.jsonc (browser MCP servers)"
copy_agents "$STAGE/opencode-AGENTS.md" "$OPENCODE_HOME/AGENTS.md" "opencode/AGENTS.md"

if [ ! -e "$OPENCODE_HOME/opencode.json" ]; then
  say "opencode.json absent, writing template (keys still need filling)"
  [ "$DRY" = 1 ] || mkdir -p "$OPENCODE_HOME"
  act cp "$ROOT/opencode/opencode.template.json" "$OPENCODE_HOME/opencode.json"
else
  say "opencode.json exists, wrote a template copy: $OPENCODE_HOME/opencode.template.json"
  act cp "$ROOT/opencode/opencode.template.json" "$OPENCODE_HOME/opencode.template.json"
fi

# ---------- next steps ----------

say ""
say "Remaining manual steps:"
say "  1. Install the 4 Qoder plugins (see qoder/plugins/PLUGINS.md)."
say "  2. Add the Lunacy and computer-use MCP servers (see mcp/MCP-CATALOG.md)."
say "  3. Fill the API keys and model keys in $OPENCODE_HOME/opencode.json."
say "  4. Start only the local bridges you use (see opencode/PROVIDERS.md)."
say "  5. Reinstall Free Claude Code if you use the FCC provider (see fcc/README.md)."
say "  6. Run the checks in INSTALL.md section 6."
if [ -d "$BACKUP" ]; then
  say ""
  say "Replaced files were backed up to $BACKUP"
fi
