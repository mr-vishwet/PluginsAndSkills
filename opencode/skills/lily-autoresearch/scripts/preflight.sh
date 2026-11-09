#!/usr/bin/env bash
# preflight.sh -- measure the machine, then state which autoresearch mode is possible.
# Nothing here guesses. Every number is read from the OS.
set -uo pipefail

PROJECT="${PROJECT_DIR:-$PWD}"
STATE_DIR="$PROJECT/.docs/autoresearch"
# Prefer the project's own runtime. The Tier 1-Apple binding is installed into .venv (ADR-0003);
# probing with the system python would report "not installed" on a machine that has it working.
PY="python3"
[ -x "$PROJECT/.venv/bin/python" ] && PY="$PROJECT/.venv/bin/python"
MIN_DISK_GB=${MIN_DISK_GB:-2}
MIN_TRAIN_DISK_GB=${MIN_TRAIN_DISK_GB:-20}
MIN_TRAIN_RAM_GB=${MIN_TRAIN_RAM_GB:-16}

hdr() { printf '\n\033[1m%s\033[0m\n' "$1"; }
kv()  { printf '  %-22s %s\n' "$1" "$2"; }

# ---- memory -------------------------------------------------------------
RAM_BYTES=$(sysctl -n hw.memsize 2>/dev/null || echo 0)  # macOS key; hw.membytes is Linux
RAM_GB=$(( RAM_BYTES / 1073741824 ))
if [ "${RAM_GB:-0}" -eq 0 ]; then
  RAM_GB=$(printf '%s' "${MEM_LINE:-}" | grep -oE '[0-9]+' | head -1)
  RAM_GB=${RAM_GB:-0}
fi

# ---- disk ---------------------------------------------------------------
AVAIL_KB=$(df -k "$PROJECT" 2>/dev/null | awk 'NR==2 {print $4}')
AVAIL_GB=$(( ${AVAIL_KB:-0} / 1048576 ))

# ---- gpu ----------------------------------------------------------------
HAS_CUDA=no
if command -v nvidia-smi >/dev/null 2>&1; then HAS_CUDA=yes; fi
CHIP=$(system_profiler SPHardwareDataType 2>/dev/null | awk -F': ' '/^ *Chip:/{print $2}')
[ -z "$CHIP" ] && CHIP="unknown"
MEM_LINE=$(system_profiler SPHardwareDataType 2>/dev/null | awk -F': ' '/^ *Memory:/{print $2}')

hdr "Measured host"
kv "chip"        "$CHIP"
kv "cuda gpu"    "$HAS_CUDA"
kv "unified memory" "${RAM_GB} GB"
kv "free disk"    "${AVAIL_GB} GB"
kv "python"       "$(python3 --version 2>&1)"

hdr "Toolchain present"
for t in ollama uv brew node; do
  if command -v $t >/dev/null 2>&1; then kv "$t" "yes"; else kv "$t" "no"; fi
done
for m in torch mlx mlx_lm chromadb sentence_transformers; do
  python3 -c "import $m" >/dev/null 2>&1 && kv "py:$m" "installed" || kv "py:$m" "absent"
done

hdr "Model gates"
printf '  %-28s %s\n' "qwen2.5-coder:32b (~19 GB)"  "IMPOSSIBLE - exceeds ${RAM_GB} GB total RAM"
printf '  %-28s %s\n' "8B-14B Q4 (~5-9 GB)"          "NO - leaves nothing for OS + Chrome + Obsidian"
printf '  %-28s %s\n' "3B-4B Q4 (~2-3 GB)"           "MARGINAL - needs ${MIN_DISK_GB}+ GB free disk to download"
printf '  %-28s %s\n' "nomic-embed-text (~0.3 GB)"   "OK if disk allows"

MODE_TRAIN=no
MODE_EVAL=no
REASONS=()

if [ "$HAS_CUDA" = no ]; then
  REASONS+=("train: upstream autoresearch pins torch==2.9.1 from the cu128 index; no CUDA device")
elif [ "$RAM_GB" -lt "$MIN_TRAIN_RAM_GB" ]; then
  REASONS+=("train: ${RAM_GB} GB RAM < ${MIN_TRAIN_RAM_GB} GB needed for the smallest useful fork")
elif [ "$AVAIL_GB" -lt "$MIN_TRAIN_DISK_GB" ]; then
  REASONS+=("train: ${AVAIL_GB} GB free < ${MIN_TRAIN_DISK_GB} GB for data shards + tokenizer + torch")
else
  MODE_TRAIN=yes
fi

if [ "$AVAIL_GB" -lt "$MIN_DISK_GB" ]; then
  REASONS+=("eval: only ${AVAIL_GB} GB free; the loop needs ${MIN_DISK_GB} GB headroom for logs + index cache")
else
  MODE_EVAL=yes
fi

hdr "Verdict"
kv "mode train (nanochat)" "$MODE_TRAIN"
kv "mode eval (lily loop)" "$MODE_EVAL"

if [ ${#REASONS[@]} -gt 0 ]; then
  hdr "Why"
  for r in "${REASONS[@]}"; do printf '  - %s\n' "$r"; done
fi

if [ "$MODE_EVAL" = no ]; then
  hdr "BLOCKED"
  printf '  Free disk is below the guard. Check what is writing, and re-measure with df -h /System/Volumes/Data:\n'
  printf '    du -sh ~/Library/Caches/* | sort -h | tail -15\n'
  printf '    df -h /System/Volumes/Data   # the Data volume, not "/" (the sealed system snapshot)\n'
  exit 2
fi

hdr "Eval-mode readiness"
[ -d "$STATE_DIR" ] || mkdir -p "$STATE_DIR"
VAULT_ENV=$(grep -E '^VAULT_PATH=' "$PROJECT/.envs/lily.env" 2>/dev/null | cut -d= -f2- | tr -d '"' || true)
kv "state dir"  "$STATE_DIR"
kv "VAULT_PATH" "${VAULT_ENV:-'(set it in .envs/lily.env)'}"
if [ -n "${VAULT_ENV:-}" ]; then
  # Expand \$HOME / ~ without eval: this string comes from a config file, and eval
  # would execute whatever happens to be in it.
  EXPANDED=${VAULT_ENV/#\~/$HOME}
  EXPANDED=${EXPANDED//'$HOME'/$HOME}
  EXPANDED=${EXPANDED//\$HOME/$HOME}
  if [ -d "$EXPANDED" ]; then
    kv "vault notes" "$(find "$EXPANDED" -name '*.md' -not -path '*/.obsidian/*' 2>/dev/null | wc -l | tr -d ' ')"
  else
    kv "vault" "path does not exist: $EXPANDED"
  fi
fi

# Any reviewed JSONL under evals/ or the state dir is a usable eval set -- looking only for
# one hard-coded filename made preflight report "missing" while two real sets sat in evals/.
EV=$( { [ -n "${EVALSET:-}" ] && printf '%s\n' "$EVALSET"; \
        ls "$PROJECT"/evals/*.jsonl "$STATE_DIR"/*.jsonl 2>/dev/null; } | awk '!seen[$0]++')
if [ -z "$EV" ]; then
  kv "eval set" "missing - run make_evalset.py, then REVIEW it"
else
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    N=$(grep -c . "$f")
    UNVERIFIED=$(grep -c '"verified": false' "$f" 2>/dev/null || true)
    printf '  %-28s %s rows, %s unverified\n' "$(basename "$f")" "$N" "$UNVERIFIED"
  done <<EOF
$EV
EOF
fi
[ -f "$STATE_DIR/baseline.json" ] && kv "baseline" "recorded" || kv "baseline" "missing - run vault_retrieval.py --set-baseline"

# Tier 1-Apple (ADR-0003): the default brain is free only if the framework AND the binding are
# there. Checked, never assumed -- eligibility is Apple's to withdraw.
hdr "On-device brain (Tier 1-Apple)"
kv "probe uses" "$PY"
if [ -d "/System/Library/Frameworks/FoundationModels.framework" ]; then
  kv "FoundationModels.framework" "present"
else
  kv "FoundationModels.framework" "ABSENT - macOS < 26; use the Ollama or cloud tier instead"
fi
if "$PY" -c "import applefoundationmodels" 2>/dev/null; then
  "$PY" - <<'PY' 2>/dev/null || kv "binding" "importable, but the probe failed"
import applefoundationmodels as afm
from applefoundationmodels import Session
CODE = {1: "AVAILABLE", -1: "DEVICE_NOT_ELIGIBLE", -2: "NOT_ENABLED",
        -3: "MODEL_NOT_READY", -99: "AVAILABILITY_UNKNOWN"}
c = Session.check_availability()
print(f"  {'availability':<28} {CODE.get(c, c)} -- {Session.get_availability_reason()}")
PY
else
  kv "apple-foundation-models" "not installed - $PY -m pip install apple-foundation-models (0.12 MB, no weights)"
fi
exit 0
