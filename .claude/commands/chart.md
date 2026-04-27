---
description: Plot stock price chart with theta gang overlays
---

Generate an interactive chart for: $ARGUMENTS

The argument format is: TICKER [PERIOD] [OPTIONS]
- TICKER: stock symbol (e.g., AMZN, TSLA)
- PERIOD: optional — 1mo, 3mo, 6mo, 1y, 2y (default: 6mo)
- OPTIONS: optional strike/strategy overlays
  - `csp=STRIKE` — draw CSP strike line (e.g., csp=240)
  - `cc=STRIKE` — draw CC strike line (e.g., cc=285)
  - Both can be used together to show the "comfort zone"
- Examples: "AMZN", "TSLA 1y", "AMZN 6mo csp=240 cc=285"

Use the Python virtual environment at `.venv/` and generate an interactive HTML chart using plotly.

Write and run a Python script that:

1. **Fetches data** via yfinance:
   - Price history for the specified period
   - Calculate: 20-day SMA, 50-day SMA, 200-day SMA
   - Calculate: RSI (14-day)
   - Calculate: Bollinger Bands (20-day, 2 std dev)
   - Volume
   - Next earnings date (from `ticker.calendar`)
   - IV history: fetch options chain for nearest expiry and calculate current IV; also use historical close prices to compute 30-day historical volatility (HV) over time

2. **Creates a multi-panel interactive plotly chart** with:

   **Panel 1 (main, 50% height): Price + Theta Gang Overlays**
   - Candlestick chart
   - 20-day SMA (blue), 50-day SMA (orange), 200-day SMA (red)
   - Bollinger Bands (shaded gray)
   - **Theta gang overlays:**
     - If `csp=STRIKE` provided: draw a horizontal dashed green line at the CSP strike, labeled "CSP $STRIKE"
     - If `cc=STRIKE` provided: draw a horizontal dashed red line at the CC strike, labeled "CC $STRIKE"
     - If both provided: shade the zone between CSP and CC strikes in light blue with transparency — this is the "comfort zone" where neither side gets assigned
     - **Earnings date marker**: draw a vertical dashed yellow line at the next earnings date, labeled "Earnings". If earnings date is within 45 days, add a red shaded zone spanning 3 days around it labeled "Earnings Danger Zone"
     - **Support/resistance**: draw horizontal dotted lines at the 52-week high and 52-week low, labeled accordingly

   **Panel 2 (15% height): RSI**
   - RSI line (purple)
   - Horizontal lines at 30 (oversold) and 70 (overbought)
   - Shade overbought zone red, oversold zone green

   **Panel 3 (15% height): Historical Volatility**
   - 30-day historical volatility (HV) as a line chart
   - Annotate the current HV value
   - This helps gauge whether current IV (from options) is cheap or expensive vs. realized vol

   **Panel 4 (20% height): Volume**
   - Volume bars colored green (up day) / red (down day)

3. **Chart formatting:**
   - Title: "TICKER — Theta Gang View | Period | Generated YYYY-MM-DD"
   - Clean dark theme (plotly_dark)
   - Hover data showing OHLCV + indicators
   - Legend horizontal at top
   - No range slider (clutters the multi-panel layout)

4. **Save and open:**
   - Save as `charts/TICKER_YYYY-MM-DD.html`
   - Open in browser automatically via `open` command (macOS)

Make sure to activate the venv before running: `source .venv/bin/activate`
Create the `charts/` directory if it doesn't exist.
