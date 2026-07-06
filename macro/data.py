"""
Seed content for the Macro Market Intelligence System core.

- INDICATORS: the Impact Library (21 US/global macro indicators) with polarity
  flags, importance and "typical surprise" scales that drive the Surprise Engine.
- SAMPLE_RELEASES: a worked set of recent data prints for the Data Tracker.
- FED_STATE / FED_SPEECHES / GLOBAL_CB: inputs for the Fed & Central Bank Tracker.

Everything here is an INPUT the analyst replaces over time. Polarity convention:
  pol_infl  +1 = a higher print is inflationary/hawkish, -1 = disinflationary/dovish
  pol_grow  +1 = a higher print signals stronger growth, -1 = weaker growth
"""

from __future__ import annotations

from datetime import date


def _ind(name, cat, unit, meas, why, high, low, fed, usd, uyld, upx, eq, gold, oil, gcc,
         pinf, pgro, imp, scale, exc):
    return dict(name=name, cat=cat, unit=unit, meas=meas, why=why, high=high, low=low, fed=fed,
                usd=usd, uyld=uyld, upx=upx, eq=eq, gold=gold, oil=oil, gcc=gcc,
                pinf=pinf, pgro=pgro, imp=imp, scale=scale, exc=exc)


INDICATORS = [
    _ind("CPI y/y", "Inflation", "% y/y", "consumer price inflation, headline",
         "the main inflation gauge; drives Fed expectations and real yields",
         "Hotter -> hawkish; supports USD & yields, pressures bonds, gold and equities",
         "Cooler -> dovish; supports bonds, gold and risk assets",
         "Higher -> fewer / later cuts", "↑", "↑", "↓", "↓", "↓", "↔", "↔ (USD peg)",
         +1, 0, 5, 0.2, "Watch core vs headline; energy and base effects can distort."),
    _ind("Core CPI y/y", "Inflation", "% y/y", "CPI excluding food and energy",
         "cleaner inflation trend the Fed focuses on",
         "Sticky core -> hawkish; bond- and gold-negative",
         "Cooling core -> dovish; bond- and gold-positive", "Higher -> hawkish",
         "↑", "↑", "↓", "↓", "↓", "↔", "↔", +1, 0, 5, 0.2,
         "Shelter lags; core services (ex-housing) is the stickiest part."),
    _ind("PCE y/y", "Inflation", "% y/y", "personal consumption price index",
         "a broad inflation measure across a wide basket",
         "Hotter -> hawkish", "Cooler -> dovish", "Higher -> hawkish",
         "↑", "↑", "↓", "↓", "↓", "↔", "↔", +1, 0, 4, 0.2, "Broader basket than CPI."),
    _ind("Core PCE y/y", "Inflation", "% y/y", "PCE excluding food and energy",
         "the Fed's PREFERRED inflation gauge (2% target)",
         "Above target -> hawkish", "Toward target -> dovish", "Higher -> hawkish",
         "↑", "↑", "↓", "↓", "↓", "↔", "↔", +1, 0, 5, 0.2, "This is the Fed's target metric."),
    _ind("GDP q/q ann", "Growth", "% ann", "real output growth, annualized",
         "headline growth; expansion vs recession",
         "Strong -> risk-on, mildly hawkish (delays cuts)",
         "Weak -> recession fear, dovish", "Higher -> mildly hawkish",
         "↑", "↑", "↑*", "↑", "↔", "↑", "↔", 0, +1, 4, 0.5,
         "Backward-looking; watch composition (inventories, net exports)."),
    _ind("Nonfarm payrolls", "Labor", "000s", "net new jobs excluding farming",
         "the top labor print; jobs = income = demand",
         "Strong jobs -> hawkish; USD & yields up, bonds down",
         "Weak jobs -> dovish, but recession fear can hit equities", "Higher -> hawkish",
         "↑", "↑", "↓", "Mixed", "↓", "↑", "↔", +1, +1, 5, 50,
         "Revisions and the household survey can flip the read."),
    _ind("Unemployment rate", "Labor", "%", "share of the labor force unemployed",
         "the Fed's employment mandate; a recession trigger (Sahm rule)",
         "Higher -> dovish, growth-negative", "Lower -> hawkish, tight labor",
         "Higher -> dovish (cuts)", "↓", "↓", "↑", "Mixed", "↑", "↓", "↔",
         -1, -1, 4, 0.1, "Participation swings distort it; read with payrolls."),
    _ind("Avg hourly earnings y/y", "Labor", "% y/y", "wage growth",
         "wages feed the services inflation the Fed fears most",
         "Hot wages -> hawkish", "Cooling wages -> dovish", "Higher -> hawkish",
         "↑", "↑", "↓", "↓", "↓", "↔", "↔", +1, +1, 4, 0.2,
         "Job-mix (composition) effects can mislead month to month."),
    _ind("Initial jobless claims", "Labor", "000s", "new unemployment filings (weekly)",
         "the most timely labor signal",
         "Rising claims -> dovish, labor weakening", "Falling claims -> hawkish, labor strong",
         "Higher -> dovish", "↓", "↓", "↑", "Mixed", "↑", "↓", "↔",
         -1, -1, 3, 15, "Noisy weekly; watch the 4-week moving average."),
    _ind("JOLTS job openings", "Labor", "mn", "unfilled job vacancies",
         "labor demand and tightness",
         "More openings -> hawkish (tight labor)", "Fewer -> dovish (loosening)",
         "Higher -> hawkish", "↑", "↑", "↓", "Mixed", "↓", "↔", "↔",
         +1, +1, 3, 0.2, "Reported with an extra month lag vs payrolls."),
    _ind("ISM Manufacturing", "Growth", "index", "factory activity (>50 = expansion)",
         "a leading cyclical gauge",
         "Expansion -> risk-on, mildly hawkish", "Contraction -> growth fear, dovish",
         "Higher -> mildly hawkish", "↑", "↑", "↓", "↑", "↔", "↑", "↔",
         +1, +1, 4, 1.0, "The prices-paid sub-index is the inflation tell."),
    _ind("ISM Services", "Growth", "index", "services activity (>50 = expansion)",
         "services are ~70% of the US economy",
         "Firm services -> hawkish, risk-on", "Soft -> dovish, growth fear",
         "Higher -> hawkish", "↑", "↑", "↓", "↑", "↔", "↑", "↔",
         +1, +1, 4, 1.0, "More important than manufacturing for the US cycle."),
    _ind("S&P Global PMI", "Growth", "index", "private-sector activity survey (composite)",
         "timely, globally comparable growth read",
         "Expansion -> risk-on", "Contraction -> risk-off", "Higher -> mildly hawkish",
         "↑", "↑", "↓", "↑", "↔", "↑", "↔", +1, +1, 3, 1.0,
         "Flash vs final releases; useful for cross-country comparison."),
    _ind("Retail sales m/m", "Growth", "% m/m", "consumer spending",
         "the consumer is the US growth engine",
         "Strong -> growth+, can delay cuts", "Weak -> growth fear",
         "Higher -> mildly hawkish", "↑", "↑", "Mixed", "↑*", "↔", "↑", "↔",
         +1, +1, 4, 0.3, "Watch the control group and autos/gas swings."),
    _ind("Consumer confidence", "Growth", "index", "household sentiment",
         "a leading indicator of future spending",
         "Confident -> growth+", "Worried -> growth-", "Higher -> mildly hawkish",
         "↑", "↔", "↔", "↑", "↔", "↔", "↔", 0, +1, 3, 2.0,
         "Sentiment and actual spending can diverge."),
    _ind("Housing starts", "Growth", "mn ann", "new residential construction",
         "a rate-sensitive cyclical indicator",
         "More building -> growth+", "Fewer -> slowdown", "Higher -> mildly hawkish",
         "↔", "↔", "↔", "↑", "↔", "↔", "↔", 0, +1, 2, 0.05,
         "Very sensitive to mortgage rates and weather."),
    _ind("Durable goods m/m", "Growth", "% m/m", "orders for long-lived goods",
         "a business-investment gauge",
         "Strong orders -> growth+", "Weak -> slowdown", "Higher -> mildly hawkish",
         "↔", "↔", "↔", "↑", "↔", "↔", "↔", 0, +1, 2, 0.8,
         "Aircraft orders make it lumpy; watch ex-transportation."),
    _ind("Trade balance", "Trade", "$bn", "exports minus imports",
         "growth composition and USD flows",
         "Smaller deficit -> mild USD+", "Wider deficit -> mild USD-", "Limited",
         "↔", "↔", "↔", "↔", "↔", "↔", "↔", 0, 0, 2, 5,
         "Usually reported as a negative number (a deficit)."),
    _ind("Federal budget balance", "Fiscal", "$bn", "government surplus / deficit",
         "Treasury supply and term premium",
         "Bigger deficit -> more bond supply -> yields up",
         "Smaller deficit -> supportive for bonds", "Limited (supply channel)",
         "↔", "↑", "↓", "↔", "↔", "↔", "↔", +1, 0, 2, 20,
         "Seasonal; watch the rolling 12-month trend, not one month."),
    _ind("EIA crude inventories", "Energy", "mn bbl", "weekly US crude stock change",
         "the near-term oil supply/demand balance",
         "Builds -> bearish oil -> disinflationary", "Draws -> bullish oil -> inflationary",
         "Via oil / inflation", "↔", "↔", "↔", "↔", "↔", "↓", "↓ (lower oil)",
         -1, 0, 2, 2.0, "Very noisy weekly; watch the trend and product stocks."),
    _ind("Global/China PMI", "Growth", "index", "ex-US global activity (e.g. China)",
         "global demand, commodities, EM and GCC",
         "Global expansion -> risk-on, oil+", "Global slowdown -> risk-off, oil-",
         "Indirect", "↓", "↑", "↓", "↑", "↔", "↑", "↑ (oil demand)",
         0, +1, 3, 1.0, "China property and policy dominate the swings."),
]

# (date, country, indicator, actual, forecast, previous, unit, source, notes)
SAMPLE_RELEASES = [
    (date(2026, 6, 11), "US", "CPI y/y", 3.4, 3.2, 3.3, "% y/y", "BLS", "Hotter than expected"),
    (date(2026, 6, 11), "US", "Core CPI y/y", 3.6, 3.5, 3.6, "% y/y", "BLS", "Sticky core"),
    (date(2026, 6, 27), "US", "Core PCE y/y", 2.9, 2.8, 2.8, "% y/y", "BEA", "Above 2% target"),
    (date(2026, 6, 5), "US", "Nonfarm payrolls", 210, 175, 168, "000s", "BLS", "Strong beat"),
    (date(2026, 6, 5), "US", "Unemployment rate", 4.0, 4.1, 4.0, "%", "BLS", "Tighter labor"),
    (date(2026, 6, 5), "US", "Avg hourly earnings y/y", 4.1, 3.9, 4.0, "% y/y", "BLS", "Hot wages"),
    (date(2026, 7, 2), "US", "Initial jobless claims", 232, 240, 245, "000s", "DOL", "Fewer claims"),
    (date(2026, 6, 1), "US", "ISM Manufacturing", 48.7, 49.5, 48.5, "index", "ISM", "Still contracting"),
    (date(2026, 6, 3), "US", "ISM Services", 53.8, 52.5, 53.0, "index", "ISM", "Firm services"),
    (date(2026, 6, 16), "US", "Retail sales m/m", 0.6, 0.3, 0.2, "% m/m", "Census", "Strong consumer"),
    (date(2026, 6, 24), "US", "Consumer confidence", 101.0, 104.0, 102.0, "index", "CB", "Softer sentiment"),
    (date(2026, 6, 26), "US", "GDP q/q ann", 2.4, 2.2, 2.5, "% ann", "BEA", "Resilient growth"),
    (date(2026, 6, 18), "US", "Housing starts", 1.35, 1.40, 1.38, "mn ann", "Census", "Rate-sensitive soft"),
    (date(2026, 6, 30), "US", "JOLTS job openings", 8.1, 7.9, 8.0, "mn", "BLS", "Still tight"),
]

FED_STATE = {
    "target_low": 4.25, "target_high": 4.50,
    "last_decision": "Hold", "last_date": date(2026, 6, 18),
    "next_fomc": date(2026, 7, 29),
    "implied_bps": 8,          # change in market-implied policy path since last meeting (bps)
    "expected_cuts": 1,        # cuts priced for the year
    "dotplot": "Fewer cuts",
    "qt_note": "QT ongoing at a reduced pace; balance-sheet runoff continues.",
    "curve_2y_bps": 6,         # 2Y yield change since last meeting (bps)
    "real_10y_bps": 5,         # 10Y real-yield change (bps)
    "analyst": "",
    "as_of": date(2026, 7, 6),
}

# (date, speaker, tone -2..+2, quote, takeaway)
FED_SPEECHES = [
    (date(2026, 6, 20), "Chair (Powell)", 1, "We need more confidence inflation is heading to 2%.", "Patient, mildly hawkish"),
    (date(2026, 6, 24), "Gov. Waller", 2, "Recent data argue for keeping policy restrictive.", "Hawkish"),
    (date(2026, 6, 27), "Pres. Daly", -1, "The labor market is coming into better balance.", "Mildly dovish"),
]

# (central bank, bias, note)
GLOBAL_CB = [
    ("ECB", "Mildly dovish", "Cutting gradually as inflation eases"),
    ("BOE", "Neutral", "Data-dependent; services inflation still sticky"),
    ("SNB", "Dovish", "Low inflation, easing bias"),
    ("BOJ", "Mildly hawkish", "Normalizing policy very slowly"),
]


def build_sample() -> dict:
    """The worked example: full library, sample releases, populated Fed state."""
    return {
        "indicators": INDICATORS,
        "releases": SAMPLE_RELEASES,
        "fed_state": dict(FED_STATE),
        "fed_speeches": FED_SPEECHES,
        "global_cb": GLOBAL_CB,
    }


def empty_like_sample() -> dict:
    """A blank template: keep the reference library and CB list, clear the inputs."""
    st = dict(FED_STATE)
    st.update(implied_bps=0, curve_2y_bps=0, real_10y_bps=0, expected_cuts=0, analyst="")
    return {
        "indicators": INDICATORS,
        "releases": [],
        "fed_state": st,
        "fed_speeches": [],
        "global_cb": GLOBAL_CB,
    }
