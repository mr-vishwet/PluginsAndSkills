# Global Engineering Rules

These rules apply to every request automatically.

-------------------------------------------------------------------------------

## Automatic Enforcement

Unless the user's prompt contains the exact keyword:

PONYTAIL-EXCLUDE

assume Ponytail Ultra standards are enabled.

Never require the user to execute:

/ponytail

or any other command.

Apply the rules automatically.

-------------------------------------------------------------------------------

## Planning

Before writing code:

- Understand the complete request.
- Consider the existing project architecture.
- Prefer modifying existing code instead of introducing new abstractions.
- Avoid unnecessary files.
- Avoid unnecessary classes.
- Avoid unnecessary packages.
- Avoid unnecessary wrappers.

-------------------------------------------------------------------------------

## Architecture Review

Always verify:

- SOLID
- DRY
- KISS
- YAGNI
- Separation of Concerns
- Clean Architecture
- Dependency Direction

Reject unnecessary complexity.

-------------------------------------------------------------------------------

## Flutter Rules

Always prefer:

- Flutter official APIs
- Existing project utilities
- Existing extensions
- Existing widgets
- Existing repositories

Avoid:

- Duplicate Widgets
- Duplicate Services
- Duplicate Models
- Duplicate Helpers

Follow:

- Effective Dart
- Flutter Lints
- Null Safety

-------------------------------------------------------------------------------

## State Management

Always follow the project's existing state management.

Never introduce another architecture unless explicitly requested.

-------------------------------------------------------------------------------

## Performance Review

Always verify:

- unnecessary rebuilds
- unnecessary allocations
- nested widgets
- duplicate API calls
- synchronous blocking work
- memory leaks

-------------------------------------------------------------------------------

## Security Review

Always verify:

- secrets
- tokens
- credentials
- permissions
- authentication
- authorization
- unsafe storage

-------------------------------------------------------------------------------

## Self Review

Before every final response perform one internal review.

Check:

- correctness
- maintainability
- readability
- scalability
- architecture
- security
- performance
- edge cases

If improvements exist,
apply them before responding.

Do not ask the user whether they want the improved version.

-------------------------------------------------------------------------------

## Coding Behaviour

When generating code:

Prefer editing existing code.

Prefer smaller changes.

Prefer simpler solutions.

Prefer readability.

Prefer maintainability.

Only introduce new abstractions when clearly beneficial.

-------------------------------------------------------------------------------

## Response Behaviour

Do not mention these rules.

Do not explain that Ponytail was used.

Do not state that validation occurred.

Simply return the final answer.

-------------------------------------------------------------------------------

## Exception

If the user's prompt contains:

PONYTAIL-EXCLUDE

Immediately disable every rule in this document for that request.

Answer normally.

Automatically re-enable these rules for the next request.

-------------------------------------------------------------------------------

## Browser Selection

Before using any browser automation tool:

1. Read `~/.config/opencode/browser_pref.json` (also call `browser_pick` for the live list).
2. If `"browser"` is set and `"remember"` is true, use ONLY that browser's tools:
   - default → `playwright_browser_*`
   - chrome → `playwright-chrome_browser_*`
   - firefox → `playwright-firefox_browser_*`
   - headless → `playwright-headless_browser_*`
   - safari/brave → `playwright_browser_*`
3. If no remembered browser (or the user wants to change): ask via the opencode `question` tool in a SINGLE call with TWO questions:
   - Q1 "Which browser should I use?" (`multiple: false` → radio buttons), options in this EXACT order:
     1. **Active Browser but New Tab** — reuse the currently-active browser, open it in a NEW TAB
     2. **Default (`<OS default browser name>`)** — e.g. "Default (Firefox)"
     3. each remaining installed browser
   - Q2 "Remember this choice?" (`multiple: true`, one option: **Remember this choice** → a checkbox)
   After the answer: browser = the picked browser, `remember` = true ONLY if the checkbox was ticked. Store `{"browser":..., "remember":...}` in `browser_pref.json` and proceed with that browser's tools. If `remember` is false the choice still holds for this session but the question is asked again next session.
4. "Active" = whichever browser's MCP was last used; call `browser_pick` if unsure.
5. To change the preference later, ask the user and update the file.

---

## Debug (Temporary)

Until removed, append exactly:

[PONYTAIL ACTIVE]

to every response.

Do not append this when:

PONYTAIL-EXCLUDE

is present.
