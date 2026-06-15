# Portfolio Risk Metrics Framework

## Core Principle

Don't just measure returns — measure **return per unit of risk**. A 20% return with 30% volatility is worse than a 15% return with 10% volatility. The Sharpe Ratio captures this: it's the slope of the line from the risk-free rate to your portfolio on the risk-return plane. The steeper the line, the better.

可以高风险，只要回报率足够高。(High risk is OK — as long as return is high enough to compensate.)

## The 8 Key Metrics

| # | Metric | Formula | Good | Excellent | What It Tells You |
|---|--------|---------|------|-----------|-------------------|
| 1 | **Sharpe Ratio** | (Return - Risk-Free Rate) / Std Dev | >1.0 | >2.0 | Return per unit of total risk. The single most important metric. |
| 2 | **Sortino Ratio** | (Return - Risk-Free Rate) / Downside Dev | >1.0 | >2.0 | Like Sharpe but only penalizes downside volatility. Better for asymmetric strategies (options). |
| 3 | **Alpha** | Return above benchmark (risk-adjusted) | positive | >2% | Your edge over the market. Negative alpha = you'd be better off in SPY. |
| 4 | **Beta** | Covariance(portfolio, market) / Var(market) | 0.5-1.0 | <1.0 | Sensitivity to market moves. Beta 1.5 = you move 1.5x the market. |
| 5 | **CAGR** | Compound Annual Growth Rate | >10% | >15% | Absolute return measure. S&P averages ~10% long-term. |
| 6 | **Max Drawdown** | Largest peak-to-trough decline | <20% | <10% | Worst-case pain. How much you'd lose at the worst possible moment. |
| 7 | **Recovery Speed** | Days to recover from max drawdown | < market | 50-100% faster than S&P | How quickly you bounce back. Fast recovery = better risk management. |
| 8 | **Volatility** | Annualized std dev of returns | <market | 10-15% | Total risk. Market is ~15-20%. Below market = smoother ride. |

## Sharpe Ratio Deep Dive

**Formula:** `Sharpe = (E[Rp] - Rf) / σp`
- `E[Rp]` = expected portfolio return
- `Rf` = risk-free rate (current ~3.5-3.75% Fed funds)
- `σp` = standard deviation of portfolio returns

**Interpretation:**
- **< 0:** You're losing money on a risk-adjusted basis. Stop.
- **0-0.5:** Poor — not compensating for risk taken
- **0.5-1.0:** Adequate — acceptable but room to improve
- **1.0-2.0:** Good — solid risk-adjusted performance
- **2.0-3.0:** Excellent — top-tier hedge fund territory
- **> 3.0:** Exceptional — verify your data, this is rare

**On the Efficient Frontier:** The Sharpe Ratio is the slope of the Capital Allocation Line from the risk-free rate to the portfolio. The tangent point where this line touches the efficient frontier is the **Market Portfolio** — the optimal mix of risk and return. Portfolios below the efficient frontier are suboptimal (same risk, less return).

**Key insight:** You must calculate Sharpe based on YOUR positions and update frequently. Published Sharpe ratios for individual stocks exist, but for options strategies the data is harder to find — you need to track your own P&L series.

## Sharpe vs. Sortino

- **Sharpe** penalizes ALL volatility equally — upside and downside
- **Sortino** only penalizes DOWNSIDE volatility — upside surprises don't count against you
- **For options sellers (theta gang):** Sortino is more appropriate because your return profile is asymmetric (many small wins, occasional large loss)
- **For buy & hold / DCA:** Sharpe is fine since returns are roughly symmetric

## How to Use These Metrics

### For Individual Stocks (before adding to portfolio)
- Check Beta — adding a Beta 2.0 stock to a portfolio of Beta 0.8 stocks increases overall risk significantly
- Check correlation with existing positions — if all your positions move together, diversification is an illusion

### For Portfolio Review (`/trade-portfolio`)
- Calculate portfolio-level Sharpe monthly (once we have enough trade history)
- Track Max Drawdown — if it exceeds 20%, review position sizing and correlation
- Compare Alpha vs. SPY — if negative, consider shifting to index

### For Position Sizing
- Higher Sharpe stocks can get larger allocations
- Lower Beta stocks can get larger allocations (less portfolio risk contribution)
- **Kelly Criterion simplified:** optimal position size ≈ (edge / odds) — but use half-Kelly in practice to account for estimation error

### For Strategy Evaluation
- Compare Sharpe across your strategies over time:
  - If theta gang has Sharpe 1.5 and buy & hold has Sharpe 0.7, allocate more to theta gang
  - But need 20+ trades per strategy for statistical significance

## Common Mistakes

1. **Ignoring Sharpe and only looking at returns** — a 40% return with 50% max drawdown is not good
2. **Comparing Sharpe across different time periods** — Sharpe in a bull market ≠ Sharpe through a full cycle
3. **Not accounting for risk-free rate changes** — Sharpe calculated with 0% rates is not comparable to Sharpe with 4% rates
4. **Too few data points** — Sharpe from 5 trades is meaningless. Need 20+ trades or 6+ months of data
5. **Survivorship bias** — only calculating Sharpe on open positions (ignoring closed losers)
