# When to Harvest — Exit & Profit-Taking Framework

**Status: DRAFT — theory and research compiled Aug 15, 2026. Not yet integrated into skills.**

## Core Principle

Different instruments have different exit logic. The biggest mistake is applying one-size-fits-all rules (e.g., "sell at +20%") across LEAPs, shares, sold options, and leveraged ETFs.

**Two types of exits:**
1. **Thesis exits** — the reason you bought has changed (conviction dropped, fundamentals broke)
2. **Mechanical exits** — position size, valuation, or technicals trigger a systematic trim

Both are valid. Thesis exits override mechanical exits (if the thesis breaks, sell regardless of gain %). But mechanical exits prevent "I'll hold forever" complacency.

---

## Framework by Position Type

### 1. Sold Options (CCs, CSPs) — Harvest Theta

**Logic:** You sold time decay. Once most of the decay is captured, close and redeploy.

| Profit Captured | Time Elapsed | Action |
|----------------|-------------|--------|
| **50%+ profit** | **<50% of DTE** | **Close and redeploy.** You captured the edge in half the time — remaining premium has poor risk/reward. Capital efficiency wins. |
| 50% profit | 50-75% of DTE | Hold to 65%. Theta accelerating in your favor. |
| 50%+ profit | >75% of DTE | Close. Gamma risk increasing, diminishing returns. |
| <30% profit | >50% of DTE | Monitor. Consider rolling if thesis intact. |
| Any profit | <14 DTE | Close or roll. Gamma risk dominates. |
| >30% profit | <5 days (IV crush) | Close. Post-earnings IV crush = windfall, take it. |
| Underwater | Underlying ITM | Roll out/up/down, or accept assignment if happy with the price. |

**Don't do:** Hold sold options to expiry for the last 10-20% of premium. Risk/reward inverts near expiry.

### 2. Bought Options (LEAPs) — Let Winners Run

**Logic:** You paid for time and direction. The premium is sunk cost. Maximize the directional bet.

| Factor | Hold | Take Profit |
|--------|------|-------------|
| Sector momentum | Accelerating / Uptrend | Pulling Back / Downtrend |
| Time remaining | >120 DTE | <90 DTE (theta accelerating) |
| Conviction | ≥7, unchanged or rising | Dropped, thesis weakening |
| # Contracts | 1 (can't split) | 2+ (sell half) |
| Gain | 100-200% | 300%+ (extraordinary, lock some in) |
| Underlying trend | Above all SMAs, MACD bullish | Breaking SMA50, MACD bearish |

**Default:** Hold if sector accelerating + conviction high + >120 DTE. Set trailing mental stop instead.
**Exception:** At 300%+ or <90 DTE, take partial regardless.
**Rule:** At 90 DTE, ROLL to a new 6-12 month expiry — never let a winning LEAP decay.

### 3. Shares — DCA Positions

**Logic:** DCA is accumulation-oriented. You're building a position over time. Exit logic is about conviction decay and concentration management, not fixed % targets.

**Conviction-Decay Triggers (thesis exits):**

| Conviction Change | Action |
|-------------------|--------|
| Drops below 5 | Stop DCA immediately. Reassess within 2 weeks. |
| Drops 2+ points in one review | Pause DCA. Research what changed. |
| Thesis broken (not just a bad quarter) | EXIT — sell in order: taxable losers first, tax-free winners first |
| Sector enters Stage 4 (Declining) | Pause DCA. Don't fight the sector. |

**Concentration Management (mechanical exits):**

| Position Size | Trigger | Action |
|--------------|---------|--------|
| >15% of portfolio | Automatic review | Trim to 10% unless conviction ≥9 AND intentional (e.g., AMZN RSUs) |
| >10%, conviction <7 | Overweight for conviction | Trim to conviction-based target (conv × 1% = target %) |
| >20% | Mandatory | Trim to 15% regardless. No single stock should dominate unless RSU/locked. |

**"House Money" Rule:** When a DCA position doubles (+100%), consider selling enough shares to recover your total cost basis. The remaining shares have zero psychological cost — much easier to hold through volatility.

**O'Neil's 20-25% Rule (adapted for DCA):**
- Original: sell at 20-25% profit from breakout
- DCA adaptation: when a DCA position reaches +25% on your average cost AND conviction < 8, trim 25%
- Exception: if stock gained 20%+ in <3 weeks (potential monster stock), hold 8 more weeks before deciding

### 4. Shares — Lump Sum / Swing Positions

**Logic:** You entered at a specific price for a specific reason. Exit is tied to the thesis playing out or stops being hit.

**Scaled Exit Template (from execution-framework.md):**
- 25% at Target 1 (analyst consensus / first resistance)
- 25% at Target 2 (stretch target)
- 25% via trailing stop (let it run)
- 25% hold indefinitely (core compounder)

**Trailing Stop Methods:**
- **ATR-based:** Trail by 2x ATR below the high. Adapts to volatility.
- **Moving average:** Exit on a close below the 50-day SMA (for trending stocks) or 10-week SMA (for longer holds).
- **Percentage:** Simple 15-20% trailing stop from the high. Works but doesn't adapt to volatility.

**Time Stops:** If a position hasn't moved +10% in 90 days, reassess. Capital has an opportunity cost.

### 5. Leveraged ETFs (TSLL, CONL, etc.)

**Logic:** Structural decay from daily reset makes long-term holding a losing proposition in volatile markets. These are trades, not investments.

| Trigger | Action |
|---------|--------|
| Position is profitable | Sell into strength. Don't hold for "more upside." |
| RSI > 65 on the leveraged ETF | Sell — momentum peak for a decaying instrument |
| Held >60 days with no profit | Sell — decay is eating you alive |
| Underlying thesis conviction <6 | Sell immediately — leveraged exposure on low conviction = gambling |
| Bounce from oversold (RSI <30 → >40) | This IS the exit window. Sell the bounce. |

**Never:** Hold leveraged ETFs through earnings, buy long-dated calls on leveraged ETFs, or treat them as core positions.

---

## Cross-Cutting Rules

### Earnings

| Situation | Action |
|-----------|--------|
| Big position + earnings <7 days | Trim 10-20% pre-earnings to reduce binary risk |
| Options through earnings | Know your max risk. Decide before the report, not after. |
| Post-earnings gap up | Sell 25% into the gap. Reassess at new levels. |
| Post-earnings gap down, thesis intact | Hold or add. The market overreacts to single quarters. |
| Post-earnings gap down, thesis broken | Exit. Don't average down on broken thesis. |

### Sector Stage Transitions

| Sector Transition | Action on Holdings in that Sector |
|-------------------|-----------------------------------|
| Stage 2 → Stage 3 (Distribution) | Tighten stops. Pause DCA. Sell CCs aggressively. |
| Stage 3 → Stage 4 (Decline) | Exit swing positions. Pause all DCA. Only hold core compounders. |
| Stage 4 → Stage 1 (Basing) | Watch. Don't buy yet. Thesis must re-emerge. |
| Stage 1 → Stage 2 (Advancing) | Resume DCA. New entries viable. |

### Tax-Aware Sell Priority

When trimming, the account order matters (from `knowledge/frameworks/tax-rules.md`):
- **Selling winners:** Tax-free accounts first (Roth), then taxable with long-term lots
- **Selling losers:** Taxable accounts first (harvest the loss), then tax-free
- **Watch wash sale rule:** Don't rebuy within 30 days across accounts

---

## Anti-Patterns (Common Mistakes)

1. **"I'll sell when it gets back to even"** — sunk cost fallacy. If you wouldn't buy it today at this price, sell it.
2. **"It can't go lower"** — yes it can. Leveraged ETFs, broken theses, and Stage 4 sectors prove this daily.
3. **Cutting flowers, watering weeds** — trimming winners to buy more of losers. Only trim to manage concentration, not to "rebalance" into underperformers.
4. **No sell discipline at all** — "I'm a long-term investor" is not a sell strategy. Even Buffett sells (IBM, airlines, etc.).
5. **Selling on a red day** — panic selling locks in losses. Sell on green days, into strength.
6. **Applying CC profit rules to LEAPs** — different instruments, different logic. The IGV LEAP lesson.

---

## Integration Plan (TODO)

When building this into the skills:

1. `/portfolio-review` Step 3 — apply position-type-specific exit checks
2. `/trading-plan` Step 5 — reference this framework for position management actions
3. `/plan-stock` Phase 5c — use scaled exit template with instrument-appropriate stops
4. `scripts/watchlist.py` — could add a "harvest signal" column for positions hitting triggers

## Sources

- [O'Neil 20-25% Profit Rule](https://www.moomoo.com/my/learn/detail-when-to-sell-stock-the-20-25-profit-taking-rule-117056-240283205)
- [Minervini's Exit Criteria](https://www.tradingview.com/chart/COIN/dRQXnzm3-Minervini-s-Specific-Exit-Criteria/)
- [Conviction-Based Position Sizing Playbook](https://fluentinquality.substack.com/p/the-position-sizing-playbook-of-26)
- [Position Management: When to Trim, Hold, Add](https://www.dividend.school/p/the-position-management-playbook)
- [Trimming for Size Discipline](https://vistack.io/learning/sell-04)
- [Fidelity: Managing Positions](https://www.fidelity.com/learning-center/trading-investing/trading/managing-positions)
- [Strategic Selling Framework](https://stocktradingapproach.substack.com/p/strategic-selling-and-profit-taking)
