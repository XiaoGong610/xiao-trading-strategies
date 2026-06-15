---
description: Deep-dive research on a stock
---

Research the stock: $ARGUMENTS

This is a strategy-agnostic fundamentals and sentiment analysis. Focus on whether this is a good company to have conviction in — the user may use the research to inform any strategy (DCA, theta gang, buy-and-hold, etc.). Do NOT cover options-specific analysis (IV, Greeks, strikes, premiums).

**Step 1:** Run the data script to get current price, technicals, and fundamentals:
```bash
.venv/bin/python3 scripts/technicals.py $ARGUMENTS --options
```

**Step 2:** Use web search to gather qualitative information (news, earnings, analyst opinions, institutional activity).

**Step 3: Consult knowledge base**
- Read `knowledge/signals/rsi-guide.md` for RSI interpretation (sector beta differences, trend context, common mistakes)
- Read `knowledge/signals/ma-guide.md` — check SMA alignment (bullish stack vs tangled) and which SMA to use for entry levels
- Read `knowledge/signals/volume-guide.md` — validate price moves with relative volume (>2x avg = institutional, <0.5x = ignore)
- Read `knowledge/signals/macd-guide.md` — check for divergences to strengthen Technical Outlook scenarios
- Read `knowledge/frameworks/valuation.md` for sector-appropriate P/E benchmarks
- If the stock is in semiconductors, read `knowledge/sectors/semiconductors.md` for cycle signals and key metrics
- If the stock is AI supply chain related, read `knowledge/frameworks/capital-flow.md` for bottleneck positioning

Combine all sources to cover the following sections:

---

## Quick Screen (5 questions — gate before deep dive)

Answer these 5 yes/no questions first. If 3+ are "No", stop here and mark as **PASS** — don't waste time on a deep dive.

| # | Question | Answer |
|---|----------|--------|
| 1 | Revenue growing >10% YoY (or accelerating)? | |
| 2 | Stock above 200-day SMA (long-term uptrend intact)? | |
| 3 | No earnings within 7 days (avoid binary risk)? | |
| 4 | Clear catalyst or thesis in next 3-6 months? | |
| 5 | Market cap >$2B (sufficient liquidity)? | |

**Result:** PASS (stop) / PROCEED (continue to deep dive)

If PASS: write a brief 2-3 line summary of why this stock doesn't pass the screen, save to file, and stop.

---

## Company Overview
- What the company does, sector, market cap
- Key products/services and revenue breakdown
- Competitive moat (network effects, switching costs, scale, IP, brand)

## Growth & Financials
- Revenue and earnings growth (recent quarters + YoY)
- Margins (gross, operating, net) and trends
- Balance sheet health (debt, cash position)
- Free cash flow
- How does this compare to sector peers? (above/below average)

## Recent Earnings
- Revenue: actual vs. estimate, YoY growth
- EPS: actual vs. estimate, YoY growth
- Management commentary: tone, strategic priorities, key quotes
- Guidance: next quarter and full year vs. consensus (raised, maintained, lowered?)
- Analyst Q&A highlights: toughest questions, any evasiveness or surprising candor
- Market reaction: stock move after earnings, analyst rating/target changes
- Next earnings date

## Institutional & Insider Activity
- Institutional ownership % and recent changes (increasing or decreasing?)
- Notable 13F filers adding/trimming (hedge funds, mutual funds)
- Insider transactions in last 90 days (cluster buying = strong signal)
- **Alignment signal:** Institutions increasing AND insiders buying = highest conviction. Institutions selling AND insiders selling = red flag.

## Market Sentiment
- Analyst consensus (buy/hold/sell breakdown, average price target)
- Recent news or catalysts
- **Anomaly check:** Is the market reacting as expected to news? If good news is being ignored or bad news isn't pushing price down, flag it — this is often more informative than the news itself.

## Technical Outlook

Provide 2-3 probabilistic scenarios based on current technicals:

| Scenario | Probability | Target | Invalidation | Trigger |
|----------|-------------|--------|--------------|---------|
| Bull | % | $X | Below $Y | What needs to happen |
| Base | % | $X | Below $Y | Default path |
| Bear | % | $X | Below $Y | What goes wrong |

Probabilities must sum to 100%. Every scenario needs an explicit invalidation price — the level where that thesis breaks.

## Risks
- Key risks to the thesis (rank by likelihood and impact)
- Upcoming binary events (earnings, FDA, regulatory, macro)
- **Thesis killer:** What single event or data point would make you abandon this stock entirely?

## Conviction Score

Rate the stock on 6 dimensions (1-10 each). Be honest — most stocks score 4-7, not 8-10.

| Dimension | Score | Notes |
|-----------|-------|-------|
| Business Quality (moat, margins, management) | /10 | |
| Growth (revenue, earnings trajectory) | /10 | |
| Valuation (relative to growth + sector) | /10 | |
| Technicals (trend, support, entry timing) | /10 | |
| Catalyst (upcoming events, narrative strength) | /10 | |
| Institutional Support (smart money alignment) | /10 | |
| **Overall Conviction** | **/10** | Weighted avg — Business & Growth count 2x |

For Valuation scoring, use sector-appropriate Forward P/E benchmarks from knowledge/frameworks/valuation.md — don't rely on absolute P/E alone.

**Conviction guide:** 8-10 = high conviction (worth a full position), 6-7 = moderate (DCA or smaller size), 4-5 = speculative (watch only), 1-3 = avoid.

## Summary
- Bull case vs. bear case (1-2 sentences each)
- Overall take: bullish, neutral, or bearish — with reasoning

## Strategy Fit

Based on the research above, recommend which strategy fits best. Consult `knowledge/signals/iv-rank-guide.md` for the IV Rank × RSI decision matrix:
- **IV Rank < 25 + RSI < 30** → LEAP Calls (see `knowledge/strategies/when-to-leaps.md`)
- **IV Rank < 25 + RSI 30-70** → Buy & Hold or DCA
- **IV Rank 50-75 + RSI < 50** → Theta Gang / CSP (see `knowledge/strategies/when-to-csp.md`)
- **IV Rank > 75** → Sell premium aggressively (CSP/CC)

Note: This is a directional recommendation. Run `technicals.py TICKER --options` for IV data, or note that strategy fit will be validated by `/plan-stock` or strategy-specific skills.

Pick one (or a combination) and explain why it suits this stock right now.

---

Save the output to `research/stocks/$ARGUMENTS.md` (use uppercase ticker as filename).
Start the entry with a date separator: `---` followed by `# TICKER — Research | YYYY-MM-DD`.
If the file already exists, prepend the new analysis above all previous entries (after the YAML frontmatter block). Never remove historical entries.

If creating a new file, add YAML frontmatter at the top:
```yaml
---
ticker: TICKER
status: researched
added_date: YYYY-MM-DD
sector: (infer from research)
thesis: "(one-line summary)"
conviction: (overall score from Conviction Score)
---
```

If updating an existing file, update the `conviction` field in frontmatter.

**Update index & dashboard:**
```bash
.venv/bin/python3 scripts/update-index.py && .venv/bin/python3 scripts/dashboard.py
```
