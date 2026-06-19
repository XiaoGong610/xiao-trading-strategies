---
description: Portfolio advisor — analyze positions against goals and recommend changes
---

Run a portfolio review and generate actionable recommendations.

This is NOT a transaction tracker — it's an investment advisor layer. The brokerage tracks transactions. We track strategy, goals, and what to do next.

## Step 0: Collect Current Positions

**Ask the user to share screenshots of each account.** This is the source of truth for current holdings.

When the user shares account screenshots:

1. **Parse each screenshot** — extract: ticker, shares, cost basis, current price, gain/loss, % of account, and any options positions (strike, expiry, quantity, value).
2. **Update the account files** — overwrite the Positions section in `portfolio/accounts/{account-name}.md` with fresh data from the screenshots. Preserve the YAML frontmatter (goals, constraints, strategy, risk tolerance) — only refresh the numbers.
3. **Update `last_updated` in frontmatter** to today's date.
4. **Update `total_value` and `cash`** in frontmatter.
5. **Preserve Flags section** — update flags based on new data (e.g., concentration %, underwater positions, options status). Remove flags that are no longer relevant, add new ones.
6. **Preserve Review Cadence section** — these are durable notes, don't remove them.

**Account file structure:**
```yaml
---
account_name: NAME
account_id: ID
account_type: brokerage | roth-ira | 401k-brokeragelink
total_value: (from screenshot)
cash: (from screenshot)
last_updated: YYYY-MM-DD
goal: "..."
strategy: ...
risk_tolerance: ...
time_horizon: ...
benchmark: ...
constraints:
  - ...
---

## Positions
(tables of current holdings — refreshed from screenshots)

## Options Positions
(active options — refreshed from screenshots)

## Flags
(concentration warnings, underwater positions, urgent items)

## Review Cadence
(durable notes on when/how to review — preserved across updates)
```

**If the user hasn't shared screenshots** in this conversation, read the existing account files and note their `last_updated` date. If stale (>7 days), ask the user: "Your account data is from [date]. Want to share updated screenshots before I run the review?"

## Step 1: Read Account Files & Market Context

Read all account files:
```
portfolio/accounts/hold.md
portfolio/accounts/thetagang.md
portfolio/accounts/roth-ira.md
portfolio/accounts/brokeragelink.md
portfolio/accounts/gobig.md
```

Read the latest market overview:
- `research/sectors/market-overview.md` — market regime, key risks

Run the dashboard for watchlist context:
```bash
.venv/bin/python3 scripts/dashboard.py --json
```

## Step 2: Cross-Account Analysis

This is the most important step. Individual account views hide the real risk.

### 2a. Cross-Account Concentration

Aggregate holdings across ALL accounts. For each stock held in multiple accounts:

| Stock | Total Shares | Total Value | % of Total Portfolio | Accounts |
|-------|-------------|-------------|---------------------|----------|

Flag:
- Any single stock >15% of total portfolio
- Any sector >30% of total portfolio
- Leveraged ETFs (TSLL, CONL, etc.) — calculate notional exposure
- Employer stock — flag career concentration risk

### 2b. Sector/Theme Allocation

| Sector/Theme | Value | % of Portfolio | Assessment |
|-------------|-------|---------------|------------|

### 2c. Cash Position

| Account | Cash | Cash % | Notes |
|---------|------|--------|-------|
| **Total** | | | |

## Step 3: Position-Level Review

For each position across all accounts:

| Ticker | Account | Shares | Value | Cost | P&L% | Action |
|--------|---------|--------|-------|------|------|--------|

**Action categories:**
- **HOLD** — on track, no changes needed
- **ACCELERATE DCA** — oversold + thesis intact → increase DCA pace
- **REDUCE** — overbought + overweight → trim or pause DCA
- **SELL CCs** — holding shares + not selling covered calls = missed income
- **ADD CSP** — IV rich + at support → sell premium
- **ADD LEAPS** — IV cheap + high conviction → buy leverage
- **REVIEW** — thesis may be changing, needs `/research-stock` refresh
- **EXIT** — thesis broken or position no longer fits goals

### Options Review

For each active option:

| Option | Account | Expiry | DTE | Status | P&L | Action |
|--------|---------|--------|-----|--------|-----|--------|

Flag:
- Options expiring within 14 days
- Sold puts that are ITM (assignment risk)
- LEAPs below 90 DTE (roll or close)
- Covered calls near the money (assignment risk)

## Step 4: Research-to-Portfolio Alignment

Compare the research conviction scores against actual portfolio weights:

| Stock | Conviction | Portfolio % | Should Be % | Gap | Action |
|-------|-----------|-------------|-------------|-----|--------|

**Key question:** Are your biggest positions your highest-conviction ideas? If not, what's blocking alignment (taxes, timing, inertia)?

## Step 5: DCA Schedule Review

If the user has active DCA schedules (recurring buys):

| DCA | $/Day | Position Size | Conviction | Assessment | Change? |
|-----|-------|--------------|------------|------------|---------|

Recommend adjustments: increase for high-conviction underweight names, decrease/pause for overweight or low-conviction names.

## Step 6: Recommendations

### Do This Week (urgent)

| # | Action | Account | Detail | Why |
|---|--------|---------|--------|-----|
| 1 | ... | ... | ... | ... |

### Do This Month

| # | Action | Account | Detail | Why |
|---|--------|---------|--------|-----|

### Watch (conditional)

| Trigger | Action | Account |
|---------|--------|---------|

### Research Gaps

| Candidate | Why | Next Step |
|-----------|-----|-----------|

## Step 7: Save Review

Save output to `portfolio/REVIEW-YYYY-MM-DD.md`.

**Do NOT auto-update account files** — only update when the user shares fresh screenshots. The account files are refreshed at Step 0, not at the end.
