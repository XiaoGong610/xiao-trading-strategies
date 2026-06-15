# When to Buy & Hold

## What Is Buy & Hold

Concentrated entry into a high-conviction position. You buy shares and hold for the long term (months to years). Simplest strategy but requires the most conviction — there's no premium cushion, no time decay working for you. Your entire edge is the thesis.

**Core mindset:** you're buying a business, not renting a price move. If you can't explain in 2 sentences why this company will be worth more in 2-3 years, you don't have a thesis.

## When Buy & Hold Has Edge

- **Conviction 8+** — you've done the research, the numbers work, and you believe in the trajectory.
- **Secular compounder** — growing revenue, expanding margins, reinvesting in the business. The kind of stock where timing matters less than participation.
- **Clear multi-year thesis** — not a trade, not a catalyst play. A durable business advantage.
- **Full upside exposure** — no cap from covered calls, no time decay from options. You want every dollar of upside.
- **Simple execution** — no rolling, no Greeks, no expiry management. Buy, monitor thesis, hold.

## Lump-Sum vs. DCA Decision

Research shows lump-sum beats DCA ~67% of the time (markets trend up). But DCA wins psychologically and in volatile or expensive markets.

| Condition | Action |
|-----------|--------|
| Conviction 8+ AND valuation cheap/fair AND sector uptrend | **Lump-sum** — deploy full position now |
| Conviction 6-7 OR valuation expensive OR sector choppy | **DCA instead** — average in over 4-8 weeks |
| Conviction < 6 | **Don't buy** — do more research |

## Ideal Setup Checklist

- [ ] Conviction score 8+ (clear, falsifiable thesis)
- [ ] Price above 200 SMA (long-term uptrend intact)
- [ ] Sector in Stage 2 (advancing — see sector-momentum.py)
- [ ] Valuation fair or cheap for sector (cross-ref valuation.md benchmarks)
- [ ] No earnings within 7 days
- [ ] Thesis articulable in 2 sentences
- [ ] Position size within limits (see below)

## Entry Timing by SMA Alignment

Cross-reference `ma-guide.md` for SMA interpretation.

| SMA Alignment | Signal | Action |
|---------------|--------|--------|
| Price > 20 > 50 > 200 (bullish stack) | Strong uptrend | Buy now — trend is confirmed |
| Price pulling back to 50 SMA in uptrend | Normal pullback | **Best entry** — buy the dip in a healthy trend |
| Price at 200 SMA, trend intact | Deep pullback | Larger position if 200 holds as support |
| Price at 200 SMA, trend breaking | Trend reversal risk | Wait or use DCA — don't catch a falling knife |
| Price below 200 SMA (bearish stack) | Downtrend | **Don't Buy & Hold** — wait for trend reversal or DCA slowly |

## Position Sizing

Conviction-based sizing. Adjust down in expensive markets.

| Conviction | Position Size | Notes |
|------------|--------------|-------|
| 8-10 | Full position (3-5% of portfolio) | Deploy with confidence |
| 6-7 | Half position (1.5-2.5%) | Plan to add on confirmation |
| < 6 | No position | More research needed |

**Guardrails:**
- Never > 5% in a single stock unless it's a core holding with years of track record.
- CAPE > 35 → reduce all position sizes by 20-30%. Expensive markets punish concentration.

## When NOT to Buy & Hold

- **IV Rank > 60** — sell CSPs instead. Get paid to enter at your target price.
- **Sustained downtrend** — below 200 SMA with bearish SMA stack. Don't fight the trend.
- **Thesis depends on a single binary event** — use LEAPs for defined risk instead.
- **Conviction < 6** — you're guessing, not investing.

## When to Sell

Sell on thesis breaks, not price drops. Red days are noise. Broken theses are signal.

| Trigger | Action |
|---------|--------|
| **Thesis breaks** (fundamentals deteriorate, competitive moat erodes) | Sell — don't hope for recovery |
| **Valuation extreme** (> 2x fair P/E for sector) | Trim or sell — gravity wins eventually |
| **Better opportunity** with limited capital | Rotate — opportunity cost is real |
| **Sector enters Stage 4 downtrend** | Sell or hedge — rising tide lifted you, falling tide sinks you |
| Price drops but thesis intact | **Hold.** This is what conviction means. |

## Decision Matrix: Conviction x Valuation

| Conviction | Cheap / Fair | Expensive | Very Expensive (> 2x sector P/E) |
|------------|-------------|-----------|-----------------------------------|
| **8-10** | **Buy & Hold** — lump-sum, full position | Buy & Hold — DCA in, smaller size | Wait for pullback or use LEAPs |
| **6-7** | DCA — half position, average in | DCA — quarter position at most | Skip — risk/reward doesn't work |
| **< 6** | More research needed | Skip | Skip |

## Buy & Hold vs. Other Strategies

| Situation | Better Strategy | Why |
|-----------|----------------|-----|
| IV Rank > 50 | **CSP** | Get paid to buy at your target price |
| IV Rank < 25 + high conviction | **LEAPs** | Same exposure, fraction of capital, defined risk |
| Uncertain timing | **DCA** | Average in, reduce regret |
| Own shares, want income | **Buy & Hold + covered calls** | Enhance returns in sideways markets |
| Single binary catalyst | **LEAPs** | Defined risk on event outcome |

## Common Mistakes

1. **Buying without a thesis** — "it's cheap" is not a thesis. Why is it cheap? What changes?
2. **No sell plan** — decide your exit criteria before entry. What breaks the thesis?
3. **Averaging down on a broken thesis** — adding to losers because "it's even cheaper now" is how small losses become large losses.
4. **Concentration risk** — 3 stocks at 5% each in the same sector is a 15% sector bet. Diversify across sectors.
5. **Ignoring sector context** — a great stock in a Stage 4 sector still goes down. Check sector momentum first.
6. **Confusing conviction with stubbornness** — update your thesis with new information. Conviction isn't ignoring red flags.
