# xiao-trading-strategies

A personal trading research and analysis workspace powered by [Claude Code](https://claude.ai/code).

## What This Is

A set of Claude Code custom skills for stock research and theta gang options trading. The skills use web search to gather live market data and produce structured, opinionated analysis.

## Skills

### Stock Research
| Command | Description |
|---------|-------------|
| `/research AAPL` | Strategy-agnostic stock fundamentals (growth, earnings, sentiment, bull/bear case) |
| `/earnings AAPL` | Latest earnings call summary and key takeaways |

### Theta Gang Analysis
| Command | Description |
|---------|-------------|
| `/plan AAPL` | Full pre-trade pipeline — conviction check, options environment, strategy selection (both CSP and CC paths), strike/expiry recommendation, final checklist |
| `/theta-gang AAPL` | Pure options environment analysis (IV rank, Greeks, premiums, go/no-go) |
| `/strike-picker AAPL CSP` | Compare multiple strike/expiry combos side by side |
| `/scanner AAPL, TSLA, NVDA` | Rank a watchlist of stocks for best theta gang setup |
| `/roll AAPL 170P 2026-05-16 CSP` | Analyze whether to roll an existing position |
| `/review-trade AAPL CSP 170P ...` | Post-trade review with Sortino/Sharpe/max drawdown tracking |
| `/check-leaders AAPL` | Check what top thetagang.com traders are doing on a ticker |

## Theta Gang Rules Baked In

- Target 30-45 DTE (theta decay sweetspot)
- Delta 0.20-0.30 for selling (70-80% probability of profit)
- Close at 50% profit if reached in half the time
- Only sell puts at a price you'd be happy owning at
- Avoid earnings and ex-dividend dates
- Roll only if still bullish and for a net credit
- Track performance with Sortino Ratio (primary), max drawdown, and Sharpe Ratio

## Folder Structure

```
.claude/commands/    # Claude Code custom skills
research/            # Stock research files (local only, gitignored)
theta-gang/          # Theta gang analysis files (local only, gitignored)
```

## Setup

1. Clone this repo
2. Use with [Claude Code](https://claude.ai/code) — the skills are automatically available as slash commands

Analysis files are gitignored since they contain personal trading data.
