---
description: Review an active position — hold, add, sell, or roll?
---

Review position: $ARGUMENTS

The argument is a ticker (e.g., "AAPL", "AMZN").

Read the portfolio file at `portfolio/$TICKER.md` to understand the current position (strategy, strike, expiry, premium, cost basis).

**Step 1:** Run the data script to get current price and technicals:
```bash
.venv/bin/python3 scripts/technicals.py $ARGUMENTS --options
```

Use the script's output for current price, technicals, and support/resistance vs. entry data. Supplement with web search for news and qualitative updates.

**Consult knowledge base:**
- Read `portfolio/$ARGUMENTS.md` for position details AND `research/stocks/$ARGUMENTS.md` for the original thesis
- Based on the position's strategy, read the relevant knowledge file:
  - CSP/CC positions → `knowledge/strategies/when-to-csp.md` (management rules: close at 50%, roll triggers)
  - LEAP positions → `knowledge/strategies/when-to-leaps.md` (roll before 90 DTE, cut on thesis break)
- Run `.venv/bin/python3 scripts/sector-momentum.py --json` — check if sector conditions have changed since entry
- Read `knowledge/signals/ma-guide.md` — has the stock broken below key SMAs since entry? SMA alignment change = trend change
- Read `knowledge/signals/volume-guide.md` — check relative volume on recent moves (high volume decline = distribution, low volume = healthy pullback)

## Position Status
- Current stock price vs. entry price and strike
- How far ITM/OTM is the position?
- Days to expiry remaining
- Estimated current option value (cost to close)
- Current P&L (premium collected vs. cost to close)
- Progress toward 50% profit target

## Market Update
- What has changed since the position was opened?
- Any new news, earnings, or catalysts?
- Has IV expanded or contracted?
- Key support/resistance levels still intact?

## Greeks Check
- Current delta exposure — has it shifted significantly?
- Theta decay — how much are you earning per day?
- Gamma risk — are you approaching expiration with the strike near the money?

## Recommendation

One of:
- **Hold** — on track, let theta do its work
- **Close early** — hit 50% profit target or risk/reward no longer favorable
- **Roll** — position tested, still bullish, roll for credit (suggest running `/strategy-theta-gang roll $ARGUMENTS`)
- **Add** — thesis strengthened, consider adding a second position
- **Exit** — thesis broken or risk too high, close the position

Include specific reasoning for the recommendation.

## Action Items
- What to do next and when to check again
- Any price levels that would change the recommendation

Save the output by prepending to `portfolio/$TICKER.md` (after the YAML frontmatter block).
Start the entry with: `---` followed by `# TICKER — Position Review | YYYY-MM-DD`.
Never remove historical entries.
