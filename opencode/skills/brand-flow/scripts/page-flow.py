#!/usr/bin/env python3
"""Inventory a site's page flow from the HTML it ships.

Fetches each path, then reports title, meta description, heading outline and
button labels. Headings in document order are the narrative a page tells, and
button labels are its calls to action, which is what a screen needs to copy.

Usage: page-flow.py <site> <path> [<path> ...] > flow.json
Discover the paths from the extracted brand spec rather than guessing them.
"""
import html
import json
import re
import subprocess
import sys

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
TAG = re.compile(r"<[^>]+>")


# Sites that animate headings often ship the same words twice: once split into
# spaced letters for the animation and once as real text. Drop the split layer.
SPLIT_LETTERS = re.compile(r"(?:\b\w\s){3,}")


def _split_layer(m: re.Match, whole: str) -> str:
    # A split run that real text follows is the animation layer, so drop it. A
    # split run at the very end is usually the word itself, so join it back.
    return "" if m.end() < len(whole) - 1 else m.group(0).replace(" ", "")


def text(s: str) -> str:
    out = re.sub(r"\s+", " ", html.unescape(TAG.sub(" ", s))).strip()
    fixed = SPLIT_LETTERS.sub(lambda m: _split_layer(m, out), out).strip()
    return fixed or out


def fetch(url: str) -> tuple[int, str]:
    r = subprocess.run(["curl", "-sL", "-A", UA, "-w", "%{http_code}", url],
                       capture_output=True, text=True)
    code = r.stdout[-3:]
    return int(code), r.stdout[:-3]


def unique(seq):
    seen, out = set(), []
    for x in seq:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def page(site: str, path: str) -> dict:
    url = site.rstrip("/") + "/" + path.lstrip("/")
    code, body = fetch(url)
    title = re.search(r"<title[^>]*>(.*?)</title>", body, re.S)
    desc = re.search(r'<meta name="description" content="([^"]*)"', body)
    out = {"path": "/" + path.lstrip("/"), "url": url, "status": code,
           "title": text(title.group(1)) if title else "",
           "description": html.unescape(desc.group(1)) if desc else ""}
    for level in (1, 2, 3):
        items = [text(x) for x in re.findall(rf"<h{level}[^>]*>(.*?)</h{level}>", body, re.S)]
        out[f"h{level}"] = unique([i for i in items if 0 < len(i) < 90])[:12]
    buttons = [text(b) for b in re.findall(r"<button[^>]*>(.*?)</button>", body, re.S)]
    out["buttons"] = unique([b for b in buttons if 0 < len(b) < 30])[:14]
    links = re.findall(r'<a[^>]+href="/([^"#?]*)"', body)
    out["internalPaths"] = unique(links)[:40]
    return out


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    site, paths = sys.argv[1], sys.argv[2:]
    pages = [page(site, p) for p in paths]
    json.dump({"site": site, "pages": pages}, sys.stdout, indent=1)
    print(file=sys.stderr)
    for p in pages:
        flag = "" if p["status"] == 200 else f"  [HTTP {p['status']}]"
        print(f"{p['path']:20} {p['title'][:52]}{flag}", file=sys.stderr)
        if p["h1"]:
            print(f"{'':20} h1: {p['h1'][0][:70]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
