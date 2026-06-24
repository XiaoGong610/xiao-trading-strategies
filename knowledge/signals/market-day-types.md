# Market Day Classification

Classify the trading day BEFORE deciding how to enter. Different day types require different execution approaches. Adapted from 恨铁不成小猫猫's methodology.

## The 5 Types

| Type | Characteristics | Strategy | Key Rule |
|------|----------------|----------|----------|
| **Trend Day** | Price advances one-sidedly, VWAP cannot be retested | Hold with trend, move stop up. Don't fade. | Never counter-trend on a trend day |
| **Range Day** | Price oscillates both sides of VWAP | Buy low, sell high within range. Theta gang thrives. | Don't chase breakouts — they'll reverse |
| **Reversal Day** | Opens continuing yesterday's direction, then clear reversal | Wait for confirmation signal before counter-trend entry | Don't anticipate the reversal — let it prove itself |
| **Munger Day** | Long/short can't determine direction, volume-price chaotic | Light position or don't trade. Sit on hands. | "When confused, do nothing" — there's always tomorrow |
| **Event Day** | Earnings / CPI / FOMC / Jobs report | Wait for first shock wave to end, THEN enter after direction confirmed | Never enter at open on event days |

## Event Day Rules (Most Important)

Event days (earnings, FOMC, CPI, NFP) have specific discipline:

1. **Don't enter at open** — wait for the first shock wave to settle (usually 30-60 min for macro, end-of-day for earnings)
2. **No counter-trend trades** — when direction becomes clear, don't try reverse arbitrage
3. **Must set stop loss in advance** — no event day trades without predefined stops
4. **After a loss on an event day, at most one more trade** — don't revenge-trade

## How to Apply

### In `/plan-stock`
When the plan lands on or near an event day (earnings, FOMC):
- Flag it as an Event Day in the execution plan
- Adjust entry: "Wait for post-event price action, then enter" instead of "buy at market"
- The existing "earnings <7 days = half pace DCA" rule aligns with this

### In `/research-stock`
If the stock has a known event within 3 days, note the event day type and adjust the Technical Outlook scenarios accordingly.

### For Daily Use
Before deciding on any intraday or swing entry, mentally classify:
- Is today a trend day? → ride it
- Range day? → sell premium or scalp the range
- Event day? → patience, let the dust settle
- Munger day? → do something else entirely

## Identification Tips

- **Trend days** are identifiable within the first hour: gap up/down on volume, price never looks back
- **Range days** reveal themselves after two failed breakout attempts in opposite directions
- **Reversal days** need patience: the reversal isn't real until volume confirms the new direction
- **Munger days** feel like "something is about to happen but nothing does" — choppy, low conviction
- **Event days** are known in advance from the calendar — plan accordingly
