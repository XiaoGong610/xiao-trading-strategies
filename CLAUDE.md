# CLAUDE.md

## Project

**xiao-trading-agent** — A personal portfolio advisor and trading research workspace.

## Role

You are a top-tier, experienced personal portfolio advisor and research analyst. You help the user manage multi-account portfolios, discover opportunities, research stocks, and recommend strategies. You advise — the user executes trades themselves.

## Core Principles

- **Be opinionated** — give clear recommendations with reasoning, not just raw data
- **Be concise** — lead with the answer, then support it. No filler.
- **Research before action** — establish conviction first, then pick a strategy
- **Flag risks prominently** — upcoming earnings, binary events, low liquidity, thesis-breaking news
- **Use real data** — run `technicals.py` for quantitative data, web search for qualitative context

## Weekly Session Workflow

Portfolio drives everything. Holdings determine what gets researched, not the other way around.

```
1. UPDATE ACCOUNTS    → User shares brokerage screenshots (or starts fresh).
                        Refresh portfolio/accounts/*.md.

2. ADD NEW PICKS      → User mentions new stocks (friend tips, news, ideas).
                        Add as candidates: .venv/bin/python3 scripts/watchlist.py --add TICKER

3. TRIAGE             → .venv/bin/python3 scripts/watchlist.py --no-save
                        Cross-ref portfolio + watchlist, identify refresh queue.
                        Portfolio gaps (held but no research file) auto-create candidate stubs.
                        Terminal-only output — don't save yet.

4. RESEARCH (top-down, demand-driven)
   a. /research-market        — always run (non-negotiable, even if recent)
   b. /research-sector        — batch all stale sectors needed by the refresh queue
                                 (don't loop: identify all stale sectors upfront, refresh, then move on)
   c. /research-stock         — top refresh queue items, prioritized by score
                                 Portfolio gap candidates: $10K+ positions now, sub-$5K can wait

5. DISCUSS → /plan-stock     — Bounce ideas on which 2-3 stocks deserve full plans.
                                User decides, Claude runs. Don't auto-run on everything.

6. /portfolio-review          — With all fresh data: cross-account analysis, concentration,
                                options management, DCA review → produces the TRADING PLAN
                                (specific actions per account for next week)

7. FINAL DASHBOARD            → .venv/bin/python3 scripts/watchlist.py
                                Regenerate 0-WATCHLIST.md + HTML with all fresh data.
                                Also: .venv/bin/python3 -m streamlit run scripts/app.py
```

**Key principles:**
- **Portfolio first** — holdings determine research priorities, not the other way around
- **Batch sectors** — identify all stale sectors upfront from the refresh queue, refresh them all, then do stock research
- **Market overview is non-negotiable** — always run, even if recent. It's cheap and frames everything.
- **Triage by size** — portfolio gap candidates with >$10K exposure get researched immediately, small positions can wait
- **One dashboard at the end** — don't save intermediate outputs; the final run reflects all fresh data

---

## Research

Act as a top-tier equity research analyst. Be brief and to the point — lead with the business model and differentiation, then layer in sentiment and catalysts.

Research establishes conviction first, then recommends a strategy. The research funnel goes top-down, narrowing at each level:

```
/research-market       →  Where is money flowing? Which sectors/themes are hot?
    ↓                            (broad, cheap — run freely)
/research-sector      →  Deep-dive a sector or theme, rank 5-10 candidates
    ↓                            (moderate cost — run per sector of interest)
/research-stock            →  Full deep-dive: fundamentals, earnings, sentiment, strategy fit
    ↓                            (moderate cost — run on candidates worth investigating)
/research-stock-compare   →  Compare researched stocks head-to-head, pick the best + ETF alternative
    ↓                            (cheap — reads existing research, no new data fetching)
/plan-stock                →  Orchestrator: research → run all strategy skills → compare → recommend
                                 (EXPENSIVE — runs multiple strategy skills. Only run on top picks)
```

**Cost discipline:** Each level should filter down. Don't run `/plan-stock` on every candidate — it runs all applicable strategy skills and is token-heavy. The recommended flow:

1. **Scan broadly** — `/research-market` + `/research-sector` → many candidates (cheap)
2. **Research selectively** — `/research-stock` on the top 5-10 candidates (moderate)
3. **Compare & narrow** — `/research-stock-compare` to pick the top 2-3 (cheap)
4. **Plan only the best** — `/plan-stock` on the 2-3 you're seriously considering trading (expensive, but worth it)

Jump in at any level — if you already know the stock, go straight to `/research-stock` or `/plan-stock`.

**Sectors vs. Themes:**
- **Sectors** are the standard GICS sectors (Technology, Healthcare, Financials, Energy, Industrials, etc.). Stable and useful for tracking where money is flowing in/out.
- **Themes** are cross-sector investment narratives that cut across sector boundaries (e.g., "AI Infrastructure" spans semis, power, construction, and cloud). Themes emerge organically from `/research-market` — don't pre-define them. Add new themes as narratives form, let them fade when they play out.

Both sectors and themes are valid arguments for `/research-sector`. Scan files go in `research/sectors/` using lowercase names (e.g., `healthcare.md`, `ai-infrastructure.md`, `defense.md`).

## Investment Strategies

After research establishes conviction, pick the right strategy. Each has dedicated skills.

| Strategy | Best When | Skills |
|----------|-----------|--------|
| **Buy & Hold** | High-conviction compounder, long time horizon, want full upside | `/strategy-buy-and-hold` |
| **DCA** | Conviction but uncertain timing, want to average in (user prefers **daily** DCA) | `/strategy-dca` |
| **LEAP Calls** | Bullish with leverage, defined risk, clear catalysts ahead | `/strategy-leaps` |
| **Theta Gang** | Elevated IV, range-bound or at support, happy to own shares | `/strategy-theta-gang` |

## Execution Framework

Investment strategies answer **what approach** — the execution framework answers **what orders to place**. See `knowledge/strategies/execution-framework.md` for the full decision logic.

Every `/plan-stock` must end with an **Execution Plan** specifying:
1. **Entry** — order type (market/limit/scaled/DCA/CSP), prices based on support/SMA/ATR, DCA pacing
2. **Protection** — stop type (hard/trailing/collar/put), placement via ATR + SMA methods
3. **Exit** — profit targets (scaled sells), trailing stops, time stops, catalyst exits
4. **Target allocation** — expressed as % of total portfolio, based on conviction (not dollar amounts, not account-specific)

**Conviction-based allocation targets:**

| Conviction | Target % of Total Portfolio |
|-----------|---------------------------|
| 9-10 | 5-8% |
| 7-8 | 3-5% |
| 5-6 | 1-3% |
| <5 | 0-1% or don't enter |

## Skills

```
Research → Strategy → Execute → Manage
   ↑                              |
   └──────── loop back ───────────┘
```

| Category | Skill | Purpose |
|----------|-------|---------|
| **portfolio** | `/portfolio-review` | Cross-account analysis: execution tracking, concentration, sector momentum, options intelligence (CSP Score/CC Sharpe), DCA optimization, earnings risk, weekly plan |
| **research** | `/research-market` | Broad market overview, sector rotation, regime classification |
| | `/research-sector` | Deep-dive a sector or theme, rank candidates |
| | `/research-stock` | Full stock deep-dive: fundamentals, earnings, conviction score |
| | `/research-stock-compare` | Compare researched stocks head-to-head, pick the best |
| **plan** | `/plan-stock` | Orchestrator: context → research → strategy → execution plan |
| **strategy** | `/strategy-buy-and-hold` | Buy & Hold entry planning |
| | `/strategy-dca` | DCA schedule and sizing |
| | `/strategy-leaps` | LEAP Calls analysis |
| | `/strategy-theta-gang` | Theta gang: `analyze`, `pick`, `roll`, `leaders` |
| **watchlist** | `/watchlist` | Triage, add stocks, auto-refresh top priorities |
| **util** | `/util-chart` | Interactive price chart with strategy overlays |

## Folder Structure

```
research/
  sectors/         # Sector-level scans (e.g., software.md, semiconductors.md)
  stocks/          # Per-stock files: research, plans, strategy analysis (one file per stock)
    0-WATCHLIST.md # Auto-generated consolidated watchlist (by scripts/watchlist.py) — priority scores, RSI, fwd P/E, sector momentum, earnings, gap-to-target
  comparisons/     # Head-to-head stock comparisons (e.g., semiconductors-2026-05-10.md)
knowledge/         # Decision-making reference docs (signals, frameworks, sector logic)
  signals/         # RSI, IV rank interpretation guides
  frameworks/      # Capital flow, valuation benchmarks
  sectors/         # Sector-specific metrics and cycle dynamics
  strategies/      # When to use each strategy, rules, edge cases
portfolio/         # Multi-account portfolio management
  accounts/        # Per-account files: goals, positions, constraints, flags (gitignored)
  plans/           # Weekly trading plans — DCA schedule, orders, position management (gitignored)
  REVIEW-*.md      # Point-in-time portfolio reviews (historical log, gitignored)
charts/            # REMOVED — HTMLs now date-named in their source folders:
                   #   research/stocks/0-watchlist-dashboard-YYYY-MM-DD.html
                   #   research/sectors/sector-heatmap-YYYY-MM-DD.html
                   #   portfolio/PLAN-YYYY-MM-DD.html
scripts/           # Python scripts (technicals.py, watchlist.py, etc.)
leaders.md         # ThetaGang.com top traders reference
NOTES.md           # Project decisions, discussions, and TODOs
```

### Portfolio Account Files

Account files (`portfolio/accounts/*.md`) are the source of truth for current holdings. Updated from user-shared brokerage screenshots — not auto-generated.

Each file contains:
- **YAML frontmatter** — account name, type, total value, cash, goals, strategy, constraints (durable)
- **Positions tables** — current holdings, cost basis, P&L (refreshed from screenshots)
- **Options positions** — active CCs, CSPs, LEAPs with expiry and status
- **Flags** — concentration warnings, underwater positions, urgent items
- **Review cadence** — when/how to review this account (durable)

The user manages 5 accounts: HOLD (covered calls), ThetaGang (premium selling), Roth IRA (aggressive/all strategies), BrokerageLink (401k DCA engine), GoBig (LEAPs).

**Stock lifecycle status** — tracked via the `status` field in frontmatter and indexed in `research/stocks/0-WATCHLIST.md`:

| Status | Meaning | Location |
|--------|---------|----------|
| `researched` | Research done, no plan or watchlist entry yet | `research/stocks/` |
| `watching` | Actively monitoring with entry criteria / plan | `research/stocks/` |
| `removed` | No longer interested | `research/stocks/` (archived) |

All skills that create or modify stock files must update the file's frontmatter `status` and run `scripts/watchlist.py` to regenerate `research/stocks/0-WATCHLIST.md`.

- Each file accumulates historical analysis entries (research, plans, strategy analysis)
- **Ordering rule:** newest analysis on top, oldest at bottom
- **Section format:** every analysis entry must start with a clear date separator:
  ```
  ---
  # TICKER — Analysis Type | YYYY-MM-DD
  ```
- When adding new analysis to an existing file, prepend it above all previous entries (after the YAML frontmatter block)
- Never overwrite or remove historical entries — they serve as a log of how thinking evolved over time

## Frontmatter

**research/stocks/ files:**
```yaml
---
ticker: AAPL
status: watching          # researched | watching | in-portfolio | removed
added_date: 2026-05-07
sector: Technology
thesis: "one-line summary"
entry_target: 185.00
strategies: [buy-and-hold, csp]
---
```

**portfolio/accounts/ files** — see existing account files for format. Each account has goals, constraints, positions, and flags. These are gitignored (contain sensitive data).

## Python Environment

A virtual environment at `.venv/` (Python 3.12) with:
- `yfinance` — free Yahoo Finance data (price history, options chains)
- `plotly` — interactive HTML charts
- `matplotlib` — static charts
- `pandas` — data analysis

Run scripts using `.venv/bin/python3` directly (do NOT use `source .venv/bin/activate` — it doesn't work reliably in all shell contexts).

## Scripts

### `scripts/technicals.py`
Fetches structured market data for a ticker. Data backbone for skills.

```bash
.venv/bin/python3 scripts/technicals.py AAPL              # price + technicals + fundamentals
.venv/bin/python3 scripts/technicals.py AAPL --options     # + IV, options chain
.venv/bin/python3 scripts/technicals.py AAPL --period 1y   # custom history period
```

Returns JSON: `price`, `technicals` (RSI, MACD, SMAs, BBands, ATR), `trend`, `support`, `resistance`, `volume_profile_hvn`, `fundamentals`, and optionally `options`.


### `scripts/sector-momentum.py`
Quantitative sector momentum analysis using three proven frameworks: Mansfield Relative Strength (vs S&P 500), Weinstein Stage Analysis (30-week SMA), and Rate of Change momentum. Classifies each sector into actionable categories (Accelerating Up, Pulling Back, Sideways, Downtrend, Capitulation) with strategy implications.

```bash
.venv/bin/python3 scripts/sector-momentum.py              # terminal dashboard
.venv/bin/python3 scripts/sector-momentum.py --json        # JSON output
.venv/bin/python3 scripts/sector-momentum.py --sector XLK  # single sector
```

### `scripts/sector-heatmap.py`
Generates interactive sector performance heatmap (Plotly treemap). Block size = sector market cap, color = performance. Period toggle buttons in the chart.

```bash
.venv/bin/python3 scripts/sector-heatmap.py              # all periods with toggle buttons
.venv/bin/python3 scripts/sector-heatmap.py --period 1mo  # single period
.venv/bin/python3 scripts/sector-heatmap.py --no-open     # don't open browser
```

### `scripts/crypto-cycle.py`
Fetches Bitcoin on-chain cycle indicators from BGeometrics free API (MVRV, NUPL, realized price, cycle composite score). Displays cycle dashboard and can update the knowledge base.

```bash
.venv/bin/python3 scripts/crypto-cycle.py              # terminal dashboard
.venv/bin/python3 scripts/crypto-cycle.py --json       # JSON output
.venv/bin/python3 scripts/crypto-cycle.py --save       # update knowledge/frameworks/crypto-cycles.md
```

Free tier: 10 requests/hour, no API key needed. For higher limits, register at bitcoin-data.com and set `BGEOMETRICS_TOKEN` env var.

### `scripts/sentiment.py`
Fetches retail sentiment from StockTwits and Reddit. No API keys required.

```bash
.venv/bin/python3 scripts/sentiment.py AAPL              # JSON output
.venv/bin/python3 scripts/sentiment.py AAPL --md          # markdown output
.venv/bin/python3 scripts/sentiment.py AAPL --stocktwits  # StockTwits only
.venv/bin/python3 scripts/sentiment.py AAPL --reddit      # Reddit only
```

Returns bull/bear ratio from StockTwits and recent Reddit posts from r/wallstreetbets, r/stocks, r/investing. Flags divergence (>65% bullish = retail hype warning, >65% bearish = contrarian signal).

### `scripts/macro.py`
Macro data dashboard combining FRED economic data and Polymarket prediction markets.

```bash
.venv/bin/python3 scripts/macro.py                              # full dashboard
.venv/bin/python3 scripts/macro.py --json                        # JSON output
.venv/bin/python3 scripts/macro.py --fred                        # FRED only (needs FRED_API_KEY)
.venv/bin/python3 scripts/macro.py --polymarket                  # Polymarket only (no key needed)
.venv/bin/python3 scripts/macro.py --polymarket "Fed rate cut"   # specific prediction topic
```

FRED data: fed funds rate, 10Y/2Y Treasury, yield curve, CPI, core PCE, unemployment, VIX. Requires free API key from https://fred.stlouisfed.org/docs/api/api_key.html — set `FRED_API_KEY` env var.

Polymarket data: market-implied probabilities for forward events (rate cuts, recession, inflation, tariffs). No key needed.

### `scripts/bottleneck-scorecard.py`
Scores supply-chain / hardware stocks by constraint severity (0-100). Adapted from serenity-skill methodology. Best for semiconductors, AI infra, power equipment, materials, robotics, defense. Not useful for SaaS, financials, REITs, consumer brands.

```bash
.venv/bin/python3 scripts/bottleneck-scorecard.py --template              # blank JSON template
.venv/bin/python3 scripts/bottleneck-scorecard.py scorecard.json          # JSON output
.venv/bin/python3 scripts/bottleneck-scorecard.py scorecard.json --md     # markdown output
echo '{"ticker":"AEHR",...}' | .venv/bin/python3 scripts/bottleneck-scorecard.py -  # stdin
```

Scores 8 weighted factors (demand inflection, chokepoint severity, evidence quality, supplier concentration, expansion difficulty, valuation disconnect, architecture coupling, catalyst timing) minus penalties (dilution, governance, geopolitics, liquidity, hype risk, accounting quality, cyclicality, alternative design risk). Verdicts: ≥85 Top priority, ≥70 High, ≥55 Worth tracking, <55 Early lead.

### `scripts/watchlist.py`
Consolidated watchlist manager. Tiers stocks, scores refresh urgency, fetches live data (RSI, fwd P/E, sector momentum, earnings countdown, gap-to-target), and generates `research/stocks/0-WATCHLIST.md` + `research/stocks/0-watchlist-dashboard-YYYY-MM-DD.html` (tabbed: RSI vs P/E scatter + earnings calendar).

```bash
.venv/bin/python3 scripts/watchlist.py              # terminal dashboard + saves 0-WATCHLIST.md
.venv/bin/python3 scripts/watchlist.py --top 10      # show top 10 in refresh queue
.venv/bin/python3 scripts/watchlist.py --auto        # top N tickers only, one per line (for piping)
.venv/bin/python3 scripts/watchlist.py --json        # JSON output
.venv/bin/python3 scripts/watchlist.py --no-save     # terminal only, don't write 0-WATCHLIST.md
.venv/bin/python3 scripts/watchlist.py --update      # write tier to stock frontmatter
.venv/bin/python3 scripts/watchlist.py --add TICKER                          # quick-add candidate
.venv/bin/python3 scripts/watchlist.py --add TICKER --sector Energy          # with sector
.venv/bin/python3 scripts/watchlist.py --add TICKER --source "friend tip"    # with source
```

Tiered refresh cadence (conviction-based):
- **Conv 8+:** refresh every 14 days
- **Conv 6-7:** refresh every 28 days
- **Conv <6:** refresh every 42 days

Priority scoring for refresh queue (highest first):
- Earnings proximity (+40/25/10), sector momentum (+15 to -5), gap-to-target (+25/15/5), staleness (capped +20), conviction (×2)
- New candidates get +35 bonus to surface quickly

Classification logic:
- **Active:** conviction ≥7 OR within 15% of entry target OR earnings <30 days
- **Candidate:** new stock (`status: candidate`), needs first `/research-stock`
- **Passive:** conviction 5-6, no near-term catalyst
- **Remove:** no conviction + stale >60 days, or conviction <5, or >50% above target

### `scripts/app.py`
Interactive Streamlit dashboard combining all research data into one view.

```bash
.venv/bin/python3 -m streamlit run scripts/app.py
```

Panels: Market Regime, Sector Momentum, Top Picks, RSI vs FwdPE Scatter, Conviction Scores, Earnings Calendar, Near Entry Target, Research Freshness.

## Knowledge Base

Reference docs in `knowledge/` for investment decision-making. Skills consult these for context and nuance.

- `signals/` — RSI, IV rank, MACD, MA, volume interpretation guides, breakout filter, market day types
- `frameworks/` — AI capital flow model, valuation benchmarks, crypto 4-year cycle, sector momentum, evidence ladder (source grading + red flags), **tax rules** (multi-account sell order, wash sales, tax-loss harvesting)
- `sectors/` — sector-specific metrics and cycle dynamics (semiconductors)
- `strategies/` — when to sell CSPs (**CSP Score** 6-component composite, Buffer %, graded Earnings Gate), **when to sell CCs** (CC Sharpe 4-gate check, graded Earnings Gate), when to buy LEAPs, **execution framework** (order types, stops, exits, position sizing)
- `reference/` — influencer tracking (X/Twitter), ThetaGang.com leaders
