---
description: Research a market sector and identify candidate stocks
---

Research the following sector or theme and identify candidate stocks: $ARGUMENTS

The argument can be a traditional sector (e.g., "healthcare", "energy", "financials") or a cross-sector investment theme (e.g., "ai-infrastructure", "defense", "glp-1"). Themes cut across traditional sector boundaries — pull relevant stocks from wherever they sit.

Use web search to analyze the current state of this sector. Cover:

## Sector Overview
- What's driving the sector right now (macro trends, catalysts, headwinds)
- Recent performance vs. S&P 500 (outperforming, underperforming, in line?)
- Key themes (e.g., AI spend, rate sensitivity, regulatory changes)

## Theme Lifecycle Stage

Assess where this sector/theme sits in its lifecycle. This gates how aggressively we pursue candidates.

| Stage | Definition | Action |
|-------|-----------|--------|
| **Emerging** | Early narrative, few players, limited coverage | Aggressive — find first movers |
| **Accelerating** | Adoption inflecting, earnings confirming thesis | Aggressive — ride the wave |
| **Trending** | Mainstream coverage, ETFs launching, broad participation | Selective — only best-in-class |
| **Mature** | Well-known trade, crowded positioning, growth decelerating | Cautious — trim, don't add |
| **Exhausting** | Multiple ETFs, retail crowding, "everyone owns it" | Avoid new entries — look for exits |

**Current stage:** [pick one]
**Evidence:** [2-3 data points — ETF count, media coverage intensity, institutional positioning, earnings growth trajectory]
**Implication:** [what this means for candidate selection below]

## Top Performers
- 3-5 stocks leading the sector and why
- Recent earnings highlights from sector leaders

## Laggards / Turnaround Candidates
- 2-3 stocks underperforming that could be interesting on a pullback
- What would need to change for them to turn around

## Sector Risks
- Key risks that could hurt the sector broadly
- Upcoming events (earnings season, regulatory decisions, macro data)

## Candidate Scoring

Rank 5-10 stocks from this sector using weighted scoring. Score each dimension 1-10:

| Rank | Ticker | Growth (25%) | Valuation (20%) | Moat (15%) | Catalyst (15%) | Technicals (15%) | Options (10%) | **Score** | Verdict |
|------|--------|-------------|-----------------|-----------|---------------|-----------------|--------------|-----------|---------|

**Scoring guide:**
- **Growth (25%):** Revenue/earnings growth rate vs. peers. >30% = 8-10, 15-30% = 5-7, <15% = 1-4
- **Valuation (20%):** Fwd P/E or PEG relative to sector. Below sector avg = 7-10, in line = 4-6, premium = 1-3
- **Moat (15%):** Competitive advantage durability. Wide moat = 8-10, narrow = 5-7, none = 1-4
- **Catalyst (15%):** Upcoming positive event within 3 months. Strong catalyst = 8-10, moderate = 5-7, none = 1-4
- **Technicals (15%):** Trend + proximity to entry. Uptrend at support = 8-10, extended = 4-6, downtrend = 1-3
- **Options (10%):** Liquid options chain for strategy flexibility. Liquid = 8-10, moderate = 5-7, illiquid/none = 1-4

**Weighted Score** = (Growth×0.25) + (Valuation×0.20) + (Moat×0.15) + (Catalyst×0.15) + (Technicals×0.15) + (Options×0.10)

**Lifecycle adjustment:** If theme stage is Mature or Exhausting, subtract 1 from all candidate scores. Note this in the table.

**Verdict:** Score ≥7 = Strong, 5-6.9 = Moderate, <5 = Watch Later

## Relevant ETFs

Identify ETFs that cover this sector or theme:

| ETF | Name | Thesis Match % | IV / Options | Verdict |
|-----|------|---------------|-------------|---------|

For each ETF, note:
- How well it matches the sector thesis (what % of holdings are relevant vs. dead weight?)
- Whether it has liquid options (for theta gang viability)
- Whether DCA into the ETF makes more sense than picking individual stocks

## Top Picks
Highlight the top 2-3 candidates (highest scoring) and suggest next steps:
- Run `/research-stock TICKER` for a deep-dive on fundamentals
- Run `/trade-watch TICKER` to add to watchlist for monitoring
- Run `/plan-stock TICKER` for full pre-trade analysis

If theme lifecycle is **Exhausting**: recommend no new entries — suggest reviewing existing positions instead.

Save the output to `research/sectors/$SECTOR.md` (use lowercase sector name as filename, e.g., `software.md`).
Start the entry with a date separator: `---` followed by `# Sector — SECTOR | YYYY-MM-DD`.
If the file already exists, prepend the new analysis above all previous entries (after the file title). Never remove historical entries.
