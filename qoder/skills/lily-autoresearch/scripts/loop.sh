#!/usr/bin/env bash
# loop.sh -- the overnight driver. Same shape as karpathy/autoresearch's experiment
# loop, on hardware with no GPU: propose -> measure -> keep/discard -> log -> advance.
#
# Requires both --count and --deadline. Upstream pairs "NEVER STOP" with a fixed 5-minute
# budget and a bounded search space; the caps are what make the autonomy safe, so copy
# the caps.
set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT=${PROJECT_DIR:-$PWD}
STATE_DIR="$PROJECT/.docs/autoresearch"
REVIEW_DIR="$PROJECT/.docs/notes/autoresearch-review"
VAULT=${VAULT_PATH:-}
EVALSET=""
COUNT=0
DEADLINE=""
BUDGET_MIN=1.0
MIN_DELTA=0.001
STRATEGY=mutate
SEED=""
MIN_DISK_GB=2
CONFIRM=no
PRIMARY=hit_rate@5
COVERAGE_SWEEP=no
COVERAGE_MAX_CTX=8500

while [ $# -gt 0 ]; do
  case "$1" in
    --vault) VAULT=$2; shift 2;;
    --eval) EVALSET=$2; shift 2;;
    --count) COUNT=$2; shift 2;;
    --deadline) DEADLINE=$2; shift 2;;
    --budget-min) BUDGET_MIN=$2; shift 2;;
    --min-delta) MIN_DELTA=$2; shift 2;;
    --strategy) STRATEGY=$2; shift 2;;
    --seed) SEED=$2; shift 2;;
    --min-disk-gb) MIN_DISK_GB=$2; shift 2;;
    --primary) PRIMARY=$2; shift 2;;
    --coverage-sweep) COVERAGE_SWEEP=yes; shift;;
    --coverage-max-ctx) COVERAGE_MAX_CTX=$2; shift 2;;
    --confirm-overnight) CONFIRM=yes; shift;;
    *) echo "unknown arg: $1" >&2; exit 64;;
  esac
done

die() { printf '\033[31mabort:\033[0m %s\n' "$*" >&2; exit 1; }
log() { printf '%s %s\n' "$(date +%H:%M:%S)" "$*" | tee -a "$STATE_DIR/loop.log"; }

# ---- argument gates -----------------------------------------------------
[ -n "$VAULT" ] && [ -d "$VAULT" ] || die "vault missing or not a directory: '${VAULT}' (set VAULT_PATH or --vault)"
[ -n "$EVALSET" ] && [ -f "$EVALSET" ] || die "eval set missing: '${EVALSET}' -- run make_evalset.py and review it first"
[ "$CONFIRM" = yes ] || die "refusing to run an unbounded autonomous loop without --confirm-overnight"
[ "$COUNT" -gt 0 ] || die "--count is required (this is the cap, not a suggestion)"
[ "$COUNT" -le 500 ] || die "--count above 500 is not overnight research, it is a drift; batch it"
[ -f "$STATE_DIR/baseline.json" ] || die "no baseline.json -- run vault_retrieval.py --set-baseline first (the first run is always the config as-is)"

mkdir -p "$STATE_DIR" "$REVIEW_DIR"
[ -f "$STATE_DIR/results.tsv" ] || printf '# lily autoresearch results -- tab-separated, do not commit, do not edit by hand\nexp_id\ttimestamp\tdescription\tprimary_metric\tprimary_value\thit_rate@1\thit_rate@5\tmrr@10\tseconds\tstatus\tsig\tconfig_json\n' > "$STATE_DIR/results.tsv"

DEADLINE_MIN=-1
if [ -n "$DEADLINE" ]; then
  if [[ "$DEADLINE" =~ ^([01]?[0-9]|2[0-3]):[0-5][0-9]$ ]]; then
    DEADLINE_MIN=$(( 10#${DEADLINE%%:*} * 60 + 10#${DEADLINE##*:} ))
  else
    die "--deadline must be HH:MM in 24h form (0-23 : 0-59), got: $DEADLINE"
  fi
fi

free_gb() { df -k "$PROJECT" 2>/dev/null | awk 'NR==2 {print int($4/1048576)}'; }

# ---- timeout guard: macOS ships no `timeout`, so use a watchdog ----------
# The child must be backgrounded in THIS shell, not inside a subshell, or `wait`
# cannot reap it and the exit status is lost.
run_guarded() {
  local secs=$1; shift
  "$@" &
  local pid=$!
  local start; start=$(date +%s)
  while kill -0 "$pid" 2>/dev/null; do
    if [ $(( $(date +%s) - start )) -ge "$secs" ]; then
      kill -TERM "$pid" 2>/dev/null; sleep 1; kill -KILL "$pid" 2>/dev/null
      wait "$pid" 2>/dev/null
      return 124
    fi
    sleep 1
  done
  wait "$pid" 2>/dev/null; return $?
}

BASE=$(python3 -c "import json;print(json.load(open('$STATE_DIR/baseline.json'))['primary_value'])")
log "start: vault=$VAULT count<=$COUNT deadline=${DEADLINE:-none} budget=${BUDGET_MIN}min primary=$PRIMARY baseline=$BASE"

i=0; kept=0; discarded=0; crashed=0; sweep=0
while [ "$i" -lt "$COUNT" ]; do
  i=$((i + 1))

  if [ "$DEADLINE_MIN" -ge 0 ]; then
    now_min=$(( $(date +%H) * 60 + $(date +%M) ))
    if [ "$now_min" -ge "$DEADLINE_MIN" ]; then log "deadline ${DEADLINE} reached after $i proposals"; break; fi
  fi
  FG=$(free_gb)
  if [ "${FG:-0}" -lt "$MIN_DISK_GB" ]; then
    log "disk guard: ${FG} GB free < ${MIN_DISK_GB} GB -- stopping. Logs and the chunk cache are the only things at risk, and they are the cheapest things to lose."
    break
  fi

  SEED_ARG=""
  [ -n "$SEED" ] && SEED_ARG="--seed $((SEED + i))"
  python3 "$SKILL_DIR/scripts/next_experiment.py" --state-dir "$STATE_DIR" \
      --out "$STATE_DIR/candidate.json" --strategy "$STRATEGY" $SEED_ARG \
      > "$STATE_DIR/.cand.stdout" 2>"$STATE_DIR/.cand.stderr"
  rc=$?
  if [ "$rc" -eq 5 ]; then log "search space exhausted after $i proposals -- every neighbour of the current best has been tried"; sweep=1; break; fi
  if [ "$rc" -ne 0 ]; then log "proposer failed (rc=$rc): $(tail -1 "$STATE_DIR/.cand.stderr")"; break; fi

  DESC=$(python3 -c "import json;print(json.load(open('$STATE_DIR/candidate.json'))['change'])")
  LIMIT_ARG=""
  [ -n "${EVAL_LIMIT:-}" ] && LIMIT_ARG="--limit $EVAL_LIMIT"

  HARD_LIMIT=$(awk -v b="$BUDGET_MIN" 'BEGIN{printf "%d", b*60*3 + 15}')
  run_guarded "$HARD_LIMIT" \
    python3 "$SKILL_DIR/scripts/vault_retrieval.py" --vault "$VAULT" --eval "$EVALSET" \
      --config "$STATE_DIR/candidate.json" --state-dir "$STATE_DIR" \
      --primary "$PRIMARY" --budget-min "$BUDGET_MIN" $LIMIT_ARG \
      > "$STATE_DIR/last_metrics.json" 2>"$STATE_DIR/.run.stderr"
  rc=$?
  if [ "$rc" -eq 4 ]; then log "setup error (rc=4), not an experiment failure: $(tail -1 "$STATE_DIR/.run.stderr")"; break; fi
  if [ "$rc" -eq 3 ] || [ "$rc" -eq 124 ]; then
    python3 "$SKILL_DIR/scripts/record.py" --state-dir "$STATE_DIR" --candidate "$STATE_DIR/candidate.json" \
        --metrics "$STATE_DIR/last_metrics.json" --description "$DESC (timeout)" --crashed --review-dir "$REVIEW_DIR" >/dev/null
    crashed=$((crashed + 1)); log "[$i] CRASH/timeout  $DESC"; continue
  fi
  if [ "$rc" -ne 0 ]; then
    python3 "$SKILL_DIR/scripts/record.py" --state-dir "$STATE_DIR" --candidate "$STATE_DIR/candidate.json" \
        --metrics "$STATE_DIR/last_metrics.json" --description "$DESC" --crashed --review-dir "$REVIEW_DIR" >/dev/null
    crashed=$((crashed + 1)); log "[$i] CRASH  $DESC :: $(tail -1 "$STATE_DIR/.run.stderr")"; continue
  fi

  # stdout of vault_retrieval.py IS the metrics JSON (redirected above); judge it here
  python3 "$SKILL_DIR/scripts/record.py" --state-dir "$STATE_DIR" --candidate "$STATE_DIR/candidate.json" \
      --metrics "$STATE_DIR/last_metrics.json" --description "$DESC" --min-delta "$MIN_DELTA" \
      --review-dir "$REVIEW_DIR" > "$STATE_DIR/.rec.stdout" 2>&1
  rc=$?
  VAL=$(python3 -c "import json;print(json.load(open('$STATE_DIR/last_metrics.json'))['primary_value'])" 2>/dev/null || echo "?")
  case "$rc" in
    0) kept=$((kept + 1));  log "[$i] KEEP     $DESC -> $VAL";;
    1) discarded=$((discarded + 1)); log "[$i] discard  $DESC -> $VAL";;
    *) crashed=$((crashed + 1)); log "[$i] CRASH    $DESC :: $(tail -1 "$STATE_DIR/.rec.stdout")";;
  esac
done

# ---- route 2: the deterministic sweep the ranker search cannot express ---------
# Fires only when route 1 (ranker neighbours) exhausted itself. The remaining
# productive space is *injection geometry* -- mode x top x cap -- and unlike a ranker
# knob its metric (evidence coverage: does every must_contain string land inside the
# text actually sent to the model?) is deterministic and brain-free: ~0.04 s/arm, so
# 7680 arms sweep in ~5 minutes instead of ~70 minutes of AFM calls, and the result is
# immune to session-health drift. That also makes a sequential proposer the wrong
# instrument here -- the space is small enough to enumerate exhaustively, so the sweep
# replaces arm-by-arm search rather than extending it.
#
# The builder lives in the project, not in this skill: the sweep delegates to
# lily_ask.inject_context so it cannot optimise a geometry no shipped agent runs.
# Nothing is merged: a coverage gain is a capability, not a behaviour change, and the
# behaviour test that could merge one is always the paired, health-gated AFM run.
if [ "$sweep" = 1 ] && [ "$COVERAGE_SWEEP" = yes ]; then
  SWEEP="$PROJECT/lily_coverage.py"
  PY="${VENV_PY:-$PROJECT/.venv/bin/python}"
  [ -x "$PY" ] || PY=python3
  if [ ! -f "$SWEEP" ]; then
    log "coverage sweep skipped: $SWEEP not found"
  elif [ ! -f "$EVALSET" ]; then
    log "coverage sweep skipped: no eval set"
  else
    log "coverage sweep starting (max-ctx $COVERAGE_MAX_CTX) -- ranker space is exhausted, injection geometry is not"
    run_guarded 1800 "$PY" "$SWEEP" --eval "$EVALSET" --max-ctx "$COVERAGE_MAX_CTX" \
      --base-config "$STATE_DIR/best_config.json" \
      --out "$STATE_DIR/cov_sweep.tsv" --report "$STATE_DIR/cov_sweep.json" \
      > "$STATE_DIR/.sweep.stdout" 2>"$STATE_DIR/.sweep.stderr"
    rc=$?
    if [ "$rc" -ne 0 ]; then
      log "coverage sweep failed (rc=$rc): $(tail -1 "$STATE_DIR/.sweep.stderr")"
    else
      read -r COV BESTARM <<<"$(python3 -c "
import json
d = json.load(open('$STATE_DIR/cov_sweep.json'))
b = str(max(int(k) for k in d['per_context_budget']))
o = d['per_context_budget'][b]
a = o['cheapest_arms_at_best_coverage']
print(o['best_coverage'], (f\"{a[0]['mode']}:{a[0]['top']}:{a[0]['cap']}@{a[0]['mean_ctx']}\" if a else 'none'))
" 2>/dev/null || echo '? ?')"
      log "coverage sweep done: best feasible coverage $COV rows under budget, cheapest arm $BESTARM -- frontier banked in $STATE_DIR/cov_sweep.json"
      log "coverage is a capability, not a verdict: to merge it, run the paired health-gated answer test on the banked arm against the shipped one."
    fi
  fi
fi

BEST=$(python3 -c "import json,os;p='$STATE_DIR/best-metrics.json';print(json.load(open(p))['primary_value'] if os.path.exists(p) else '$BASE')")
printf '\n=== %s ===\n' "summary" | tee -a "$STATE_DIR/loop.log"
printf 'proposed %s | kept %s | discarded %s | crashed %s\n' "$i" "$kept" "$discarded" "$crashed" | tee -a "$STATE_DIR/loop.log"
printf 'baseline %s -> best %s (%s)\n' "$BASE" "$BEST" "$PRIMARY" | tee -a "$STATE_DIR/loop.log"
printf 'ledger  %s\nreviews %s\n' "$STATE_DIR/results.tsv" "$REVIEW_DIR" | tee -a "$STATE_DIR/loop.log"
N_REV=$(find "$REVIEW_DIR" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
[ "${N_REV:-0}" -gt 0 ] && printf '%s proposal(s) waiting. Nothing was merged into any agent file.\n' "$N_REV" | tee -a "$STATE_DIR/loop.log"
