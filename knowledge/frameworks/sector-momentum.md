# Sector Momentum Framework

How we measure sector momentum and translate it into trading strategy.

## Three Pillars

Our sector momentum analysis combines three proven frameworks. No single indicator is reliable alone — we use all three for confirmation.

### 1. Mansfield Relative Strength (MRS)

**Source:** Stan Weinstein's "Secrets for Profiting in Bull and Bear Markets"

**What it measures:** Whether a sector is outperforming or underperforming the S&P 500, normalized against its own history.

**Formula:**
```
RP = sector_price / SPY_price
MRS = ((RP / SMA(RP, 200)) - 1) × 100
```

**How to read:**
- **MRS > +5:** Strong outperformance — money flowing INTO this sector
- **MRS +2 to +5:** Moderate outperformance — sector is healthy
- **MRS -2 to +2:** In line with market — no edge
- **MRS -2 to -5:** Moderate underperformance — money flowing OUT
- **MRS < -5:** Strong underperformance — avoid or contrarian opportunity

**Why it matters:** MRS strips out market-wide moves. A sector can be down 5% and still have positive MRS if the market is down 10%. It shows where institutional money is rotating, not just absolute performance.

### 2. Weinstein Stage Analysis

**Source:** Stan Weinstein's 4-stage model, adapted for sector ETFs.

**What it measures:** The structural trend phase using price vs. 30-week (150-day) SMA and SMA slope.

| Stage | SMA Slope | Price vs. SMA | Meaning | Action |
|-------|-----------|---------------|---------|--------|
| **Stage 1 (Basing)** | Flat | Near SMA | Accumulation — smart money buying quietly | Watch for breakout |
| **Stage 2 (Advancing)** | Rising | Above SMA | Uptrend — confirmed, ride the wave | Buy, hold, add on dips |
| **Stage 3 (Distribution)** | Flattening | Crossing SMA | Topping — smart money selling into strength | Trim, tighten stops |
| **Stage 4 (Declining)** | Falling | Below SMA | Downtrend — avoid or short | Sell, avoid new entries |

**Weinstein's key rule:** Only buy Stage 2 stocks in Stage 2 sectors in a Stage 2 market. A stock breaking out of Stage 1 in a Stage 4 sector has low odds of success.

### 3. Rate of Change (ROC) Momentum

**What it measures:** The speed and direction of price change over multiple timeframes.

**Timeframes:**
- **1-week ROC:** Short-term momentum — is the sector accelerating or decelerating right now?
- **1-month ROC:** Intermediate momentum — the primary signal for entry timing
- **3-month ROC:** Medium-term trend — confirms whether the move has legs

**How the pattern tells a story:**

| 1W ROC | 1M ROC | 3M ROC | Pattern | Interpretation |
|--------|--------|--------|---------|---------------|
| + | + | + | All positive | Strong uptrend — momentum on all timeframes |
| - | + | + | Short-term dip | Pullback in an uptrend — best buying window |
| + | + | - | Early reversal | Bottoming — new uptrend forming |
| + | - | - | Dead cat bounce | Bear market rally — don't trust it |
| - | - | - | All negative | Downtrend — avoid or accumulate slowly |

## Momentum Classification

We combine all three pillars into a single actionable classification:

| Classification | Criteria | Strategy |
|---------------|----------|----------|
| **Accelerating Up** | 1W>0, 1M>0, MRS>+2, Stage 2 | Buy strength — momentum carries higher. Trail stops. |
| **Steady Uptrend** | 1W>0, 1M>0, Stage 2 | Normal DCA. Buy support tests. Standard sizing. |
| **Pulling Back in Uptrend** | 1W<0, 1M>0, Stage 2 | **Best entry window.** Buy the dip. Accelerate DCA. CSP at support. |
| **Sideways** | 1W~0, 1M~0, Stage 1 or 3 | Theta gang. Sell premium. No directional bets. |
| **Downtrend** | 1W<0, 1M<0, MRS<-2, Stage 4 | Slow DCA only. Save cash. Wait for Stage 1 basing. |
| **Capitulation** | 1W<0, 1M<0, RSI<30, Stage 4 | Contrarian buy if thesis intact. Aggressive once basing confirmed. |

## How This Connects to `/plan-stock`

The sector momentum classification is the FIRST input to strategy selection in `/plan-stock` Phase 4a. It overrides stock-level RSI when they conflict:

- **Sector Accelerating + Stock RSI 75** → Buy a starter. The sector wave carries it higher.
- **Sector Sideways + Stock RSI 75** → Wait. No sector tailwind = overextension.
- **Sector Downtrend + Stock RSI 25** → Slow DCA. The stock is cheap but the sector is against you.

The key insight: **a stock's RSI only tells you its own story. Sector momentum tells you whether the wind is at your back.**

## Running the Analysis

```bash
.venv/bin/python3 scripts/sector-momentum.py              # all sectors
.venv/bin/python3 scripts/sector-momentum.py --sector XLK  # single sector
.venv/bin/python3 scripts/sector-momentum.py --json        # for programmatic use
```

The script computes all three pillars automatically from yfinance data (free, no API key).
