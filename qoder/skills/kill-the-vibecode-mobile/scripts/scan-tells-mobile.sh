#!/bin/sh
# Mobile tell scanner: greps high-signal AI-slop tells in app source.
# Portable POSIX sh + BSD/GNU grep -E. No lookaheads, no PCRE.
# Usage: sh scan-tells-mobile.sh <file-or-dir> [more...]
# Exit 1 if any tell matched, 0 if clean, 2 on bad usage.

if [ "$#" -eq 0 ]; then
  echo "usage: sh scan-tells-mobile.sh <file-or-dir> [more...]" >&2
  exit 2
fi

STATUS=0

run_group() {
  label="$1"
  pattern="$2"
  shift 2
  hits=$(grep -rEhin --include='*.dart' --include='*.swift' --include='*.kt' \
    --include='*.java' --include='*.js' --include='*.jsx' --include='*.ts' \
    --include='*.tsx' --include='*.css' --include='*.html' --include='*.vue' \
    --include='*.rb' --color=never "$pattern" "$@" 2>/dev/null)
  if [ -n "$hits" ]; then
    count=$(printf '%s\n' "$hits" | grep -c .)
    STATUS=1
    printf '%-24s %s\n' "$label" "$count"
    printf '%s\n' "$hits" | sed 's/^[[:space:]]*/    /' | head -12
    [ "$count" -gt 12 ] && printf '    ... and %s more\n' "$((count - 12))"
  else
    printf '%-24s %s\n' "$label" "0"
  fi
}

run_group "framework-defaults" \
  '\bInter\b|\bGeist\b|Space Grotesk|\bPoppins\b|\bManrope\b|google_fonts|useMaterial3: *false|Colors\.purple|Colors\.indigo' \
  "$@"

run_group "slop-palette" \
  '#[Ff]4[Ff]1[Ee][Aa]|#D97757|#0[Bb]0[Bb]0[Bb]|#6C5CE7|#8B5CF6|#A855F7|#7C3AED|LinearGradient\(colors: *\[[^]]*Colors\.(purple|indigo)|backdrop-filter|BackdropFilter\(|BlurStyle\.|Colors\.black' \
  "$@"

run_group "templated-structure" \
  'BorderRadius\.circular\(([1-9][0-9]{2,}|[5-9][0-9])\)|elevation: *([4-9]|[1-9][0-9])|blurRadius: *([2-9][0-9])|SizedBox\(height: *[1-9][0-9]{2,}|SizedBox\(width: *[1-9][0-9]{2,}|fontSize: *[3-9][0-9](\.[0-9]+)?,' \
  "$@"

run_group "copy-glyphs" \
  '—|–|✨|🚀|⚡|🔥|→|·.*·|not just|it.s not|[Uu]nlock|[Ee]mpower|[Ss]eamless|revolutioniz|Get started|Welcome to' \
  "$@"

run_group "fake-proof" \
  '4\.9|5\.0 stars|10,000|99\.9|[Tt]rusted by|[Oo]ver [0-9]+(,[0-9]{3})\+? (users|downloads|ratings)|lorem ipsum|Lorem|placeholder (text|copy|content)|TODO|FIXME|Coming soon|StarRating|rating: *[0-4]\.[5-9]' \
  "$@"

run_group "platform-correctness" \
  'width: *375|height: *[1-9][0-9]{3}|MediaQuery[^;]*(375|414)|100vh|100vw|minWidth: *[123][0-9],|minHeight: *[123][0-9],|resizeToAvoidBottomInset: *false' \
  "$@"

echo
echo "grep cannot see these; each still needs a device or test check:"
echo "  back gesture intact  |  44pt or 48dp targets  |  pressed state on pointer-down"
echo "  safe area used       |  both light and dark   |  no overflow at 200% text scale"
echo "  keyboard reachable   |  loading, empty, error, offline, denied states present"
echo "  one icon family      |  no invented data       |  tested on real hardware"
echo

if [ "$STATUS" -eq 0 ]; then
  echo "clean: no tell patterns matched (the device and state checks above still apply)"
else
  echo "tells found: fix or justify every hit, then score per section 8 of anti-tells-mobile.md"
fi
exit "$STATUS"
