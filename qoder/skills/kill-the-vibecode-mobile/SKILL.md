---
name: kill-the-vibecode-mobile
description: >-
  Make AI-built mobile app UI stop looking AI-built, for native and cross
  platform apps (Flutter, SwiftUI, Jetpack Compose, React Native) and for the
  mobile web. Use when designing, building, restyling, or reviewing app screens,
  flows, onboarding, bottom sheets, tab bars, dashboards, or store screenshots,
  including "make the app look professional", "this looks like a template",
  "design my Flutter screens", "make it feel native", and domain-specific asks
  for fintech, health, ecommerce, education, fitness, productivity, or social
  apps. Enforces a real-screen gate, per-vertical identity grounding, platform
  correctness, domain-specific tells, and a visual audit at large text on a real
  device. For desktop and marketing websites use kill-the-vibecode instead.
user-invocable: true
argument-hint: <platform, vertical, the real screens and data you have>
---

# Kill The VibeCode: Mobile

Mobile has its own slop signature, and a small screen makes each default
louder. The gradient AppBar, the four identical rounded cards, the mismatched
icon set, the emoji on a button, the invented 4.9-star strip, the screen that
ignores the safe area and blows up at 200 percent text size. None of those are
proof of AI alone. Together they read as generated in under a second.

The mobile web counterpart has a separate tell set: sticky hover states, the
`100vh` bug, inputs that zoom the page, content under the notch, and a tap that
feels laggy. Both are covered here.

## Scope

Applies to app screens and flows in Flutter, SwiftUI or UIKit, Jetpack Compose
or Views, React Native, and to responsive or mobile-first web UI. For desktop
layouts and marketing pages use the `kill-the-vibecode` skill. Where both apply
to one project, this skill governs anything touched with a thumb.

An explicit user brief overrides the lists below, including when it asks for
something called a tell.

If the user also has `mobile-app-ui-design` installed, that skill supplies
positive design guidance, HIG mapping, and onboarding benchmarks. This one
supplies the tells, the gate, and the audit. Read both when both are available.

## Sequence

### 1. Screen gate (blocking)

Collect before designing:

- Platform and target: which OS versions, smallest phone you will support, fold
  or tablet behavior
- Vertical and audience: who uses it, with what hand, in what context
- The real screens and flow this version needs
- Real data shape: what a populated list, an empty list, and a failed load look
  like
- Brand assets: logo, wordmark, product photography, brand colors, the icon set
  in use
- Existing theme or design system, and whether Material 3 or Cupertino is the
  base
- What offline, permission-denied, and loading actually mean here

Missing anything above, ask and stop. Do not substitute a generic mockup, stock
illustration, invented metrics, or a fake review strip. Never hand-recreate a
logo the user supplied.

Anything you must write because the user has not supplied it is labelled
`DRAFT, needs your review`, never presented as finished.

### 2. Ground it in the vertical, then in real apps

Before choosing a single color, name three shipped apps in the same vertical
whose UI you are modeling the quality of, not copying, and say what each gets
right about information density, color role, and navigation. Real references are
the only reliable escape from the median: browse
[Mobbin](https://mobbin.com/), the platform's design awards finalists, or the
vertical's own market leaders.

Then run the sameness test on your plan for that vertical:

> Would this exact plan be what I produce for any other app in this category?

If yes, revise and say what changed. Per-vertical defaults and what a real
operator in that field actually expects are in
[references/mobile-verticals.md](references/mobile-verticals.md).

### 3. Identity plan as tokens, before widgets

Write, and keep short:

- **Color**: 4 to 6 named roles mapped onto the platform's own slots, light and
  dark. Surface, on-surface text, one accent, semantic states (success,
  warning, error), and what the elevation color does in dark mode.
- **Type**: which families, mapped onto the platform type scale. SF and Roboto
  or a custom face, with roles: display, headline, title, body, label. Decide
  what happens at the largest accessibility text size before writing a widget.
- **Shape and spacing**: one radius scale with a stated reason for each step,
  one spacing rhythm, and the elevation rules. One radius on everything is a
  default, not a decision.
- **Iconography**: exactly one family. Mixed Material plus Cupertino plus a
  third-party pack is a tell and a craft failure.
- **Motion**: name the one or two transitions that carry meaning, with the
  spring or duration values.

### 4. Build against the tells

Read [references/anti-tells-mobile.md](references/anti-tells-mobile.md) while
building. Platform correctness is the floor, not a bonus:

- Respect safe areas, and let content scroll under translucent bars rather than
  stopping at them.
- Minimum touch targets: 44pt on iOS, 48dp on Android, with spacing between them.
- Support the platform's text scaling. iOS Dynamic Type and Android font scale
  up to 200 percent, or 340 percent where the app claims support. Nothing may
  clip, overlap, or overflow at that size. Spacing in relative units that scale
  with type, not fixed pixel values that fight it.
- Ship both appearances. A light-only or dark-only app is unfinished, and dark
  mode is not inverted light: surfaces, elevation, and contrast all change.
- Honor the back gesture and never trap the user. Custom chrome that kills the
  iOS swipe-back is a regression users feel immediately.
- Handle the keyboard: nothing important sits under it, the focused field stays
  visible, and a scroll view can still reach the last field.
- Haptics and sound only on meaningful commits, never on every tap.
- Real states per screen: loading, empty, error, offline, permission denied,
  and the signed-out case. Each says what happened and what to do next.
- Reduced motion and increased contrast both supported on the web surfaces.

### 5. Audit before reporting done

1. Run `scripts/scan-tells-mobile.sh` over the source. Fix or justify every hit.
2. Build the screen set visually at three conditions minimum: smallest supported
   phone, largest accessibility text scale, and both light and dark. In Flutter
   use `matchesGoldenFile` goldens; on other platforms use screenshot tests or a
   device farm. Overflow errors, truncation, and dark-mode contrast failures
   count as failures, not warnings.
3. Run on a real device. Emulators hide the tap latency, the 100 percent
   brightness glare, and the safe-area problems that make it feel generated.
4. Complete the main flow end to end with real data. Tap every element in the
   tab bar or bottom nav. Open the sheet and dismiss it with the gesture.
5. Read every label at arm's length in one hand. Emoji, ALL-CAPS eyebrows, and
   trailing arrows are defects on a phone, not style.
6. Score against section 8 of the tells file and state the score.
7. Report which device, OS version, text scale, and appearance you actually
   tested, and what remains untested. Never claim a device check you did not run.

## Invention is forbidden

No invented ratings, download counts, prices, patient or account balances,
transactions, followers, streaks, or progress percentages presented as real. If
a screen needs sample content to be reviewable, mark it as sample data in code
and say so in the report. Never invent legal text, health claims, financial
disclaimers, or store listing copy: mark those `DRAFT, needs review`.

## References

- [references/mobile-native.md](references/mobile-native.md): the MIT-licensed
  `mobile-native` skill from Emil Kowalski, verbatim, with its license. The
  symptom-and-fix table for making mobile web UI feel installed. Ignore its
  "Initial Response" section; it belongs to that skill, not to this workflow.
- [references/mobile-verticals.md](references/mobile-verticals.md): per-vertical
  defaults, what real operators expect, and the domain checks.
- [references/anti-tells-mobile.md](references/anti-tells-mobile.md): the tell
  list, the scanner patterns, and scoring.
- [references/upstream-sources-mobile.md](references/upstream-sources-mobile.md):
  Apple HIG, Material 3, Flutter docs, Mobbin, and the current tell articles,
  with what to pull each one for.
- For motion and type craft values, the web skill's
  `../kill-the-vibecode/references/apple-design.md` carries the spring,
  interruptibility, and optical-sizing tables.
