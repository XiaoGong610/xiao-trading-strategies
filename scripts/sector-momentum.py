#!/usr/bin/env python3
"""
sector-momentum.py — Quantitative sector momentum analysis.

Computes sector momentum using three proven frameworks:
1. Relative Strength vs. S&P 500 (Mansfield-style)
2. Rate of Change (ROC) with trend direction
3. Weinstein Stage Analysis (price vs. 30-week SMA)

Usage:
    python3 scripts/sector-momentum.py              # terminal dashboard
    python3 scripts/sector-momentum.py --json        # JSON output
    python3 scripts/sector-momentum.py --sector XLK  # single sector deep-dive

Sources:
- Mansfield Relative Strength: stageanalysis.net
- Weinstein Stage Analysis: "Secrets for Profiting in Bull and Bear Markets"
- ROC momentum: standard technical analysis
"""

import argparse
import json
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import yfinance as yf

# GICS sector ETFs
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

BENCHMARK = "SPY"


def fetch_data(tickers: list[str], period: str = "1y") -> dict[str, pd.DataFrame]:
    """Fetch historical price data for all tickers."""
    all_tickers = tickers + [BENCHMARK]
    data = yf.download(all_tickers, period=period, progress=False, group_by="ticker")

    result = {}
    for ticker in all_tickers:
        try:
            if len(all_tickers) == 1:
                df = data
            else:
                df = data[ticker]
            if not df.empty:
                result[ticker] = df
        except (KeyError, TypeError):
            continue
    return result


def calculate_rsi(series: pd.Series, window: int = 14) -> float:
    """Calculate current RSI."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return round(float(rsi.iloc[-1]), 1) if not rsi.empty else 0


def calculate_roc(series: pd.Series, window: int) -> float:
    """Calculate Rate of Change over window days."""
    if len(series) < window + 1:
        return 0.0
    current = series.iloc[-1]
    past = series.iloc[-window - 1]
    if past == 0:
        return 0.0
    return round(((current - past) / past) * 100, 2)


def calculate_mansfield_rs(sector_close: pd.Series, benchmark_close: pd.Series,
                           window: int = 200) -> float:
    """
    Calculate Mansfield Relative Strength.
    MRS = ((RP / SMA(RP, n)) - 1) * 100
    where RP = sector_close / benchmark_close
    Positive = outperforming benchmark, Negative = underperforming
    """
    if len(sector_close) < window or len(benchmark_close) < window:
        return 0.0

    # Align indices
    common_idx = sector_close.index.intersection(benchmark_close.index)
    sector = sector_close.loc[common_idx]
    bench = benchmark_close.loc[common_idx]

    rp = sector / bench
    sma_rp = rp.rolling(window=window).mean()

    if sma_rp.iloc[-1] == 0 or pd.isna(sma_rp.iloc[-1]):
        return 0.0

    mrs = ((rp.iloc[-1] / sma_rp.iloc[-1]) - 1) * 100
    return round(float(mrs), 2)


def classify_weinstein_stage(close: pd.Series) -> tuple[int, str]:
    """
    Classify into Weinstein stages using 150-day SMA (≈30 weeks).
    Returns (stage_number, stage_name).
    """
    if len(close) < 150:
        return 0, "Unknown"

    sma_150 = close.rolling(150).mean()
    current_price = close.iloc[-1]
    current_sma = sma_150.iloc[-1]
    prev_sma_20d = sma_150.iloc[-20] if len(sma_150) > 20 else current_sma

    # SMA slope (is it rising, flat, or falling?)
    sma_slope = (current_sma - prev_sma_20d) / prev_sma_20d * 100

    price_vs_sma = ((current_price / current_sma) - 1) * 100

    if abs(sma_slope) < 0.5:  # SMA is flat
        if abs(price_vs_sma) < 5:
            return 1, "Stage 1 (Basing)"      # Price near flat SMA = accumulation
        elif price_vs_sma > 5:
            return 3, "Stage 3 (Distribution)"  # Price above flattening SMA after run
        else:
            return 1, "Stage 1 (Basing)"
    elif sma_slope > 0.5:  # SMA rising
        if price_vs_sma > 0:
            return 2, "Stage 2 (Advancing)"    # Price above rising SMA = uptrend
        else:
            return 3, "Stage 3 (Distribution)"  # Price below rising SMA = weakening
    else:  # SMA falling
        if price_vs_sma < 0:
            return 4, "Stage 4 (Declining)"    # Price below falling SMA = downtrend
        else:
            return 1, "Stage 1 (Basing)"       # Price above falling SMA = potential base


def classify_momentum(roc_1w: float, roc_1m: float, mansfield_rs: float,
                      rsi: float) -> tuple[str, str]:
    """
    Classify sector momentum into actionable categories.
    Returns (classification, strategy_implication).
    """
    if roc_1w < -3 and roc_1m < -5 and rsi < 30:
        return "Capitulation", "Contrarian buy zone — aggressive accumulation if thesis intact"

    if roc_1w < 0 and roc_1m < 0 and mansfield_rs < -2:
        return "Downtrend", "Slow DCA only — accumulate for the turn, save cash"

    if abs(roc_1w) < 1 and abs(roc_1m) < 2:
        return "Sideways", "Theta gang — sell premium, no directional bets"

    if roc_1w < 0 and roc_1m > 0:
        return "Pulling Back in Uptrend", "Best entry window — buy the dip, accelerate DCA"

    if roc_1w > 0 and roc_1m > 0 and mansfield_rs > 2:
        return "Accelerating Up", "Buy strength — momentum entries work, don't wait for pullback"

    if roc_1w > 0 and roc_1m > 0:
        return "Steady Uptrend", "Normal DCA — buy support tests, standard sizing"

    return "Mixed", "Assess individually — no clear sector signal"


def analyze_sector(sector: str, etf: str, data: dict[str, pd.DataFrame]) -> dict | None:
    """Analyze a single sector's momentum."""
    if etf not in data or BENCHMARK not in data:
        return None

    sector_df = data[etf]
    bench_df = data[BENCHMARK]
    close = sector_df["Close"].dropna()
    bench_close = bench_df["Close"].dropna()

    if len(close) < 200:
        return None

    # Current price
    price = round(float(close.iloc[-1]), 2)

    # Rate of Change
    roc_1w = calculate_roc(close, 5)
    roc_1m = calculate_roc(close, 21)
    roc_3m = calculate_roc(close, 63)

    # RSI
    rsi = calculate_rsi(close)

    # Mansfield Relative Strength vs S&P 500
    mrs = calculate_mansfield_rs(close, bench_close, window=200)

    # Weinstein Stage
    stage_num, stage_name = classify_weinstein_stage(close)

    # Moving averages
    sma_50 = round(float(close.rolling(50).mean().iloc[-1]), 2)
    sma_150 = round(float(close.rolling(150).mean().iloc[-1]), 2)
    sma_200 = round(float(close.rolling(200).mean().iloc[-1]), 2)

    # Momentum classification
    momentum, strategy = classify_momentum(roc_1w, roc_1m, mrs, rsi)

    return {
        "sector": sector,
        "etf": etf,
        "price": price,
        "roc_1w": roc_1w,
        "roc_1m": roc_1m,
        "roc_3m": roc_3m,
        "rsi": rsi,
        "mansfield_rs": mrs,
        "weinstein_stage": stage_num,
        "weinstein_label": stage_name,
        "sma_50": sma_50,
        "sma_150": sma_150,
        "sma_200": sma_200,
        "momentum": momentum,
        "strategy": strategy,
    }


def format_dashboard(results: list[dict]) -> str:
    """Format results into a terminal dashboard."""
    lines = []
    lines.append("=" * 100)
    lines.append(f"  SECTOR MOMENTUM DASHBOARD — {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("=" * 100)
    lines.append("")

    # Sort by Mansfield RS (strongest outperformers first)
    results.sort(key=lambda x: x["mansfield_rs"], reverse=True)

    # Header
    lines.append(f"  {'Sector':<18s} {'ETF':>4s} {'1W':>7s} {'1M':>7s} {'3M':>7s}"
                 f" {'RSI':>5s} {'MRS':>6s} {'Stage':>22s} {'Momentum':<25s}")
    lines.append("  " + "-" * 96)

    for r in results:
        # Color indicators
        mrs_indicator = "+" if r["mansfield_rs"] > 0 else "-"
        rsi_flag = " OB" if r["rsi"] > 70 else (" OS" if r["rsi"] < 30 else "   ")

        lines.append(
            f"  {r['sector']:<18s} {r['etf']:>4s}"
            f" {r['roc_1w']:>+6.1f}% {r['roc_1m']:>+6.1f}% {r['roc_3m']:>+6.1f}%"
            f" {r['rsi']:>4.0f}{rsi_flag}"
            f" {r['mansfield_rs']:>+5.1f}"
            f" {r['weinstein_label']:>22s}"
            f" {r['momentum']:<25s}"
        )

    lines.append("")
    lines.append("  " + "-" * 96)
    lines.append("  LEGEND:")
    lines.append("    1W/1M/3M = Rate of Change (%) | RSI = 14-day | MRS = Mansfield Relative Strength vs S&P 500")
    lines.append("    OB = Overbought (>70) | OS = Oversold (<30) | Stage = Weinstein (1=Base, 2=Advance, 3=Dist, 4=Decline)")
    lines.append("")

    # Strategy summary
    lines.append("  STRATEGY PLAYBOOK:")
    lines.append("  " + "-" * 96)
    for r in results:
        lines.append(f"    {r['sector']:<18s} [{r['momentum']}] → {r['strategy']}")

    lines.append("")
    lines.append("=" * 100)
    lines.append(f"  Methodology: Mansfield RS (vs SPY, 200-day), Weinstein Stage (150-day SMA), ROC momentum")
    lines.append("=" * 100)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Sector momentum analysis")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--sector", type=str, help="Single sector ETF (e.g., XLK)")
    args = parser.parse_args()

    # Determine which sectors to analyze
    if args.sector:
        # Find sector name from ETF ticker
        sector_name = None
        for name, etf in SECTOR_ETFS.items():
            if etf == args.sector.upper():
                sector_name = name
                break
        if not sector_name:
            print(f"Unknown sector ETF: {args.sector}. Available: {', '.join(SECTOR_ETFS.values())}")
            sys.exit(1)
        tickers = [args.sector.upper()]
        sectors_to_analyze = {sector_name: args.sector.upper()}
    else:
        tickers = list(SECTOR_ETFS.values())
        sectors_to_analyze = SECTOR_ETFS

    # Fetch data
    print("Fetching sector data (1 year)...", file=sys.stderr)
    data = fetch_data(tickers, period="1y")

    # Analyze each sector
    results = []
    for sector, etf in sectors_to_analyze.items():
        result = analyze_sector(sector, etf, data)
        if result:
            results.append(result)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_dashboard(results))


if __name__ == "__main__":
    main()
