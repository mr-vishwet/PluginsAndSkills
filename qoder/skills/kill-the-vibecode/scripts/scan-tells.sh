#!/bin/sh
# Scan source for templated "AI slop" tells. Portable BSD/GNU grep.
# Usage: sh scan-tells.sh <file-or-dir> [more...]
# Every hit needs a reason or a fix. Exit 1 if any tell matched.

if [ "$#" -eq 0 ]; then
  echo "usage: sh scan-tells.sh <file-or-dir> [more...]" >&2
  exit 2
fi

STATUS=0

run_group() {
  label="$1"
  pattern="$2"
  shift 2
  hits=$(grep -Ehin --color=never "$pattern" "$@" 2>/dev/null)
  count=$(printf '%s' "$hits" | grep -c . )
  if [ "$count" -gt 0 ]; then
    STATUS=1
    printf '%-26s %s\n' "$label" "$count"
    printf '%s\n' "$hits" | sed 's/^[[:space:]]*/    /' | head -12
  else
    printf '%-26s %s\n' "$label" "0"
  fi
}

TARGETS="$*"

run_group "fonts-and-icons" \
  '\bInter\b|\bGeist\b|Space Grotesk|[Ll]ucide|react-icons|@tabler' $TARGETS

run_group "palette-and-decoration" \
  '#ff6|[Pp]urple|#8B5CF6|#A855F7|#7C3AED|#F4F1EA|#D97757|#0B0B0B|linear-gradient|radial-gradient|backdrop-filter|blur\(|\bnoise|\baurora|\bblob|\borb' \
  $TARGETS

run_group "templated-structure" \
  'rounded-(2|3|xl|2xl|3xl)|shadow-(md|lg|xl)|grid-cols-3|feature-card|testimonial|pricing-tier|bento' \
  $TARGETS

run_group "copy-glyphs" \
  '—|–|✨|🚀|⚡|🔥|→|·.*·|not just|it.s not|unlock|empower|seamless|revolutioniz' \
  $TARGETS

run_group "fake-proof" \
  '5\.0 stars|4\.9|10,000|99\.9|[Tt]rusted by|lorem ipsum|Lorem|placeholder (text|copy|content)|TODO|FIXME|Coming soon' \
  $TARGETS

echo
if [ "$STATUS" -eq 0 ]; then
  echo "clean: no tell patterns matched (behavior and layout still need a human read)"
else
  echo "tells found: fix or justify every hit, then score per section 8 of anti-tells.md"
fi
exit "$STATUS"
