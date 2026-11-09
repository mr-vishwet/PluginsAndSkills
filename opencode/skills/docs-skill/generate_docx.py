#!/usr/bin/env python3
"""Generic Markdown -> branded .docx / .pdf generator for the docs-skill.

Usage:
  python generate_docx.py content.md config.json output.docx
  python generate_docx.py content.md config.json output.pdf

The output format is chosen by the file extension. Both renderers consume the
same config.json and the same parsed blocks, so branding cannot drift between
them.

Markdown subset supported: # .. #### headings, paragraphs, - / 1. lists
(nesting-aware), pipe tables, fenced code blocks (```), --- rules,
![alt](path) images, and inline **bold** / `code`. Every layout choice (header,
footer, cover, fonts, colors, tables, page setup) lives in config.json.
"""
import argparse
import copy
import json
import re
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Emu, Mm, Pt, RGBColor

DEFAULTS = {
    "doc": {
        "title": "Untitled Document",
        "subtitle": "",
        "version": "1.0",
        "date": "",
        "author": "",
        "company": "",
    },
    "page": {
        "size": "A4",
        "orientation": "portrait",
        "margin_top": 2.0,
        "margin_bottom": 2.0,
        "margin_left": 2.0,
        "margin_right": 2.0,
        "header_distance": 1.0,
        "footer_distance": 1.0,
        "header_gap": 0.8,
    },
    "cover": {"enabled": True, "logo": "", "fields": [], "notice": ""},
    "toc": {"enabled": True},
    "styles": {
        "heading_font": "Calibri",
        "body_font": "Calibri",
        "code_font": "Consolas",
        "body_size": 11,
        "h1_size": 22,
        "h2_size": 16,
        "h3_size": 13,
        "h4_size": 11,
        "accent": "#1F4E79",
        "numbered_headings": False,
    },
    "header": {
        "type": "text",
        "image": "",
        "full_bleed": False,
        "text": "",
        "font": "Calibri",
        "size": 9,
        "color": "#808080",
        "align": "right",
        "border": True,
    },
    "footer": {
        "type": "text",
        "image": "",
        "full_bleed": False,
        "text": "",
        "font": "Calibri",
        "size": 9,
        "color": "#808080",
        "align": "center",
        "border": True,
        "page_numbers": True,
        "number_format": "page_of_numpages",
    },
    "tables": {
        "header_fill": "#1F4E79",
        "header_font_color": "#FFFFFF",
        "borders": True,
        "zebra": True,
    },
    # Inline ![alt](path) images are scaled to this width; height follows the
    # source aspect ratio. 12 cm suits a screenshot; diagrams usually want the
    # full text column (A4 with 2 cm margins = 17 cm).
    "images": {"width_cm": 12},
}

PAGE_SIZES = {
    "A4": (Cm(21), Cm(29.7)),
    "A3": (Cm(29.7), Cm(42)),
    "LETTER": (Cm(21.59), Cm(27.94)),
}

# Used when Pillow is unavailable and the header image height can't be measured.
FULL_BLEED_FALLBACK_TOP_CM = 3.0

# Tokens starting with "_" are page-number fields; the rest are literal runs.
PAGE_NUMBER_FORMATS = {
    "page_of_numpages": ["Page ", "_PAGE", " of ", "_NUMPAGES"],
    "x_of_y": ["_PAGE", " of ", "_NUMPAGES"],
    "x_slash_y": ["_PAGE", " / ", "_NUMPAGES"],
    "page_only": ["Page ", "_PAGE"],
    "plain": ["_PAGE"],
}

# Bold first: the italic alternative must not swallow the "**" markers.
INLINE = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)")


def warn(message):
    print(f"WARN: {message}", file=sys.stderr)


def rgb(hex_color):
    hex_color = hex_color.strip("#")
    return RGBColor(int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))


def resolve_path(path, cfg, base_dir):
    p = Path(path)
    if p.is_absolute() and p.exists():
        return p
    expanded = Path(str(path).replace("~", str(Path.home())))
    if expanded.is_absolute() and expanded.exists():
        return expanded
    if (base_dir / p).exists():
        return base_dir / p
    if (Path(cfg.get("_config_dir", Path.cwd())) / p).exists():
        return Path(cfg["_config_dir"]) / p
    return None


# ---------------------------------------------------------------------------
# Shared parsing: markdown -> blocks consumed by both renderers
# ---------------------------------------------------------------------------

def _is_block_start(strip):
    """True when a line opens a new block, so it must not be absorbed."""
    if strip.startswith(("|", "#", "```", "---", "<pagebreak/>", "![", "-", "*", "+", ">")):
        return True
    return bool(re.match(r"^\d+[.)]\s", strip))


def _absorb(lines, i, first):
    # Markdown treats a single newline inside a paragraph as a space. Source
    # files are hard-wrapped for readability, so joining here is what keeps
    # ragged line breaks out of the rendered document.
    out, j = first.strip(), i + 1
    while j < len(lines) and lines[j].strip() and not _is_block_start(lines[j].strip()):
        out += " " + lines[j].strip()
        j += 1
    return out


def parse_table(lines, i):
    header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
    i += 1
    while i < len(lines) and re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", lines[i]) and "-" in lines[i]:
        i += 1
    rows = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
        i += 1
    return header, rows, i


def bullet_depth(line):
    indent = line[: len(line) - len(line.lstrip())]
    return len(indent.replace("\t", "   ")) // 2


def parse_blocks(content, cfg):
    """Turn markdown into blocks. Heading numbering happens here so the .docx
    and the .pdf cannot disagree about it."""
    lines = content.splitlines()
    counters = [0, 0, 0, 0]
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        strip = line.strip()
        if not strip:
            i += 1
            continue
        if strip.startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            blocks.append(("code", code))
            continue
        if strip.startswith("|"):
            header, rows, i = parse_table(lines, i)
            blocks.append(("table", header, rows))
            continue
        if strip == "---":
            blocks.append(("rule",))
            i += 1
            continue
        if strip == "<pagebreak/>":
            blocks.append(("pagebreak",))
            i += 1
            continue
        match = re.match(r"^(#{1,4})\s+(.*)$", strip)
        if match:
            level = len(match.group(1))
            text = match.group(2)
            if cfg["styles"]["numbered_headings"]:
                counters[level - 1] += 1
                for k in range(level, 4):
                    counters[k] = 0
                text = ".".join(str(counters[k]) for k in range(level)) + ". " + text
            blocks.append(("heading", level, text))
            i += 1
            continue
        match = re.match(r"^!\[(.*?)\]\((.*?)\)$", strip)
        if match:
            blocks.append(("image", match.group(2)))
            i += 1
            continue
        match = re.match(r"^(\d+)[.)]\s+(.*)$", strip)
        if match:
            blocks.append(("number", _absorb(lines, i, match.group(2)), int(match.group(1))))
            i += 1
            while i < len(lines) and lines[i].strip() and not _is_block_start(lines[i].strip()):
                i += 1
            continue
        match = re.match(r"^([-*+])\s+(.*)$", strip)
        if match:
            # A line starting with "**bold**" is a paragraph, not a bullet: the
            # marker must be followed by whitespace.
            depth = bullet_depth(line)
            blocks.append(("bullet", _absorb(lines, i, match.group(2)), depth))
            i += 1
            while i < len(lines) and lines[i].strip() and not _is_block_start(lines[i].strip()):
                i += 1
            continue
        blocks.append(("para", _absorb(lines, i, line)))
        i += 1
        while i < len(lines) and lines[i].strip() and not _is_block_start(lines[i].strip()):
            i += 1
    return blocks


# ---------------------------------------------------------------------------
# Shared layout maths
# ---------------------------------------------------------------------------

def is_full_bleed_image(cfg, part="header"):
    part_cfg = cfg[part]
    return (
        part_cfg["type"] == "image"
        and bool(part_cfg.get("full_bleed"))
        and bool(part_cfg.get("image"))
    )


def image_size(path):
    try:
        from PIL import Image

        with Image.open(str(path)) as pil_img:
            return pil_img.size
    except Exception:
        return None


def full_bleed_top_margin(cfg, page_width_cm):
    """Top margin that clears a full-bleed header banner: banner height + gap.

    The banner is drawn at full page width, so its rendered height follows the
    source aspect ratio. Without it the banner overlaps the first body line.
    """
    page = cfg["page"]
    if not is_full_bleed_image(cfg, "header"):
        return page["margin_top"]
    img = resolve_path(cfg["header"]["image"], cfg, Path(cfg.get("_config_dir", ".")))
    if not img:
        return max(page["margin_top"], FULL_BLEED_FALLBACK_TOP_CM)
    size = image_size(img)
    if not size or not size[0]:
        return max(page["margin_top"], FULL_BLEED_FALLBACK_TOP_CM)
    banner_cm = page_width_cm * (size[1] / size[0])
    return max(page["margin_top"], banner_cm + page.get("header_gap", 0.8))


def page_dimensions(cfg):
    page = cfg["page"]
    width, height = PAGE_SIZES.get(page["size"].upper(), PAGE_SIZES["A4"])
    landscape = page["orientation"].lower() == "landscape"
    if landscape:
        width, height = height, width
    return width, height, landscape


def doc_meta_line(cfg):
    meta = [cfg["doc"][key] for key in ("company", "author", "version", "date") if cfg["doc"].get(key)]
    return "  |  ".join(meta)


def banner_geometry(cfg, part, base_dir, page_width_pt, pt_per_cm):
    if not is_full_bleed_image(cfg, part):
        return None
    img = resolve_path(cfg[part]["image"], cfg, base_dir)
    if not img:
        warn(f"{part} image not found: {cfg[part]['image']}")
        return None
    size = image_size(img)
    height = page_width_pt * (size[1] / size[0]) if size and size[0] else 2.2 * pt_per_cm
    return (str(img), page_width_pt, height)


# ---------------------------------------------------------------------------
# .docx renderer
# ---------------------------------------------------------------------------

def shade_cell(cell, hex_color):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hex_color.strip("#"))
    cell._tc.get_or_add_tcPr().append(shd)


def shade_paragraph(paragraph, hex_color):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color.strip("#"))
    paragraph._p.get_or_add_pPr().append(shd)


# Cell tint markers: a table cell whose text starts with {green} or {red}
# renders with that fill colour; the marker itself is stripped.
CELL_TINTS = {"{green}": ("#C6EFCE", "#1E7B34"), "{red}": ("#FFC7CE", "#B00020")}


def pop_cell_tint(text):
    stripped = text.strip()
    for marker in CELL_TINTS:
        if stripped.lower().startswith(marker):
            return marker, stripped[len(marker):].strip()
    return None, stripped


def set_paragraph_border(paragraph, edge, hex_color="#BFBFBF", size=6):
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = p_pr.find(qn("w:pBdr"))
    if p_bdr is None:
        p_bdr = OxmlElement("w:pBdr")
        p_pr.append(p_bdr)
    border = OxmlElement(f"w:{edge}")
    border.set(qn("w:val"), "single")
    border.set(qn("w:sz"), str(size))
    border.set(qn("w:space"), "1")
    border.set(qn("w:color"), hex_color.strip("#"))
    p_bdr.append(border)


def add_field(paragraph, field_code):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = field_code
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(end)


def add_rich(paragraph, text, cfg, base_font=None):
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        elif part.startswith("*") and part.endswith("*"):
            run = paragraph.add_run(part[1:-1])
            run.italic = True
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            run.font.name = cfg["styles"]["code_font"]
        else:
            run = paragraph.add_run(part)
        if run.font.name != cfg["styles"]["code_font"]:
            run.font.name = base_font or cfg["styles"]["body_font"]


def setup_page(section, cfg):
    width, height, landscape = page_dimensions(cfg)
    section.orientation = WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
    section.page_width = width
    section.page_height = height
    section.left_margin = Cm(cfg["page"]["margin_left"])
    section.right_margin = Cm(cfg["page"]["margin_right"])
    section.top_margin = Cm(full_bleed_top_margin(cfg, width.cm))
    section.bottom_margin = Cm(cfg["page"]["margin_bottom"])


def setup_styles(doc, cfg):
    styles = cfg["styles"]
    normal = doc.styles["Normal"]
    normal.font.name = styles["body_font"]
    normal.font.size = Pt(styles["body_size"])
    for name, size_key in (
        ("Heading 1", "h1_size"),
        ("Heading 2", "h2_size"),
        ("Heading 3", "h3_size"),
        ("Heading 4", "h4_size"),
    ):
        style = doc.styles[name]
        style.font.name = styles["heading_font"]
        style.font.size = Pt(styles[size_key])
        style.font.color.rgb = rgb(styles["accent"])
        style.font.bold = True


def apply_cover(doc, cfg, base_dir):
    if not cfg["cover"]["enabled"]:
        return
    styles = cfg["styles"]
    # A full-bleed banner already eats the top of the page, so the cover needs
    # less manual padding to keep the title centred.
    for _ in range(3 if is_full_bleed_image(cfg, "header") else 6):
        doc.add_paragraph()
    if cfg["cover"].get("logo"):
        img = resolve_path(cfg["cover"]["logo"], cfg, base_dir)
        if img:
            par = doc.add_paragraph()
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            par.add_run().add_picture(str(img), width=Cm(10))
            doc.add_paragraph()
        else:
            warn(f"cover logo not found: {cfg['cover']['logo']}")
    doc.add_paragraph()
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(cfg["doc"]["title"])
    run.font.name = styles["heading_font"]
    run.font.size = Pt(styles["h1_size"] + 8)
    run.font.bold = True
    run.font.color.rgb = rgb(styles["accent"])
    if cfg["doc"].get("subtitle"):
        sub = doc.add_paragraph()
        sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = sub.add_run(cfg["doc"]["subtitle"])
        run.font.size = Pt(styles["h3_size"])
        run.font.color.rgb = rgb("#595959")
    doc.add_paragraph()
    meta = doc_meta_line(cfg)
    if meta:
        m = doc.add_paragraph()
        m.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = m.add_run(meta)
        run.font.color.rgb = rgb("#808080")
    doc.add_paragraph()
    add_cover_fields(doc, cfg)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def add_cover_fields(doc, cfg):
    """Document-control block: labelled rows plus an ownership notice."""
    fields = cfg["cover"].get("fields") or []
    styles = cfg["styles"]
    if fields:
        table = doc.add_table(rows=0, cols=2)
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for f in fields:
            cells = table.add_row().cells
            run = cells[0].paragraphs[0].add_run(str(f.get("label", "")))
            run.font.size = Pt(styles["body_size"])
            run.font.color.rgb = rgb("#595959")
            run = cells[1].paragraphs[0].add_run(str(f.get("value", "")))
            run.font.size = Pt(styles["body_size"])
            run.font.bold = True
        for row in table.rows:
            row.cells[0].width = Cm(5.2)
            row.cells[1].width = Cm(9.5)
        doc.add_paragraph()
    notice = cfg["cover"].get("notice")
    if notice:
        par = doc.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = par.add_run(notice)
        run.font.size = Pt(max(styles["body_size"] - 2, 8))
        run.font.color.rgb = rgb("#808080")


def apply_toc(doc, cfg):
    if not cfg["toc"]["enabled"]:
        return
    toc_title = doc.add_paragraph()
    run = toc_title.add_run("Table of Contents")
    run.font.name = cfg["styles"]["heading_font"]
    run.font.size = Pt(cfg["styles"]["h2_size"])
    run.font.bold = True
    run.font.color.rgb = rgb(cfg["styles"]["accent"])
    add_field(doc.add_paragraph(), 'TOC \\o "1-3" \\h \\z \\u')
    hint = doc.add_paragraph()
    hint_run = hint.add_run("(Right-click the table above and choose \u201cUpdate Field\u201d to fill it.)")
    hint_run.font.size = Pt(9)
    hint_run.font.italic = True
    hint_run.font.color.rgb = rgb("#808080")
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def align(value, default):
    return {
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
    }.get(str(value).lower(), default)


def apply_header_footer(section, doc, cfg, base_dir):
    # Deliberately does NOT set different_first_page_header_footer: that flag
    # blanks the banner on page 1. The section header repeats on every page.
    header_cfg = cfg["header"]
    footer_cfg = cfg["footer"]

    header_par = section.header.paragraphs[0]
    header_par.text = ""
    header_par.paragraph_format.space_before = Pt(0)
    header_par.paragraph_format.space_after = Pt(0)
    header_par.paragraph_format.line_spacing = Pt(0)
    if header_cfg["type"] == "text" and (header_cfg.get("text") or cfg["doc"]["title"]):
        header_par.alignment = align(header_cfg["align"], WD_ALIGN_PARAGRAPH.RIGHT)
        run = header_par.add_run(header_cfg.get("text") or cfg["doc"]["title"])
        run.font.name = header_cfg["font"]
        run.font.size = Pt(header_cfg["size"])
        run.font.color.rgb = rgb(header_cfg["color"])
        if header_cfg.get("border"):
            set_paragraph_border(header_par, "bottom")
    elif header_cfg["type"] == "image" and header_cfg.get("image"):
        img = resolve_path(header_cfg["image"], cfg, base_dir)
        if img:
            if header_cfg.get("full_bleed"):
                header_par.paragraph_format.left_indent = Emu(-int(section.left_margin))
                header_par.paragraph_format.right_indent = Emu(-int(section.right_margin))
                header_par.add_run().add_picture(str(img), width=Emu(section.page_width))
            else:
                header_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                header_par.add_run().add_picture(str(img), width=Cm(8))
        else:
            warn(f"header image not found: {header_cfg['image']}")
    section.header_distance = Mm(0) if is_full_bleed_image(cfg, "header") else Cm(cfg["page"]["header_distance"])

    footer_par = section.footer.paragraphs[0]
    footer_par.text = ""
    if footer_cfg["type"] == "text":
        footer_par.alignment = align(footer_cfg["align"], WD_ALIGN_PARAGRAPH.CENTER)
        if footer_cfg.get("text"):
            run = footer_par.add_run(footer_cfg["text"])
            run.font.name = footer_cfg["font"]
            run.font.size = Pt(footer_cfg["size"])
            run.font.color.rgb = rgb(footer_cfg["color"])
        if footer_cfg.get("page_numbers"):
            if footer_cfg.get("text"):
                run = footer_par.add_run("   |   ")
                run.font.color.rgb = rgb(footer_cfg["color"])
            for token in PAGE_NUMBER_FORMATS.get(
                footer_cfg.get("number_format", "page_of_numpages"), PAGE_NUMBER_FORMATS["page_of_numpages"]
            ):
                if token.startswith("_"):
                    add_field(footer_par, token[1:])
                else:
                    footer_par.add_run(token)
            for r in footer_par.runs:
                r.font.name = footer_cfg["font"]
                r.font.size = Pt(footer_cfg["size"])
                if r.font.color is None or r.font.color.rgb is None:
                    r.font.color.rgb = rgb(footer_cfg["color"])
        if footer_cfg.get("border"):
            set_paragraph_border(footer_par, "top")
    elif footer_cfg["type"] == "image" and footer_cfg.get("image"):
        img = resolve_path(footer_cfg["image"], cfg, base_dir)
        if img:
            if footer_cfg.get("full_bleed"):
                footer_par.paragraph_format.left_indent = Emu(-int(section.left_margin))
                footer_par.paragraph_format.right_indent = Emu(-int(section.right_margin))
                footer_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                footer_par.add_run().add_picture(str(img), width=Emu(section.page_width))
            else:
                footer_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                footer_par.add_run().add_picture(str(img), width=Cm(8))
        else:
            warn(f"footer image not found: {footer_cfg['image']}")
    section.footer_distance = Mm(0) if is_full_bleed_image(cfg, "footer") else Cm(cfg["page"]["footer_distance"])


def build_table(doc, header, rows, cfg):
    table = doc.add_table(rows=len(rows) + 1, cols=len(header))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    if cfg["tables"]["borders"]:
        table.style = "Table Grid"
    for j, cell_text in enumerate(header):
        cell = table.cell(0, j)
        cell.text = ""
        add_rich(cell.paragraphs[0], cell_text, cfg)
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.color.rgb = rgb(cfg["tables"]["header_font_color"])
        if cfg["tables"]["header_fill"]:
            shade_cell(cell, cfg["tables"]["header_fill"])
    for i, row in enumerate(rows):
        for j, cell_text in enumerate(row):
            if j >= len(header):
                break
            cell = table.cell(i + 1, j)
            cell.text = ""
            marker, cell_text = pop_cell_tint(cell_text)
            add_rich(cell.paragraphs[0], cell_text, cfg)
            if marker:
                fill, font_color = CELL_TINTS[marker]
                shade_cell(cell, fill)
                for run in cell.paragraphs[0].runs:
                    run.font.color.rgb = rgb(font_color)
            elif cfg["tables"]["zebra"] and i % 2 == 1:
                shade_cell(cell, "#F2F2F2")
    if header:
        table.columns[0].width = Cm(3)


def render_docx(cfg, blocks, base_dir):
    doc = Document()
    section = doc.sections[0]
    setup_page(section, cfg)
    setup_styles(doc, cfg)
    apply_header_footer(section, doc, cfg, base_dir)
    apply_cover(doc, cfg, base_dir)
    apply_toc(doc, cfg)
    for block in blocks:
        kind = block[0]
        if kind == "code":
            for code_line in block[1]:
                par = doc.add_paragraph(code_line if code_line else " ")
                par.style = doc.styles["No Spacing"]
                for run in par.runs:
                    run.font.name = cfg["styles"]["code_font"]
                    run.font.size = Pt(max(cfg["styles"]["body_size"] - 1, 9))
                shade_paragraph(par, "#F5F5F5")
            continue
        if kind == "table":
            build_table(doc, block[1], block[2], cfg)
            doc.add_paragraph()
            continue
        if kind == "rule":
            par = doc.add_paragraph()
            set_paragraph_border(par, "bottom", hex_color="#BFBFBF", size=8)
            continue
        if kind == "pagebreak":
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
            continue
        if kind == "heading":
            heading = doc.add_heading(level=block[1])
            add_rich(heading, block[2], cfg, base_font=cfg["styles"]["heading_font"])
            continue
        if kind == "image":
            img = resolve_path(block[1], cfg, base_dir)
            if img:
                par = doc.add_paragraph()
                par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                par.add_run().add_picture(str(img), width=Cm(cfg["images"]["width_cm"]))
            else:
                warn(f"inline image not found: {block[1]}")
            continue
        if kind == "number":
            numbering = doc.add_paragraph(style="List Number")
            add_rich(numbering, block[1], cfg)
            continue
        if kind == "bullet":
            text, depth = block[1], block[2]
            bullet = doc.add_paragraph(style="List Bullet")
            if depth:
                # python-docx has no guaranteed multi-level list style, so nest
                # by indentation instead of silently flattening.
                bullet.paragraph_format.left_indent = Cm(0.63 * depth)
            add_rich(bullet, text, cfg)
            continue
        par = doc.add_paragraph()
        add_rich(par, block[1], cfg)
    return doc


# ---------------------------------------------------------------------------
# .pdf renderer (ReportLab) — same config, same blocks
# ---------------------------------------------------------------------------

# Configured families that this machine may not actually have; each maps to
# install locations tried before falling back to a built-in face.
PDF_TTF_CANDIDATES = {
    "Calibri": [
        "/System/Library/Fonts/Supplemental/Calibri.ttf",
        "/Library/Fonts/Calibri.ttf",
        "/Library/Fonts/Carlito-Regular.ttf",
        "/usr/share/fonts/truetype/croasest/Carlito-Regular.ttf",
    ],
    "Consolas": [
        "/System/Library/Fonts/Supplemental/Consolas.ttf",
        "/Library/Fonts/Consolas.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ],
}
PDF_BUILTIN = {"helvetica", "times", "courier"}


def build_pdf(cfg, blocks, base_dir, out_path):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A3, A4, LETTER, landscape
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        BaseDocTemplate,
        Frame,
        Image as RLImage,
        PageBreak,
        PageTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        XPreformatted,
    )
    from reportlab.platypus.tableofcontents import TableOfContents

    styles_cfg = cfg["styles"]
    base_size = styles_cfg["body_size"]
    accent_hex = styles_cfg["accent"]

    def colour(value):
        return colors.HexColor(value)

    page_map = {"A4": A4, "A3": A3, "LETTER": LETTER}
    pdf_page = page_map.get(cfg["page"]["size"].upper(), A4)
    if cfg["page"]["orientation"].lower() == "landscape":
        pdf_page = landscape(pdf_page)
    page_w, page_h = pdf_page

    # Fonts: Calibri/Consolas are usually absent on non-Windows machines, so try
    # the configured family on disk and otherwise pick the nearest built-in and
    # say so, rather than quietly shipping a substituted typeface.
    registered = {}

    def face(name, bold=False):
        key = (name, bold)
        if key in registered:
            return registered[key]
        resolved = None
        for candidate in PDF_TTF_CANDIDATES.get(name, []):
            if Path(candidate).exists():
                try:
                    tag = f"{name}-{Path(candidate).stem}"
                    pdfmetrics.registerFont(TTFont(tag, candidate))
                    resolved = tag
                    break
                except Exception:
                    continue
        if resolved is None:
            lowered = (name or "").lower()
            if lowered.startswith("helv") or lowered.startswith("arial"):
                resolved = "Helvetica-Bold" if bold else "Helvetica"
            elif lowered.startswith("time") or lowered.startswith("georgia"):
                resolved = "Times-Bold" if bold else "Times-Roman"
            elif lowered.startswith(("cons", "mono", "cour", "dejavu")):
                resolved = "Courier-Bold" if bold else "Courier"
            else:
                if name:
                    warn(f"'{name}' is not installed; the PDF uses Helvetica for it")
                resolved = "Helvetica-Bold" if bold else "Helvetica"
        registered[key] = resolved
        return resolved

    heading_styles = {
        level: ParagraphStyle(
            f"h{level}",
            fontName=face(styles_cfg["heading_font"], True),
            fontSize=styles_cfg[size_key],
            leading=styles_cfg[size_key] * 1.25,
            textColor=colour(accent_hex),
            spaceBefore=10 if level > 1 else 4,
            spaceAfter=6,
            keepWithNext=1,
        )
        for level, size_key in ((1, "h1_size"), (2, "h2_size"), (3, "h3_size"), (4, "h4_size"))
    }
    body_style = ParagraphStyle("body", fontName=face(styles_cfg["body_font"]), fontSize=base_size,
                                leading=base_size * 1.35, spaceAfter=6)
    code_style = ParagraphStyle("code", fontName=face(styles_cfg["code_font"]),
                                fontSize=max(base_size - 1, 9), leading=max(base_size - 1, 9) * 1.25,
                                backColor=colour("#F5F5F5"), borderPadding=3, spaceAfter=1)
    cell_style = ParagraphStyle("cell", parent=body_style, fontSize=max(base_size - 1, 9), spaceAfter=0)
    tint_cell_styles = {marker: ParagraphStyle(f"cell{marker}", parent=cell_style,
                                                textColor=colour(font_color))
                        for marker, (fill, font_color) in CELL_TINTS.items()}
    header_cell_style = ParagraphStyle(
        "headerCell", parent=cell_style,
        fontName=face(styles_cfg["heading_font"], True),
        # TableStyle TEXTCOLOR can't override a Paragraph's own colour.
        textColor=colour(cfg["tables"]["header_font_color"]) if cfg["tables"]["header_fill"] else colour("#000000"))

    def rich(text):
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        for part in INLINE.split(escaped):
            if part.startswith("**") and part.endswith("**"):
                escaped = escaped.replace(part, f"<b>{part[2:-2]}</b>", 1)
            elif part.startswith("*") and part.endswith("*"):
                escaped = escaped.replace(part, f"<i>{part[1:-1]}</i>", 1)
            elif part.startswith("`") and part.endswith("`"):
                escaped = escaped.replace(part, f'<font face="{face(styles_cfg["code_font"])}">{part[1:-1]}</font>', 1)
        return escaped

    def fitted_image(path, width_pt):
        """ReportLab needs both edges up front: height=0 silently renders nothing."""
        from reportlab.lib.utils import ImageReader

        native_w, native_h = ImageReader(str(path)).getSize()
        flowable = RLImage(str(path), width=width_pt, height=width_pt * native_h / native_w)
        flowable.hAlign = "CENTER"  # the .docx renderer centres images too
        return flowable

    left = cfg["page"]["margin_left"] * cm
    right = cfg["page"]["margin_right"] * cm
    bottom = cfg["page"]["margin_bottom"] * cm
    top = full_bleed_top_margin(cfg, page_w / cm) * cm

    header_cfg = cfg["header"]
    footer_cfg = cfg["footer"]
    top_banner = banner_geometry(cfg, "header", base_dir, page_w, cm)
    bottom_banner = banner_geometry(cfg, "footer", base_dir, page_w, cm)

    total_pages = {"n": None}

    def footer_line(page_index):
        pieces = []
        if footer_cfg.get("text"):
            pieces.append(footer_cfg["text"])
        if footer_cfg.get("page_numbers"):
            rendered = []
            for token in PAGE_NUMBER_FORMATS.get(
                footer_cfg.get("number_format", "page_of_numpages"), PAGE_NUMBER_FORMATS["page_of_numpages"]
            ):
                if token == "_PAGE":
                    rendered.append(str(page_index))
                elif token == "_NUMPAGES":
                    rendered.append(str(total_pages["n"]) if total_pages["n"] else "")
                else:
                    rendered.append(token)
            pieces.append("".join(rendered))
        return "   |   ".join(pieces)

    def draw_page(canvas, _doc):
        canvas.saveState()
        if top_banner:
            path, w, h = top_banner
            canvas.drawImage(path, 0, page_h - h, width=w, height=h)
        elif header_cfg["type"] == "text" and (header_cfg.get("text") or cfg["doc"]["title"]):
            size = header_cfg["size"]
            y = page_h - cfg["page"]["header_distance"] * cm - size
            canvas.setFont(face(header_cfg["font"]), size)
            canvas.setFillColor(colour(header_cfg["color"]))
            canvas.drawRightString(page_w - right, y, header_cfg.get("text") or cfg["doc"]["title"])
            if header_cfg.get("border"):
                canvas.setStrokeColor(colour("#BFBFBF"))
                canvas.setLineWidth(0.6)
                canvas.line(left, y - 3, page_w - right, y - 3)

        if bottom_banner:
            path, w, h = bottom_banner
            canvas.drawImage(path, 0, 0, width=w, height=h)
        elif footer_cfg["type"] == "text" and (footer_cfg.get("text") or footer_cfg.get("page_numbers")):
            size = footer_cfg["size"]
            y = cfg["page"]["footer_distance"] * cm
            canvas.setFont(face(footer_cfg["font"]), size)
            canvas.setFillColor(colour(footer_cfg["color"]))
            line = footer_line(canvas.getPageNumber())
            mode = str(footer_cfg["align"]).lower()
            if mode == "left":
                canvas.drawString(left, y, line)
            elif mode == "right":
                canvas.drawRightString(page_w - right, y, line)
            else:
                canvas.drawCentredString(page_w / 2.0, y, line)
            if footer_cfg.get("border"):
                canvas.setStrokeColor(colour("#BFBFBF"))
                canvas.setLineWidth(0.6)
                canvas.line(left, y + size + 3, page_w - right, y + size + 3)
        canvas.restoreState()

    def column_weights(header, rows):
        strip = lambda t: re.sub(r"[*`]|\{(?:green|red)\}", "", t)
        widths = []
        longest_word = []
        cell_size = max(base_size - 1, 9)
        cell_faces = [face(styles_cfg["body_font"]), face(styles_cfg["code_font"])]
        for j in range(len(header)):
            cells = [strip(header[j])] + [strip(row[j]) for row in rows if j < len(row)]
            widths.append(max([len(c) for c in cells] + [4]))
            words = [w for c in cells for w in c.split() if w]
            longest_word.append(
                max(
                    [max(pdfmetrics.stringWidth(w, f, cell_size) for f in cell_faces) for w in words]
                    + [1]
                )
            )
        total = sum(widths) or 1
        avail = page_w - left - right
        scaled = [avail * (w / total) for w in widths]
        # A column narrower than its longest word breaks that word mid-token, so
        # every column gets at least its word width plus the cell padding. Inline
        # code renders in the wider code face, so that face sets the floor too.
        floors = [w + 0.6 * cm for w in longest_word]
        needed = sum(floors)
        if needed > avail:
            # Floors that cannot all fit are scaled to the page instead of being
            # applied as-is, which is what pushed a wide table past the margins.
            floors = [f * avail / needed for f in floors]
        scaled = [max(s, f) for s, f in zip(scaled, floors)]
        overshoot = sum(scaled) - avail
        while overshoot > 1e-6:
            giveable = [scaled[j] - floors[j] for j in range(len(scaled))]
            if max(giveable) <= 0:
                break
            j = max(range(len(scaled)), key=lambda i: giveable[i])
            take = min(overshoot, giveable[j])
            scaled[j] -= take
            overshoot -= take
        total_w = sum(scaled)
        if total_w > avail:
            scaled = [s * avail / total_w for s in scaled]
        return scaled

    story = []
    if cfg["cover"]["enabled"]:
        pad = 3 if is_full_bleed_image(cfg, "header") else 6
        story.append(Spacer(1, pad * base_size * 1.4))
        if cfg["cover"].get("logo"):
            logo = resolve_path(cfg["cover"]["logo"], cfg, base_dir)
            if logo:
                story.append(fitted_image(logo, 10 * cm))
                story.append(Spacer(1, 0.4 * cm))
            else:
                warn(f"cover logo not found: {cfg['cover']['logo']}")
        # ReportLab's ParagraphStyle has no automatic leading: every style built
        # without one overlaps its own wrapped lines.
        title_size = styles_cfg["h1_size"] + 8
        story.append(Paragraph(rich(cfg["doc"]["title"]), ParagraphStyle(
            "coverTitle", fontName=face(styles_cfg["heading_font"], True), fontSize=title_size,
            leading=title_size * 1.25, textColor=colour(accent_hex), alignment=1, spaceAfter=14)))
        if cfg["doc"].get("subtitle"):
            story.append(Paragraph(rich(cfg["doc"]["subtitle"]), ParagraphStyle(
                "coverSub", fontName=face(styles_cfg["body_font"]), fontSize=styles_cfg["h3_size"],
                leading=styles_cfg["h3_size"] * 1.4, textColor=colour("#595959"), alignment=1, spaceAfter=14)))
        meta = doc_meta_line(cfg)
        if meta:
            story.append(Paragraph(meta.replace("&", "&amp;"), ParagraphStyle(
                "coverMeta", fontName=face(styles_cfg["body_font"]), fontSize=base_size,
                leading=base_size * 1.4, textColor=colour("#808080"), alignment=1)))
        fields = cfg["cover"].get("fields") or []
        if fields:
            story.append(Spacer(1, 1.4 * cm))
            label_style = ParagraphStyle("coverLabel", parent=body_style, fontSize=base_size,
                                         leading=base_size * 1.4, alignment=0, spaceAfter=0,
                                         textColor=colour("#595959"))
            value_style = ParagraphStyle("coverValue", parent=label_style,
                                         fontName=face(styles_cfg["body_font"], True),
                                         textColor=colour("#000000"))
            grid = [[Paragraph(str(f.get("label", "")).replace("&", "&amp;"), label_style),
                     Paragraph(str(f.get("value", "")).replace("&", "&amp;"), value_style)]
                    for f in fields]
            control = Table(grid, colWidths=[5.2 * cm, 9.5 * cm])
            control.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.6, colour("#BFBFBF")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (0, -1), colour("#F7F7F7")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(control)
        notice = cfg["cover"].get("notice")
        if notice:
            story.append(Spacer(1, 1.2 * cm))
            story.append(Paragraph(notice.replace("&", "&amp;"), ParagraphStyle(
                "coverNotice", parent=body_style, fontSize=max(base_size - 2, 8),
                leading=max(base_size - 2, 8) * 1.45, textColor=colour("#808080"), alignment=1)))
        story.append(PageBreak())

    if cfg["toc"]["enabled"]:
        # A style named h1..h3 would feed the TOC its own title.
        story.append(Paragraph("Table of Contents", ParagraphStyle(
            "tocTitle", parent=heading_styles[2])))
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(f"toc{level}", fontName=face(styles_cfg["body_font"]),
                           fontSize=base_size - level, leading=(base_size - level) * 1.4,
                           leftIndent=8 * (level - 1), spaceBefore=2, endDots=1)
            for level in (1, 2, 3)
        ]
        story.append(toc)
        story.append(PageBreak())

    for block in blocks:
        kind = block[0]
        if kind == "heading":
            level, text = block[1], block[2]
            story.append(Paragraph(rich(text), heading_styles[min(level, 4)]))
            continue
        if kind == "code":
            for code_line in block[1]:
                escaped = code_line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(XPreformatted(escaped or " ", code_style))
            story.append(Spacer(1, 0.18 * cm))
            continue
        if kind == "table":
            header, rows = block[1], block[2]
            ncols = len(header)
            grid = [[Paragraph(rich(c), header_cell_style) for c in header]]
            tints = {}
            for ri, row in enumerate(rows):
                line = []
                for j in range(ncols):
                    marker, rest = pop_cell_tint(row[j] if j < len(row) else "")
                    if marker:
                        tints[(ri + 1, j)] = CELL_TINTS[marker]
                    line.append(Paragraph(rich(rest), tint_cell_styles.get(marker, cell_style)))
                grid.append(line)
            cmds = [("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
            if cfg["tables"]["header_fill"]:
                cmds.append(("BACKGROUND", (0, 0), (-1, 0), colour(cfg["tables"]["header_fill"])))
                cmds.append(("TEXTCOLOR", (0, 0), (-1, 0), colour(cfg["tables"]["header_font_color"])))
            if cfg["tables"]["borders"]:
                cmds.append(("GRID", (0, 0), (-1, -1), 0.5, colour("#BFBFBF")))
            if cfg["tables"]["zebra"]:
                cmds.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colour("#F2F2F2")]))
            for (ri, j), (fill, font_color) in tints.items():
                cmds.append(("BACKGROUND", (j, ri), (j, ri), colour(fill)))
            table = Table(grid, colWidths=column_weights(header, rows), repeatRows=1)
            table.setStyle(TableStyle(cmds))
            story.append(table)
            story.append(Spacer(1, 0.25 * cm))
            continue
        if kind == "rule":
            story.append(Spacer(1, 0.1 * cm))
            rule = Table([[""]], colWidths=[page_w - left - right],
                         style=TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.8, colour("#BFBFBF"))]))
            story.append(rule)
            story.append(Spacer(1, 0.1 * cm))
            continue
        if kind == "pagebreak":
            story.append(PageBreak())
            continue
        if kind == "image":
            img = resolve_path(block[1], cfg, base_dir)
            if img:
                width = min(cfg["images"]["width_cm"] * cm, page_w - left - right)
                story.append(fitted_image(img, width))
                story.append(Spacer(1, 0.2 * cm))
            else:
                warn(f"inline image not found: {block[1]}")
            continue
        if kind == "number":
            # Word auto-numbers "List Number"; ReportLab has no equivalent
            # counter, so the literal markdown number is rendered instead.
            style = ParagraphStyle("number", parent=body_style, leftIndent=24, firstLineIndent=-14, spaceAfter=2)
            story.append(Paragraph(f"{block[2]}.&nbsp;{rich(block[1])}", style))
            continue
        if kind == "bullet":
            text, depth = block[1], block[2]
            style = ParagraphStyle(f"bullet{depth}", parent=body_style, leftIndent=10 + 14 * depth)
            story.append(Paragraph(f"\u2022&nbsp;{rich(text)}", style))
            continue
        story.append(Paragraph(rich(block[1]), body_style))

    class TocDocTemplate(BaseDocTemplate):
        """Feeds real headings into the Word-independent ReportLab TOC."""

        _h_keys = []

        def handle_documentBegin(self):
            # multiBuild re-renders every pass; a counter that kept growing
            # across passes would change each bookmark key forever and the TOC
            # would never settle.
            self._h_keys = []
            BaseDocTemplate.handle_documentBegin(self)

        def afterFlowable(self, flowable):
            name = getattr(getattr(flowable, "style", None), "name", "")
            if not (isinstance(flowable, Paragraph) and re.match(r"^h[123]$", name)):
                return
            level = int(name[1])
            text = flowable.getPlainText()
            key = f"h{level}-{len(self._h_keys)}-{re.sub(r'\W+', '-', text)[:40]}"
            self._h_keys.append(key)
            self.canv.bookmarkPage(key)
            self.notify("TOCEntry", (level - 1, text, self.page, key))

    def render(target):
        template = TocDocTemplate(
            str(target), pagesize=pdf_page,
            leftMargin=left, rightMargin=right, topMargin=top, bottomMargin=bottom,
            title=cfg["doc"]["title"],
            author=cfg["doc"].get("author") or cfg["doc"].get("company") or "",
        )
        template._h_keys = []
        frame = Frame(left, bottom, page_w - left - right, page_h - top - bottom, id="body",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        template.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=draw_page)])
        template.multiBuild(copy.deepcopy(story))
        return template.page

    # Page numbering needs the total, which is only known after the first pass.
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as probe:
        probe_path = Path(probe.name)
    try:
        total_pages["n"] = render(probe_path)
        render(out_path)
    finally:
        probe_path.unlink(missing_ok=True)
    return Path(out_path)


def deep_merge(base, override):
    out = dict(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def main():
    parser = argparse.ArgumentParser(description="Generate a branded .docx or .pdf from Markdown.")
    parser.add_argument("content", help="Markdown content file")
    parser.add_argument("config", help="JSON config file")
    parser.add_argument("output", help="Output .docx or .pdf path (format picked by extension)")
    args = parser.parse_args()

    content_path = Path(args.content)
    cfg_path = Path(args.config)
    base_dir = content_path.resolve().parent
    cfg = deep_merge(DEFAULTS, json.loads(cfg_path.read_text(encoding="utf-8")))
    cfg["_config_dir"] = str(cfg_path.resolve().parent)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    blocks = parse_blocks(content_path.read_text(encoding="utf-8"), cfg)

    if out.suffix.lower() == ".pdf":
        build_pdf(cfg, blocks, base_dir, out)
    else:
        render_docx(cfg, blocks, base_dir).save(out)
    print(f"OK -> {out}")


if __name__ == "__main__":
    main()
