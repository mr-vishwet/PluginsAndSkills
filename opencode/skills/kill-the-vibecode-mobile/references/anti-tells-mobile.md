# The Mobile Tell List

Defaults that mark a phone UI as generated. Sections 1 to 6 are for reading while
building. Section 7 is the mechanical search run before the audit. Section 8 is
the score.

A brief that explicitly asks for one of these wins. What is being attacked is
the unconsidered default, not the device.

## 1. Structure and layout

- A gradient AppBar, a gradient bottom bar, or a gradient header card. The single
  strongest native tell, and it appears regardless of vertical.
- Four identical rounded cards stacked as a feature list. The mobile version of
  three-in-a-row.
- A stats strip: big number, small label, three across, invented.
- Everything in a card with a shadow, on a screen that has no reason for
  grouping. Rules, whitespace, and position carry structure on a phone better
  than boxes do.
- One border radius applied to every widget regardless of role.
- A centered title bar with three competing actions plus a hamburger, when the
  screen has one job.
- Fixed `375`-style widths, hardcoded pixel heights, or a layout that assumes one
  device and breaks on a 320pt phone, a fold, or landscape.
- Content that stops at the notch or runs under the home indicator instead of
  using the safe area.
- A bottom navigation bar with five labels, or four tabs where two would do.
- Onboarding that is three carousel pages of stock illustration naming features,
  with the actual first task never shown.
- Section headers built as ALL-CAPS eyebrow labels above everything.
- A FAB that overlaps the last list row because the scroll view is not inset.

## 2. Color and material

- Indigo or purple on near-black, the default seed of most generated themes.
  Check whether `Colors.purple`, `#6C5CE7`, `#8B5CF6`, `#A855F7`, or `#7C3AED`
  is doing the accent work.
- Rainbow or tri-gradient surfaces, neon accents on `#0B0B0B`, glow and shadow
  effects around cards.
- Cream plus terracotta plus serif, or near-black plus acid green: the current
  generated-editorial look, now showing up in apps that are not editorial.
- Pure white backgrounds with pure black text everywhere, no surface hierarchy.
- Gradient text on a headline.
- Glassmorphism and blurred blobs behind content that then fails contrast.
- Dark mode implemented as inverted light mode: elevation wrong, surfaces flat,
  text contrast dropped.
- Semantic color misuse: red for a destructive label that is not destructive,
  green for a decorative accent.
- An accent color chosen from the framework default rather than from the brand.

## 3. Typography and iconography

- Roboto, Inter, Poppins, Manrope, or Space Grotesk as the whole identity.
- `google_fonts` pulling four families for one app.
- Icon families mixed on one screen: Material plus Cupertino plus Iconify plus a
  third-party pack, each with different stroke weight and optical size.
- Emoji standing in for icons, on buttons, tabs, or labels.
- An icon inside a tinted rounded square as decoration next to every row.
- Huge thin display weights that fail contrast at small sizes on a bright screen.
- Fixed pixel font sizes with no scaling path, so a user at 200 percent text
  gets clipped labels and overflow errors.
- Truncated text with no wrapping strategy and no minimum row height.
- Letter-spaced ALL-CAPS button labels on every button.

## 4. Copy and proof

- Generic labels: "Dashboard", "Home", "Settings" for screens that do one
  specific thing. Name by what the user is doing.
- "Welcome to the app", "Get started", "Explore features" as the entire
  onboarding narrative.
- A rating strip, download counts, or review quotes: `4.9`, `5.0 stars`,
  `10,000+ users`, `Trusted by`. Invented proof is the fastest way to make a
  screen read as generated, and on a store listing it is also a policy problem.
- Lorem ipsum, `placeholder text`, `Coming soon`, `TODO`, or a hardcoded fake
  balance, transaction, patient record, or streak presented as real data.
- Em dashes and en dashes in UI strings, and the "not just X, it's Y" formula.
- System language instead of the user's: "sync webhook" where the person manages
  "connected devices".
- Errors that apologize without saying what failed or what to do next, and empty
  screens with no next action.
- Buttons that do not name what happens: "Submit" instead of "Save changes".

## 5. Interaction and platform correctness

The half a screenshot hides, and the half users feel in the first ten seconds.

- Custom chrome that breaks the iOS back swipe or the Android predictive back.
- Tap targets under 44pt or 48dp, or targets touching each other with no gap.
- Pressed state missing entirely, so nothing confirms the tap landed.
- Feedback only at the end of a gesture instead of continuously during it.
- A modal sheet with no drag-to-dismiss and no way out except a small close icon.
- Destructive confirm dialogs on trivial actions, training users to click past
  the one that matters.
- No loading, empty, error, offline, or permission-denied state; a spinner
  forever, or a blank screen.
- Artificial delays added to fake a load.
- Keyboard covering the focused field, or the last field unreachable in a scroll.
- Lists built without recycling, so a long list janks on a mid-range phone.
- Animation on layout-driving properties instead of compositor-friendly ones,
  and no 60 or 120 fps check on real hardware.
- Haptics on everything, or on nothing meaningful.
- Reachability ignored: the primary action pinned to the top of a tall screen.
- No `Semantics` or accessibility labels on icon-only controls, and custom
  gestures with no keyboard or switch alternative.
- A signed-out or first-launch state that does not exist, so the app opens to an
  error.

## 6. Mobile web

- `100vh` for a full-screen layout, which is wrong the moment the browser chrome
  appears. Use the dynamic viewport units.
- `:hover` styles that stick after a tap on touch devices.
- The gray or blue tap highlight flash left visible.
- Inputs under 16px, which zoom the page and never zoom back out.
- `touch-action` unset on a horizontal carousel, so dragging scrolls vertically.
- Pull-to-refresh hijacking the scroll on a page that should just scroll.
- Long-press selecting a button's text label.
- Status bar color that does not match the app surface.
- No `viewport-fit=cover` while claiming the safe area insets with `env()`.
- Tap latency from a 300ms delay or a debounce on the input path.
- Testing only in Chrome's device frame. On the phone the layout, the scroll
  physics, the keyboard, and the paint cost are all different.

## 7. Mechanical search

`scripts/scan-tells-mobile.sh` runs six `grep -E` groups over Dart, Swift,
Kotlin, Java, JS, JSX, TS, TSX, CSS, HTML, Vue, and Ruby, prints the matching
lines, and exits `1` on any hit:

```sh
sh scripts/scan-tells-mobile.sh lib/ src/ app/ styles/
```

The exact patterns, so you can widen one without opening the script:

- `framework-defaults`: `\bInter\b|\bGeist\b|Space Grotesk|\bPoppins\b|\bManrope\b|google_fonts|useMaterial3: *false|Colors\.purple|Colors\.indigo`
- `slop-palette`: `#[Ff]4[Ff]1[Ee][Aa]|#D97757|#0[Bb]0[Bb]0[Bb]|#6C5CE7|#8B5CF6|#A855F7|#7C3AED|LinearGradient\(colors: *\[[^]]*Colors\.(purple|indigo)|backdrop-filter|BackdropFilter\(|BlurStyle\.|Colors\.black`
- `templated-structure`: `BorderRadius\.circular\(([1-9][0-9]{2,}|[5-9][0-9])\)|elevation: *([4-9]|[1-9][0-9])|blurRadius: *([2-9][0-9])|SizedBox\(height: *[1-9][0-9]{2,}|SizedBox\(width: *[1-9][0-9]{2,}|fontSize: *[3-9][0-9](\.[0-9]+)?,`
- `copy-glyphs`: `—|–|✨|🚀|⚡|🔥|→|·.*·|not just|it.s not|[Uu]nlock|[Ee]mpower|[Ss]eamless|revolutioniz|Get started|Welcome to`
- `fake-proof`: `4\.9|5\.0 stars|10,000|99\.9|[Tt]rusted by|[Oo]ver [0-9]+(,[0-9]{3})\+? (users|downloads|ratings)|lorem ipsum|Lorem|placeholder (text|copy|content)|TODO|FIXME|Coming soon|StarRating|rating: *[0-4]\.[5-9]`
- `platform-correctness`: `width: *375|height: *[1-9][0-9]{3}|MediaQuery[^;]*(375|414)|100vh|100vw|minWidth: *[123][0-9],|minHeight: *[123][0-9],|resizeToAvoidBottomInset: *false`

What each threshold means, because the numbers are deliberate:

- `elevation: 4` and up, `blurRadius: 20` and up, and `BorderRadius.circular(50)`
  and up are the values a generated theme picks; a 2 or a 12 is not a finding.
- `fontSize: 30` and up inside a widget means the screen is bypassing the type
  scale, which is what breaks at 200 percent text.
- `minWidth` or `minHeight` between 10 and 39 is a touch target under the 44pt
  and 48dp floor.
- Boundary-anchored font names keep "interactive" and "interest" from matching.
  `placeholder` is narrowed to `placeholder text|copy|content` so a real input
  attribute is not a finding.

Verified against the shipped fixtures: `tests/fixtures/slop.dart` produces 29
hits spread over all six groups and exits `1`;
`tests/fixtures/clean.dart` produces 0 hits in every group and exits `0`. Both
directions are re-runnable, and a checker that only ever goes green is worthless.

Two pattern rules learned by breaking them first:

- BSD `grep -E` has no lookahead. An early draft of this list used
  `100vh(?!\s*\(dvh)` and silently misbehaved on macOS. Keep patterns POSIX and
  test both directions instead of assuming PCRE.
- An earlier `paddingVertical: *[0-9]` rule flagged ordinary React Native
  spacing. It is gone. Precision beats coverage here: a noisy check gets
  ignored within a day.

A hit is a question, not a verdict. A `bottomNavigationBar` in a real tabbed app
is correct, and `Colors.black` in a true-black OLED theme may be a decision.

## 8. Score

| Group | Weight |
| --- | --- |
| Platform correctness and states (section 5) | 4 |
| Fake proof and invented data (section 4) | 3 |
| Structure defaults (section 1) | 2 |
| Palette and material (section 2) | 2 |
| Type and iconography (section 3) | 2 |
| Mobile web defects (section 6) | 2 |
| Copy mechanics (section 4, prose only) | 1 |

Report `Tells: N (list)`, one line per group, plus what was removed and what is
deliberately kept with the reason. Any of these is a fail regardless of total:
invented proof or data presented as real, broken back gesture, a screen that
overflows or clips at the largest supported text scale, missing dark mode, or a
main flow that cannot be completed.
