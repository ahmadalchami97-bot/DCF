"""
Styling for the Financial Ratio Analysis workbook.

Implements the mandated cell-type colour scheme (input = yellow, formula = blue,
output = green, error = red) plus an institutional header palette, exposed through
one ``apply()`` function used by every sheet. Cell-protection attributes are set
per role (inputs unlocked, formulas/outputs locked) so sheet protection can be
toggled on without blocking data entry.
"""

from __future__ import annotations

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.styles.protection import Protection

from .config import Palette

FONT = "Calibri"
SZ = 10


def _fill(color):
    return PatternFill(start_color=color, end_color=color, fill_type="solid") if color else None


def _font(color=Palette.TEXT, size=SZ, bold=False, italic=False):
    return Font(name=FONT, size=size, color=color, bold=bold, italic=italic)


_thin = Side(style="thin", color=Palette.GRID)
_med = Side(style="medium", color=Palette.RULE)
B_GRID = Border(left=_thin, right=_thin, top=_thin, bottom=_thin)
B_BOX = Border(left=_med, right=_med, top=_med, bottom=_med)
B_BOTTOM = Border(bottom=_thin)
B_UNDER = Border(bottom=_med)
B_NONE = Border()

A_L = Alignment(horizontal="left", vertical="center")
A_C = Alignment(horizontal="center", vertical="center")
A_R = Alignment(horizontal="right", vertical="center")
A_LW = Alignment(horizontal="left", vertical="center", wrap_text=True)
A_LTW = Alignment(horizontal="left", vertical="top", wrap_text=True)
A_CW = Alignment(horizontal="center", vertical="center", wrap_text=True)

LOCKED = Protection(locked=True)
UNLOCKED = Protection(locked=False)

# role -> (font, fill, alignment, border, locked)
_ROLES = {
    "title": (_font(Palette.WHITE, 18, bold=True), _fill(Palette.TITLE), A_L, B_NONE, True),
    "subtitle": (_font(Palette.WHITE, 11), _fill(Palette.TITLE), A_L, B_NONE, True),
    "header": (_font(Palette.WHITE, 12, bold=True), _fill(Palette.HEADER), A_L, B_NONE, True),
    "subheader": (_font(Palette.WHITE, 10, bold=True), _fill(Palette.SUBHEADER), A_L, B_NONE, True),
    "section": (_font(Palette.WHITE, 10, bold=True), _fill(Palette.SECTION), A_L, B_NONE, True),
    "colhdr": (_font(Palette.WHITE, 9, bold=True), _fill(Palette.SUBHEADER), A_C, B_NONE, True),
    "colhdr_r": (_font(Palette.WHITE, 9, bold=True), _fill(Palette.SUBHEADER), A_R, B_NONE, True),
    "label": (_font(Palette.TEXT, SZ), None, A_L, B_NONE, True),
    "label_b": (_font(Palette.TEXT, SZ, bold=True), None, A_L, B_NONE, True),
    "sublabel": (_font(Palette.MUTED, 9, italic=True), None, A_L, B_NONE, True),
    "note": (_font(Palette.MUTED, 8.5), None, A_LW, B_NONE, True),
    "note_l": (_font(Palette.MUTED, 8.5), None, A_L, B_NONE, True),
    # mandated cell types
    "input": (_font(Palette.INPUT_FONT, SZ), _fill(Palette.INPUT_FILL), A_R, B_GRID, False),
    "input_l": (_font(Palette.INPUT_FONT, SZ), _fill(Palette.INPUT_FILL), A_L, B_GRID, False),
    "formula": (_font(Palette.FORMULA_FONT, SZ), _fill(Palette.FORMULA_FILL), A_R, B_GRID, True),
    "formula_l": (_font(Palette.FORMULA_FONT, SZ), _fill(Palette.FORMULA_FILL), A_L, B_GRID, True),
    "output": (_font(Palette.OUTPUT_FONT, SZ, bold=True), _fill(Palette.OUTPUT_FILL), A_R, B_GRID, True),
    "output_l": (_font(Palette.OUTPUT_FONT, SZ, bold=True), _fill(Palette.OUTPUT_FILL), A_L, B_GRID, True),
    "error": (_font(Palette.ERROR_FONT, SZ, bold=True), _fill(Palette.ERROR_FILL), A_C, B_GRID, True),
    # status / classification (CF colours it by value)
    "status": (_font(Palette.TEXT, SZ, bold=True), _fill(Palette.NEUTRAL_FILL), A_C, B_GRID, True),
    "panel": (_font(Palette.TEXT, SZ), _fill(Palette.PANEL), A_L, B_NONE, True),
    "kpi": (_font(Palette.TITLE, 20, bold=True), _fill(Palette.PANEL), A_C, B_BOX, True),
}

_ALIGN = {"l": A_L, "c": A_C, "r": A_R, "lw": A_LW, "ltw": A_LTW, "cw": A_CW}


def apply(cell, role="label", *, fmt=None, bold=None, italic=None, align=None,
          fill=None, font_color=None, size=None, border=None, locked=None):
    base_font, base_fill, base_align, base_border, base_locked = _ROLES.get(role, _ROLES["label"])
    f = base_font
    if any(v is not None for v in (bold, italic, font_color, size)):
        f = Font(name=FONT, size=size if size is not None else f.size,
                 color=font_color if font_color is not None else f.color,
                 bold=bold if bold is not None else f.bold,
                 italic=italic if italic is not None else f.italic)
    cell.font = f
    if fill is not None:
        cell.fill = _fill(fill)
    elif base_fill is not None:
        cell.fill = base_fill
    cell.alignment = _ALIGN.get(align, base_align) if align else base_align
    cell.border = border if border is not None else base_border
    if fmt is not None:
        cell.number_format = fmt
    cell.protection = LOCKED if (base_locked if locked is None else locked) else UNLOCKED
    return cell
