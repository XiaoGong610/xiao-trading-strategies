---
description: Plot interactive stock price chart with optional strategy overlays
---

Generate an interactive chart for: $ARGUMENTS

The argument format is: TICKER [PERIOD] [OVERLAYS]
- TICKER: stock symbol (e.g., AMZN, TSLA)
- PERIOD: optional — 1mo, 3mo, 6mo, 1y, 2y (default: 6mo)
- OVERLAYS: optional price level lines for any strategy
  - `buy=PRICE` — draw a buy target line (e.g., buy=185)
  - `sell=PRICE` — draw a sell/take-profit target line (e.g., sell=220)
  - `csp=STRIKE` — draw CSP strike line (theta gang)
  - `cc=STRIKE` — draw CC strike line (theta gang)
  - `leap=STRIKE` — draw LEAP call strike line
  - Multiple overlays can be combined
- Examples: "AMZN", "TSLA 1y", "AAPL 6mo buy=185 sell=220", "AMZN 6mo csp=240 cc=285"

Use the Python virtual environment at `.venv/` and generate an interactive HTML chart using plotly.

Write and run a Python script that:

1. **Fetches data** via yfinance:
   - Price history for the specified period
   - Calculate: 20-day SMA, 50-day SMA, 200-day SMA
   - Calculate: RSI (14-day)
   - Calculate: Bollinger Bands (20-day, 2 std dev)
   - Volume
   - Next earnings date (from `ticker.calendar`)
   - 30-day historical volatility (HV) computed from close prices

2. **Creates a multi-panel interactive plotly chart** with:

   **Panel 1 (main, 50% height): Price + Overlays**
   - Candlestick chart
   - 20-day SMA (blue), 50-day SMA (orange), 200-day SMA (red)
   - Bollinger Bands (shaded gray)
   - **Strategy overlays** (if provided):
     - `buy=PRICE`: horizontal dashed green line, labeled "Buy $PRICE"
     - `sell=PRICE`: horizontal dashed red line, labeled "Sell $PRICE"
     - `csp=STRIKE`: horizontal dashed green line, labeled "CSP $STRIKE"
     - `cc=STRIKE`: horizontal dashed red line, labeled "CC $STRIKE"
     - `leap=STRIKE`: horizontal dashed blue line, labeled "LEAP $STRIKE"
     - If both `csp` and `cc` provided: shade the zone between them in light blue — the "comfort zone"
     - If both `buy` and `sell` provided: shade the zone between them in light green — the target range
   - **Earnings date marker**: vertical dashed yellow line at the next earnings date, labeled "Earnings". If within 45 days, add red shaded zone spanning 3 days around it labeled "Earnings Danger Zone"
   - **Support/resistance**: horizontal dotted lines at 52-week high and low

   **Panel 2 (15% height): RSI**
   - RSI line (purple)
   - Horizontal lines at 30 (oversold) and 70 (overbought)
   - Shade overbought zone red, oversold zone green

   **Panel 3 (15% height): Historical Volatility**
   - 30-day historical volatility (HV) as a line chart
   - Annotate the current HV value

   **Panel 4 (20% height): Volume**
   - Volume bars colored green (up day) / red (down day)
   - Add 20-day average volume line as a reference (see `knowledge/signals/volume-guide.md` — bars >2x average = institutional activity)

**Interpretation references** (for adding annotations or reading guide):
- SMA alignment and entry levels → `knowledge/signals/ma-guide.md`
- Volume confirmation patterns → `knowledge/signals/volume-guide.md`
- RSI thresholds by sector → `knowledge/signals/rsi-guide.md`

3. **Chart formatting:**
   - Title: "TICKER — Chart | Period | Generated YYYY-MM-DD"
   - Clean dark theme (plotly_dark)
   - Hover data showing OHLCV + indicators
   - Legend horizontal at top
   - No range slider

4. **Save and open:**
   - Save as `charts/TICKER_YYYY-MM-DD.html`
   - Open in browser automatically via `open` command (macOS)

Use `.venv/bin/python3` to run the script (do NOT use `source .venv/bin/activate`).
Create the `charts/` directory if it doesn't exist.
