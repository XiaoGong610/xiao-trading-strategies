# xiao-trading-agent

A personal trading research and analysis workspace powered by [Claude Code](https://claude.ai/code).

## What This Is

A set of Claude Code custom skills for stock research and multi-strategy trading. The skills use `technicals.py` for quantitative data and web search for qualitative context. The repo is organized around a trading workflow: research, plan, execute, manage, exit, repeat.

## Skills

### Research
| Command | Description |
|---------|-------------|
| `/research-scan-market` | Broad market overview — sector rotation, money flow, hot themes |
| `/research-scan-sector software` | Deep-dive a sector or theme, rank 5-10 candidates |
| `/research-stock AAPL` | Full stock deep-dive — fundamentals, earnings, sentiment, strategy fit |
| `/research-stock-compare AAPL, TSLA, NVDA` | Compare stocks head-to-head, rank by opportunity, ETF alternative |

### Planning
| Command | Description |
|---------|-------------|
| `/plan-stock AAPL` | Orchestrator — context, research, strategy selection, trade setup |

### Strategy
| Command | Description |
|---------|-------------|
| `/strategy-buy-and-hold AAPL` | Entry planning, position sizing, thesis tracking |
| `/strategy-dca AAPL 10000` | DCA schedule, sizing, acceleration/pause rules |
| `/strategy-leaps AAPL` | LEAP calls — strike/expiry selection, risk management |
| `/strategy-theta-gang analyze AAPL` | Options environment, recommended trades, go/no-go |
| `/strategy-theta-gang pick AAPL CSP` | Compare strike/expiry combos |
| `/strategy-theta-gang roll AAPL 170P 2026-05-16 CSP` | Analyze whether to roll a position |
| `/strategy-theta-gang leaders AAPL` | Check what top thetagang.com traders are doing |

### Trade Management
| Command | Description |
|---------|-------------|
| `/trade-watch AAPL` | Add a stock to the watchlist with entry criteria |
| `/trade-open AAPL CSP 185P 2026-06-18 3.20` | Log a new position to the portfolio |
| `/trade-review AAPL` | Review an active position — hold, add, sell, or roll? |
| `/trade-portfolio` | Dashboard — all positions, alerts, stats |
| `/trade-close AAPL expired-worthless` | Close a position, calculate P&L, run trade review |

### Utility
| Command | Description |
|---------|-------------|
| `/util-chart AAPL 6mo buy=185 sell=220` | Interactive price chart with strategy overlays |

## Folder Structure

```
research/
  sectors/           # Sector-level scans (gitignored)
  stocks/            # Per-stock research & plans (gitignored)
    0-INDEX.md       # Auto-generated stock index
    1-DASHBOARD.md   # Auto-generated trading dashboard
  comparisons/       # Head-to-head stock comparisons (gitignored)
knowledge/           # Decision-making reference docs (committed)
  signals/           # RSI, IV rank, volume, moving averages, MACD guides
  frameworks/        # Capital flow, valuation, sector momentum, crypto cycles, risk metrics
  sectors/           # Sector-specific metrics and cycle dynamics (semiconductors)
  strategies/        # Strategy rules — CSP, LEAPs, Buy & Hold, DCA
portfolio/           # Active positions (gitignored)
trades/              # Closed trade log (gitignored)
charts/              # Generated HTML charts (gitignored)
scripts/             # Python scripts (committed)
  technicals.py      # Market data fetcher (price, technicals, options)
  update-index.py    # Auto-generate 0-INDEX.md from frontmatter
  dashboard.py       # Trading dashboard with live prices, RSI, fwd P/E
  sector-momentum.py # Mansfield RS + Weinstein Stage + ROC momentum
  sector-heatmap.py  # Interactive Plotly sector performance treemap
  crypto-cycle.py    # BTC on-chain cycle dashboard (MVRV, NUPL)
  chart-watchlist.py # RSI vs fwd P/E scatter plot for watchlist
  chart-earnings.py  # Earnings calendar timeline with urgency colors
.claude/commands/    # Claude Code custom skills (committed)
leaders.md           # ThetaGang.com top traders reference
NOTES.md             # Project decisions, discussions, and TODOs
```

## Knowledge Base

Reference docs in `knowledge/` that skills consult for decision-making. All skills are wired to read the relevant knowledge files automatically.

| File | Purpose |
|------|---------|
| `signals/rsi-guide.md` | RSI interpretation — sector beta, trend context, common mistakes |
| `signals/iv-rank-guide.md` | IV Rank thresholds, IV Rank × RSI decision matrix for strategy selection |
| `signals/volume-guide.md` | Volume confirmation — relative volume, HVN/LVN, capitulation signals |
| `signals/ma-guide.md` | SMA 20/50/200 alignment, golden/death cross, entry level selection |
| `signals/macd-guide.md` | MACD crossovers, divergences, histogram momentum |
| `frameworks/capital-flow.md` | AI supply chain: 9-track bottleneck progression, demand timeline, Qual cycle, 3-question checklist |
| `frameworks/valuation.md` | Forward P/E benchmarks by sector, CAPE/Shiller P/E, PEG ratio |
| `frameworks/sector-momentum.md` | Mansfield RS + Weinstein Stage + ROC — three-pillar momentum system |
| `frameworks/crypto-cycles.md` | BTC 4-year halving cycle, on-chain indicators (MVRV, NUPL) |
| `frameworks/risk-metrics.md` | Sharpe, Sortino, Alpha, Beta, Max Drawdown — portfolio risk assessment |
| `sectors/semiconductors.md` | Semi cycles, Qual cycle trading, optical sub-layer, AI architecture transitions |
| `strategies/when-to-csp.md` | CSP setup checklist, IV×RSI matrix, management rules, position sizing |
| `strategies/when-to-leaps.md` | LEAP delta/expiry selection, vega risk, IV<30 gate, capital efficiency |
| `strategies/when-to-buy-and-hold.md` | Lump-sum vs DCA routing, conviction sizing, SMA entries, sell triggers |
| `strategies/when-to-dca.md` | RSI × sector pacing matrix, budget planning, acceleration/pause rules |

## Setup

1. Clone this repo
2. Use with [Claude Code](https://claude.ai/code) — the skills are automatically available as slash commands
3. Set up the Python environment: `python3 -m venv .venv && pip install yfinance plotly matplotlib pandas numpy`
4. Run the dashboard: `.venv/bin/python3 scripts/dashboard.py`

Analysis files are gitignored since they contain personal trading data. Knowledge base and scripts are committed.
