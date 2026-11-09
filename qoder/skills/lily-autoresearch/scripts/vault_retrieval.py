#!/usr/bin/env python3
"""vault_retrieval.py -- the metric for Lily's autoresearch loop.

Scores a retrieval config against a personal eval set by running BM25 over the
real Obsidian vault. Standard library only: no torch, no chromadb, no ollama,
so it runs on an 8 GB M1 Air with no GPU and no model download.

Usage:
  python3 vault_retrieval.py --vault "$VAULT_PATH" --eval eval-set.jsonl \
      --config candidate.json --out last_metrics.json --budget-min 0.5

Output: JSON metrics on stdout (and in --out). Exit 0 = ran, 3 = timeout, 4 = input error.
The chunk cache is JSON, never pickle: a cache file is on-disk data this script re-reads,
and pickle-loading it would execute arbitrary objects if anything else ever wrote that path.
"""
from __future__ import annotations

import argparse, hashlib, json, math, os, re, sys, time
from collections import Counter

SKIP_DIRS = {".obsidian", ".trash", ".git", "node_modules", ".vscode", "_attachments"}
METRIC_KEYS = (1, 3, 5, 10)

DEFAULT_CONFIG = {
    "chunk_words": 128,
    "chunk_overlap": 0,
    "k1": 1.5,
    "b": 0.75,
    "title_boost": 2.0,
    "path_boost": 0.0,
    "tag_boost": 1.5,
    "freshness_weight": 0.0,
    "half_life_days": 90.0,
    "fold_devanagari": False,
    "strip_stopwords": False,
    "top_k": 10,
}

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "is", "are", "was", "were", "be",
    "to", "of", "in", "on", "for", "with", "at", "by", "from", "as", "that", "this",
    "it", "my", "me", "i", "you", "we", "they", "he", "she", "what", "how", "why",
    "hai", "ha", "ko", "ka", "ki", "ke", "me", "par", "se", "aur", "kya", "kaisa",
}

# Chandran-style transliteration fold: map Devanagari to roman approximations so a
# Hinglish query can match a Devanagari note. Cheap, lossy, honest about being lossy.
_DEV_TO_ROM = {
    "अ": "a", "आ": "aa", "इ": "i", "ई": "ee", "उ": "u", "ऊ": "oo", "ए": "e", "ऐ": "ai",
    "ओ": "o", "औ": "au", "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "च": "ch", "छ": "chh",
    "ज": "j", "झ": "jh", "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n", "त": "t",
    "थ": "th", "द": "d", "ध": "dh", "न": "n", "प": "p", "फ": "ph", "ब": "b", "भ": "bh",
    "म": "m", "य": "y", "र": "r", "ल": "l", "व": "v", "श": "sh", "ष": "sh", "स": "s",
    "ह": "h", "क्ष": "ksh", "त्र": "tr", "ज्ञ": "gy", " ा": "a", "ि": "i", "ी": "ee",
    "ु": "u", "ू": "oo", "े": "e", "ै": "ai", "ो": "o", "ौ": "au", "ं": "n", "ँ": "n",
    "़": "", "्": "", "ः": "h", "।": ".", "ॐ": "om",
}


def normalize(text: str, cfg: dict) -> str:
    if cfg["fold_devanagari"]:
        for src, dst in sorted(_DEV_TO_ROM.items(), key=lambda kv: -len(kv[0])):
            text = text.replace(src, dst)
    text = text.lower()
    return text


def tokenize(text: str, cfg: dict) -> list[str]:
    toks = re.findall(r"[a-z0-9_\u0900-\u097F]+", text)
    if cfg["strip_stopwords"]:
        toks = [t for t in toks if t not in STOPWORDS]
    return toks


def read_frontmatter(head: str) -> dict:
    """Minimal YAML-ish frontmatter parse. No pyyaml dependency."""
    out = {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", head, re.S)
    if not m:
        return out
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, _, v = line.partition(":")
            v = v.strip().strip("'\"")
            if v:
                out[k.strip().lower()] = v
    return out


def iter_notes(vault: str):
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in files:
            if fn.lower().endswith((".md", ".markdown")):
                path = os.path.join(root, fn)
                try:
                    if os.path.getsize(path) > 2_000_000:
                        continue
                    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                        yield path, fh.read()
                except OSError:
                    continue


def chunk_note(body: str, cfg: dict) -> list[str]:
    words = body.split()
    size, overlap = cfg["chunk_words"], cfg["chunk_overlap"]
    if size <= 0 or len(words) <= size:
        return [body.strip()] if body.strip() else []
    step = max(1, size - overlap)
    out = [" ".join(words[i:i + size]) for i in range(0, max(1, len(words) - size + 1), step)]
    return out or [body.strip()]


def build_chunks(vault: str, cfg: dict, signature: str) -> list[dict]:
    chunks = []
    for path, raw in iter_notes(vault):
        fm = read_frontmatter(raw[:4000])
        body = re.sub(r"^---\s*\n.*?\n---\s*\n?", "", raw, count=1, flags=re.S)
        title = fm.get("title") or os.path.splitext(os.path.basename(path))[0]
        tags = fm.get("tags", "").replace(",", " ")
        date = fm.get("date") or fm.get("created") or fm.get("modified")
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            mtime = time.time()
        n_title = tokenize(normalize(title, cfg), cfg)
        n_tags = tokenize(normalize(tags, cfg), cfg)
        # Path tokens are a separate field because a vault of per-project docs repeats
        # filenames: 58 "Architecture.md" share a title, so the title boosts every
        # candidate equally and only the directory says which project this chunk is from.
        reldir = os.path.relpath(os.path.dirname(path), vault)
        if reldir.startswith(".."):
            reldir = ""
        n_path = tokenize(normalize(reldir.replace(os.sep, " "), cfg), cfg)
        for idx, piece in enumerate(chunk_note(body, cfg)):
            n_body = tokenize(normalize(piece, cfg), cfg)
            if not n_body and not n_title:
                continue
            boosted = n_body[:]
            boosted += n_title * max(0, int(round(cfg["title_boost"])) - 1)
            boosted += n_path * max(0, int(round(cfg["path_boost"])) - 1)
            boosted += n_tags * max(0, int(round(cfg["tag_boost"])) - 1)
            chunks.append({
                "note": path, "i": idx, "tokens": boosted,
                "date": date, "mtime": mtime,
                "text": piece[:400],
            })
    return chunks


def relency_multiplier(age_days: float, cfg: dict) -> float:
    if cfg["freshness_weight"] <= 0:
        return 1.0
    hl = max(1.0, cfg["half_life_days"])
    recency = math.exp(-math.log(2) * age_days / hl)
    return 1.0 + cfg["freshness_weight"] * recency


def bm25(query_tokens, chunks, cfg):
    k1, b = cfg["k1"], cfg["b"]
    lengths = [len(c["tokens"]) for c in chunks] or [1]
    avgdl = sum(lengths) / len(lengths)
    n = len(chunks)
    df = Counter()
    for c in chunks:
        df.update(set(c["tokens"]))
    qset = set(query_tokens)
    scored = []
    now = time.time()
    for c, dl in zip(chunks, lengths):
        tf = Counter(c["tokens"])
        s = 0.0
        for t in qset & set(tf):
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            s += idf * (tf[t] * (k1 + 1)) / (tf[t] + k1 * (1 - b + b * dl / avgdl))
        if s <= 0:
            continue
        age_days = max(0.0, (now - c["mtime"]) / 86400.0)
        scored.append((s * relency_multiplier(age_days, cfg), c))
    scored.sort(key=lambda x: (-x[0], x[1]["note"], x[1]["i"]))
    return scored


class EvalFormatError(ValueError):
    """Eval set is unreadable or badly shaped. main() maps this to exit 4."""


def load_eval(path: str, limit: int) -> list[dict]:
    items = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as exc:
        raise EvalFormatError(f"cannot read eval set {path}: {exc}")
    # A whole-file JSON array is the most common accidental format (and the one an LLM
    # writes back). Iterating its text line by line would raise a bare AttributeError
    # inside json.loads, so detect it and say what to do instead.
    stripped = raw.lstrip()
    if stripped.startswith("["):
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError:
            raise EvalFormatError(f"{path} looks like JSON but does not parse")
        if isinstance(obj, list):
            raise EvalFormatError(
                f"{path} is one JSON array; expected JSONL (one object per line). "
                f"Fix with: jq -c '.[]' {path} > {path}.fixed")
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvalFormatError(f"{path} is not valid JSONL ({exc}) near: {line[:80]}")
        if not isinstance(d, dict):
            raise EvalFormatError(
                f"eval row must be an object, got {type(d).__name__}: {line[:80]}")
        if not d.get("question") or not d.get("gold_note"):
            raise EvalFormatError(f"eval row needs question + gold_note: {line[:80]}")
        items.append(d)
        if limit and len(items) >= limit:
            break
    if not items:
        raise EvalFormatError(f"{path} yielded no rows")
    return items


def resolve_gold(gold: str, keys: dict, vault: str):
    """Map an eval row's gold_note to an indexed note path.

    Eval sets get written with absolute paths, then the vault moves or the loop is
    launched with a relative --vault. Comparing raw strings silently scores 0.0000
    for a perfect retriever, which is the worst possible failure: it looks like a
    result. So try, in order: absolute, vault-relative, then unique basename.
    """
    for cand in (os.path.abspath(gold),
                 os.path.abspath(os.path.join(vault, gold)),
                 os.path.abspath(os.path.expanduser(gold))):
        if cand in keys:
            return keys[cand]
    base = os.path.basename(gold)
    matches = [v for k, v in keys.items() if os.path.basename(k) == base]
    return matches[0] if len(matches) == 1 else None


def evaluate(cfg: dict, chunks, items, primary: str, vault: str):
    note_keys = {os.path.abspath(c["note"]): c["note"] for c in chunks}
    hits = {k: 0 for k in METRIC_KEYS}
    rr_sum, per_item, unmatched = 0.0, [], 0
    top_k = max(METRIC_KEYS)
    for it in items:
        q = tokenize(normalize(it["question"], cfg), cfg)
        if cfg["strip_stopwords"] and not q:
            q = tokenize(normalize(it["question"], {**cfg, "strip_stopwords": False}), cfg)
        ranked = bm25(q, chunks, cfg)[:top_k]
        notes_in_order = []
        for _, c in ranked:
            if c["note"] not in notes_in_order:
                notes_in_order.append(c["note"])
        gold = resolve_gold(it["gold_note"], note_keys, vault)
        rank = None
        if gold:
            for i, note in enumerate(notes_in_order, start=1):
                if note == gold:
                    rank = i
                    break
        else:
            unmatched += 1
        for k in METRIC_KEYS:
            if rank and rank <= k:
                hits[k] += 1
        if rank:
            rr_sum += 1.0 / rank
        per_item.append({"question": it["question"][:120], "rank": rank,
                         "top": [os.path.basename(x) for x in notes_in_order[:3]]})
    n = len(items) or 1
    out = {
        "config": cfg,
        "primary_metric": primary,
        "primary_value": round(hits[5] / n, 4) if primary == "hit_rate@5" else
                        round(rr_sum / n, 4) if primary == "mrr@10" else
                        round(hits[int(primary.split("@")[1])] / n, 4),
        "hit_rate@1": round(hits[1] / n, 4),
        "hit_rate@3": round(hits[3] / n, 4),
        "hit_rate@5": round(hits[5] / n, 4),
        "hit_rate@10": round(hits[10] / n, 4),
        "mrr@10": round(rr_sum / n, 4),
        "n_items": len(items),
        "unmatched_gold": unmatched,
        "n_chunks": len(chunks),
        # Failures lead the sample. A cap taken in eval order hides whichever rows happen
        # to sort last, so a reviewer reading 12 examples can spend the whole sample on
        # rows that already pass and never see the miss that explains the score drop.
        "detail": ([d for d in per_item if not d["rank"] or d["rank"] > 5] + per_item)[:24],
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="BM25-over-vault scorer for the Lily autoresearch loop")
    ap.add_argument("--vault", required=True)
    ap.add_argument("--eval", dest="evalset", required=True)
    ap.add_argument("--config", help="JSON config; omit for baseline defaults")
    ap.add_argument("--out", help="write metrics JSON here")
    ap.add_argument("--primary", default="hit_rate@5")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--budget-min", type=float, default=0.0, help="abort (exit 3) past this wall clock")
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--set-baseline", action="store_true", help="also write baseline.json")
    ap.add_argument("--state-dir", default=".docs/autoresearch")
    args = ap.parse_args()

    if not os.path.isdir(args.vault):
        print(f"error: vault not found: {args.vault}", file=sys.stderr)
        return 4
    if not os.path.isfile(args.evalset):
        print(f"error: eval set not found: {args.evalset}", file=sys.stderr)
        return 4

    cfg = dict(DEFAULT_CONFIG)
    if args.config:
        with open(args.config, "r", encoding="utf-8") as fh:
            user = json.load(fh)
        # loop.sh passes the whole candidate wrapper {exp_id, change, config:{...}};
        # accept both the wrapper and a bare flat config.
        if isinstance(user.get("config"), dict):
            user = user["config"]
        unknown = set(user) - set(DEFAULT_CONFIG)
        if unknown:
            print(f"error: unknown config keys (refusing to silently ignore): {sorted(unknown)}",
                  file=sys.stderr)
            return 4
        cfg.update(user)

    t0 = time.time()
    os.makedirs(args.state_dir, exist_ok=True)
    sig = hashlib.sha256(json.dumps({
        "chunk": [cfg["chunk_words"], cfg["chunk_overlap"], cfg["fold_devanagari"],
                  cfg["strip_stopwords"], cfg["title_boost"], cfg["path_boost"],
                  cfg["tag_boost"]],
        "vault_mtime": max((os.path.getmtime(p) for p, _ in iter_notes(args.vault)), default=0),
    }, sort_keys=True).encode()).hexdigest()[:24]

    cache = os.path.join(args.state_dir, f"chunks-{sig}.json")
    if not args.no_cache and os.path.exists(cache):
        with open(cache, "r", encoding="utf-8") as fh:
            chunks = json.load(fh)
        cached = True
    else:
        chunks = build_chunks(args.vault, cfg, sig)
        with open(cache, "w", encoding="utf-8") as fh:
            json.dump(chunks, fh)
        cached = False

    try:
        items = load_eval(args.evalset, args.limit)
    except EvalFormatError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 4
    metrics = evaluate(cfg, chunks, items, args.primary, args.vault)
    metrics["index_seconds"] = round(time.time() - t0, 3)
    metrics["cached"] = cached
    if args.budget_min and (time.time() - t0) > args.budget_min * 60:
        metrics["status"] = "timeout"
        print(json.dumps(metrics, indent=2))
        return 3

    blob = json.dumps(metrics, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(blob + "\n")
    if args.set_baseline:
        with open(os.path.join(args.state_dir, "baseline.json"), "w", encoding="utf-8") as fh:
            snapshot = {k: v for k, v in metrics.items() if k != "detail"}
            json.dump(snapshot, fh, indent=2)
    print(blob)
    return 0


if __name__ == "__main__":
    sys.exit(main())
