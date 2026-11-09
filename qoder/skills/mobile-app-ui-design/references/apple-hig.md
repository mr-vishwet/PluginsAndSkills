# Apple Human Interface Guidelines — iOS Essentials

Platform-native rules distilled from Apple's Human Interface Guidelines (current "Liquid Glass" design language). Use these when the target is a real iOS/iPadOS app (SwiftUI/UIKit) — they take precedence over the generic skill defaults where they conflict, because shipping on-platform means looking and behaving like the platform. For web/React artifacts, treat them as principles rather than literal APIs.

Source: developer.apple.com/design/human-interface-guidelines (Foundations + Patterns).

## The Liquid Glass model (read this first)

Apple's current system splits the screen into two layers:

- **Content layer** — your actual content. Use **standard materials** (blur, vibrancy) here, never Liquid Glass.
- **Functional layer** — controls and navigation (tab bars, sidebars, toolbars) **float above** content on **Liquid Glass**, a dynamic material that refracts and adapts to whatever scrolls beneath it.

Consequences for layout:
- **Extend content to the screen edges.** Backgrounds and scroll views run edge-to-edge and *under* the floating controls — controls are on a separate plane, not inline. Account for content peeking through.
- Use a **scroll edge effect** (system-provided blur/opacity transition) instead of a hard background to separate content from the control area.
- **Don't put Liquid Glass in the content layer**, and apply it to custom controls only sparingly — overuse distracts from content. System components adopt it automatically.
- Regular vs clear variant: **regular** (blurs/adjusts luminosity for legibility) for text-heavy components (alerts, sidebars, popovers); **clear** (highly translucent) only over rich media, and add a ~35% dark dimming layer if the underlying content is bright.

## Layout

- **Respect safe areas, layout margins, and guides.** Safe areas avoid Dynamic Island, camera housing, and the bars. Don't hand-place content where the system reserves space.
- **Reading order = importance.** People scan top→bottom, leading→trailing. Put the most important items top-leading. Honor right-to-left layouts.
- **Group related items** with negative space, background shapes, materials, or separators — keep content and controls clearly distinct.
- **Align components** to a shared grid; alignment + indentation communicate hierarchy and make scanning effortless.
- **Progressive disclosure** for large/hidden collections — reveal partial items or use disclosure controls to hint there's more.
- **Adapt to context**: device sizes, orientation, Dynamic Type, Display Zoom, external displays, locale/RTL. Test largest and smallest layouts first.

## Typography

- **Use the system fonts** (SF Pro, SF Compact, New York) unless brand demands otherwise — they ship optical sizing, correct tracking, and Dynamic Type for free.
- **iOS/iPadOS: 17 pt default body, 11 pt minimum.** (macOS 13/10, tvOS 29/23, visionOS 17/12, watchOS 16/12.)
- **Avoid light font weights**; if a custom thin font is required, size up for legibility.
- **Convey hierarchy with the built-in text styles** (Large Title, Title 1–3, Headline, Body, Callout, Subheadline, Footnote, Caption 1–2) — they scale correctly with Dynamic Type. Differentiate with size, weight, and color, not weight alone.
- **Support Dynamic Type.** Test at the largest accessibility sizes; layouts must reflow, not clip or truncate. Limit the number of typefaces/styles on a screen.

## Color

- **Prefer system semantic colors; never hard-code system color values.** Documented values shift between releases — apply them via API (`Color`, `UIColor.label`, etc.).
- **Dynamic colors are defined by purpose, not appearance** (e.g. view backgrounds at hierarchy levels, label/link/separator foregrounds). Don't repurpose them (don't use `separator` as text, or `secondaryLabel` as a background).
- **Ship light + dark + increased-contrast variants** for every custom color (Color Set in the asset catalog) — required even if the app is single-appearance, for Liquid Glass adaptivity.
- **Label hierarchy via opacity-backed semantic colors**: primary / secondary / tertiary / quaternary label colors adapt automatically.
- **Accent color** drives interactivity. Apply color to a control's Liquid Glass *background* for primary actions (not to the symbol/text). Apply color sparingly — colorful backgrounds → prefer monochromatic toolbars/tab bars.
- **Never rely on color alone** to convey state/meaning — pair with text, shape, or SF Symbol. Mind cultural color meaning (red = danger vs. fortune).

## Materials & Dark Mode

- **Don't offer an app-specific appearance toggle.** Respect the systemwide Light/Dark/Auto choice — an in-app override makes people set the same thing twice and reads as broken.
- **Use semantic/system colors and SF Symbols** so everything adapts to Dark Mode automatically; supply separate light/dark image assets only when one doesn't read in the other.
- **Contrast: 4.5:1 minimum** for text/icons; **strive for 7:1** on custom small text. Verify in *both* appearances and with Increase Contrast / Reduce Transparency on.
- **Vibrant colors on top of materials** stay legible across contexts. Thicker material = more contrast; thinner = more background context retained.
- Soften pure-white image backgrounds in Dark Mode so they don't glow.

## SF Symbols

- **Use SF Symbols** wherever an icon is needed — 6000+ symbols that match the system fonts, ship multiple weights/scales, and adapt to Dynamic Type and Dark Mode.
- **Match symbol weight and scale to the adjacent text.** Tint with dynamic colors or vibrancy. Prefer a symbol over a custom glyph for anything the system already has.

## Accessibility (non-negotiable on-platform)

- **Minimum control/tap target: 44×44 pt.**
- **Contrast** meets WCAG AA (use Accessibility Inspector / a contrast calculator); provide a higher-contrast scheme when Increase Contrast is on.
- **Support Dynamic Type up to ≥200%** (watchOS ≥140%) without breaking layout.
- **More than color alone** for state, interactivity, and information.
- **Label everything for VoiceOver** (`accessibilityLabel`, hints, identifiers); test with VoiceOver, Switch Control, Full Keyboard Access.
- **Honor Reduce Motion**: when on, cut automatic/repetitive animation — zooming, scaling, peripheral/parallax motion — and offer a crossfade instead. (SwiftUI: `@Environment(\.accessibilityReduceMotion)`.)

## Onboarding (Apple's stance)

Apple's official guidance aligns with — and sharpens — the patterns in `onboarding-flows.md`:

- **Fast, fun, and optional.** Onboarding happens *after* launch completes; it is not the launch/splash screen. Ideally the app is self-explanatory and needs none.
- **Teach through interactivity**, not slides — let people safely perform the real action while learning.
- **Prefer context-specific tips over one upfront flow.** Surface a tip next to the relevant UI when the user reaches it (Apple's **TipKit**). Lets people learn one thing at a time.
- **Make any tutorial skippable**; don't re-show it on later launches; keep it findable later (Help/Settings).
- **Postpone nonessential setup.** Ship sensible defaults so people can start immediately — don't front-load configuration.
- **Integrate permission requests into onboarding to show *why* and the benefit** of granting — exactly the pre-permission priming pattern. Otherwise request at first point of use. (See `onboarding-flows.md` → "Prime before you ask.")
- **Let people experience the app before prompting for ratings or purchases** — engagement first, ask later. (Mirrors "earn the paywall.")
- Keep onboarding about *your* app, not how to use the device/system.

## Feedback

- **Match the significance of the information to the level of interruption.** Passive status display for ambient info; an interrupting **alert only for critical, actionable** info (overusing alerts dilutes them).
- **Make feedback accessible by combining channels** — color + text + sound + haptics — so it lands whether the device is silenced, the user looks away, or VoiceOver is on.
- **Integrate status feedback near the item** it describes (unread count in the toolbar) instead of forcing a separate screen.
- **Warn before unexpected, irreversible data loss** — but *don't* warn when the loss is the expected result of the action.
- **Confirm significant completed actions** (e.g. a successful payment); reserve confirmation for things important enough that people need to know when they *fail*.
- **When a command can't run, show it and explain why.**
- Use **haptics** purposefully for tactile confirmation (see HIG → Playing haptics).

## How this maps to the generic skill

| Generic skill says | Apple HIG sharpens it to |
|---|---|
| Max 4 sizes / 2 weights, opacity for hierarchy | Use the built-in text styles + Dynamic Type; primary/secondary/tertiary/quaternary label colors |
| 60/30/10, accent at 10% | Semantic system colors + a single accent; color on Liquid Glass backgrounds for primary actions only |
| 8-pt grid, thumb zone | 8-pt grid + safe areas/layout margins; controls float on the Liquid Glass layer, content edge-to-edge |
| Soft shadows | Prefer materials (blur/vibrancy) + scroll edge effects over drawn shadows on iOS |
| 44×44 tap targets, contrast | 44×44 pt minimum; WCAG AA (4.5:1), 7:1 for custom small text; Dynamic Type ≥200%; Reduce Motion |
| Peak-End, emotional feedback | Match feedback significance to interruption; multi-channel (haptics included); confirm only what matters |
