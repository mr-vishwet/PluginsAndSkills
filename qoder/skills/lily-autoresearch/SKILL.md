---
name: lily-autoresearch
description: Runs autonomous overnight experiment loops for the Lily personal-agent project, adapted from karpathy/autoresearch to hardware that has no CUDA and only 8 GB of RAM. Replaces upstream's val_bpb training metric with a measured retrieval/behaviour score over the user's own Obsidian vault, logs keep/discard/crash to results.tsv, and writes a review bundle instead of silently editing persona files. Use when the user asks to run autoresearch, "let Lily improve overnight", kick off experiments / N possibilities, schedule an experiment loop, or evaluate a config change against the vault eval set.
---

# Lily Autoresearch

Autonomous experiment loop. Same shape as `karpathy/autoresearch`, different substrate.

## Hardware reality (read before promising anything)

Upstream autoresearch requires a **single NVIDIA GPU** — `pyproject.toml` pins
`torch==2.9.1` from `download.pytorch.org/whl/cu128`. It has never run on a Mac.
The Lily host is a MacBook Air **M1, 8 GB unified memory, ~42 GB free disk as measured 2026-10-06**
(earlier drafts of this skill said "3.4 GB free / 99% full" — that reading is not reproducible and
is wrong; **RAM is the binding constraint, not disk**).

| Mode | What it is | Runnable here |
|---|---|---|
| `train` | upstream: agent edits `train.py`, 5-min nanochat pretraining, metric `val_bpb` | **No.** Needs CUDA. MLX forks (`trevin-creator/autoresearch-mlx`, `miolini/autoresearch-macos`) exist but want disk + RAM this box does not have |
| `eval` | this skill: agent edits a **retrieval/behaviour config**, metric is score over a personal eval set | **Yes.** CPU-only, stdlib-only, ~seconds per experiment |

Run `scripts/preflight.sh` first. It prints the verdict with measured numbers. If a later
machine clears the gates, `train` mode is documented in [RUNBOOK.md](RUNBOOK.md) — do not
guess the requirements, read the repo's own README.

## The loop (eval mode)

The artifact under experiment is **not** model weights. It is `config.json`:
chunking, BM25 parameters, freshness weighting, title boost, top-k, query expansion —
the knobs that decide whether Lily finds the note she wrote at 2am.

Metric: `hit_rate@5` on the eval set, tie-broken by `mrr@10`. Both are computed by a
lexical BM25 retriever over the real vault in `.docs`-grade pure Python, so an experiment
costs seconds, not GPU-hours. 100 experiments is an honest number here.

```
LOOP FOREVER (until --count or --deadline hits):
  1. next_experiment.py  -> .docs/autoresearch/candidate.json   (never repeats a tried config)
  2. vault_retrieval.py  -> .docs/autoresearch/last_metrics.json (enforces --budget-min)
  3. record.py           -> keep | discard | crash, appends results.tsv
  4. keep  -> best_config.json advances, review bundle written
     discard/crash -> candidate reverted, branch does not advance
```

## Hard rules

1. **Never edit a persona or agent file.** `.docs/agentic/lily-persona.md` and its
   "Do-not-improve list" are off limits to the loop. Improvements land as a *proposal* in
   `.docs/notes/autoresearch-review/` for the human to merge. Upstream can self-modify
   freely because its metric is objective; a personal agent's metric is not, so a human
   gate is load-bearing, not bureaucratic.
2. **Never modify the scorer or the eval set** to make a number look better. Same reason
   upstream freezes `prepare.py`. If the eval set is wrong, say so and stop.
3. **Everything stays local.** `.docs/` is gitignored; `results.tsv` and run logs must never
   be committed or pushed.
4. **Disk is a live constraint.** The loop aborts itself if free space drops below
   `--min-disk-gb` (default 2). Keep the guard even on a volume with room to spare: a runaway log
   is the failure mode being guarded against, not the free-space figure.
5. **Cap the run.** `--count` and `--deadline` are both required. Upstream's "NEVER STOP"
   is paired there with a 5-minute budget and a bounded search space; copy that discipline,
   not the phrase.

## Setup (first run only)

```bash
cd C:/Users/User/Desktop/Vishwet/Experiments/Automation/LilyTheSaviour

# 1. gates + measured numbers
bash ~/.qoder/skills/lily-autoresearch/scripts/preflight.sh

# 2. vault path — from .envs/lily.env, e.g. $HOME/Documents/ObsidianVault
python3 ~/.qoder/skills/lily-autoresearch/scripts/make_evalset.py \
  --vault "$VAULT_PATH" --out .docs/autoresearch/eval-set.jsonl --limit 40

# 3. REVIEW it. Auto-generated pairs are candidates, not gold. Delete the junk
#    before the first baseline, or every conclusion is built on sand.

# 4. baseline (rule: the first run is always the config as-is)
python3 ~/.qoder/skills/lily-autoresearch/scripts/vault_retrieval.py \
  --vault "$VAULT_PATH" --eval .docs/autoresearch/eval-set.jsonl \
  --config ~/.qoder/skills/lily-autoresearch/evals/baseline.config.json \
  --set-baseline
```

## Run overnight

```bash
bash ~/.qoder/skills/lily-autoresearch/scripts/loop.sh \
  --vault "$VAULT_PATH" \
  --eval  .docs/autoresearch/eval-set.jsonl \
  --count 100 \
  --deadline 07:30 \
  --budget-min 0.5 \
  --confirm-overnight
```

Wakes up as: `results.tsv`, `best_config.json`, and one markdown per kept experiment in
`.docs/notes/autoresearch-review/`.

Add `--coverage-sweep` to spend the rest of the night instead of stopping. When the ranker
space exhausts (exit 5 -- every neighbour of the current best already in `tried.jsonl`), the
loop runs `$PROJECT/lily_coverage.py` once: an exhaustive, brain-free sweep of *injection
geometry* (mode x top x cap) against evidence coverage, banked to `cov_sweep.{tsv,json}`.
Tune its ceiling with `--coverage-max-ctx` (default 8500 chars, the largest arm measured to
complete on AFM). It merges nothing -- coverage is a capability; only the paired, health-gated
answer run can justify a behaviour change.

## Pointers

- [RUNBOOK.md](RUNBOOK.md) — upstream file-by-file mapping, `train` mode on a real GPU, metrics glossary, troubleshooting, forks
- [program.md](program.md) — the agent-facing instructions, in upstream's style
- `evals/eval-set.example.jsonl` + `evals/baseline.config.json` — formats and the frozen starting config
