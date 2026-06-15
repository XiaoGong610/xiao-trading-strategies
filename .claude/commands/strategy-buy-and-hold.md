---
description: Buy & Hold strategy — entry planning, position sizing, and thesis tracking
---

Buy & Hold strategy analysis for: $ARGUMENTS

The argument is a ticker (e.g., "AAPL", "MSFT").

Assume the user already has conviction from `/research-stock` or `/plan-stock`. This skill focuses on execution: when to buy, how much, and what would change the thesis.

**Step 1:** Run the data script:
```bash
.venv/bin/python3 scripts/technicals.py $ARGUMENTS --options
```

Use the script's output for price, technicals, and support/resistance. Supplement with web search for recent news or valuation context.

**Step 2: Consult knowledge base**
- Read `knowledge/strategies/when-to-buy-and-hold.md` — apply the ideal setup checklist, Conviction × Valuation decision matrix, and lump-sum vs DCA routing
- Read `knowledge/frameworks/valuation.md` — use the Forward P/E by Sector table to assess if current valuation is cheap, fair, or expensive. Apply the RSI + Fwd P/E quick decision rule.
- Read `knowledge/signals/rsi-guide.md` — don't buy solely because RSI < 30 — check WHY it's oversold
- Read `knowledge/signals/ma-guide.md` — check SMA alignment for trend confirmation. Buy at 50 SMA in normal uptrend, 200 SMA for weak/early recovery. Avoid if price below all SMAs (bearish stack).
- Read `knowledge/signals/volume-guide.md` — confirm entry with volume (low volume pullback to support = healthy, high volume breakdown = distribution)
- Run `.venv/bin/python3 scripts/sector-momentum.py --json` and consult `knowledge/frameworks/sector-momentum.md` — sector momentum determines entry approach
- If IV Rank > 50 (from technicals.py --options output), note that initiating via CSP may be more capital-efficient — see `knowledge/signals/iv-rank-guide.md` decision matrix
- For AI supply chain stocks, read `knowledge/frameworks/capital-flow.md` for bottleneck positioning context

## Entry Analysis

- Current price vs. 52-week range — where are we?
- Key support levels — ideal buy zones
- RSI, SMA alignment — is it oversold or extended?
- Is now a good time to enter, or should you wait for a pullback?

## Position Sizing

- Suggest a position size as % of portfolio (consider conviction level and volatility)
- Full position vs. starter position — recommend scaling in if price is extended
- If starting small, suggest price levels to add more

## Entry Plan

- **Entry price / zone**: specific price range to buy
- **Full position target**: how many shares for a full-sized position
- **Scaling plan**: buy X shares now, add at $Y, add at $Z
- **Timeline**: enter now vs. wait for a level

## Thesis Tracker

- **Bull case**: 1-2 sentences — what drives upside
- **Bear case**: 1-2 sentences — what could go wrong
- **Thesis-break triggers**: specific events or price levels that would make you sell (not just "if it drops")
- **Review cadence**: how often to re-evaluate (quarterly earnings? monthly check?)

## Exit Rules

- **Take profit**: is there a target price or is this a hold-forever compounder?
- **Stop loss**: hard stop or thesis-based exit?
- **When to sell**: what would change your mind?

Save the output to `research/stocks/$TICKER.md` (use uppercase ticker as filename).
Start the entry with: `---` followed by `# TICKER — Buy & Hold Plan | YYYY-MM-DD`.
If the file already exists, prepend above previous entries (after YAML frontmatter). Never remove historical entries.

If creating a new file, add YAML frontmatter:
```yaml
---
ticker: TICKER
status: watching
added_date: YYYY-MM-DD
sector: (infer from research)
thesis: "(one-line summary)"
entry_target: (target buy price)
strategies: [buy-and-hold]
---
```

**Update index:** Run `.venv/bin/python3 scripts/update-index.py` to regenerate `0-INDEX.md`.
