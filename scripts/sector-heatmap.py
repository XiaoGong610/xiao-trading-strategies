#!/usr/bin/env python3
"""
sector-heatmap.py — Generate an interactive sector performance heatmap.

Usage:
    python3 scripts/sector-heatmap.py              # all periods with toggle buttons
    python3 scripts/sector-heatmap.py --period 1wk  # single period only

Outputs an interactive Plotly treemap to charts/sector-heatmap.html.
When no --period is specified, fetches all periods and adds toggle buttons in the chart.
"""

import argparse
import webbrowser
from datetime import datetime
from pathlib import Path

import yfinance as yf
import plotly.graph_objects as go

# GICS sector ETFs — proxy for sector performance
SECTOR_ETFS = {
    "Technology": "XLK",
    "Healthcare": "XLV",
    "Financials": "XLF",
    "Consumer Disc.": "XLY",
    "Consumer Staples": "XLP",
    "Energy": "XLE",
    "Industrials": "XLI",
    "Materials": "XLB",
    "Real Estate": "XLRE",
    "Utilities": "XLU",
    "Communication": "XLC",
}

ALL_PERIODS = ["1wk", "1mo", "3mo", "6mo", "ytd", "1y"]
DEFAULT_PERIOD_INDEX = 1  # 1mo

PERIOD_MAP = {
    "1wk": "1-Week",
    "1mo": "1-Month",
    "3mo": "3-Month",
    "6mo": "6-Month",
    "ytd": "YTD",
    "1y": "1-Year",
}


def fetch_sector_market_caps() -> dict[str, float]:
    """Fetch total net assets for each sector ETF as a proxy for sector size."""
    caps = {}
    for sector, etf in SECTOR_ETFS.items():
        try:
            info = yf.Ticker(etf).info
            # totalAssets = ETF AUM, a reasonable proxy for relative sector size
            assets = info.get("totalAssets") or info.get("marketCap") or 1
            caps[sector] = float(assets)
        except Exception:
            caps[sector] = 1.0
    return caps


def fetch_sector_performance(period: str, market_caps: dict[str, float] | None = None) -> list[dict]:
    """Fetch performance for all sector ETFs over the given period."""
    tickers = list(SECTOR_ETFS.values())
    data = yf.download(tickers, period=period if period != "ytd" else "1y",
                       progress=False, group_by="ticker")

    results = []
    now = datetime.now()

    for sector, etf in SECTOR_ETFS.items():
        try:
            if len(tickers) == 1:
                df = data
            else:
                df = data[etf]

            if df.empty:
                continue

            if period == "ytd":
                df = df[df.index.year == now.year]
                if df.empty:
                    continue

            start_price = df["Close"].dropna().iloc[0]
            end_price = df["Close"].dropna().iloc[-1]
            pct_change = ((end_price - start_price) / start_price) * 100

            cap = (market_caps or {}).get(sector, 1.0)

            results.append({
                "sector": sector,
                "etf": etf,
                "pct_change": round(float(pct_change), 2),
                "price": round(float(end_price), 2),
                "market_cap": cap,
            })
        except (KeyError, IndexError):
            continue

    return results


def build_treemap_trace(results: list[dict], visible: bool = False) -> go.Treemap:
    """Build a single treemap trace from sector results."""
    sectors = [r["sector"] for r in results]
    changes = [r["pct_change"] for r in results]
    etfs = [r["etf"] for r in results]

    max_abs = max(abs(c) for c in changes) if changes else 1
    max_abs = max(max_abs, 1)

    market_caps = [r["market_cap"] for r in results]

    def fmt_cap(cap):
        """Format market cap as human-readable string."""
        if cap >= 1e12:
            return f"${cap/1e12:.1f}T"
        if cap >= 1e9:
            return f"${cap/1e9:.1f}B"
        if cap >= 1e6:
            return f"${cap/1e6:.0f}M"
        return f"${cap:,.0f}"

    labels = [
        f"<b>{s}</b><br>{etf}<br>{c:+.1f}%<br>{fmt_cap(cap)}"
        for s, etf, c, cap in zip(sectors, etfs, changes, market_caps)
    ]

    market_caps = [r["market_cap"] for r in results]

    return go.Treemap(
        labels=labels,
        parents=[""] * len(sectors),
        values=market_caps,
        text=[f"{c:+.1f}%" for c in changes],
        textinfo="label",
        textfont=dict(size=16),
        visible=visible,
        marker=dict(
            colors=changes,
            colorscale=[
                [0, "#d32f2f"],
                [0.35, "#ef5350"],
                [0.5, "#424242"],
                [0.65, "#66bb6a"],
                [1, "#2e7d32"],
            ],
            cmid=0,
            cmin=-max_abs,
            cmax=max_abs,
            colorbar=dict(
                title=dict(text="% Change"),
                ticksuffix="%",
            ),
            line=dict(width=2, color="white"),
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
            "Change: %{customdata[2]:+.2f}%<br>"
            "Price: $%{customdata[3]:.2f}<br>"
            "AUM: %{customdata[4]}"
            "<extra></extra>"
        ),
        customdata=[
            [r["sector"], r["etf"], r["pct_change"], r["price"], fmt_cap(r["market_cap"])]
            for r in results
        ],
    )


READING_GUIDE_HTML = """
<div style="background:#1a1a1a; padding:12px 20px; font-family:sans-serif; font-size:13px; color:#aaaaaa; line-height:1.6;">
  <b>How to read:</b>
  Each block = one GICS sector (via ETF).
  <span style="color:#66bb6a">Green</span> = positive return,
  <span style="color:#ef5350">Red</span> = negative return.
  Deeper color = stronger move.
  Hover for details.
  Toggle period buttons above to compare timeframes and spot rotation.
</div>
"""


def _save_with_guide(fig: go.Figure, output_path: Path):
    """Save chart HTML with a responsive reading guide div below the plot."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chart_html = fig.to_html(include_plotlyjs="cdn", full_html=True)
    # Insert reading guide before closing </body>
    html = chart_html.replace("</body>", READING_GUIDE_HTML + "</body>")
    output_path.write_text(html)
    print(f"Heatmap saved to {output_path}")


def generate_interactive_heatmap(all_results: dict[str, list[dict]], output_path: Path):
    """Generate a heatmap with period toggle buttons."""
    fig = go.Figure()
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Add one trace per period
    for i, period in enumerate(ALL_PERIODS):
        results = all_results.get(period, [])
        if not results:
            continue
        is_default = (i == DEFAULT_PERIOD_INDEX)
        fig.add_trace(build_treemap_trace(results, visible=is_default))

    # Build toggle buttons
    buttons = []
    for i, period in enumerate(ALL_PERIODS):
        visibility = [False] * len(ALL_PERIODS)
        visibility[i] = True
        buttons.append(dict(
            label=PERIOD_MAP[period],
            method="update",
            args=[
                {"visible": visibility},
                {"title.text": f"Sector Performance Heatmap — {PERIOD_MAP[period]} | {date_str}"},
            ],
        ))

    default_label = PERIOD_MAP[ALL_PERIODS[DEFAULT_PERIOD_INDEX]]
    fig.update_layout(
        title=dict(
            text=f"Sector Performance Heatmap — {default_label} | {date_str}",
            font=dict(size=20),
        ),
        updatemenus=[dict(
            type="buttons",
            direction="right",
            x=0.5,
            xanchor="center",
            y=1.08,
            yanchor="top",
            buttons=buttons,
            bgcolor="#555555",
            bordercolor="#888888",
            borderwidth=1,
            font=dict(color="white", size=13),
            active=DEFAULT_PERIOD_INDEX,
            showactive=False,
        )],
        margin=dict(t=100, l=10, r=10, b=10),
        paper_bgcolor="#1a1a1a",
        plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
    )

    _save_with_guide(fig, output_path)


def generate_single_heatmap(results: list[dict], period: str, output_path: Path):
    """Generate a heatmap for a single period (no buttons)."""
    if not results:
        print("No data available.")
        return

    fig = go.Figure(build_treemap_trace(results, visible=True))

    fig.update_layout(
        title=dict(
            text=f"Sector Performance Heatmap — {PERIOD_MAP.get(period, period)} | {datetime.now().strftime('%Y-%m-%d')}",
            font=dict(size=20),
        ),
        margin=dict(t=60, l=10, r=10, b=10),
        paper_bgcolor="#1a1a1a",
        plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
    )

    _save_with_guide(fig, output_path)


def main():
    parser = argparse.ArgumentParser(description="Sector performance heatmap")
    parser.add_argument("--period", default=None,
                        choices=ALL_PERIODS,
                        help="Single period (omit for interactive with all periods)")
    parser.add_argument("--no-open", action="store_true",
                        help="Don't open in browser")
    args = parser.parse_args()

    output_path = Path(__file__).parent.parent / "charts" / "sector-heatmap.html"

    print("Fetching sector market caps...")
    market_caps = fetch_sector_market_caps()

    if args.period:
        # Single period mode
        print(f"Fetching sector performance ({args.period})...")
        results = fetch_sector_performance(args.period, market_caps)
        generate_single_heatmap(results, args.period, output_path)
    else:
        # Interactive mode — fetch all periods
        all_results = {}
        for period in ALL_PERIODS:
            print(f"Fetching sector performance ({period})...")
            all_results[period] = fetch_sector_performance(period, market_caps)
        generate_interactive_heatmap(all_results, output_path)

    if not args.no_open:
        webbrowser.open(f"file://{output_path.resolve()}")


if __name__ == "__main__":
    main()
