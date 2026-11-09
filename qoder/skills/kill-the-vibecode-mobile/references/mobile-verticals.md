# Domain-Specific Mobile Checks

The sameness test applied per vertical. For each: what the model defaults to,
what someone who actually uses that kind of app expects, and the specific thing
to verify. None of this is a style guide. Pick one vertical's cues, not all of
them, and ground the rest in three real shipped apps as step 2 of the sequence
requires.

## Finance, banking, investing

- **Default to avoid**: near-black with a neon green accent, a rainbow portfolio
  chart, big-number balance cards, and a "trusted by" strip.
- **What the vertical expects**: legible figures before decoration. Tabular
  numerals so amounts align, one accent that means something (positive,
  negative, pending), dates and times stated with their timezone, and the
  account or product name shown rather than "Your account".
- **Verify**: destructive money actions are confirmable and undoable where the
  platform allows, balances show the real loading and stale-data states, and
  support contact is reachable from any screen with an error.
- Do not invent balances, transactions, yields, or rates. Any financial
  disclaimer comes from the business, marked `DRAFT, needs review`, never from
  you.

## Crypto and web3

- **Default to avoid**: black plus acid green plus monospace everywhere, glow
  effects, and token glyph grids.
- **What the vertical expects**: addresses truncated in the middle with a copy
  action next to them, network and fee visible before signing, a clear warning
  when an operation is irreversible, and the distinction between test and main
  net impossible to miss.
- **Verify**: seed-phrase handling never appears in a screenshot or a mock, and
  no invented APY or price history exists anywhere in the UI.

## Health, fitness, wellness

- **Default to avoid**: mint and coral gradients, blob shapes, emoji hearts, and
  a ring or streak graphic on every screen.
- **What the vertical expects**: units explicit and consistent, ranges with the
  source of the range, progress stated without moralising, and a visible path to
  edit or delete entries.
- **Verify**: no invented medical claim, no fake patient data, and any health
  measurement labelled as sample or simulated wherever it is not real. Where the
  app touches regulated data, the consent moment is designed in rather than
  bolted on at the end.

## Medical and clinical

- **Default to avoid**: consumer prettiness. Clinicians read dense lists under
  interruptions.
- **What the vertical expects**: high information density with tight leading,
  monospaced or tabular identifiers, one-hand operability, dark environment
  legibility, and alarms that are never decorative.
- **Verify**: nothing in a clinical UI is simulated data presented as a real
  record. Any dose, lab value, or patient identifier in a mock is visibly marked
  as sample.

## Ecommerce and food delivery

- **Default to avoid**: white background with red discount badges, a hero
  carousel of five banners, and product cards with no price because none was
  supplied.
- **What the vertical expects**: real product photography as the main visual,
  price and availability before description, variant selection that updates the
  image and price together, and delivery time stated as a range with the cutoff.
- **Verify**: cart, checkout, and the failed-payment path all work. Sold-out,
  out-of-area, and minimum-order states exist. Ratings come from the business or
  are absent.

## Education and learning

- **Default to avoid**: pastel cards, a mascot, confetti on completion, and
  numbered `01 / 02 / 03` markers where the content is not a sequence.
- **What the vertical expects**: the lesson's actual object visible (the
  exercise, the passage, the problem), progress by unit rather than by streak,
  and the wrong answer explained rather than just marked.
- **Verify**: no invented learner counts or outcome claims. Offline matters here;
  lessons are commonly opened in transit.

## Productivity and team tools

- **Default to avoid**: purple gradient, three feature cards, checkmark bullets,
  and a decorative terminal window.
- **What the vertical expects**: the user's own work as the hero, keyboard and
  quick-add paths, bulk actions, and empty states that show how to get the first
  item in rather than celebrating the void.
- **Verify**: sync conflict, offline read, and partial-failure states exist. Real
  screenshot beats mock UI; the mock is where slop enters.

## Social and messaging

- **Default to avoid**: bubble layouts with no tail direction, a compose button
  that floats over the last message, and invented follower counts.
- **What the vertical expects**: tap targets sized for a thumb over a small
  avatar, unread state that survives scrolling, media that loads progressively
  without reflowing the thread, and blocked, reported, and deleted states that
  are reachable.
- **Verify**: moderation, blocking, and account deletion paths are present and
  named plainly. Store listings will ask about them.

## Travel and mobility

- **Default to avoid**: full-bleed destination photography with unreadable
  overlay text.
- **What the vertical expects**: times, terminals, gates, and confirmation codes
  readable in sunlight at arm's length, offline access to the ticket, and a
  boarding pass that does not depend on a network call.
- **Verify**: date and timezone handling, delayed and cancelled states, and the
  low-brightness and high-glance use cases.

## Media, streaming, reading

- **Default to avoid**: dark mode with low-contrast grey metadata, and poster
  grids with invented artwork.
- **What the vertical expects**: artwork aspect ratios respected rather than
  cropped, playback controls reachable with one hand, scrubbing that shows what
  remains, and resume position surfaced before anything else.
- **Verify**: no placeholder cover art presented as real, no invented titles or
  catalog data, and reduced motion honored on autoplay surfaces.

## AI and tech products

- **Default to avoid**: the sparkle icon, the terminal mock, and the "future of
  productivity" headline. This is the vertical with the most slop and the least
  excuse.
- **What the vertical expects**: the actual output shown, model or data limits
  stated, latency designed for with a real loading and cancellation path, and
  the wrong answer handled as a product state rather than a joke.
- **Verify**: no invented accuracy figures, no fabricated demo transcripts, and
  simulated results labelled on screen.

## B2B, dashboards, field and back-office

- **Default to avoid**: bento grids of identical stat cards.
- **What the vertical expects**: dense tables with sortable headers, row-level
  actions, filters that persist, tabular numerals, and one screen that answers
  the operator's actual question.
- **Verify**: role-restricted empty states, real pagination or virtualization at
  production row counts, and a print or export path where the workflow needs it.

## Reading list, not a copy list

For every vertical: three real shipped apps, screenshotted, form the reference.
Compare against them, not against the median of what you can generate. If the
plan survives that comparison unchanged, it is the default and step 2 is not
done.
