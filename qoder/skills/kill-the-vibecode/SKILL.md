---
name: kill-the-vibecode
description: >-
  Make AI-built websites stop looking AI-built. Use for ANY website, landing
  page, portfolio, marketing page, product page, dashboard, docs site, or
  desktop web app that is being designed, built, restyled, or reviewed,
  including requests like "make it look premium", "make it like Apple", "build
  me a site", "redesign this", or "make it not look AI generated". Enforces a
  real content gate, a per-brief visual identity, a categorized list of
  templated tells to avoid, honest copy, working behavior, and a verification
  pass before reporting done. For phone and tablet app UI, including Flutter,
  SwiftUI, Compose, and React Native screens, use kill-the-vibecode-mobile
  instead. Activate even when the user does not name this skill.
user-invocable: true
argument-hint: <what you are building, plus your real content and assets>
---

# Kill The VibeCode: Web

This is the web half of the plugin. The phone and tablet half, with its own tell
list, per-vertical checks, and scanner, is `kill-the-vibecode-mobile`.

AI slop is not one visual style. It is the accumulation of generic choices plus
unfinished behavior, and the combination is what gives the page away. A single
font or layout proves nothing; cream background with a terracotta accent, three
identical feature cards, an Inter headline, a sparkle icon, and a button that
goes nowhere together read as generated instantly.

This skill removes both halves of that signature: the defaulted aesthetic
decisions, and the stub functionality.

## Scope

Applies to any web page or web UI being designed, built, or reshaped. Does not
apply to non-web work, and does not override an explicit visual direction the
user supplies. The user's brief always beats this file where they conflict,
including when the brief asks for something listed as a tell below.

## Sequence

Run all four steps in order. Do not start with code.

### 1. Brief gate (blocking)

Collect before designing:

- Product: what it actually does
- Audience: who it is for
- Main action: the one thing a visitor should do
- Real content and assets: copy, screenshots, product photos, demo
- Pages and functionality this version needs
- Existing stack, if any
- Reference: URL or screenshot, plus what is liked about it

If real content or assets are missing, ask for them and stop. Do not substitute
invented copy, fake screenshots, decorative mockups, or placeholder brands. The
most common cause of a slop-looking page is a missing real asset, which the
model then covers with glowing orbs and generic cards.

Anything you must write yourself because the user has not supplied it is
labelled `DRAFT, needs your review` in your report, never presented as final.

### 2. Identity plan, then interrogate it

Before code, write a compact plan in four parts:

- **Color**: 4 to 6 named hex values, including the page background, the text
  color, and exactly one accent.
- **Type**: which face at which role, and the type scale. Two families at most,
  and if two, clearly distinct.
- **Layout**: one-sentence concept per major section plus a short ASCII
  wireframe. Include the alignment decision.
- **Principles**: two or three lines on what makes this page specific to this
  subject.

Ground it in the subject matter: the industry, materials, and vocabulary of the
thing being described are where distinctive choices come from. A page for a
ceramics studio and a page for an API monitoring tool should not be
distinguishable only by their logos.

Then run the sameness test. For each part of the plan ask: would this be what I
produce for any other brief in this category? If yes, revise that part and say
what changed. Present the plan to the user in five lines or fewer before
building.

### 3. Build against the tells

Read [references/anti-tells.md](references/anti-tells.md) and check the choices
against it as you write. Non-negotiable core:

- The actual product is the main visual. A real screenshot of a working
  interface, or real photography of a physical product. No animation library
  rescues a meaningless hero.
- Hierarchy comes from typography, spacing, and alignment, not from boxes.
  Vary section composition to match what each section explains. Give the
  strongest evidence more space instead of sizing every block the same.
- Establish reusable design tokens for background, text, accent, type scale,
  and spacing. Do not scatter one-off values.
- Motion budget is one deliberate interaction, chosen because it explains
  something. Not hover transitions on every card, not fade-and-slide on every
  section.
- Prefer existing components and the simplest implementation that supports the
  brief. Inspect an existing project before changing it and preserve working
  features.

### 4. Audit before reporting done

Not optional, and report it honestly:

1. Run the mechanical search over the source, then fix or justify every hit:

   ```sh
   sh scripts/scan-tells.sh src/ index.html styles.css
   ```

   It checks fonts, palette and decoration, templated structure, copy glyphs,
   and fake proof, and exits `1` on any match. What each group searches, and the
   reasons its patterns are bounded the way they are, is in
   [references/anti-tells.md](references/anti-tells.md) section 7.
2. Verify each headline sells the specific task, not the category. "Turn meeting
   notes into assigned tasks", not "The future of productivity".
3. Confirm every button, link, menu, and form actually works. Complete the main
   action end to end.
4. Render at desktop and mobile widths and read the page on a phone. Check
   wrapping, overflow, contrast, and the mobile menu.
5. Check keyboard focus is visible on every interactive element, inputs are
   labelled, and error, empty, and loading states exist for real states.
6. Score the page against the tells list and state the score.
7. Report what was actually tested and what remains unfinished. Never claim to
   have inspected a page you could not run.

Ask for targeted follow-ups rather than vague ones. "Give the product image more
space" produces a better next revision than "make it better".

## The floor

Restraint is the default, per brief. Near-white or warm neutral background, never
pure `#FFFFFF`, dark readable text, one accent, generous space around what
matters, consistent alignment. This is a floor to build above, not a house
style: the identity plan in step 2 decides the actual palette and type.

## Copy

Write from the visitor's point of view, in plain sentence case.

- Headline states the task the product performs.
- Active voice. A button names what happens when it is used, and the same word
  is used in the confirmation.
- No em dashes, no en dashes, and no "it's not X, it's Y" formula. State the
  benefit directly.
- No all-caps labels, no eyebrow label above every heading, no meta strings
  joined with middle dots, no arrow appended to link text.
- Do not accent a single word in a headline with italic, bold, or color.
- Errors explain what went wrong and the fix. They do not apologize and are not
  vague. Empty screens point at the next action.

## Invention is forbidden

Do not create testimonials, star ratings, customer counts, usage statistics,
partner or customer logos, awards, or claims. Show real pricing only if the user
supplied it. Label any simulated result as simulated, on the page, near the
result.

Do not write invented Terms of Service, Privacy Policy, or refund language.
Include those links and pages only from real business and data practices, and
mark any missing detail `DRAFT, needs legal review`.

## Behavior floor

- Motion respects `prefers-reduced-motion`; normal scrolling is preserved.
- Skeleton loaders only where real async content actually needs one. No
  artificial delays.
- Icons only where they clarify an action. No icon set shipped on the page for
  decoration.
- For complex controls in React, Radix Primitives can supply focus management
  and keyboard behavior; style them with the page's own tokens. Do not install
  every available library, and follow current documentation for whatever is
  installed.

## Craft reference

[references/apple-design.md](references/apple-design.md) is the MIT-licensed
`apple-design` skill from Emil Kowalski, kept verbatim for the craft half:
spring values, interruptibility, materials, reduced-motion, and optical type
sizing. Use it as reference material for motion and typography. Ignore its
"Initial Response" section; that block belongs to its own skill and must not
change how this one opens.

Anthropic's `frontend-design` and Vercel's `web-design-guidelines` are fetched at
runtime rather than bundled, for licensing and drift reasons.
[references/upstream-sources.md](references/upstream-sources.md) has the URLs and
when to pull each one.
