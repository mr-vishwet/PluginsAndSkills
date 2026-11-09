# The Six Resources

The external resources named in the source article, with when to pull each one
and the licensing status that decides whether it ships inside this plugin or is
fetched at runtime.

| Resource | URL | Bundled? |
| --- | --- | --- |
| Apple MacBook Pro page | <https://www.apple.com/macbook-pro/> | No, reference only |
| Anthropic `frontend-design` | <https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md> | No, fetch at runtime |
| Radix Primitives | <https://www.radix-ui.com/primitives/docs/overview/introduction> · <https://github.com/radix-ui/primitives> | No, install only when needed |
| Motion | <https://github.com/motiondivision/motion> · React docs <https://motion.dev/docs/react> | No, install only when needed |
| GSAP ScrollTrigger | <https://gsap.com/docs/v3/Plugins/ScrollTrigger/> · <https://github.com/greensock/GSAP> · license <https://gsap.com/pricing/> | No, install only when needed |
| Vercel `web-design-guidelines` | <https://github.com/vercel-labs/agent-skills> | No, fetch at runtime |
| Emil Kowalski `apple-design` | <https://github.com/emilkowalski/skills/blob/main/skills/apple-design/SKILL.md> | Yes, MIT, verbatim in `apple-design.md` |

## 1. A real reference, not a reusable asset

Apple's product pages teach how product, headline, and supporting detail share
space. Screenshot the specific section liked and ask for its hierarchy, image
scale, and spacing to be applied to the user's own content. Apple's page is a
visual reference: do not lift its imagery, assets, or exact layout.

## 2. Anthropic's `frontend-design`

The strongest anti-template guidance available, including the calibration list
of current generated-design clusters and the two-pass plan-then-interrogate
process this skill's step 2 is built on.

License status: the `anthropics/skills` repository exposes no license file, so
its text is not copied into this plugin. Fetch the `SKILL.md` above when a build
needs the full reasoning, and pair it with the direction line the source article
recommends:

> Read this skill and apply it to my brief. Keep the direction restrained,
> editorial, and focused on the product.

That trailing clause matters. Distinctive design can also be bold or
experimental, so the clause states which direction is wanted rather than leaving
it to the skill's own leanings.

## 3. Radix Primitives, maintained by WorkOS

Unstyled components that supply focus management and keyboard behavior. Use only
where a dialog, tabs, or dropdown is genuinely needed, then style those controls
with the page's own type, spacing, and palette. The primitives supply behavior;
the identity plan supplies appearance. Keep existing components that already do
the job.

## 4. Motion, for one interaction

The free core library covers transitions, springs, and scroll-linked effects.
Brief that works: short opacity transitions and small movements for meaningful
state changes, page stays calm, reduced motion supported. Start with one
interaction. A product image that changes cleanly when a variant is selected
beats every paragraph flying onto the screen. Paid Motion+ extras are not needed
for this approach.

## 5. GSAP ScrollTrigger, for a deliberate reveal

Optional, and only when the sequence explains the product. One product
demonstration that progresses with scrolling, kept short, with scroll control
preserved and a simple mobile and reduced-motion version provided. GSAP is free
under its standard license, supported by Webflow. Do not add both GSAP and
Motion to a simple landing page.

## 6. Vercel's `web-design-guidelines`, for the finish

The upstream skill is itself a thin wrapper that fetches
<https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md>
before each review, so nothing is bundled here. Fetch fresh guidelines, then
apply:

> Apply the web-design-guidelines rules to this implementation. Fix relevant
> issues while preserving the approved visual direction.

Use it for the final polish pass only. It checks focus states, forms, typography,
images, and motion, which is where a vague "make it premium" request loses
details. It will not choose an aesthetic.

## Starting combination

A reference screenshot, this skill's step 2 identity plan, and the brief in
`design-brief.md`. Add Radix only when the interface needs complex controls. Add
one motion library only when there is a specific interaction to build.
