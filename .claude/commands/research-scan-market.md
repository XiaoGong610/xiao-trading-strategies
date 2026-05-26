---
description: Broad market overview — where is money flowing, what sectors are hot, what's next
---

Run a broad market scan to identify opportunities.

This skill takes no arguments. It provides a high-level market overview before diving into specific sectors or stocks.

Use web search to gather current market data. Cover all sections below, then write the **Action Summary** first in the output (even though it's listed first, write it last after completing the full analysis).

## Action Summary

Start every scan output with a 5-line TL;DR. This is the single most important section — the user should get the answer in 10 seconds.

- **Regime:** [regime name] — [one-line positioning guidance]
- **Focus on:** [top 2-3 sectors/themes to research next, with lifecycle stage]
- **Avoid:** [sectors to skip and why, in a few words]
- **Key risk:** [the biggest thing that could go wrong right now]
- **Next catalyst:** [the most important upcoming event + date]

## Market Regime

Classify the current market environment. This frames everything below.

| Factor | Reading | Signal |
|--------|---------|--------|
| S&P 500 vs. 50/200 SMA | Above/below | Trend direction |
| VIX level | Current | <15 complacent, 15-20 normal, 20-30 elevated, >30 fear |
| Fear & Greed Index (CNN) | 0-100 | 0-25 extreme fear (contrarian buy), 25-45 fear, 45-55 neutral, 55-75 greed, 75-100 extreme greed (contrarian sell) |
| Yield curve (2Y-10Y) | Spread | Inverted = recession risk |
| Market breadth | % stocks above 200 SMA | >60% healthy, 40-60% mixed, <40% weak (200 SMA ≈ 1 trading year — the institutional standard for long-term trend; broad participation above it = healthy market, narrow = fragile rally) |

**Regime:** [pick one]
- **Strong Uptrend** — broad participation, low vol → full offense (Buy & Hold, LEAPs, DCA)
- **Uptrend** — trending up but selective → normal positioning
- **Choppy / Range-bound** — no clear direction → theta gang thrives, reduce size
- **Correction** — pullback in uptrend → look for support entries, DCA opportunities
- **Downtrend** — sustained selling, weak breadth → cash priority, defensive only

## Market Pulse
- S&P 500, Nasdaq, Russell 2000 recent performance (1-week, 1-month, YTD)
- Market sentiment: fear/greed index, VIX level and trend
- Macro backdrop: Fed policy, inflation, rates, any geopolitical events affecting markets

## Sector Rotation

**Generate the sector heatmap first** for a visual overview:
```bash
.venv/bin/python3 scripts/sector-heatmap.py --no-open
```
This saves an interactive treemap to `charts/sector-heatmap.html` with period toggle buttons (1-Week through 1-Year). Reference it in the analysis below.

**How to read the heatmap:**
- Each block = one GICS sector (represented by its ETF, e.g., XLK = Technology)
- Color = performance over the selected period: **green** = positive return (outperforming), **red** = negative return (underperforming), gray = flat
- Deeper color = stronger move. Hover for exact % change and current price.
- Use the period buttons at the top to toggle between timeframes — compare 1-week vs. YTD to spot rotation shifts.

Where is money flowing right now? Show a sector performance table:

| Sector | 1-Week | 1-Month | YTD | Trend | Notable Movers |
|--------|--------|---------|-----|-------|----------------|

Identify:
- **Leading sectors** — outperforming, money flowing in
- **Lagging sectors** — underperforming, but watch for rotation opportunities
- **Turning sectors** — showing early signs of reversing (either topping out or bottoming)

## Volatility & Options Landscape
- VIX level and trend — is volatility elevated or depressed?
- Any upcoming macro events that could move markets (FOMC, jobs report, CPI, earnings season)?
- Which sectors have elevated IV right now? (opportunities for theta gang)

## Hot Themes

For each theme, assess the lifecycle stage:

| Theme | Stage | Heat | Key Stocks | What's New |
|-------|-------|------|-----------|------------|
| e.g., AI Infrastructure | Accelerating | High | NVDA, AVGO | Data center capex rising |

**Stage:** Emerging / Accelerating / Trending / Mature / Exhausting
**Heat:** How much attention and capital is flowing (High / Medium / Low)

Signs of exhaustion to watch for: multiple ETFs launched, mainstream media saturation, retail crowding, "everyone owns it."

- Contrarian opportunities — sectors/themes that are hated but could be turning

## Anomaly Watch

Flag anything where the market reaction doesn't match expectations. These are often the most informative signals.

Examples:
- Good earnings but stock sold off → market already priced in, or hidden concern
- Bad macro data but market rallied → market looking past it, bullish undertone
- Sector divergence from broad market → rotation signal

If no anomalies observed, note "No significant anomalies this scan."

## Sector Recommendations

Rank 3-5 sectors to investigate further:

| Priority | Sector/Theme | Why | Lifecycle Stage | Next Step |
|----------|-------------|-----|-----------------|-----------|
| 1 | ... | ... | ... | `/research-scan-sector SECTOR` |
| 2 | ... | ... | ... | `/research-scan-sector SECTOR` |
| 3 | ... | ... | ... | `/research-scan-sector SECTOR` |

Be opinionated — don't just list everything. Focus on what's actionable right now. Prefer Emerging/Accelerating themes over Mature/Exhausting ones. The user may pursue any strategy (buy-and-hold, DCA, theta gang, swing trading), so keep recommendations strategy-agnostic.

Save the output to `research/sectors/market-overview.md`.
Start the entry with a date separator: `---` followed by `# Market Overview | YYYY-MM-DD`.
If the file already exists, prepend the new scan above all previous entries. Never remove historical entries.
