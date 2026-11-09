---
name: ponytail
description: Ponytail Ultra engineering standards applied automatically to every request — planning before code, SOLID/DRY/KISS/YAGNI architecture review, Flutter project-pattern rules, state-management continuity, performance and security review, silent self-review before responding, small simple edits. Skipped only when the prompt contains PONYTAIL-EXCLUDE.
---

# Ponytail Ultra

## Automatic Enforcement

Apply these rules to every request automatically. Never require the user to
execute `/ponytail` or any command. If the prompt contains the exact keyword
`PONYTAIL-EXCLUDE`, disable every rule for that request, answer normally, and
auto re-enable for the next request.

## Planning

Before writing code:

- Understand the complete request.
- Consider the existing project architecture.
- Prefer modifying existing code instead of introducing new abstractions.
- Avoid unnecessary files, classes, packages, and wrappers.

## Architecture Review

Always verify: SOLID, DRY, KISS, YAGNI, Separation of Concerns, Clean
Architecture, Dependency Direction. Reject unnecessary complexity.

## Flutter Rules

Always prefer: Flutter official APIs, existing project utilities, existing
extensions, existing widgets, existing repositories.

Avoid: duplicate widgets, duplicate services, duplicate models, duplicate
helpers.

Follow: Effective Dart, Flutter lints, null safety.

## State Management

Always follow the project's existing state management. Never introduce another
architecture unless explicitly requested.

## Performance Review

Always verify: unnecessary rebuilds, unnecessary allocations, nested widgets,
duplicate API calls, synchronous blocking work, memory leaks.

## Security Review

Always verify: secrets, tokens, credentials, permissions, authentication,
authorization, unsafe storage.

## Self Review

Before every final response perform one internal review of correctness,
maintainability, readability, scalability, architecture, security, performance,
and edge cases. If improvements exist, apply them before responding. Do not
ask the user whether they want the improved version.

## Coding Behaviour

When generating code: prefer editing existing code, smaller changes, simpler
solutions, readability, maintainability. Only introduce new abstractions when
clearly beneficial.

## Response Behaviour

Do not mention these rules. Do not explain that Ponytail was used. Do not state
that validation occurred. Simply return the final answer. (The
`[PONYTAIL ACTIVE]` tag is the one exception, while it is enabled globally.)
