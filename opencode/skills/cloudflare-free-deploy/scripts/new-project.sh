#!/bin/sh
# Scaffold a Cloudflare project from a bundled template.
set -u

kind="${1:-}"
name="${2:-}"
target="${3:-$PWD}"

if [ -z "$kind" ] || [ -z "$name" ]; then
  echo "usage: new-project.sh <static-site|worker-api|fullstack-d1> <project-name> [target-dir]"
  exit 2
fi

case "$name" in
  *[!a-z0-9-]*|"-"|*-)
    echo "error: '$name' must be lowercase letters, digits and internal hyphens (npm + Worker name rules)"
    exit 2
    ;;
esac

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tpl="$script_dir/../assets/templates/$kind"
[ -d "$tpl" ] || { echo "error: unknown template '$kind'"; exit 2; }

dest="$target/$name"
if [ -e "$dest" ]; then
  echo "error: $dest already exists - pick another name or remove it"
  exit 1
fi

mkdir -p "$dest" || exit 1
cp -R "$tpl/." "$dest/" || exit 1

# Substitute the project name without leaving sed backups behind.
find "$dest" -type f | while IFS= read -r f; do
  sed -e "s/__NAME__/$name/g" "$f" > "$f.tmp" && mv "$f.tmp" "$f"
done

echo "created $dest  (template: $kind)"
echo
echo "next:"
echo "  cd \"$dest\""
echo "  npm install"
echo "  npx wrangler dev        # http://localhost:8787"
echo "  npx wrangler deploy     # prints the live URL"

if [ "$kind" = "fullstack-d1" ]; then
  echo
  echo "then, for the database (free):"
  echo "  npx wrangler d1 create $name-db"
  echo "  # paste the printed database_id into wrangler.jsonc"
  echo "  npx wrangler d1 execute $name-db --local  --file=./schema.sql"
  echo "  npx wrangler d1 execute $name-db --remote --file=./schema.sql"
  echo
  echo "and for bot protection on the form (free, no card):"
  echo "  https://dash.cloudflare.com/?to=/:account/turnstile  -> create widget"
  echo "  npx wrangler secret put TURNSTILE_SECRET"
  echo "  # put the sitekey in .dev.vars locally and in \"vars\" in wrangler.jsonc"
fi
