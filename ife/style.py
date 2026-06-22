"""
Styling for the Institutional Forecasting Engine.

Implements the mandated colour code as font colours (blue inputs, black formulas,
green key outputs, white-on-gray headers, red errors) with subtle fills to make
input/output cells easy to find, exposed through one ``apply()`` function.
"""

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
B_GRID = Border(left=_thin, right=_thin, top=_thin, bottom=_thin)
B_BOX = Border(left=_med, right=_med, top=_med, bottom=_med)
B_BOTTOM = Border(bottom=_thin)
B_TOP = Border(top=_med)
B_NONE = Border()

A_L = Alignment(horizontal="left", vertical="center")
A_C = Alignment(horizontal="center", vertical="center")
A_R = Alignment(horizontal="right", vertical="center")
A_LW = Alignment(horizontal="left", vertical="center", wrap_text=True)
A_LTW = Alignment(horizontal="left", vertical="top", wrap_text=True)

LOCKED = Protection(locked=True)
UNLOCKED = Protection(locked=False)

_ROLES = {
    "title": (_font(Palette.WHITE, 18, bold=True), _fill(Palette.TITLE), A_L, B_NONE, True),
    "subtitle": (_font(Palette.WHITE, 11), _fill(Palette.TITLE), A_L, B_NONE, True),
    "header": (_font(Palette.WHITE, 12, bold=True), _fill(Palette.HEADER), A_L, B_NONE, True),
    "subheader": (_font(Palette.WHITE, 10, bold=True), _fill(Palette.SUBHEADER), A_L, B_NONE, True),
    "colhdr": (_font(Palette.WHITE, 9, bold=True), _fill(Palette.SUBHEADER), A_C, B_NONE, True),
    "colhdr_r": (_font(Palette.WHITE, 9, bold=True), _fill(Palette.SUBHEADER), A_R, B_NONE, True),
    # actual vs forecast year headers (distinct, so the two can never be confused)
    "actual_hdr": (_font(Palette.WHITE, 9, bold=True), _fill(Palette.ACTUAL_HDR), A_C, B_NONE, True),
    "fcst_hdr": (_font(Palette.WHITE, 9, bold=True), _fill(Palette.FCST_HDR), A_C, B_NONE, True),
    "actual_tag": (_font(Palette.ACTUAL_HDR, 9, bold=True), _fill(Palette.ACTUAL_FILL), A_C, B_GRID, True),
    "fcst_tag": (_font(Palette.FCST_HDR, 9, bold=True), _fill(Palette.FCST_FILL), A_C, B_GRID, True),
    "label": (_font(Palette.TEXT, SZ), None, A_L, B_NONE, True),
    "label_b": (_font(Palette.TEXT, SZ, bold=True), None, A_L, B_NONE, True),
    "sublabel": (_font(Palette.MUTED, 9, italic=True), None, A_L, B_NONE, True),
    "note": (_font(Palette.MUTED, 8.5), None, A_LW, B_NONE, True),
    "note_l": (_font(Palette.MUTED, 8.5), None, A_L, B_NONE, True),
    # colour code
    "input": (_font(Palette.INPUT, SZ), _fill(Palette.INPUT_FILL), A_R, B_GRID, False),
    "input_l": (_font(Palette.INPUT, SZ), _fill(Palette.INPUT_FILL), A_L, B_GRID, False),
    "formula": (_font(Palette.FORMULA, SZ), None, A_R, B_NONE, True),
    "formula_l": (_font(Palette.FORMULA, SZ), None, A_L, B_NONE, True),
    "output": (_font(Palette.OUTPUT, SZ, bold=True), _fill(Palette.OUTPUT_FILL), A_R, B_GRID, True),
    "output_l": (_font(Palette.OUTPUT, SZ, bold=True), _fill(Palette.OUTPUT_FILL), A_L, B_GRID, True),
    "error": (_font(Palette.ERROR, SZ, bold=True), _fill(Palette.ERROR_FILL), A_C, B_GRID, True),
    "status": (_font(Palette.TEXT, SZ, bold=True), None, A_C, B_GRID, True),
    "panel": (_font(Palette.TEXT, SZ), _fill(Palette.PANEL), A_L, B_NONE, True),
    "kpi": (_font(Palette.OUTPUT, 16, bold=True), _fill(Palette.PANEL), A_C, B_BOX, True),
    "total": (_font(Palette.TEXT, SZ, bold=True), _fill(Palette.BAND), A_R, B_TOP, True),
    "total_l": (_font(Palette.TEXT, SZ, bold=True), _fill(Palette.BAND), A_L, B_TOP, True),
}

_ALIGN = {"l": A_L, "c": A_C, "r": A_R, "lw": A_LW, "ltw": A_LTW}


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
