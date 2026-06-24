# Reference Repos — Learning Notes

Open-source trading/investment skill projects we can learn from. Cloned to `~/Workspace/Learning Resources/`.

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

## 3. serenity-skill (muxuuu)

**Repo**: `~/Workspace/Learning Resources/serenity-skill/`
**GitHub**: https://github.com/muxuuu/serenity-skill
**Philosophy**: Supply-chain bottleneck hunting — start from a market narrative, walk through the real system, find the scarce layer, verify with hard evidence, rank what deserves attention
**Scale**: 1 skill (SKILL.md), 8 reference docs, 3 asset templates, 2 scripts, 3 examples
**APIs**: None (methodology-only — relies on host agent's web search, market data, and filing access)
**Origin**: Distilled from public Serenity / @aleabitoreddit X posts and research patterns

### Core Methodology

```
market story → system change → required parts → supply-chain layers
→ scarce constraints → public companies → evidence → repricing path
→ what could prove the idea wrong
```

### Reference Docs (8)

| File | Purpose |
|------|---------|
| `deep-research-workflow.md` | 8-step workflow: scope → system change → value chain → scarce layers → company universe → evidence → rank → explain |
| `evidence-ladder.md` | Source grading (strong/medium/weak), red flags, per-candidate evidence standard |
| `market-source-playbook.md` | Per-market source paths: US (SEC, shelf/ATM risk), A-shares (tenders, env approvals), HK, Taiwan, Japan, Korea, Europe |
| `serenity-dialogue-protocol.md` | Socratic stress-test mode — one question per turn, pushes thesis from story to proof |
| `output-style-and-language.md` | Plain-language output rules, mandatory "what could go wrong" section, judgment guardrails |
| `research-sources.md` | Curated source list: Agent Skills docs, Serenity public profile, case study companies (AXT, Sivers, Tower, Aehr) |
| `risk-and-compliance.md` | Investment research boundaries — no guaranteed returns, no trade commands, no MNPI |
| `public-profile-and-evaluation.md` | Public profile context and reliability notes |

### Assets & Scripts

| File | Purpose |
|------|---------|
| `assets/thesis-template.md` | Structured thesis memo: view, trend, system change, value-chain map, evidence table, "what market may be missing", financials, catalysts, risks |
| `assets/bottleneck-scorecard.json` | JSON schema for the scorecard (8 factors + 8 penalties, 0-5 each) |
| `assets/research-prompt-pack.md` | Pre-built prompts for theme scans, single-company challenges, comparisons, scorecard |
| `scripts/serenity_scorecard.py` | Local scoring script — 0-100 weighted score from JSON input, markdown output |
| `scripts/validate_skill.py` | Agent Skill structure validator |

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Layer-first ranking** | Rank value-chain layers before companies. Prevents "popular ticker list" syndrome. |
| **Scarce layer** | Company is interesting when customers cannot route around it — moat via constraint, not just quality |
| **Evidence strength labeling** | Strong / Medium / Weak / Needs checking — forces clarity on what you know vs. believe |
| **Red flag checklist** | 7 mechanical checks: single customer rumor, social-driven move, financing risk, vague customer, inventory divergence, margin contradiction, theme-washing |
| **"What the market may be missing"** | Current category → possible new category → why investors are slow → what triggers re-pricing |
| **US financing risk flags** | Shelf registration, ATM, convertible debt, SBC dilution, insider selling pattern |
| **Explicitly downgrade one popular area** | Every sector scan must name one obvious/popular area and explain why it ranks lower |
| **Bottleneck scorecard** | 8 weighted factors (demand, chokepoint, evidence, concentration, expansion, valuation, coupling, catalyst) minus penalties (dilution, governance, geopolitics, liquidity, hype, accounting, cyclicality, alt design risk) |

### What We Integrated (2026-06-23)

| Integration | Where | Description |
|-------------|-------|-------------|
| **Bottleneck scorecard** | `scripts/bottleneck-scorecard.py` | Adapted scoring script — 0-100 for supply-chain stocks. Runs conditionally in `/research-stock` for hardware/manufacturing sectors |
| **Evidence ladder + red flags** | `knowledge/frameworks/evidence-ladder.md` | Source grading, 7 red flags, per-candidate evidence standard. Red flags run on ALL stocks in `/research-stock` |
| **US financing risk flags** | `/research-stock` Red Flag Check + evidence-ladder.md | 5 dilution/financing checks (S-3, ATM, converts, SBC, insider selling). Noted in Risks, don't reduce conviction directly |
| **Value-chain layer ranking** | `/research-sector` | For supply-chain sectors: rank constrained layers before companies. 8-layer checklist + "explicitly downgrade one popular area" |
| **"What the market may be missing"** | `/research-stock` | Re-rating framework between Summary and Bottleneck Scorecard: current category → possible new category → why investors are slow → trigger |

### What We Didn't Take (and why)

| Item | Why Skipped |
|------|-------------|
| Thesis challenge / dialogue protocol | Interesting but not urgent — bear case section partially covers this. Could become a `/challenge` skill later |
| Market source playbook (non-US) | We're US-focused. Taiwan monthly revenue and Japan low-coverage signals are interesting but low priority |
| Research prompt pack | Pre-built prompts for their skill system — we have our own skill triggers |
| Deep research workflow (8-step) | Already embedded in our value-chain layer ranking addition |
| Full SKILL.md installation | Designed for generic Agent Skills clients — our skills are purpose-built Claude Code commands |

---

## 4. stock-skill / 美股大佬蒸馏 (destiny520537work)

**Repo**: `~/Workspace/Learning Resources/stock-skill/`
**Gitee**: https://gitee.com/destiny520537work/stock-skill
**Philosophy**: Distills 3 public US stock traders into a unified decision framework: supply chain (Serenity) × macro (TraderS) × technical execution (恨铁)
**Scale**: 1 SKILL.md + 4 trader files (serenity.md, tradersS.md, bei.md, combined.md)
**APIs**: None (methodology-only, relies on host agent's tools)
**Language**: Primarily Chinese with English concepts

### The Three Traders

| Trader | Handle | Focus | Core Question |
|--------|--------|-------|---------------|
| **Serenity** | @serenity (X) | Supply-chain bottleneck analysis | "Who in this chain is hardest to replace?" |
| **TraderS 缺德道人** | @Trader_S18 (X) | Macro-first judgment | "Is macro tailwind or headwind?" |
| **恨铁不成小猫猫** | 小红书 | Technical execution & discipline | "Is the volume-price-ATR confirming?" |

### 3-Step Decision Flow

```
Step 1 (TraderS): Is macro tailwind? → Yes → Step 2
Step 2 (Serenity): Is bottleneck logic valid? → Yes → Step 3
Step 3 (恨铁): Volume/price/ATR confirmed? → Yes → Enter
```

### Key Concepts

| Concept | Source | Description |
|---------|--------|-------------|
| **5-type market day classification** | 恨铁 | Trend / Range / Reversal / Munger / Event — classify before deciding how to enter |
| **True/false breakout filter** | 恨铁 | Volume >1.5x + ATR >1x average + moderate IV = true breakout |
| **3-phase entry** | 恨铁 | Probe (2-3/10) → Validate (add after confirmation) → Trend delivery (full size) |
| **Event Day rules** | 恨铁 | Wait for first shock wave, no counter-trend, must have stop, max 1 retry after loss |
| **Crypto as liquidity indicator** | TraderS | BTC direction + ETF flows + stablecoin market cap as second-layer macro verification |
| **12-dimension fundamental checklist** | 恨铁 | Cash flow > NI, margins vs peers, management track record, pledge ratio, related-party transactions, channel inventory |
| **Data provenance labeling** | Combined | Tag data as "user-provided" / "web search" / "⚠️ training memory — may be stale" |
| **Expectation gap analysis** | TraderS | What's priced in vs. reality → where is the gap? |

### What We Integrated (2026-06-23)

| Integration | Where | Description |
|-------------|-------|-------------|
| **Crypto liquidity triangulation** | `/research-market` Liquidity Check | BTC direction + ETF flows + stablecoin cap + 10Y yield as second-layer macro verification |
| **Market day classification** | `knowledge/signals/market-day-types.md` | 5-type system (Trend/Range/Reversal/Munger/Event) with Event Day discipline rules |
| **True/false breakout filter** | `knowledge/signals/breakout-filter.md` | 3-way filter (Volume >1.5x + ATR >1x + IV <50) with signal grades A-D |
| **Fundamental due diligence items** | `/research-stock` | Added: shareholder pledge ratio, core team turnover, related-party transactions, channel inventory truth |

### What We Didn't Take (and why)

| Item | Why Skipped |
|------|-------------|
| Serenity persona/supply-chain methodology | Already integrated from serenity-skill repo (more comprehensive) |
| 3-phase entry (probe/validate/deliver) | Our DCA + scaled limits approach serves the same purpose with less complexity |
| Debate mode between 3 personas | Fun UI feature but low analytical value for a personal advisor |
| Data provenance labeling | Good discipline but hard to enforce in skill prompts without adding noise. May revisit. |
| Forced output templates per persona | Our skills already have structured output templates |
| TraderS's expectation gap analysis | Covered by the "What the Market May Be Missing" section (from serenity-skill) |

---

## 5. TradingAgents (TauricResearch)

**Repo**: `~/Workspace/Learning Resources/TradingAgents-Framework/`
**GitHub**: https://github.com/TauricResearch/TradingAgents (88K stars)
**Philosophy**: Multi-agent LLM framework mirroring a real trading firm — analysts, researchers, trader, risk management, portfolio manager
**Scale**: Full Python package with LangGraph orchestration, 4 analyst agents, bull/bear researchers, 3-way risk debate, trader, portfolio manager
**APIs**: OpenAI/Claude/Gemini/Grok (LLM), Alpha Vantage, yfinance, FRED, Polymarket, StockTwits, Reddit
**Architecture**: LangGraph state machine with checkpointing, memory reflection, and structured output

### Agent Pipeline

```
4 Analysts (parallel) → Research Manager → Bull/Bear Debate
→ Trader → Risk Debate (aggressive/conservative/neutral) → Portfolio Manager
```

### Key Data Sources

| Source | API Key | What It Provides |
|--------|---------|------------------|
| **FRED** | Free (register) | Fed funds rate, Treasury yields, CPI, PCE, unemployment, M2, VIX — hard macro numbers |
| **Polymarket** | None | Market-implied probabilities for binary events (rate cuts, recession, tariffs, elections) |
| **StockTwits** | None | Retail sentiment with bull/bear labels per message — leading indicator |
| **Reddit** | None | r/wallstreetbets, r/stocks, r/investing — post volume and themes |
| **Alpha Vantage** | Free tier | Fundamentals, income statement, balance sheet, cash flow |

### Key Architectural Patterns

| Pattern | Description |
|---------|-------------|
| **Pre-fetch sentinel** | Social data fetched OUTSIDE the LLM call, injected as structured blocks — prevents hallucination when data is sparse |
| **Confidence degradation** | Sentiment output includes `confidence: low/medium/high` based on data quality — honest about signal strength |
| **Verified snapshot** | Technical analyst must call ground-truth endpoint; prompt says "if sources conflict, flag it, don't reconcile" |
| **Memory reflection loop** | After decisions, outcomes tracked. Next run for same ticker injects "lessons from prior decisions" to Portfolio Manager |
| **Cross-source divergence** | "If news is bearish but StockTwits is bullish, that mismatch is itself a signal" |
| **Two-LLM split** | Heavy model for analysis, light model for routing — token cost optimization |
| **Data provenance** | Every data point tagged with source — prevents stale training data from being cited as current |

### What We Integrated (2026-06-23)

| Integration | Where | Description |
|-------------|-------|-------------|
| **Retail sentiment script** | `scripts/sentiment.py` → `/research-stock` | StockTwits bull/bear ratio + Reddit posts. Flags divergence (>65% bullish = hype, >65% bearish = contrarian) |
| **Macro data script** | `scripts/macro.py` → `/research-market` | FRED dashboard (8 key indicators) + Polymarket predictions (rate cuts, recession, inflation, tariffs) |
| **Memory reflection loop** | `/plan-stock` Phase 0c | Reads prior plans and portfolio reviews for same ticker, extracts lessons to avoid repeating mistakes |
| **Anti-hallucination prompt** | `/plan-stock` Phase 2 | "Treat technicals.py as source of truth. If sources conflict, flag it, don't reconcile." |
| **Data provenance rule** | `/research-market` | Tag numbers as [FRED], [Polymarket], [web search]. Flag training memory with ⚠️ |

### What We Didn't Take (and why)

| Item | Why Skipped |
|------|-------------|
| LangGraph orchestration | We use Claude Code skills, not a Python pipeline |
| Multi-agent debate (bull/bear + risk) | Our bull/bear case sections cover this; full debate is token-heavy for marginal insight |
| Two-LLM architecture | We use one model; relevant if token cost becomes a concern |
| Structured output schemas | Our skills output markdown to files, not typed JSON |
| Alpha Vantage integration | We use yfinance (free, no key); AV has better fundamentals but requires API key |
| Five-tier rating (Buy/Overweight/Hold/Underweight/Sell) | Our conviction + allocation table already maps to this implicitly |

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

## Comparison: All Five Projects

| Aspect | claude-trading-skills | TradingAgent | serenity-skill | stock-skill | TradingAgents (Tauric) | xiao-trading-agent |
|--------|----------------------|--------------|----------------|-------------|----------------------|---------------------|
| **Focus** | Broad toolkit | Goal-driven swing | Bottleneck hunting | 3-trader distillation | Multi-agent firm | Research-first advisor |
| **Scale** | 57 skills | 14 skills | 1 skill (deep) | 4 trader files | Full Python pipeline | 16 skills (growing) |
| **Data** | FMP + FINVIZ + Alpaca | yfinance | Host agent's tools | Host agent's tools | yfinance + FRED + Polymarket + StockTwits | yfinance + FRED + Polymarket + StockTwits |
| **State** | YAML + JSON | YAML | Stateless | Stateless | LangGraph + SQLite | Markdown + YAML |
| **Options** | Black-Scholes | CC/CSP | N/A | N/A | N/A | Theta gang + LEAPS |
| **Gating** | Breadth + regime | Distribution days | N/A | Macro → supply chain → technical | 3-way risk debate | Sector momentum + regime |
| **Evidence** | Data quality checker | N/A | Ladder + red flags | N/A | Memory reflection | Integrated from all |
| **Unique** | Edge pipeline | Simplicity | Bottleneck scoring | 3-persona debate | Data source breadth | Research funnel + execution |
