#!/bin/sh
# Preflight for Cloudflare free-tier deploys: reports env + auth, repairs Node PATH.
set -u

# A session started before Node was installed keeps a stale environment, so
# append the usual install locations rather than trusting the inherited PATH.
for p in "/c/Program Files/nodejs" "/c/Program Files (x86)/nodejs" \
         "$HOME/AppData/Roaming/npm" "/usr/local/bin" "/opt/homebrew/bin"; do
  [ -d "$p" ] && PATH="$PATH:$p"
done
export PATH

show() { printf '%-10s %s\n' "$1" "$2"; }

run_timed() {
  if command -v timeout >/dev/null 2>&1; then
    timeout 60 "$@" 2>&1
  else
    "$@" 2>&1
  fi
}

NODE_PATH_FOUND=$(command -v node || true)
if [ -n "$NODE_PATH_FOUND" ]; then
  NODE_V=$(run_timed node -v | tail -1)
else
  NODE_V="MISSING"
fi

NPM_V=$(command -v npm >/dev/null 2>&1 && run_timed npm -v | tail -1 || echo "MISSING")

# Prefer a project-local wrangler; fall back to a global one. Never auto-download.
WRANGLER="MISSING"
WRANGLER_WHERE=""
if [ -x "./node_modules/.bin/wrangler" ]; then
  WRANGLER_WHERE="./node_modules/.bin/wrangler"
elif command -v wrangler >/dev/null 2>&1; then
  WRANGLER_WHERE=$(command -v wrangler)
fi
if [ -n "$WRANGLER_WHERE" ]; then
  WRANGLER_V=$(run_timed "$WRANGLER_WHERE" --version | tail -1)
  WRANGLER="${WRANGLER_V:-found} ($WRANGLER_WHERE)"
fi

AUTH="n/a (no wrangler yet)"
ACCOUNT=""
if [ "$WRANGLER" != "MISSING" ] && [ -n "$NODE_PATH_FOUND" ]; then
  WHO=$(run_timed npx --no-install wrangler whoami)
  case "$WHO" in
    *"not authenticated"*|*"Not authenticated"*|*"not logged"*|*"Unauthorized"*)
      AUTH="NOT_AUTHENTICATED"
      ;;
    *"Account ID"*)
      AUTH="authenticated"
      ACCOUNT=$(printf '%s' "$WHO" | tr '\n' ' ' | sed 's/.*Account ID[ ]*|[ ]*\([A-Za-z0-9]\{16,\}\).*/\1/')
      ;;
    *) AUTH="unknown - run 'npx wrangler whoami' manually" ;;
  esac
fi

NEXT="ready: npx wrangler dev"
if [ "$NODE_V" = "MISSING" ]; then
  NEXT="install Node: winget install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --silent"
elif [ "$WRANGLER" = "MISSING" ]; then
  NEXT="install wrangler in the project: npm add -D wrangler   (first npx use downloads it)"
elif [ "$AUTH" = "NOT_AUTHENTICATED" ]; then
  NEXT="the USER must run in a browser: npx wrangler login   (no account yet? preview: npx wrangler deploy --temporary)"
elif [ "$AUTH" = "n/a (no wrangler yet)" ]; then
  NEXT="run: npx wrangler whoami"
fi

show "node" "$NODE_V"
show "npm" "$NPM_V"
show "wrangler" "$WRANGLER"
show "auth" "$AUTH"
[ -n "$ACCOUNT" ] && show "account" "$ACCOUNT"
show "cwd" "$PWD"
echo
show "next:" "$NEXT"
