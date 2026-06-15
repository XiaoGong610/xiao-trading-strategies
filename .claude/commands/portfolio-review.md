---
description: Portfolio advisor — analyze positions against goals and recommend changes
---

Run a portfolio review and generate actionable recommendations.

This skill reads the user's investment profile and current positions, combines them with live market data, and produces specific recommendations for what to change.

This is NOT a transaction tracker — it's an investment advisor layer. The brokerage tracks transactions. We track strategy, goals, and what to do next.

## Step 1: Read Profile & Positions

Read these files:
- `portfolio/PROFILE.md` — goals, risk tolerance, allocation limits, preferences
- `portfolio/POSITIONS.md` — current holdings snapshot (what you own now)

If either file is missing, tell the user to set them up first.

## Step 2: Fetch Live Data

Run the dashboard and sector momentum for current market context:
```bash
.venv/bin/python3 scripts/dashboard.py --json
.venv/bin/python3 scripts/sector-momentum.py --json
```

For each position in POSITIONS.md, run technicals:
```bash
.venv/bin/python3 scripts/technicals.py TICKER --options
```

Also generate the watchlist scatter chart for visual reference:
```bash
.venv/bin/python3 scripts/chart-watchlist.py --no-open
```

## Step 3: Consult Knowledge Base

- Read `knowledge/signals/rsi-guide.md` — interpret RSI for each position
- Read `knowledge/signals/iv-rank-guide.md` — identify CSP/LEAPs opportunities
- Read `knowledge/frameworks/valuation.md` — check if any position is extremely over/undervalued
- Read `knowledge/frameworks/sector-momentum.md` — sector context for each position
- Read `knowledge/frameworks/risk-metrics.md` — portfolio-level risk assessment
- Read `knowledge/frameworks/capital-flow.md` — AI supply chain positioning

## Step 4: Portfolio Health Check

### 4a. Allocation Analysis

Calculate current allocation by:
- **Sector** — what % of portfolio is in each sector? Flag if any sector >30% of total.
- **Theme** — what % is in each investment theme (AI infra, crypto, software, etc.)? Flag concentration.
- **Strategy** — what % is DCA vs Buy & Hold vs Theta Gang vs LEAPs?
- **Single-stock concentration** — any position >10% of portfolio? Flag it.

Compare actual allocation to the targets in PROFILE.md. Show the gaps.

| Sector | Target % | Actual % | Gap | Action |
|--------|----------|----------|-----|--------|

### 4b. Position-Level Review

For each position, assess:

| Ticker | Shares/Value | Cost Basis | P&L% | RSI | Fwd P/E | Sector Momentum | IV Rank | Action |
|--------|-------------|-----------|------|-----|---------|----------------|---------|--------|

**Action categories:**
- **HOLD** — on track, no changes needed
- **ACCELERATE** — oversold + thesis intact → increase DCA pace
- **REDUCE** — overbought + overweight → trim or pause DCA
- **ADD CSP** — IV rich + at support → sell premium
- **ADD LEAPS** — IV cheap + high conviction → buy leverage
- **REVIEW** — thesis may be changing, needs `/research-stock` refresh
- **EXIT** — thesis broken or position no longer fits goals

### 4c. Risk Assessment

- **Correlation check** — are positions moving together? If 5 of 7 positions are AI/tech, a single NVDA miss could hit everything.
- **Earnings proximity** — flag any position with earnings within 14 days
- **Sector concentration** — is money too concentrated in one sector?
- **Market regime context** — given current regime, should overall exposure increase or decrease?

## Step 5: Recommendations

### What to Change NOW (this week)

Specific, actionable items:

| Priority | Action | Ticker | Detail | Why |
|----------|--------|--------|--------|-----|
| 1 | ... | ... | ... | ... |
| 2 | ... | ... | ... | ... |

### What to Watch (next 2 weeks)

Conditional actions — "if X happens, do Y":

| Trigger | Action | Ticker |
|---------|--------|--------|
| RSI drops below 30 | Accelerate DCA to 2x | ... |
| Earnings in <7 days | Pause DCA or sell CSP | ... |
| Price hits entry target | Add CSP at support | ... |

### What to Research

Stocks or sectors not in the portfolio that SHOULD be, based on goals and current gaps:

| Candidate | Why | Next Step |
|-----------|-----|-----------|
| ... | Fills sector gap / matches goal | `/research-stock TICKER` |

## Step 6: Update Positions File

If any recommendations were acted on (user confirmed), update `portfolio/POSITIONS.md` with the new state.

Do NOT auto-update — always confirm with the user first.

---

Save the review output to `portfolio/REVIEW-YYYY-MM-DD.md`.
