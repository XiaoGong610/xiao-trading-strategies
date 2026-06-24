# True vs False Breakout Filter

A 3-way confirmation filter for breakout trades. Adapted from 恨铁不成小猫猫's methodology.

## The Filter

All three must confirm for a true breakout. If any fails, treat as false/pending.

| Dimension | True Breakout | False Breakout |
|-----------|--------------|----------------|
| **Volume** | Concurrent increase (>1.5x 20-day avg) | No volume increase, shrinking |
| **ATR magnitude** | Breakout move exceeds 1x ATR (stock's daily "lung capacity") | Amplitude much smaller than ATR |
| **IV level** | Moderate-to-low (IV Rank <50) | Abnormally high (IV Rank >75 = overheated) |

**Next-day confirmation:** True breakouts open strong and hold. False breakouts usually reverse and retrace by next session.

## How to Use

Use `technicals.py TICKER --options` output:
- Volume: compare `last_volume` to `avg_volume_20d` — need >1.5x ratio
- ATR: check if the day's price move (high - low, or gap) exceeds `atr_14`
- IV: check `current_iv` against the IV Rank thresholds in `iv-rank-guide.md`

## When to Apply

- **Breakout buy entries** in `/plan-stock` Phase 5 — validate before placing a stop-limit buy above resistance
- **Position adds** — when a stock breaks to new highs, confirm it's real before adding
- **Earnings gaps** — apply the filter to post-earnings gaps (Event Day rule: wait for first shock wave, then check)

## Signal Grades

| Volume | ATR | IV | Grade | Action |
|--------|-----|-----|-------|--------|
| >1.5x | >1x ATR | <50 IV Rank | **A — Confirmed** | Enter with confidence |
| >1.5x | >1x ATR | >50 IV Rank | **B — Caution** | Enter with smaller size, tighter stop |
| <1.5x | Any | Any | **C — Suspect** | Don't chase. Wait for volume confirmation |
| Any | <0.5x ATR | Any | **D — Fake** | Ignore the breakout entirely |

## Common Mistakes

1. **Chasing a low-volume breakout** — the most common retail trap. No volume = no institutions = no follow-through.
2. **Buying breakouts when IV is already extreme** — if IV Rank >75, the "breakout" may be options-driven noise, not institutional buying.
3. **Not waiting for next-day confirmation** — a true breakout holds its gains. If it gives back >50% of the move by next day, it's false.
