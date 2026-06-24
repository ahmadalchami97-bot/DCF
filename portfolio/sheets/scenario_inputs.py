"""
Scenario Inputs.

The single place the user types scenario data: the period, each asset's start/end
price and FX rate, the amount invested, target/min/max weights, the explanatory
market indicators, and a small bond-return calculator. Everything else in the
workbook reads from here.
"""

from __future__ import annotations

from .. import common
from ..common import define_name
from ..config import ASSETS, INDICATORS, Fmts

LAST = 11


def build(sh, ctx):
    refs = ctx.refs
    d = ctx.data
    scen = d["scenario"]

    common.title_block(sh, "SCENARIO INPUTS", "Type your scenario here -- the whole workbook updates from this sheet",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "WHAT THIS SHEET IS FOR:  describe one scenario (e.g. 'Since Fed Rate Decision') and the price/FX moves over it.",
        "WHAT TO INPUT:  the yellow cells -- scenario dates, each asset's start & end price, its FX rate vs your base "
        "currency, how much you have invested, and your target / minimum / maximum weights.",
        "FX RATE MEANING:  the value of 1 unit of the asset's currency in your base currency "
        f"({ctx.base_ccy}).  USD assets use USD/{ctx.base_ccy};  CHF assets use CHF/{ctx.base_ccy}.",
        "DXY and the FX pairs are DRIVERS / context only -- they are NOT portfolio holdings unless you set 'Investable?' to Yes.",
    ], last_col=LAST)
    r = common.legend(sh, r, LAST) + 1

    # ---- scenario meta ----
    r = common.section(sh, r, "Scenario", c1=1, c2=LAST)
    meta = [("Scenario name", "scen_name", scen.get("name"), Fmts.INT, "input_l"),
            ("Start date", "start_date", scen.get("start_date"), None, "input_l"),
            ("End date", "end_date", scen.get("end_date"), None, "input_l"),
            ("Holding period (days)", "holding_days", scen.get("holding_days"), Fmts.INT, "input"),
            ("Base currency", "base_ccy", scen.get("base_currency"), None, "input_l")]
    for label, key, val, fmt, role in meta:
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 3, val, role=role, fmt=fmt, key=f"in.{key}")
        sh.merge(r, 3, r, 5)
        r += 1
    define_name(sh, "BaseCcy", r - 1, 3)
    r += 1

    # ---- asset input table ----
    r = common.section(sh, r, "Portfolio Assets  (investable)", c1=1, c2=LAST)
    hdr = r
    cols = ["Asset", "Ccy", "Start price\n(local)", "End price\n(local)",
            f"Start FX\n(1 ccy = ? {ctx.base_ccy})", f"End FX\n(? {ctx.base_ccy})",
            f"Invested\n({ctx.base_ccy})", "Current\nweight", "Target\nweight", "Min\nweight", "Max\nweight"]
    for c, t in enumerate(cols, start=1):
        sh.put(hdr, c, t, role="colhdr" if c > 1 else "colhdr_l")
    sh.row_height(hdr, 26)
    r += 1
    first = r
    for key, name, ccy in ASSETS:
        a = d["assets"][key]
        sh.put(r, 1, name, role="label")
        sh.put(r, 2, ccy, role="input_c", key=f"in.ccy@{key}")
        sh.put(r, 3, a.get("start_price"), role="input", fmt=Fmts.PRICE, key=f"in.start_price@{key}")
        sh.put(r, 4, a.get("end_price"), role="input", fmt=Fmts.PRICE, key=f"in.end_price@{key}")
        sh.put(r, 5, a.get("start_fx"), role="input", fmt=Fmts.FX, key=f"in.start_fx@{key}")
        sh.put(r, 6, a.get("end_fx"), role="input", fmt=Fmts.FX, key=f"in.end_fx@{key}")
        sh.put(r, 7, a.get("invested"), role="input", fmt=Fmts.MONEY, key=f"in.invested@{key}")
        sh.put(r, 8, None, role="output", fmt=Fmts.PCT, key=f"in.cur_w@{key}")  # filled below
        sh.put(r, 9, a.get("target_w"), role="input", fmt=Fmts.PCT, key=f"in.target_w@{key}")
        sh.put(r, 10, a.get("min_w"), role="input", fmt=Fmts.PCT, key=f"in.min_w@{key}")
        sh.put(r, 11, a.get("max_w"), role="input", fmt=Fmts.PCT, key=f"in.max_w@{key}")
        r += 1
    # total invested + current-weight formulas
    inv_rng = refs.range(f"in.invested@{ctx.keys[0]}", f"in.invested@{ctx.keys[-1]}")
    sh.put(r, 1, "Total", role="total_l")
    for c in (2, 3, 4, 5, 6):
        sh.put(r, c, None, role="total")
    sh.put(r, 7, f"=SUM({inv_rng})", role="total", fmt=Fmts.MONEY, key="in.total_invested")
    define_name(sh, "TotalInvested", r, 7)
    sh.put(r, 8, f"=SUM({refs.range('in.cur_w@'+ctx.keys[0], 'in.cur_w@'+ctx.keys[-1])})",
           role="total", fmt=Fmts.PCT)
    sh.put(r, 9, f"=SUM({refs.range('in.target_w@'+ctx.keys[0], 'in.target_w@'+ctx.keys[-1])})",
           role="total", fmt=Fmts.PCT)
    total_row = r
    for i, key in enumerate(ctx.keys):
        sh.put(first + i, 8, f"=IFERROR({refs.ref(f'in.invested@{key}')}/TotalInvested,0)",
               role="output", fmt=Fmts.PCT)
    sh.put(total_row + 1, 1, "Tip: target weights should sum to 100%. Current weights are computed from the amounts invested.",
           role="note"); sh.merge(total_row + 1, 1, total_row + 1, LAST)
    r = total_row + 3

    # ---- market indicators ----
    r = common.section(sh, r, "Market Indicators  (drivers / context only -- not holdings unless marked investable)",
                       c1=1, c2=LAST)
    ihdr = r
    for c, t in enumerate(["Indicator", "Start", "End", "% change", "Investable?", "What it tells you"], start=1):
        sh.put(ihdr, c, t, role="colhdr" if c > 1 else "colhdr_l")
    sh.merge(ihdr, 6, ihdr, LAST)
    r += 1
    for key, name, note in INDICATORS:
        ind = d["indicators"][key]
        sh.put(r, 1, name, role="label")
        sh.put(r, 2, ind.get("start"), role="input", fmt=Fmts.FX, key=f"in.ind_start@{key}")
        sh.put(r, 3, ind.get("end"), role="input", fmt=Fmts.FX, key=f"in.ind_end@{key}")
        sh.put(r, 4, f"=IFERROR({refs.ref(f'in.ind_end@{key}')}/{refs.ref(f'in.ind_start@{key}')}-1,\"\")",
               role="formula", fmt=Fmts.PCT)
        sh.put(r, 5, "No", role="input_c", key=f"in.investable@{key}")
        common.dropdown(sh, r, 5, ["No", "Yes"])
        sh.put(r, 6, note, role="note_l")
        sh.merge(r, 6, r, LAST)
        r += 1
    r += 1

    # ---- bond scenario calculator ----
    r = common.section(sh, r, "Bond Scenario Calculator  (US Government Bonds)", c1=1, c2=LAST)
    r = common.explain_box(sh, r, [
        "Bonds earn a coupon as well as moving in price, so we add the coupon to the price change.",
        "Bond return = (End price - Start price + Coupon earned) / Start price.   "
        "Coupon earned = Face x Coupon rate x (Holding days / 365).",
        "This bond Total return feeds the 'US Government Bonds' local return on the Scenario Output sheet.",
    ], last_col=LAST, title="How the bond return works")
    b = d["bond"]
    binputs = [("Starting bond price", "start_price", b.get("start_price"), Fmts.PRICE),
               ("Ending bond price", "end_price", b.get("end_price"), Fmts.PRICE),
               ("Face value", "face", b.get("face"), Fmts.PRICE),
               ("Coupon rate (annual)", "coupon_rate", b.get("coupon_rate"), Fmts.PCT),
               ("Holding period (days)", "holding_days", b.get("holding_days"), Fmts.INT),
               ("Coupon frequency (per year)", "frequency", b.get("frequency"), Fmts.INT)]
    for label, key, val, fmt in binputs:
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 3, val, role="input", fmt=fmt, key=f"bond.{key}")
        r += 1
    B = lambda k: refs.ref(f"bond.{k}")  # noqa: E731

    def bond_out(label, key, formula, fmt, expl, role="formula"):
        nonlocal r
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 3, formula, role=role, fmt=fmt, key=f"bond.{key}")
        sh.put(r, 5, expl, role="note_l")
        sh.merge(r, 5, r, LAST)
        r += 1

    bond_out("Price return", "price_return",
             f"=IFERROR(({B('end_price')}-{B('start_price')})/{B('start_price')},0)",
             Fmts.PCT, "(End - Start) / Start")
    bond_out("Coupon earned (per 100 face)", "coupon_earned",
             f"={B('face')}*{B('coupon_rate')}*{B('holding_days')}/365",
             Fmts.PRICE, "Face x Coupon rate x Days / 365")
    bond_out("Total bond return", "total_return",
             f"=IFERROR(({B('end_price')}-{B('start_price')}+{B('coupon_earned')})/{B('start_price')},0)",
             Fmts.PCT, "(End - Start + Coupon) / Start", role="result")
    common.cell_comment(sh, r - 1, 1, "Bond return = (End price - Start price + Coupon earned) / Start price.\n"
                                      "It feeds the US Government Bonds local return on Scenario Output.")

    sh.freeze("A6")
    widths = [30, 6, 12, 12, 13, 13, 13, 9, 9, 8, 8]
    for c, w in enumerate(widths, start=1):
        sh.col_width(c, w)
    return sh
