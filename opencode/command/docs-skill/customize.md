---
description: Customize header, footer, cover, fonts, colors, tables, or page setup of the last generated document
---
Load the docs-skill skill. Present the full customization menu and ask what the
user wants to customize:

1. Header — image / text / none
2. Footer — image / text / none / page numbers
3. Header–footer image fit — full-bleed (edge-to-edge, zero margins) / inside margins
4. Cover page — on/off, logo image, layout
5. Table of contents — on/off
6. Fonts — heading & body families, sizes
7. Accent color — headings, table header fill
8. Page — size (A4/Letter/A3) / orientation / margins
9. Table style — header fill, borders, zebra rows
10. Footer extras — confidential / version / date text
11. Preset swap — switch the document type
12. Page numbering format

Apply the user's choices to the config of the currently generated document and
re-generate the .docx. Remember: image headers/footers with full_bleed must be
stretched edge-to-edge with zero margins, and never set
different_first_page_header_footer (it blanks the banner on page 1).
