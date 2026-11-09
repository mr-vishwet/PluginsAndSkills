# Lily autoresearch — program

Adapted from `karpathy/autoresearch/program.md`. That file is the best cheap artifact in
this space: a research protocol written for an agent, not about an agent. What follows is
its shape, re-grounded on hardware with no GPU and a metric that is not `val_bpb`.

**The one substantive change:** upstream auto-merges because `val_bpb` is objective and a
worse model is unambiguously worse. Retrieval quality over a personal vault is a *proxy*.
So the loop may advance its own branch, but every promotion is written as a proposal for a
human. Autonomy over the search, not over the merge.

## Setup

Agree these with the human before the first experiment. Do not start without all five.

1. **Vault path** — `VAULT_PATH` from `.envs/lily.env`. Confirm it exists and note the
   count of `.md` files it holds.
2. **Eval set** — `.docs/autoresearch/eval-set.jsonl`. If absent, generate with
   `make_evalset.py`, then have the human delete rows that are not real questions.
   A generated eval set is a starting draft, never ground truth.
3. **Primary metric** — one of `hit_rate@1`, `hit_rate@5`, `mrr@10`. Default `hit_rate@5`.
   Record the baseline with `--set-baseline` and `--primary` set to that choice. Changing
   `--primary` mid-run without re-baselining is refused by `record.py`, deliberately.
4. **Caps** — `--count` and `--deadline`. Both mandatory.
5. **Run tag** — e.g. `oct6`, so ledgers from different nights stay separable.

Then: `bash scripts/preflight.sh`. If it reports `mode eval = no`, stop and clear disk
space; do not attempt the loop on a full volume.

## Experimentation

Each experiment is one config mutation, measured against the whole eval set.

**What you CAN do:**
- Mutate one knob in `evals/search-space.json`: `chunk_words`, `chunk_overlap`, `k1`, `b`,
  `title_boost`, `tag_boost`, `freshness_weight`, `half_life_days`, `fold_devanagari`,
  `strip_stopwords`.
- Read `detail` rows in the metrics output to understand *why* a number moved.
- Note in the description what you expected and whether it happened.

**What you CANNOT do:**
- Edit `vault_retrieval.py`, `record.py`, or the eval set. That is the evaluation harness.
  Upstream freezes `prepare.py` for exactly this reason and it is the only thing keeping
  the numbers comparable across 100 runs.
- Change `top_k`. It is in `FROZEN` for a reason: moving it changes what the metric means.
- Edit any file in `.docs/agentic/`, the persona, or the router. Proposals only.
- Try a config already in `tried.jsonl`. The proposer enforces this; do not route around it.

**One hypothesis per experiment.** `--strategy mutate` changes exactly one knob. A config
that moves three knobs at once can "win" for reasons you cannot name, which is worthless
to a system that has to explain itself to you in the morning.

## Judging

`record.py` decides: keep if `primary_value > best + --min-delta`, else discard.
On a tiny vault most variants tie; ties are discards, not "promising". Resist narrating a
tie as a win.

Before reporting a keep as real, check:
- `unmatched_gold` is 0. Otherwise the eval set references deleted notes and every number
  understates quality — the whole night's ranking is noise.
- `n_items` is large enough to mean something. Under ~30 verified rows, a +0.05 delta is
  one or two notes, not an improvement.
- `n_chunks` is plausible for the vault size. A chunk count equal to the note count means
  `chunk_words` is above your longest note and the chunking knob was never actually tested.

## Output

`results.tsv` (tab-separated, 12 columns, one row per experiment) is the ledger. It stays
untracked. Read it in the morning with:

```bash
column -t -s$'\t' .docs/autoresearch/results.tsv | cut -c1-160
```

## The loop

Use `loop.sh`; it implements the iterate/advance/reset discipline in `program.md` terms:

1. propose one mutation from the current best
2. measure it against the eval set under the wall-clock budget
3. keep or discard; on keep, advance the branch (`best_config.json`) and write a proposal
4. repeat until `--count` or `--deadline`, or the neighbourhood is exhausted (exit 5)

Stopping on exhaustion is a *good* result. "Every one-knob neighbour of the current best
has been tried and none improved" is a finding. Do not respond to it by loosening the rules.

## When to stop and say something

- The eval set is too small or mostly unverified → the loop will confidently optimise noise.
- Free disk under 2 GB → stop. (Disk was never really the limit here: 2026-10-06 measurement says ~42 GB free; the "3.4 GB" figure circulating in earlier notes was wrong.)
- The baseline metric is 0.0 or 1.0 → the eval set is broken, not the retriever.
- Kept experiments only move one knob family → the search space is not where the real
  bottleneck is; report that instead of grinding.
