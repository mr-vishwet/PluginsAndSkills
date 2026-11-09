#!/bin/bash
# Ralph loop runner — ported from snarktank/ralph (MIT) for this machine.
# Usage: ./ralph.sh [--tool opencode|amp|claude] [--max N]
# Run from the directory containing prd.json, progress.txt and the prompt.

set -e

TOOL="opencode"
MAX_ITERATIONS=10

while [[ $# -gt 0 ]]; do
  case $1 in
    --tool)   TOOL="$2"; shift 2 ;;
    --tool=*) TOOL="${1#*=}"; shift ;;
    --max)    MAX_ITERATIONS="$2"; shift 2 ;;
    --max=*)  MAX_ITERATIONS="${1#*=}"; shift ;;
    *)        [[ "$1" =~ ^[0-9]+$ ]] && MAX_ITERATIONS="$1"; shift ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "$TOOL" in
  opencode|amp|claude) ;;
  *) echo "Error: unknown tool '$TOOL' (opencode|amp|claude)"; exit 1 ;;
esac
PRD_FILE="$SCRIPT_DIR/prd.json"
PROMPT_FILE="$SCRIPT_DIR/iteration-prompt.md"
PROGRESS_FILE="$SCRIPT_DIR/progress.txt"
ARCHIVE_DIR="$SCRIPT_DIR/archive"
LAST_BRANCH_FILE="$SCRIPT_DIR/.last-branch"

command -v jq >/dev/null || { echo "Error: jq is required."; exit 1; }
[ -f "$PRD_FILE" ] || { echo "Error: no prd.json at $SCRIPT_DIR"; exit 1; }
[ -f "$PROMPT_FILE" ] || { echo "Error: no iteration-prompt.md at $SCRIPT_DIR"; exit 1; }

run_tool() {
  case "$TOOL" in
    opencode) opencode run --file "$PROMPT_FILE" "$1" ;;
    amp)      amp --dangerously-allow-all < "$PROMPT_FILE" ;;
    claude)   claude --dangerously-skip-permissions --print < "$PROMPT_FILE" ;;
    *)        echo "Error: unknown tool '$TOOL' (opencode|amp|claude)"; return 1 ;;
  esac
}

CURRENT_BRANCH=$(jq -r '.branchName // empty' "$PRD_FILE")
LAST_BRANCH=$(cat "$LAST_BRANCH_FILE" 2>/dev/null || echo "")

if [ -n "$CURRENT_BRANCH" ] && [ -n "$LAST_BRANCH" ] && [ "$CURRENT_BRANCH" != "$LAST_BRANCH" ]; then
  FOLDER=$(echo "$LAST_BRANCH" | sed 's|^ralph/||')
  ARCHIVE="$ARCHIVE_DIR/$(date +%Y-%m-%d)-$FOLDER"
  mkdir -p "$ARCHIVE"
  [ -f "$PRD_FILE" ] && cp "$PRD_FILE" "$ARCHIVE/"
  [ -f "$PROGRESS_FILE" ] && cp "$PROGRESS_FILE" "$ARCHIVE/"
  echo "Archived previous run ($LAST_BRANCH) to $ARCHIVE"
  printf '# Ralph Progress Log\nStarted: %s\n---\n' "$(date)" > "$PROGRESS_FILE"
fi

if [ -n "$CURRENT_BRANCH" ]; then printf '%s' "$CURRENT_BRANCH" > "$LAST_BRANCH_FILE"; fi

[ -f "$PROGRESS_FILE" ] || printf '# Ralph Progress Log\nStarted: %s\n---\n' "$(date)" > "$PROGRESS_FILE"

echo "Ralph: tool=$TOOL max=$MAX_ITERATIONS branch=$CURRENT_BRANCH"

for i in $(seq 1 "$MAX_ITERATIONS"); do
  echo "=============== iteration $i / $MAX_ITERATIONS ==============="
  OUTPUT=$(run_tool "Implement the next story per the instructions in the attached file." 2>&1 | tee /dev/stderr) || true
  grep -q '<promise>COMPLETE</promise>' <<< "$OUTPUT" && {
    echo "All stories complete at iteration $i."; exit 0; }
done

echo "Stopped at max iterations ($MAX_ITERATIONS). See $PROGRESS_FILE for status."
exit 1
