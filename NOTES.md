# Project Notes

A living document for brainstorming, discussions, decisions, and TODOs.

---

## Decisions Made

### Skill Naming Convention (2026-05-09)
- `research-*` — research skills
- `strategy-*` — strategy-specific skills
- `trade-*` — portfolio/trade management
- `plan-*` — orchestrator skills
- `util-*` — utility tools

### Research Funnel (2026-05-09)
Cost-aware top-down funnel:
1. `/research-scan-market` (cheap) → many sectors
2. `/research-scan-sector` (moderate) → 5-10 candidates per sector
3. `/research-stock` (moderate) → deep-dive on candidates worth investigating
4. `/research-stock-compare` (cheap) → narrow to top 2-3
5. `/plan-stock` (expensive) → only run on stocks you're seriously considering

### Folder Structure (2026-05-10)
- `research/stocks/` — one file per stock, accumulates research + plans
- `research/sectors/` — sector scans
- `research/comparisons/` — head-to-head comparisons
- `portfolio/` — active positions
- `trades/` — closed trade log
- Status lifecycle: `researched → watching → in-portfolio → removed`
- `0-INDEX.md` groups stocks by actionability (Ready / Wait / Watching / Not Planned)

### Multi-Strategy Framework (2026-05-09)
Four strategies: Buy & Hold, DCA, LEAP Calls, Theta Gang. Research recommends strategy fit. Plan runs all applicable strategy skills and compares.

### DCA Preference (2026-05-10)
- Daily DCA by default
- Three approaches: Static Recurring, Limit Buys at Support, Hybrid Zone-Based
- For restricted stocks: plan per trading window, not per day

### AI Capital Flow Framework (2026-05-10)
Bottleneck progression: GPU → HBM → Cluster Scaling → Optical → next
Five tracks: Memory, I/O Interconnect, Optical, Power/Cooling, Custom ASIC
Key insight: "Don't chase hot spots — position ahead of the bottleneck shift."

### Sector Momentum Framework (2026-06-06)
Three-pillar quantitative momentum system: Mansfield Relative Strength (vs S&P 500), Weinstein Stage Analysis (30-week SMA), ROC momentum. Classifies sectors into: Accelerating Up, Steady Uptrend, Pulling Back in Uptrend, Sideways, Downtrend, Capitulation. Each maps to a strategy playbook. Sector momentum overrides stock-level RSI when they conflict. See `knowledge/frameworks/sector-momentum.md`.

### Regime-Aware Strategy Matrix (2026-06-06)
`/plan-stock` Phase 4a: sector momentum × stock RSI determines entry approach. Key insight: "Stock RSI 75" means momentum in an accelerating sector but overextension in a sideways sector. The sector context is the primary input for timing decisions.

### Crypto 4-Year Cycle Framework (2026-06-04)
BTC halving cycle analysis with on-chain indicators (MVRV, NUPL, Pi Cycle, Hash Ribbon, Puell Multiple). Current cycle peaked at $126K on Oct 6, 2025 (18 months post-halving — textbook). On-chain metrics suggest dampened drawdown with higher floor ($50-63K). Affects COIN/CRCL/MSTR position sizing. See `knowledge/frameworks/crypto-cycles.md`.

### Knowledge Base Wired Into All Skills (2026-06-14)
Full audit and update of all 14 skills. Every skill now consults relevant knowledge files instead of reinventing guidance inline. Key changes: added `--options` flag to technicals.py calls for IV data, added `dashboard.py` to trade lifecycle skills, fixed naming bugs (`/plan` → `/plan-stock`, `/roll` → `/strategy-theta-gang roll`), added CAPE to market regime, added crypto-cycle.py trigger in scan-market.

### GICS Sector Misclassification (2026-06-06)
META, GOOG, and APP are classified as Communication Services by GICS but functionally behave as Technology/Ad-Tech. When using sector momentum framework, treat these as hybrid — check both Communication (GICS) and Technology (functional). Don't blindly apply Communication downtrend signals to these names.

---

## Discussions & Ideas

### ETF vs. Individual Stocks (2026-05-10)
- `/research-scan-sector` includes relevant ETFs
- `/research-stock-compare` includes ETF alternative analysis
- ETFs win when: can't pick a winner, want diversification, limited capital
- Individual stocks win when: high conviction, want theta gang (need higher IV), ETF dilutes thesis

### Comparison Grouping (2026-05-10)
Comparisons can be within-sector or cross-sector. Saved to `research/comparisons/` with flexible naming.

### Knowledge Base — Hybrid Approach (2026-05-12)
Build a knowledge layer so the agent makes better decisions over time. Two components:

**1. Knowledge files** (start here) — human-readable reference docs that skills can consult:
```
knowledge/
  sectors/              — sector-specific logic (what metrics matter, cycle dynamics)
  strategies/           — when to use each strategy, edge cases, rules of thumb
  frameworks/           — reusable mental models (AI capital flow, valuation benchmarks)
  signals/              — how to interpret RSI, IV rank, P/E in different contexts
```

**2. Scoring scripts** (build later) — systematic ranking of stocks by composite signals:
- `scripts/screener.py` — input tickers, output ranked list by composite score
- Rules codified in Python, not prompt-dependent
- Consistent, fast, no token cost

**Why hybrid:** Knowledge files handle nuance and context (when does low P/E NOT mean cheap?). Scripts handle systematic scoring (rank 42 stocks). Skills reference both.

---

## TODOs

### 1. Capture Current Holdings & Trades ⬆️ HIGH
Import existing portfolio positions and trade history so `/trade-portfolio` has real data. Without this, the agent can't factor in existing positions when recommending strategies.

- [ ] Build `/trade-import` skill to bulk-load positions into `portfolio/` files
- [ ] Support importing from brokerage exports (CSV) or manual entry
- [ ] Populate frontmatter with strategy, entry date, cost basis, etc.

### 2. Refine & Test Trade Skills ⬆️ HIGH (depends on #1)
The trade lifecycle skills (`trade-open`, `trade-close`, `trade-review`, `trade-portfolio`) have been built but never tested with real data.

- [ ] Test `/trade-open` — log a real position, verify frontmatter and portfolio file creation
- [ ] Test `/trade-review` — review an active position, verify technicals integration
- [ ] Test `/trade-close` — close a position, verify P&L calculation and move to `trades/`
- [ ] Test `/trade-portfolio` — dashboard with active positions, trade history, and candidates summary
- [ ] Verify index (`0-INDEX.md`) status transitions work end-to-end
- [ ] Refine skills based on real usage — same way we improved research and plan skills

### 3. Risk & Portfolio Management ⬆️ HIGH
Prevent overconcentration and size positions properly. Critical before scaling up positions.

- [ ] **Correlation analysis** — measure how correlated watching/portfolio stocks are. Flag if 80% of positions move together (e.g., all AI semis drop on one NVDA miss)
- [ ] **Allocation framework** — define max % per stock, per sector, per theme. Enforce in `/plan-stock` recommendations
- [ ] **Position sizing calculator** — Kelly criterion or fixed-risk model. Input: conviction level, volatility, portfolio size → output: how many shares/contracts
- [ ] Add a portfolio risk section to `/trade-portfolio` dashboard showing sector concentration, correlation heatmap, and allocation vs. limits

### 4. Knowledge Base ✅ DONE (2026-06-14)
Build a knowledge layer for smarter decision-making. Start with knowledge files, add scoring scripts later.

**Phase 1 — Knowledge files (10/10 done):**
- [x] `knowledge/signals/rsi-guide.md`
- [x] `knowledge/signals/iv-rank-guide.md`
- [x] `knowledge/frameworks/ai-capital-flow.md`
- [x] `knowledge/frameworks/valuation.md` — includes CAPE/Shiller P/E (added 2026-05-26)
- [x] `knowledge/frameworks/crypto-cycles.md` — 4-year halving cycle + on-chain indicators (added 2026-06-04)
- [x] `knowledge/frameworks/sector-momentum.md` — Mansfield RS + Weinstein Stage + ROC (added 2026-06-06)
- [x] `knowledge/frameworks/macro-regimes.md` — now embedded in `/research-scan-market` regime classification
- [x] `knowledge/sectors/semiconductors.md` — cycle dynamics, sub-sectors, HBM/NAND drivers, key metrics, AI overlay (added 2026-06-14)
- [x] `knowledge/strategies/when-to-csp.md` — IV rank thresholds, delta/DTE rules, earnings avoidance, management rules (added 2026-06-14)
- [x] `knowledge/strategies/when-to-leaps.md` — IV environment, delta selection, vega risk, capital efficiency (added 2026-06-14)

**Phase 2 — Scoring scripts:**
- [x] `scripts/sector-momentum.py` — Mansfield RS + Weinstein Stage + ROC for all 11 GICS sectors
- [x] `scripts/sector-heatmap.py` — interactive Plotly treemap with period toggle
- [x] `scripts/crypto-cycle.py` — BTC on-chain cycle dashboard (MVRV, NUPL, cycle composite)
- [ ] `scripts/screener.py` — composite scoring (RSI + fwd P/E + gap-to-target + IV rank)
- [ ] Wire into `/research-stock-compare` for systematic ranking

### 5. Macro Regime Detection ✅ DONE (2026-06-06)
~~Different market regimes favor different strategies.~~

Implemented via:
- `/research-scan-market` — Market Regime table (S&P vs SMAs, VIX, Fear & Greed, yield curve, breadth) → 5 regime classifications with strategy implications
- `/research-scan-sector` — Sector Momentum & Trend section with 6 momentum classifications
- `/plan-stock` Phase 4a — Regime-aware strategy matrix (sector momentum × stock RSI)
- `scripts/sector-momentum.py` — quantitative sector momentum with Mansfield RS, Weinstein Stage, ROC
- `knowledge/frameworks/sector-momentum.md` — documents the three-pillar methodology

### 6. Market Intelligence Skills ➡️ MEDIUM
Add continuous monitoring capabilities beyond point-in-time research snapshots.

- [ ] **Whale tracking** — institutional buys/sells, 13F filings, insider transactions, unusual options activity (dark pool, large blocks)
- [ ] **Social sentiment** — monitor X (Twitter) for trending tickers and sentiment shifts, Reddit (r/wallstreetbets, r/options), StockTwits
- [ ] **News alerts** — breaking news, FDA decisions, earnings surprises, analyst upgrades/downgrades
- [ ] Consider using `/loop` for periodic monitoring

### 7. Scheduled Cloud Agents ➡️ MEDIUM
Set up Claude Code cloud triggers to run jobs on a recurring schedule.

- [ ] Daily: refresh technicals for all watching stocks
- [ ] Weekly: re-run `/research-scan-market` for sector rotation updates
- [ ] Pre-earnings: auto-flag stocks in watchlist with earnings approaching within 7 days
- [ ] Explore Claude Code `/schedule` for cron-based remote agent triggers

### 8. Visual Dashboard & Charts 🔄 IN PROGRESS
Interactive visualizations to help interpret signals at a glance. Two phases:

**Phase 1 — Plotly chart scripts (5 done, 1 remaining):**
- [x] `scripts/sector-heatmap.py` — sector performance treemap, market-cap weighted, period toggles, reading guide
- [x] `scripts/sector-momentum.py` — terminal dashboard with MRS, Weinstein Stage, ROC, momentum classification
- [x] `scripts/crypto-cycle.py` — BTC on-chain cycle dashboard (MVRV, NUPL, composite score)
- [x] `scripts/chart-watchlist.py` — RSI vs fwd P/E scatter plot, sector-colored, gap-to-target sizing, quadrant labels (added 2026-06-14)
- [x] `scripts/chart-earnings.py` — earnings calendar timeline with urgency color-coding (red/orange/yellow/green), terminal summary (added 2026-06-14)
- [ ] `scripts/chart-performance.py` — portfolio P&L over time (once we have trade history)

**Phase 2 — Streamlit web app (full interactive dashboard):**
- [ ] `scripts/app.py` — local web dashboard at `localhost:8501`
- [ ] Combines: data tables + charts + filters (sector, strategy, RSI range) in one page
- [ ] Built on top of existing `dashboard.py` logic
- [ ] Live-updating with `streamlit run scripts/app.py`
- [ ] Add `streamlit` to `.venv` dependencies

### 9. Multi-Timeframe Analysis ⬇️ LOW
Daily RSI tells one story; weekly/monthly tell another. Combining timeframes gives higher conviction signals.

- [ ] Add weekly and monthly RSI to dashboard alongside daily
- [ ] **Confluence signals** — daily oversold + weekly at support + monthly uptrend = highest conviction entry
- [ ] Update `scripts/dashboard.py` to fetch and display multi-timeframe RSI
- [ ] Add to knowledge base: `knowledge/signals/multi-timeframe.md`
- [ ] Consider adding weekly/monthly SMA alignment (e.g., price above monthly SMA 10 = long-term uptrend intact)

### 9. Leveraged ETF Strategy ⬇️ LOW
Evaluate leveraged single-stock ETFs as alternative to options. Examples: TSLL (2x TSLA), CONL (2x COIN), NVDL (2x NVDA).

- [ ] Research available leveraged ETFs for stocks on our watchlist
- [ ] Add leveraged ETF consideration to `/plan-stock`
- [ ] Document the tradeoffs: daily rebalancing decay, no options needed, volatility drag on long holds
- [ ] Consider as a strategy of its own (`/strategy-leveraged-etf`?) or fold into existing strategies

### 10. Tax Optimization 📅 SEASONAL
Maximize after-tax returns. Critical before year-end.

- [ ] **Wash sale tracking** — flag if you sell a stock at a loss and rebuy within 30 days
- [ ] **Tax-loss harvesting** — identify positions with unrealized losses that could offset gains
- [ ] **Short-term vs. long-term gains** — track holding periods (>1 year = favorable rate)
- [ ] **End-of-year review** — annual skill to scan portfolio for tax optimization before Dec 31
- [ ] Add to knowledge base: `knowledge/frameworks/tax-rules.md`
