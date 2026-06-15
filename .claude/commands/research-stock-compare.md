---
description: Compare researched stocks head-to-head and pick the best trading opportunity
---

Compare these stocks and rank them for the best trading opportunity: $ARGUMENTS

The argument is a comma-separated list of tickers (e.g., "AAPL, TSLA, NVDA, AMZN, MSFT"). These should already be researched individually via `/research-stock` — this skill does the head-to-head comparison to decide which one to trade.

---

**Step 1: Read & validate research**

Read the existing research files for each ticker from `research/stocks/TICKER.md`.

**Staleness check:** For each ticker, check the date of the most recent research entry:
- **Fresh (<7 days):** Use as-is
- **Stale (7-14 days):** Flag with [WARNING] — usable but note data may have shifted
- **Very stale (>14 days):** Flag with [STALE] — recommend re-running `/research-stock TICKER` before comparing
- **Missing:** Flag — must run `/research-stock TICKER` first

| Ticker | Last Researched | Status | Conviction Score |
|--------|----------------|--------|-----------------|

If any ticker is missing or very stale, list it and suggest the user re-research before proceeding. Continue with available data but note the gap.

**Step 2: Pull fresh technicals**

Run `technicals.py` for each ticker to get current price data:
```bash
.venv/bin/python3 scripts/technicals.py TICKER1 --options && .venv/bin/python3 scripts/technicals.py TICKER2 --options
```

**Step 3: Consult knowledge base for interpretation**
- Read `knowledge/signals/rsi-guide.md` — note that RSI thresholds differ by sector beta (semis routinely hit extremes, utilities rarely do)
- Read `knowledge/frameworks/valuation.md` — use sector-appropriate P/E benchmarks, not raw P/E comparisons
- Read `knowledge/signals/iv-rank-guide.md` — validate strategy recommendations against IV Rank thresholds

---

## Head-to-Head Scoring

Score each stock on 5 weighted dimensions (1-10). Pull conviction scores from research files where available.

| Dimension (Weight) | TICK1 | TICK2 | TICK3 | ... |
|--------------------|-------|-------|-------|-----|
| Conviction (25%) — bull case strength, moat, growth | | | | |
| Timing (25%) — entry point quality, near support vs. extended | | | | |
| Growth/Valuation (20%) — best growth-to-valuation ratio | | | | |
| Risk Profile (15%) — earnings proximity, binary events, sector headwinds | | | | |
| Strategy Fit (15%) — how actionable is the best strategy right now | | | | |
| **Weighted Score** | | | | |

**Scoring notes:**
- Conviction should align with the `/research-stock` conviction score — don't reinvent it
- Timing: at key support = 8-10, no-man's-land = 4-6, overextended = 1-3
- Risk: lower risk = higher score (no earnings soon, no binary events = 8-10)

## Ranking Table

| Rank | Ticker | Score | Price | Trend | RSI | IV Rank | Fwd P/E | Next Earnings | Best Strategy | Verdict |
|------|--------|-------|-------|-------|-----|---------|---------------|---------------|---------|

## Strategy Fit (per stock)

For each stock, recommend the best strategy:
- **Buy & Hold** — strong compounder, trending up, just accumulate
- **DCA** — conviction but uncertain timing
- **LEAP Calls** — bullish with catalyst ahead, want leverage
- **Theta Gang** — elevated IV, range-bound or at support, premium is rich

Validate strategy recommendations against knowledge base checklists:
- Theta Gang → check `knowledge/strategies/when-to-csp.md` (IV Rank >50? At support? Liquid options?)
- LEAP Calls → check `knowledge/strategies/when-to-leaps.md` (IV Rank <30? Clear catalyst? High conviction?)

## Top Picks

For the top 2-3 candidates (highest weighted score):
- Why they stand out vs. the rest
- Recommended strategy and why
- Quick entry suggestion (price level, strike, or DCA schedule)

## Skip For Now
- Which stocks to avoid right now and why (earnings too close, IV too low, overextended, thesis unclear, etc.)
- For each: what would need to change to reconsider (specific trigger, not vague)

## ETF Alternative

If the compared stocks share a common sector or theme, consider whether an ETF is a better option:

- **When ETF wins:** Can't pick a clear winner among the candidates, want diversification, limited capital, or planning long-term DCA into a theme
- **When individual stocks win:** High conviction in one name, want theta gang (ETFs usually have low IV), or the ETF dilutes the thesis with unrelated holdings

For the stocks being compared, identify:
- Any relevant ETFs that cover this group (e.g., SOXX/SMH for semis, IGV for software, XLE for energy)
- What % of the ETF matches your thesis vs. dead weight
- Whether the ETF has liquid options (for theta gang viability)
- **Verdict:** ETF or individual stocks — and why

Save the output to `research/comparisons/THEME-YYYY-MM-DD.md` (use lowercase theme name, e.g., `semiconductors-2026-05-10.md`, `software-2026-05-10.md`). For cross-sector comparisons, use a descriptive name (e.g., `best-csp-setups-2026-05-10.md`, `top-picks-overall-2026-05-10.md`).
