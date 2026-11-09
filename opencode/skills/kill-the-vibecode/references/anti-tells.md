# The Tell List

Categorized defaults that mark a page as generated. Use during the build, then
run section 7 as a mechanical search, then score with section 8.

Where a brief explicitly asks for something on this list, the brief wins. The
problem these entries describe is a default chosen without a reason, not the
device itself.

## 1. Layout and structure

- Three identical feature cards in a row. The single strongest giveaway.
- Everything placed inside a card: features, benefits, testimonials, all
  equally sized and equally loud.
- Bento grids assembled for their own sake, with cells sized by the template
  rather than by the content.
- Equal-weight sections in a row of the same width and padding.
- Three pricing tiers with a middle one flagged "popular", when the user never
  supplied pricing.
- Hero that opens with a big number, a small label, supporting stats, and a
  gradient accent, because that is the default treatment rather than the best
  one for this subject.
- Checkmark bullet lists standing in for explanation.
- Decorative terminal windows and fake code panes on pages that are not about a
  developer tool.
- Numbered markers `01 / 02 / 03` where the content is not actually a sequence.

## 2. Visual and color

- Purple-and-black themes. Harsh gradients. Rainbow palettes. Neon accents.
  Generic pastels.
- Pure `#FFFFFF` as the page background.
- Warm cream near `#F4F1EA` with a high-contrast serif display and a terracotta
  or warm-clay accent near `#D97757`. This is the current signature of generated
  pages and reads as a tell on any brief that did not ask for it.
- Near-black background with one bright acid-green or vermilion accent.
- Tinted near-blacks such as `#0B0B0B` or `#111` used as a stand-in for real
  black with no decision behind it.
- Radial orbs, glow fields, aurora blobs, floating shapes, dot grids, grid
  line textures, noise overlays.
- Liquid glass, glassmorphism, decorative colored stripes, gradient washes used
  purely as decoration.
- A soft grey shadow, typically `rgba(0,0,0,.1)`, under every element.
- One border radius applied to everything regardless of hierarchy.
- Soft rounded corners throughout with no structural reason.
- Decoration that outruns the product: a full screen of effects and no useful
  screenshot or demonstration anywhere.
- Broadsheet layouts with hairline rules, zero radius, and dense newspaper
  columns, chosen as a default rather than for an editorial subject.

## 3. Typography and icons

- Inter, Geist, Space Grotesk. These are the three most common generated
  headlines. Use a readable alternative or a proper system font stack unless the
  identity plan deliberately chose one.
- A monospace face for small data labels purely to look technical.
- One fixed `letter-spacing` used at every size. Large display text wants
  negative tracking, small text wants near-zero or slightly positive.
- Serif body copy at sans line-height, or any body line length past about 80
  characters.
- Lucide icons. Icons used as decoration rather than to clarify an action.
- Sparkle icons, and any emoji used as interface iconography.
- Single-word accents in a headline via italic, bold, or a color change.
- ALL-CAPS tracked eyebrow labels above every heading, and typographic labels
  above content that carry no information.
- Meta strings joined with middle dots, in the form `A · B · C`.
- Trailing `→` appended to link and button text.
- A typeface treated as a neutral delivery vehicle rather than as part of the
  design, when the identity plan said it would carry personality.

## 4. Proof and content

- Five-star ratings, "trusted by thousands", anonymous praise, and invented
  customer logos. Suspiciously perfect proof with no source.
- Statistics and metrics with no derivation and no owner.
- Generic headlines that could sell anything: "The future of productivity",
  "Unlock your potential", "Work smarter, not harder".
- Copy that describes the category instead of the actual task the product
  performs.
- Features listed as nouns with no consequence for the reader.

## 5. Copy mechanics

- Em dashes and en dashes.
- The rejection formula: "It's not just X, it's Y", "More than a tool, a
  partner".
- Passive voice on calls to action: "Submit" where "Save changes" is correct.
- A CTA that names one thing and the confirmation that names another.
- System language instead of user language: "webhook configuration" where the
  user manages "notifications".
- Apologizing or vague errors, and empty screens with no next step.
- Jargon, filler, and cleverness where a plain noun would be understood faster.

## 6. Behavior

The half that finishes the signature, and the half a screenshot hides.

- Buttons that go nowhere, links that 404, and nav items that scroll to nothing.
- A mobile menu that breaks, overflows, or cannot be closed.
- No visible keyboard focus ring on interactive elements.
- Inputs without labels, and validation that only fires on submit.
- No loading state, no error state, no empty state, and no explanation of what
  happens while data arrives.
- Artificial delays added to simulate loading.
- Every hover animating, every section fading and sliding up on entry, motion
  that answers nothing.
- `prefers-reduced-motion` ignored, and normal scrolling hijacked by a
  scroll-jacked pin with no simple mobile fallback.
- No Terms of Service or Privacy Policy anywhere on a real business site.
- Layout that breaks when text is scaled up, because spacing is fixed px while
  type is `rem`.

## 7. Mechanical search

Run `scripts/scan-tells.sh` against the source before the audit report. It exits
`1` when any group matches and prints the matching lines.

```sh
sh scripts/scan-tells.sh src/ index.html styles.css
```

The five groups it searches, as `grep -E` disjunctions, if you need to run them
separately or widen one:

- `fonts-and-icons`: `\bInter\b|\bGeist\b|Space Grotesk|[Ll]ucide|react-icons|@tabler`
- `palette-and-decoration`: `#ff6|[Pp]urple|#8B5CF6|#A855F7|#7C3AED|#F4F1EA|#D97757|#0B0B0B|linear-gradient|radial-gradient|backdrop-filter|blur\(|\bnoise|\baurora|\bblob|\borb`
- `templated-structure`: `rounded-(2|3|xl|2xl|3xl)|shadow-(md|lg|xl)|grid-cols-3|feature-card|testimonial|pricing-tier|bento`
- `copy-glyphs`: `—|–|✨|🚀|⚡|🔥|→|·.*·|not just|it.s not|unlock|empower|seamless|revolutioniz`
- `fake-proof`: `5\.0 stars|4\.9|10,000|99\.9|[Tt]rusted by|lorem ipsum|Lorem|placeholder (text|copy|content)|TODO|FIXME|Coming soon`

Pattern notes, learned by testing both directions rather than by assumption:

- Fonts use word boundaries. `Inter` without them matches every "interactive"
  and "interest" on the page and makes the check noise.
- `placeholder` is narrowed to `placeholder text|copy|content`. A plain
  `placeholder=` attribute on an input is correct HTML and is not a tell.
- `blur(` is targeted so ordinary `filter` uses stay quiet while a glass effect
  is caught.
- `noise`, `aurora`, `blob`, and `orb` carry a leading word boundary. An early
  draft used them bare, and because the search is case-insensitive,
  `separatorBuilder` matched `orb` inside it. The boundary goes on the front
  only: `auroraBg` and `.orb {` are still findings, `separorb` is not.
- A clean page built to these rules scores 0 hits across all five groups, so a
  green run means the search found nothing, not that the search is broken.
- A deliberately templated page scores 22 hits across all five groups, which is
  the check that the list still has teeth.
- Cross-check: this scanner on the mobile half's clean Dart fixture returns 0,
  and on its templated Dart fixture it still returns 15 hits, so the shared
  tells are caught whichever language the code is written in.

Every hit needs a reason or a fix. A hit is not automatically a defect: a page
about gradients may legitimately use one, and the user's brief overrides.

Also confirm by reading, not searching: each section's composition differs
because its content differs, the strongest evidence occupies the most space, and
the hero shows the real product.

## 8. Score

Count distinct tells actually present, weighted:

| Group | Weight |
| --- | --- |
| Behavior (section 6) | 3 |
| Fake proof and invented content (section 4) | 3 |
| Layout defaults (section 1) | 2 |
| Palette and decoration (section 2) | 2 |
| Type and icons (section 3) | 2 |
| Copy mechanics (section 5) | 1 |

Report as `Tells: N (list)`, one line per group, plus what was removed and what
is deliberately kept with the reason. Any live behavior tell or any invented
proof is a fail regardless of the total, because those two categories are what a
visitor meets within the first minute.
