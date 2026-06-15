#!/usr/bin/env python3
"""
chart-watchlist.py — RSI vs Forward P/E scatter plot for all watching stocks.

Stocks in the bottom-left quadrant (low RSI + low P/E) are the best opportunities.

Usage:
    .venv/bin/python3 scripts/chart-watchlist.py              # generate chart
    .venv/bin/python3 scripts/chart-watchlist.py --no-open     # don't open browser

Outputs an interactive Plotly scatter plot to charts/watchlist-scatter.html.
"""

import argparse
import re
import webbrowser
from datetime import datetime
from pathlib import Path

import plotly.graph_objects as go
import yfinance as yf

STOCKS_DIR = Path(__file__).parent.parent / "research" / "stocks"
OUTPUT_PATH = Path(__file__).parent.parent / "charts" / "watchlist-scatter.html"

# Reference lines
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
PE_FAIR_VALUE = 25

# Sector color palette
SECTOR_COLORS = {
    "Technology": "#1f77b4",
    "Healthcare": "#2ca02c",
    "Financials": "#ff7f0e",
    "Consumer Discretionary": "#d62728",
    "Consumer Staples": "#9467bd",
    "Energy": "#8c564b",
    "Industrials": "#e377c2",
    "Materials": "#7f7f7f",
    "Real Estate": "#bcbd22",
    "Utilities": "#17becf",
    "Communication": "#aec7e8",
    "Communication Services": "#aec7e8",
}
DEFAULT_COLOR = "#888888"


def parse_frontmatter(filepath: Path) -> dict:
    """Parse YAML frontmatter from a markdown file."""
    content = filepath.read_text(encoding="utf-8")
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    for line in match.group(1).strip().split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value.startswith('[') and value.endswith(']'):
                value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(',')]
            frontmatter[key] = value

    return frontmatter


def compute_rsi(closes, period=14):
    """Compute RSI from a series of closing prices."""
    if len(closes) < period + 1:
        return None
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 1)


def load_watching_stocks() -> list[dict]:
    """Load stocks with status: watching from research/stocks/."""
    stocks = []
    if not STOCKS_DIR.exists():
        return stocks

    for filepath in sorted(STOCKS_DIR.glob("*.md")):
        if filepath.name in ("0-INDEX.md", "1-DASHBOARD.md") or filepath.name.startswith("."):
            continue

        fm = parse_frontmatter(filepath)
        if not fm.get("ticker") or fm.get("status") != "watching":
            continue

        entry_target = fm.get("entry_target", "")
        try:
            entry_target = float(entry_target) if entry_target else None
        except (ValueError, TypeError):
            entry_target = None

        strategies = fm.get("strategies", [])
        if isinstance(strategies, str):
            strategies = [strategies]

        stocks.append({
            "ticker": fm["ticker"],
            "sector": fm.get("sector", "Unknown"),
            "entry_target": entry_target,
            "strategies": strategies,
        })

    return stocks


def fetch_market_data(stocks: list[dict]) -> list[dict]:
    """Fetch live price, RSI, and forward P/E for each stock. Returns enriched list."""
    if not stocks:
        return []

    tickers = [s["ticker"] for s in stocks]
    # Filter out non-US tickers
    us_tickers = [t for t in tickers if not any(c in t for c in ['.', '/'])]

    if not us_tickers:
        return []

    # Batch download price history for RSI
    print(f"Fetching price data for {len(us_tickers)} tickers...")
    prices = {}
    rsi_values = {}

    try:
        data = yf.download(us_tickers, period="1mo", progress=False)
        if len(us_tickers) == 1:
            closes = data['Close'].dropna().tolist()
            if closes:
                prices[us_tickers[0]] = round(float(closes[-1]), 2)
                rsi = compute_rsi(closes)
                if rsi is not None:
                    rsi_values[us_tickers[0]] = rsi
        else:
            for ticker in us_tickers:
                try:
                    closes = data['Close'][ticker].dropna().tolist()
                    if closes:
                        prices[ticker] = round(float(closes[-1]), 2)
                        rsi = compute_rsi(closes)
                        if rsi is not None:
                            rsi_values[ticker] = rsi
                except (KeyError, IndexError):
                    pass
    except Exception as e:
        print(f"  Warning: price download failed: {e}")

    # Fetch forward P/E individually
    print("Fetching forward P/E ratios...")
    fwd_pe = {}
    for ticker in us_tickers:
        try:
            info = yf.Ticker(ticker).info
            pe = info.get('forwardPE')
            if pe and pe > 0:
                fwd_pe[ticker] = round(float(pe), 1)
        except Exception:
            pass

    # Build enriched results — only include stocks that have both RSI and fwd P/E
    enriched = []
    for s in stocks:
        ticker = s["ticker"]
        if ticker not in rsi_values or ticker not in fwd_pe:
            skipped = []
            if ticker not in rsi_values:
                skipped.append("RSI")
            if ticker not in fwd_pe:
                skipped.append("fwd P/E")
            print(f"  Skipping {ticker} — missing {', '.join(skipped)}")
            continue

        price = prices.get(ticker)
        gap_pct = None
        if price and s["entry_target"]:
            gap_pct = round(((price - s["entry_target"]) / price) * 100, 1)

        enriched.append({
            **s,
            "price": price,
            "rsi": rsi_values[ticker],
            "fwd_pe": fwd_pe[ticker],
            "gap_to_target": gap_pct,
        })

    return enriched


def build_scatter(stocks: list[dict]) -> go.Figure:
    """Build the RSI vs Forward P/E scatter plot."""
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Group by sector for coloring
    sectors = sorted(set(s["sector"] for s in stocks))

    fig = go.Figure()

    for sector in sectors:
        sector_stocks = [s for s in stocks if s["sector"] == sector]
        color = SECTOR_COLORS.get(sector, DEFAULT_COLOR)

        # Compute marker sizes — inversely proportional to gap-to-target
        sizes = []
        for s in sector_stocks:
            gap = s["gap_to_target"]
            if gap is not None:
                # Closer to target (or below) = bigger dot
                # gap of 0% or negative = max size (22), gap of 30%+ = min size (8)
                size = max(8, min(22, 22 - abs(gap) * 0.5))
            else:
                size = 12  # default
            sizes.append(size)

        hover_texts = []
        for s in sector_stocks:
            strategies_str = ", ".join(s["strategies"]) if s["strategies"] else "—"
            target_str = f"${s['entry_target']:.2f}" if s["entry_target"] else "—"
            gap_str = f"{s['gap_to_target']:+.1f}%" if s["gap_to_target"] is not None else "—"
            price_str = f"${s['price']:.2f}" if s["price"] else "—"

            hover_texts.append(
                f"<b>{s['ticker']}</b><br>"
                f"Price: {price_str}<br>"
                f"RSI: {s['rsi']}<br>"
                f"Fwd P/E: {s['fwd_pe']:.1f}x<br>"
                f"Sector: {s['sector']}<br>"
                f"Target: {target_str}<br>"
                f"Gap to target: {gap_str}<br>"
                f"Strategies: {strategies_str}"
            )

        fig.add_trace(go.Scatter(
            x=[s["rsi"] for s in sector_stocks],
            y=[s["fwd_pe"] for s in sector_stocks],
            mode="markers+text",
            name=sector,
            text=[s["ticker"] for s in sector_stocks],
            textposition="top center",
            textfont=dict(size=11, color="#cccccc"),
            hovertext=hover_texts,
            hoverinfo="text",
            marker=dict(
                size=sizes,
                color=color,
                opacity=0.85,
                line=dict(width=1, color="#ffffff"),
            ),
        ))

    # Reference lines
    # Vertical: RSI oversold / overbought
    fig.add_vline(x=RSI_OVERSOLD, line_dash="dash", line_color="#66bb6a", line_width=1,
                  annotation_text="Oversold", annotation_position="top",
                  annotation_font_color="#66bb6a", annotation_font_size=11)
    fig.add_vline(x=RSI_OVERBOUGHT, line_dash="dash", line_color="#ef5350", line_width=1,
                  annotation_text="Overbought", annotation_position="top",
                  annotation_font_color="#ef5350", annotation_font_size=11)

    # Horizontal: P/E fair value (works with log scale)
    fig.add_hline(y=PE_FAIR_VALUE, line_dash="dash", line_color="#888888", line_width=1,
                  annotation_text=f"P/E {PE_FAIR_VALUE}x", annotation_position="right",
                  annotation_font_color="#888888", annotation_font_size=11)

    # Quadrant labels
    all_rsi = [s["rsi"] for s in stocks]
    all_pe = [s["fwd_pe"] for s in stocks]
    rsi_min = max(0, min(all_rsi) - 5)
    rsi_max = min(100, max(all_rsi) + 5)
    pe_min = max(1, min(all_pe) * 0.8)
    pe_max = max(all_pe) * 1.2

    # Bottom-left: OVERSOLD + CHEAP (green)
    fig.add_annotation(
        x=RSI_OVERSOLD / 2, y=6,
        text="OVERSOLD + CHEAP",
        showarrow=False,
        font=dict(size=13, color="#66bb6a", family="Arial Black"),
        opacity=0.4,
    )

    # Top-right: OVERBOUGHT + EXPENSIVE (red)
    fig.add_annotation(
        x=(RSI_OVERBOUGHT + rsi_max) / 2, y=700,
        text="OVERBOUGHT + EXPENSIVE",
        showarrow=False,
        font=dict(size=13, color="#ef5350", family="Arial Black"),
        opacity=0.4,
    )

    fig.update_layout(
        title=dict(
            text=f"Watchlist: RSI vs Forward P/E | {date_str}",
            font=dict(size=20),
        ),
        xaxis=dict(
            title="RSI (14-period)",
            range=[rsi_min, rsi_max],
            gridcolor="#333333",
            zeroline=False,
        ),
        yaxis=dict(
            title="Forward P/E (log scale)",
            type="log",
            range=[0.6, 3.0],  # log10: 4x to 1000x P/E
            gridcolor="#333333",
            zeroline=False,
            tickvals=[5, 10, 15, 25, 50, 100, 200, 500],
            ticktext=["5x", "10x", "15x", "25x", "50x", "100x", "200x", "500x"],
        ),
        legend=dict(
            title="Sector",
            bgcolor="rgba(30,30,30,0.8)",
            bordercolor="#555555",
            borderwidth=1,
            font=dict(color="white"),
        ),
        margin=dict(t=80, l=60, r=30, b=60),
        paper_bgcolor="#1a1a1a",
        plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        hoverlabel=dict(
            bgcolor="#2a2a2a",
            bordercolor="#555555",
            font_size=13,
            font_color="white",
        ),
    )

    return fig


READING_GUIDE_HTML = """
<div style="background:#1a1a1a; padding:12px 20px; font-family:sans-serif; font-size:13px; color:#aaaaaa; line-height:1.6;">
  <b>How to read:</b>
  Each dot = one stock on your watchlist.
  <b>X-axis:</b> RSI (momentum) &mdash; left is oversold, right is overbought.
  <b>Y-axis:</b> Forward P/E (valuation) &mdash; bottom is cheap, top is expensive.
  <span style="color:#66bb6a"><b>Bottom-left quadrant</b></span> = best opportunities (oversold + cheap).
  <span style="color:#ef5350"><b>Top-right quadrant</b></span> = most stretched (overbought + expensive).
  Dot color = sector. Bigger dot = closer to your entry target.
  Hover for details.
</div>
"""


def save_with_guide(fig: go.Figure, output_path: Path):
    """Save chart HTML with a reading guide div below the plot."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chart_html = fig.to_html(include_plotlyjs="cdn", full_html=True)
    html = chart_html.replace("</body>", READING_GUIDE_HTML + "</body>")
    output_path.write_text(html)
    print(f"Chart saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Watchlist RSI vs Forward P/E scatter plot")
    parser.add_argument("--no-open", action="store_true",
                        help="Don't open in browser")
    args = parser.parse_args()

    # Load watching stocks
    stocks = load_watching_stocks()
    if not stocks:
        print("No stocks with status: watching found in research/stocks/")
        return

    print(f"Found {len(stocks)} watching stocks")

    # Fetch market data
    enriched = fetch_market_data(stocks)
    if not enriched:
        print("No stocks with complete data (RSI + fwd P/E). Nothing to plot.")
        return

    print(f"Plotting {len(enriched)} stocks with complete data")

    # Build and save chart
    fig = build_scatter(enriched)
    save_with_guide(fig, OUTPUT_PATH)

    if not args.no_open:
        webbrowser.open(f"file://{OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    main()
