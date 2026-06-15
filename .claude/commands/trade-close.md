---
description: Close a position, log P&L, and run trade review
---

Close position: $ARGUMENTS

The argument format is: TICKER OUTCOME [EXIT_PRICE] [CLOSE_PREMIUM]

Examples:
- "AAPL expired-worthless"
- "TSLA closed-early 2.50" (closed the option by buying back at $2.50)
- "AMZN assigned 185" (assigned at $185 strike)
- "COIN rolled-and-closed" (rolled to a new position, closing this one)

Outcomes: expired-worthless, closed-early, assigned, called-away, rolled-and-closed

## Actions

1. **Read the portfolio file** at `portfolio/TICKER.md` to get position details from frontmatter (strategy, strike, expiry, premium, contracts, entry_date, cost_basis). Read the relevant `knowledge/strategies/` file for the position's strategy type to compare actual results vs. ideal setup in the trade review.

2. **Calculate P&L:**
   - **expired-worthless:** P&L = premium × contracts × 100
   - **closed-early:** P&L = (premium - close_premium) × contracts × 100
   - **assigned:** P&L = premium × contracts × 100 (note: now holding shares at cost_basis)
   - **called-away:** P&L = premium × contracts × 100 + (strike - underlying_price) × contracts × 100
   - **rolled-and-closed:** P&L depends on net credit/debit of the roll
   - Calculate hold_days, annualized return, return on buying power

3. **Run trade review** — analyze what happened:
   - Was the thesis correct?
   - Did the stock behave as expected?
   - What went right? What could improve?
   - Any lessons for future trades?

4. **Update risk-adjusted metrics** (read all existing files in `trades/` to calculate running totals):
   - **Sortino Ratio** (primary) — use 10-year Treasury yield as risk-free rate
   - **Sharpe Ratio** (secondary)
   - **Max Drawdown**
   - **Win Rate** (% of profitable trades)
   - If not enough trades yet for meaningful ratios, note this and track individual results

5. **Add closing entry** to the portfolio file, then **move it** to `trades/TICKER-YYYYMMDD.md` (using today's date):
   - Update frontmatter: set `status: closed`, add `exit_date`, `outcome`, `realized_pnl`, `annualized_return`
   - Append the trade review analysis

6. **Update stock file** (if `research/stocks/TICKER.md` exists):
   - If outcome is assigned/called-away and user may want to re-enter, set status back to `watching`
   - If the user is done with this ticker, set status to `removed`
   - **Update index & dashboard:**
     ```bash
     .venv/bin/python3 scripts/update-index.py && .venv/bin/python3 scripts/dashboard.py
     ```

Start the trade review entry with: `---` followed by `# TICKER — Trade Review | YYYY-MM-DD`.
