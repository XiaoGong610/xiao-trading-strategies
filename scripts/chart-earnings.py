#!/usr/bin/env python3
"""
chart-earnings.py — Earnings calendar timeline for watchlist stocks.

Visual countdown showing which stocks report earnings soon.
Generates an interactive Plotly horizontal bar chart.

Usage:
    .venv/bin/python3 scripts/chart-earnings.py              # generate chart
    .venv/bin/python3 scripts/chart-earnings.py --no-open     # don't open browser
    .venv/bin/python3 scripts/chart-earnings.py --all         # include non-watching stocks too

Outputs an interactive Plotly chart to charts/earnings-calendar.html.
"""

import argparse
import re
import webbrowser
from datetime import datetime, date
from pathlib import Path

import yfinance as yf
import plotly.graph_objects as go

STOCKS_DIR = Path(__file__).parent.parent / "research" / "stocks"
OUTPUT_PATH = Path(__file__).parent.parent / "charts" / "earnings-calendar.html"


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


def load_stocks(include_all: bool = False) -> list[dict]:
    """Load stock files, optionally filtering to watching-only."""
    stocks = []
    if not STOCKS_DIR.exists():
        print(f"Directory not found: {STOCKS_DIR}")
        return stocks

    for filepath in sorted(STOCKS_DIR.glob("*.md")):
        if filepath.name in ("0-INDEX.md", "1-DASHBOARD.md") or filepath.name.startswith("."):
            continue

        fm = parse_frontmatter(filepath)
        if not fm.get("ticker"):
            continue

        status = fm.get("status", "unknown")
        if not include_all and status != "watching":
            continue

        strategies = fm.get("strategies", [])
        if isinstance(strategies, str):
            strategies = [strategies]

        stocks.append({
            "ticker": fm["ticker"],
            "status": status,
            "sector": fm.get("sector", "Unknown"),
            "strategies": strategies,
        })

    return stocks


def fetch_earnings_date(ticker: str) -> date | None:
    """Fetch next earnings date for a ticker using yfinance."""
    try:
        cal = yf.Ticker(ticker).calendar
        if cal is None:
            return None

        # cal can be a dict or a DataFrame
        if isinstance(cal, dict):
            earnings = cal.get("Earnings Date")
            if earnings is None:
                return None
            if isinstance(earnings, list) and len(earnings) > 0:
                val = earnings[0]
            else:
                val = earnings
        else:
            # DataFrame — try to get Earnings Date row
            try:
                val = cal.loc["Earnings Date"].iloc[0]
            except (KeyError, IndexError):
                return None

        # Convert to date
        if hasattr(val, "date"):
            return val.date()
        if isinstance(val, str):
            for fmt in ("%Y-%m-%d", "%b %d, %Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(val, fmt).date()
                except ValueError:
                    continue
        return None
    except Exception:
        return None


def urgency_color(days: int) -> str:
    """Return color based on days until earnings."""
    if days < 7:
        return "#ef5350"   # red — imminent
    elif days < 14:
        return "#ffa726"   # orange — soon
    elif days < 30:
        return "#ffee58"   # yellow — upcoming
    else:
        return "#66bb6a"   # green — safe


def urgency_label(days: int) -> str:
    """Return urgency label for the reading guide."""
    if days < 7:
        return "IMMINENT"
    elif days < 14:
        return "SOON"
    elif days < 30:
        return "UPCOMING"
    else:
        return "SAFE"


def print_terminal_summary(entries: list[dict]):
    """Print a simple terminal summary table."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    print()
    print("=" * 60)
    print(f"  EARNINGS CALENDAR — {today_str}")
    print("=" * 60)
    print(f"  {'Ticker':<10s} {'Earnings Date':<16s} {'Days':>6s}  {'Urgency':<10s}")
    print(f"  {'-'*10} {'-'*16} {'-'*6}  {'-'*10}")

    for e in entries:
        ticker = e["ticker"]
        earn_date = e["earnings_date"].strftime("%Y-%m-%d")
        days = e["days_until"]
        urgency = urgency_label(days)
        print(f"  {ticker:<10s} {earn_date:<16s} {days:>6d}  {urgency:<10s}")

    print()
    print(f"  {len(entries)} stocks with upcoming earnings")
    print("=" * 60)
    print()


READING_GUIDE_HTML = """
<div style="background:#1a1a1a; padding:12px 20px; font-family:sans-serif; font-size:13px; color:#aaaaaa; line-height:1.6;">
  <b>How to read:</b>
  Each bar = time until a stock's next earnings report.
  <span style="color:#ef5350">Red</span> = &lt;7 days (imminent),
  <span style="color:#ffa726">Orange</span> = 7-14 days (soon),
  <span style="color:#ffee58">Yellow</span> = 14-30 days (upcoming),
  <span style="color:#66bb6a">Green</span> = 30+ days (safe).
  Vertical white line = today.
  Hover for details (sector, strategies, exact date).
</div>
"""


def _save_with_guide(fig: go.Figure, output_path: Path):
    """Save chart HTML with a responsive reading guide div below the plot."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chart_html = fig.to_html(include_plotlyjs="cdn", full_html=True)
    html = chart_html.replace("</body>", READING_GUIDE_HTML + "</body>")
    output_path.write_text(html)
    print(f"Chart saved to {output_path}")


def build_chart(entries: list[dict], output_path: Path):
    """Build the Plotly horizontal bar chart."""
    if not entries:
        print("No stocks with upcoming earnings data found.")
        return

    today = datetime.now().date()
    date_str = today.strftime("%Y-%m-%d")

    # Sort by earnings date ascending (soonest at top in the chart means
    # we reverse for plotly since y-axis goes bottom-to-top)
    entries_sorted = sorted(entries, key=lambda e: e["earnings_date"], reverse=True)

    fig = go.Figure()

    for e in entries_sorted:
        earn_date = e["earnings_date"]
        strategies_str = ", ".join(e["strategies"]) if e["strategies"] else "—"
        color = urgency_color(e["days_until"])

        # Horizontal bar from today to earnings date
        fig.add_trace(go.Bar(
            y=[e["ticker"]],
            x=[(earn_date - today).days],
            base=[today.isoformat()],
            orientation="h",
            marker=dict(color=color, opacity=0.85, line=dict(width=0)),
            hovertemplate=(
                f"<b>{e['ticker']}</b><br>"
                f"Earnings: {earn_date.strftime('%b %d, %Y')}<br>"
                f"Days until: {e['days_until']}<br>"
                f"Sector: {e['sector']}<br>"
                f"Strategies: {strategies_str}<br>"
                f"Urgency: {urgency_label(e['days_until'])}"
                "<extra></extra>"
            ),
            showlegend=False,
        ))

        # Add days annotation on the bar
        mid_date = today + (earn_date - today) / 2
        fig.add_annotation(
            x=mid_date.isoformat(),
            y=e["ticker"],
            text=f"<b>{e['days_until']}d</b>",
            showarrow=False,
            font=dict(color="white", size=12),
        )

    # Add vertical TODAY line
    fig.add_vline(
        x=today.isoformat(),
        line=dict(color="white", width=2, dash="dash"),
        annotation_text="TODAY",
        annotation_position="top",
        annotation=dict(font=dict(color="white", size=12)),
    )

    # Chart height scales with number of stocks
    chart_height = max(400, len(entries_sorted) * 40 + 120)

    fig.update_layout(
        title=dict(
            text=f"Earnings Calendar — Watchlist | {date_str}",
            font=dict(size=20),
        ),
        xaxis=dict(
            title="Date",
            type="date",
            gridcolor="#333333",
            tickfont=dict(color="#cccccc"),
        ),
        yaxis=dict(
            title="",
            tickfont=dict(color="#cccccc", size=13),
            automargin=True,
        ),
        barmode="overlay",
        height=chart_height,
        margin=dict(t=80, l=10, r=30, b=60),
        paper_bgcolor="#1a1a1a",
        plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
    )

    _save_with_guide(fig, output_path)


def main():
    parser = argparse.ArgumentParser(description="Earnings calendar timeline chart")
    parser.add_argument("--no-open", action="store_true",
                        help="Don't open in browser")
    parser.add_argument("--all", action="store_true",
                        help="Include non-watching stocks too")
    args = parser.parse_args()

    stocks = load_stocks(include_all=args.all)
    if not stocks:
        print("No stocks found.")
        return

    label = "all" if args.all else "watching"
    print(f"Found {len(stocks)} {label} stocks. Fetching earnings dates...")

    today = datetime.now().date()
    entries = []

    for s in stocks:
        ticker = s["ticker"]
        earn_date = fetch_earnings_date(ticker)
        if earn_date is None:
            print(f"  {ticker}: no earnings date found, skipping")
            continue
        if earn_date < today:
            print(f"  {ticker}: earnings date {earn_date} is in the past, skipping")
            continue

        days_until = (earn_date - today).days
        entries.append({
            "ticker": ticker,
            "earnings_date": earn_date,
            "days_until": days_until,
            "sector": s["sector"],
            "strategies": s["strategies"],
        })
        print(f"  {ticker}: {earn_date} ({days_until} days)")

    # Sort by earnings date ascending (soonest first)
    entries.sort(key=lambda e: e["earnings_date"])

    # Terminal summary
    print_terminal_summary(entries)

    # Build chart
    build_chart(entries, OUTPUT_PATH)

    if not args.no_open:
        webbrowser.open(f"file://{OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    main()
