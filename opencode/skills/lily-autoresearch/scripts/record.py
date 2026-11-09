#!/usr/bin/env python3
"""record.py -- judge one experiment and append the ledger.

Reads the metrics JSON vault_retrieval.py produced, compares the primary metric against
the current best, decides keep | discard | crash, and appends a tab-separated row to
results.tsv. On keep it advances best_config.json and writes a human-facing proposal
into the review directory.

It never edits an agent or persona file. Upstream can auto-merge because val_bpb is
objective; retrieval quality on your own vault is a proxy, so the merge stays a human act.

Usage:
  python3 record.py --state-dir .docs/autoresearch --candidate candidate.json \
      --metrics last_metrics.json --description "k1: 1.5 -> 2.0"
Exit: 0 keep, 1 discard, 2 crash, 4 input error.
"""
from __future__ import annotations

import argparse, datetime, json, os, sys

TSV_COLUMNS = ["exp_id", "timestamp", "description", "primary_metric", "primary_value",
               "hit_rate@1", "hit_rate@5", "mrr@10", "seconds", "status", "sig", "config_json"]
HEADER = "# lily autoresearch results -- tab-separated, do not commit, do not edit by hand"


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def append_row(path: str, row: dict) -> None:
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8") as fh:
        if new:
            fh.write(HEADER + "\n")
            fh.write("\t".join(TSV_COLUMNS) + "\n")
        fh.write("\t".join(str(row.get(c, "")).replace("\t", " ").replace("\n", " ")
                           for c in TSV_COLUMNS) + "\n")


def write_review(review_dir: str, row: dict, ref: dict, cand: dict) -> str:
    os.makedirs(review_dir, exist_ok=True)
    path = os.path.join(review_dir, f"{row['exp_id']}-{row['sig']}.md")
    deltas = []
    keys = list(dict.fromkeys([ref.get("primary_metric"), "hit_rate@1", "hit_rate@5", "mrr@10"]))
    for key in keys:
        if key and key in ref and key in row:
            deltas.append(f"| {key} | {ref[key]} | {row[key]} | {row[key] - ref[key]:+.4f} |")
    body = f"""# Proposal {row['exp_id']} -- {row['description']}

**Generated:** {row['timestamp']}
**Status:** awaiting human review. Nothing was merged.

## Metric

| metric | before | after | delta |
|---|---|---|---|
{chr(10).join(deltas)}

## Config diff vs previous best

```diff
{os.linesep.join(f'- {k}: {v}' for k, v in sorted((ref.get('config') or {}).items())
                 if cand['config'].get(k) != v)}
{os.linesep.join(f'+ {k}: {v}' for k, v in sorted(cand['config'].items())
                 if (ref.get('config') or {}).get(k) != v)}
```

## What to check before you merge

1. Read 3 rows of `detail` in the metrics file. Did it improve because retrieval got
   better, or because the eval set happens to reward this wording?
2. `unmatched_gold` must be 0. If it is not, the eval set references notes that no
   longer exist and every number here is understated.
3. Apply it deliberately: copy `config_json` from `results.tsv` into
   `.docs/autoresearch/promoted-config.json`, then wire that file into the real
   retriever. Do not paste it into a persona MD.
"""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-dir", default=".docs/autoresearch")
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--metrics", required=True)
    ap.add_argument("--description", default="")
    ap.add_argument("--min-delta", type=float, default=0.001,
                    help="improvement required to keep; guards against noise-chasing")
    ap.add_argument("--crashed", action="store_true", help="run failed before producing metrics")
    ap.add_argument("--review-dir", default=".docs/notes/autoresearch-review")
    args = ap.parse_args()

    cand = load(args.candidate)
    os.makedirs(args.state_dir, exist_ok=True)
    tsv = os.path.join(args.state_dir, "results.tsv")
    tried = os.path.join(args.state_dir, "tried.jsonl")

    ref = {}
    for name in ("best-metrics.json", "baseline.json"):
        p = os.path.join(args.state_dir, name)
        if os.path.exists(p):
            ref = load(p)
            break

    row = {
        "exp_id": cand.get("exp_id", "e????"),
        "timestamp": now(),
        "description": args.description or cand.get("change") or "(no description)",
        "sig": cand.get("sig", ""),
        "config_json": json.dumps(cand.get("config", {}), sort_keys=True),
    }

    if args.crashed or not os.path.exists(args.metrics):
        row.update({"status": "crash", "primary_metric": ref.get("primary_metric", ""),
                    "primary_value": 0.0, "hit_rate@1": 0.0, "hit_rate@5": 0.0,
                    "mrr@10": 0.0, "seconds": 0.0})
        status_code = 2
    else:
        m = load(args.metrics)
        if m.get("status") == "timeout":
            row.update({"status": "crash", "primary_metric": ref.get("primary_metric", ""),
                        "primary_value": 0.0, "hit_rate@1": m.get("hit_rate@1", 0.0),
                        "hit_rate@5": m.get("hit_rate@5", 0.0),
                        "mrr@10": m.get("mrr@10", 0.0), "seconds": m.get("index_seconds", 0.0)})
            status_code = 2
        else:
            value = m["primary_value"]
            ref_metric = ref.get("primary_metric")
            if ref_metric and ref_metric != m["primary_metric"]:
                print(f"error: refusing to compare {m['primary_metric']} against a "
                      f"reference recorded as {ref_metric}. Re-run --set-baseline with "
                      f"--primary {m['primary_metric']}, or the keep/discard line is "
                      f"comparing two different measurements.", file=sys.stderr)
                return 4
            best_val = ref.get("primary_value")
            improved = best_val is None or value > best_val + args.min_delta
            status = "keep" if improved else "discard"
            status_code = 0 if improved else 1
            row.update({"status": status, "primary_metric": m["primary_metric"],
                        "primary_value": value, "hit_rate@1": m["hit_rate@1"],
                        "hit_rate@5": m["hit_rate@5"],
                        "mrr@10": m["mrr@10"], "seconds": m.get("index_seconds", 0.0)})
            if m.get("unmatched_gold"):
                print(f"warning: {m['unmatched_gold']} eval rows reference notes that are not "
                      f"in the index -- the score understates retrieval quality", file=sys.stderr)
            if improved:
                with open(os.path.join(args.state_dir, "best_config.json"), "w", encoding="utf-8") as fh:
                    json.dump(m["config"], fh, indent=2)
                with open(os.path.join(args.state_dir, "best-metrics.json"), "w", encoding="utf-8") as fh:
                    json.dump({k: v for k, v in m.items() if k != "detail"}, fh, indent=2)
                review = write_review(args.review_dir, row, ref, cand)
                row["description"] += f" -> {os.path.basename(review)}"

    append_row(tsv, row)
    with open(tried, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"sig": row["sig"], "exp_id": row["exp_id"],
                             "status": row["status"], "at": row["timestamp"]}) + "\n")

    print(json.dumps(row, indent=2))
    return status_code


if __name__ == "__main__":
    sys.exit(main())
