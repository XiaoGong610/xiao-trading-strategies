# CLAUDE.md

## Project

**xiao-trading-strategies** — A personal trading research and analysis workspace.

## Use Cases

### 1. Stock Research
Deep-dive research on individual stocks including:
- Company fundamentals and growth trajectory
- Earnings calls analysis (key takeaways, guidance, surprises)
- Market sentiment (analyst ratings, institutional activity, news flow)
- Competitive positioning and sector trends

### 2. Theta Gang Options Trading
Expert analysis for selling options (theta decay strategies). Core principle: time is your friend — earn premium by selling extrinsic value (time + IV).

**Trading Rules:**
- Target 30-45 DTE (theta decay sweetspot)
- Delta 0.20-0.30 for selling puts → 70-80% probability of profit
- Only sell puts at a strike price you'd be happy to own the stock at
- Prefer opening CSPs when stock is pulling back, or after a breakout (sell at breakout level)
- Close at 50% profit if reached in half the time (diminishing returns beyond that)
- Avoid earnings and ex-dividend dates — both cause unpredictable moves
- If stock drops, do NOT exercise early to take assignment
- Rolling: only if still bullish on the thesis. Must roll for a credit
  - Puts: roll out & down
  - Calls: roll out & up

**Strategies (in order of complexity):**
1. **Cash Secured Put (CSP)**: Bullish bias. Sell OTM put, delta 0.20-0.30
2. **Covered Call (CC)**: Own 100 shares of a stable stock. Sell call above cost basis at your take-profit level
3. **Poor Man's Covered Call (PMCC)**: Buy deep ITM long call (delta 0.80-0.90) + sell short OTM call (delta 0.20-0.30). For long-term bullish stocks with low IV rank / IV percentile <50%. Less capital than CC
4. **Iron Condor**: For sideways/range-bound stocks. Sell call+put at ~16 delta, buy wings further out. Target profit = 1/3 of width

**Greeks to monitor:**
- Delta = directional exposure (speed)
- Gamma = rate of delta change (acceleration) — watch for gamma risk near expiration
- Theta = daily time decay earned — our edge
- Vega = IV sensitivity — we want IV to drop after selling (negative vega position). IV crush after earnings benefits sellers

**Performance Tracking:**
- **Sortino Ratio** (primary) — like Sharpe but only penalizes downside volatility, more honest for options selling where returns are negatively skewed
- **Max Drawdown** — catches tail risk that Sharpe/Sortino miss
- **Sharpe Ratio** — useful for comparison but can be artificially inflated by consistent small premiums hiding large tail risk
- Track per-stock and portfolio-wide over time

## How to Work

- When researching a stock, present findings in a structured format with clear sections
- For theta gang analysis, always include: IV rank/percentile context, suggested strike/expiry, probability of profit, max profit/loss, and any upcoming catalysts (earnings, ex-div dates) that could affect the trade
- Be opinionated — give clear recommendations with reasoning, not just raw data
- Flag risks prominently (e.g., upcoming earnings, binary events, low liquidity)
- Use current market data when available via web search

## Folder Structure

```
research/          # Stock research — one file per stock (e.g., AAPL.md)
theta-gang/        # Theta gang trade analysis — one file per stock (e.g., AAPL.md)
```

- Each file is a living document that accumulates historical analysis
- **Ordering rule:** newest analysis on top, oldest at bottom
- **Section format:** every analysis entry must start with a clear date separator:
  ```
  ---
  # TICKER — Analysis Type | YYYY-MM-DD
  ```
- When adding new analysis to an existing file, prepend it above all previous entries (after the file title line if one exists)
- Never overwrite or remove historical entries — they serve as a log of how thinking evolved over time
- New use cases get their own top-level folder

## Python Environment

A virtual environment at `.venv/` (Python 3.12) with:
- `yfinance` — free Yahoo Finance data (price history, options chains)
- `plotly` — interactive HTML charts
- `matplotlib` — static charts
- `pandas` — data analysis

Activate before running scripts: `source .venv/bin/activate`

## Future Extensions

This project may expand to additional trading strategies and tooling over time.
