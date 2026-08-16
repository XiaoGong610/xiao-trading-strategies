#!/usr/bin/env python3
"""
Unified dashboard — portfolio + watchlist in one interactive HTML.

Combines portfolio account data with watchlist classified stock data to generate
a multi-tab HTML dashboard with: Portfolio Overview, RSI vs P/E, Earnings Calendar,
and cross-account Holdings table.

Usage:
    .venv/bin/python3 scripts/dashboard.py                    # auto-runs watchlist.py
    .venv/bin/python3 scripts/watchlist.py --json | .venv/bin/python3 scripts/dashboard.py
    .venv/bin/python3 scripts/dashboard.py --no-open          # don't open browser

Output: research/stocks/0-watchlist-dashboard-YYYY-MM-DD.html
"""

import argparse
import json
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

# Import shared functions from watchlist.py
sys.path.insert(0, str(Path(__file__).parent))
from watchlist import (
    parse_frontmatter,
    parse_portfolio_holdings,
    ACCOUNT_ABBREV,
    ACCOUNTS_DIR,
    SECTOR_TO_GICS,
)

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# --- Paths ---
OUTPUT_PATH = Path("research/stocks") / f"0-watchlist-dashboard-{date.today().isoformat()}.html"

# --- Colors ---
SECTOR_COLORS = {
    "Technology": "#1f77b4",
    "Healthcare": "#2ca02c",
    "Financials": "#ff7f0e",
    "Consumer Disc.": "#d62728",
    "Consumer Staples": "#9467bd",
    "Energy": "#8c564b",
    "Industrials": "#e377c2",
    "Materials": "#7f7f7f",
    "Real Estate": "#bcbd22",
    "Utilities": "#17becf",
    "Communication": "#aec7e8",
    "Other": "#888888",
}

ACCOUNT_COLORS = {
    "BROKERAGELINK": "#58a6ff",
    "ROTH IRA": "#3fb950",
    "HOLD": "#d29922",
    "THETAGANG": "#bc8cff",
    "GOBIG": "#f85149",
}


# --- Data loading ---

def load_watchlist_json() -> list[dict]:
    """Load watchlist data from stdin or by running watchlist.py --json."""
    # Try stdin first (when piped from watchlist.py)
    if not sys.stdin.isatty():
        try:
            data = sys.stdin.read()
            if data.strip():
                return json.loads(data)
        except (json.JSONDecodeError, ValueError):
            pass

    # Fall back to running watchlist.py --json
    print("Running watchlist.py --json...", file=sys.stderr)
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "watchlist.py"),
         "--json", "--no-save"],
        capture_output=True, text=True, timeout=180,
    )
    if result.returncode != 0:
        print(f"  watchlist.py failed: {result.stderr[:200]}", file=sys.stderr)
        return []
    return json.loads(result.stdout)


def load_account_summaries() -> list[dict]:
    """Load account-level summaries from frontmatter."""
    if not ACCOUNTS_DIR.exists():
        return []
    accounts = []
    for f in sorted(ACCOUNTS_DIR.glob("*.md")):
        fm = parse_frontmatter(f)
        if fm.get('account_name'):
            accounts.append({
                'name': fm['account_name'],
                'total_value': float(fm.get('total_value', 0)),
                'cash': float(fm.get('cash', 0)),
                'strategy': fm.get('strategy', ''),
                'last_updated': fm.get('last_updated', ''),
            })
    return accounts


def build_sector_map(watchlist: list[dict]) -> dict[str, str]:
    """Build {TICKER: GICS_sector} from watchlist data + research files."""
    sector_map: dict[str, str] = {}

    for s in watchlist:
        ticker = s.get('ticker')
        sector = s.get('sector', '')
        if ticker and sector:
            gics = SECTOR_TO_GICS.get(sector)
            if gics:
                sector_map[ticker] = gics

    stocks_dir = Path("research/stocks")
    if stocks_dir.exists():
        for f in stocks_dir.glob("*.md"):
            if f.name.startswith(('0-', '1-')):
                continue
            fm = parse_frontmatter(f)
            ticker = fm.get('ticker')
            if ticker and ticker not in sector_map:
                gics = SECTOR_TO_GICS.get(fm.get('sector', ''))
                if gics:
                    sector_map[ticker] = gics

    return sector_map


# --- Tab 1: Portfolio Overview ---

def _build_overview(accounts, holdings, sector_map, date_str):
    """Portfolio Overview — donut charts, metric cards, account bars."""
    total_value = sum(a['total_value'] for a in accounts)
    total_cash = sum(a['cash'] for a in accounts)

    # Aggregate position values by ticker
    stock_values: dict[str, float] = {}
    for ticker, positions in holdings.items():
        total = sum(p.get('value') or 0 for p in positions)
        if total > 0:
            stock_values[ticker] = total

    # --- Donut by stock ---
    sorted_stocks = sorted(stock_values.items(), key=lambda x: -x[1])
    top_n = 12
    top_stocks = sorted_stocks[:top_n]
    other_value = sum(v for _, v in sorted_stocks[top_n:])

    stock_labels = [t for t, _ in top_stocks]
    stock_vals = [v for _, v in top_stocks]
    if other_value > 0:
        stock_labels.append("Other")
        stock_vals.append(other_value)
    if total_cash > 0:
        stock_labels.append("Cash")
        stock_vals.append(total_cash)

    stock_fig = go.Figure(data=[go.Pie(
        labels=stock_labels, values=stock_vals,
        hole=0.45, textinfo='label+percent', textposition='inside',
        hovertemplate='<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>',
        sort=False,
        marker=dict(line=dict(color='#0d1117', width=2)),
    )])
    stock_fig.update_layout(
        title=dict(text="By Stock", font=dict(size=16, color='#e6edf3')),
        height=400, margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor='#161b22', font=dict(color='#e6edf3'),
        legend=dict(font=dict(size=11, color='#8b949e'), bgcolor='rgba(0,0,0,0)'),
    )

    # --- Donut by sector ---
    sector_values: dict[str, float] = {}
    for ticker, value in stock_values.items():
        sector = sector_map.get(ticker, 'Other')
        sector_values[sector] = sector_values.get(sector, 0) + value
    if total_cash > 0:
        sector_values['Cash'] = total_cash

    sorted_sectors = sorted(sector_values.items(), key=lambda x: -x[1])
    sector_labels = [s for s, _ in sorted_sectors]
    sector_vals = [v for _, v in sorted_sectors]
    sector_colors = [SECTOR_COLORS.get(s, '#888') if s != 'Cash' else '#4a4a4a'
                     for s in sector_labels]

    sector_fig = go.Figure(data=[go.Pie(
        labels=sector_labels, values=sector_vals,
        hole=0.45, textinfo='label+percent', textposition='inside',
        hovertemplate='<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>',
        sort=False,
        marker=dict(colors=sector_colors, line=dict(color='#0d1117', width=2)),
    )])
    sector_fig.update_layout(
        title=dict(text="By Sector", font=dict(size=16, color='#e6edf3')),
        height=400, margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor='#161b22', font=dict(color='#e6edf3'),
        legend=dict(font=dict(size=11, color='#8b949e'), bgcolor='rgba(0,0,0,0)'),
    )

    stock_html = stock_fig.to_html(include_plotlyjs=False, full_html=False, div_id="pie-stock")
    sector_html = sector_fig.to_html(include_plotlyjs=False, full_html=False, div_id="pie-sector")

    # --- Account bars ---
    account_bars = ""
    for a in sorted(accounts, key=lambda x: -x['total_value']):
        pct = (a['total_value'] / total_value * 100) if total_value > 0 else 0
        abbrev = ACCOUNT_ABBREV.get(a['name'], a['name'])
        color = ACCOUNT_COLORS.get(a['name'], '#888')
        cash_pct = (a['cash'] / a['total_value'] * 100) if a['total_value'] > 0 else 0
        account_bars += (
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">'
            f'<div style="width:60px;color:#8b949e;font-size:13px;text-align:right;">{abbrev}</div>'
            f'<div style="flex:1;background:#21262d;border-radius:4px;height:28px;position:relative;overflow:hidden;">'
            f'<div style="width:{pct}%;background:{color};height:100%;border-radius:4px;opacity:0.85;"></div>'
            f'<div style="position:absolute;top:4px;left:8px;font-size:12px;font-weight:600;">'
            f'${a["total_value"]/1000:.0f}K ({pct:.1f}%)</div>'
            f'</div>'
            f'<div style="width:80px;color:#8b949e;font-size:12px;">cash {cash_pct:.0f}%</div>'
            f'</div>'
        )

    n_positions = len(stock_values)
    last_updated = max((a['last_updated'] for a in accounts if a['last_updated']), default='—')

    return f"""
    <div class="metrics">
      <div class="metric">
        <div class="label">Total Portfolio</div>
        <div class="value" style="color:#3fb950">${total_value/1000:.0f}K</div>
      </div>
      <div class="metric">
        <div class="label">Total Cash</div>
        <div class="value">${total_cash/1000:.0f}K <span style="font-size:14px;color:#8b949e">({total_cash/total_value*100:.1f}%)</span></div>
      </div>
      <div class="metric">
        <div class="label">Positions</div>
        <div class="value">{n_positions}</div>
      </div>
      <div class="metric">
        <div class="label">Last Updated</div>
        <div class="value" style="font-size:18px;">{last_updated}</div>
      </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px;">
      <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:8px;">
        {stock_html}
      </div>
      <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:8px;">
        {sector_html}
      </div>
    </div>
    <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;">
      <div style="font-size:14px;font-weight:600;margin-bottom:12px;">Account Breakdown</div>
      {account_bars}
    </div>
    """


# --- Tab 2: RSI vs P/E Scatter ---

def _build_scatter(stocks, date_str):
    """RSI vs Forward P/E scatter plot with held stock markers."""
    plottable = [s for s in stocks
                 if s.get('rsi') is not None and s.get('fwd_pe') is not None]

    fig = go.Figure()

    # Group by GICS sector
    sector_groups: dict[str, list] = {}
    for s in plottable:
        gics = SECTOR_TO_GICS.get(s.get('sector', ''), 'Other') or 'Other'
        sector_groups.setdefault(gics, []).append(s)

    for sector in sorted(sector_groups.keys()):
        ss = sector_groups[sector]
        color = SECTOR_COLORS.get(sector, "#888888")

        sizes = []
        for s in ss:
            gap = s.get('gap_pct')
            sizes.append(max(8, min(22, 22 - abs(gap) * 0.5)) if gap is not None else 12)

        hover_texts = []
        for s in ss:
            target = f"${s['entry_target']}" if s.get('entry_target') else "—"
            gap = f"{s['gap_pct']:+.1f}%" if s.get('gap_pct') is not None else "—"
            price = f"${s['price']:.2f}" if s.get('price') else "—"
            conv = f"{s['conviction']:.1f}" if s.get('conviction') else "?"
            earn = f"{s['earnings_days']}d" if s.get('earnings_days') and s['earnings_days'] > 0 else "—"
            held_line = ""
            if s.get('held_in'):
                accts = [ACCOUNT_ABBREV.get(h['account'], h['account'])
                         for h in s['held_in']]
                hv = s.get('total_held_value', 0)
                held_line = (f"<br><b>Held:</b> {', '.join(accts)}"
                             + (f" (${hv/1000:.0f}K)" if hv >= 1000 else ""))
            hover_texts.append(
                f"<b>{s['ticker']}</b><br>Price: {price}<br>"
                f"RSI: {s['rsi']}<br>Fwd P/E: {s['fwd_pe']:.1f}x<br>"
                f"Sector: {s.get('sector', '')}<br>"
                f"Conv: {conv} | Target: {target} | Gap: {gap}<br>"
                f"Earnings: {earn}{held_line}"
            )

        line_widths = [2.5 if s.get('held_in') else 1 for s in ss]

        fig.add_trace(go.Scatter(
            x=[s['rsi'] for s in ss],
            y=[s['fwd_pe'] for s in ss],
            mode="markers+text", name=sector,
            text=[s['ticker'] for s in ss],
            textposition="top center",
            textfont=dict(size=11, color="#cccccc"),
            hovertext=hover_texts, hoverinfo="text",
            marker=dict(size=sizes, color=color, opacity=0.85,
                        line=dict(width=line_widths, color="#ffffff")),
        ))

    fig.add_vline(x=30, line_dash="dash", line_color="#66bb6a", line_width=1)
    fig.add_vline(x=70, line_dash="dash", line_color="#ef5350", line_width=1)
    fig.add_hline(y=25, line_dash="dash", line_color="#888888", line_width=1)
    fig.add_annotation(x=15, y=6, text="OVERSOLD + CHEAP", showarrow=False,
                       font=dict(size=13, color="#66bb6a", family="Arial Black"), opacity=0.4)
    fig.add_annotation(x=80, y=200, text="OVERBOUGHT + EXPENSIVE", showarrow=False,
                       font=dict(size=13, color="#ef5350", family="Arial Black"), opacity=0.4)

    fig.update_layout(
        title=dict(text=f"RSI vs Forward P/E | {date_str}", font=dict(size=18)),
        xaxis=dict(title="RSI (14-period)", gridcolor="#333333", zeroline=False),
        yaxis=dict(title="Forward P/E (log scale)", type="log",
                   range=[0.6, 3.0], gridcolor="#333333", zeroline=False,
                   tickvals=[5, 10, 15, 25, 50, 100, 200, 500],
                   ticktext=["5x", "10x", "15x", "25x", "50x", "100x", "200x", "500x"]),
        legend=dict(title="Sector", bgcolor="rgba(30,30,30,0.8)",
                    bordercolor="#555555", borderwidth=1, font=dict(color="white")),
        height=650, margin=dict(t=60, l=60, r=30, b=60),
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="white"),
        hoverlabel=dict(bgcolor="#2a2a2a", bordercolor="#555555",
                        font_size=13, font_color="white"),
    )
    return fig


# --- Tab 3: Earnings Calendar ---

def _build_earnings(stocks, date_str):
    """Earnings calendar horizontal bar chart."""
    today = datetime.now().date()
    current_year = datetime.now().year

    entries = []
    for s in stocks:
        days = s.get('earnings_days')
        earn_str = s.get('earnings')
        if days is None or days <= 0 or earn_str is None:
            continue
        for fmt in ['%B %d, %Y', '%B %d', '%b %d, %Y', '%b %d']:
            try:
                dt = datetime.strptime(earn_str.strip('*'), fmt)
                if dt.year < current_year:
                    dt = dt.replace(year=current_year)
                entries.append({
                    'ticker': s['ticker'], 'earnings_date': dt.date(),
                    'days_until': days, 'sector': s.get('sector', ''),
                    'conviction': s.get('conviction'),
                    'held': bool(s.get('held_in')),
                })
                break
            except ValueError:
                continue

    if not entries:
        return None

    entries.sort(key=lambda e: e['earnings_date'], reverse=True)
    fig = go.Figure()

    for e in entries:
        earn_date = e['earnings_date']
        d = e['days_until']
        color = "#ef5350" if d < 7 else "#ffa726" if d < 14 else "#ffee58" if d < 30 else "#66bb6a"
        urgency = "IMMINENT" if d < 7 else "SOON" if d < 14 else "UPCOMING" if d < 30 else "SAFE"
        conv = f"{e['conviction']:.1f}" if e.get('conviction') else "?"
        held = "Yes" if e['held'] else "No"

        fig.add_trace(go.Bar(
            y=[e['ticker']], x=[(earn_date - today).days],
            base=[today.isoformat()], orientation="h",
            marker=dict(color=color, opacity=0.85, line=dict(width=0)),
            hovertemplate=(
                f"<b>{e['ticker']}</b><br>Earnings: {earn_date.strftime('%b %d, %Y')}<br>"
                f"Days: {d}<br>Sector: {e['sector']}<br>Conv: {conv}<br>"
                f"Held: {held}<br>Urgency: {urgency}<extra></extra>"
            ),
            showlegend=False,
        ))
        mid_date = today + (earn_date - today) / 2
        fig.add_annotation(x=mid_date.isoformat(), y=e['ticker'],
                           text=f"<b>{d}d</b>", showarrow=False,
                           font=dict(color="white", size=12))

    fig.add_shape(type="line", x0=today.isoformat(), x1=today.isoformat(),
                  y0=0, y1=1, yref="paper",
                  line=dict(color="white", width=2, dash="dash"))
    fig.add_annotation(x=today.isoformat(), y=1, yref="paper",
                       text="TODAY", showarrow=False,
                       font=dict(color="white", size=12), yshift=10)

    fig.update_layout(
        title=dict(text=f"Earnings Calendar | {date_str}", font=dict(size=18)),
        xaxis=dict(title="Date", type="date", gridcolor="#333333",
                   tickfont=dict(color="#cccccc")),
        yaxis=dict(title="", tickfont=dict(color="#cccccc", size=13), automargin=True),
        barmode="overlay", height=max(400, len(entries) * 35 + 120),
        margin=dict(t=60, l=10, r=30, b=60),
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="white"),
    )
    return fig


# --- Tab 4: Holdings Table ---

def _build_holdings_table(holdings, watchlist, sector_map):
    """Cross-account holdings table grouped by GICS sector."""
    wl_lookup = {s['ticker']: s for s in watchlist}

    # Aggregate per ticker
    ticker_data = {}
    for ticker, positions in holdings.items():
        total_shares = sum(p.get('shares') or 0 for p in positions)
        total_value = sum(p.get('value') or 0 for p in positions)
        accounts = sorted(set(
            ACCOUNT_ABBREV.get(p['account'], p['account']) for p in positions
        ))
        is_option_only = all(p.get('is_option') for p in positions)
        wl = wl_lookup.get(ticker, {})

        ticker_data[ticker] = {
            'ticker': ticker,
            'sector': sector_map.get(ticker, 'Other'),
            'accounts': ', '.join(accounts),
            'shares': total_shares if not is_option_only else None,
            'value': total_value,
            'conviction': wl.get('conviction'),
            'rsi': wl.get('rsi'),
            'fwd_pe': wl.get('fwd_pe'),
        }

    total_portfolio = sum(d['value'] for d in ticker_data.values()) or 1

    # Group by sector
    sectors: dict[str, list] = {}
    for d in ticker_data.values():
        sectors.setdefault(d['sector'], []).append(d)
    for sector in sectors:
        sectors[sector].sort(key=lambda x: -x['value'])

    rows = []
    for sector in sorted(sectors.keys(),
                         key=lambda s: -sum(d['value'] for d in sectors[s])):
        sector_total = sum(d['value'] for d in sectors[sector])
        sector_pct = sector_total / total_portfolio * 100
        color = SECTOR_COLORS.get(sector, '#888')

        rows.append(
            f'<tr style="background:#161b22;font-weight:600;">'
            f'<td style="border-left:3px solid {color};padding-left:12px;">{sector}</td>'
            f'<td></td><td></td>'
            f'<td style="text-align:right;">${sector_total/1000:.0f}K</td>'
            f'<td style="text-align:right;">{sector_pct:.1f}%</td>'
            f'<td></td><td></td><td></td></tr>'
        )

        for d in sectors[sector]:
            pct = d['value'] / total_portfolio * 100
            conv = f"{d['conviction']:.1f}" if d['conviction'] else "—"
            rsi = f"{d['rsi']:.0f}" if d['rsi'] else "—"
            pe = f"{d['fwd_pe']:.1f}x" if d['fwd_pe'] else "—"
            shares = f"{d['shares']:,.1f}" if d['shares'] else "opts"
            value = f"${d['value']:,.0f}" if d['value'] > 0 else "—"

            rows.append(
                f'<tr>'
                f'<td style="padding-left:28px;color:#8b949e;">{d["ticker"]}</td>'
                f'<td>{d["accounts"]}</td>'
                f'<td style="text-align:right;">{shares}</td>'
                f'<td style="text-align:right;">{value}</td>'
                f'<td style="text-align:right;">{pct:.1f}%</td>'
                f'<td style="text-align:center;">{conv}</td>'
                f'<td style="text-align:center;">{rsi}</td>'
                f'<td style="text-align:center;">{pe}</td></tr>'
            )

    return (
        '<table><thead><tr>'
        '<th>Sector / Ticker</th><th>Accounts</th>'
        '<th style="text-align:right;">Shares</th>'
        '<th style="text-align:right;">Value</th>'
        '<th style="text-align:right;">% Port</th>'
        '<th style="text-align:center;">Conv</th>'
        '<th style="text-align:center;">RSI</th>'
        '<th style="text-align:center;">Fwd P/E</th>'
        '</tr></thead><tbody>'
        + ''.join(rows)
        + '</tbody></table>'
    )


# --- Tab 5: Trading Plan (from latest PLAN markdown) ---

def _load_latest_plan() -> tuple[str, str]:
    """Find and render the most recent PLAN markdown as HTML.

    Returns (plan_html, plan_date) or ('', '') if no plan found.
    """
    plans_dir = Path("portfolio/plans")
    if not plans_dir.exists():
        return '', ''

    plan_files = sorted(plans_dir.glob("PLAN-*.md"), reverse=True)
    if not plan_files:
        return '', ''

    plan_path = plan_files[0]
    # Extract date from filename: PLAN-2026-08-08.md → 2026-08-08
    plan_date = plan_path.stem.replace('PLAN-', '')
    content = plan_path.read_text(encoding="utf-8")

    return _render_plan_md(content), plan_date


def _render_plan_md(md: str) -> str:
    """Convert plan markdown to styled HTML. Lightweight parser for tables and headers."""
    import re
    lines = md.split('\n')
    html_parts = []
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            return
        # First row is header, second is separator, rest are data
        header = table_rows[0]
        data = [r for r in table_rows[1:] if not all(c.strip(' -') == '' for c in r)]
        cols = [c.strip() for c in header]

        thead = '<tr>' + ''.join(f'<th>{c}</th>' for c in cols) + '</tr>'
        tbody = ''
        for row in data:
            cells = [c.strip() for c in row]
            # Pad or trim to match header length
            while len(cells) < len(cols):
                cells.append('')
            style = ''
            first = cells[0] if cells else ''
            # Color-code action types
            if any(k in first for k in ['SELL', 'TAKE PROFIT', 'CLOSE']):
                style = ' style="border-left:3px solid #f85149;"'
            elif any(k in first for k in ['BUY', 'RESUME', 'RESUMED']):
                style = ' style="border-left:3px solid #3fb950;"'
            elif any(k in first for k in ['ROLL', 'MONITOR']):
                style = ' style="border-left:3px solid #d29922;"'
            elif any(k in first for k in ['HOLD', 'DELIBERATE']):
                style = ' style="border-left:3px solid #58a6ff;"'
            elif any(k in first for k in ['LET EXPIRE']):
                style = ' style="border-left:3px solid #8b949e;"'
            tbody += f'<tr{style}>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>'

        html_parts.append(f'<table><thead>{thead}</thead><tbody>{tbody}</tbody></table>')
        table_rows = []
        in_table = False

    for line in lines:
        stripped = line.strip()

        # Table rows
        if stripped.startswith('|') and stripped.endswith('|'):
            cells = stripped.split('|')[1:-1]
            # Skip separator rows
            if all(c.strip().replace('-', '').replace(':', '') == '' for c in cells):
                if not in_table:
                    in_table = True
                continue
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(cells)
            continue
        elif in_table:
            flush_table()

        # Headers
        if stripped.startswith('# '):
            html_parts.append(f'<h2 style="margin:24px 0 8px;font-size:20px;color:#e6edf3;">'
                              f'{stripped[2:]}</h2>')
        elif stripped.startswith('## '):
            html_parts.append(f'<h3 style="margin:20px 0 8px;font-size:16px;color:#e6edf3;'
                              f'border-bottom:1px solid #30363d;padding-bottom:6px;">'
                              f'{stripped[3:]}</h3>')
        elif stripped.startswith('### '):
            html_parts.append(f'<h4 style="margin:16px 0 6px;font-size:14px;color:#8b949e;">'
                              f'{stripped[4:]}</h4>')
        elif stripped == '---':
            html_parts.append('<hr style="border:none;border-top:1px solid #30363d;margin:16px 0;">')
        elif stripped.startswith('**') and stripped.endswith('**') and len(stripped) > 4:
            # Bold standalone line → callout
            html_parts.append(f'<p style="color:#e6edf3;font-weight:600;margin:8px 0;">'
                              f'{stripped}</p>')
        elif stripped:
            # Numbered list items (1. 2. 3.)
            m = re.match(r'^(\d+)\.\s+(.+)', stripped)
            if m:
                html_parts.append(
                    f'<div style="margin:8px 0;padding:12px 16px;background:#161b22;'
                    f'border:1px solid #30363d;border-radius:8px;line-height:1.5;">'
                    f'<span style="color:#58a6ff;font-weight:700;margin-right:8px;">'
                    f'{m.group(1)}.</span>{m.group(2)}</div>'
                )
            else:
                html_parts.append(f'<p style="margin:6px 0;line-height:1.5;">{stripped}</p>')

    if in_table:
        flush_table()

    return '\n'.join(html_parts)


# --- HTML Assembly ---

def generate_dashboard(watchlist, accounts, holdings, sector_map, no_open=False):
    """Generate unified HTML dashboard with 4 tabs."""
    date_str = date.today().isoformat()
    total_value = sum(a['total_value'] for a in accounts)
    n_positions = len(holdings)

    overview_html = _build_overview(accounts, holdings, sector_map, date_str)

    all_stocks = [s for s in watchlist if s.get('tier') in ('active', 'candidate', 'passive')]
    scatter_fig = _build_scatter(all_stocks, date_str)
    scatter_html = scatter_fig.to_html(
        include_plotlyjs=False, full_html=False, div_id="scatter")

    earnings_fig = _build_earnings(all_stocks, date_str)
    earnings_html = (
        earnings_fig.to_html(include_plotlyjs=False, full_html=False, div_id="earnings")
        if earnings_fig else
        "<p style='color:#8b949e;padding:40px;'>No upcoming earnings found.</p>"
    )

    holdings_html = _build_holdings_table(holdings, watchlist, sector_map)

    # Trading plan (optional — from most recent PLAN markdown)
    plan_html, plan_date = _load_latest_plan()
    plan_tab = (f'<div class="tab" onclick="showTab(\'plan\')">Trading Plan</div>'
                if plan_html else '')
    plan_panel = ''
    if plan_html:
        plan_panel = f"""
<div id="panel-plan" class="panel">
  <div class="guide" style="margin-bottom:16px;margin-top:0;">
    Source: <code>portfolio/plans/PLAN-{plan_date}.md</code>
  </div>
  {plan_html}
</div>"""

    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>Dashboard — {date_str}</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  :root {{ --bg:#0d1117; --card:#161b22; --border:#30363d; --text:#e6edf3;
           --muted:#8b949e; --green:#3fb950; --red:#f85149; --orange:#d29922;
           --blue:#58a6ff; --purple:#bc8cff; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text);
          font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }}
  .tabs {{ display:flex; gap:0; background:#010409; border-bottom:2px solid var(--border);
           padding:0 20px; position:sticky; top:0; z-index:100; }}
  .tab {{ padding:12px 24px; cursor:pointer; color:var(--muted); font-size:14px;
          font-weight:600; border-bottom:3px solid transparent; transition:all 0.2s; }}
  .tab:hover {{ color:#c9d1d9; }}
  .tab.active {{ color:var(--text); border-bottom-color:var(--blue); }}
  .panel {{ display:none; padding:20px; max-width:1400px; margin:0 auto; }}
  .panel.active {{ display:block; }}
  .metrics {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:24px; }}
  .metric {{ background:var(--card); border:1px solid var(--border); border-radius:8px; padding:16px; }}
  .metric .label {{ color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:0.5px; }}
  .metric .value {{ font-size:28px; font-weight:700; margin-top:4px; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th {{ text-align:left; padding:8px 12px; border-bottom:2px solid var(--border);
       color:var(--muted); font-weight:600; font-size:12px; text-transform:uppercase; }}
  td {{ padding:8px 12px; border-bottom:1px solid #21262d; }}
  tr:hover {{ background:var(--card); }}
  .guide {{ background:var(--card); padding:12px 20px; font-size:13px; color:var(--muted);
            line-height:1.6; border-top:1px solid var(--border); margin-top:20px; border-radius:8px; }}
  h1 {{ margin:0; padding:16px 20px 0; font-size:22px; }}
  .subtitle {{ padding:0 20px 8px; font-size:13px; color:#484f58; }}
</style>
</head><body>
<h1>Dashboard</h1>
<p class="subtitle">Generated {date_str} &middot; {n_positions} positions &middot; ${total_value/1000:.0f}K portfolio</p>
<div class="tabs">
  <div class="tab active" onclick="showTab('overview')">Portfolio</div>
  <div class="tab" onclick="showTab('scatter')">RSI vs P/E</div>
  <div class="tab" onclick="showTab('earnings')">Earnings</div>
  <div class="tab" onclick="showTab('holdings')">Holdings</div>
  {plan_tab}
</div>
<div id="panel-overview" class="panel active">
  {overview_html}
</div>
<div id="panel-scatter" class="panel">
  {scatter_html}
  <div class="guide">
    <b>How to read:</b> Each dot = one stock.
    <b>X-axis:</b> RSI (momentum) — left is oversold, right is overbought.
    <b>Y-axis:</b> Forward P/E (valuation) — bottom is cheap, top is expensive.
    <span style="color:#66bb6a"><b>Bottom-left</b></span> = best opportunities (oversold + cheap).
    <span style="color:#ef5350"><b>Top-right</b></span> = most stretched.
    Dot color = sector. Bigger dot = closer to entry target. <b>Thick border = held in portfolio.</b> Hover for details.
  </div>
</div>
<div id="panel-earnings" class="panel">
  {earnings_html}
  <div class="guide">
    <b>How to read:</b> Each bar = days until earnings.
    <span style="color:#ef5350">Red</span> = &lt;7 days (imminent),
    <span style="color:#ffa726">Orange</span> = 7-14 days (soon),
    <span style="color:#ffee58">Yellow</span> = 14-30 days (upcoming),
    <span style="color:#66bb6a">Green</span> = 30+ days (safe).
    White dashed line = today.
  </div>
</div>
<div id="panel-holdings" class="panel">
  {holdings_html}
  <div class="guide">
    <b>How to read:</b> All positions grouped by GICS sector, aggregated across accounts.
    Conv / RSI / Fwd P/E from watchlist data. Sector rows show total value and portfolio weight.
  </div>
</div>
{plan_panel}
<script>
function showTab(name) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('panel-' + name).classList.add('active');
  window.dispatchEvent(new Event('resize'));
}}
</script>
</body></html>"""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Dashboard saved to {OUTPUT_PATH}")

    if not no_open:
        subprocess.run(["open", str(OUTPUT_PATH)], check=False)


def main():
    parser = argparse.ArgumentParser(description="Unified portfolio + watchlist dashboard")
    parser.add_argument("--no-open", action="store_true", help="Don't open browser")
    args = parser.parse_args()

    if not HAS_PLOTLY:
        print("Error: plotly required. Install: pip install plotly", file=sys.stderr)
        sys.exit(1)

    watchlist = load_watchlist_json()
    accounts = load_account_summaries()
    holdings = parse_portfolio_holdings()
    sector_map = build_sector_map(watchlist)

    generate_dashboard(watchlist, accounts, holdings, sector_map,
                       no_open=args.no_open)


if __name__ == "__main__":
    main()
