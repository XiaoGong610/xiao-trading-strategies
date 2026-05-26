# Reference Repos — Learning Notes

Two open-source Claude Code trading projects we can learn from. Cloned to `~/Workspace/Learning Resources/`.

---

## 1. claude-trading-skills (tradermonty)

**Repo**: `~/Workspace/Learning Resources/claude-trading-skills/`
**Philosophy**: "Decision-process OS" — Plan → Trade → Record → Review → Improve
**Scale**: 57 skills, 6 workflows, 480 Python scripts, 129 knowledge base files
**APIs**: FMP ($80/mo), FINVIZ, Alpaca, yfinance

### Skills (57 total)

#### Screening & Discovery (9)

| # | Skill | Description |
|---|-------|-------------|
| 1 | `vcp-screener` | Minervini Volatility Contraction Pattern screening on S&P 500 |
| 2 | `canslim-screener` | O'Neil CANSLIM growth stock methodology, 7-component analysis |
| 3 | `finviz-screener` | Build FinViz screener URLs from natural language |
| 4 | `value-dividend-screener` | High-quality dividend opportunities (3%+ yield, value metrics) |
| 5 | `dividend-growth-pullback-screener` | Dividend growth stocks at RSI oversold pullbacks (<40) |
| 6 | `earnings-calendar` | Upcoming earnings announcements via FMP API |
| 7 | `earnings-trade-analyzer` | Post-earnings 5-factor scoring (Gap, Trend, Volume, MAs) |
| 8 | `pead-screener` | Post-Earnings Announcement Drift pattern screening |
| 9 | `pair-trade-screener` | Cointegrated stock pairs for market-neutral stat arb |

#### Analysis & Research (7)

| # | Skill | Description |
|---|-------|-------------|
| 10 | `us-stock-analysis` | Comprehensive fundamentals + technicals + comparisons |
| 11 | `technical-analyst` | Weekly chart analysis: trends, S/R, probabilistic scenarios |
| 12 | `sector-analyst` | Sector rotation patterns and market cycle positioning |
| 13 | `theme-detector` | Trending market themes with lifecycle maturity tracking |
| 14 | `market-news-analyst` | Recent market-moving news analysis (past 10 days) |
| 15 | `market-environment-analysis` | Global market analysis (US, EU, Asia, forex, commodities) |
| 16 | `news-catalyst-analyst` | News/geopolitics/social signal impact assessment |

#### Market Timing & Signals (6)

| # | Skill | Description |
|---|-------|-------------|
| 17 | `market-top-detector` | Market top probability (0-100) via distribution days + deterioration |
| 18 | `ftd-detector` | Follow-Through Day signals for market bottom confirmation |
| 19 | `market-breadth-analyzer` | Breadth health score (0-100), 6 components |
| 20 | `uptrend-analyzer` | Uptrend Ratio Dashboard with 5-component composite |
| 21 | `ibd-distribution-day-monitor` | IBD Distribution Days for QQQ/SPY with exposure recs |
| 22 | `breadth-chart-analyst` | S&P 500 breadth index + uptrend ratio chart analysis |

#### Macro & Regime (3)

| # | Skill | Description |
|---|-------|-------------|
| 23 | `macro-regime-detector` | Structural macro regime transitions via cross-asset ratios |
| 24 | `us-market-bubble-detector` | Bubble risk via Minsky/Kindleberger framework |
| 25 | `economic-calendar-fetcher` | Upcoming economic events (Fed, employment, inflation, GDP) |

#### Portfolio & Position Management (7)

| # | Skill | Description |
|---|-------|-------------|
| 26 | `position-sizer` | Risk-based sizing: Fixed Fractional, ATR-based, Kelly Criterion |
| 27 | `portfolio-manager` | Portfolio analysis via Alpaca MCP (allocation, risk, rebalancing) |
| 28 | `exposure-coach` | Net exposure ceiling (0-100%) based on market regime |
| 29 | `breakout-trade-planner` | Minervini breakout plans with Alpaca order templates |
| 30 | `parabolic-short-trade-planner` | 3-phase parabolic exhaustion short screening (screen/plan/trigger) |
| 31 | `options-strategy-advisor` | Black-Scholes pricing, Greeks, P/L simulation, earnings strategies |
| 32 | `covered-call-strategy` | Systematic covered calls for income + cost basis reduction |

#### Dividend Investing (3)

| # | Skill | Description |
|---|-------|-------------|
| 33 | `kanchi-dividend-sop` | Kanchi-style dividend investing: screening + entry planning |
| 34 | `kanchi-dividend-review-monitor` | Forced-review triggers (T1-T5) for dividend portfolios |
| 35 | `kanchi-dividend-us-tax-accounting` | US dividend tax workflow (qualified vs ordinary, account placement) |

#### Institutional & Flow (2)

| # | Skill | Description |
|---|-------|-------------|
| 36 | `institutional-flow-tracker` | 13F filing analysis for smart money accumulation/distribution |
| 37 | `edge-signal-aggregator` | Aggregate + rank signals from multiple skills with weighted scoring |

#### Edge Research Pipeline (6)

| # | Skill | Description |
|---|-------|-------------|
| 38 | `edge-candidate-agent` | Generate edge research tickets from EOD observations |
| 39 | `edge-hint-extractor` | Extract edge hints from daily observations + news reactions |
| 40 | `edge-concept-synthesizer` | Abstract tickets into reusable edge concepts with invalidation signals |
| 41 | `edge-strategy-designer` | Convert edge concepts into strategy draft variants |
| 42 | `edge-strategy-reviewer` | Review strategy drafts for edge plausibility + overfitting |
| 43 | `edge-pipeline-orchestrator` | Orchestrate full edge research pipeline end-to-end |

#### Strategy & Backtesting (4)

| # | Skill | Description |
|---|-------|-------------|
| 44 | `backtest-expert` | Backtesting guidance with robustness testing + bias prevention |
| 45 | `strategy-pivot-designer` | Detect backtest stagnation, generate pivot proposals |
| 46 | `trade-hypothesis-ideator` | Falsifiable trade hypotheses with experiment designs + kill criteria |
| 47 | `scenario-analyzer` | 18-month investment scenarios from news headlines |

#### Memory & Postmortem (2)

| # | Skill | Description |
|---|-------|-------------|
| 48 | `signal-postmortem` | Post-trade outcome analysis, false positive tracking |
| 49 | `trader-memory-core` | Thesis lifecycle: screening → active → closed with P&L + MAE/MFE |

#### Infrastructure & Tools (6)

| # | Skill | Description |
|---|-------|-------------|
| 50 | `downtrend-duration-analyzer` | Historical downtrend duration analysis with interactive histograms |
| 51 | `data-quality-checker` | Validate data quality in analysis documents before publishing |
| 52 | `dual-axis-skill-reviewer` | Deterministic + LLM skill scoring (0-100) |
| 53 | `skill-designer` | Auto-generate new skill scaffolding |
| 54 | `skill-idea-miner` | Mine session logs for skill improvement ideas |
| 55 | `skill-integration-tester` | Validate multi-skill workflow compatibility |

#### Navigation & Synthesis (2)

| # | Skill | Description |
|---|-------|-------------|
| 56 | `stanley-druckenmiller-investment` | Synthesize 8 skill outputs into unified conviction score (0-100) |
| 57 | `trading-skills-navigator` | Router: recommend right workflow from natural-language goals |

### Workflows (6)

| Workflow | Cadence | Purpose |
|----------|---------|---------|
| `market-regime-daily` | Daily (15 min) | Breadth → uptrend → top detection → exposure decision |
| `swing-opportunity-daily` | Daily (30 min) | VCP screen → technical analysis → position sizing → thesis |
| `core-portfolio-weekly` | Weekly (60 min) | Portfolio review → dividend monitoring → thesis updates |
| `trade-memory-loop` | Per trade close | Thesis close → postmortem → lessons learned |
| `monthly-performance-review` | Monthly (90 min) | Stats → postmortem all closed → backtest validation |

---

## 2. TradingAgent (mylife126)

**Repo**: `~/Workspace/Learning Resources/TradingAgent/`
**Philosophy**: Goal-driven ($1M target), rules-based, share accumulation focus
**Scale**: 14 skills, 10 commands, 3 workflows
**APIs**: yfinance only (free)

### Skills (14 total)

| # | Skill | Category | Description |
|---|-------|----------|-------------|
| 1 | `stock-discovery` | Discovery | Discover, rank, and track high-potential stock candidates |
| 2 | `stock-evaluator` | Discovery | Go/no-go analysis for new stocks + accumulation strategy |
| 3 | `technical-analyst` | Analysis | Chart analysis: trend, S/R, probabilistic scenarios |
| 4 | `market-scanner` | Market | Daily market context (indices, sectors, regime, news) |
| 5 | `news-catalyst-analyst` | Market | News/geopolitics impact on specific stocks |
| 6 | `portfolio-tracker` | Portfolio | Brokerage CSV import + reconciliation + performance |
| 7 | `portfolio-cleanup` | Portfolio | Identify sell candidates (dead money, broken thesis) |
| 8 | `exposure-coach` | Portfolio | Net exposure (0-100%) based on market regime |
| 9 | `position-sizer` | Strategy | Risk-based sizing (Fixed Fractional, ATR-based) |
| 10 | `covered-call-strategy` | Strategy | Covered calls + CSPs for monthly income |
| 11 | `swing-accumulator` | Strategy | Score-based (0-10) trim/rebuy to grow share count |
| 12 | `scenario-analyzer` | Analysis | 3-scenario probability analysis (Base/Bull/Bear) |
| 13 | `signal-postmortem` | Memory | Analyze completed swing cycles for patterns |
| 14 | `financial-goal-planner` | Goals | $1M target tracking with milestones |

### Commands (10 total)

| Command | Purpose |
|---------|---------|
| `/status` | Unified portfolio dashboard |
| `/daily` | Market scan + swing signals + CC alerts |
| `/weekly` | Portfolio import + week review + forward outlook |
| `/check TICKER` | Quick swing signal with catalyst context |
| `/plan TICKER` | Detailed swing accumulation plan |
| `/evaluate TICKER` | Full go/no-go for new stock candidates |
| `/discover` | Multi-stock comparison + watchlist ranking |
| `/cleanup` | Identify sell candidates + capital redeployment |
| `/cc` | Covered call + CSP opportunities |
| `/positions` | GTC orders dashboard with gap analysis |

### Workflows (3 total)

| Workflow | Purpose |
|----------|---------|
| `daily-scan` | Market context → holdings check → discovery |
| `evaluate-stock` | Comprehensive stock evaluation |
| `weekly-portfolio-review` | Holdings review + postmortem + rebalancing |

---

## Key Patterns Worth Borrowing

### High Priority

| Pattern | Source | What It Does |
|---------|--------|--------------|
| **Distribution day gating** | Both | IBD method counts distribution days on SPY/QQQ, gates all buy decisions as circuit breaker |
| **Thesis lifecycle tracking** | Original | IDEA → ENTRY_READY → ACTIVE → CLOSED with MAE/MFE postmortem |
| **Action tracking** | Fork | Every suggestion gets SUGGESTED/EXECUTED/SKIPPED status for execution discipline |
| **Exposure coach** | Both | Market-level health check BEFORE any individual stock decision |

### Medium Priority

| Pattern | Source | What It Does |
|---------|--------|--------------|
| **Multi-skill workflows with gates** | Original | YAML-defined skill chains with decision gates and artifact dependencies |
| **Cost basis reduction tracking** | Fork | Tracks option income against each position, goal = $0 cost basis |
| **Catalyst modifiers** | Fork | +/-2 points adjusting quantitative scores based on news/events |
| **Theme lifecycle stages** | Both | Emerging → Accelerating → Trending → Mature → Exhausting |

### Lower Priority (interesting but not urgent)

| Pattern | Source | What It Does |
|---------|--------|--------------|
| **Edge research pipeline** | Original | 6-skill pipeline for systematic edge discovery |
| **Parabolic short planner** | Original | 3-phase FSM (screen → plan → intraday trigger) |
| **Skill auto-improvement** | Original | Daily automated scoring + PR creation via launchd |
| **Druckenmiller synthesis** | Original | Aggregates 8 skill outputs into single conviction score |

---

## Comparison: All Three Projects

| Aspect | claude-trading-skills | TradingAgent | xiao-trading-agent |
|--------|----------------------|--------------|---------------------|
| **Focus** | Broad toolkit | Goal-driven swing | Research-first |
| **Skills** | 57 | 14 | 16 (and growing) |
| **Data** | FMP + FINVIZ + Alpaca | yfinance only | yfinance only |
| **State** | YAML + JSON schemas | YAML | Markdown + YAML frontmatter |
| **Options** | Black-Scholes + Greeks | Conservative CC/CSP | Theta gang + LEAPS |
| **Market gating** | Breadth + regime + bubble | Distribution days | Not yet |
| **Screening** | VCP, CANSLIM, PEAD, dividend | Swing scoring (0-10) | Manual research funnel |
| **Postmortem** | MAE/MFE + lessons | Swing cycle analysis | Not yet |
| **Charts** | User screenshots | User screenshots | Generated Plotly HTML |
| **Unique strength** | Depth + edge pipeline | Simplicity + focus | Research funnel + strategy fit |
