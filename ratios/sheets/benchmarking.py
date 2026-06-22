"""Industry Benchmarking (Sheet 13): company vs five peers, ranked and charted."""

from __future__ import annotations

from dcf.config import Fmt
from .. import common
from ..formulas import q, sentence

PCT, MULT = Fmt.PCT, Fmt.MULT2
CO, P0 = 2, 3  # company column, first peer column


def build(sh, ctx):
    refs = ctx.refs
    li = ctx.last_hist_idx
    peers = ctx.data.get("peers", {})
    pnames = peers.get("names", [f"Peer {i+1}" for i in range(5)])
    med_c, rank_c, pct_c, best_c = 8, 9, 10, 11

    common.title_block(sh, "INDUSTRY BENCHMARKING",
                       "Company vs peers — ranking, percentile and best-in-class", last_col=best_c)
    common.nav_bar(sh, 5, exclude={"Home"})
    r = 7
    sh.put(r, 1, "Company figures link to the latest reported year; peer cells are inputs.",
           role="note")
    sh.merge(r, 1, r, best_c)
    r += 1

    # header
    sh.put(r, 1, "Ratio (latest year)", role="colhdr")
    sh.put(r, CO, "Company", role="colhdr_r")
    for j in range(5):
        sh.put(r, P0 + j, pnames[j], role="input_l", key=f"bm.name{j}")
    sh.put(r, med_c, "Median", role="colhdr_r")
    sh.put(r, rank_c, "Rank", role="colhdr_r")
    sh.put(r, pct_c, "Pct'ile", role="colhdr_r")
    sh.put(r, best_c, "Flag", role="colhdr")
    sh.freeze(f"B{r+1}")
    r += 1

    rows = [
        ("Gross margin", f"prof.gross_margin@{li}", "gross_margin", True, PCT),
        ("Operating margin", f"prof.operating_margin@{li}", "operating_margin", True, PCT),
        ("Net margin", f"prof.net_margin@{li}", "net_margin", True, PCT),
        ("ROE", f"prof.roe@{li}", "roe", True, PCT),
        ("ROIC", f"prof.roic@{li}", "roic", True, PCT),
        ("Current ratio", f"liq.current_ratio@{li}", "current_ratio", True, MULT),
        ("Net debt / EBITDA", f"solv.net_debt_ebitda@{li}", "net_debt_ebitda", False, MULT),
        ("Revenue 5y CAGR", "grow.cagr5.revenue", "rev_cagr5", True, PCT),
        ("FCF margin", f"prof.fcf_margin@{li}", "fcf_margin", True, PCT),
        ("EV / EBITDA", f"val.ev_ebitda@{li}", "ev_ebitda", False, MULT),
    ]
    first = r
    radar_src = {}  # ratio_key -> (company_cell, median_cell)
    best_cells = []
    roic_row = None
    for label, comp_ref, pkey, higher, fmt in rows:
        sh.put(r, 1, label, role="label")
        sh.put(r, CO, f"={refs.ref(comp_ref)}", role="output", fmt=fmt)
        vals = peers.get(pkey, [None] * 5)
        for j in range(5):
            sh.put(r, P0 + j, vals[j], role="input", fmt=fmt, key=f"bm.{pkey}.{j}")
        rng = f"{sh.coord(r, CO)}:{sh.coord(r, P0 + 4)}"
        comp = sh.local(r, CO)
        sh.put(r, med_c, f'=IFERROR(MEDIAN({rng}),"")', role="formula", fmt=fmt)
        order = 0 if higher else 1
        sh.put(r, rank_c, f'=IFERROR(RANK({comp},{rng},{order}),"")', role="formula", fmt=Fmt.INT)
        rk = sh.local(r, rank_c)
        sh.put(r, pct_c, f'=IFERROR((6-{rk})/5,"")', role="output", fmt=PCT)
        sh.put(r, best_c, f'=IFERROR(IF({rk}=1,"Best-in-Class",""),"")', role="status", key=f"bm.best.{pkey}")
        best_cells.append((r, best_c))
        common.heat_map(sh, rng, reverse=not higher)
        radar_src[pkey] = (sh.local(r, CO), sh.local(r, med_c))
        if pkey == "roic":
            roic_row = r
        r += 1
    last = r - 1
    if best_cells:
        common.traffic_light(sh, f"{sh.coord(first, best_c)}:{sh.coord(last, best_c)}",
                             sh.coord(first, best_c))
    r += 1

    # radar block (company vs peer median across margin/return ratios)
    common.section(sh, r, "Competitive Profile (vs peer median)", c1=1, c2=best_c)
    r += 1
    radar_keys = [("Gross", "gross_margin"), ("Operating", "operating_margin"),
                  ("Net", "net_margin"), ("ROE", "roe"), ("ROIC", "roic"), ("FCF mgn", "fcf_margin")]
    head_row = r
    sh.put(r, 1, "Entity", role="colhdr")
    for j, (lab, _) in enumerate(radar_keys):
        sh.put(r, CO + j, lab, role="colhdr_r")
    r += 1
    sh.put(r, 1, "Company", role="label")
    for j, (_, k) in enumerate(radar_keys):
        sh.put(r, CO + j, f"={radar_src[k][0]}", role="output", fmt=PCT)
    co_row = r
    r += 1
    sh.put(r, 1, "Peer median", role="label")
    for j, (_, k) in enumerate(radar_keys):
        sh.put(r, CO + j, f"={radar_src[k][1]}", role="formula", fmt=PCT)
    med_row = r
    r += 2

    common.radar_chart(sh, f"{_col(CO)}{r}", "Company vs peer median",
                       rows=[co_row, med_row], cat_row=head_row,
                       first_col=CO, last_col=CO + len(radar_keys) - 1, width=13, height=9)
    if roic_row:
        common.bar_chart(sh, f"{_col(CO + 7)}{r}", "ROIC vs peers",
                         rows=[roic_row, roic_row], cat_row=first - 1,
                         first_col=CO, last_col=P0 + 4, width=13, height=9)
    r += 19

    common.section(sh, r, "Automated Observations", c1=1, c2=best_c)
    r += 1
    cnt_best = f'COUNTIF({sh.coord(first, best_c)}:{sh.coord(last, best_c)},"Best-in-Class")'
    sh.put(r, 1, sentence(q("» The company ranks best-in-class on "), f"TEXT({cnt_best},\"0\")",
                          q(" of "), q(str(len(rows))), q(" benchmarked metrics versus its peer set.")),
           role="panel", align="lw")
    sh.merge(r, 1, r, best_c)
    sh.col_width(1, 24)
    for c in range(2, best_c + 1):
        sh.col_width(c, 12)
    return sh


def _col(idx):
    from dcf.utils import col_letter
    return col_letter(idx)
