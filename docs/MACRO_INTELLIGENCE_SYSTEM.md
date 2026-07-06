# Macro Market Intelligence System — Workbook Architecture & Build Specification

**Purpose:** a single Excel workbook that acts as a professional macro-strategy
desk in a file. It tells you *what changed* in the macro/geopolitical environment,
*why it matters*, *which assets are affected*, *whether the signal is
inflationary/deflationary/hawkish/dovish/risk-on/risk-off*, and *what it means for
your exposures* (USD, US Treasuries, equities, gold, oil, Kuwait/GCC). It is built
for monitoring and decision support, and for explaining a view to senior
management in under a minute.

> **Build status.** The **core engine (Phase 1–2)** of this design is built and
> shipping: six live-formula sheets — Cover, Settings, Impact Library (21
> indicators), Data Tracker, Data Surprise Engine, and Fed & Central Bank Tracker.
> Run `python build_macro.py` (or `--blank` for an empty template); verified by
> `tests/test_macro.py`. The remaining sheets in this spec (market modules,
> cross-asset matrix, scenario engine, regime classifier, portfolio link,
> watchlist, and the executive dashboard) are the next phases and extend the same
> named-range wiring described below.

**Design principle:** the workbook separates three layers, and every number flows
one way through them:

```
   INPUT LAYER            →     ENGINE LAYER              →     OUTPUT LAYER
   (you type / paste)            (formulas score it)             (management reads)
   ─────────────────            ──────────────────              ────────────────
   Macro Data Tracker           Surprise Engine                 Executive Dashboard
   Fed inputs                   Fed Bias Score                  Exec Cross-Asset Snapshot
   Geopolitical inputs          Geo Risk Score                  Scenario Engine output
   Market levels (DXY,           Regime Classifier              Market Note Generator
   yields, gold, oil, VIX)      Cross-Asset logic               Watchlist alerts
   Settings & parameters        Asset-Impact mapping            Portfolio Exposure read
```

The analyst only ever maintains the **input layer** and the **Settings** sheet.
Everything downstream recalculates. Nothing is hard-coded; every score is a
formula you can audit.

---

## 0. Contents

1. Sheet map & dependency flow
2. Global design standards (colour, formatting, conditional formatting, signal vocabulary)
3. The four scoring engines (methodologies + exact formulas)
   - 3.1 Data-Surprise scoring (surprise-vs-expectations)
   - 3.2 Fed hawkish/dovish score
   - 3.3 Geopolitical risk score
   - 3.4 Asset-class impact scoring
   - 3.5 Market-regime classifier (fingerprint matching)
4. Sheet-by-sheet specification (all 18 tabs)
5. Executive Dashboard layout (cell-grid map)
6. Named ranges master list
7. Dropdown lists master list
8. Formula cookbook (INDEX/MATCH, XLOOKUP, IFS, SUMPRODUCT, TEXTJOIN, conditional formatting)
9. Recommended charts
10. Implementation roadmap (phased)

---

## 1. Sheet map & dependency flow

18 tabs, grouped. Codes (e.g. `S03`) are used for cross-references throughout.

| Code | Tab | Group | Layer |
|------|-----|-------|-------|
| S00 | Cover & User Guide | Navigation | — |
| S01 | **Executive Macro Dashboard** | Output | Output |
| S02 | Macro Data Tracker | Input | Input |
| S03 | Data Surprise Engine | Engine | Engine |
| S04 | Indicator Impact Library | Reference | Reference |
| S05 | Fed & Central Bank Tracker | Input+Engine | Input/Engine |
| S06 | USD Exposure Dashboard | Analysis | Engine |
| S07 | US Treasury / Bond Module | Analysis | Engine |
| S08 | Geopolitical Risk Tracker | Input+Engine | Input/Engine |
| S09 | Oil & Commodity Shock Module | Analysis | Engine |
| S10 | Cross-Asset Reaction Matrix | Reference/Engine | Engine |
| S11 | Scenario Engine | Output | Output |
| S12 | Market Regime Classifier | Engine | Engine |
| S13 | Portfolio Exposure Link | Output | Output |
| S14 | Market Note Generator | Output | Output |
| S15 | Watchlist & Early-Warning Signals | Output | Engine/Output |
| S16 | Executive Cross-Asset Snapshot | Output | Output |
| S17 | Settings & Lists | Config | Input |
| S18 | Glossary & Methodology | Reference | — |

**Dependency flow (who feeds whom):**

```
S17 Settings ──► (dropdowns, weights, thresholds, signal vocab) ──► every sheet

S02 Data Tracker ──► S03 Surprise Engine ──┬──► S05 Fed Score
                                           ├──► S12 Regime Classifier
                                           └──► S01 Dashboard

S04 Impact Library ──► S03, S10, S11  (lookup reference for asset impacts)

S05 Fed ─┐
S06 USD ─┤
S07 Bond ┤──► S10 Reaction Matrix ─┬─► S13 Portfolio Link
S08 Geo ─┤    S11 Scenario Engine ─┤   S14 Note Generator
S09 Oil ─┘    S12 Regime ──────────┴─► S16 Exec Snapshot

S15 Watchlist ──► S01 Dashboard ("What to watch next")
S01 Dashboard + S16 Snapshot ──► senior management
```

Rule of thumb: **arrows only point right and down.** A left/up reference means a
circular dependency — avoid it. The Dashboard (S01) and Exec Snapshot (S16) are
pure consumers; they never feed anything.

---

## 2. Global design standards

### 2.1 Colour-coding system

Use one consistent palette so any reader instantly knows what a cell *is*.

| Meaning | Fill | Font | Use for |
|---------|------|------|---------|
| **Input** (you type) | Pale yellow `#FFF7D6` | Navy `#1F3A5F` | every cell the analyst maintains |
| **Formula / derived** | none (white) | Black `#111111` | calculated cells |
| **Linked from another sheet** | none | Blue-grey `#2E5984` | pulled values (read-only) |
| **Key output / headline** | Pale green `#E3F2E1` | Dark green `#1F7A3D` bold | scores, regime, signals |
| **Section header** | Slate `#2E5984` | White bold | band titles |
| **Title bar** | Navy `#1F3A5F` | White | sheet titles |
| **Warning / alert** | Amber `#FFF1C2` / Red `#F8D7DA` | Dark | triggered watchlist / crisis |

**Signal colours** (semantic, used by conditional formatting on scores/arrows):

| Tone | Fill | Applies to |
|------|------|-----------|
| Risk-on / Positive / Dovish-easy | Green `#C6EFCE` / text `#1F7A3D` | ↑, "Risk-on", "Attractive", "Low" risk |
| Neutral | Grey `#EDEDED` / text `#595959` | ↔, "Neutral" |
| Caution | Amber `#FFEB9C` / text `#9C6500` | "Elevated", "Mildly hawkish", "Mixed" |
| Risk-off / Negative / Hawkish-tight | Red `#FFC7CE` / text `#9C0006` | ↓, "Risk-off", "High/Crisis", "Hawkish" |

### 2.2 Cell-formatting rules

- **Inputs unlocked, everything else locked** (Format Cells → Protection), so when
  you protect a sheet only yellow cells are editable. Do not enable sheet
  protection until the build is finished.
- Numbers: yields & rates `0.00%`; index levels `#,##0.0`; oil/gold `#,##0.00`;
  scores `0.0`; bps `+0;-0;0` with a `" bps"` suffix.
- Dates: `dd-mmm-yyyy`. Freeze the header row + first column on every wide table.
- Fonts: Calibri 10 body, 9 for notes (grey italic), 18 white for titles.
- Column A left as a 2-3px "gutter"; start content in column B for a framed look.
- Every sheet: title bar (row 1), one-line purpose (row 2), a nav strip of
  hyperlinks to other tabs (row 3), content from row 5.

### 2.3 Conditional-formatting library (reusable rules)

| # | Rule | Where | How |
|---|------|-------|-----|
| CF1 | 3-colour scale red→white→green on **score** columns | S03, S05, S08, S15 | Home → CF → Colour Scales |
| CF2 | Icon set (↑ ↔ ↓ arrows) driven by a −2..+2 impact number | S10, S16 | CF → Icon Sets → 3 arrows; or map numbers to arrow glyphs with a formula (below) |
| CF3 | Text rule: cell = "Risk-off"/"Hawkish"/"High"/"Crisis" → red fill | S01, S05, S08 | CF → New Rule → "Format cells that contain" specific text, or `=$X5="Crisis"` |
| CF4 | Text rule: cell = "Risk-on"/"Dovish"/"Low" → green fill | S01, S05, S08 | as above |
| CF5 | Surprise heat: `=ABS($H5)>=1.5` (big z-score) → bold amber | S03 | formula rule |
| CF6 | Watchlist trigger: `=$D5>=$E5` (level ≥ trigger) → red row | S15 | formula rule applied to `$B5:$H5` |
| CF7 | Data-staleness: `=TODAY()-$B5>35` → grey italic (indicator gone quiet) | S02 | formula rule |

Arrow glyph from a number (avoids fighting Excel's icon-set thresholds):

```
=IFS([@impact]>=2,"⇈",[@impact]=1,"↑",[@impact]=0,"↔",[@impact]=-1,"↓",[@impact]<=-2,"⇊")
```

### 2.4 Signal vocabulary (fixed everywhere)

- **Direction:** `↑` up/positive · `↓` down/negative · `↔` neutral · `Mixed` · `↑/↓` context-dependent
- **Inflation:** Inflationary · Disinflationary · Neutral
- **Fed:** Hawkish · Mildly hawkish · Neutral · Mildly dovish · Dovish
- **Risk tone:** Risk-on · Neutral · Risk-off
- **Geo risk:** Low · Moderate · Elevated · High · Crisis
- **Confidence:** Low · Medium · High

Store each list once on **S17 Settings** as a named range and point every dropdown
at it. Change the vocabulary in one place, it updates everywhere.

---

## 3. The four scoring engines

These are the analytical heart. Each is a transparent, weighted formula — no black
box. All weights and thresholds live on **S17 Settings** as named ranges so you can
tune them without touching formulas.

### 3.1 Data-Surprise scoring (the "surprise vs expectations" core)

**Key idea the model must encode:** markets trade the *surprise* (Actual −
Forecast), not the raw level, and the *meaning* of a beat depends on the
indicator's polarity. A hot CPI beat is hawkish; a hot unemployment beat is
dovish/growth-negative. So every indicator carries **polarity flags** in the
Impact Library (S04).

Per-indicator attributes stored in S04:

| Attribute | Range | Meaning |
|-----------|-------|---------|
| `Pol_Infl` | +1 / −1 | does a *higher* print push inflation/Fed **hawkish** (+1, e.g. CPI, wages, ISM prices) or **dovish** (−1, e.g. unemployment, jobless claims)? |
| `Pol_Growth` | +1 / −1 | does a higher print signal **stronger** growth (+1, e.g. NFP, retail sales, GDP) or **weaker** (−1, e.g. unemployment, claims)? |
| `Importance` | 1–5 | market-moving weight (CPI/NFP = 5; durable goods = 2) |
| `SurpriseScale` | number | the "typical" surprise size for that series, used to normalise (e.g. NFP ≈ 50k, CPI m/m ≈ 0.1pp) |

Surprise Engine (S03) columns and formulas (`[@x]` = this-row structured ref):

```
Abs surprise      =[@Actual]-[@Forecast]
% surprise        =IF([@Forecast]=0,"n/a",([@Actual]-[@Forecast])/ABS([@Forecast]))
Std surprise (z)  =IFERROR([@[Abs surprise]]/XLOOKUP([@Indicator],Lib_Name,Lib_Scale),0)
Hot/Cold/Neutral  =IFS(ABS([@z])<0.5,"Neutral",[@z]>0,"Hot","TRUE","Cold")
Inflation signal  =LET(s,[@z]*XLOOKUP([@Indicator],Lib_Name,Lib_PolInfl),
                       IFS(s>0.5,"Inflationary",s<-0.5,"Disinflationary",TRUE,"Neutral"))
Growth signal     =LET(s,[@z]*XLOOKUP([@Indicator],Lib_Name,Lib_PolGrow),
                       IFS(s>0.5,"Growth+",s<-0.5,"Growth−",TRUE,"Neutral"))
Hawkish impulse   =[@z]*XLOOKUP([@Indicator],Lib_Name,Lib_PolInfl)
                     *XLOOKUP([@Indicator],Lib_Name,Lib_Importance)/5      → a −? .. +? number
```

Translate the hawkish/growth impulses into **first-order asset impacts** (−2..+2)
with a small rule set (these are the "usual reaction" — Section 3.4 maps them to
arrows):

```
USD impact     = clamp( 0.6*Hawkish + 0.4*Growth , -2, 2)      ' hawkish & strong US → USD up
UST yield      = clamp( 0.7*Hawkish + 0.3*Growth , -2, 2)      ' hawkish/strong → yields up
UST price      = -[UST yield]                                   ' price is the inverse of yield
Gold           = clamp( -0.8*Hawkish , -2, 2)                   ' real-yield/USD channel
S&P 500        = clamp( 0.5*Growth - 0.5*Hawkish , -2, 2)       ' "good news is bad news" tension
EM             = clamp( 0.4*Growth - 0.6*Hawkish , -2, 2)       ' USD/rates sensitive
GCC/Kuwait     = (mostly oil & USD-peg → pull from S09 oil signal, not data directly)
```

`clamp(x,lo,hi)` in Excel: `=MEDIAN(lo,x,hi)`. Store the 0.6/0.4 style weights as
`SurpWeights` on Settings so they are tunable. The **overall risk tone** of a
release: `=IF(AND([S&P]>=1,[UST yield]<=0),"Risk-on",IF([S&P]<=-1,"Risk-off","Neutral"))`.

### 3.2 Fed hawkish/dovish score

A weighted composite of seven sub-scores, each on a **−2 (very dovish) … +2 (very
hawkish)** scale. Sub-scores 1–3 are pulled from the Surprise Engine; 4 is your
read of Fed communication; 5–7 come from market moves you paste in.

| # | Sub-score | Source | Default weight |
|---|-----------|--------|----------------|
| 1 | Inflation surprises | avg hawkish-impulse of CPI/Core CPI/PCE from S03 | 25% |
| 2 | Labor-market strength | NFP/unemployment/wages/claims impulse from S03 | 20% |
| 3 | Growth strength | GDP/ISM/retail impulse from S03 | 15% |
| 4 | Fed-speech tone | manual −2..+2 (S05 input) | 15% |
| 5 | Market-implied rate change | Δ implied policy path (bps), scaled | 10% |
| 6 | Yield-curve move | 2Y change; bear-flattening = hawkish | 10% |
| 7 | Real-yield move | 10Y real change | 5% |

```
Fed composite  =SUMPRODUCT(Fed_SubScores, Fed_Weights)          ' both are 7-cell named ranges
Fed bias label =IFS(Fed>=1,"Hawkish", Fed>=0.33,"Mildly hawkish",
                    Fed>-0.33,"Neutral", Fed>-1,"Mildly dovish", TRUE,"Dovish")
```

Sub-scores 5–7 convert a raw market move to −2..+2 with a threshold ladder, e.g.
implied path: `=IFS(d>=15,2,d>=5,1,d>-5,0,d>-15,-1,TRUE,-2)` where `d` is the bps
change. `Fed composite` is the single number the Dashboard, Regime Classifier and
Scenario Engine all read (`Score_Fed`).

### 3.3 Geopolitical risk score

Each risk on S08 gets a 0–100 score from its severity, probability and transmission
channels, then an escalation multiplier. Inputs are ordinal (1–5) or a probability.

| Component | Input | Weight |
|-----------|-------|--------|
| Severity | 1–5 | `wSev` 30% |
| Probability | 0–100% | `wProb` 25% |
| Oil-supply proximity | 1–5 | `wOil` 15% |
| Shipping/trade disruption | 1–5 | `wTrade` 10% |
| Inflation channel | 1–5 | `wInfl` 10% |
| Risk-sentiment channel | 1–5 | `wSent` 10% |
| Escalation momentum | −2..+2 | multiplier |

```
Base score  =100*( wSev*([@Severity]/5) + wProb*[@Probability]
                 + wOil*([@Oil]/5) + wTrade*([@Trade]/5)
                 + wInfl*([@Infl]/5) + wSent*([@Sent]/5) )        ' weights are a named range GeoWeights
Momentum    =1 + 0.15*[@Escalation]                               ' +2 → ×1.30, −2 → ×0.70
Risk score  =MEDIAN(0, [@Base]*[@Momentum], 100)
Risk band   =IFS([@Risk]<20,"Low",[@Risk]<40,"Moderate",[@Risk]<60,"Elevated",
                 [@Risk]<80,"High",TRUE,"Crisis")
```

**Aggregate geo score** for the Dashboard — a single crisis should dominate, but
breadth matters too, so blend the worst risk with the average of the top five:

```
Score_Geo =0.6*MAX(Geo_Scores) + 0.4*AVERAGE(LARGE(Geo_Scores,1),LARGE(Geo_Scores,2),
            LARGE(Geo_Scores,3),LARGE(Geo_Scores,4),LARGE(Geo_Scores,5))
```

### 3.4 Asset-class impact scoring

One ordinal scale used by the Reaction Matrix (S10), Scenario Engine (S11), Snapshot
(S16) and Surprise Engine (S03), so everything speaks the same language:

| Number | Arrow | Label |
|--------|-------|-------|
| +2 | ⇈ | Strong positive |
| +1 | ↑ | Positive |
| 0 | ↔ | Neutral |
| −1 | ↓ | Negative |
| −2 | ⇊ | Strong negative |
| (text) | Mixed / ↑↓ | Context-dependent (low confidence) |

Store the reaction matrix as **numbers** (−2..+2) in a hidden helper block, and
display arrows via the `IFS(...)` glyph formula (CF2). That way the matrix is both
human-readable (arrows) and machine-usable (a Scenario pick can average a
portfolio's exposure against the row). Confidence 1–3 sits beside each row and
drives whether the cell shows a clean arrow or a "Mixed" tag:
`=IF([@Confidence]="Low","Mixed", arrow_glyph)`.

### 3.5 Market-regime classifier (fingerprint matching)

Turn nine current signals into one regime label by matching against each regime's
"fingerprint" — the elegant, auditable way (no giant nested IF).

**Current signal vector** (each −1/0/+1), built on S12 from the other engines:

| Signal | Source | −1 / 0 / +1 |
|--------|--------|-------------|
| Inflation trend | S03 avg inflation signal | falling / stable / rising |
| Growth trend | S03 avg growth signal | weak / stable / strong |
| Labor trend | S03 labor block | weakening / stable / strong |
| Fed bias | `Score_Fed` sign | dovish / neutral / hawkish |
| USD trend | S06 | down / flat / up |
| Yield trend | S07 10Y | down / flat / up |
| Oil trend | S09 | down / flat / up |
| Equity sentiment | S07/S15 (SPX, VIX) | risk-off / neutral / risk-on |
| Geo risk | `Score_Geo` band | low / moderate / high(+) |

**Fingerprint matrix** (on S17, rows = regimes, cols = the 9 signals, entries −1/0/+1).
Illustrative fingerprints:

| Regime | Infl | Grow | Labor | Fed | USD | Yield | Oil | Equity | Geo |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Reflation | +1 | +1 | +1 | +1 | 0 | +1 | +1 | +1 | 0 |
| Stagflation | +1 | −1 | −1 | +1 | +1 | +1 | +1 | −1 | +1 |
| Disinflation | −1 | 0 | 0 | −1 | 0 | −1 | −1 | +1 | 0 |
| Goldilocks / Soft landing | −1 | +1 | +1 | 0 | 0 | 0 | 0 | +1 | 0 |
| Hard landing | −1 | −1 | −1 | −1 | +1 | −1 | −1 | −1 | 0 |
| Risk-off | 0 | −1 | 0 | −1 | +1 | −1 | −1 | −1 | +1 |
| Risk-on | 0 | +1 | +1 | 0 | −1 | +1 | +1 | +1 | −1 |
| Oil shock | +1 | −1 | 0 | +1 | +1 | +1 | +1 | −1 | +1 |
| Fed pivot (dovish) | −1 | −1 | −1 | −1 | −1 | −1 | 0 | +1 | 0 |
| Fed tightening | +1 | +1 | +1 | +1 | +1 | +1 | 0 | −1 | 0 |
| Dollar squeeze | 0 | 0 | 0 | +1 | +1 | 0 | −1 | −1 | +1 |
| Growth slowdown | −1 | −1 | −1 | 0 | 0 | −1 | −1 | −1 | 0 |

```
Match score (per regime)  =SUMPRODUCT(Current_Signals, INDEX(Regime_Matrix,row,0))
Best match                =INDEX(Regime_Names, MATCH(MAX(MatchScores), MatchScores, 0))
2nd match (for "risks")   =INDEX(Regime_Names, MATCH(LARGE(MatchScores,2), MatchScores,0))
Conviction                =MAX(MatchScores)/9                     ' 1.0 = perfect fingerprint fit
```

`Regime_Current` (the best match) is the Dashboard headline. The 2nd-best match is
shown as "Risk to the view," and the signals with the largest contribution are the
"Main drivers."

---

## 4. Sheet-by-sheet specification

Each sheet lists: **Purpose · Layout · Columns · Key formulas · Inputs/dropdowns ·
Charts · Links · Example row.**

### S00 — Cover & User Guide
- **Purpose:** front door. What the system is, the colour legend, the 3-layer model,
  a clickable table of contents, "how to update daily/weekly," and the disclaimer
  ("intelligence tool, not investment advice").
- **Layout:** title, legend block, TOC as hyperlinks (`=HYPERLINK("#'S01 Dashboard'!A1","Dashboard")`),
  an "update checklist" (daily / weekly / on-event).
- **Links:** hyperlinks out to every tab. **Charts:** none.

### S01 — Executive Macro Dashboard
- **Purpose:** the one-page answer to all seven questions. Everything here is a link
  or a formula — you never type on this sheet.
- **Layout:** see the cell-grid map in Section 5. Six signal tiles across the top,
  regime + Fed + geo score band, Top-5 risks, Top-5 drivers, "What to watch,"
  executive-summary text box, and a mini cross-asset snapshot.
- **Key formulas / cells:**
  - Regime tile: `=Regime_Current` · conviction `=TEXT(Regime_Conviction,"0%")`
  - Fed tile: `=Fed_Bias_Label` (colour by CF3/CF4)
  - USD/DXY tile: `=sig_DXY_Label` from S06 · Treasury tile from S07 · Gold/Oil from S09/market · Risk sentiment from S15/S07
  - Geo score tile: `=Score_Geo` + band, coloured by 3-colour scale
  - Top-5 risks: `=INDEX(Geo_Name, MATCH(LARGE(Geo_Scores,k), Geo_Scores,0))` for k=1..5
  - Top-5 drivers: top absolute hawkish-impulse rows from S03 via `LARGE` on `ABS(impulse)`
  - What to watch: pulled from S15 triggered rows and S05 upcoming FOMC date
  - Exec summary box: a TEXTJOIN sentence (see cookbook 8.5) that assembles regime +
    Fed bias + top risk + main asset call into English.
- **Charts:** a small "regime gauge" (bar), a DXY/10Y sparkline row, a geo-score bullet.
- **Links:** reads S06, S07, S08, S09, S12, S15, S05, S16. Feeds nothing.

### S02 — Macro Data Tracker
- **Purpose:** the structured log of every macro release you follow.
- **Columns:** `Date · Country/Region · Indicator · Actual · Forecast · Previous ·
  Unit · Frequency · [Surprise] · [Surprise dir] · [Macro interpretation] ·
  [Market implication] · Importance · Source · Notes`. Bracketed columns are
  formulas (mirrors of S03) or pulled from the Library.
- **Key formulas:** `Importance =XLOOKUP([@Indicator],Lib_Name,Lib_Importance)`;
  interpretation & implication `=XLOOKUP([@Indicator],Lib_Name,Lib_Interp_Higher/Lower)`
  chosen by surprise sign. Make it an **Excel Table** (`tblData`) so rows auto-extend.
- **Dropdowns:** Country (`List_Country`), Indicator (`Lib_Name`), Frequency
  (`List_Frequency`), Source (`List_Source`).
- **Charts:** optional surprise-history column chart per indicator (filterable).
- **Links:** feeds S03. Reads S04. **Example row:**
  `14-Jan-2026 · US · CPI y/y · 3.4% · 3.2% · 3.1% · % · Monthly · +0.2pp · Hot ·
  "Inflation hotter than expected" · "Hawkish: USD↑ yields↑ gold↓" · 5 · BLS · —`

### S03 — Data Surprise Engine
- **Purpose:** convert each release into standardized surprise → inflation/growth
  signal → first-order asset impacts. (Section 3.1.)
- **Columns:** `Date · Indicator · Actual · Forecast · Previous · Abs surprise ·
  % surprise · z · Hot/Cold · Inflation signal · Growth signal · Hawkish impulse ·
  USD · UST yld · UST px · Gold · Oil · S&P · EM · GCC · Risk tone · Confidence`.
- **Key formulas:** all in Section 3.1. Asset-impact columns use the `clamp` rules.
- **Charts:** bar of top-10 hawkish impulses (`ABS`), coloured by sign.
- **Links:** reads S02 + S04; feeds S05 (sub-scores 1–3), S12, S01.

### S04 — Indicator Impact Library
- **Purpose:** the reference brain. One row per indicator with its polarity, weight,
  and canned interpretation text that the Tracker/Surprise/Scenario sheets look up.
- **Columns:** `Indicator · What it measures · Why it matters · Higher-than-expected
  read · Lower-than-expected read · Fed impact · USD · UST yields · UST prices ·
  Equities · Gold · Oil · GCC · Pol_Infl · Pol_Growth · Importance · SurpriseScale ·
  Exceptions/context`.
- **Named ranges:** `Lib_Name, Lib_PolInfl, Lib_PolGrow, Lib_Importance, Lib_Scale,
  Lib_USD, Lib_Interp_Higher, Lib_Interp_Lower, ...` (whole-column names on the table).
- **Links:** referenced by S02, S03, S10, S11. Reads nothing. **Example row:**
  `CPI · consumer price inflation y/y · main inflation gauge Fed watches ·
  "Hotter → hawkish, supports USD & yields, pressures bonds & gold, can hurt
  equities" · "Cooler → dovish, supports bonds & gold, risk-on" · +1 hawkish ·
  USD↑ · yields↑ · prices↓ · equities↓ · gold↓ · oil↔ · GCC↔(USD peg) ·
  Pol_Infl +1 · Pol_Growth +1 · Importance 5 · Scale 0.1 · "Watch core vs headline;
  base effects can mislead."`

### S05 — Fed & Central Bank Tracker
- **Purpose:** track policy state + compute the Fed bias score (Section 3.2).
- **Layout:** (a) **State block** — current target range, last FOMC decision & date,
  next FOMC date, market-implied path, expected cuts/hikes, dot-plot direction,
  QT/QToT notes; (b) **Score block** — the 7 sub-scores, weights, composite, label;
  (c) **Speech log** — date · speaker · tone (−2..+2) · quote · takeaway; (d) **Global
  CBs** — ECB/BOE/SNB/BOJ one-line bias each.
- **Key formulas:** `Fed composite =SUMPRODUCT(Fed_SubScores,Fed_Weights)`,
  band via IFS; speech tone average `=AVERAGE(recent tone)` feeds sub-score 4;
  days-to-FOMC `=Next_FOMC-TODAY()`.
- **Dropdowns:** tone (`List_Score5`), direction (`List_Direction`), each CB bias
  (`List_FedBias`).
- **Charts:** implied-rate-path line; sub-score contribution bar.
- **Links:** reads S03; feeds S01, S12, S11, S16.

### S06 — USD Exposure Dashboard
- **Purpose:** explain USD drivers and translate DXY moves into portfolio effects.
- **Layout:** DXY level/trend, driver checklist (rate differential, safe-haven,
  Fed expectations, US-vs-RoW growth) each scored −2..+2, a composite **USD signal**,
  and an impact table (foreign assets, commodities, gold, imported inflation, GCC).
- **Key formulas:** `USD signal =SUMPRODUCT(USD_Drivers,USD_Weights)` → label via IFS;
  `sig_DXY_Label` is what the Dashboard tile reads. Impact rows use XLOOKUP into a
  small USD→asset map.
- **Charts:** DXY line with 50/200-dma if you paste history; driver bar.
- **Links:** reads S05, S03; feeds S01, S10, S12, S13.

### S07 — US Treasury / Bond Module
- **Purpose:** the rates brain — levels, curve, real yields, breakevens, and the
  teaching logic your management asks about.
- **Layout:** (a) **Levels** 2Y/5Y/10Y/30Y with daily/weekly change; (b) **Spreads**
  2s10s, 5s30s (`=UST10−UST2`) with steepening/inverting flag; (c) **Real & breakeven**
  10Y real, 10Y breakeven (`=UST10−real10`); (d) **Driver read** (Fed, inflation,
  growth, risk-off demand) each −2..+2 → yield-direction signal; (e) **Bond impact
  table** (scenario → yield impact → price impact → duration impact → portfolio).
- **Key formulas:** curve `=UST10−UST2`; flag `=IFS(spr>0.1,"Steepening/normal",
  spr<-0.1,"Inverted","Flat")`; price sensitivity `≈ −Duration×Δy` for the impact
  table; yield signal `=SUMPRODUCT(Bond_Drivers,Bond_Weights)`.
- **Teaching cells (static text):** why prices fall when yields rise; how hot
  inflation, Fed hawkishness, recession fear and geo risk each move yields; how
  duration scales sensitivity.
- **Charts:** yield-curve line (2/5/10/30); 2s10s spread over time.
- **Links:** reads S05, S03, S08; feeds S01, S10, S12, S13, S15.

### S08 — Geopolitical Risk Tracker
- **Purpose:** log and score each geopolitical risk (Section 3.3).
- **Columns:** `Risk · Region · Current status · Severity(1-5) · Probability(%) ·
  Oil-proximity(1-5) · Trade(1-5) · Inflation(1-5) · Sentiment(1-5) · Escalation(−2..+2) ·
  [Risk score] · [Band] · Transmission channel · Assets affected · Oil · USD · Gold ·
  Bond · Equity · GCC · What to monitor · Latest update · Notes`.
- **Key formulas:** Section 3.3 (base × momentum → band). Asset-impact cells −2..+2
  → arrows via CF2.
- **Dropdowns:** Region (`List_Region`), status (`List_GeoStatus`), all 1–5 scales
  (`List_1to5`), escalation (`List_Score5`), band auto.
- **Charts:** ranked bar of risk scores (top 10); optional bubble (severity ×
  probability, size = oil-proximity).
- **Links:** feeds S01 (Top-5, `Score_Geo`), S10, S11, S12, S13. **Example row:**
  `Strait of Hormuz closure · Gulf · Elevated tension · Sev 5 · Prob 20% · Oil 5 ·
  Trade 5 · Infl 4 · Sent 4 · Escalation +1 → Risk 63 "High" · "oil supply + shipping"
  · oil⇈ USD↑ gold↑ bonds↑ equities↓ GCC↓(risk)/↑(oil rev, mixed) · "monitor tanker
  traffic, OPEC response" · ...`

### S09 — Oil & Commodity Shock Module
- **Purpose:** decompose oil moves into demand vs supply/geo and read the macro
  consequence — the distinction your brief stresses.
- **Layout:** Brent/WTI level & change, OPEC+ note, inventory trend, a **cause
  selector** (Demand-strong / Demand-weak / Supply-shock / Supply-normalization /
  Geo-premium), and a consequence block that changes with the cause.
- **Key formulas (cause-aware):**
  ```
  Inflation impact =XLOOKUP(Oil_Cause, OilCause_List, OilCause_Infl)
  Growth read      =XLOOKUP(Oil_Cause, OilCause_List, OilCause_Growth)
  Risk tone        =XLOOKUP(Oil_Cause, OilCause_List, OilCause_RiskTone)
  GCC fiscal       =IF(Brent>=GCC_Breakeven,"Supportive","Pressured")&" (breakeven "&GCC_Breakeven&")"
  ```
  So "oil ↑ on supply shock" → Inflationary / Growth− / Risk-off, while "oil ↑ on
  demand" → Neutral-infl / Growth+ / Risk-on. GCC fiscal compares Brent to a
  fiscal-breakeven input.
- **Charts:** Brent vs WTI line; inventory-vs-5yr-range column.
- **Links:** reads S08 (geo premium); feeds S01, S06, S07, S10, S12, S13.

### S10 — Cross-Asset Reaction Matrix
- **Purpose:** the desk's "usual first-order reaction" grid — the market-intuition
  guide (explicitly *not* a fixed prediction model).
- **Layout:** ~19 scenario rows × columns `USD · Gold · Oil · UST price · UST yield ·
  S&P · EM · GCC · Portfolio implication · Confidence · Notes`. Store impacts as
  numbers −2..+2 in a hidden mirror block; display arrows via CF2. A prominent banner:
  *"Usual first-order reaction — context can override; see notes."*
- **Rows:** Hot inflation · Cooling inflation · Fed hawkish surprise · Fed dovish
  surprise · Strong US data · Weak US data · Iran/Gulf escalation · Ukraine/Russia
  escalation · Oil supply shock · Oil demand shock · US recession scare · Risk-on
  rally · Risk-off shock · USD surge · Treasury yield spike · Curve steepening ·
  Curve inversion · China slowdown · Global growth rebound.
- **Context notes (must include):** gold can rise on geo risk but fall when real
  yields & USD rise; oil rises on supply shocks but falls on recession fear; bonds
  rally in risk-off but sell off in inflation shocks; USD rises on both Fed
  hawkishness *and* safe-haven demand; equities like growth but dislike growth that
  delays Fed cuts.
- **Links:** referenced by S11, S13, S16. **Example row:**
  `Oil supply shock → USD ↑ · Gold ↑ · Oil ⇈ · UST price ↔/↓ · UST yield ↔/↑ ·
  S&P ↓ · EM ↓ · GCC Mixed (↑ revenue / ↓ risk) · "inflationary, risk-negative" ·
  Confidence Med · "if demand-driven instead, flip growth read positive."`

### S11 — Scenario Engine
- **Purpose:** pick a scenario from a dropdown, read the full cross-asset + portfolio
  consequence instantly.
- **Layout:** a **scenario selector** (data-validation dropdown, `Sel_Scenario`),
  then a read-out block populated entirely by XLOOKUP into the S10 matrix + a
  scenario-detail table (description, macro interpretation, what to monitor,
  confidence), plus an analyst-comment input box.
- **Key formulas:**
  ```
  Description   =XLOOKUP(Sel_Scenario, Scn_Name, Scn_Desc)
  USD impact    =arrow_glyph( XLOOKUP(Sel_Scenario, Mtx_Row, Mtx_USD) )
  Gold impact   =arrow_glyph( XLOOKUP(Sel_Scenario, Mtx_Row, Mtx_Gold) )   ' …repeat per asset
  GCC impact    =XLOOKUP(Sel_Scenario, Mtx_Row, Mtx_GCC)
  Portfolio     =XLOOKUP(Sel_Scenario, Mtx_Row, Mtx_Portfolio)
  Monitor next  =XLOOKUP(Sel_Scenario, Scn_Name, Scn_Monitor)
  Confidence    =XLOOKUP(Sel_Scenario, Scn_Name, Scn_Conf)
  ```
- **Dropdown:** `Sel_Scenario` = the 21 scenarios in your brief.
- **Charts:** a horizontal bar of the selected row's −2..+2 impacts across assets.
- **Links:** reads S10; feeds S14 (note), S13 (portfolio). Pure output otherwise.

### S12 — Market Regime Classifier
- **Purpose:** compute the current regime by fingerprint match (Section 3.5).
- **Layout:** the 9-signal input/derive column (each pulled from its engine), the
  regime-match score table, and an output block: current regime, conviction, main
  drivers, asset-class implications, risks to the view (2nd match), and "what would
  change the regime" (which signal flips move the match).
- **Key formulas:** Section 3.5 (SUMPRODUCT match, INDEX/MATCH best pick).
- **Charts:** radar/column of the current signal vector; bar of top-3 regime matches.
- **Links:** reads S03, S05, S06, S07, S08, S09; feeds S01, S16.

### S13 — Portfolio Exposure Link
- **Purpose:** connect a macro shock to *your* book. Translate market effect →
  portfolio effect for each exposure bucket.
- **Layout:** rows = exposure buckets (`USD cash/USD-linked · US govt bonds ·
  Equities · Gold · Oil sensitivity · Kuwait/GCC · Foreign-currency translation`);
  columns = `Direct market effect · Portfolio effect · Risk level · Possible benefit ·
  Possible damage · Monitoring item · Suggested analyst comment`. A scenario/regime
  selector at top drives the "direct market effect" via lookups into S10/S11.
- **Key formulas:** effect per bucket `=XLOOKUP(Sel_Scenario, Mtx_Row, Mtx_[asset])`
  mapped to the bucket; risk level `=IFS(ABS(impact)>=2,"High",ABS(impact)=1,"Medium",
  TRUE,"Low")`; benefit/damage are canned text keyed by sign.
- **Links:** reads S10/S11 + the market modules; a pure output for management.
- **Example:** `US govt bonds — direct: yields↑ → prices↓ · portfolio: mark-to-market
  loss, duration risk up · risk High · benefit: higher reinvestment yield · damage:
  price loss on long duration · monitor: 10Y level, Fed path · comment: "Trim
  duration if 10Y breaks range."`

### S14 — Daily/Weekly Market Note Generator
- **Purpose:** assemble a clean, management-ready note from linked cells.
- **Layout:** an **input column** (Date, Main move, Key data, Data surprise, Fed
  implication, USD, Treasury, Gold, Oil, Equity, Geo update, Portfolio implication,
  What to watch) — several of these can auto-fill from S01/S03/S05 — and an **output
  box** that TEXTJOINs them into the 7-point structure.
- **Key formula (the generator):**
  ```
  =TEXTJOIN(CHAR(10),TRUE,
     "Today's Macro Drivers — "&TEXT(Note_Date,"dd mmm yyyy"),
     "1. Market move: "&Note_MainMove,
     "2. Key data: "&Note_KeyData&"  ("&Note_Surprise&")",
     "3. Fed implication: "&Fed_Bias_Label&" — "&Note_FedText,
     "4. Geopolitics: "&Note_GeoText,
     "5. Asset impact: USD "&t_USD&", UST "&t_UST&", Gold "&t_Gold&", Oil "&t_Oil&", S&P "&t_SPX,
     "6. Portfolio implication: "&Note_Portfolio,
     "7. Watch next: "&Note_Watch)
  ```
  (Set the output cell to Wrap Text; `CHAR(10)` gives line breaks.)
- **Links:** reads S01, S03, S05, S15. Copy-paste output into email/Word.

### S15 — Watchlist & Early-Warning Signals
- **Purpose:** a trigger board — is any signal breaching a level that flags a regime
  change?
- **Columns:** `Signal · Current level · Trigger level · Direction · [Triggered?] ·
  Risk signal · Asset implication · Portfolio implication · Comment`.
- **Signals:** sharp DXY move · 10Y breakout · 2Y move · curve inversion/steepening ·
  real-yield spike · gold breakout · oil spike · credit-spread widening · VIX spike ·
  equity drawdown · inflation surprise · weak labor · Fed-speech shift · OPEC+
  surprise · shipping disruption · geo escalation.
- **Key formula:** `Triggered =IF(directional_compare,"⚠ TRIGGERED","ok")` e.g.
  `=IF([@Direction]="Above", IF([@Current]>=[@Trigger],"⚠ TRIGGERED","ok"),
       IF([@Current]<=[@Trigger],"⚠ TRIGGERED","ok"))`. Count `=COUNTIF(...,"⚠*")`
  feeds the Dashboard alert.
- **Conditional formatting:** CF6 red-fills any triggered row.
- **Links:** feeds S01 ("What to watch"), S14.

### S16 — Executive Cross-Asset Snapshot
- **Purpose:** the <1-minute management table — a trimmed, arrow-only version of S10
  for the most important 14 scenarios, plus a copy embedded on the Dashboard.
- **Layout:** 14 rows × `USD · Gold · Oil · UST price · UST yield · S&P · EM · GCC ·
  Portfolio implication · Confidence`, arrows + Positive/Negative/Neutral labels,
  colour-coded. Rows are a subset of S10 pulled by XLOOKUP so there is one source of
  truth.
- **Key formula:** each cell `=arrow_glyph(XLOOKUP([@Scenario],Mtx_Row,Mtx_[asset]))`.
- **Links:** reads S10. Pure output.

### S17 — Settings & Lists
- **Purpose:** single control panel — every dropdown list, every weight, every
  threshold, every fingerprint. Nothing analytical lives elsewhere.
- **Blocks:** (a) **Vocab lists** (Direction, FedBias, RiskTone, Regime, Scenario,
  Country, Region, Frequency, Importance, Confidence, 1to5, Score5, YesNo);
  (b) **Weights** (Fed_Weights, GeoWeights, USD_Weights, Bond_Weights, SurpWeights);
  (c) **Thresholds** (surprise z-bands, Fed bands, geo bands, GCC_Breakeven);
  (d) **Regime_Matrix** (12×9); (e) **OilCause map**.
- **Links:** referenced by every sheet via named ranges. Consider hiding after build.

### S18 — Glossary & Methodology
- **Purpose:** define every term (DXY, real yield, breakeven, 2s10s, QT, dot plot,
  fiscal breakeven, duration, DV01, risk-on/off, carry…) and document each scoring
  methodology so a reviewer or successor can audit the system. Mirrors this spec.

---

## 5. Executive Dashboard layout (cell-grid map)

A 12-column grid (B–M), landscape, fit-to-width. Approximate block placement:

```
Row 1   ┌───────────────────────────────────────────────────────────────────┐
        │  MACRO MARKET INTELLIGENCE — EXECUTIVE DASHBOARD     [as of DATE]   │  title bar
Row 2   │  Regime: <Reflation>  ·  Fed: <Mildly hawkish>  ·  Geo: <Elevated>  │  headline strip
Row 4   ├──────────┬──────────┬──────────┬──────────┬──────────┬────────────┤
        │  REGIME  │   FED    │ USD/DXY  │ 10Y UST  │  GOLD    │   OIL      │  6 signal tiles
Row 5   │ Reflation│ M-hawk ↑ │  ↑ Strong│  ↑ 4.35% │  ↓ soft  │ ⇈ shock    │  (big, colour-coded)
        ├──────────┴──────────┴────┬─────┴──────────┴──────────┴────────────┤
Row 7   │  EQUITY / RISK SENTIMENT │  GEO RISK SCORE:  63 / 100  "High"       │
Row 8   │  Risk-off ↓  (VIX 22)    │  [red 3-colour-scale bar]                │
Row 10  ├─────────────────────────┼──────────────────────────────────────────┤
        │  TOP 5 MACRO RISKS       │  TOP 5 MARKET DRIVERS                     │
Row 11  │  1 Hormuz closure   63   │  1 CPI beat  +0.2pp  (hawkish)            │
  ...   │  2 …                     │  2 …                                      │
Row 17  ├─────────────────────────┴──────────────────────────────────────────┤
        │  WHAT TO WATCH NEXT:  FOMC in 6d · 10Y trigger 4.50% · OPEC+ 5 Feb   │
Row 19  ├───────────────────────────────────────────────────────────────────┤
        │  EXECUTIVE SUMMARY (auto-text): "Regime is Reflation with a mildly   │
        │  hawkish Fed. Main risk is Gulf oil supply (score 63). Base case:    │
        │  USD firm, yields biased up, gold soft, oil bid on geo premium.      │
        │  Portfolio: watch bond duration; GCC oil-revenue positive but risk   │
        │  sentiment negative."                                                │
Row 24  ├───────────────────────────────────────────────────────────────────┤
        │  MINI CROSS-ASSET SNAPSHOT (embed of S16, 6-8 key scenario rows)     │
        └───────────────────────────────────────────────────────────────────┘
```

Tiles use large bold text, the semantic fill from CF3/CF4, and a small trend arrow.
Keep the whole thing to one printed landscape page.

---

## 6. Named ranges master list

Define on S17 unless noted. Table-column names (S02/S03/S04/S08) come free from
Excel Tables.

**Vocab:** `List_Direction, List_FedBias, List_RiskTone, List_Regime, List_Scenario,
List_Country, List_Region, List_Frequency, List_Importance, List_Confidence,
List_1to5, List_Score5, List_YesNo, List_GeoStatus, List_Source, OilCause_List`.

**Library (S04):** `Lib_Name, Lib_PolInfl, Lib_PolGrow, Lib_Importance, Lib_Scale,
Lib_USD, Lib_Yield, Lib_Gold, Lib_Oil, Lib_Interp_Higher, Lib_Interp_Lower`.

**Scores / signals:** `Score_Fed, Fed_Bias_Label, Score_Geo, Geo_Name, Geo_Scores,
Regime_Current, Regime_Conviction, Regime_Names, Regime_Matrix, Current_Signals,
sig_DXY, sig_DXY_Label, sig_UST10, sig_UST2, sig_Gold, sig_Oil, sig_SPX, sig_VIX`.

**Weights/params:** `Fed_Weights, Fed_SubScores, GeoWeights, USD_Weights, USD_Drivers,
Bond_Weights, Bond_Drivers, SurpWeights, GCC_Breakeven, Next_FOMC`.

**Matrix (S10):** `Mtx_Row, Mtx_USD, Mtx_Gold, Mtx_Oil, Mtx_USTpx, Mtx_USTyld,
Mtx_SPX, Mtx_EM, Mtx_GCC, Mtx_Portfolio, Mtx_Conf`.

**Scenario (S11):** `Sel_Scenario, Scn_Name, Scn_Desc, Scn_Monitor, Scn_Conf`.

**Note (S14):** `Note_Date, Note_MainMove, Note_KeyData, Note_Surprise, Note_FedText,
Note_GeoText, Note_Portfolio, Note_Watch, t_USD, t_UST, t_Gold, t_Oil, t_SPX`.

---

## 7. Dropdown lists master list

| Dropdown | Values |
|----------|--------|
| Direction | ↑, ↓, ↔, Mixed, ↑/↓ |
| Fed bias | Hawkish, Mildly hawkish, Neutral, Mildly dovish, Dovish |
| Risk tone | Risk-on, Neutral, Risk-off |
| Regime | Reflation, Stagflation, Disinflation, Soft landing, Hard landing, Risk-on, Risk-off, Dollar squeeze, Oil shock, Fed pivot, Fed tightening, Growth slowdown, Goldilocks |
| Scenario | (the 21 from your brief: Hotter inflation … Treasury rally) |
| Geo band | Low, Moderate, Elevated, High, Crisis |
| 1–5 scale | 1, 2, 3, 4, 5 |
| Score5 | −2, −1, 0, +1, +2 |
| Confidence | Low, Medium, High |
| Frequency | Monthly, Weekly, Quarterly, Daily, Ad hoc |
| Country/Region | US, Eurozone, UK, Japan, China, Global, Kuwait, GCC, EM |
| Oil cause | Demand-strong, Demand-weak, Supply-shock, Supply-normalization, Geo-premium |

Attach via Data → Data Validation → List → `=List_Xxx`.

---

## 8. Formula cookbook

**8.1 XLOOKUP — pull an asset impact for the selected scenario (S11):**
```
=XLOOKUP(Sel_Scenario, Mtx_Row, Mtx_Gold, "n/a")
```

**8.2 INDEX/MATCH — same idea, back-compatible with older Excel (S02 → S04):**
```
=INDEX(Lib_USD, MATCH([@Indicator], Lib_Name, 0))
```

**8.3 IFS — band a score into a label (S05 Fed, S08 geo):**
```
=IFS(Score_Fed>=1,"Hawkish", Score_Fed>=0.33,"Mildly hawkish",
     Score_Fed>-0.33,"Neutral", Score_Fed>-1,"Mildly dovish", TRUE,"Dovish")
```

**8.4 SUMPRODUCT — weighted composites (Fed score, regime match):**
```
Fed:     =SUMPRODUCT(Fed_SubScores, Fed_Weights)
Regime:  =SUMPRODUCT(Current_Signals, INDEX(Regime_Matrix, [@row], 0))
```

**8.5 Top-N without sorting — Dashboard Top-5 risks (S01):**
```
=INDEX(Geo_Name, MATCH(LARGE(Geo_Scores, ROW()-headerRow), Geo_Scores, 0))
```

**8.6 Surprise, normalized (S03):**
```
=IFERROR(([@Actual]-[@Forecast]) / XLOOKUP([@Indicator],Lib_Name,Lib_Scale), 0)
```

**8.7 Arrow glyph from a −2..+2 number (display layer):**
```
=IFS([@n]>=2,"⇈",[@n]=1,"↑",[@n]=0,"↔",[@n]=-1,"↓",[@n]<=-2,"⇊")
```

**8.8 Clamp / bound a computed impact:**
```
=MEDIAN(-2, 0.6*[@Hawkish]+0.4*[@Growth], 2)
```

**8.9 Watchlist trigger (S15):**
```
=IF([@Direction]="Above", IF([@Current]>=[@Trigger],"⚠ TRIGGERED","ok"),
                          IF([@Current]<=[@Trigger],"⚠ TRIGGERED","ok"))
```

**8.10 Conditional-formatting formula rules:**
```
Crisis text →  Applies to =$X5   Rule: =$X5="Crisis"           → red fill
Triggered row → Applies to =$B5:$I5  Rule: =LEFT($F5,1)="⚠"    → red fill
Stale data →   Applies to =$B5:$O5  Rule: =TODAY()-$B5>35      → grey italic
```

**8.11 Exec-summary auto-text (S01) / note generator (S14):** `TEXTJOIN` with
`CHAR(10)` (Section S14). Wrap the concatenations in `IFERROR(...,"—")` so a blank
input never breaks the sentence.

---

## 9. Recommended charts

| Sheet | Chart | Purpose |
|-------|-------|---------|
| S01 | Regime/Fed/Geo mini-gauges + DXY/10Y sparklines | at-a-glance state |
| S03 | Column: top-10 |hawkish impulse| by indicator | what moved this week |
| S05 | Line: market-implied rate path; bar: Fed sub-score contributions | policy read |
| S06 | Line: DXY vs 50/200-dma | USD trend |
| S07 | Line: yield curve (2/5/10/30); line: 2s10s over time | curve shape |
| S08 | Ranked bar of risk scores; bubble severity×probability | risk map |
| S09 | Line: Brent vs WTI; column: inventory vs 5-yr range | oil state |
| S11 | Bar: selected scenario's cross-asset impacts | scenario read |
| S12 | Radar: current 9-signal vector; bar: top-3 regime matches | regime evidence |

Keep charts small, borderless, no gridlines, single-accent colour. Sparklines
(Insert → Sparklines) are ideal for the Dashboard tiles.

---

## 10. Implementation roadmap (build in this order)

**Phase 1 — Foundation (skeleton that already "works"):**
1. S17 Settings — all vocab lists, weights, thresholds, regime matrix.
2. S00 Cover, colour legend, named-range scaffolding.
3. S04 Impact Library — populate ~20 indicators with polarity/importance/text.

**Phase 2 — Input + first engine:**
4. S02 Data Tracker (as an Excel Table).
5. S03 Surprise Engine — surprise math + asset-impact rules.
6. S05 Fed Tracker + Fed score.

**Phase 3 — Market modules:**
7. S06 USD, S07 Bond, S09 Oil, S08 Geo (with their scores).

**Phase 4 — Synthesis engines:**
8. S10 Reaction Matrix (fill the −2..+2 grid + notes).
9. S12 Regime Classifier (fingerprint match).
10. S11 Scenario Engine (dropdown → lookups).

**Phase 5 — Outputs for management:**
11. S13 Portfolio Link, S15 Watchlist, S14 Note Generator.
12. S16 Exec Snapshot, then **S01 Dashboard** last (it only links what now exists).
13. S18 Glossary/Methodology; conditional formatting pass; protect input-only cells.

**Phase 6 — Polish:** charts, sparklines, print areas (fit-to-width landscape),
tab colours by group, freeze panes, final colour/formatting sweep.

Build the Dashboard **last** — it is pure output, so it can only be wired once its
sources exist. If you build it first you will chase broken links.

---

*This is an intelligence and decision-support tool for monitoring macro and
geopolitical risk. Its scores are transparent, weighted heuristics — a structured
way to organise judgement, not a guaranteed predictor of market moves.*
