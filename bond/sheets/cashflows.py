"""Sheet 3: Cash Flows -- coupon & principal schedule, discounted at the YTM."""

from __future__ import annotations

from .. import common
from ..common import cell_comment, define_name
from ..config import Fmt, MAX_CF_ROWS

LAST = 10


def build(sh, ctx):
    common.title_block(sh, "CASH FLOWS", "Every future payment, its timing, and its present value at the YTM",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "WHAT THIS SHOWS:  each remaining coupon and the final principal, discounted back to today at the YTM. "
        "The present values add up to the DIRTY price - this is the engine behind the bond's price.",
        "Only payments AFTER the settlement date are shown. Coupon count matches the frequency "
        "(Annual=1, Semiannual=2, Quarterly=4 per year; Zero-coupon = principal only).",
        "Discount factor = 1 / (1 + YTM/frequency) ^ (periods to payment). PV = Total cash flow x Discount factor.",
    ], last_col=LAST)
    r += 1

    # ---- schedule parameters (auto) ----
    r = common.section(sh, r, "Schedule parameters (auto)", c1=1, c2=LAST)
    sh.put(r, 1, "Remaining payments", role="label_b")
    sh.put(r, 2, "=IF(IsZero=1,1,COUPNUM(Settle,Maturity,Freq,Basis))", role="formula", fmt=Fmt.INT)
    define_name(sh, "Ncoup", r, 2)
    sh.put(r, 4, f"Number of future payments (capped at {MAX_CF_ROWS} rows below).", role="note_l")
    sh.merge(r, 4, r, LAST); r += 1
    sh.put(r, 1, "Next payment date", role="label_b")
    sh.put(r, 2, "=IF(IsZero=1,Maturity,COUPNCD(Settle,Maturity,Freq,Basis))", role="formula", fmt=Fmt.DATE)
    define_name(sh, "Ncd", r, 2); r += 1
    sh.put(r, 1, "Fraction of 1st period left", role="label_b")
    sh.put(r, 2, "=IF(IsZero=1,YearsToMat,COUPDAYSNC(Settle,Maturity,Freq,Basis)/COUPDAYS(Settle,Maturity,Freq,Basis))",
           role="formula", fmt=Fmt.NUM4)
    define_name(sh, "Wfrac", r, 2)
    cell_comment(sh, r, 2, "How much of the current coupon period is still ahead of you.\n"
                           "Used so the first payment is discounted over the correct (partial) period.")
    sh.merge(r, 4, r, LAST); r += 2

    # ---- schedule table ----
    hdr = r
    cols = ["Payment #", "Payment date", "Coupon CF", "Principal CF", "Total CF",
            "Time (years)", "Discount factor", "PV of CF", "Convexity term", "Time x PV"]
    for c, tx in enumerate(cols, 1):
        sh.put(hdr, c, tx, role="colhdr" if c > 1 else "colhdr_l")
    sh.row_height(hdr, 24)
    cell_comment(sh, hdr, 9, "Helper for convexity: Total x t x (t+1) / (1+YTM/f)^(t+2), t in periods.\n"
                             "Summed below and divided by (dirty price x frequency^2).")
    cell_comment(sh, hdr, 10, "Helper for Macaulay duration: Time (years) x PV. Summed and divided by total PV.")
    first = hdr + 1
    for i in range(1, MAX_CF_ROWS + 1):
        r = first + i - 1
        g = f'IF({i}>Ncoup,""'  # guard prefix
        sh.put(r, 1, f'=IF({i}>Ncoup,"",{i})', role="formula", fmt=Fmt.INT)
        sh.put(r, 2, f'={g},EDATE(Ncd,(12/Freq)*({i}-1)))', role="formula", fmt=Fmt.DATE)
        sh.put(r, 3, f'={g},IF(IsZero=1,0,CouponRate/Freq*Face))', role="formula", fmt=Fmt.MONEY)
        sh.put(r, 4, f'={g},IF({i}=Ncoup,Face,0))', role="formula", fmt=Fmt.MONEY)
        sh.put(r, 5, f'={g},{sh.local(r,3)}+{sh.local(r,4)})', role="formula", fmt=Fmt.MONEY)
        sh.put(r, 6, f'={g},(({i}-1)+Wfrac)/Freq)', role="formula", fmt=Fmt.RATIO)
        sh.put(r, 7, f'={g},1/(1+YTM/Freq)^(({i}-1)+Wfrac))', role="formula", fmt=Fmt.NUM4)
        sh.put(r, 8, f'={g},{sh.local(r,5)}*{sh.local(r,7)})', role="formula", fmt=Fmt.MONEY)
        sh.put(r, 9, f'={g},{sh.local(r,5)}*(({i}-1)+Wfrac)*(({i}-1)+Wfrac+1)/(1+YTM/Freq)^(({i}-1)+Wfrac+2))',
               role="formula", fmt=Fmt.NUM4)
        sh.put(r, 10, f'={g},{sh.local(r,6)}*{sh.local(r,8)})', role="formula", fmt=Fmt.NUM4)
    last = first + MAX_CF_ROWS - 1

    # ---- totals + summary ----
    tot = last + 1
    sh.put(tot, 1, "Totals", role="total_l")
    for c in (3, 4, 5, 8):
        sh.put(tot, c, f"=SUM({common.col_letter(c)}{first}:{common.col_letter(c)}{last})", role="total",
               fmt=Fmt.MONEY)
    r = tot + 2

    r = common.section(sh, r, "From the schedule (auto)", c1=1, c2=LAST)
    pv_rng = f"H{first}:H{last}"
    tpv_rng = f"J{first}:J{last}"
    sh.put(r, 1, "Sum of PV  =  Dirty price", role="label_b")
    sh.put(r, 2, f"=SUM({pv_rng})", role="output", fmt=Fmt.PRICE)
    define_name(sh, "DirtyCF", r, 2)
    sh.put(r, 4, "Should equal the Dirty price on the Valuation sheet (checked in Audit).", role="note_l")
    sh.merge(r, 4, r, LAST); r += 1
    sh.put(r, 1, "Macaulay duration (schedule)", role="label_b")
    sh.put(r, 2, f"=SUM({tpv_rng})/SUM({pv_rng})", role="output", fmt=Fmt.YEARS)
    define_name(sh, "MacaulayCF", r, 2)
    cell_comment(sh, r, 2, "Weighted-average time to get your money back:\n"
                           "sum(time x PV) / sum(PV). This is Macaulay duration.")
    r += 1
    sh.put(r, 1, "Convexity (schedule)", role="label_b")
    sh.put(r, 2, f"=SUM(I{first}:I{last})/(SUM({pv_rng})*Freq^2)", role="output", fmt=Fmt.RATIO)
    define_name(sh, "Convexity", r, 2)
    sh.put(r, 4, "Excel has no convexity function, so it is computed here from the schedule.", role="note_l")
    sh.merge(r, 4, r, LAST); r += 1

    sh.freeze(f"A{first}")
    sh.col_width(1, 10)
    sh.col_width(2, 13)
    for c in range(3, LAST + 1):
        sh.col_width(c, 13)
    return sh
