Manage the watchlist — triage, add stocks, or auto-refresh the top priorities.

This skill wraps `scripts/watchlist.py` and orchestrates watchlist operations.

## Arguments

Parse the user's input to determine the action:

- **No args / "triage"** — run the watchlist dashboard and summarize what needs attention
- **"add TICKER"** — add a new stock as a candidate (optionally with sector and source)
- **"refresh"** — auto-refresh the top N stocks by running `/research-stock` on each
- **"remove TICKER"** — change a stock's status to "removed"

## Actions

### Triage (default)

Run the watchlist manager and present the results. This generates `research/stocks/0-WATCHLIST.md` with the consolidated view (priority scores, RSI, fwd P/E, sector momentum, earnings countdown, gap-to-target, thesis).

```bash
.venv/bin/python3 scripts/watchlist.py --top 10
```

After showing the output, provide a brief summary:
1. How many stocks need refresh, how many are candidates
2. The top 5 refresh priorities and why (from the score breakdown)
3. Any stocks approaching earnings that are still fresh (no action needed, but flag them)
4. Notable signals from the live data (e.g., oversold RSI, cheap fwd P/E, strong sector momentum)
5. Recommend: "Want me to refresh the top N?" or "Want to add any new stocks?"

### Add

Add one or more stocks as candidates:

```bash
# Single stock
.venv/bin/python3 scripts/watchlist.py --add TICKER --source "SOURCE"

# With known sector
.venv/bin/python3 scripts/watchlist.py --add TICKER --sector "Sector Name" --source "SOURCE"
```

If the user doesn't specify a source, ask briefly: "Where did you hear about it?" (friend, news, sector scan, Twitter, etc.)

After adding, show the updated refresh queue to confirm the stock appears.

### Refresh

Run `/research-stock` on the top N stocks from the refresh queue. Default N=5, or user can specify.

```bash
# Get the list
.venv/bin/python3 scripts/watchlist.py --auto --top N
```

Then run `/research-stock TICKER` for each ticker in the output. Run them in parallel using the Agent tool for efficiency (max 3 concurrent to avoid rate limits).

After all refreshes complete, run the watchlist again to show the updated state.

### Remove

To remove a stock, update its frontmatter status to "removed":

1. Read the stock file at `research/stocks/TICKER.md`
2. Change `status: watching` (or `status: candidate`) to `status: removed`
3. Run `scripts/watchlist.py` to regenerate `0-WATCHLIST.md`
4. Confirm the removal

## Notes

- The watchlist script fetches live prices and sector momentum data — it takes 10-15 seconds to run
- Priority scoring is automatic: earnings proximity > sector momentum > gap-to-target > staleness > conviction
- Candidates (new stocks with no research) automatically get a +35 bonus to surface in the refresh queue
- The `--auto` flag outputs just ticker symbols (one per line) for piping into automated workflows
- Tiered refresh cadence: conviction 8+ = every 14 days, conv 6-7 = 28 days, conv <6 = 42 days
