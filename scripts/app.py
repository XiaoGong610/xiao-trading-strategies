#!/usr/bin/env python3
"""
Xiao Trading Agent — Interactive Dashboard (Streamlit)

Run: .venv/bin/python3 -m streamlit run scripts/app.py
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# --- Config ---
ROOT = Path(__file__).resolve().parent.parent
STOCKS_DIR = ROOT / "research" / "stocks"
SECTORS_DIR = ROOT / "research" / "sectors"
ACCOUNTS_DIR = ROOT / "portfolio" / "accounts"
KNOWLEDGE_DIR = ROOT / "knowledge"
PYTHON = ROOT / ".venv" / "bin" / "python3"

st.set_page_config(
    page_title="Xiao Trading Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --- Data Loading ---
@st.cache_data(ttl=300)
def parse_frontmatter(filepath: Path) -> dict:
    content = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value.startswith("[") and value.endswith("]"):
                value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
            fm[key] = value
    return fm


@st.cache_data(ttl=300)
def load_all_stocks() -> list[dict]:
    stocks = []
    if not STOCKS_DIR.exists():
        return stocks
    for f in STOCKS_DIR.glob("*.md"):
        if f.name.startswith(("0-", "1-")):
            continue
        fm = parse_frontmatter(f)
        if not fm.get("ticker"):
            continue
        # Find last update date
        content = f.read_text(encoding="utf-8")
        dates = re.findall(r"\|\s*(\d{4}-\d{2}-\d{2})", content)
        if not dates:
            dates = re.findall(r"(\d{4}-\d{2}-\d{2})", content[:2000])
        last_update = max(dates) if dates else None
        days_stale = (
            (datetime.now() - datetime.strptime(last_update, "%Y-%m-%d")).days
            if last_update
            else 999
        )
        stocks.append(
            {
                "ticker": fm.get("ticker", ""),
                "status": fm.get("status", "unknown"),
                "sector": fm.get("sector", ""),
                "thesis": fm.get("thesis", ""),
                "entry_target": fm.get("entry_target", ""),
                "conviction": fm.get("conviction", ""),
                "strategies": fm.get("strategies", []),
                "last_update": last_update,
                "days_stale": days_stale,
            }
        )
    return sorted(stocks, key=lambda s: s["ticker"])


@st.cache_data(ttl=300)
def load_market_overview() -> dict:
    f = SECTORS_DIR / "market-overview.md"
    if not f.exists():
        return {}
    content = f.read_text(encoding="utf-8")
    # Extract date
    date_match = re.search(r"# Market Overview \| (\d{4}-\d{2}-\d{2})", content)
    date = date_match.group(1) if date_match else "unknown"
    # Extract regime
    regime_match = re.search(r"\*\*Regime:\*\*\s*(.+?)(?:\n|$)", content)
    regime = regime_match.group(1).strip() if regime_match else "Unknown"
    # Extract action summary bullets
    lines = content.split("\n")
    summary = {}
    for line in lines:
        for key in ["Regime", "Playbook", "Focus on", "Avoid", "Key risk", "Next catalyst"]:
            if line.strip().startswith(f"- **{key}:**"):
                summary[key] = line.split(f"- **{key}:**")[1].strip()
    return {"date": date, "regime": regime, "summary": summary}


@st.cache_data(ttl=300)
def load_sector_momentum() -> list[dict]:
    try:
        result = subprocess.run(
            [str(PYTHON), str(ROOT / "scripts" / "sector-momentum.py"), "--json"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(ROOT),
        )
        # Find JSON array in output (skip any non-JSON lines)
        output = result.stdout
        start = output.find("[")
        if start >= 0:
            return json.loads(output[start:])
    except Exception:
        pass
    return []


@st.cache_data(ttl=300)
def load_accounts() -> list[dict]:
    accounts = []
    if not ACCOUNTS_DIR.exists():
        return accounts
    for f in ACCOUNTS_DIR.glob("*.md"):
        fm = parse_frontmatter(f)
        if fm.get("account_name"):
            accounts.append(fm)
    return accounts


@st.cache_data(ttl=60)
def fetch_prices(tickers: list[str]) -> dict:
    """Fetch current prices for a list of tickers via yfinance."""
    try:
        import yfinance as yf

        us_tickers = [t for t in tickers if not any(c in t for c in [".", "/", "IBDNF"])]
        if not us_tickers:
            return {}
        data = yf.download(us_tickers, period="5d", progress=False)
        prices = {}
        if len(us_tickers) == 1:
            try:
                closes = data["Close"].dropna().tolist()
                if closes:
                    prices[us_tickers[0]] = round(float(closes[-1]), 2)
            except (KeyError, IndexError):
                pass
        else:
            for t in us_tickers:
                try:
                    closes = data["Close"][t].dropna().tolist()
                    if closes:
                        prices[t] = round(float(closes[-1]), 2)
                except (KeyError, IndexError):
                    pass
        return prices
    except Exception:
        return {}


# --- Dashboard Sections ---


def render_header():
    st.markdown(
        "<h1 style='text-align: center; margin-bottom: 0;'>📊 Xiao Trading Agent</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align: center; color: gray;'>Weekly Dashboard — {datetime.now().strftime('%B %d, %Y')}</p>",
        unsafe_allow_html=True,
    )
    st.divider()


def render_market_regime(overview: dict):
    st.subheader("Market Regime")
    if not overview:
        st.warning("No market overview found. Run `/research-market` first.")
        return

    summary = overview.get("summary", {})
    days_old = (
        (datetime.now() - datetime.strptime(overview["date"], "%Y-%m-%d")).days
        if overview.get("date") and overview["date"] != "unknown"
        else 999
    )
    freshness = "🟢 Fresh" if days_old <= 7 else f"🟡 {days_old}d old"

    col1, col2 = st.columns([1, 2])
    with col1:
        regime = summary.get("Regime", "Unknown")
        # Color code regime
        if "Uptrend" in regime or "Strong" in regime:
            st.success(f"**{regime}**")
        elif "Choppy" in regime or "Range" in regime:
            st.warning(f"**{regime}**")
        else:
            st.error(f"**{regime}**")
        st.caption(f"Updated: {overview.get('date', '?')} ({freshness})")

    with col2:
        if summary.get("Focus on"):
            st.markdown(f"**Focus:** {summary['Focus on']}")
        if summary.get("Key risk"):
            st.markdown(f"**Risk:** {summary['Key risk']}")
        if summary.get("Next catalyst"):
            st.markdown(f"**Catalyst:** {summary['Next catalyst']}")
        if summary.get("Avoid"):
            st.markdown(f"**Avoid:** {summary['Avoid']}")


def render_sector_heatmap(sectors: list[dict]):
    st.subheader("Sector Momentum")
    if not sectors:
        st.warning("No sector data. Run `sector-momentum.py` first.")
        return

    df = pd.DataFrame(sectors)

    # Color by momentum classification
    color_map = {
        "Accelerating Up": "#00C853",
        "Steady Uptrend": "#69F0AE",
        "Pulling Back in Uptrend": "#FFD600",
        "Sideways": "#9E9E9E",
        "Downtrend": "#FF5252",
        "Capitulation": "#B71C1C",
    }

    fig = go.Figure()
    for _, row in df.iterrows():
        color = color_map.get(row.get("momentum", ""), "#9E9E9E")
        fig.add_trace(
            go.Bar(
                x=[row["sector"]],
                y=[row.get("roc_1m", 0)],
                marker_color=color,
                text=f"{row.get('roc_1m', 0):+.1f}%",
                textposition="outside",
                hovertemplate=(
                    f"<b>{row['sector']}</b> ({row.get('etf', '')})<br>"
                    f"1W: {row.get('roc_1w', 0):+.1f}% | 1M: {row.get('roc_1m', 0):+.1f}%<br>"
                    f"RSI: {row.get('rsi', 0):.0f} | MRS: {row.get('mansfield_rs', 0):+.1f}<br>"
                    f"Stage: {row.get('weinstein_label', '')} | {row.get('momentum', '')}"
                    "<extra></extra>"
                ),
                name=row.get("momentum", ""),
                showlegend=False,
            )
        )

    fig.update_layout(
        yaxis_title="1-Month Return (%)",
        height=350,
        margin=dict(t=30, b=30, l=50, r=20),
        yaxis=dict(zeroline=True, zerolinecolor="gray", zerolinewidth=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Momentum legend
    cols = st.columns(6)
    for i, (label, color) in enumerate(color_map.items()):
        with cols[i]:
            st.markdown(
                f"<span style='color:{color}'>●</span> {label}",
                unsafe_allow_html=True,
            )


def render_top_picks(stocks: list[dict], prices: dict):
    st.subheader("Top Picks (Conviction ≥ 7)")
    watching = [s for s in stocks if s["status"] == "watching" and s.get("conviction")]
    if not watching:
        st.info("No watching stocks with conviction scores.")
        return

    # Sort by conviction
    for s in watching:
        try:
            s["_conv"] = float(s["conviction"])
        except (ValueError, TypeError):
            s["_conv"] = 0
    watching.sort(key=lambda s: s["_conv"], reverse=True)
    top = [s for s in watching if s["_conv"] >= 7]

    if not top:
        st.info("No stocks with conviction ≥ 7.")
        return

    rows = []
    for s in top[:10]:
        ticker = s["ticker"]
        price = prices.get(ticker, "—")
        target = s.get("entry_target", "—")
        try:
            gap = f"{((float(price) / float(target)) - 1) * 100:+.1f}%" if price != "—" and target and target != "—" else "—"
        except (ValueError, TypeError):
            gap = "—"
        strategies = ", ".join(s.get("strategies", [])) if isinstance(s.get("strategies"), list) else str(s.get("strategies", ""))
        rows.append(
            {
                "Ticker": ticker,
                "Conviction": s["_conv"],
                "Sector": s.get("sector", ""),
                "Price": f"${price}" if price != "—" else "—",
                "Target": f"${target}" if target and target != "—" else "—",
                "Gap": gap,
                "Strategies": strategies,
                "Stale?": "⚠️" if s["days_stale"] > 7 else "✅",
            }
        )

    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Conviction": st.column_config.NumberColumn(format="%.1f"),
        },
    )


@st.cache_data(ttl=300)
def fetch_rsi_and_pe(tickers: list[str]) -> list[dict]:
    """Fetch RSI and Forward PE for a list of tickers directly via yfinance."""
    import yfinance as yf

    us_tickers = [t for t in tickers if not any(c in t for c in [".", "/", "IBDNF"])]
    if not us_tickers:
        return []

    results = []
    try:
        data = yf.download(us_tickers, period="1mo", progress=False)
        for ticker in us_tickers:
            try:
                if len(us_tickers) == 1:
                    closes = data["Close"].dropna().tolist()
                else:
                    closes = data["Close"][ticker].dropna().tolist()
                if len(closes) < 15:
                    continue
                # Compute RSI
                deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
                gains = [d if d > 0 else 0 for d in deltas]
                losses = [-d if d < 0 else 0 for d in deltas]
                period = 14
                avg_gain = sum(gains[:period]) / period
                avg_loss = sum(losses[:period]) / period
                for i in range(period, len(gains)):
                    avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                    avg_loss = (avg_loss * (period - 1) + losses[i]) / period
                rsi = 100 if avg_loss == 0 else round(100 - (100 / (1 + avg_gain / avg_loss)), 1)

                # Get forward PE
                info = yf.Ticker(ticker).info
                fwd_pe = info.get("forwardPE")
                price = round(float(closes[-1]), 2)
                sector = info.get("sector", "Other")

                if fwd_pe and 0 < fwd_pe < 300:
                    results.append(
                        {
                            "Ticker": ticker,
                            "RSI": rsi,
                            "FwdPE": round(float(fwd_pe), 1),
                            "Sector": sector,
                            "Price": price,
                        }
                    )
            except Exception:
                continue
    except Exception:
        pass
    return results


def render_watchlist_scatter(stocks: list[dict], prices: dict):
    st.subheader("Watchlist — RSI vs Forward P/E")

    watching = [s for s in stocks if s["status"] == "watching"]
    tickers = [s["ticker"] for s in watching]

    if not tickers:
        st.info("No watching stocks.")
        return

    with st.spinner("Fetching RSI & P/E data..."):
        scatter_data = fetch_rsi_and_pe(tickers)

    if not scatter_data:
        st.warning("Could not fetch RSI/PE data. Check network connection.")
        return

    df = pd.DataFrame(scatter_data)

    fig = px.scatter(
        df,
        x="FwdPE",
        y="RSI",
        text="Ticker",
        color="Sector",
        hover_data=["Price"],
        height=450,
    )
    fig.update_traces(textposition="top center", marker=dict(size=10))

    # Quadrant lines
    fig.add_hline(y=30, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_hline(y=70, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=25, line_dash="dash", line_color="gray", opacity=0.5)

    # Annotations
    fig.add_annotation(x=12, y=20, text="OVERSOLD + CHEAP", showarrow=False, font=dict(color="green", size=10), opacity=0.5)
    fig.add_annotation(x=80, y=80, text="OVERBOUGHT + EXPENSIVE", showarrow=False, font=dict(color="red", size=10), opacity=0.5)

    fig.update_layout(
        xaxis_title="Forward P/E",
        yaxis_title="RSI (14)",
        margin=dict(t=30, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_conviction_chart(stocks: list[dict]):
    st.subheader("Conviction Scores")

    watching = [s for s in stocks if s["status"] == "watching" and s.get("conviction")]
    if not watching:
        st.info("No conviction scores yet.")
        return

    rows = []
    for s in watching:
        try:
            conv = float(s["conviction"])
        except (ValueError, TypeError):
            continue
        rows.append({
            "Ticker": s["ticker"],
            "Conviction": conv,
            "Sector": s.get("sector", "Other"),
        })

    rows.sort(key=lambda r: r["Conviction"], reverse=True)
    df = pd.DataFrame(rows[:20])

    colors = []
    for c in df["Conviction"]:
        if c >= 8:
            colors.append("#00C853")
        elif c >= 7:
            colors.append("#69F0AE")
        elif c >= 6:
            colors.append("#FFD600")
        else:
            colors.append("#FF5252")

    fig = go.Figure(
        go.Bar(
            y=df["Ticker"],
            x=df["Conviction"],
            orientation="h",
            marker_color=colors,
            text=[f"{c:.1f}" for c in df["Conviction"]],
            textposition="inside",
            hovertemplate="<b>%{y}</b><br>Conviction: %{x:.1f}/10<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis_title="Conviction Score",
        xaxis=dict(range=[0, 10]),
        height=max(300, len(df) * 25),
        margin=dict(t=10, b=30, l=60, r=20),
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)


def render_earnings_calendar(stocks: list[dict]):
    st.subheader("Upcoming Earnings")

    watching = [s for s in stocks if s["status"] == "watching"]
    # Read earnings from stock files
    earnings = []
    for s in watching:
        f = STOCKS_DIR / f"{s['ticker']}.md"
        if not f.exists():
            continue
        content = f.read_text(encoding="utf-8")
        # Look for earnings date patterns
        patterns = [
            r"[Ee]arnings\s*(?:\*\*)?(?:date)?:?\s*(?:\*\*)?\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2}(?:,?\s*\d{4})?)",
            r"[Nn]ext\s+earnings[:\s]+(?:\*\*)?((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2}(?:,?\s*\d{4})?)",
        ]
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                date_str = match.group(1).strip("*")
                try:
                    # Try parsing
                    for fmt in ["%B %d, %Y", "%B %d", "%b %d, %Y", "%b %d"]:
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            if dt.year < 2026:
                                dt = dt.replace(year=2026)
                            days_until = (dt - datetime.now()).days
                            if -7 < days_until < 90:
                                earnings.append(
                                    {
                                        "Ticker": s["ticker"],
                                        "Date": dt.strftime("%b %d"),
                                        "Days": days_until,
                                    }
                                )
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass
                break

    if not earnings:
        st.info("No upcoming earnings found.")
        return

    earnings.sort(key=lambda e: e["Days"])

    # Bar chart
    df = pd.DataFrame(earnings[:15])
    colors = []
    for d in df["Days"]:
        if d <= 7:
            colors.append("#FF1744")
        elif d <= 14:
            colors.append("#FF9100")
        elif d <= 30:
            colors.append("#FFD600")
        else:
            colors.append("#00E676")

    fig = go.Figure(
        go.Bar(
            y=df["Ticker"],
            x=df["Days"],
            orientation="h",
            marker_color=colors,
            text=[f"{d}d — {dt}" for d, dt in zip(df["Days"], df["Date"])],
            textposition="inside",
        )
    )
    fig.update_layout(
        xaxis_title="Days Until Earnings",
        height=max(250, len(df) * 30),
        margin=dict(t=10, b=30, l=60, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_near_target(stocks: list[dict], prices: dict):
    st.subheader("Near Entry Target")

    watching = [s for s in stocks if s["status"] == "watching" and s.get("entry_target")]
    if not watching:
        st.info("No entry targets set.")
        return

    rows = []
    for s in watching:
        ticker = s["ticker"]
        price = prices.get(ticker)
        target = s.get("entry_target", "")
        if not price or not target:
            continue
        try:
            target_f = float(target)
            gap_pct = ((price / target_f) - 1) * 100
        except (ValueError, TypeError):
            continue
        # Show stocks within 10% of target (either direction)
        if -15 < gap_pct < 10:
            rows.append({
                "Ticker": ticker,
                "Price": f"${price:,.2f}",
                "Target": f"${target_f:,.2f}",
                "Gap": f"{gap_pct:+.1f}%",
                "Signal": "AT TARGET" if abs(gap_pct) < 3 else ("BELOW" if gap_pct < 0 else "Above"),
            })

    if not rows:
        st.info("No stocks near entry targets right now.")
        return

    rows.sort(key=lambda r: float(r["Gap"].strip("%+")))
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_stale_research(stocks: list[dict]):
    st.subheader("Research Freshness")

    watching = [s for s in stocks if s["status"] == "watching"]
    if not watching:
        st.info("No watching stocks.")
        return

    fresh = len([s for s in watching if s["days_stale"] <= 7])
    stale = len([s for s in watching if s["days_stale"] > 7])
    total = len(watching)

    # Progress bar
    freshness_pct = fresh / total if total > 0 else 0
    st.progress(freshness_pct, text=f"{fresh}/{total} fresh")

    if stale > 0:
        stale_list = sorted(
            [s for s in watching if s["days_stale"] > 7],
            key=lambda s: s["days_stale"],
            reverse=True,
        )
        rows = [
            {"Ticker": s["ticker"], "Days Old": s["days_stale"], "Last Update": s.get("last_update", "?")}
            for s in stale_list[:10]
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.success("All research is fresh!")


# --- Main ---
def main():
    render_header()

    # Load data
    stocks = load_all_stocks()
    overview = load_market_overview()
    sectors = load_sector_momentum()

    # Get prices for watchlist
    watching_tickers = [s["ticker"] for s in stocks if s["status"] == "watching"]
    prices = fetch_prices(watching_tickers) if watching_tickers else {}

    # --- Row 1: Market Regime + Sector Momentum ---
    col1, col2 = st.columns([1, 2])
    with col1:
        render_market_regime(overview)
    with col2:
        render_sector_heatmap(sectors)

    st.divider()

    # --- Row 2: Top Picks ---
    render_top_picks(stocks, prices)

    st.divider()

    # --- Row 3: Scatter + Conviction ---
    col1, col2 = st.columns(2)
    with col1:
        render_watchlist_scatter(stocks, prices)
    with col2:
        render_conviction_chart(stocks)

    st.divider()

    # --- Row 4: Earnings + Near Target + Freshness ---
    col1, col2, col3 = st.columns(3)
    with col1:
        render_earnings_calendar(stocks)
    with col2:
        render_near_target(stocks, prices)
    with col3:
        render_stale_research(stocks)


if __name__ == "__main__":
    main()
