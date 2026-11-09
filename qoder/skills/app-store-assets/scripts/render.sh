#!/usr/bin/env bash
# render.sh — render one theme-driven HTML template to exact store dimensions.
#
# Usage:
#   render.sh INPUT_HTML LOGICAL_W LOGICAL_H OUT_PREFIX [FINAL_W FINAL_H]
#
#   INPUT_HTML   Path to the .html template (relative paths for logo/screenshot resolve next to it).
#   LOGICAL_W/H  CSS pixel size the HTML is authored at (e.g. 1024 500).
#   OUT_PREFIX   Output base path, no extension. Writes OUT_PREFIX.png and OUT_PREFIX.jpg.
#   FINAL_W/H    Optional. Exact pixel size to resample to (e.g. 2048 1000 for a 2x featured graphic,
#                or 5244 2950 for the iOS header). Omit to keep the 2x native render.
#
# The page is captured at 2x device scale for crisp text, then resampled to FINAL_W x FINAL_H when given.
# Requires Google Chrome (or chromium) and macOS `sips`.
set -euo pipefail

if [ "$#" -lt 4 ]; then
  echo "Usage: render.sh INPUT_HTML LOGICAL_W LOGICAL_H OUT_PREFIX [FINAL_W FINAL_H]" >&2
  exit 2
fi

html="$1"; lw="$2"; lh="$3"; out="$4"; fw="${5:-}"; fh="${6:-}"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || CHROME="$(command -v google-chrome || command -v chromium || command -v chromium-browser || true)"
if [ -z "$CHROME" ]; then echo "ERROR: Chrome/Chromium not found." >&2; exit 1; fi

abs_html="$(cd "$(dirname "$html")" && pwd)/$(basename "$html")"
tmp="${TMPDIR:-/tmp}/app-store-asset_$$.png"

"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --window-size="${lw},${lh}" \
  --virtual-time-budget=15000 --default-background-color=00000000 \
  --screenshot="$tmp" "file://${abs_html}" 2>/dev/null

mkdir -p "$(dirname "$out")"
if [ -n "$fw" ] && [ -n "$fh" ]; then
  # sips -z takes HEIGHT WIDTH
  sips -z "$fh" "$fw" "$tmp" --out "${out}.png" >/dev/null
else
  cp "$tmp" "${out}.png"
fi
sips -s format jpeg -s formatOptions 92 "${out}.png" --out "${out}.jpg" >/dev/null
rm -f "$tmp"

dims="$(sips -g pixelWidth -g pixelHeight "${out}.png" 2>/dev/null | awk '/pixel/{printf "%s ", $2}')"
echo "wrote ${out}.png + ${out}.jpg  (${dims}px)"
