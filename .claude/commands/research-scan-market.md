---
description: Broad market overview — where is money flowing, what sectors are hot, what's next
---

Run a broad market scan to identify opportunities.

This skill takes no arguments. It provides a high-level market overview before diving into specific sectors or stocks.

Use web search to gather current market data. Cover all sections below, then write the **Action Summary** first in the output (even though it's listed first, write it last after completing the full analysis).

## Action Summary

Start every scan output with a 5-line TL;DR. This is the single most important section — the user should get the answer in 10 seconds.

- **Regime:** [regime name] — [one-line positioning guidance]
- **Playbook:** [what strategies work in this regime — e.g., "Buy strength in accelerating sectors, DCA in pulling-back sectors, theta gang in sideways sectors"]
- **Focus on:** [top 2-3 sectors/themes to research next, with momentum classification]
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
| CAPE (Shiller P/E) | Current | <20 cheap, 20-25 fair, 25-35 expensive, >35 extreme — see `knowledge/frameworks/valuation.md` |
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

**Generate the sector heatmap and momentum dashboard first:**
```bash
.venv/bin/python3 scripts/sector-heatmap.py --no-open
.venv/bin/python3 scripts/sector-momentum.py
```
The heatmap (`charts/sector-heatmap.html`) shows visual performance. The momentum dashboard provides quantitative signals: Mansfield RS (vs S&P 500), Weinstein Stage (1-4), ROC, and momentum classification for each sector. Use both in the analysis below.

**How to read the heatmap:**
- Each block = one GICS sector (represented by its ETF, e.g., XLK = Technology)
- Color = performance over the selected period: **green** = positive return (outperforming), **red** = negative return (underperforming), gray = flat
- Deeper color = stronger move. Hover for exact % change and current price.
- Use the period buttons at the top to toggle between timeframes — compare 1-week vs. YTD to spot rotation shifts.

Where is money flowing right now? Show a sector performance table with momentum classification:

| Sector | 1-Week | 1-Month | YTD | Momentum | Notable Movers |
|--------|--------|---------|-----|----------|----------------|

**Momentum classification** (based on 1-week and 1-month performance):
- **Accelerating Up** (1W>0, 1M>0, beating S&P) → buy strength, momentum entries work
- **Steady Uptrend** (1W>0, 1M>0) → normal DCA, buy support
- **Pulling Back** (1W<0, 1M>0) → best dip-buy window
- **Sideways** (1W~0, 1M~0) → theta gang territory
- **Downtrend** (1W<0, 1M<0) → slow accumulation only
- **Capitulation** (1W<0, 1M<0, oversold) → contrarian buy if thesis intact

Identify:
- **Accelerating sectors** — outperforming, money flowing in → ride the momentum
- **Pulling-back sectors** — dipping in an uptrend → best entry window
- **Turning sectors** — showing early signs of reversing (either topping out or bottoming)

## Volatility & Options Landscape
- VIX level and trend — is volatility elevated or depressed?
- Any upcoming macro events that could move markets (FOMC, jobs report, CPI, earnings season)?
- Which sectors have elevated IV right now? Consult `knowledge/signals/iv-rank-guide.md` for thresholds: IV Rank >50 = theta gang opportunities, IV Rank <25 = LEAPs territory

## Hot Themes

**For AI-related themes**, consult `knowledge/frameworks/capital-flow.md` to identify which track in the AI supply chain is at the inflection point (GPU → HBM → Networking → Power → ASIC). Position ahead of the bottleneck shift, not after it re-rates.

**If crypto is a relevant theme**, run the on-chain cycle dashboard and consult the framework:
```bash
.venv/bin/python3 scripts/crypto-cycle.py
```
Reference `knowledge/frameworks/crypto-cycles.md` for cycle positioning (MVRV, NUPL, composite score). Note where we are in the 4-year halving cycle and implications for crypto-adjacent stocks (COIN, MSTR, GLXY).

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
