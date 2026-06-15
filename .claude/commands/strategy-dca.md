---
description: Dollar Cost Averaging strategy — schedule, sizing, and tracking
---

DCA strategy analysis for: $ARGUMENTS

The argument format is: TICKER [TOTAL_BUDGET]
- TICKER: stock symbol (e.g., "AAPL")
- TOTAL_BUDGET: optional — total amount to invest (e.g., "AAPL 10000")

Assume the user already has conviction from `/research-stock` or `/plan-stock`. This skill focuses on building a DCA plan: schedule, amounts, and guardrails.

**Important:** If the user has trading restrictions on this stock (e.g., trading windows, no options), adapt the plan accordingly — recommend how much to buy per open window instead of daily, and skip options strategies.

**Step 1:** Run the data script:
```bash
.venv/bin/python3 scripts/technicals.py $ARGUMENTS --options
```
(Extract the ticker from the arguments.)

Use the script's output for price, volatility, and support/resistance. Supplement with web search for upcoming catalysts.

**Step 2: Consult knowledge base**
- Read `knowledge/signals/rsi-guide.md` — RSI zones map to DCA pacing: RSI <30 = accelerate (double daily amount), RSI 30-50 = normal, RSI >70 = pause or halve
- Read `knowledge/frameworks/valuation.md` — use the RSI + Fwd P/E combo for sizing. Oversold + cheap = accelerate DCA, overbought + expensive = pause. If CAPE >35, consider reducing total budget or extending duration.
- Run `.venv/bin/python3 scripts/sector-momentum.py --json` and consult `knowledge/frameworks/sector-momentum.md` — map sector classification to DCA behavior: Accelerating = normal DCA, Pulling Back = accelerate, Downtrend = slow DCA only
- Read `knowledge/signals/iv-rank-guide.md` — if IV Rank >50, note that CSP entry may be more capital-efficient. If IV Rank <25, LEAPs may offer better leverage.

## Stock Profile for DCA

- Current price and 52-week range
- Average daily/weekly volatility (ATR) — helps set expectations for price swings between buys
- Upcoming events: earnings dates, ex-div dates in the DCA window
- Is the stock in an uptrend, downtrend, or range? (DCA works in all, but sets expectations)

## DCA Approaches

Present all three approaches and recommend the best fit (or a combination):

### Approach A: Static Recurring (Pure DCA)
Fixed dollar amount every day, regardless of price. Removes emotion and timing entirely.
- **Schedule**: daily by default (user preference)
- **Amount per day**: fixed (e.g., $100/day)
- **Total budget**: if provided, calculate how many days to reach full position
- **Duration**: how long to DCA (e.g., 1 month, 3 months, 6 months)
- **Best when:** high conviction but uncertain timing, volatile stock, want hands-off

### Approach B: Limit Buys at Target Prices
Set buy orders at specific support levels. Only executes if price drops to target.
- Use the script's support levels and volume profile HVN to set targets
- Suggest 3-5 limit buy levels with amounts that increase at lower prices
- **Best when:** stock is overextended, you want a better entry, you're patient

| Level | Price | Amount | Rationale |
|-------|-------|--------|-----------|

### Approach C: Hybrid (DCA + Zone-Based Sizing)
Daily recurring as the base, with zone-based adjustments — buy more at lower prices, less at highs.
- **Base**: daily amount (e.g., $50/day)
- **Zones**: define 3-4 price zones with multipliers

| Zone | Price Range | Daily Amount | Rationale |
|------|------------|-------------|-----------|
| Extended | Above SMA 20 | 0.5x base | Reduce buying when overextended |
| Fair | SMA 20 to SMA 50 | 1x base | Normal accumulation |
| Attractive | SMA 50 to support | 2x base | Accelerate on pullback |
| Deep value | Below support | 3x base | Heavy buying at key levels |

- **Best when:** want steady accumulation but also want to capitalize on dips

**Recommendation:** Pick the best approach (or combination) based on the stock's current price action, volatility, and how extended it is.

## Acceleration & Pause Rules

- **Accelerate buys if**: stock drops >15% from average cost — increase daily amount or trigger limit buys
- **Pause buys if**: thesis-breaking news, earnings miss, or stock drops below a key support level that changes the outlook
- **Stop entirely if**: thesis breaks — specific triggers

## Tracking

- Track average cost basis as buys accumulate
- Review thesis at each earnings report
- Reassess DCA plan if stock moves ±20% from starting price

Save the output to `research/stocks/$TICKER.md` (use uppercase ticker as filename).
Start the entry with: `---` followed by `# TICKER — DCA Plan | YYYY-MM-DD`.
If the file already exists, prepend above previous entries (after YAML frontmatter). Never remove historical entries.

If creating a new file, add YAML frontmatter:
```yaml
---
ticker: TICKER
status: watching
added_date: YYYY-MM-DD
sector: (infer from research)
thesis: "(one-line summary)"
entry_target: (current price — DCA starts at market)
strategies: [dca]
---
```

**Update index:** Run `.venv/bin/python3 scripts/update-index.py` to regenerate `0-INDEX.md`.
