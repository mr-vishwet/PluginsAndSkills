# Mobile Sources and When to Pull Each

Every URL here was fetched and returned `200` on 2026-11-01. Nothing in this
list is bundled except the MIT `mobile-native` skill.

| Source | URL | Pull it for |
| --- | --- | --- |
| Apple Human Interface Guidelines, Typography | <https://developer.apple.com/design/human-interface-guidelines/typography> | Dynamic Type, text scaling, SF weights |
| Apple HIG, Materials | <https://developer.apple.com/design/human-interface-guidelines/materials> | translucency, bars, dark surfaces |
| Apple HIG, Motion | <https://developer.apple.com/design/human-interface-guidelines/motion> | transitions, reduced motion on iOS |
| Apple UIKit accessibility | <https://developer.apple.com/documentation/uikit/accessibility> | VoiceOver, traits, focus order |
| Material 3, type scale tokens | <https://m3.material.io/styles/typography/type-scale-tokens> | the token names a Compose or Flutter Material 3 theme should use |
| Material 3, color roles | <https://m3.material.io/styles/color/roles> | surface, on-surface, container roles instead of raw hex |
| Android design, mobile accessibility | <https://developer.android.com/design/ui/mobile/guides/foundations/accessibility> | 48dp targets, TalkBack, contrast |
| Android dark theme guide | <https://developer.android.com/develop/ui/views/theming/darktheme> | correct dark mode, not inverted light |
| Flutter, design overview | <https://docs.flutter.dev/ui/design> | Material and Cupertino positioning |
| Flutter, `useMaterial3` | <https://api.flutter.dev/flutter/material/ThemeData/useMaterial3.html> | whether the app is on Material 2 defaults |
| Flutter, `matchesGoldenFile` | <https://api.flutter.dev/flutter/flutter_test/matchesGoldenFile.html> | the visual audit at large text and in both themes |
| Flutter, integration tests | <https://docs.flutter.dev/testing/integration-tests> | completing the main flow on a device |
| Mobbin | <https://mobbin.com/> | three real shipped apps in the vertical, step 2 |
| Emil Kowalski, mobile-native | <https://github.com/emilkowalski/skills/blob/main/skills/mobile-native/SKILL.md> | bundled verbatim as `mobile-native.md` |
| Why every AI-built app looks the same, 15 tells | <https://mowgli.ai/blog/why-ai-built-apps-look-the-same> | the current cross-platform tell list |
| AI slop design, 10 signs | <https://www.noqode.fr/en/blog/design-ia-generique> | palette, weight, and layout tells on small screens |
| Reviewing AI-generated Flutter code | <https://dev.to/nixan/how-to-review-ai-generated-flutter-code-before-it-breaks-production-486f> | goldens catching overflow, dark-mode contrast, and truncation at 200 percent scale |

## How each one is used

**Platform guides override taste.** Where Apple HIG or Material 3 states a rule,
that rule beats any preference in these files, because shipping off-platform is
the loudest mobile tell there is: an iOS app that ignores the back gesture or the
safe area reads as generated even when the palette is fine.

**`mobile-native.md` is the mobile web half.** It is a symptom table: sticky
hover after tap, the tap highlight flash, the `100vh` height bug, the input that
zooms the page, laggy taps, pull-to-refresh stealing scroll, content stopping at
the notch, long-press selecting button text, carousels scrolling the wrong way,
mismatched status bar color, and its closing rule that you test on real hardware.
Copy its fixes; ignore its "Initial Response" block, which belongs to that skill.

**The two tell articles are for currency, not for authority.** They restate the
web tells plus the mobile-specific ones now circulating: icon in a tinted
rounded square, emoji as an icon, ALL-CAPS eyebrow on every heading, the
big-number stats strip, and gradient text. Refresh both before a large project,
since the defaults move roughly every model generation.

**Mobbin, or the App Store's own top charts, is the escape from the median.**
Screenshots of three real apps in the vertical, pulled before choosing a palette,
are the single most effective input. A plan that survives that comparison without
change is the default, not a design.

## What is deliberately not here

- **No copied Anthropic or Vercel text.** Neither repo publishes a license file,
  so their skills are fetched at runtime, same rule as the web half. Anthropic's
  `frontend-design` calibration list still applies to app screens.
- **No UI kit or template package.** Radix, shadcn, and the Flutter widget
  galleries solve different problems; the identity plan in step 3 decides
  appearance, and installed behavior should come from one framework, not four.
- **No device mockup generators.** A store graphic needs the real build, not a
  framed fake screen. Framed mockups of screens that do not exist are a policy
  risk on both stores as well as a tell.
