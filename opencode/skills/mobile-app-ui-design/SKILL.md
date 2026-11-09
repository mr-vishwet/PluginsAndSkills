---
name: mobile-app-ui-design
description: Design high-quality mobile app UI/UX screens, flows, and components. Use this skill whenever the user asks to design a mobile app screen, create app mockups, build mobile UI components, improve an existing mobile app design, create onboarding flows, design mobile navigation, or requests any mobile-first interface work. Also trigger when the user mentions app design, mobile UI, mobile UX, screen design, app mockups, wireframes, or wants to build React Native / Flutter / SwiftUI style interfaces as visual prototypes. Even if the user just says "design an app" or "make this screen look better", use this skill.
---

# Mobile App UI/UX Design Skill

This skill guides the creation of professional, polished mobile app interfaces that follow proven design principles used by top-tier apps like Airbnb, Duolingo, Spotify, Revolut, and Phantom.

## Core Philosophy

Great mobile UI isn't about flashiness — it's about intentionality. Every pixel, every spacing value, every color choice should serve the user. The goal is to create interfaces that feel smooth, personal, and alive — not just functional.

Before designing anything, understand three things:
1. **What is the user trying to accomplish?** (reduce friction to that goal)
2. **How should this make the user feel?** (trust, delight, confidence, calm)
3. **What's the one thing they should notice first?** (visual hierarchy)

## Design Process

Follow this sequence for any mobile screen:

### Step 1: Understand the Context
- What type of app? (fitness, finance, social, productivity, health, crypto, etc.)
- Who is the user? (new, returning, power user — adapt the experience)
- What's the primary action on this screen?
- What industry design conventions apply? (See `references/industry-conventions.md`)

### Step 2: Structure First (UX Lens)
- Map the user flow: what screen comes before and after?
- Identify the MVP elements — only what's essential for this screen
- Place primary actions in the **thumb zone** (bottom 1/3 of screen)
- Follow the **F-pattern** reading order for content layout
- Reduce interaction cost: expose content directly instead of hiding behind taps
- Turn empty states into opportunities with guidance, illustration, and a CTA
- Choose the right input method: sliders/scroll wheels for one-time setup, text fields for repeated/precise entry

### Step 3: Apply Visual Design (UI Lens)
Follow these rules in order:

#### Typography
- Use **one font family** (two max, with clear hierarchy purpose)
- Maximum **4 font sizes** and **2 font weights**
- Use monospace variants for large numbers (prices, stats, metrics)
- Keep text containers under 600px wide for readability
- Create hierarchy with size, weight, and opacity — not just bold everything

#### Color System (60/30/10 Rule)
- **60%** — neutral base (white, light gray, or dark background)
- **30%** — complementary color (black text, dark elements)
- **10%** — brand/accent color (CTAs, key indicators, icons)
- Use **opacity variations** of the neutral color for text hierarchy: 100% for headings, 80% for body, 60-70% for secondary text
- Use the accent color at 5% opacity for secondary buttons and subtle card highlights
- Match shadow colors to the background (tint shadows, never pure gray/black on colored backgrounds)
- Save strong colors (like red) for meaningful moments — overuse kills hierarchy

#### Spacing (8-Point Grid System)
- All spacing values must be divisible by **8 or 4** (8, 12, 16, 24, 32, 48, 64, 80, 96)
- Use **relationship-based spacing**: related elements closer together, unrelated further apart
- Multiplier rule: if related text elements are 16px apart, the gap to the next group should be 2× (32px)
- Section vertical padding: at least 80-96px (160px for major sections on larger screens)
- Card internal padding: 24-32px baseline
- Larger text = larger spacing needed

#### Shadows
- Always use **soft shadows** — never harsh/distinct
- Match shadow color to the background with a tinted hue
- Use subtle white inner shadows on buttons to add dimension
- Add faded drop shadows for depth without heaviness

#### Visual Cues & Imagery
- Use icons, emojis, illustrations, and images to make information digestible
- User avatars/photos > initials > generic icons (for representing people)
- Color-coded categories with soft solid backgrounds + clean isolated images
- Keep visual style consistent across the entire app — no random stock photo mix
- Use AI-generated or curated visuals with matching color palettes

### Step 4: Design for Emotion (Peak-End Rule)
The user will remember two moments: the **peak** (most intense) and the **end** (last impression).

- **Identify your peak moment**: completing a core task, hitting a milestone, finding what they want
- **Design the peak**: micro-animations, celebratory feedback, sparkles, badges, encouraging copy
- **Design the ending**: summary card, progress affirmation, gentle nudge to return
- Add **emotional feedback loops**: success states should feel rewarding (bounce, glow, sparkle)
- Celebrate small wins — success states don't need to be huge, but they should feel intentional
- Use motion and animation as trust signals, especially in high-stakes domains (finance, crypto, health)

### Step 5: Polish & Details
- Add subtle glow effects behind key elements (blur + opacity)
- Use tiny white inner shadows on primary buttons
- Add 5% opacity primary-color borders on secondary elements
- Consider micro-animations for state changes
- Ensure all tap targets are at least 44×44pt
- Check contrast ratios for accessibility
- Design error states, empty states, loading states, and success states

## Onboarding Flows

Onboarding is a tool to shorten **time-to-value**, not a checklist of screens. Length is not the point — the average app has ~25 onboarding screens, and some of the longest flows (Duolingo ~60, finance apps) are also the most successful. Optimize for how fast and how delightfully the user reaches the **aha moment**, not for fewest taps.

Core moves (full case studies and conversion data in `references/onboarding-flows.md`):

- **Structure backward from the aha moment**: sign up → set up → the moment value is felt (Airbnb = first booking, Netflix = watching a show, Duolingo = completing the first lesson). Remove anything between the user and it that isn't earning its place.
- **Sell the outcome, not features**: show the product in action, animate the feel, or let users try the core experience *before* signup (Timehop, Runkeeper, Elma). Use social proof / logos as the pitch (Superhuman).
- **Personalize, and make it pay off**: every question must visibly change what the user gets — then reflect the result back before they've used the product ("In 2 months you'll communicate in France," a pre-built plan with an exact goal date). Allow multi-select goals where users have more than one (Headspace: +10% trial conversion).
- **Make long flows feel short**: animate the screens nobody bothers with (loading, verification), give the user something to do or name (Bipul's named raccoon). Add a human touch at the peak or end (founder note, CEO video).
- **Teach in context, not up front**: tooltips that explain each step's impact, real-time field validation, and persistent checklists (Mural's 6-step checklist: +10% one-week retention) beat a wall of tutorial pop-ups.
- **Prime before you ask**: show a custom pre-permission screen explaining the *why* before any OS prompt (notifications, location) to lift accept rates. This is partly why iOS onboarding runs ~21% longer than web — budget for permission + paywall screens.
- **Earn the paywall**: if you paywall during onboarding (22% of apps do), show the personalized plan/outcome first, and make the moment itself delightful (Focus Flight's vibrating flight-ticket offer; Grammarly's quiz-tailored pricing: +~20% upgrades).
- **Consider no onboarding at all**: for instant-value products (Mobbin, AI chat apps where the first prompt is the value), the best flow is getting out of the way.

Before designing an onboarding flow, read `references/onboarding-flows.md` for the benchmarks, the conversion-tested patterns, and the onboarding design checklist.

## Platform-Native Design (Apple HIG)

When the target is a real iOS/iPadOS app (SwiftUI/UIKit), follow Apple's Human Interface Guidelines — they override the generic defaults above where they conflict, because shipping on-platform means looking native. Full detail in `references/apple-hig.md`. The essentials:

- **Two-layer model (Liquid Glass)**: content lives in the **content layer** (use standard materials — blur/vibrancy — never Liquid Glass); controls and navigation **float above** on Liquid Glass. Extend content edge-to-edge under the floating controls; use a **scroll edge effect** instead of a hard background to separate them.
- **Respect safe areas, layout margins, and Dynamic Type.** Layouts must reflow (not clip) when text scales; honor RTL; reading order = importance (top-leading first).
- **Typography**: system fonts + built-in text styles (Body, Headline, Title…) for free Dynamic Type. iOS body **17 pt default / 11 pt min**. Avoid light weights. Limit typefaces.
- **Color**: use **semantic/dynamic system colors** (never hard-code system values); ship light + dark + increased-contrast variants for custom colors; label hierarchy via primary/secondary/tertiary/quaternary; a single accent, applied to the control's Liquid Glass background for primary actions only. Never rely on color alone.
- **Dark Mode**: respect the systemwide setting — **don't add an app-specific appearance toggle**. Semantic colors + SF Symbols adapt automatically.
- **SF Symbols** for iconography, matched in weight/scale to adjacent text.
- **Accessibility (non-negotiable)**: **44×44 pt** min tap target; **4.5:1** contrast (7:1 custom small text); Dynamic Type ≥200%; label for VoiceOver; honor **Reduce Motion** (cut zoom/scale/parallax, offer crossfade).
- **Onboarding (HIG)**: fast, fun, **optional**, *after* launch; teach through interactivity or context tips (TipKit); skippable + findable later; postpone nonessential setup with good defaults; integrate permission requests to show *why*; let people experience the app before rating/purchase prompts.
- **Feedback**: match significance to interruption (passive status vs. alert for critical/actionable only); make it multi-channel (color + text + sound + haptics); warn only before *unexpected* irreversible loss.

## Smart Patterns to Apply

### Personalization by User Stage
- **New users**: simple welcome, guided setup, minimal options
- **Returning users**: personalized content, routine-focused, progress indicators
- **Power users**: advanced stats, optimization tools, dense information

### Smarter Search
Never show a blank search screen. Include:
- Recent searches
- Popular/trending items
- Personalized recommendations

### Order/Status Tracking
- Open with a confident status message
- Humanize with photos, names, quick-action buttons
- Use visual timelines instead of text-based date lists

### Category Screens
- Use color-coded cards with soft backgrounds and clean isolated images
- Ensure visual consistency across all category items
- Create rhythm in the layout for effortless scanning

### Selection Over Manual Input
- Offer tappable selections for common options (job titles, preferences, etc.)
- Include icons/emojis alongside options for personality
- Provide an "Other" option with manual input as fallback

## Anti-Patterns to Avoid
- Overusing flashy gradients and blur effects (unless you can truly pull it off)
- More than 4 font sizes or 3 font weights
- Random spacing values (use the 8-point grid!)
- Hiding key content behind banners or extra taps
- Placing CTAs outside the thumb zone
- Generic empty states with no guidance
- Using sliders for frequent/precise data entry
- Making all information the same visual weight (no hierarchy)
- Emphasizing labels over values (e.g., making "Sales" bigger than "591")
- Pure gray/black shadows on colored backgrounds
- Listing features on a welcome screen instead of showing the product in action
- Asking onboarding questions that don't change anything the user then sees
- Firing the raw OS permission prompt with no priming screen (tanks accept rates)
- Dropping a paywall before the user has seen any personalized value
- Optimizing onboarding for "fewest screens" at the cost of time-to-value or delight
- (iOS) Hard-coding system color values instead of using semantic/dynamic colors
- (iOS) Adding an app-specific Light/Dark toggle instead of respecting the system setting
- (iOS) Putting Liquid Glass in the content layer, or drawing custom shadows where a material/scroll edge effect belongs
- (iOS) Tap targets under 44×44 pt, or animations that ignore Reduce Motion

## Implementation Notes

When building these designs as React artifacts or HTML:
- Use Tailwind CSS utility classes for spacing, colors, and typography
- Import Lucide React for clean, consistent iconography
- Use Recharts for any data visualization
- Apply CSS transitions for micro-interactions and state changes
- Use CSS variables for the color system
- Mobile-first: design for 375px width (iPhone SE) as baseline
- Use `rounded-2xl` or `rounded-3xl` for modern card aesthetics
- Apply `backdrop-blur` for glassmorphism effects where appropriate

For deeper guidance on industry-specific conventions and emotional design patterns, read `references/industry-conventions.md`. For onboarding flows specifically — benchmarks, conversion-tested patterns, and a design checklist — read `references/onboarding-flows.md`. For native iOS work, read `references/apple-hig.md` (Apple Human Interface Guidelines: Liquid Glass, layout/safe areas, typography, semantic color, Dark Mode, SF Symbols, accessibility, onboarding, feedback).
