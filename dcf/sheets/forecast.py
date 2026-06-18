"""
Forecast sheet -- the projection engine (active scenario).

Builds the operating forecast and unlevered free cash flow year by year, with
every intermediate step visible (no compressed mega-formulas):

  revenue growth fades linearly from the year-1 rate to the terminal rate;
  revenue compounds off the last actual; EBIT margin fades from the last actual
  to the terminal target; D&A, capex and ΔWC are driven by revenue intensity.

  Unlevered FCF (FCFF) = NOPAT + D&A − Capex − Increase in NWC

The first data column anchors on the last reported year so the hand-off from
actuals to forecast is explicit. Everything is registered under ``fc.<line>@<t>``
(t = 0 anchor, 1..N forecast) for the DCF, Sensitivity and Scenario sheets.
"""

from __future__ import annotations

from ..config import Fmt
from . import common

L = 1          # label column
ANCHOR = 2     # last-actual anchor column
FC0 = 3        # first forecast column


def build(sh, ctx: common.Context):
    refs = ctx.refs
    N = ctx.n_fcst
    last = ctx.n_hist - 1
    note_col = FC0 + N
    R = lambda k, p: refs.ref(f"in.{k}@{p}")     # noqa: E731
    H = lambda k, p: refs.ref(f"h.{k}@{p}")      # noqa: E731
    A = lambda k: refs.ref(f"as.{k}")            # noqa: E731
    F = lambda k, t: refs.ref(f"fc.{k}@{t}")     # noqa: E731

    sh.hide_gridlines()
    sh.col_width(L, 40)
    sh.col_width(ANCHOR, 13)
    for i in range(N):
        sh.col_width(FC0 + i, 13)
    sh.col_width(note_col, 50)

    r = common.title_block(sh, "FORECAST",
                           "Driver-based operating forecast & unlevered free cash flow",
                           last_col=note_col)
    sh.put(r, L, "Active scenario:", role="label")
    sh.put(r, ANCHOR, f"={refs.ref('as.scenario_name')}", role="link", align="l")
    sh.put(r, note_col, common.money_units_note(ctx), role="note")
    r += 2

    # header row
    sh.put(r, L, "Forecast line item", role="colhdr")
    sh.put(r, ANCHOR, f'="{ctx.last_hist_label} (base)"', role="colhdr_r")
    for i, lab in enumerate(ctx.fcst_labels):
        sh.put(r, FC0 + i, lab, role="colhdr_r")
    sh.put(r, note_col, "Driver / logic", role="colhdr")
    r += 1

    def frac(t, denom):
        return 0.0 if denom == 0 else t / denom

    # Revenue growth path -------------------------------------------------
    sh.put(r, L, "Revenue growth", role="label")
    for t in range(1, N + 1):
        fr = frac(t - 1, N - 1)
        formula = f"={A('act_start_growth')}+({A('act_tv_growth')}-{A('act_start_growth')})*{fr:.6f}"
        sh.put(r, FC0 + t - 1, formula, role="calc", fmt=Fmt.PCT, key=f"fc.rev_growth@{t}")
    sh.put(r, ANCHOR, f"={H('rev_growth', last)}", role="link", fmt=Fmt.PCT)
    sh.put(r, note_col, "Linear fade from start growth to terminal growth.", role="note")
    r += 1

    # Revenue -------------------------------------------------------------
    sh.put(r, L, "Revenue", role="label_b")
    sh.put(r, ANCHOR, f"={R('revenue', last)}", role="link", fmt=Fmt.MONEY, bold=True,
           key="fc.revenue@0")
    for t in range(1, N + 1):
        prev = F("revenue", t - 1)
        formula = f"={prev}*(1+{F('rev_growth', t)})"
        sh.put(r, FC0 + t - 1, formula, role="calc", fmt=Fmt.MONEY, key=f"fc.revenue@{t}", bold=True)
    sh.put(r, note_col, "Compounds off the last actual by the growth path.", role="note")
    r += 1

    # EBIT margin path ----------------------------------------------------
    sh.put(r, L, "EBIT margin", role="label")
    anchor_margin = f"=IF(ISNUMBER({H('ebit_margin', last)}),{H('ebit_margin', last)},{A('act_target_margin')})"
    sh.put(r, ANCHOR, anchor_margin, role="link", fmt=Fmt.PCT, key="fc.ebit_margin@0")
    for t in range(1, N + 1):
        fr = frac(t, N)
        formula = f"={F('ebit_margin', 0)}+({A('act_target_margin')}-{F('ebit_margin', 0)})*{fr:.6f}"
        sh.put(r, FC0 + t - 1, formula, role="calc", fmt=Fmt.PCT, key=f"fc.ebit_margin@{t}")
    sh.put(r, note_col, "Linear fade from last-actual margin to terminal target.", role="note")
    r += 1

    # EBIT ----------------------------------------------------------------
    r = _line(sh, r, "EBIT (operating profit)", "ebit", N, note_col,
              lambda t: f"={F('revenue', t)}*{F('ebit_margin', t)}",
              anchor=f"={R('ebit', last)}", bold=True, R=R, last=last,
              note="Revenue × EBIT margin.")

    # D&A -----------------------------------------------------------------
    r = _line(sh, r, "(+) Depreciation & amortisation", "da", N, note_col,
              lambda t: f"={F('revenue', t)}*{A('da_pct_used')}",
              anchor=f"={R('da', last)}", R=R, last=last,
              note="Revenue × D&A intensity (historical average).")

    # EBITDA --------------------------------------------------------------
    r = _line(sh, r, "EBITDA", "ebitda", N, note_col,
              lambda t: f"={F('ebit', t)}+{F('da', t)}",
              anchor=f"={R('ebitda', last)}", bold=True, R=R, last=last,
              note="EBIT + D&A.")
    r += 1

    # ---- unlevered FCF build --------------------------------------------
    r = common.section(sh, r, "Unlevered Free Cash Flow", c1=1, c2=note_col)
    sh.put(r, L, "EBIT (operating profit)", role="label")
    for t in range(1, N + 1):
        sh.put(r, FC0 + t - 1, f"={F('ebit', t)}", role="link", fmt=Fmt.MONEY)
    r += 1

    r = _line(sh, r, "(−) Cash tax on EBIT", "tax_on_ebit", N, note_col,
              lambda t: f"=-{F('ebit', t)}*{A('tax')}", R=R, last=last, forecast_only=True,
              note="EBIT × marginal tax rate (unlevered, so no interest tax shield here).")

    r = _line(sh, r, "NOPAT", "nopat", N, note_col,
              lambda t: f"={F('ebit', t)}*(1-{A('tax')})", R=R, last=last, bold=True,
              forecast_only=True, note="Net operating profit after tax = EBIT × (1 − tax).")

    r = _line(sh, r, "(+) Depreciation & amortisation", "da_addback", N, note_col,
              lambda t: f"={F('da', t)}", R=R, last=last, forecast_only=True,
              note="Non-cash; added back.")

    r = _line(sh, r, "(−) Capital expenditure", "capex", N, note_col,
              lambda t: f"=-{F('revenue', t)}*{A('capex_pct_used')}", R=R, last=last,
              forecast_only=True, note="Revenue × capex intensity (historical average).")

    r = _line(sh, r, "(−) Increase in net working capital", "dnwc", N, note_col,
              lambda t: f"=-{A('nwc_pct_used')}*({F('revenue', t)}-{F('revenue', t - 1)})",
              R=R, last=last, forecast_only=True,
              note="WC % × change in revenue; cash use when revenue grows.")

    # FCFF ----------------------------------------------------------------
    sh.put(r, L, "Unlevered free cash flow (FCFF)", role="label_b")
    for t in range(1, N + 1):
        formula = (f"={F('nopat', t)}+{F('da_addback', t)}+{F('capex', t)}+{F('dnwc', t)}")
        sh.put(r, FC0 + t - 1, formula, role="output", fmt=Fmt.MONEY, key=f"fc.fcff@{t}", bold=True)
    sh.put(r, note_col, "NOPAT + D&A − Capex − ΔWC. Discounted on the DCF sheet.", role="note")
    r += 2

    # ---- method note -----------------------------------------------------
    r = common.section(sh, r, "Forecast Method", c1=1, c2=note_col)
    method = (
        f"Revenue method: trend + mean-reversion (growth fades from "
        f"{ctx.last_hist_label} drivers to the long-run rate). If unit volume and "
        f"price are entered on Inputs, a bottom-up volume × price override can be "
        f"used instead. Operating costs, capex, D&A and working capital are tied to "
        f"revenue, so the forecast is driver-based rather than a flat assumption."
    )
    sh.put(r, L, method, role="note", align="ltw")
    sh.merge(r, L, r + 2, note_col)
    sh.freeze("C8")
    return sh


def _line(sh, row, label, key, N, note_col, formula_fn, *, anchor=None, bold=False,
          R=None, last=None, forecast_only=False, note=""):
    """Render one forecast row for t=1..N with an optional anchor cell."""
    sh.put(row, L, label, role="label_b" if bold else "label")
    if anchor is not None:
        sh.put(row, ANCHOR, anchor, role="link", fmt=Fmt.MONEY, bold=bold or None)
    for t in range(1, N + 1):
        sh.put(row, FC0 + t - 1, formula_fn(t),
               role="output" if bold else "calc", fmt=Fmt.MONEY,
               key=f"fc.{key}@{t}", bold=bold or None)
    if note:
        sh.put(row, note_col, note, role="note")
    return row + 1
