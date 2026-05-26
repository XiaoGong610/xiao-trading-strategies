# Valuation Benchmarks

## Market-Level: CAPE (Shiller P/E)

**CAPE** (Cyclically Adjusted Price-to-Earnings) = S&P 500 price / average of the last 10 years of inflation-adjusted earnings. Created by Nobel laureate Robert Shiller.

Unlike regular P/E which uses a single year of earnings (noisy, distorted by business cycles), CAPE smooths over a full decade to reveal whether the overall market is cheap or expensive relative to its long-term earning power.

| CAPE Level | Signal | Historical Context |
|-----------|--------|-------------------|
| <15 | Cheap — historically strong forward returns | Post-crash bottoms (2009, 1982, 1932) |
| 15-20 | Fair value | Long-term average is ~17 |
| 20-25 | Moderately expensive — positive but lower returns | Most of the 2010s |
| 25-35 | Expensive — muted forward returns | 2017-2024 range |
| 35-40 | Very expensive — thin margin of safety | Great Depression peak (~35), 2025-2026 |
| 40+ | Extreme — only dot-com bubble reached 44 | January 2000 peak |

**How to use CAPE:**
- **Not a timing tool** — CAPE can stay elevated for years. High CAPE doesn't mean "sell now"
- **A positioning tool** — high CAPE = be selective, size down, tighten stops. The margin of safety is thin, so any negative surprise hits harder
- **Forward return predictor** — historically, CAPE >30 has led to below-average 10-year returns. CAPE <15 has led to above-average returns. The relationship is strong over decades, weak over months
- **Regime context** — in `/research-scan-market`, CAPE adds to the regime assessment. CAPE near 40 + low VIX + Greed sentiment = complacency at extreme valuations

**CAPE limitations:**
- Structurally higher today due to tech dominance (higher-margin businesses than the historical average)
- Share buybacks reduce share count and inflate per-share earnings, distorting comparisons to pre-2000 data
- Interest rates matter: CAPE of 30 at 1% rates is different from CAPE of 30 at 5% rates

**Quick rule:** When CAPE >35, every `/plan-stock` should note the elevated market valuation as a risk factor and consider smaller position sizes.

---

## Forward P/E by Sector

Not all P/E ratios are created equal. A 30x P/E means different things in different sectors.

| Sector | Cheap | Fair | Expensive | Notes |
|--------|-------|------|-----------|-------|
| Energy (E&P) | < 10x | 10-15x | > 20x | Cyclical — cheap at cycle peak can be a trap |
| Energy (Midstream/LNG) | < 12x | 12-18x | > 25x | Toll-model = more predictable, deserves slight premium |
| Semiconductors (mature) | < 15x | 15-25x | > 35x | TXN, QCOM, INTC type |
| Semiconductors (growth) | < 25x | 25-50x | > 60x | AMD, AVGO, MRVL — growth justifies premium |
| Semiconductors (hyper-growth) | < 40x | 40-80x | > 100x | CRDO, ALAB — 100%+ growth, priced for perfection |
| Software (mature SaaS) | < 20x | 20-35x | > 45x | CRM, NOW, ADBE |
| Software (high-growth) | < 35x | 35-60x | > 80x | DDOG, CRWD, PLTR |
| Healthcare (large pharma) | < 12x | 12-18x | > 25x | LLY is an exception due to GLP-1 growth |
| Healthcare (biotech) | < 15x | 15-25x | > 35x | Often negative earnings — use P/S instead |
| Industrials | < 18x | 18-30x | > 40x | GEV, ETN — AI infra premium justified? |
| Consumer (FAANG) | < 18x | 18-30x | > 40x | META, GOOG, AMZN |

## When Cheap P/E is NOT a Buy Signal

1. **Cyclical peak** — earnings are temporarily inflated (energy at oil highs, memory at NAND price peaks). P/E looks cheap but earnings will decline.
2. **Declining business** — cheap because growth is negative. Market is right to discount.
3. **One-time earnings bump** — non-recurring items inflating EPS.
4. **Geopolitical discount** — Chinese stocks, Russia-exposed. Cheap for a reason.

## When Expensive P/E is Justified

1. **Accelerating growth** — PEG ratio < 1 (P/E divided by growth rate). 50x P/E with 60% growth = PEG 0.83 = reasonable.
2. **Winner-take-all dynamics** — monopoly/duopoly positions (NVDA in AI GPUs, ASML in EUV).
3. **Platform economics** — network effects create compounding returns (META, GOOG).
4. **Secular tailwind** — multi-year demand cycle that won't slow (AI infrastructure 2024-2030).

## Quick Decision Rule

**RSI + Fwd P/E combo:**
| | Cheap P/E | Fair P/E | Expensive P/E |
|---|-----------|----------|---------------|
| **Oversold RSI** | Strong buy | Buy | Investigate why |
| **Neutral RSI** | Accumulate | Normal DCA | Reduce position |
| **Overbought RSI** | Wait for pullback, then buy | Wait | Avoid |
