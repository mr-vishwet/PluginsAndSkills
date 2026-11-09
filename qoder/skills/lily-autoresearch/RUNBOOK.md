# Runbook

## Upstream: what `karpathy/autoresearch` actually is

Verified from the repo itself (cloned 2026-10-06, default branch `master`):

| Fact | Value |
|---|---|
| Description | "AI agents running research on single-GPU nanochat training automatically" |
| Created / last pushed | 2026-03-06 / 2026-03-26 — effectively frozen |
| Stars / forks | ~97k / ~13.5k |
| License | README says MIT; **GitHub detects no license file** (API returns `license: null`). Verify before vendoring. |
| Contents | 5 real files: `prepare.py`, `train.py`, `program.md`, `pyproject.toml`, `analysis.ipynb` |
| Requirement | **single NVIDIA GPU**, tested on H100. `pyproject.toml` pins `torch==2.9.1` from `download.pytorch.org/whl/cu128` |

It is autonomous *pretraining* research. The agent edits `train.py`, runs 5 minutes of
nanochat training, reads `val_bpb`, keeps or reverts, loops. It is not a persona, memory,
or agent-behaviour improvement system, and it does not train anything on Apple Silicon.

### File-for-file mapping to this skill

| Upstream | Here | Why it maps |
|---|---|---|
| `train.py` (the only editable file) | `candidate.json` — a retrieval config | the artifact the agent mutates, and nothing else |
| `prepare.py` (frozen harness) | `vault_retrieval.py` + the eval set | fixes the metric so 100 runs are comparable |
| `val_bpb` | `hit_rate@5` / `hit_rate@1` / `mrr@10` | single scalar, lower-is-better replaced by higher-is-better; both objective per-run |
| fixed 5-min wall clock | `--budget-min` + `run_guarded` | makes runs comparable across whatever the machine is doing |
| `results.tsv` (5 cols, untracked) | `results.tsv` (12 cols, untracked) | the morning artifact; append-only |
| branch `autoresearch/<tag>` | `best_config.json` advancing | "keep" moves the frontier, "discard" leaves it |
| `program.md` | `program.md` | the protocol is the product; the code is incidental |
| NEVER STOP | `--count` and `--deadline`, both required | see the divergence below |

### Where this deliberately diverges

1. **Human gate on merges.** Upstream optimises an objective scalar and can self-apply.
   Retrieval over your notes is a proxy for "does Lily remember me", and a proxy optimised
   overnight without review becomes a number that is right and a behaviour that is wrong.
   Proposals land in `.docs/notes/autoresearch-review/`; you merge them.
2. **Capped autonomy.** Upstream's "NEVER STOP" works because its budget is fixed and its
   space is bounded. Here the eval set is small and possibly mislabelled, so the loop must
   be able to end. Exhaustion (exit 5) is a reported finding, not a failure.
3. **Disk as a first-class guard.** `--min-disk-gb` aborts the loop. Upstream never needs
   this; a volume that a runaway log could fill does. Guard the failure mode, not a remembered number.

## Getting `train` mode running for real

Only if the host clears: NVIDIA GPU (CUDA 12.8), ≥16 GB system RAM, ≥20 GB free disk,
and a willingness to have the machine idle overnight.

```bash
git clone https://github.com/karpathy/autoresearch.git vendor/autoresearch
cd vendor/autoresearch
curl -Ls https://astral.sh/uv/install.sh | sh && uv sync
uv run prepare.py     # downloads shards, trains the BPE tokenizer (~2 min)
uv run train.py       # one 5-minute experiment, prints val_bpb
```

Then point an agent at `program.md`. Its README's own guidance for small compute applies
even to a real GPU: drop `DEPTH` from 8, `vocab_size` toward 4096, `WINDOW_PATTERN` to
just `L`, `MAX_SEQ_LEN` and `EVAL_TOKENS` down, `TOTAL_BATCH_SIZE` toward `2**14`, and use
the TinyStories dataset rather than the default shard mix.

Forks listed in upstream's README, verified to exist with star counts as of 2026-10-06:

| Fork | Platform | Stars |
|---|---|---|
| `miolini/autoresearch-macos` | macOS (PyTorch/MPS) | ~2.4k |
| `trevin-creator/autoresearch-mlx` | Apple Silicon MLX, no PyTorch | ~1.9k |
| `jsegov/autoresearch-win-rtx` | Windows NVIDIA | ~0.7k |
| `andyluo7/autoresearch` | AMD | ~75 |

Neither Mac fork runs comfortably in 8 GB of RAM, which is the real limit here (disk measured ~42 GB free on 2026-10-06). They are the path for a future machine,
not this one.

## Metrics glossary

| Metric | Meaning | Weakness |
|---|---|---|
| `hit_rate@k` | fraction of questions with the gold note inside the top k *distinct* notes | saturates on small vaults |
| `mrr@10` | mean reciprocal rank of the gold note | sensitive to one hard question in a small set |
| `unmatched_gold` | eval rows whose gold note is absent from the index | must be 0, else all scores are understated |
| `n_chunks == n_notes` | `chunk_words` exceeds your longest note | the chunking knob was never exercised |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `refusing to compare hit_rate@1 against a reference recorded as hit_rate@5` | `--primary` changed after baselining | re-run `--set-baseline` with the same `--primary` |
| every experiment discards | eval set saturates (small vault, `hit_rate@5` near 1) | switch to `hit_rate@1` or `mrr@10` and re-baseline |
| `unknown config keys` exit 4 | config contains a key outside `DEFAULT_CONFIG` | remove it; typos here used to be silently free |
| `proposer failed rc=5` immediately | every neighbour already in `tried.jsonl` | legitimate: widen `search-space.json` or start a new run tag |
| loop aborts on disk guard | free space under `--min-disk-gb` | find what is writing (logs, chunk caches); do not lower the guard to get past a real fill-up |
| `eval sets this small measure noise` | fewer than 5 eligible vault notes after age filter | lower `--min-age-days` or point at the real vault |
| run.log/loop.log growing fast | a crash loop, not a research loop | check `status` column; >5 consecutive `crash` means stop and read `.run.stderr` |

## Safety notes

- Everything this skill writes goes under `.docs/` (gitignored) or the skill's own state dir.
  Re-verify after any `.gitignore` edit: `git status --porcelain --ignored=matching .docs`
  must show `!!` for every `.docs/` path.
- The chunk cache is JSON, not pickle. It is regenerated from vault content anyway;
  deleting `.docs/autoresearch/chunks-*.json` is always safe.
- `logs` and `results.tsv` contain note titles and filenames. That is your private thinking.
  It must never be pushed, pasted into a cloud model, or included in a README example.
