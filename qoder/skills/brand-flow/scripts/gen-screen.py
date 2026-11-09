#!/usr/bin/env python3
"""Emit design-tool layer payloads from an extracted brand spec.

Reads a spec produced by the brand-flow method and prints FREE-format JSON for a
screen, so every colour, radius and type role comes from the measurement rather
than from memory. Nothing here is Cardboard specific: pass another spec and it
generates that brand.

Usage: gen-screen.py <spec.json> <screen> [--w 390 --h 844] [--x 0] > payload.json

Screens: home, pricing, recipes, desktop, mcp.
"""
import argparse
import json
import re
import sys


def argb(css):
    """CSS writes #RRGGBBAA; the design format reads ARGB. Reorder the pair."""
    h = css.lstrip('#').upper()
    return h[6:8] + h[0:6] if len(h) == 8 else h


def load(spec_path):
    s = json.load(open(spec_path))
    c, sh = s['color'], s['shape']
    radii = {}
    for r in sh.get('radiusCensus', []):
        try:
            radii[float(r['r'].replace('px', ''))] = r['uses']
        except ValueError:
            pass
    # The census includes 1 and 2 px radii that are really hairlines, so the
    # component roles snap to the usable part of the ladder.
    usable = [k for k in sorted(radii) if 2 <= k <= 24] or [4, 8, 12]
    token = float(re.search(r'[\d.]+', sh.get('radiusToken', '8px')).group(0))

    def pick(v):
        return min(usable, key=lambda k: (abs(k - v), k))
    chrom = {x['hex'].upper(): x['hex'] for x in c.get('chromatic', [])}
    return {
        'bg': argb(c['background']), 'fg': argb(c['foreground']),
        'strong': argb(c.get('textPrimary') or c['foreground']),
        'muted': argb(c['mutedForeground']), 'surface': argb(c['muted']),
        'surface2': argb(c['accent']), 'cta': argb(c['primary']),
        'ctaFg': argb(c['primaryForeground']), 'hair': argb(c['borderSubtle']),
        'hairStrong': argb(c['borderStrong']),
        'blue': argb(chrom.get('#2680D9', c['primary'])),
        'mint': argb(chrom.get('#3CDDA7', c['ring'])),
        'r': {'xs': pick(4), 'sm': pick(6), 'md': pick(token), 'lg': pick(12), 'pill': 999},
    }


def text(name, x, y, w, h, body, size, weight, color):
    face = {'light': 'Inter-Light', 'medium': 'Inter-Medium', 'regular': 'Inter-Regular'}[weight]
    return {"_t": "TEXT", "name": name, "pos": [x, y], "size": [w, h], "text": body,
            "font": face, "fontSize": size, "fill": color}


def rect(name, x, y, w, h, fill=None, r=None, grad=None):
    d = {"_t": "RECT", "name": name, "pos": [x, y], "size": [w, h]}
    if grad:
        d["fills"] = [{"type": 1, "opacity": 1, "enabled": True,
                       "gradient": {"type": 0, "from": [0, 0], "to": [1, 1],
                                    "stops": [{"pos": 0, "color": grad[0]}, {"pos": 1, "color": grad[1]}]}}]
    elif fill:
        d["fill"] = fill
    if r is not None:
        d["cornerRadius"] = [r]
    return d


def frame(name, x, y, w, h, layers, t, r=None, fill=None, border=None, vertical=True, spacing=8, pad=10, align=None):
    d = {"_t": "FRAME", "name": name, "pos": [x, y], "size": [w, h], "clipContent": True}
    if fill:
        d["fill"] = fill
    if r is not None:
        d["cornerRadius"] = [r]
    if border:
        d["borders"] = [{"type": 0, "color": border, "opacity": 1, "enabled": True}]
        d["thickness"] = 1
        d["linePos"] = 1
    al = {"vertical": vertical, "spacing": spacing, "padding": [pad, pad, pad, pad]}
    if align is not None:
        al["align"] = align
    d["autoLayout"] = al
    d["layers"] = layers
    return d


def chip(label, x, w, t, active=False):
    inner = [text("label", 10, 5, w - 20, 16, label, 12, 'medium', t['ctaFg'] if active else t['fg'])]
    return frame(label.replace(' ', '') + " chip", x, 0, w, 26, inner, t, r=t['r']['pill'],
                 fill=t['cta'] if active else t['surface'], border=None if active else t['hairStrong'],
                 vertical=False, spacing=0, pad=0)


def card(name, x, y, w, h, title, meta, t, grad, live=False):
    inner = w - 20
    thumb = h - 20 - 16 - 6 - 14          # pad, title, gap, meta
    return frame("Card " + name, x, y, w, h, [
        rect("thumb", 0, 0, inner, thumb, grad=grad, r=t['r']['md']),
        text("title", 0, thumb + 6, inner, 16, title, 13, 'medium', t['strong']),
        text("meta", 0, thumb + 22, inner, 14, meta, 11, 'regular', t['muted']),
    ], t, r=t['r']['lg'], fill=t['surface'], border=t['hair'], spacing=0, pad=10)


def home(w, h, t):
    inner = w - 40
    prompt = frame("Prompt bar", 20, 120, inner, 56, [
        text("prompt placeholder", 14, 19, inner - 120, 18, "What are we editing today?", 14, 'regular', t['muted']),
        rect("launch", inner - 92, 12, 80, 32, fill=t['cta'], r=t['r']['sm']),
        text("launch label", inner - 82, 20, 60, 16, "Launch", 13, 'medium', t['ctaFg']),
    ], t, r=t['r']['lg'], fill=t['surface'], border=t['hairStrong'], vertical=False, spacing=0, pad=0)
    chips = [chip("Auto", 0, 52, t, active=True), chip("UGC", 58, 52, t), chip("Explainer", 116, 78, t),
             chip("Montage", 200, 74, t)]
    row = frame("Recipe chips", 20, 92, inner, 26, chips, t, vertical=False, spacing=6, pad=0)
    grid = frame("Made with Cardboard", 20, 196, inner, 224, [
        frame("row 1", 0, 0, inner, 108, [card("cut", 0, 0, (inner - 12) / 2, 108, "Match cut", "0:48", t, ("2A2A2A", "141414")),
                                           card("doc", (inner + 12) / 2, 0, (inner - 12) / 2, 108, "Documentary", "3:12", t, ("2680D9", "141414"))],
             t, vertical=False, spacing=12, pad=0),
        frame("row 2", 0, 116, inner, 108, [card("ugc", 0, 0, (inner - 12) / 2, 108, "UGC ad", "0:22", t, ("3CDDA7", "141414")),
                                            card("cast", (inner + 12) / 2, 0, (inner - 12) / 2, 108, "Talking head", "1:05", t, ("404040", "0A0A0A"))],
             t, vertical=False, spacing=12, pad=0)], t, r=t['r']['lg'], fill=None, border=None, spacing=8, pad=0)
    export = frame("Export state", 20, 440, inner, 92, [
        text("title", 0, 0, inner - 20, 18, "Rendering your edit", 14, 'medium', t['strong']),
        text("detail", 0, 24, inner - 20, 15, "Captions burned, reframe locked, 4K ready", 12, 'regular', t['muted']),
        rect("track", 0, 50, inner - 20, 6, fill=t['surface2'], r=3),
        rect("progress", 0, 50, (inner - 20) * 0.62, 6, fill=t['mint'], r=3),
    ], t, r=t['r']['lg'], fill=t['surface'], border=t['hair'], spacing=6, pad=12)
    return [
        text("Wordmark", 20, 24, inner, 40, "Cardboard", 34, 'light', t['strong']),
        text("Tagline", 20, 66, inner, 18, "Make any video you can think of", 14, 'regular', t['fg']),
        row, prompt, grid, export,
    ]


def pricing(w, h, t):
    inner = w - 40
    def plan(name, x, price, blurb, feats, featured):
        rows = [text("plan name", 0, 0, 140, 18, name, 15, 'medium', t['strong']),
                text("price", 0, 24, 140, 34, price, 30, 'light', t['fg']),
                text("blurb", 0, 64, 140, 30, blurb, 11, 'regular', t['muted'])]
        rows += [text("f" + str(i), 0, 104 + i * 22, 140, 16, f, 12, 'regular', t['fg']) for i, f in enumerate(feats)]
        cta_y = 104 + len(feats) * 22 + 10
        rows.append(rect("cta", 0, cta_y, 150, 36, fill=t['cta'] if featured else t['surface2'], r=t['r']['sm']))
        rows.append(text("cta label", 0, cta_y + 10, 150, 16, "Get started" if featured else "Choose", 13,
                         'medium', t['ctaFg'] if featured else t['fg']))
        return frame("Plan " + name, x, 0, 150, 104 + len(feats) * 22 + 60, rows, t,
                     r=t['r']['lg'], fill=t['surface'], border=t['hairStrong'] if featured else t['hair'], spacing=0, pad=14)
    plans = frame("Plans", 20, 120, inner, 300, [
        plan("Lite", 0, "Free", "Included with the Mac app", ["Browser export", "Recipes"], False),
        plan("Pro", 170, "$24", "Per month, billed annually", ["Faster exports", "Shareable recipes", "No watermark", "Priority renders"], True),
    ], t, vertical=False, spacing=20, pad=0)
    return [
        text("Wordmark", 20, 24, inner, 40, "Pricing", 34, 'light', t['strong']),
        text("Sub", 20, 66, inner, 18, "For every stage of editing", 14, 'regular', t['fg']),
        plans,
        frame("Billing toggle", 20, 440, 200, 30, [
            rect("track", 0, 0, 200, 30, fill=t['surface'], r=t['r']['pill']),
            rect("knob", 104, 3, 92, 24, fill=t['cta'], r=t['r']['pill']),
            text("monthly", 14, 7, 80, 16, "Monthly", 12, 'regular', t['muted']),
            text("annual", 112, 7, 80, 16, "Annual", 12, 'medium', t['ctaFg']),
        ], t, vertical=False, spacing=0, pad=0),
    ]


def recipes(w, h, t):
    inner = w - 40
    rows = []
    y = 96
    for name, kind, dur in [("Talking head", "Podcast", "1:05"), ("UGC ad", "Commerce", "0:22"),
                            ("Travel vlog", "Story", "2:40"), ("Product demo", "Launch", "0:58"),
                            ("Montage", "Recap", "1:30")]:
        rows.append(frame("Recipe " + name, 20, y, inner, 74, [
            rect("thumb", 0, 0, 96, 58, grad=("2680D9", "141414") if y % 2 else ("3CDDA7", "141414"), r=t['r']['md']),
            text("name", 108, 4, inner - 190, 18, name, 14, 'medium', t['strong']),
            text("kind", 108, 26, inner - 190, 15, kind + " recipe", 12, 'regular', t['muted']),
            text("dur", 108, 44, 60, 14, dur, 11, 'regular', t['fg']),
            rect("remix", inner - 74, 16, 74, 28, fill=t['surface2'], r=t['r']['sm']),
        ], t, r=t['r']['lg'], fill=t['surface'], border=t['hair'], vertical=False, spacing=12, pad=8))
        y += 82
    return [text("Wordmark", 20, 24, inner, 40, "Recipes", 34, 'light', t['strong']),
            text("Sub", 20, 66, inner, 18, "Outcomes you can make today", 14, 'regular', t['fg'])] + rows


def desktop(w, h, t):
    inner = w - 40
    return [
        text("Wordmark", 20, 24, inner, 40, "Cardboard for Mac", 30, 'light', t['strong']),
        text("Sub", 20, 66, inner, 18, "The editor that edits, on your machine", 14, 'regular', t['fg']),
        rect("download", 20, 100, 180, 44, fill=t['cta'], r=t['r']['sm']),
        text("download label", 20, 113, 180, 18, "Download for Mac", 14, 'medium', t['ctaFg']),
        frame("Included", 20, 164, inner, 84, [
            text("title", 0, 0, inner - 20, 18, "Lite plan included", 14, 'medium', t['strong']),
            text("detail", 0, 24, inner - 20, 32, "Free to download. Your browser project opens here with the same library.", 12, 'regular', t['muted']),
        ], t, r=t['r']['lg'], fill=t['surface'], border=t['hair'], pad=14),
        frame("Library", 20, 264, inner, 240, [
            rect("clip " + str(i), (i % 3) * ((inner - 20 + 10) / 3), (i // 3) * 78, (inner - 20 - 20) / 3, 70,
                 grad=[("2680D9", "141414"), ("3CDDA7", "141414"), ("404040", "0A0A0A")][i % 3], r=t['r']['md'])
            for i in range(6)], t, vertical=False, spacing=10, pad=0),
    ]


def mcp(w, h, t):
    inner = w - 40
    steps = ["Connect", "Attach clips", "Ask", "Launch", "Finish in Cardboard"]
    return [
        text("Wordmark", 20, 24, inner, 40, "In ChatGPT and Claude", 28, 'light', t['strong']),
        text("Sub", 20, 66, inner, 18, "Your video editor, now in the chat you already use", 14, 'regular', t['fg']),
        frame("Agents", 20, 100, inner, 44, [
            rect("ChatGPT", 0, 0, (inner - 10) / 2, 44, fill=t['cta'], r=t['r']['sm']),
            rect("Claude", (inner + 10) / 2, 0, (inner - 10) / 2, 44, fill=t['surface2'], r=t['r']['sm']),
        ], t, vertical=False, spacing=10, pad=0),
        frame("How to connect", 20, 160, inner, 210, [
            text("step " + str(i), 0, i * 40, inner - 20, 24, f"{i + 1}.  " + s, 13, 'regular', t['fg'] if i < 4 else t['muted'])
            for i, s in enumerate(steps)], t, spacing=8, pad=12, fill=t['surface'], border=t['hair'], r=t['r']['lg']),
    ]


SCREENS = {'home': home, 'pricing': pricing, 'recipes': recipes, 'desktop': desktop, 'mcp': mcp}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('screen', choices=sorted(SCREENS) + ['doc'])
    ap.add_argument('--w', type=int, default=390)
    ap.add_argument('--h', type=int, default=844)
    ap.add_argument('--x', type=int, default=0)
    a = ap.parse_args()
    t = load(a.spec)
    if a.screen == 'doc':
        boards = []
        for i, name in enumerate(['home', 'pricing', 'recipes', 'desktop', 'mcp']):
            b = {"_t": "FRAME", "name": "Screen " + name, "pos": [i * (a.w + 60), 0], "size": [a.w, a.h],
                 "clipContent": True, "fill": t['bg'],
                 "borders": [{"type": 0, "color": t['hair'], "opacity": 1, "enabled": True}],
                 "thickness": 1, "linePos": 1, "layers": SCREENS[name](a.w, a.h, t)}
            boards.append(b)
        json.dump(boards, sys.stdout, separators=(',', ':'))
        print(file=sys.stdout)
        return
    board = {"_t": "FRAME", "name": "Screen " + a.screen, "pos": [a.x, 0], "size": [a.w, a.h],
             "clipContent": True, "fill": t['bg'],
             "borders": [{"type": 0, "color": t['hair'], "opacity": 1, "enabled": True}],
             "thickness": 1, "linePos": 1,
             "layers": SCREENS[a.screen](a.w, a.h, t)}
    json.dump([board], sys.stdout, separators=(',', ':'))
    print(file=sys.stdout)


if __name__ == '__main__':
    main()
