# Execution Framework

How to turn a trade plan into specific orders. Every `/plan-stock` output should end with an execution plan that specifies exact order types, prices, and sizes.

## The Three Phases of Execution

Every trade has three phases. Plan ALL THREE before placing the first order.

```
ENTRY (how to get in)
  → PROTECTION (how to limit downside)
    → EXIT (how to take profits or cut losses)
```

Skipping any phase = gambling, not trading.

---

## Phase 1: Entry Strategy Selection

### Decision Matrix

Two inputs: **sector momentum** (urgency) and **price location** (opportunity).

| | At/Near Support | Mid-Range | Extended / Near ATH |
|---|---|---|---|
| **Accelerating Sector + Catalyst <14 days** | Market buy or tight limit (within 0.5 ATR) | Market buy — don't wait for a dip that may not come | Small market buy (30%), scaled limits below for rest |
| **Accelerating Sector + No Near Catalyst** | Limit at support (GTC) | Daily DCA | Daily DCA at half-pace |
| **Steady/Pulling Back Sector** | Scaled limits at support levels | Daily DCA | Limit orders 1-2 ATR below current |
| **Sideways/Choppy Sector** | Limit at range bottom or CSP | Small DCA only | Don't enter — wait for direction |
| **Downtrend/Capitulation + High Conviction (>=8)** | Scaled deep limits at major supports | Small DCA at half-pace | Don't enter |
| **Downtrend/Capitulation + Low Conviction (<8)** | Don't enter — set price alerts only | Don't enter | Don't enter |

### Entry Types

| Type | How It Works | Best For | Downside |
|------|-------------|----------|----------|
| **Market buy** | Buy immediately at current ask | Urgency, pre-catalyst, small positions | No price control — may overpay in volatile markets |
| **Limit buy** | Buy only at your specified price or lower (GTC) | Waiting for support, patient entry | May never fill — stock runs away without you |
| **Scaled limits** | 3-5 limit orders at descending prices | High conviction, uncertain timing | Capital tied up in multiple orders |
| **Stop-limit buy (breakout)** | Buy only if stock rises ABOVE a price | Confirmation — buy strength after a breakout | May chase if breakout fails (bull trap) |
| **Daily DCA (recurring)** | Fixed dollar amount every day | Long-term accumulation, removes emotion | No price optimization — buys at any level |
| **CSP entry** | Sell a put — get paid to wait for your price | High IV + at support + happy to own at strike | Requires cash collateral, assignment risk |

### Price Level Determination

Use `technicals.py` output to set specific prices:

| Level | Source | When to Use |
|-------|--------|-------------|
| **SMA 20** | Short-term trend average | First pullback target in uptrend |
| **SMA 50** | Medium-term trend | Standard support in healthy uptrend |
| **SMA 200** | Long-term trend | Major support — breaks here = trend change |
| **Support levels** | Prior lows, consolidation zones | Natural buying interest — orders cluster here |
| **Volume Profile HVN** | High Volume Node — price with most trading activity | Price "magnet" — tends to pull back here |
| **Bollinger Lower Band** | 2 std deviations below 20-day mean | Statistical oversold — mean reversion target |
| **52W Low** | Annual floor | Maximum fear entry — only for highest conviction |
| **ATR-adjusted levels** | Support minus 1 ATR | Accounts for normal daily noise — avoids getting stopped by routine volatility |

### Scaled Order Spacing

Use **ATR** (Average True Range) to space orders — it reflects the stock's normal daily movement.

```
Entry 1: Nearest support level (SMA or prior low)
Entry 2: Entry 1 minus 1 ATR
Entry 3: Entry 2 minus 1 ATR

Default sizing: 40% / 30% / 30%
Aggressive sizing: 50% / 30% / 20%
Conservative sizing: 30% / 30% / 40% (more at lower levels)
```

**Example — NVDA ($211, ATR $8.49):**
- Entry 1: $195 (support level) — 40%
- Entry 2: $186 ($195 - $8.49 ATR) — 30%
- Entry 3: $178 ($186 - $8.49 ATR) — 30%

### DCA Pacing Rules

| Condition | Pace | Why |
|-----------|------|-----|
| Sector Accelerating + Stock RSI 30-60 | Full pace ($100/day) | Momentum supports buying |
| Sector Accelerating + Stock RSI >70 | Half pace ($50/day) | Overbought — slow down |
| Sector Downtrend + Stock RSI >50 | Half pace | Don't fight sector headwinds at full speed |
| Sector Downtrend + Stock RSI <30 | Full pace (contrarian) | Capitulation = accumulation zone |
| Earnings <7 days | Half pace or pause | Reduce binary event exposure |
| Stock >20% above SMA20 | Half pace | Extended — likely to mean-revert |

---

## Phase 2: Protection Strategy Selection

### Decision Matrix

Based on **position size** (% of portfolio) and **gain status** (how much you're up/down).

| | Gain >50% | Gain 0-50% | Loss 0-20% | Loss >20% |
|---|---|---|---|---|
| **>15% of portfolio** | Trailing stop OR collar — MANDATORY | Trailing stop | Hard stop at thesis invalidation | Review thesis — exit if broken |
| **5-15% of portfolio** | Trailing stop recommended | Stop at thesis invalidation | Stop at thesis invalidation | Review thesis |
| **<5% of portfolio** | Mental stop — monitor weekly | Mental stop | Mental stop | Mental stop or accept small loss |

### Protection Types

| Type | How It Works | Best For | Cost |
|------|-------------|----------|------|
| **Hard stop loss** | GTC sell order at a fixed price | Clear invalidation level (below SMA, below support) | Free — but can get triggered by intraday noise |
| **Trailing stop (%)** | Stop follows price up, triggers on X% pullback | Riding momentum winners | Free — but wide % needed to avoid noise |
| **Trailing stop ($)** | Stop follows by fixed dollar amount | Lower-priced stocks where % is misleading | Free |
| **Protective put** | Buy a put option for insurance | Can't sell shares (tax, RSU, lockup) but want protection | Premium cost (typically 2-5% of position) |
| **Collar** | Buy put + sell call = near-zero cost hedge | Large winner you want to protect without paying premium | Free (put cost offset by call income) but caps upside |
| **Mental stop** | No order — review at price level, decide then | Small positions, high-conviction long-term holds | Free — but requires discipline to actually execute |

### Stop Loss Placement

**The ATR method** — prevents getting stopped out by normal daily noise:

```
Conservative stop: 2.0x ATR below entry (wider, fewer false triggers)
Standard stop:     1.5x ATR below entry (balanced)
Tight stop:        1.0x ATR below entry (more responsive, more whipsaws)
```

**The SMA method** — uses trend structure:
```
Uptrend (above all SMAs):     Stop below SMA 50
Neutral (mixed SMAs):          Stop below SMA 200
Downtrend (below all SMAs):    Stop below 52W low or don't enter
```

**Combine both:** Use the HIGHER of ATR-stop and SMA-stop. This ensures your stop respects both volatility and trend structure.

**Example — TSLA ($400, ATR ~$20):**
- ATR stop (1.5x): $400 - $30 = $370
- SMA stop: SMA50 at ~$350
- Combined: use $350 (higher structural level)
- Trailing: 12% from current high = $352 (close to SMA50, good alignment)

### When NOT to Use Stops

- **Daily DCA accumulation phase** — you're buying every day, a stop would fight your own strategy
- **Deep value / contrarian plays** — stock is already beaten down, a stop creates permanent loss at the worst level
- **Options positions** — risk is already defined (premium = max loss)
- **Tax-locked positions** — selling triggers undesirable tax events (use protective puts instead)

---

## Phase 3: Exit Strategy Selection

### Decision Matrix

Based on **why you own it** and **what's happening now**.

| Scenario | Exit Type | Implementation |
|----------|-----------|---------------|
| Hit your price target | **Limit sell (full or partial)** | Set GTC limit sell when entering the trade |
| Momentum stock still running | **Trailing stop** | Let profits run, auto-exit on reversal |
| Taking profits in tranches | **Scaled sells** | 25% at target 1, 25% at target 2, hold 50% |
| Income position (CC) | **Let assignment happen** | Stock called away at strike = planned exit |
| Thesis broke (fundamental) | **Market sell immediately** | Don't negotiate with a broken thesis |
| Time-based deadline | **Calendar exit** | Close on X date regardless of price |
| Post-catalyst review | **Manual review** | Evaluate post-event, decide then |

### Exit Types

| Type | How It Works | Best For |
|------|-------------|----------|
| **Limit sell (target)** | GTC sell at a predefined profit target | Clear valuation target or resistance level |
| **Scaled sells** | Multiple sell orders at ascending prices | Large positions — take profits gradually |
| **Trailing stop sell** | Auto-sell on X% pullback from highest point | Momentum stocks — let winners run |
| **Covered call exit** | Sell CC at a price you're happy to sell at | Income + planned exit above cost basis |
| **Market sell** | Sell immediately at current bid | Thesis broken, urgent exit |
| **Time stop** | Close position on a specific date | LEAPs approaching expiry, thesis has a deadline |
| **Catalyst exit** | Pre-defined: "if X happens, I sell" | Earnings, FDA, regulatory decisions |

### Profit Target Setting

| Method | How to Calculate | When to Use |
|--------|-----------------|-------------|
| **Analyst consensus** | Average 12-month price target | Default for most positions |
| **Resistance level** | Next technical resistance from technicals.py | Short-term swing trades |
| **Valuation-based** | Fair PE × estimated EPS | When you have a specific valuation thesis |
| **% return target** | Fixed % gain (e.g., +30%) | Simple, works when you don't have a price thesis |
| **Risk/reward ratio** | Target = entry + 2x(entry - stop) | Ensures every trade has at least 2:1 reward:risk |

### Scaled Exit Template

For large winners or concentrated positions:

```
25% at Target 1 (analyst consensus or first resistance)
25% at Target 2 (stretch target or second resistance)
25% via trailing stop (let it run)
25% hold indefinitely (core position / compounder)
```

---

## Putting It All Together: Execution Plan Template

Every `/plan-stock` should output this at the end. Keep it **account-agnostic** — specify target allocation and order types/prices, but let the user decide which account to use.

```
## Execution Plan

Target allocation: Y% of total portfolio (based on conviction Z/10)
Current allocation: X% — [underweight/on-target/overweight]

### Entry
- Strategy: [Market buy / Limit buy / Scaled limits / DCA / CSP / Breakout buy]
- Orders:
  - Order 1: [type] [size%] at $X — [rationale: SMA support, prior low, etc.]
  - Order 2: [type] [size%] at $X — [rationale]
  - Order 3: [type] [size%] at $X — [rationale]
- DCA: $X/day [full/half pace] — [duration or "ongoing"]
- Order duration: GTC / cancel after X days

### Protection
- Stop type: [Hard stop / Trailing stop / Collar / Protective put / Mental stop]
- Stop level: $X (-Y% from entry) — [rationale: below SMA, 1.5x ATR, thesis invalidation]
- Reassess if: [condition that triggers review without auto-exit]

### Exit
- Target 1: $X (+Y%) — [sell Z%, rationale: analyst target, resistance]
- Target 2: $X (+Y%) — [sell Z%, rationale: stretch target]
- Trailing stop: X% from high — [for remaining position after targets hit]
- Time stop: [date] — [reassess or close if no progress]
- Thesis killer exit: [specific event that means immediate exit]

### Risk Check
- Risk/reward ratio: [reward ÷ risk, minimum 2:1]
- Max loss at stop: $X (Z% of portfolio)
```

---

## Position Sizing via Risk

**The 2% rule:** Never risk more than 2% of total portfolio on a single trade.

```
Position size = (Portfolio × 2%) ÷ (Entry price - Stop price)

Example:
- Portfolio: $746,000
- 2% risk: $14,920
- Entry: $211 (NVDA)
- Stop: $175
- Risk per share: $36
- Max shares: $14,920 ÷ $36 = 414 shares ($87,354)
```

This tells you the MAXIMUM position, not the target. For DCA positions built over weeks, the effective risk is lower because you average in — but always know your max loss scenario.

**Conviction-based target allocation:**

| Conviction | Target Allocation (% of total portfolio) | DCA Pace |
|-----------|------------------------------------------|----------|
| 9-10 | 5-8% | Full pace |
| 7-8 | 3-5% | Full pace |
| 5-6 | 1-3% | Half pace |
| <5 | 0-1% (or don't enter) | Quarter pace or alerts only |

This table drives the "Target allocation" line in every `/plan-stock` execution plan. Compare target vs. current allocation to determine whether you're underweight (add), on-target (hold), or overweight (trim).

---

## Quick Reference: Common Mistakes

1. **No stop on a concentrated position.** If one stock is >10% of portfolio and you have no exit plan, you're gambling with house money.
2. **Stops too tight.** A stop inside 1 ATR will get triggered by routine daily movement. Use 1.5-2x ATR minimum.
3. **No profit target.** "I'll sell when it feels right" = you'll never sell. Set targets before entering.
4. **Limit orders too far from current price.** A limit 20% below current on a stock in an uptrend will never fill. Use 1-2 ATR below, not arbitrary round numbers.
5. **Ignoring ATR.** A $500 stock with ATR $50 (10%) needs MUCH wider stops than a $500 stock with ATR $10 (2%). Always calibrate to the stock's actual volatility.
6. **Same-day stops and entries.** Place your stop AFTER your entry fills, not simultaneously. If your limit buy fills at the day's low, a tight stop might trigger immediately on the bounce.
7. **Trailing stops too tight in volatile names.** High-beta stocks (MU, TSLA, AMD) routinely swing 5-8% intraday. A 5% trailing stop = constant whipsaws. Use 12-15% for volatile names.
