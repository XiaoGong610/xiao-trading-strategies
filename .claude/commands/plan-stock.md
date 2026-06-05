---
description: Full pre-trade analysis plan — research, strategy fit, and trade setup
---

Run a complete pre-trade analysis for: $ARGUMENTS

The argument is just a ticker (e.g., "AAPL", "TSLA").

This is the **orchestrator** — it chains together the research funnel, strategy selection, and trade setup in one shot. It pulls from existing research when available and fills gaps.

---

## Phase 0: Market & Sector Context Check

Before planning any individual trade, check the macro and sector environment. These provide the context that shapes position sizing, strategy selection, and timing.

### 0a. Market Overview

1. Read `research/sectors/0-market-overview.md` — check the most recent Market Regime classification and Action Summary.
2. **Freshness check:**
   - **Fresh (<7 days):** Use as-is — reference regime, key risk, and next catalyst in the plan.
   - **Stale (>7 days):** Flag: "⚠️ Market overview is stale (X days old). Consider running `/research-scan-market` first." If user wants to proceed, note the gap and use the last known regime with a caveat.

**Regime gate:**
- **Strong Uptrend / Uptrend** → proceed with full position sizing
- **Choppy** → proceed but reduce position size by 25-50%, favor theta gang
- **Correction** → proceed only for DCA entries or CSP at deep support
- **Downtrend** → STOP — recommend waiting. Only proceed if user explicitly overrides.

If the regime gates you out, explain why and suggest what trigger to watch for (e.g., "Wait for S&P to reclaim 50-day SMA, then re-run `/plan-stock`").

### 0b. Sector / Theme Context

1. Identify the stock's sector or theme (e.g., semiconductors, crypto, software, energy).
2. Check `research/sectors/` for a matching sector scan file.
3. **Freshness check:**
   - **Fresh (<14 days):** Use it — pull theme lifecycle stage, sector risks, and any sector-level insights that affect this stock.
   - **Stale (>14 days) or missing:** Flag: "⚠️ No recent sector scan for [sector]. Consider running `/research-scan-sector [sector]` for broader context." If user wants to proceed, note the gap.

4. **Integrate sector context into the plan:** The sector scan provides critical framing:
   - **Theme lifecycle stage** — is this sector Emerging (aggressive) or Exhausting (avoid)?
   - **Sector-specific risks** — cycle dynamics, regulation, competition that affect all stocks in the space
   - **Relative positioning** — how does this stock rank vs. peers in the sector scan?
   - **Knowledge base** — check `knowledge/` for relevant frameworks (e.g., `crypto-cycles.md` for crypto stocks, `valuation.md` for P/E context)

**Document what you found:** In Phase 1, include a brief "Sector Context" section summarizing: lifecycle stage, sector-level risks/tailwinds, and any knowledge base insights that apply to this stock.

---

## Phase 1: Research

**Check for existing research:**
- Read `research/stocks/$TICKER.md` — if a recent `/research-stock` entry exists (<7 days old), summarize key findings and move to Phase 2.
- Pull the **Conviction Score** from the research file. If score < 5, flag: "Low conviction — consider whether this stock warrants a full plan."

**If no existing research, or research is stale (>7 days old):** Run `/research-stock $TICKER` first. This will:
- Run `technicals.py` for quantitative data
- Web search for qualitative info (business model, earnings, sentiment)
- Save full output to `research/stocks/$TICKER.md`
- Include a Strategy Fit recommendation and Conviction Score

Wait for the research to complete before proceeding.

**Sector Context** (from Phase 0b):
- Theme lifecycle stage: [from sector scan]
- Sector tailwinds/headwinds: [key factors affecting all stocks in this space]
- Knowledge base insights: [any relevant frameworks — e.g., crypto 4-year cycle, CAPE valuation, sector-specific metrics]
- Peer ranking: [where does this stock sit vs. sector scan candidates?]

**Conviction check** — based on the research output AND sector context:
- **Verdict:** Pass / Fail — do you have conviction? (Score ≥ 5 = Pass)
- If the sector lifecycle is **Exhausting**, require conviction ≥ 7 to proceed (higher bar for crowded trades)
- If Fail → stop here.

---

## Phase 2: Market Context & Timing

Use the script's `price`, `technicals`, `support`, `resistance`, and `options` data:
- Current stock price, 5-day and 1-month trend
- Technical levels: key support AND resistance
- Where is price relative to 52-week range?
- IV rank and IV percentile — is premium rich or cheap?
- Upcoming events: earnings date, ex-dividend date, binary catalysts
- Is now a good entry point, or should you wait?

---

## Phase 3: Run Strategy Analysis

Run the applicable strategy skills to get concrete trade setups. Which skills to run depends on what's available:

**Always run:**
- `/strategy-buy-and-hold $TICKER`
- `/strategy-dca $TICKER`

**Run if US-listed options are available AND the user is not restricted from trading options on this stock:**
- `/strategy-theta-gang analyze $TICKER`
- `/strategy-leaps $TICKER`

**Trading restrictions check:** If the user has restrictions on this stock (check memory — e.g., trading windows, no options), skip restricted strategies and note the constraint.

Each skill will produce its own detailed analysis (entry, sizing, exit rules, risk management). Collect all outputs before proceeding to Phase 4.

---

## Phase 4: Compare & Recommend

With all strategy outputs in hand, compare them and pick the best fit:

| Factor | Consider |
|--------|----------|
| Valuation | Stretched → favors DCA over lump sum. Fair/cheap → Buy & Hold viable |
| IV environment | High IV → theta gang. Low IV → LEAPs or Buy & Hold |
| Timing | At support → Buy & Hold. Uncertain → DCA. Pre-earnings → Wait |
| Options liquidity | Illiquid or unavailable → stock-based strategies only |
| Growth profile | Compounder → Buy & Hold/DCA. Range-bound → Theta Gang |
| User's position | Already owns shares? → CC or add via DCA. No position → CSP or Buy & Hold |

**Recommendation:** Pick the best strategy (or combination) with clear reasoning. Reference the specific trade setup from the winning strategy skill's output.

---

## Phase 5: Exit Plan

Every entry needs a predefined exit plan. Define these BEFORE entering the trade:

| Exit Type | Level | Action |
|-----------|-------|--------|
| **Profit target** | $X (+Y%) | Take profit / trail stop |
| **Thesis invalidation** | $X (-Y%) | Hard stop — thesis is broken, exit immediately |
| **Time stop** | Date | If thesis hasn't played out by this date, reassess |
| **Catalyst failure** | Event | If expected catalyst doesn't materialize, exit |

**Invalidation price** is NOT a trailing stop — it's the price where your fundamental thesis breaks (e.g., breaks below key support that held for months, or loses a critical customer).

---

## Phase 6: Final Checklist

- [ ] Market regime allows new entries? (Phase 0)
- [ ] Conviction in the company (score ≥ 5)? (Phase 1)
- [ ] Entry timing makes sense given technicals? (Phase 2)
- [ ] Strategy skills have been run and outputs collected? (Phase 3)
- [ ] Best strategy selected with clear reasoning? (Phase 4)
- [ ] Exit plan defined with invalidation + profit target? (Phase 5)
- [ ] No earnings/ex-div landmines in the trade window? (Phase 2)
- [ ] Position sizing appropriate for portfolio?

**Final Verdict:** Go / No-Go / Wait — with a one-line summary, recommended strategy, and next action.

If "Wait": specify the concrete trigger to revisit:
- **Price trigger:** "Wait for pullback to $X support, then re-run"
- **Event trigger:** "Wait for post-earnings May 11, then re-run `/plan-stock`"
- **Regime trigger:** "Wait for market regime to improve (S&P reclaims 50 SMA)"
- **Time trigger:** "Revisit in 2 weeks if thesis holds"

---

Save the output to `research/stocks/$TICKER.md` (use uppercase ticker as filename).
Start the entry with a date separator: `---` followed by `# TICKER — Pre-Trade Plan | YYYY-MM-DD`.
If the file already exists, prepend the new analysis above all previous entries (after the YAML frontmatter block). Never remove historical entries.

If creating a new file, add YAML frontmatter at the top:
```yaml
---
ticker: TICKER
status: watching
added_date: YYYY-MM-DD
sector: (infer from research)
thesis: "(one-line summary of why this stock is interesting)"
entry_target: (target entry price from Phase 4)
strategies: [(recommended strategy from Phase 3)]
---
```

If the file already exists and has frontmatter:
- If status is `researched`, update it to `watching` (plan promotes to watchlist)
- Update `entry_target` and `strategies` based on Phase 4 results
- Prepend the new analysis entry below the frontmatter

**Update index & dashboard:**
```bash
.venv/bin/python3 scripts/update-index.py && .venv/bin/python3 scripts/dashboard.py
```
