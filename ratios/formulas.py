"""
Simple, auditable Excel-formula builders for the ratio workbook.

Design rule (from the brief): keep every formula short and readable. Ratios are a
single guarded division; classifications use a CHOOSE() over boolean arithmetic
instead of nested IFs:

    index = 1 + (v>=lo) + (v>=hi)        -> 1, 2 or 3
    label = CHOOSE(index, low, mid, high)

All builders return a string beginning with '='. Intermediate steps (averages,
totals, etc.) are written as their own helper rows by the sheets, so a ratio
formula only ever references already-computed cells.
"""

from __future__ import annotations


def div(a: str, b: str) -> str:
    """Guarded division: blank instead of #DIV/0!."""
    return f'=IFERROR({a}/{b},"")'


def diff(a: str, b: str) -> str:
    return f"={a}-{b}"


def add(*refs: str) -> str:
    return "=" + "+".join(refs)


def avg2(prior: str, curr: str) -> str:
    """Two-point average (e.g. average balance) = (prior + current) / 2."""
    return f"=({prior}+{curr})/2"


def summ(refs: list[str]) -> str:
    return "=SUM(" + ",".join(refs) + ")"


def growth(curr: str, prev: str) -> str:
    """Period-over-period growth, blank if the base is non-positive/non-numeric."""
    return f'=IFERROR({curr}/{prev}-1,"")'


def cagr(end: str, start: str, years: int) -> str:
    return f'=IFERROR(({end}/{start})^(1/{years})-1,"")'


def bps(curr: str, prev: str) -> str:
    """Change in a rate expressed in basis points."""
    return f"=({curr}-{prev})*10000"


def product(a: str, b: str) -> str:
    return f"={a}*{b}"


def mult3(a: str, b: str, c: str) -> str:
    return f"={a}*{b}*{c}"


# --- single-formula classifiers (no nested IF) -----------------------------
def classify_bands(v: str, lo: float, hi: float, labels: tuple[str, str, str]) -> str:
    """Three-band classification via CHOOSE over boolean arithmetic."""
    return (f'=IF(ISNUMBER({v}),CHOOSE(1+({v}>={lo})+({v}>={hi}),'
            f'"{labels[0]}","{labels[1]}","{labels[2]}"),"")')


def classify_trend(latest: str, avg: str, band: float,
                   labels=("Deteriorating", "Stable", "Improving")) -> str:
    """Compare latest vs trailing average with a +/- band."""
    return (f'=IF(AND(ISNUMBER({latest}),ISNUMBER({avg})),'
            f'CHOOSE(2+({latest}>{avg}*(1+{band}))-({latest}<{avg}*(1-{band})),'
            f'"{labels[0]}","{labels[1]}","{labels[2]}"),"")')


def arrow(latest: str, prior: str) -> str:
    """Up/flat/down arrow glyph comparing two cells."""
    return (f'=IF(AND(ISNUMBER({latest}),ISNUMBER({prior})),'
            f'CHOOSE(2+({latest}>{prior})-({latest}<{prior}),'
            f'"▼","►","▲"),"")')


def bar(v: str, scale: str, maxchars: int = 10) -> str:
    """Text data-bar (sparkline-style) = REPT of block chars scaled to a max."""
    return f'=IFERROR(REPT("█",MIN({maxchars},ROUND({v}/{scale}*{maxchars},0))),"")'


def link(ref: str) -> str:
    return f"={ref}"


# --- commentary helpers (formula-driven sentences) -------------------------
def text(ref: str, fmt: str) -> str:
    """Bare TEXT(ref, fmt) fragment for embedding in concatenations."""
    return f'TEXT({ref},"{fmt}")'


def sentence(*parts: str) -> str:
    """Join concatenation fragments into one formula (blank-safe via IFERROR)."""
    return '=IFERROR(' + "&".join(parts) + ',"(insufficient data — populate inputs)")'


def q(s: str) -> str:
    """Quote a literal string fragment for use inside sentence()."""
    return '"' + s.replace('"', '""') + '"'


def dirword(latest: str, base: str, words=("decreased", "was unchanged", "increased")) -> str:
    """A direction word chosen by comparing two cells (fragment, no leading '=')."""
    return (f'CHOOSE(2+({latest}>{base})-({latest}<{base}),'
            f'"{words[0]}","{words[1]}","{words[2]}")')


def pick(cond: str, yes: str, no: str) -> str:
    """Single IF fragment for a binary word choice (no leading '=')."""
    return f'IF({cond},{yes},{no})'
