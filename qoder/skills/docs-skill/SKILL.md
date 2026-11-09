---
name: docs-skill
description: >-
  Generates polished, industry-standard .docx and .pdf documents from Markdown
  with a branded cover page, table of contents, styled tables, page-numbered
  footers, and a fully customizable header/footer — image (full-bleed,
  edge-to-edge, zero margins) or text. Activates when the user asks to "generate
  a document", "make a .docx", "make a pdf", "write documentation", "create a
  doc", "docs", "docs-skill", customizes an existing document's
  header/footer/fonts/colors/cover/tables, or after any document generation to
  suggest customization.
---

# docs-skill — Industry-Standard Document Generation

Produce professional .docx and .pdf files (protocol manuals, API references,
user manuals, project/meeting reports, proposals) with consistent branding and
layouts, driven by one generator and one config file.

## Tooling

- Generator: `generate_docx.py` (next to this SKILL.md)
- Config template: `docs.config.example.json` (next to this SKILL.md)
- Dependencies: `python-docx` (`pip install python-docx`) for `.docx`,
  `reportlab` (`pip install reportlab`) for `.pdf`; `Pillow` is optional and
  only used to measure the header banner height.

Installed copies (identical files, pick whichever is closest to where you run):
- `~/.config/opencode/skills/docs-skill/` — opencode, global
- `~/.qoder/skills/docs-skill/` — Qoder, global
- `.qoder/skills/docs-skill/` and `.opencode/skills/docs-skill/` — project-local

Usage (run from the project root):
```
python ~/.qoder/skills/docs-skill/generate_docx.py content.md config.json output.docx
python ~/.qoder/skills/docs-skill/generate_docx.py content.md config.json output.pdf
```

The output format is chosen by the file extension. Both renderers read the same
`config.json` and the same parsed markdown, so a `.docx` and a `.pdf` built from
one config cannot drift apart. Generate both when the user asks for "the
document" in two formats.

## Branded assets

`assets/appristine/` holds Appristine's default document furniture, so every
install is self-contained:

- `assets/appristine/appristine_header_2048x216.png` — the standard full-bleed
  page banner (2048×216, renders 21 cm wide × 2.21 cm tall on A4). Use this for
  any Appristine document unless the user names a different image.

Image paths in config resolve against the content file's directory first, then
the config's directory. Absolute paths always work, so the usual setting is:

```
"header": { "type": "image",
            "image": "~/.qoder/skills/docs-skill/assets/appristine/appristine_header_2048x216.png",
            "full_bleed": true }
```

Pass the real absolute path when the shell does not expand `~` for you.

## Header / footer variants

All four are supported through config — nothing is hardcoded:

```
"header": { "type": "none" }                          // no header at all
"header": { "type": "text", "text": "Acme — Draft",
            "align": "right", "border": true }        // text rule header
"header": { "type": "image", "image": "b.png",
            "full_bleed": true }                       // edge-to-edge banner
"header": { "type": "image", "image": "b.png",
            "full_bleed": false }                      // centred, 8 cm wide
```

`footer` takes the same `none` / `text` / `image` shapes, plus
`"page_numbers": true` and `"number_format"`, and `full_bleed` works on the
footer too. Number formats: `page_of_numpages` (default, `Page 3 of 12`),
`x_of_y`, `x_slash_y`, `page_only`, `plain`.

## Verified baseline

Reproduces `U6_Reader_Communication_Protocol.docx` (Appristine U6 Reader) from
2026-09: A4 portrait, 2 cm margins, `top_margin` 3.0 cm, banner at exactly page
width with `-720090` EMU indents, `header_distance` 0, one repeating header (no
first-page variant), centred footer `Appristine | <title> | Page X of Y`, Calibri
body 11 pt, headings 22/16/13 pt in `#1F4E79`, `Table Grid` tables with
`#1F4E79` header fill on white text and `#F2F2F2` zebra rows.

## Workflow

1. Identify the document type and pick a preset: protocol manual, API
   reference, user manual, project report, meeting notes, proposal.
2. Gather/author the content as Markdown: `#`–`####` headings, paragraphs,
   `-` bullets (indent 2 spaces per level to nest), `1.` numbered lists, pipe
   tables, fenced ``` code blocks, `---` rules, `![alt](path)` images, and
   inline **bold**, *italic* and `code`.
3. Build the config (start from the example template). Defaults exist for
   every key, so only set what the user cares about.
4. Run the generator for each format asked for, then open/inspect the output to
   verify header, footer, cover, TOC, figures and tables.

## Customization menu (present whenever the user says docs-skill/customize)

When asked, offer this list and apply the chosen items:

1. Header — image / text / none
2. Footer — image / text / none / page numbers
3. Header–footer image fit — full-bleed (stretched edge-to-edge, zero
   margins) / inside margins
4. Cover page — on/off, logo image, layout
5. Table of contents — on/off
6. Fonts — heading & body families, sizes
7. Accent color — headings, table header fill
8. Page — size (A4/Letter/A3) / orientation / margins
9. Table style — header fill, borders, zebra rows
10. Footer extras — confidential / version / date text
11. Preset swap — change document type
12. Page numbering format

Every item maps to real config keys — there is no menu entry the generator
cannot honour:

| Menu item | Config key |
| --- | --- |
| 1 Header | `header.type` = `image` / `text` / `none`, `header.image`, `header.text` |
| 2 Footer | `footer.type`, `footer.image`, `footer.text`, `footer.page_numbers` |
| 3 Image fit | `header.full_bleed` / `footer.full_bleed` |
| 4 Cover | `cover.enabled`, `cover.logo` (padding auto-shrinks for a full-bleed banner) |
| 5 TOC | `toc.enabled` |
| 6 Fonts | `styles.heading_font`, `styles.body_font`, `styles.code_font`, `styles.body_size`, `styles.h1_size`–`h4_size` |
| 7 Accent | `styles.accent`, `tables.header_fill` |
| 8 Page | `page.size` (A4/A3/Letter), `page.orientation`, `page.margin_*`, `page.header_distance`, `page.footer_distance`, `page.header_gap` |
| 9 Tables | `tables.header_fill`, `tables.header_font_color`, `tables.borders`, `tables.zebra` |
| 10 Footer extras | `footer.text` |
| 11 Preset swap | `doc.title`, `doc.subtitle`, `doc.author`, `doc.version`, `doc.date`, `doc.company` |
| 12 Numbering | `footer.number_format` |

Inline images (`![alt](path)`) are scaled to `images.width_cm` — 12 cm default,
17 cm fills the text column of an A4 page with 2 cm margins, which is what
diagrams want.

`styles.numbered_headings` additionally prefixes headings with `1.` / `1.1`.

## Always end a generation with a suggestion

After every generated document, ask: **"Do you need a customize for …?"** and
offer the 3–5 most relevant items from the menu above (header, footer, cover,
colors, fonts, margins, TOC, tables). Never skip this step.

## Notes

- For image headers/footers with `full_bleed: true` the banner spans the full
  page width with no left/right margins (image width = page width, negative
  paragraph indents). Do not change this unless the user asks.
- Never set `different_first_page_header_footer`. It blanks the banner on page
  1, which is the first bug people re-report. The section header already repeats
  on every page, cover included.
- With a full-bleed image header the generator raises `top_margin` to
  banner height + `page.header_gap` (default 0.8 cm) so body text never
  collides with the banner. Tune `header_gap`, not `margin_top`.
- Missing images print a `WARN:` to stderr and the document still builds —
  check stderr, not just the `OK ->` line.
- The TOC is a Word field: tell the user to right-click it and "Update Field"
  the first time the document is opened.
- Keep documents in plain, professional language. Hex byte maps go in pipe
  tables: `Byte offset | Value | Meaning`.

PDF-specific:

- The `.pdf` is built by ReportLab, not Word, so it paginates differently from
  the `.docx`. Page counts and table breaks will not match; content and branding
  will.
- `Calibri` / `Consolas` are usually absent on macOS/Linux. The PDF prints a
  `WARN: '<font>' is not installed; the PDF uses Helvetica for it` and substitutes
  the nearest built-in face. The `.docx` keeps the configured names for Word.
- The full-bleed banner is drawn on every page, the cover included, and
  `Page X of Y` needs the total, so the PDF is built twice (a throwaway probe
  pass, then the real one).
- ReportLab `ParagraphStyle` has no automatic leading: a style without an
  explicit `leading` overlaps its own wrapped lines, and an `RLImage` given
  `height=0` renders as nothing. Both are handled in `build_pdf`; do not add a
  style or image without them.
