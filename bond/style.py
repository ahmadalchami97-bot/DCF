"""Styling for the Fixed-Rate Bond Analyzer (one apply() used by every sheet)."""

from __future__ import annotations

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.styles.protection import Protection

from .config import Palette

FONT = "Calibri"
SZ = 10


def _fill(c):
    return PatternFill(start_color=c, end_color=c, fill_type="solid") if c else None


def _font(color=Palette.TEXT, size=SZ, bold=False, italic=False):
    return Font(name=FONT, size=size, color=color, bold=bold, italic=italic)


_thin = Side(style="thin", color=Palette.GRID)
_med = Side(style="medium", color=Palette.RULE)
_amber = Side(style="medium", color=Palette.EXPLAIN_BORDER)
B_GRID = Border(left=_thin, right=_thin, top=_thin, bottom=_thin)
B_BOX = Border(left=_med, right=_med, top=_med, bottom=_med)
B_EXPLAIN = Border(left=_amber, right=_amber, top=_amber, bottom=_amber)
B_TOP = Border(top=_med)
B_NONE = Border()

A_L = Alignment(horizontal="left", vertical="center")
A_C = Alignment(horizontal="center", vertical="center")
A_R = Alignment(horizontal="right", vertical="center")
A_LW = Alignment(horizontal="left", vertical="center", wrap_text=True)
A_LTW = Alignment(horizontal="left", vertical="top", wrap_text=True)
A_CW = Alignment(horizontal="center", vertical="center", wrap_text=True)

LOCKED = Protection(locked=True)
UNLOCKED = Protection(locked=False)

_ROLES = {
    "title": (_font(Palette.WHITE, 18, bold=True), _fill(Palette.TITLE), A_L, B_NONE, True),
    "subtitle": (_font(Palette.WHITE, 11), _fill(Palette.TITLE), A_L, B_NONE, True),
    "header": (_font(Palette.WHITE, 12, bold=True), _fill(Palette.HEADER), A_L, B_NONE, True),
    "section": (_font(Palette.WHITE, 10, bold=True), _fill(Palette.SECTION), A_L, B_NONE, True),
    "colhdr": (_font(Palette.WHITE, 9, bold=True), _fill(Palette.HEADER), A_C, B_NONE, True),
    "colhdr_l": (_font(Palette.WHITE, 9, bold=True), _fill(Palette.HEADER), A_L, B_NONE, True),
    "label": (_font(Palette.TEXT, SZ), None, A_L, B_NONE, True),
    "label_b": (_font(Palette.TEXT, SZ, bold=True), None, A_L, B_NONE, True),
    "sublabel": (_font(Palette.MUTED, 9, italic=True), None, A_L, B_NONE, True),
    "note": (_font(Palette.MUTED, 9), None, A_LW, B_NONE, True),
    "note_l": (_font(Palette.MUTED, 9), None, A_L, B_NONE, True),
    "explain": (_font(Palette.TEXT, 9), _fill(Palette.EXPLAIN_FILL), A_LTW, B_EXPLAIN, True),
    "input": (_font(Palette.INPUT, SZ), _fill(Palette.INPUT_FILL), A_R, B_GRID, False),
    "input_l": (_font(Palette.INPUT, SZ), _fill(Palette.INPUT_FILL), A_L, B_GRID, False),
    "input_c": (_font(Palette.INPUT, SZ), _fill(Palette.INPUT_FILL), A_C, B_GRID, False),
    "formula": (_font(Palette.FORMULA, SZ), None, A_R, B_NONE, True),
    "formula_l": (_font(Palette.FORMULA, SZ), None, A_L, B_NONE, True),
    "link": (_font(Palette.LINK, SZ), None, A_R, B_NONE, True),
    "output": (_font(Palette.OUTPUT, SZ, bold=True), _fill(Palette.OUTPUT_FILL), A_R, B_GRID, True),
    "output_l": (_font(Palette.OUTPUT, SZ, bold=True), _fill(Palette.OUTPUT_FILL), A_L, B_GRID, True),
    "result": (_font(Palette.OUTPUT, 12, bold=True), _fill(Palette.RESULT_FILL), A_R, B_BOX, True),
    "kpi": (_font(Palette.OUTPUT, 14, bold=True), _fill(Palette.PANEL), A_C, B_BOX, True),
    "status": (_font(Palette.TEXT, SZ, bold=True), None, A_C, B_GRID, True),
    "panel": (_font(Palette.TEXT, SZ), _fill(Palette.PANEL), A_L, B_NONE, True),
    "total": (_font(Palette.TEXT, SZ, bold=True), _fill(Palette.BAND), A_R, B_TOP, True),
    "total_l": (_font(Palette.TEXT, SZ, bold=True), _fill(Palette.BAND), A_L, B_TOP, True),
}

_ALIGN = {"l": A_L, "c": A_C, "r": A_R, "lw": A_LW, "ltw": A_LTW, "cw": A_CW}


def apply(cell, role="label", *, fmt=None, bold=None, italic=None, align=None,
          fill=None, font_color=None, size=None, border=None, locked=None):
    bf, bfill, balign, bborder, blocked = _ROLES.get(role, _ROLES["label"])
    f = bf
    if any(v is not None for v in (bold, italic, font_color, size)):
        f = Font(name=FONT, size=size if size is not None else f.size,
                 color=font_color if font_color is not None else f.color,
                 bold=bold if bold is not None else f.bold,
                 italic=italic if italic is not None else f.italic)
    cell.font = f
    if fill is not None:
        cell.fill = _fill(fill)
    elif bfill is not None:
        cell.fill = bfill
    cell.alignment = _ALIGN.get(align, balign) if align else balign
    cell.border = border if border is not None else bborder
    if fmt is not None:
        cell.number_format = fmt
    cell.protection = LOCKED if (blocked if locked is None else locked) else UNLOCKED
    return cell
