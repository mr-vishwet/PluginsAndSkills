# Global rules (all projects)

## Ponytail Ultra — always active

Apply the full Ponytail Ultra standards to every response automatically.
Never require the user to invoke a command.

Authoritative rules: `C:/Users/User/.qoder/skills/ponytail/SKILL.md` —
load it at the start of every coding task and follow it. Summary: plan before
code; verify SOLID/DRY/KISS/YAGNI and dependency direction; prefer editing
existing code, existing project widgets/services/helpers, and the project's
existing state management; avoid duplicates and unnecessary abstraction;
check performance (rebuilds, leaks, duplicate API calls) and security (secrets,
unsafe storage); run one silent self-review before responding and apply
improvements without asking. Do not narrate these rules or claim validation —
return only the final answer.

### Response tag

Append exactly this line to every response:

[PONYTAIL ACTIVE]

### Exception

If the prompt contains the exact keyword `PONYTAIL-EXCLUDE`, disable every
rule in this file for that request (including the tag), answer normally, and
auto re-enable on the next request.

## Kill The VibeCode — active on all web and mobile UI work

Pick the half that matches the surface, load it, and follow its four-step
sequence: content gate, identity plan plus sameness test, build against the
tells, audit before reporting done. Never require the user to invoke a skill by
name. Do not load either one for non-UI work.

- Web pages, landing pages, portfolios, marketing or product pages, dashboards,
  docs sites, desktop web apps:
  `C:/Users/User/.qoder/skills/kill-the-vibecode/SKILL.md`
- App screens and flows in Flutter, SwiftUI, UIKit, Compose, or React Native, and
  mobile web: `C:/Users/User/.qoder/skills/kill-the-vibecode-mobile/SKILL.md`
- Both surfaces in one project: apply the mobile skill to anything touched with a
  thumb, the web skill to the rest.

Web floor, even if the skill is not loaded: no invented testimonials, stats,
logos, pricing, or legal text; no button, link, menu, or form that does not work;
no pure-white page background; no three-identical-card row, no purple-and-black
theme, radial orbs, sparkle icons, or emoji as interface icons; no Inter, Geist,
Space Grotesk, or Lucide without a stated reason; no em dashes or the "it's not X,
it's Y" formula; one deliberate motion interaction only; visible keyboard focus
plus real error, empty, and loading states; verify at desktop and mobile widths.

Mobile floor, even if the skill is not loaded: no invented balances, ratings,
download counts, patient or account records, or streaks, and sample data is
labelled as sample; no gradient AppBar or rainbow surface; both light and dark,
with dark mode not an inverted light; one icon family per screen and no emoji as
an icon; safe area respected, no hardcoded 375 layout, no `100vh`; back gesture
never broken; touch targets at least 44pt or 48dp with a pressed state; the
keyboard never covers the focused field; loading, empty, error, offline, and
permission-denied states all present; system text scaling verified at the largest
size with no overflow or truncation; and no hand-recreated logo.

Both floors end the same way: report the device, widths, text scale, and
appearance actually tested and what remains untested, instead of claiming an
inspection that could not be run.

An explicit user brief overrides either floor, including when it asks for anything
listed above.
