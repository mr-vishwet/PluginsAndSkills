#!/usr/bin/env python3
"""make_evalset.py -- bootstrap a retrieval eval set from an Obsidian vault.

Emits (question, gold_note) pairs three ways, all deliberately worded *differently*
from the note, because the thing Lily must do is find a note from a half-remembered
thought, not from its own title:

  heading      a markdown heading used as a keyword query
  title        the note title / filename as a query
  cloze        the note's most content-dense sentence with its rarest terms deleted

Output rows carry "verified": false. Auto pairs are candidates, not ground truth:
review and delete the junk before establishing a baseline, or the loop optimises a
number that measures nothing.

Usage:
  python3 make_evalset.py --vault "$VAULT_PATH" --out .docs/autoresearch/eval-set.jsonl \
      --limit 40 --min-age-days 14
"""
from __future__ import annotations

import argparse, json, os, random, re, sys, time
from collections import Counter

SKIP_DIRS = {".obsidian", ".trash", ".git", "node_modules", "templates", "_attachments"}
CJK_DEV = r"\u0900-\u097F"


def words(text: str) -> list[str]:
    return re.findall(rf"[a-z0-9_\u00C0-\u024F{CJK_DEV}]+", text.lower())


def strip_frontmatter(raw: str) -> str:
    return re.sub(r"^---\s*\n.*?\n---\s*\n?", "", raw, count=1, flags=re.S)


def sentences(body: str) -> list[str]:
    parts = re.split(r"(?<=[.!?\n])\s+", body)
    return [p.strip() for p in parts if 8 <= len(words(p)) <= 30]


def rarest(sent: str, df: Counter, n_terms: int, vocab: set[str]) -> list[str]:
    ws = [w for w in words(sent) if len(w) > 3 and w not in vocab]
    return sorted(ws, key=lambda w: df.get(w, 1))[:n_terms]


def cloze_query(sent: str, drop: list[str]) -> str:
    q = sent
    for term in drop:
        q = re.sub(re.escape(term), "", q, flags=re.I)
    q = re.sub(r"\s{2,}", " ", q).strip(" .,;:!?-")
    return q if len(words(q)) >= 5 else ""


def collect(vault: str, min_age_days: float):
    notes = []
    cutoff = time.time() - min_age_days * 86400
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in files:
            if not fn.lower().endswith((".md", ".markdown")):
                continue
            path = os.path.join(root, fn)
            try:
                st = os.stat(path)
                if st.st_size > 2_000_000 or st.st_mtime > cutoff:
                    continue
                raw = open(path, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            body = strip_frontmatter(raw)
            if len(words(body)) < 25:
                continue
            title = os.path.splitext(fn)[0].replace("-", " ").replace("_", " ")
            m = re.search(r"^title:\s*(.+)$", raw[:2000], re.M)
            if m:
                title = m.group(1).strip().strip("'\"")
            heads = [h.strip() for h in re.findall(r"^#{2,4}\s+(.+)$", body, re.M) if len(words(h)) >= 3]
            notes.append({"path": path, "title": title, "heads": heads[:4], "sents": sentences(body)})
    return notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--min-age-days", type=float, default=14.0,
                    help="ignore notes newer than this; testing recall of past thinking")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    if not os.path.isdir(args.vault):
        print(f"error: vault not found: {args.vault}", file=sys.stderr)
        return 4

    notes = collect(args.vault, args.min_age_days)
    if len(notes) < 5:
        print(f"error: only {len(notes)} eligible notes -- eval sets this small measure noise",
              file=sys.stderr)
        return 4

    df = Counter()
    all_tokens = Counter()
    for n in notes:
        toks = set(words(n["title"])) | {w for s in n["sents"] for w in words(s)}
        df.update(toks)
        all_tokens.update(toks)
    vocab = {w for w, c in all_tokens.items() if c < 2}  # hapax terms are the discriminative ones

    rows = []
    for n in notes:
        for h in n["heads"][:2]:
            rows.append({"question": h, "gold_note": n["path"], "kind": "heading"})
        rows.append({"question": n["title"], "gold_note": n["path"], "kind": "title"})
        dense = sorted(n["sents"], key=lambda s: -len([w for w in words(s) if w in vocab]))
        for s in dense[:1]:
            drop = rarest(s, df, 3, set())
            q = cloze_query(s, drop)
            if q:
                rows.append({"question": q, "gold_note": n["path"], "kind": "cloze"})

    seen, uniq = set(), []
    for r in rows:
        key = (re.sub(r"\W+", "", r["question"].lower()), r["gold_note"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)

    rng = random.Random(args.seed)
    rng.shuffle(uniq)
    chosen = uniq[: args.limit] if args.limit else uniq

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        for i, r in enumerate(chosen, 1):
            fh.write(json.dumps({
                "id": f"auto{i:03d}",
                "question": r["question"],
                "gold_note": r["gold_note"],
                "kind": r["kind"],
                "verified": False,
                "source": "auto",
            }, ensure_ascii=False) + "\n")

    kinds = Counter(r["kind"] for r in chosen)
    print(json.dumps({
        "written": args.out,
        "rows": len(chosen),
        "eligible_notes": len(notes),
        "kinds": dict(kinds),
        "next_step": "OPEN THE FILE AND DELETE ROWS THAT ARE NOT REAL QUESTIONS. "
                     "Set verified=true on the ones you keep, or the baseline is fiction.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
