---
name: brand-flow
description: Extract a real brand system from a live website and map its full page flow, then generate design screens from that extracted spec only. Use when asked to match a site's theme colors and branding, clone a visual identity into a design file, build a themed prototype, or produce every screen of a product's visual flow from its own published styles. Activates on "match their theme", "extract the branding", "get their exact colors", "all pages of the visual flow", "clone the style", "brand spec".
---

# Brand Flow

Extract what a site actually renders, not what its stylesheet claims, then drive
design generation from the measured spec.

## Why not read the CSS

A production stylesheet declares far more tokens than the page uses. Reading
`colors.css` gives you a palette the designer may never have applied. The
rendered DOM gives you the truth: which surface colour is on 141 elements, which
text colour carries 846 of them, which radius repeats, and which display face is
actually on the `h1`. Both are cheap, so take both and prefer the rendered one.

Two traps this avoids:

- **Hidden accents.** A site whose CSS variables are all neutral grey can still
  paint its primary button a saturated blue. Only the rendered census finds it.
- **Wrong family.** The declared `font-family` stack often names a fallback that
  never loads. The computed value on the real heading is what to copy.

## Step 1, tokens

Run `scripts/extract-brand.js` in the page (browser evaluate, save the result to
a file rather than into context). It returns:

| Key | What it answers |
| --- | --- |
| `vars` | every CSS custom property declared, first value wins |
| `els` | computed style of `html body h1 h2 h3 h4 p a button` |
| `bgs`, `colors` | rendered surface and text colours, by frequency |
| `radii` | corner radii by frequency |
| `typeScale` | `size/weight` pairs on headings and body, by frequency |
| `fonts` | font families by frequency |
| `links`, `nav` | the site's own internal graph |

Record the viewport it ran at. Type and colour are viewport independent;
spacing, layout and section order are not, and a spec captured at 531 px will
mislead you about a desktop layout.

## Step 2, flow

`scripts/page-flow.py <site> <paths...>` fetches each page and extracts title,
meta description, `h1`, `h2`, `h3` and button labels. That is the page inventory
and, in document order, the narrative each page tells. Discover the path list
from `links` and `nav` from step 1 rather than guessing URLs.

## Step 3, derive the spec

Write one JSON file with `color`, `type`, `shape`, `elevation` and `flow`.
Derive every value from the extraction; nothing hand-typed. Keep the measured
frequencies next to the values so a later reader can tell a system colour from a
one-off. `references/cardboard.json` is a worked example.

Then write the flow as prose in `references/<brand>-flow.md`: for each page, its
job in the funnel, the order of its sections, and its single call to action.

## Step 4, generate from the spec only

Every screen you produce must take its colours, type roles, radii and borders
from the spec file. If a value is missing, go back and measure it; do not invent
one. Generate all screens from the same spec object so they cannot drift.

`scripts/gen-screen.py <spec.json> <screen|doc>` turns a spec into layer payloads.
It carries no brand values of its own: colours, radii and type roles all resolve
through the spec file, and it converts CSS `#RRGGBBAA` into the ARGB order the
design format reads. `doc` emits every screen in one pass so they cannot drift
from each other. Check the arithmetic after generating: the deepest child's bottom
edge must sit inside its container's padding box. That test caught a 2 px overflow
in a card here.

When the target is a design document rather than markup, prefer one authoring
call per screen. Several tools append children in document order and re-run
layout per call, which silently reorders anything you add afterwards.

## Verify

Re-measure after generating. Compare your spec against what the output actually
carries, and check the output renders the same census you extracted: same
background, same text colour, same radius set, same display face at the same
weight. A theme you cannot re-measure is a theme you guessed.

## Rules

- Never substitute a plausible colour for a measured one.
- Never trust a declared font that the rendered element does not use.
- Note the sampled viewport in the spec, always.
- Keep the frequency counts; they are the evidence.
- If the brand has no accent in its tokens, look for one in its buttons before
  concluding there is none.
