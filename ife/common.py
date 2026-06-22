"""Shared context + drawing/visual helpers for the forecasting engine."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Font, PatternFill
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

from dcf.utils import Refs, col_letter  # noqa: F401  (Refs used as a type)
from .config import (APP_NAME, APP_VERSION, BAD_WORDS, FCST_YEARS, GOOD_WORDS,
                     HIST_YEARS, Palette, WARN_WORDS)

LABEL_COL = 1
FIRST_COL = 2  # first year column


@dataclass
class Context:
    data: dict
    refs: Refs
    sheets: dict = field(default_factory=dict)

    @property
    def hist(self):
        return self.data.get("hist_years", HIST_YEARS)

    @property
    def fcst(self):
        return self.data.get("fcst_years", FCST_YEARS)

    @property
    def hist_periods(self):
        return self.data["periods"]

    @property
    def fcst_periods(self):
        m = re.search(r"(\d{4})", self.hist_periods[-1])
        if m:
            base = int(m.group(1))
            pre = self.hist_periods[-1][:m.start()] or "FY"
            return [f"{pre}{base + i}" for i in range(1, self.fcst + 1)]
        return [f"F{i}" for i in range(1, self.fcst + 1)]

    @property
    def all_periods(self):
        return self.hist_periods + self.fcst_periods

    @property
    def n_all(self):
        return self.hist + self.fcst

    @property
    def last_hist(self):
        return self.hist - 1  # index of last historical year (0-based)

    def hcol(self, i):
        """Column for historical year index i (0..hist-1)."""
        return FIRST_COL + i

    def fcol(self, t):
        """Column for forecast year t (1..fcst); t=0 = last historical (anchor)."""
        return FIRST_COL + self.hist - 1 + t

    def sheet(self, name):
        return self.sheets[name]


# --- drawing ----------------------------------------------------------------
def title_block(sh, title, subtitle, *, last_col, row=1):
    sh.hide_gridlines()
    sh.merge(row, 1, row, last_col)
    sh.put(row, 1, title, role="title")
    sh.row_height(row, 28)
    sh.merge(row + 1, 1, row + 1, last_col)
    sh.put(row + 1, 1, subtitle, role="subtitle")
    sh.merge(row + 2, 1, row + 2, last_col)
    sh.put(row + 2, 1, f"{APP_NAME}  ·  v{APP_VERSION}", role="note")
    return row + 3


def section(sh, row, text, *, c1=1, c2=1, role="header"):
    if c2 > c1:
        sh.merge(row, c1, row, c2)
    sh.put(row, c1, text, role=role)
    sh.row_height(row, 18 if role != "header" else 20)
    return row + 1


def nav_bar(sh, row, *, exclude=None, start_col=1, per_row=10):
    from .config import SHEET_ORDER
    exclude = exclude or set()
    targets = [s for s in SHEET_ORDER if s not in exclude]
    col = start_col
    for i, name in enumerate(targets):
        if i and i % per_row == 0:
            row += 1
            col = start_col
        c = sh.put(row, col, name, role="subheader", align="c")
        c.hyperlink = f"#'{name}'!A1"
        sh.col_width(col, 12)
        col += 1
    return row + 1


def hist_headers(sh, ctx, row, *, label="Item", split=True):
    """Header row spanning historical (+forecast if split) year columns."""
    sh.put(row, LABEL_COL, label, role="colhdr")
    n = ctx.n_all if split else ctx.hist
    labels = ctx.all_periods if split else ctx.hist_periods
    for i in range(n):
        is_fcst = split and i >= ctx.hist
        c = sh.put(row, FIRST_COL + i, labels[i] + ("  (F)" if is_fcst else ""), role="colhdr_r")
        if is_fcst:
            c.font = Font(name="Calibri", size=9, bold=True, italic=True, color="DDDDDD")
    sh.row_height(row, 20)
    return row + 1


def setup_cols(sh, ctx, *, label_w=34, year_w=9, split=True):
    sh.col_width(LABEL_COL, label_w)
    n = ctx.n_all if split else ctx.hist
    for i in range(n):
        sh.col_width(FIRST_COL + i, year_w)


def units_note(ctx):
    m = ctx.data["meta"]
    return (f"All figures in {m.get('currency','USD')} {m.get('units','millions')} "
            "unless stated; (F) = forecast year. Blue = input · Black = formula · "
            "Green = key output · Red = warning.")


# --- named ranges -----------------------------------------------------------
def define_name(sh, name, row, col):
    """Create a workbook-level named range pointing at one cell; return its ref."""
    wb = sh.ws.parent
    coord = f"'{sh.name}'!${col_letter(col)}${row}"
    wb.defined_names[name] = DefinedName(name, attr_text=coord)
    return name


# --- dropdowns --------------------------------------------------------------
def dropdown(sh, row, col, options):
    """Attach a list data-validation (a real Excel dropdown) to a cell."""
    formula = '"' + ",".join(options) + '"'
    dv = DataValidation(type="list", formula1=formula, allow_blank=False, showErrorMessage=True)
    sh.ws.add_data_validation(dv)
    dv.add(sh.ws.cell(row=row, column=col))


# --- status colouring -------------------------------------------------------
def traffic_light(sh, cell_range, anchor):
    def rule(words):
        return ["OR(" + ",".join(f'ISNUMBER(SEARCH("{w}",{anchor}))' for w in words) + ")"]
    for words, fc, fl in ((GOOD_WORDS, Palette.GOOD, Palette.GOOD_FILL),
                          (WARN_WORDS, Palette.WARN, Palette.WARN_FILL),
                          (BAD_WORDS, Palette.BAD, Palette.BAD_FILL)):
        sh.ws.conditional_formatting.add(
            cell_range, FormulaRule(formula=rule(words), stopIfTrue=True,
                                    font=Font(name="Calibri", size=10, bold=True, color=fc),
                                    fill=PatternFill(start_color=fl, end_color=fl, fill_type="solid")))


# --- charts -----------------------------------------------------------------
def line_chart(sh, anchor, title, *, rows, cat_row, first_col, last_col, width=22, height=8):
    ws = sh.ws
    ch = LineChart()
    ch.title = title
    ch.height = height
    ch.width = width
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    data = Reference(ws, min_col=LABEL_COL, max_col=last_col, min_row=rows[0], max_row=rows[-1])
    ch.add_data(data, from_rows=True, titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=first_col, max_col=last_col, min_row=cat_row, max_row=cat_row))
    ws.add_chart(ch, anchor)


def bar_chart(sh, anchor, title, *, rows, cat_row, first_col, last_col, width=22, height=8):
    ws = sh.ws
    ch = BarChart()
    ch.type = "col"
    ch.title = title
    ch.height = height
    ch.width = width
    data = Reference(ws, min_col=LABEL_COL, max_col=last_col, min_row=rows[0], max_row=rows[-1])
    ch.add_data(data, from_rows=True, titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=first_col, max_col=last_col, min_row=cat_row, max_row=cat_row))
    ws.add_chart(ch, anchor)
