"""
Grid -- a reusable renderer for ratio sheets.

Keeps every ratio sheet consistent and terse: a ratio row writes one short output
formula per year (green), a trend arrow, a traffic-light classification and a
per-row heat-map; helper rows (blue) hold intermediate steps; commentary rows
hold formula-driven sentences. Charts and the traffic-light colouring are applied
at the end via finalize().
"""

from __future__ import annotations

from dcf.config import Fmt
from dcf.utils import col_letter
from . import common, formulas
from .config import BANDS, TREND_BAND


class Grid:
    def __init__(self, sh, ctx: common.Context, prefix: str):
        self.sh = sh
        self.ctx = ctx
        self.prefix = prefix
        self.r = 1
        self.last = ctx.last_year_col          # last year column index
        self.x_trend = self.last + 1
        self.x_read = self.last + 2
        self._reads = []                       # (row, col) of classification cells
        self._li = ctx.last_hist_idx

    # -- references --
    def R(self, key, i):
        return self.ctx.refs.ref(f"in.{key}@{i}")

    def S(self, key, i):
        return self.ctx.refs.ref(f"{self.prefix}.{key}@{i}")

    # -- structure --
    def title(self, title, subtitle):
        common.title_block(self.sh, title, subtitle, last_col=self.x_read)
        common.nav_bar(self.sh, 5, exclude={"Home"})
        self.r = 7
        self.sh.put(self.r, 1, common.units_note(self.ctx), role="note")
        self.sh.merge(self.r, 1, self.r, self.x_read)
        self.r += 1

    def yearhead(self, label="Ratio"):
        self.r = common.year_headers(self.sh, self.ctx, self.r, label=label,
                                     extra=["Trend", "Assessment"])
        self.sh.freeze(f"B{self.r}")
        # column widths
        self.sh.col_width(1, 34)
        for i in range(self.ctx.n_years):
            self.sh.col_width(self.ctx.year_col(i), 9)
        self.sh.col_width(self.x_trend, 7)
        self.sh.col_width(self.x_read, 15)

    def section(self, text):
        self.r = common.section(self.sh, self.r, text, c1=1, c2=self.x_read)

    def blank(self, n=1):
        self.r += n

    # -- rows --
    def helper(self, key, label, builder, fmt=Fmt.MONEY, start=0):
        sh = self.sh
        sh.put(self.r, 1, "  " + label, role="sublabel")
        for i in range(self.ctx.n_years):
            if i < start:
                sh.put(self.r, self.ctx.year_col(i), None, role="formula", fmt=fmt,
                       key=f"{self.prefix}.{key}@{i}")
            else:
                sh.put(self.r, self.ctx.year_col(i), builder(i), role="formula", fmt=fmt,
                       key=f"{self.prefix}.{key}@{i}")
        self.r += 1
        return self.r - 1

    def ratio(self, key, label, builder, fmt=Fmt.PCT, classify=None, *, arrow=True,
              heat=True, reverse=False, total=False, start=0):
        sh, ctx = self.sh, self.ctx
        r = self.r
        sh.put(r, 1, label, role="label_b" if total else "label")
        for i in range(ctx.n_years):
            if i < start:
                sh.put(r, ctx.year_col(i), None, role="output", fmt=fmt, key=f"{self.prefix}.{key}@{i}")
            else:
                sh.put(r, ctx.year_col(i), builder(i), role="output", fmt=fmt, key=f"{self.prefix}.{key}@{i}")
        latest = sh.local(r, ctx.year_col(self._li))
        prior = sh.local(r, ctx.year_col(self._li - 1))
        if arrow:
            sh.put(r, self.x_trend, formulas.arrow(latest, prior), role="status")
        if classify is not None:
            sh.put(r, self.x_read, self._classify(classify, r, latest), role="status",
                   key=f"{self.prefix}.{key}.read")
            self._reads.append((r, self.x_read))
        if heat:
            rng = f"{sh.coord(r, ctx.year_col(0))}:{sh.coord(r, ctx.last_year_col)}"
            common.heat_map(sh, rng, reverse=reverse)
        self.r += 1
        return r

    def commentary(self, formula):
        sh = self.sh
        sh.put(self.r, 1, formula, role="panel", align="lw")
        sh.merge(self.r, 1, self.r, self.x_read)
        sh.row_height(self.r, 20)
        self.r += 1

    def note(self, text):
        sh = self.sh
        sh.put(self.r, 1, text, role="note", align="lw")
        sh.merge(self.r, 1, self.r, self.x_read)
        self.r += 1

    # -- classification formula --
    def _classify(self, classify, row, latest):
        kind = classify[0]
        if kind == "bands":
            lo, hi, labels = BANDS[classify[1]]
            return formulas.classify_bands(latest, lo, hi, labels)
        if kind == "bandc":
            _, lo, hi, labels = classify
            return formulas.classify_bands(latest, lo, hi, labels)
        if kind == "trend":
            sh, ctx = self.sh, self.ctx
            avg = f"AVERAGE({sh.local(row, ctx.year_col(0))}:{sh.local(row, ctx.year_col(self._li))})"
            labels = classify[1] if len(classify) > 1 else ("Deteriorating", "Stable", "Improving")
            return formulas.classify_trend(latest, avg, TREND_BAND, labels)
        return '=""'

    # -- charts & finalize --
    def chart(self, anchor_row, title, first_row, last_row, *, cat_row=None, kind="line",
              width=22, height=8):
        anchor = f"{col_letter(self.x_read + 2)}{anchor_row}"
        cat_row = cat_row or self._yearhead_row()
        rows = [first_row, last_row]
        if kind == "line":
            common.line_chart(self.sh, anchor, title, rows=rows, cat_row=cat_row,
                              first_col=common.FIRST_YEAR_COL, last_col=self.last,
                              width=width, height=height)
        elif kind == "bar":
            common.bar_chart(self.sh, anchor, title, rows=rows, cat_row=cat_row,
                             first_col=common.FIRST_YEAR_COL, last_col=self.last,
                             width=width, height=height)

    def _yearhead_row(self):
        return 8  # year header sits at row 8 (title 1-3, nav 5, units 7, head 8)

    def finalize(self):
        if self._reads:
            rows = [r for r, _ in self._reads]
            col = self._reads[0][1]
            rng = f"{self.sh.coord(min(rows), col)}:{self.sh.coord(max(rows), col)}"
            common.traffic_light(self.sh, rng, self.sh.coord(min(rows), col))
