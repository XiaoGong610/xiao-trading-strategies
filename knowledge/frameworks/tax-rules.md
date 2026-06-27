# Tax Rules for Multi-Account Portfolio

## Account Types & Tax Treatment

| Account | Tax on Gains | Tax on Losses | Rebalance Freely? |
|---------|-------------|---------------|-------------------|
| **Brokerage (HOLD, ThetaGang)** | Yes — short-term (ordinary income) or long-term (15-20%) | **Deductible** — offset gains, up to $3K/year against income | No — every sell triggers taxes |
| **Roth IRA** | **None** — tax-free growth | **Not deductible** — losses are wasted | Yes — no tax consequences |
| **401k / BrokerageLink** | **None** (tax-deferred, taxed on withdrawal) | **Not deductible** — losses are wasted | Yes — no tax consequences |

## The Core Rule: Which Account to Sell In

### Selling a LOSER (position is underwater)

```
SELL IN TAXABLE ACCOUNT FIRST

Taxable (HOLD, ThetaGang)  →  Loss is deductible. Harvest it.
Tax-free (Roth, 401k)      →  Loss is wasted. No benefit.
```

**Why:** A realized loss in a taxable account offsets capital gains dollar-for-dollar. In a tax-free account, the loss simply disappears — you can't deduct it anywhere.

### Selling a WINNER (position is profitable)

```
SELL IN TAX-FREE ACCOUNT FIRST

Tax-free (Roth, 401k)      →  No tax on gains. Pure profit.
Taxable (HOLD, ThetaGang)  →  Gains are taxed. Reduced profit.
```

**Why:** Gains in a Roth IRA are never taxed. The same gain in a taxable account loses 15-20% (LTCG) or up to 37% (STCG) to taxes.

### Summary Matrix

| | Position is a LOSER | Position is a WINNER |
|---|---|---|
| **Sell in taxable first** | ✅ **YES — harvest the tax loss** | ❌ No — you'll pay taxes on the gain |
| **Sell in tax-free first** | ❌ No — loss is wasted | ✅ **YES — gains are tax-free** |

## Holding Period Rules (Taxable Accounts Only)

| Holding Period | Tax Rate | Rule |
|---------------|----------|------|
| < 1 year | **Short-term** = ordinary income (up to 37%) | Avoid selling if you're close to 1 year |
| > 1 year | **Long-term** = 15-20% | Much better — wait for this if practical |

**Practical implication:** If a position in a taxable account is 10 months old with a big gain, wait 2 more months for long-term treatment. The tax savings on a $50K gain can be $5K-10K.

**Example from your portfolio:** AMZN HOLD account has 279 shares from Oct 2025. These become long-term on Oct 15, 2026. DO NOT sell before that date — the tax difference on ~$5K gain per share is significant.

## Tax-Loss Harvesting

**What:** Sell a losing position to realize the loss, then use it to offset gains elsewhere.

**Rules:**
1. Losses offset gains dollar-for-dollar (no limit)
2. Excess losses offset up to $3,000/year of ordinary income
3. Remaining losses carry forward to future years
4. **Wash sale rule:** If you buy the same or "substantially identical" security within 30 days (before or after the sale), the loss is disallowed

**Wash sale across accounts:** The wash sale rule applies ACROSS ALL your accounts. If you sell TSLL at a loss in ThetaGang and buy TSLL in your Roth IRA within 30 days, the loss is disallowed. Be careful when the same stock is held in multiple accounts.

**Safe alternatives during the 30-day window:**
- Sell TSLL, buy TSLA shares instead (not substantially identical — different security)
- Sell one semi ETF, buy a different semi ETF (different fund, different index)
- Wait 31 days, then rebuy if you still want the position

## Where to Hold What (Tax Efficiency)

| Asset Type | Best Account | Why |
|-----------|-------------|-----|
| High-growth stocks (NVDA, MU) | **Roth IRA** | Gains compound tax-free. Max growth = max tax savings. |
| Dividend stocks | **Roth IRA or 401k** | Dividends are taxed annually in brokerage. Tax-free in Roth. |
| Theta gang (CSPs, CCs) | **Roth IRA** | Premium income is short-term gains in brokerage. Tax-free in Roth. |
| Buy & Hold (AMZN, GOOG) | **Either** — brokerage is fine if holding >1 year | Long-term cap gains rate is manageable (15-20%). |
| Speculative / high-turnover | **Roth IRA** | Frequent trading = all short-term gains. Tax-free in Roth avoids the penalty. |
| Positions you might tax-loss harvest | **Brokerage** | You need it in a taxable account to harvest the loss. |

## Multi-Account Concentration & Tax Implications

When the same stock is held across multiple accounts, selling in one account requires checking:

1. **Wash sale risk** — are you buying in another account within 30 days?
2. **Which account gives the best tax treatment** for this specific sale? (loser → taxable, winner → tax-free)
3. **Holding period** — in the taxable account, is it short-term or long-term?

## Rules for `/portfolio-review`

When recommending sells across accounts, always specify the account order and tax rationale:

```
Selling a LOSER:
  1st: Taxable account (harvest loss)
  2nd: Tax-free accounts (no benefit, just cleaning up)

Selling a WINNER:
  1st: Tax-free account (no tax on gains)
  2nd: Taxable account, ONLY if long-term (>1 year)
  3rd: Taxable account, short-term — AVOID unless necessary
```

Flag any position approaching the 1-year holding mark — waiting 2-4 weeks can save thousands in taxes.
