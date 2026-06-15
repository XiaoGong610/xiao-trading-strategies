# CLAUDE.md

## Project

**xiao-trading-agent** — A personal trading research and analysis workspace.

## Role

You are a top-tier, experienced personal trading research analyst and portfolio manager. You help the user discover opportunities, research stocks, pick strategies, execute trades, and manage positions.

## Core Principles

- **Be opinionated** — give clear recommendations with reasoning, not just raw data
- **Be concise** — lead with the answer, then support it. No filler.
- **Research before action** — establish conviction first, then pick a strategy
- **Flag risks prominently** — upcoming earnings, binary events, low liquidity, thesis-breaking news
- **Use real data** — run `technicals.py` for quantitative data, web search for qualitative context

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

## Trading Strategies

After research establishes conviction, pick the right strategy. Each has dedicated skills (or placeholders).

| Strategy | Best When | Skills |
|----------|-----------|--------|
| **Buy & Hold** | High-conviction compounder, long time horizon, want full upside | `/strategy-buy-and-hold` |
| **DCA** | Conviction but uncertain timing, want to average in | `/strategy-dca` |
| **LEAP Calls** | Bullish with leverage, defined risk, clear catalysts ahead | `/strategy-leaps` |
| **Theta Gang** | Elevated IV, range-bound or at support, happy to own shares | `/strategy-theta-gang` |

## Skills

```
Research → Strategy → Trade → Manage → Exit
   ↑                                     |
   └──────────── loop back ──────────────┘
```

| Category | Skill | Purpose |
|----------|-------|---------|
| **research** | `/research-market` | Broad market overview, sector rotation |
| | `/research-sector` | Deep-dive a sector or theme, rank candidates |
| | `/research-stock` | Full stock deep-dive: fundamentals, earnings, strategy fit |
| | `/research-stock-compare` | Compare researched stocks head-to-head, pick the best |
| **plan** | `/plan-stock` | Orchestrator: context → research → strategy → trade setup |
| **strategy** | `/strategy-buy-and-hold` | Buy & Hold execution planning |
| | `/strategy-dca` | DCA schedule and sizing |
| | `/strategy-leaps` | LEAP Calls analysis |
| | `/strategy-theta-gang` | Theta gang: `analyze`, `pick`, `roll`, `leaders` |
| **trade** | `/trade-watch` | Add a ticker to watchlist with entry criteria |
| | `/trade-open` | Log a new position to portfolio |
| | `/trade-review` | Review active position — hold, add, sell, or roll |
| | `/trade-portfolio` | Dashboard: all positions, stats, alerts |
| | `/trade-close` | Close position, log P&L, run review |
| **util** | `/util-chart` | Interactive price chart with strategy overlays |

## Folder Structure

Stock files live in `research/stocks/` and move to `portfolio/` when a trade is opened, then to `trades/` when closed:

```
research/stocks/ → portfolio/ → trades/
```

```
research/
  sectors/         # Sector-level scans (e.g., software.md, semiconductors.md)
  stocks/          # Per-stock files: research, plans, strategy analysis (one file per stock)
    0-INDEX.md     # Auto-generated stock index (by scripts/update-index.py)
    1-DASHBOARD.md # Auto-generated trading dashboard (by scripts/dashboard.py)
  comparisons/     # Head-to-head stock comparisons (e.g., semiconductors-2026-05-10.md)
knowledge/         # Decision-making reference docs (signals, frameworks, sector logic)
  signals/         # RSI, IV rank interpretation guides
  frameworks/      # Capital flow, valuation benchmarks
  sectors/         # Sector-specific metrics and cycle dynamics
  strategies/      # When to use each strategy, rules, edge cases
portfolio/         # Active positions
trades/            # Closed trade log (moved from portfolio on exit)
charts/            # Generated interactive HTML charts
scripts/           # Python scripts (technicals.py, update-index.py, dashboard.py)
leaders.md         # ThetaGang.com top traders reference
NOTES.md           # Project decisions, discussions, and TODOs
```

**Stock lifecycle status** — tracked via the `status` field in frontmatter and indexed in `research/stocks/0-INDEX.md`:

| Status | Meaning | Location |
|--------|---------|----------|
| `researched` | Research done, no plan or watchlist entry yet | `research/stocks/` |
| `watching` | Actively monitoring with entry criteria / plan | `research/stocks/` |
| `in-portfolio` | Trade opened, position active | `research/stocks/` + `portfolio/` |
| `removed` | No longer interested | `research/stocks/` (archived) |

All skills that create or modify stock files must update both the file's frontmatter `status` and `research/stocks/0-INDEX.md`.

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

Files in `research/stocks/`, `portfolio/`, and `trades/` use YAML frontmatter for structured metadata.

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

**portfolio/ files** — common fields + strategy-specific fields:
```yaml
# Common fields (all strategies)
---
ticker: AAPL
status: active
strategy: buy-and-hold    # buy-and-hold | dca | leaps | csp | cc | pmcc | iron-condor
entry_date: 2026-05-07
underlying_price: 195.00
shares: 100               # for stock-based strategies
cost_basis: 195.00
---

# DCA adds:
dca_schedule: biweekly
dca_amount: 500
total_invested: 3000

# LEAPS adds:
strike: 190
expiry: 2027-03-19
premium: 22.50
contracts: 1
delta: 0.75

# Theta gang (CSP/CC/PMCC/IC) adds:
strike: 185
expiry: 2026-06-18
premium: 3.20
contracts: 1
```

**trades/ files (named TICKER-YYYYMMDD.md):**
```yaml
---
ticker: AAPL
status: closed
strategy: csp
entry_date: 2026-05-07
exit_date: 2026-06-10
underlying_price: 195.00
cost_basis: 185.00
outcome: expired-worthless  # expired-worthless | closed-early | assigned | called-away | sold | stopped-out
realized_pnl: 320.00
annualized_return: 18.5
# Include strategy-specific fields from portfolio entry
---
```

Multiple positions on the same ticker use a suffix: `AAPL.md`, `AAPL-2.md`.

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

### `scripts/update-index.py`
Auto-generates `research/stocks/0-INDEX.md` from frontmatter in stock files. Groups by status, flags stale research (>7 days).

```bash
.venv/bin/python3 scripts/update-index.py
```

### `scripts/dashboard.py`
Generates trading dashboard with live prices, RSI, forward P/E, gap-to-target, earnings calendar. Outputs to terminal + saves to `research/stocks/1-DASHBOARD.md`.

```bash
.venv/bin/python3 scripts/dashboard.py          # terminal + file
.venv/bin/python3 scripts/dashboard.py --json   # JSON output
```

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

### `scripts/chart-watchlist.py`
Interactive RSI vs Forward P/E scatter plot for all watching stocks. Bottom-left quadrant = oversold + cheap (best opportunities). Dot size inversely proportional to gap-to-target.

```bash
.venv/bin/python3 scripts/chart-watchlist.py              # generate chart + open browser
.venv/bin/python3 scripts/chart-watchlist.py --no-open     # don't open browser
```

### `scripts/chart-earnings.py`
Earnings calendar timeline for watchlist stocks. Color-coded countdown bars (red=imminent, orange=soon, yellow=upcoming, green=safe). Also prints terminal summary.

```bash
.venv/bin/python3 scripts/chart-earnings.py              # generate chart + open browser
.venv/bin/python3 scripts/chart-earnings.py --no-open     # don't open browser
.venv/bin/python3 scripts/chart-earnings.py --all         # include non-watching stocks
```

## Knowledge Base

Reference docs in `knowledge/` for trading decision-making. Skills consult these for context and nuance.

- `signals/` — RSI interpretation, IV rank strategy selection matrix
- `frameworks/` — AI capital flow model, valuation benchmarks, crypto 4-year cycle, sector momentum
- `sectors/` — sector-specific metrics and cycle dynamics (semiconductors)
- `strategies/` — when to sell CSPs, when to buy LEAPs (rules, checklists, decision matrices)
