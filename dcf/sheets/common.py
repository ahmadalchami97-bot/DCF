"""
Shared sheet-building utilities: the build :class:`Context` passed to every
sheet, plus drawing helpers (title bands, section headers, period headers,
legend) so all sheets share one visual grammar.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..config import (DATA_COL_WIDTH, Defaults, LABEL_COL_WIDTH, NOTE_COL_WIDTH,
                      Palette, ROW_H_HEADER, ROW_H_TITLE, SCENARIOS, APP_NAME, APP_VERSION)
from ..styles import BORDER_BOTTOM_RULE
from ..utils import Refs, Sheet


@dataclass
class Context:
    data: dict
    refs: Refs
    sheets: dict = field(default_factory=dict)   # name -> Sheet wrapper
    n_fcst: int = Defaults.FORECAST_YEARS

    @property
    def periods(self) -> list[str]:
        return self.data["periods"]

    @property
    def n_hist(self) -> int:
        return len(self.data["periods"])

    @property
    def last_hist_label(self) -> str:
        return self.data["periods"][-1]

    @property
    def fcst_labels(self) -> list[str]:
        """Forecast year labels, continuing the historical numbering if possible."""
        m = re.search(r"(\d{4})", self.last_hist_label)
        if m:
            base = int(m.group(1))
            prefix = self.last_hist_label[: m.start()] or "FY"
            return [f"{prefix}{base + i}" for i in range(1, self.n_fcst + 1)]
        return [f"Year +{i}" for i in range(1, self.n_fcst + 1)]

    @property
    def scenarios(self) -> list[str]:
        return list(SCENARIOS)

    def sheet(self, name: str) -> Sheet:
        return self.sheets[name]


# --- drawing helpers --------------------------------------------------------
def title_block(sh: Sheet, title: str, subtitle: str, *, last_col: int, row: int = 1):
    """Big title band spanning columns 1..last_col with a subtitle line beneath."""
    sh.merge(row, 1, row, last_col)
    sh.put(row, 1, title, role="title")
    sh.row_height(row, ROW_H_TITLE)
    sh.merge(row + 1, 1, row + 1, last_col)
    sh.put(row + 1, 1, subtitle, role="subtitle")
    sh.row_height(row + 1, 16)
    # thin breadcrumb line
    sh.merge(row + 2, 1, row + 2, last_col)
    sh.put(row + 2, 1, f"{APP_NAME}  ·  v{APP_VERSION}", role="note")
    return row + 3  # next free row


def section(sh: Sheet, row: int, text: str, *, c1: int = 1, c2: int = 1, role: str = "header"):
    """A coloured section band from column c1..c2."""
    if c2 > c1:
        sh.merge(row, c1, row, c2)
    sh.put(row, c1, text, role=role)
    sh.row_height(row, ROW_H_HEADER)
    return row + 1


def subsection(sh: Sheet, row: int, text: str, *, c1: int = 1, c2: int = 1):
    return section(sh, row, text, c1=c1, c2=c2, role="subheader")


def period_headers(sh: Sheet, row: int, *, label_col: int, first_data_col: int,
                   labels: list[str], label_text: str = "", note_col: int | None = None,
                   note_text: str = "Interpretation / notes"):
    """Write a period-header row: a label column then one column per period."""
    sh.put(row, label_col, label_text, role="colhdr")
    for i, lab in enumerate(labels):
        sh.put(row, first_data_col + i, lab, role="colhdr_r")
    if note_col is not None:
        sh.put(row, note_col, note_text, role="colhdr")
    sh.row_height(row, ROW_H_HEADER)
    return row + 1


def setup_grid(sh: Sheet, *, n_data_cols: int, label_col: int = 1, first_data_col: int = 2,
               note_col: int | None = None, label_width: float = LABEL_COL_WIDTH,
               data_width: float = DATA_COL_WIDTH, note_width: float = NOTE_COL_WIDTH):
    """Apply standard column widths and hide gridlines for a clean look."""
    sh.hide_gridlines()
    sh.col_width(label_col, label_width)
    for i in range(n_data_cols):
        sh.col_width(first_data_col + i, data_width)
    if note_col is not None:
        sh.col_width(note_col, note_width)


def legend_block(sh: Sheet, row: int, col: int = 1):
    """A compact legend explaining the cell-type colour coding."""
    sh.put(row, col, "LEGEND", role="label_b")
    r = row + 1
    samples = [
        ("input_l", "1,234", "Input — type your data here (yellow fill, blue font)"),
        ("calc", "a / b", "Calculated on this sheet (black formula)"),
        ("link", "→ link", "Linked from another sheet (green font)"),
        ("output", "12.3x", "Key output (shaded)"),
    ]
    for role, sample, desc in samples:
        sh.put(r, col, sample, role=role)
        sh.put(r, col + 1, desc, role="note")
        sh.merge(r, col + 1, r, col + 4)
        r += 1
    # status colours on one line
    sh.put(r, col, "Strong", role="good")
    sh.put(r, col + 1, "Caution", role="warn")
    sh.put(r, col + 2, "Weak / flag", role="bad")
    sh.put(r, col + 3, "n/a = data missing · n/m = not meaningful", role="note")
    sh.merge(r, col + 3, r, col + 6)
    return r + 1


def money_units_note(ctx: Context) -> str:
    m = ctx.data["meta"]
    return f"All figures in {m.get('currency','USD')} {m.get('units','millions')} unless stated."


def thin_rule(sh: Sheet, row: int, c1: int, c2: int):
    for c in range(c1, c2 + 1):
        cell = sh.ws.cell(row=row, column=c)
        cell.border = BORDER_BOTTOM_RULE


# --- dynamic colouring of plain-English interpretation labels ---------------
# A sentiment-consistent vocabulary so a keyword search can colour reliably.
GOOD_WORDS = ["Strong", "Improving", "Expanding", "Accelerating", "Conservative",
              "Undervalued", "Value-creating", "Robust", "Healthy", "Low risk",
              "PASS", "Balanced", "Ties", "Acyclic", "Present", "Consistent", "Positive"]
BAD_WORDS = ["Weak", "Deteriorating", "Compressing", "Elevated", "Stretched",
             "Overvalued", "Value-destroying", "Severe", "High risk", "Negative",
             "Breach", "FAIL", "Imbalanced", "Outlier", "Missing"]
WARN_WORDS = ["Moderate", "Caution", "Decelerating", "Watch", "Partial", "Thin",
              "REVIEW", "TV-heavy", "Outside"]


def add_label_coloring(sh: Sheet, cell_range: str, anchor: str):
    """Conditionally colour interpretation labels in *cell_range*.

    Excel evaluates the rule formula relative to *anchor* (the range's top-left
    cell) and shifts it per row, so a single rule colours the whole column.
    """
    from openpyxl.formatting.rule import FormulaRule
    from openpyxl.styles import Font, PatternFill

    def _search(words):
        terms = ",".join(f'ISNUMBER(SEARCH("{w}",{anchor}))' for w in words)
        return [f"OR({terms})"]

    rules = [
        (_search(GOOD_WORDS), Palette.GOOD, Palette.GOOD_FILL),
        (_search(BAD_WORDS), Palette.BAD, Palette.BAD_FILL),
        (_search(WARN_WORDS), Palette.WARN, Palette.WARN_FILL),
    ]
    for formula, font_color, fill_color in rules:
        sh.ws.conditional_formatting.add(
            cell_range,
            FormulaRule(formula=formula, stopIfTrue=True,
                        font=Font(name="Calibri", size=9, bold=True, color=font_color),
                        fill=PatternFill(start_color=fill_color, end_color=fill_color,
                                         fill_type="solid")),
        )
