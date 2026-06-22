"""
Workbook plumbing: a cross-sheet cell reference registry, a thin worksheet
wrapper, and a library of *defensive* Excel-formula builders.

Why this exists
---------------
Every headline number in the model is a live Excel formula that points back at
input cells -- not a value baked in by Python. To wire formulas across a dozen
sheets without hand-maintaining hundreds of ``'Sheet'!$C$12`` strings, sheets
*register* the cells they create under stable logical keys (e.g.
``"is.revenue@2024"``) and *reference* them later by key. The registry resolves
keys to absolute, sheet-qualified references.

The formula builders wrap raw arithmetic in guards (``ISNUMBER``, zero-checks,
``IFERROR``) so the workbook degrades to ``"n/m"`` / ``"n/a"`` instead of
spraying ``#DIV/0!`` / ``#VALUE!`` when data is missing or a base is non-positive.
"""

from __future__ import annotations

from openpyxl.utils import get_column_letter

from . import styles
from .config import NA_TEXT, NM_TEXT


# ===========================================================================
# Cross-sheet reference registry
# ===========================================================================
class Refs:
    """Maps logical keys to absolute, sheet-qualified cell references.

    A key is any stable string. Convention used in this project:
        "<area>.<metric>"            for scalars (e.g. "wacc.value")
        "<area>.<metric>@<period>"   for time series (e.g. "fc.revenue@1")
    """

    def __init__(self) -> None:
        self._map: dict[str, tuple[str, str]] = {}

    def put(self, key: str, sheet: str, coord: str) -> None:
        if key in self._map:
            raise KeyError(f"duplicate ref key registered: {key!r}")
        self._map[key] = (sheet, coord)

    def has(self, key: str) -> bool:
        return key in self._map

    def coord(self, key: str) -> str:
        """Bare coordinate, e.g. 'C12' (no sheet, no '$')."""
        return self._map[key][1]

    def ref(self, key: str) -> str:
        """Absolute sheet-qualified reference, e.g. "'Inputs'!$C$12"."""
        sheet, coord = self._map[key]
        col = "".join(ch for ch in coord if ch.isalpha())
        row = "".join(ch for ch in coord if ch.isdigit())
        return f"'{sheet}'!${col}${row}"

    def ref_or(self, key: str, fallback: str) -> str:
        """Reference if known, else a literal fallback (e.g. '0' or '\"n/a\"')."""
        return self.ref(key) if key in self._map else fallback

    def range(self, key1: str, key2: str) -> str:
        """Sheet-qualified range between two same-sheet keys, e.g. "'H'!$D$5:$F$5"."""
        s1, c1 = self._map[key1]
        s2, c2 = self._map[key2]
        if s1 != s2:
            raise ValueError(f"range across sheets: {key1} / {key2}")
        col1 = "".join(ch for ch in c1 if ch.isalpha())
        row1 = "".join(ch for ch in c1 if ch.isdigit())
        col2 = "".join(ch for ch in c2 if ch.isalpha())
        row2 = "".join(ch for ch in c2 if ch.isdigit())
        return f"'{s1}'!${col1}${row1}:${col2}${row2}"


# ===========================================================================
# Period model
# ===========================================================================
class Period:
    """A single column period in the model (historical or forecast)."""

    def __init__(self, label: str, idx: int, kind: str):
        self.label = label      # e.g. "FY2024"
        self.idx = idx          # 0-based position within its kind
        self.kind = kind        # "hist" | "fcst" | "terminal"

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Period({self.label!r}, {self.idx}, {self.kind})"


# ===========================================================================
# Thin worksheet wrapper
# ===========================================================================
class Sheet:
    """Convenience wrapper around an openpyxl worksheet.

    Adds styled writes and automatic registry registration so a sheet can both
    place a value *and* expose it to other sheets in one call.
    """

    def __init__(self, ws, refs: Refs, styler=None):
        self.ws = ws
        self.refs = refs
        self.name = ws.title
        # which style module's apply() to use; defaults to the DCF palette.
        self._apply = styler or styles.apply

    # -- core write ---------------------------------------------------------
    def put(self, row, col, value=None, role="body", fmt=None, key=None, **style):
        """Write *value* at (row, col) with a style role; optionally register it.

        ``col`` may be an int (1-based) or a column letter. If ``value`` is a
        string beginning with ``=`` openpyxl stores it as a formula.
        """
        c = self.ws.cell(row=row, column=_col_idx(col))
        if value is not None:
            c.value = value
        self._apply(c, role, fmt=fmt, **style)
        if key is not None:
            self.refs.put(key, self.name, c.coordinate)
        return c

    def label(self, row, col, text, role="label", **style):
        return self.put(row, col, text, role=role, **style)

    def merge(self, r1, c1, r2, c2):
        self.ws.merge_cells(
            start_row=r1, start_column=_col_idx(c1), end_row=r2, end_column=_col_idx(c2)
        )

    def col_width(self, col, width):
        self.ws.column_dimensions[get_column_letter(_col_idx(col))].width = width

    def row_height(self, row, height):
        self.ws.row_dimensions[row].height = height

    def freeze(self, coord):
        self.ws.freeze_panes = coord

    def hide_gridlines(self):
        self.ws.sheet_view.showGridLines = False

    def coord(self, row, col) -> str:
        return f"{get_column_letter(_col_idx(col))}{row}"

    def abs_ref(self, row, col) -> str:
        """Absolute, sheet-qualified reference to a (row,col) on THIS sheet."""
        return f"'{self.name}'!${get_column_letter(_col_idx(col))}${row}"

    def local(self, row, col) -> str:
        """Absolute reference WITHOUT sheet name (same-sheet formulas)."""
        return f"${get_column_letter(_col_idx(col))}${row}"


def _col_idx(col) -> int:
    if isinstance(col, int):
        return col
    # column letter -> index
    idx = 0
    for ch in col.upper():
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx


def col_letter(idx: int) -> str:
    return get_column_letter(idx)


# ===========================================================================
# Defensive formula builders
# Each returns a string beginning with '=' suitable for a formula cell.
# `a`, `b`, ... are reference strings or numeric literals (as str).
# ===========================================================================
def f(expr: str) -> str:
    """Mark a raw expression as a formula."""
    return expr if expr.startswith("=") else "=" + expr


def num(ref: str) -> str:
    """Coerce a possibly-blank/text cell to a number (blank/text -> 0)."""
    return f"N({ref})"


def iferr(expr: str, fallback: str = f'"{NM_TEXT}"') -> str:
    """Wrap an expression so any Excel error degrades to *fallback*."""
    return f"=IFERROR({_body(expr)},{fallback})"


def ratio(a: str, b: str, fallback: str = f'"{NM_TEXT}"') -> str:
    """a / b, guarded against non-numeric inputs and zero/negative denominator-as-error.

    Returns *fallback* when either side is non-numeric or b == 0.
    """
    return (
        f'=IF(AND(ISNUMBER({a}),ISNUMBER({b}),{b}<>0),{a}/{b},{fallback})'
    )


def growth(curr: str, prev: str, fallback: str = f'"{NM_TEXT}"') -> str:
    """Period-over-period growth, only meaningful off a positive base."""
    return (
        f'=IF(AND(ISNUMBER({curr}),ISNUMBER({prev}),{prev}>0),{curr}/{prev}-1,{fallback})'
    )


def cagr(end: str, start: str, periods: str, fallback: str = f'"{NM_TEXT}"') -> str:
    """Compound annual growth rate over *periods* years (positive endpoints only)."""
    return (
        f'=IF(AND(ISNUMBER({end}),ISNUMBER({start}),{start}>0,{end}>0,{periods}>0),'
        f'({end}/{start})^(1/{periods})-1,{fallback})'
    )


def pct_of(part: str, whole: str, fallback: str = f'"{NM_TEXT}"') -> str:
    """part / whole expressed as a percentage of a base (guarded)."""
    return ratio(part, whole, fallback)


def safe_sum(refs: list[str]) -> str:
    """Sum that treats blanks/text as zero (uses N() coercion via SUM of refs).

    SUM already ignores text/blanks, so a plain SUM is the defensive choice.
    """
    return "=SUM(" + ",".join(refs) + ")"


def avg_of(refs: list[str], fallback: str = f'"{NA_TEXT}"') -> str:
    """Average of numeric cells only; *fallback* if none are numeric."""
    inner = ",".join(refs)
    return f'=IFERROR(AVERAGE({inner}),{fallback})'


def choose(index_ref: str, options: list[str]) -> str:
    """Excel CHOOSE: pick option by 1-based index (used by scenario switch)."""
    return "=CHOOSE(" + index_ref + "," + ",".join(_body(o) for o in options) + ")"


def minus(a: str, b: str) -> str:
    return f"={_body(a)}-{_body(b)}"


def _body(expr: str) -> str:
    """Strip a leading '=' so an expression can be embedded inside another."""
    return expr[1:] if expr.startswith("=") else expr


def expr(*parts: str) -> str:
    """Concatenate body fragments into a formula (caller supplies operators)."""
    return "=" + "".join(_body(p) if p.startswith("=") else p for p in parts)


# ===========================================================================
# Plain-English interpretation label formulas (Excel-side, so they live-update)
# ===========================================================================
def label_trend(latest: str, avg: str, band: float,
                up="Improving", flat="Stable", down="Deteriorating",
                higher_is_better: bool = True) -> str:
    """Compare *latest* to trailing *avg* with a +/- relative *band*.

    If ``higher_is_better`` is False, the up/down labels swap so that the label
    reflects desirability, not raw direction.
    """
    hi, lo = (up, down) if higher_is_better else (down, up)
    return (
        f'=IF(NOT(AND(ISNUMBER({latest}),ISNUMBER({avg}))),"{NA_TEXT}",'
        f'IF({latest}>{avg}*(1+{band}),"{hi}",'
        f'IF({latest}<{avg}*(1-{band}),"{lo}","{flat}")))'
    )


def label_growth(latest: str, prior: str, band_pp: float,
                 up="Accelerating", flat="Stable", down="Decelerating") -> str:
    """Label change in a growth *rate* (pp) vs the prior period's rate."""
    return (
        f'=IF(NOT(AND(ISNUMBER({latest}),ISNUMBER({prior}))),"{NA_TEXT}",'
        f'IF({latest}>{prior}+{band_pp},"{up}",'
        f'IF({latest}<{prior}-{band_pp},"{down}","{flat}")))'
    )


def label_bands(value: str, bands: list[tuple[float, str]], above_last: str) -> str:
    """Threshold ladder. *bands* = ascending [(upper_bound, label), ...].

    Returns the label of the first band whose ``upper_bound`` the value is below;
    otherwise *above_last*. Non-numeric -> "n/a".
    """
    inner = f'"{above_last}"'
    for bound, lab in reversed(bands):
        inner = f'IF({value}<{bound},"{lab}",{inner})'
    return f'=IF(NOT(ISNUMBER({value})),"{NA_TEXT}",{inner})'


def label_compare(a: str, b: str, gap: float,
                  a_gt="Value-creating", eq="Roughly neutral", a_lt="Value-destroying") -> str:
    """Compare two numeric refs with a tolerance *gap* (e.g. ROIC vs WACC)."""
    return (
        f'=IF(NOT(AND(ISNUMBER({a}),ISNUMBER({b}))),"{NA_TEXT}",'
        f'IF({a}>{b}+{gap},"{a_gt}",'
        f'IF({a}<{b}-{gap},"{a_lt}","{eq}")))'
    )


def label_valuation(implied: str, current: str, band: float,
                    under="Undervalued", fair="Fairly valued", over="Overvalued") -> str:
    """Implied value vs current price/market with a +/- band -> valuation label."""
    return (
        f'=IF(NOT(AND(ISNUMBER({implied}),ISNUMBER({current}),{current}>0)),"{NA_TEXT}",'
        f'IF({implied}>{current}*(1+{band}),"{under}",'
        f'IF({implied}<{current}*(1-{band}),"{over}","{fair}")))'
    )
