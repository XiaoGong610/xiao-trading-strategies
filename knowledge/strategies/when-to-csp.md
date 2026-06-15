# When to Sell Cash-Secured Puts (CSPs)

## What Is a CSP

You sell a put option and hold enough cash to buy 100 shares at the strike price if assigned. You collect premium upfront. If the stock stays above your strike through expiration, you keep the premium free and clear. If it drops below, you buy shares at the strike — but your effective cost basis is strike minus premium collected.

**Core mindset:** you're getting paid to place a limit buy order. Only sell CSPs on stocks you'd happily own at the strike price.

## When CSPs Have Edge

- **IV Rank > 50** — premium is rich relative to its own history. You're selling expensive insurance.
- **Stock at or near support** — technical floor reduces probability of assignment at a loss.
- **You want to own shares at strike** — this is the filter that prevents bad trades.
- **Range-bound to mildly bullish outlook** — CSPs profit when stock goes up, sideways, or even slightly down.
- **Post-selloff elevated IV** — fear spikes IV, you collect fat premium while others panic.

## Ideal Setup Checklist

- [ ] IV Rank > 50 (prefer > 65)
- [ ] RSI 30-50 (oversold to neutral — not chasing)
- [ ] Stock at identifiable support level (SMA, prior low, volume shelf)
- [ ] No earnings within DTE window (unless intentional)
- [ ] Liquid options (bid-ask spread < 5% of mid price)
- [ ] Clear thesis — you know why you'd own this stock
- [ ] Position size < 5% of portfolio

## Delta & DTE Selection

| Parameter | Sweet Spot | Notes |
|-----------|-----------|-------|
| **Delta** | 0.20-0.30 | ~70-80% probability of profit. Balances premium vs. safety. |
| **DTE** | 30-45 days | Peak theta decay zone. Shorter = less premium. Longer = more capital tied up. |

**When to adjust delta:**
- **Go further OTM (0.15-0.20):** high IV Rank > 75, you want income not ownership, wider margin of safety needed
- **Go closer to ATM (0.30-0.40):** you actively want assignment, stock is deeply oversold at strong support, higher premium justifies the risk

## Decision Matrix: IV Rank x RSI

| IV Rank | RSI < 30 (oversold) | RSI 30-50 (neutral-low) | RSI 50-70 (neutral-high) | RSI > 70 (overbought) |
|---------|---------------------|------------------------|-------------------------|----------------------|
| **> 75** | **Best setup** — sell aggressively at support, 0.25-0.30 delta | Sell at 0.20-0.25 delta | Sell far OTM, 0.15-0.20 delta | Skip — wait for pullback |
| **50-75** | Sell at support, 0.20-0.25 delta | Standard CSP, 0.20 delta | Small position, far OTM | Skip |
| **25-50** | Consider DCA instead — not enough premium | Marginal — only if setup is perfect | Skip — use Buy & Hold | Skip |
| **< 25** | **Don't sell CSPs** — buy LEAPs instead | Skip — premium too thin | Skip | Skip |

## Earnings Considerations

- **Pre-earnings (7-14 days out):** IV inflates. CSPs collect elevated premium, but you accept binary risk. Only sell if you'd own shares through any outcome at your strike.
- **Never sell CSPs through earnings you don't understand.** Biotech FDA decisions, uncertain guidance — the gap risk isn't worth the premium.
- **Post-earnings IV crush:** if you sold pre-earnings and it went your way, close at 50%+ profit immediately. Don't wait — the edge is gone.
- **Post-earnings entry:** IV crushed = less premium. Wait for IV to rebuild or use a different strategy.

## When NOT to Sell CSPs

- **IV Rank < 25** — you're selling cheap insurance. The math doesn't work.
- **Strong downtrend** — falling knife. Support levels break in downtrends. Wait for stabilization.
- **Thesis-breaking news** — regulatory action, fraud, competitive destruction. No amount of premium compensates.
- **Illiquid options** — wide bid-ask spreads eat your edge. If spread > 5% of mid, walk away.
- **You don't want to own the stock** — this is the #1 filter. If assignment would make you uncomfortable, don't sell the put.

## Management Rules

| Scenario | Action |
|----------|--------|
| Hit 50% of max profit | **Close.** Take the money. Re-sell at better levels if setup still valid. |
| Hit 65% of max profit | **Close.** Diminishing returns — remaining premium isn't worth the risk. |
| Stock drops to strike (tested) | **Roll down and out** — lower strike, extend 30 days. Only if thesis intact. |
| Stock drops through strike, thesis broken | **Close for a loss.** Don't roll a broken thesis. |
| Near expiration, stock well above strike | Let expire worthless or close for pennies to free up capital. |
| Assigned | **Own the shares.** Sell covered calls against them. This was the plan. |

**Close early rule of thumb:** close at 50% profit in the first half of the DTE period. After that, theta is your friend — let it run unless tested.

## Position Sizing

- **Max 5% of portfolio per CSP** (based on max loss = strike x 100 x contracts).
- Don't sell more contracts than shares you'd actually want to own. 5 contracts = 500 shares. Would you really buy 500 shares?
- **Diversify strikes and expirations.** Don't concentrate all CSPs in the same expiration week.

## Common Mistakes

1. **Selling CSPs on stocks you don't want to own** — chasing premium on garbage. When the stock drops 30%, you'll regret it.
2. **Ignoring assignment risk** — "it won't get assigned" is not a plan. If you'd panic at assignment, don't sell the put.
3. **No management plan** — decide your close target, roll trigger, and loss limit before entering.
4. **Selling in low IV** — collecting $0.50 on a $100 stock is not worth tying up $10,000.
5. **Oversizing** — selling 10 CSPs on one stock because "the premium is amazing." That's a concentrated bet, not income.
6. **Holding to expiration for max profit** — the last 20% of premium carries 80% of the remaining risk. Close early.
