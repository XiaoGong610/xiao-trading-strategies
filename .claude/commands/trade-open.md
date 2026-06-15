---
description: Log a new position to the portfolio
---

Log a new position: $ARGUMENTS

The argument format is: TICKER STRATEGY STRIKE EXPIRY PREMIUM [CONTRACTS] [UNDERLYING_PRICE]

Examples:
- "AAPL CSP 185P 2026-06-18 3.20"
- "TSLA CC 430C 2026-06-18 8.50 1 390"
- "AMZN shares 100 268.00" (for share purchases)

Parse the arguments to extract:
- **ticker**: The stock symbol
- **strategy**: CSP, CC, PMCC, IC, or shares
- **strike**: The strike price (include P or C suffix)
- **expiry**: Expiration date (for options)
- **premium**: Premium collected per share
- **contracts**: Number of contracts (default 1)
- **underlying_price**: Stock price at entry (if not provided, look up current price)

## Actions

1. **Create portfolio file** at `portfolio/TICKER.md` with YAML frontmatter:

```yaml
---
ticker: TICKER
status: active
strategy: (CSP/CC/PMCC/IC/shares)
entry_date: YYYY-MM-DD
underlying_price: (stock price at entry)
strike: (strike price)
expiry: (expiration date)
premium: (premium per share)
contracts: (number)
cost_basis: (strike - premium for CSP, or underlying price for shares)
---
```

2. **Add an entry** below the frontmatter:
```
---
# TICKER — Position Opened | YYYY-MM-DD

**Strategy:** (e.g., "Sold $185 Put, June 18 expiry")
**Premium:** $X.XX/share ($XXX/contract)
**Underlying at entry:** $XXX.XX
**Max profit:** $XXX | **Breakeven:** $XXX.XX
**Management plan:** Close at 50% profit, roll if tested (per trading rules)
```

3. **Update stock file** (if `research/stocks/TICKER.md` exists):
   - Update the frontmatter `status` field to `in-portfolio`
   - **Update index & dashboard:**
     ```bash
     .venv/bin/python3 scripts/update-index.py && .venv/bin/python3 scripts/dashboard.py
     ```

4. If `portfolio/TICKER.md` already exists (second position on same ticker):
   - Create `portfolio/TICKER-2.md` instead (increment the suffix)
   - Keep the same frontmatter structure

Do NOT run a full analysis — this is a logging action. The analysis should have been done via `/plan-stock` before this point.
