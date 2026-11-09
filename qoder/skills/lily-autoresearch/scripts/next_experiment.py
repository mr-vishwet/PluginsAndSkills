#!/usr/bin/env python3
"""next_experiment.py -- propose the next config to try.

Default strategy is `mutate`: change exactly ONE knob from the current best. That is
the discipline that keeps upstream autoresearch's diffs reviewable, and here it keeps
every result attributable to a single hypothesis instead of a confounded bundle.
`--strategy random` samples the whole space, useful for the first cold few experiments.

Refuses to re-propose a config already in tried.jsonl. Exit 5 = search space exhausted,
which the loop treats as a legitimate stop reason rather than spinning forever.

Usage:
  python3 next_experiment.py --state-dir .docs/autoresearch --out .docs/autoresearch/candidate.json
"""
from __future__ import annotations

import argparse, hashlib, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASELINE = os.path.join(os.path.dirname(HERE), "evals", "baseline.config.json")
SPACE = os.path.join(os.path.dirname(HERE), "evals", "search-space.json")

# Never offered as an experiment: the metric definition is not a tunable. Letting the
# loop move top_k or half_life of the report would be harness tampering, upstream's
# "do not modify the evaluation harness" rule in this guise.
FROZEN = {"top_k"}


def signature(cfg: dict) -> str:
    core = {k: v for k, v in sorted(cfg.items()) if k not in FROZEN}
    return hashlib.sha256(json.dumps(core, sort_keys=True).encode()).hexdigest()[:16]


def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def read_tried(path: str) -> set[str]:
    done = set()
    if not os.path.exists(path):
        return done
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    done.add(json.loads(line)["sig"])
                except (ValueError, KeyError):
                    continue
    return done


def neighbours(base: dict, space: dict, rng: random.Random):
    """One-knob variations of base, in random order."""
    knobs = [k for k in space if k not in FROZEN and k in base]
    rng.shuffle(knobs)
    for knob in knobs:
        values = [v for v in space[knob] if v != base[knob]]
        rng.shuffle(values)
        for v in values:
            yield knob, v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-dir", default=".docs/autoresearch")
    ap.add_argument("--out", required=True)
    ap.add_argument("--strategy", choices=["mutate", "random"], default="mutate")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--space", default=SPACE)
    args = ap.parse_args()

    space = load_json(args.space)
    if not space:
        print(f"error: search space not readable: {args.space}", file=sys.stderr)
        return 4

    best = load_json(os.path.join(args.state_dir, "best_config.json"))
    baseline = load_json(BASELINE, {})
    base = best or baseline
    if not base:
        print("error: no baseline config available", file=sys.stderr)
        return 4

    tried = read_tried(os.path.join(args.state_dir, "tried.jsonl"))
    rng = random.Random(args.seed)

    candidate = change = None
    if args.strategy == "mutate":
        for knob, value in neighbours(base, space, rng):
            cfg = dict(base)
            cfg[knob] = value
            if signature(cfg) not in tried:
                candidate, change = cfg, f"{knob}: {base.get(knob)} -> {value}"
                break
    else:
        for _ in range(400):
            cfg = dict(base)
            for knob, values in space.items():
                # Annotation keys (_corpus_notes) and frozen keys are not tunables. Without
                # the `knob in base` test, rng.choice() over a *string* note returns one
                # random character and the candidate carries a bogus key -- which the scorer
                # then rejects with exit 4, poisoning every random-strategy experiment.
                if knob in FROZEN or knob not in base:
                    continue
                cfg[knob] = rng.choice(values)
            if signature(cfg) not in tried:
                candidate = cfg
                diff = [f"{k}: {base.get(k)}->{cfg[k]}" for k in space
                        if k not in FROZEN and k in base and cfg.get(k) != base.get(k)]
                change = "; ".join(diff[:4]) or "identical to current best"
                break

    if candidate is None:
        print(json.dumps({"status": "exhausted", "tried": len(tried)}))
        return 5

    exp_id = f"e{len(tried) + 1:04d}"
    payload = {"exp_id": exp_id, "strategy": args.strategy, "change": change,
               "sig": signature(candidate), "config": candidate,
               "hypothesis_required": True}

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
