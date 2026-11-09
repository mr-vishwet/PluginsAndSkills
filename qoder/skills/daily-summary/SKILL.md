---
name: daily-summary
description: >-
  Generates a daily task sheet (planning) or completion summary (recap) in
  plain, generic language — no file names, no paths, no commit hashes, no code
  jargon, no line counts. Groups work into themes rather than files and writes
  in simple human terms. Activates when the user asks for a "daily summary",
  "today's tasks", "today's work", "task sheet", "daily plan", "daily report",
  "what did we do today", "completion checklist", "task points", or says "use
  the skill". Also triggered when a session opens with a plan for split-shift
  work (e.g. "first half" / "second half" of the day) or a request to draft a
  task sheet under a word limit.
---

# Daily Summary / Task Sheet

Produce a concise, module-wise, plain-language daily task sheet (planned work)
or completion summary (done work) covering both plan and recap in one document.
Optionally read today's file-modification timestamps to reflect completed work.

## Workflow

1. Understand what was planned and/or completed today from the conversation
   and file timestamps.
2. Group work into module / phase areas (themes), never individual files.
3. Describe each entry in simple human terms: what was done, not where it lives.
4. If both a plan and a recap are needed, keep them in one sheet.

## Output Rules — STRICT

- NO file names, NO paths, NO commit hashes, NO line counts
- NO code jargon — plain language: "analysed the older project",
  "sniffed device bytes", "mapped each command", "understood the decode mechanism"
- Default max 150 words. If the user states another limit in the prompt
  (e.g. "within 100 words" or "in full detail"), follow that instead.
- One bullet per logical change, grouped under simple headings
- Generic every time: "byte mapping extracted", never "file X updated"
- Prefer short bullets with one sub-detail each over long sentences

## Format

## Daily Task Sheet / Summary

**Date:** YYYY-MM-DD

### <Module / Phase>
- What was done/planned (generic)
  - sub-detail
