---
description: Add a stock to the watchlist with entry criteria
---

Add to watchlist: $ARGUMENTS

The argument is a ticker (e.g., "AAPL", "TSLA").

This is a lightweight skill to quickly add a stock to the watchlist for monitoring. It does NOT do a full pre-trade analysis (use `/plan` for that).

**Step 1:** Run the data script for quick price, support, and 52-week data:
```bash
.venv/bin/python3 scripts/technicals.py $ARGUMENTS --options
```

Use the script's output for price, support levels, and technicals. Supplement with web search for earnings dates, news, and IV context.

Read `knowledge/signals/iv-rank-guide.md` to interpret IV Rank thresholds for strategy selection.

## Quick Assessment
- Current price, 52-week range, sector
- One-line thesis: why is this stock interesting right now?
- Key support levels (where would you want to enter?)
- Next earnings date (is it clear of a 30-45 DTE window?)
- IV level: is premium currently rich or cheap?

## Entry Criteria
- What price level or condition would trigger a deeper analysis / trade entry?
- Which strategies make sense (CSP, CC, PMCC)?
- Any events to wait for before entering (earnings, ex-div, macro)?

## Next Steps
- Suggest running `/plan-stock TICKER` when entry conditions are approaching
- Note any upcoming catalysts to watch

Save the output to `research/stocks/$TICKER.md` (use uppercase ticker as filename).

If creating a new file, add YAML frontmatter at the top:
```yaml
---
ticker: TICKER
status: watching
added_date: YYYY-MM-DD
sector: (infer from research)
thesis: "(one-line summary)"
entry_target: (key support level / entry price)
strategies: [CSP, CC]
---
```

Start the analysis entry with: `---` followed by `# TICKER — Watchlist Entry | YYYY-MM-DD`.

If the file already exists:
- If status is `researched`, update it to `watching`
- Prepend the new analysis above all previous entries (after the YAML frontmatter block). Never remove historical entries.

**Update index & dashboard:**
```bash
.venv/bin/python3 scripts/update-index.py && .venv/bin/python3 scripts/dashboard.py
```
