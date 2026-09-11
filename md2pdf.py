# -*- coding: utf-8 -*-
"""Markdown -> PDF via markdown-it-py + reportlab (Cyrillic-safe)."""
import re, sys
from markdown_it import MarkdownIt
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable)
from reportlab.lib.styles import ParagraphStyle

SRC, DST = sys.argv[1], sys.argv[2]

FD = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("A", FD + "Arial.ttf"))
pdfmetrics.registerFont(TTFont("AB", FD + "Arial Bold.ttf"))
pdfmetrics.registerFont(TTFont("AI", FD + "Arial Italic.ttf"))
pdfmetrics.registerFont(TTFont("ABI", FD + "Arial Bold Italic.ttf"))

def esc(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*\*(.+?)\*\*\*", r'<font name="ABI">\1</font>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r'<font name="AB">\1</font>', t)
    t = re.sub(r"(?<!\w)\*([^*]+?)\*(?!\w)", r'<font name="AI">\1</font>', t)
    t = re.sub(r"`([^`]+)`", r'<font name="A" backColor="#f0f0f0">\1</font>', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<font color="#1a5fb4">\1</font>', t)
    return t

S = {
 "h1": ParagraphStyle("h1", fontName="AB", fontSize=17, leading=22, spaceBefore=14, spaceAfter=8, textColor=colors.HexColor("#111111")),
 "h2": ParagraphStyle("h2", fontName="AB", fontSize=13.5, leading=18, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#1a5fb4")),
 "h3": ParagraphStyle("h3", fontName="AB", fontSize=11.5, leading=15, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#333333")),
 "p":  ParagraphStyle("p", fontName="A", fontSize=9.5, leading=13.5, spaceAfter=5),
 "li": ParagraphStyle("li", fontName="A", fontSize=9.5, leading=13.5, spaceAfter=3, leftIndent=14, bulletIndent=4),
 "td": ParagraphStyle("td", fontName="A", fontSize=8, leading=10.5),
 "th": ParagraphStyle("th", fontName="AB", fontSize=8, leading=10.5, textColor=colors.white),
}

md = MarkdownIt("commonmark").enable("table")
tokens = md.parse(open(SRC, encoding="utf-8").read())

story, i = [], 0
while i < len(tokens):
    t = tokens[i]
    if t.type == "heading_open":
        lvl = int(t.tag[1]); txt = tokens[i+1].content
        story.append(Paragraph(esc(txt), S.get(f"h{min(lvl,3)}", S["h3"]))); i += 3
    elif t.type == "paragraph_open":
        story.append(Paragraph(esc(tokens[i+1].content), S["p"])); i += 3
    elif t.type == "bullet_list_open" or t.type == "ordered_list_open":
        ordered = t.type == "ordered_list_open"; n = 0; i += 1
        while tokens[i].type not in ("bullet_list_close", "ordered_list_close"):
            if tokens[i].type == "list_item_open":
                n += 1; i += 1
                if tokens[i].type == "paragraph_open":
                    txt = tokens[i+1].content; i += 3
                else:
                    txt = tokens[i].content if tokens[i].type == "inline" else ""; i += 1
                bullet = f"{n}." if ordered else "•"
                story.append(Paragraph(esc(txt), S["li"], bulletText=bullet))
            else:
                i += 1
        i += 1
        story.append(Spacer(1, 2*mm))
    elif t.type == "table_open":
        i += 1; header, rows = [], []
        while tokens[i].type != "table_close":
            if tokens[i].type == "tr_open":
                row = []
                i += 1
                while tokens[i].type != "tr_close":
                    if tokens[i].type in ("th_open", "td_open"):
                        row.append(tokens[i+1].content); i += 3
                    else:
                        i += 1
                (header if not header and tokens[i-3].type == "th_open" or not header and rows==[] and any("th" in x for x in []) else rows)
                i += 1
                if not header:
                    header = row
                else:
                    rows.append(row)
            else:
                i += 1
        data = [[Paragraph(esc(c), S["th"]) for c in header]] + \
               [[Paragraph(esc(c), S["td"]) for c in r] for r in rows]
        ncol = len(header)
        tbl = Table(data, colWidths=[(180*mm)/ncol]*ncol, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a5fb4")),
            ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f4f7fb")]),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ]))
        story.append(tbl); story.append(Spacer(1, 3*mm)); i += 1
    elif t.type == "hr":
        story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#bbbbbb"), spaceBefore=6, spaceAfter=6)); i += 1
    else:
        i += 1

doc = SimpleDocTemplate(DST, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm,
                        topMargin=15*mm, bottomMargin=15*mm, title="Анализ рынка видеографии 2026")
doc.build(story)
print("OK", DST)
