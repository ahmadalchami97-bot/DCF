"""Simple, auditable Excel-formula builders for the forecasting engine."""

from __future__ import annotations


def div(a, b):
    return f'=IFERROR({a}/{b},"")'


def diff(a, b):
    return f"={a}-{b}"


def add(*refs):
    return "=" + "+".join(refs)


def summ(refs):
    return "=SUM(" + ",".join(refs) + ")"


def product(a, b):
    return f"={a}*{b}"


def growth(curr, prev):
    return f'=IFERROR({curr}/{prev}-1,"")'


def cagr(end, start, years):
    return f'=IFERROR(({end}/{start})^(1/{years})-1,"")'


def avg2(a, b):
    return f"=({a}+{b})/2"


def link(ref):
    return f"={ref}"


def classify_bands(v, lo, hi, labels):
    """Three-band label via CHOOSE over boolean arithmetic (no nested IF)."""
    return (f'=IF(ISNUMBER({v}),CHOOSE(1+({v}>={lo})+({v}>={hi}),'
            f'"{labels[0]}","{labels[1]}","{labels[2]}"),"")')


def flag(cond_expr, ok="PASS", bad="FAIL"):
    """Single IF returning a PASS/FAIL token from a boolean expression."""
    return f'=IF({cond_expr},"{ok}","{bad}")'


def warn_band(v, lo, hi, ok="OK", bad="WARN"):
    """OK if lo <= v <= hi else WARN (single formula)."""
    return f'=IF(AND(ISNUMBER({v}),{v}>={lo},{v}<={hi}),"{ok}","{bad}")'


def text(ref, fmt):
    return f'TEXT({ref},"{fmt}")'


def pick(cond, yes, no):
    return f'IF({cond},{yes},{no})'


def q(s):
    return '"' + s.replace('"', '""') + '"'


def sentence(*parts):
    return '=IFERROR(' + "&".join(parts) + ',"(insufficient data)")'
