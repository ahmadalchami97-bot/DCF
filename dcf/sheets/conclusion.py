"""
Conclusion sheet -- the written investment thesis.

Most of the prose is *formula-driven*: the stance, the value drivers, the risks
and the swing assumptions all read live from the model, so the narrative always
matches the numbers. Static text is reserved for framing and caveats. This is the
page an analyst would lift into an investment memo / IC note.
"""

from __future__ import annotations

from ..config import Fmt, Thresholds as T
from . import common

LAST = 8


def build(sh, ctx: common.Context):
    refs = ctx.refs
    last = ctx.n_hist - 1
    H = lambda k, p: refs.ref(f"h.{k}@{p}")     # noqa: E731
    HL = lambda k: refs.ref(f"h.lbl.{k}")       # noqa: E731
    Dk = lambda k: refs.ref(f"dcf.{k}")         # noqa: E731
    A = lambda k: refs.ref(f"as.{k}")           # noqa: E731
    SC = lambda s, k: refs.ref(f"sc.{s}.{k}")   # noqa: E731

    up = Dk("upside")
    vps = Dk("value_per_share")
    px = Dk("current_price")
    roic = H("roic", last)
    wv = refs.ref("wacc.value")

    sh.hide_gridlines()
    sh.col_width(1, 26)
    for c in range(2, LAST + 1):
        sh.col_width(c, 12)
    r = common.title_block(sh, "INVESTMENT CONCLUSION",
                           f"{ctx.data['meta'].get('name','Company')} — thesis, drivers, risks & stance",
                           last_col=LAST)
    r += 1

    def para(row, formula, role="note", height=30):
        sh.put(row, 1, formula, role=role, align="ltw")
        sh.merge(row, 1, row, LAST)
        sh.row_height(row, height)
        return row + 1

    def bullets(row, formulas, height=26):
        for fm in formulas:
            row = para(row, fm, role="body_l", height=height)
        return row

    # ---- final stance ----------------------------------------------------
    r = common.section(sh, r, "Final Stance", c1=1, c2=LAST)
    stance = (
        f'="Stance:  "&'
        f'IF(ISNUMBER({up}),IF({up}>{T.VAL_BAND},"CONSTRUCTIVE — the DCF implies meaningful upside.",'
        f'IF({up}<-{T.VAL_BAND},"CAUTIOUS — the DCF implies the price is rich.",'
        f'"NEUTRAL — price is close to intrinsic value.")),'
        f'"VALUE-ONLY — no market price entered; compare to the DCF value per share.")'
        f'&"  Business quality is "&'
        f'IF(AND(ISNUMBER({roic}),{roic}>{wv}+0.01),"GOOD (ROIC above WACC). ",'
        f'IF(AND(ISNUMBER({roic}),{roic}<{wv}-0.01),"CHALLENGED (ROIC below WACC). ","ADEQUATE (ROIC ~ WACC). "))'
    )
    r = para(r, stance, role="output", height=34)
    common.add_label_coloring(sh, f"{sh.coord(r-1,1)}:{sh.coord(r-1,1)}", sh.coord(r - 1, 1))
    r += 1

    # ---- valuation summary ----------------------------------------------
    r = common.section(sh, r, "Valuation Summary", c1=1, c2=LAST)
    summ = (
        f'="The base-case DCF values the equity at "&TEXT({vps},"#,##0.00")&" per share, '
        f'versus a market price of "&IF(ISNUMBER({px}),TEXT({px},"#,##0.00"),"n/a")&" — "&'
        f'IF(ISNUMBER({up}),TEXT({up},"+0.0%;-0.0%")&" upside/(downside).","no price entered.")'
        f'&" The scenario range runs from "&TEXT({SC("Downside","per_share")},"#,##0.00")&'
        f'" (downside) to "&TEXT({SC("Bull","per_share")},"#,##0.00")&" (bull)."'
    )
    r = para(r, summ, height=30)
    r += 1

    # ---- what is driving value ------------------------------------------
    r = common.section(sh, r, "What Is Driving Value", c1=1, c2=LAST)
    r = bullets(r, [
        f'="•  Capital returns:  ROIC "&TEXT({roic},"0.0%")&" vs WACC "&TEXT({wv},"0.0%")&" — "&'
        f'IF(AND(ISNUMBER({roic}),{roic}>{wv}+0.01),"value-creating.",'
        f'IF(AND(ISNUMBER({roic}),{roic}<{wv}-0.01),"value-destroying.","roughly neutral."))',
        f'="•  Profitability:  EBIT margin "&TEXT({H("ebit_margin",last)},"0.0%")&" ("&{HL("ebit_margin")}&"), '
        f'gross margin "&TEXT({H("gross_margin",last)},"0.0%")&" ("&{HL("gross_margin")}&")."',
        f'="•  Cash generation:  FCF margin "&TEXT({H("fcf_margin",last)},"0.0%")&" ("&{HL("fcf_margin")}&"); '
        f'CFO/EBITDA "&TEXT({H("cash_conversion",last)},"0.0%")&"."',
        f'="•  Growth:  latest revenue growth "&TEXT({H("rev_growth",last)},"0.0%")&" ("&{HL("rev_growth")}&"); '
        f'forecast fades toward the long-run rate."',
        f'="•  Balance sheet:  net debt / EBITDA "&TEXT({H("net_debt_ebitda",last)},"0.0")&"x ("&{HL("net_debt_ebitda")}&"), '
        f'interest coverage "&TEXT({H("interest_coverage",last)},"0.0")&"x."',
    ])
    r += 1

    # ---- what is hurting / risks ----------------------------------------
    r = common.section(sh, r, "What Is Hurting Value / Key Risks", c1=1, c2=LAST)
    r = bullets(r, [
        f'="•  Valuation:  "&{Dk("val_label")}&" at the current price ("&'
        f'IF(ISNUMBER({up}),TEXT({up},"+0.0%;-0.0%")&" vs DCF value).","n/a).")',
        f'="•  Leverage & coverage:  "&{HL("net_debt_ebitda")}&" leverage; "&{HL("interest_coverage")}&" interest coverage."',
        f'="•  Growth & margin trend:  revenue "&{HL("rev_growth")}&"; gross margin "&{HL("gross_margin")}&"."',
        f'="•  Terminal-value reliance:  "&TEXT({Dk("tv_share")},"0.0%")&" of enterprise value sits in the terminal value '
        f'— sensitive to WACC and g."',
        f'="•  Data & model health:  "&{refs.ref("chk.verdict")}&" (see Checks sheet)."',
    ])
    r += 1

    # ---- key assumptions that matter most -------------------------------
    r = common.section(sh, r, "Key Assumptions That Matter Most", c1=1, c2=LAST)
    sh.put(r, 1, "Assumption", role="colhdr")
    sh.put(r, 2, "Active value", role="colhdr_r")
    sh.merge(r, 2, r, 3)
    sh.put(r, 4, "Why it matters (see Sensitivity sheet for the swing)", role="colhdr")
    sh.merge(r, 4, r, LAST)
    r += 1
    swing = [
        ("WACC (discount rate)", refs.ref("wacc.value"), Fmt.PCT2,
         "The single biggest lever; lower WACC raises value sharply."),
        ("Terminal growth (g)", A("act_tv_growth"), Fmt.PCT,
         "Drives the terminal value; capped below WACC for stability."),
        ("Terminal EBIT margin", A("act_target_margin"), Fmt.PCT,
         "Sets steady-state profitability and hence cash flow."),
        ("Year-1 revenue growth", A("act_start_growth"), Fmt.PCT,
         "Anchors the near-term trajectory before mean reversion."),
        ("Exit EBITDA multiple", A("exit_multiple"), Fmt.MULT,
         "Cross-check only; compare to the implied perpetuity multiple."),
    ]
    for label, ref, fmt, why in swing:
        sh.put(r, 1, label, role="label")
        sh.put(r, 2, f"={ref}", role="link", fmt=fmt)
        sh.merge(r, 2, r, 3)
        sh.put(r, 4, why, role="note")
        sh.merge(r, 4, r, LAST)
        r += 1
    r += 1

    # ---- upside / downside ----------------------------------------------
    r = common.section(sh, r, "Upside & Downside", c1=1, c2=LAST)
    r = para(r,
             f'="Upside (bull):  value per share "&TEXT({SC("Bull","per_share")},"#,##0.00")&" ("&'
             f'IF(ISNUMBER({SC("Bull","upside")}),TEXT({SC("Bull","upside")},"+0.0%;-0.0%"),"n/a")&'
             f'") on faster growth and wider margins.    Downside (stress):  value per share "&'
             f'TEXT({SC("Downside","per_share")},"#,##0.00")&" ("&'
             f'IF(ISNUMBER({SC("Downside","upside")}),TEXT({SC("Downside","upside")},"+0.0%;-0.0%"),"n/a")&'
             f'") on weak growth and margin compression."', height=30)
    r += 1

    # ---- caveats ---------------------------------------------------------
    r = common.section(sh, r, "Caveats & Limitations", c1=1, c2=LAST)
    for line in _CAVEATS:
        r = para(r, f'="•  {line}"', role="note", height=24)
    return sh


_CAVEATS = [
    "A DCF is only as good as its inputs: revise the market data, growth and margin "
    "assumptions for your own view before relying on the output.",
    "Where data was missing the model used clearly-labelled fallbacks; replace them "
    "with company-specific figures to firm up the valuation.",
    "Terminal value typically dominates a DCF — treat WACC and terminal growth as the "
    "key swing factors and lean on the Sensitivity and Scenario sheets.",
    "This is an analytical tool, not investment advice. Validate against filings, peers "
    "and qualitative judgement before acting.",
]
