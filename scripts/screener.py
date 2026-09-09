#!/usr/bin/env python3
"""
screener.py — Composite stock screener for watchlist triage.

Scores and ranks all watchlist stocks by a weighted composite metric combining:
RSI positioning, PEG (valuation vs growth), gap-to-target, conviction,
sector momentum, and research staleness.

Usage:
    # Piped from watchlist.py (no extra network calls):
    .venv/bin/python3 scripts/watchlist.py --json --no-save | .venv/bin/python3 scripts/screener.py

    # Standalone (re-runs watchlist internally):
    .venv/bin/python3 scripts/screener.py

    # Filters:
    .venv/bin/python3 scripts/screener.py --held           # only held positions
    .venv/bin/python3 scripts/screener.py --top 10         # top 10 only
    .venv/bin/python3 scripts/screener.py --min-score 60   # only scores >= 60
    .venv/bin/python3 scripts/screener.py --json           # JSON output
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime


# ---------------------------------------------------------------------------
# ANSI color helpers
# ---------------------------------------------------------------------------
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
DIM = "\033[2m"

BOLD_GREEN = "\033[1;32m"
BOLD_YELLOW = "\033[1;33m"
BOLD_RED = "\033[1;31m"
BOLD_CYAN = "\033[1;36m"
BOLD_WHITE = "\033[1;37m"


def supports_color() -> bool:
    """Check if stdout supports ANSI color codes."""
    if not hasattr(sys.stdout, "isatty"):
        return False
    return sys.stdout.isatty()


USE_COLOR = supports_color()


def c(text: str, code: str) -> str:
    """Wrap text in ANSI color if terminal supports it."""
    if USE_COLOR:
        return f"{code}{text}{RESET}"
    return text


# ---------------------------------------------------------------------------
# Refresh cadence (mirrors watchlist.py)
# ---------------------------------------------------------------------------
REFRESH_CADENCE = {
    "high": 14,    # conviction 8+
    "medium": 28,  # conviction 6-7.9
    "low": 42,     # conviction < 6
}


def get_cadence(conviction: float | None) -> int:
    if conviction is not None and conviction >= 8:
        return REFRESH_CADENCE["high"]
    elif conviction is not None and conviction >= 6:
        return REFRESH_CADENCE["medium"]
    return REFRESH_CADENCE["low"]


# ---------------------------------------------------------------------------
# Scoring functions (each returns 0..max_points)
# ---------------------------------------------------------------------------

def score_rsi(rsi: float | None) -> int:
    """RSI positioning: oversold = opportunity, overbought = avoid. Max 20."""
    if rsi is None:
        return 10  # neutral if unavailable
    if rsi < 30:
        return 20
    elif rsi < 40:
        return 15
    elif rsi < 60:
        return 10
    elif rsi < 70:
        return 5
    return 0


def score_peg(fwd_pe: float | None, trailing_pe: float | None = None,
              revenue_growth: float | None = None) -> int:
    """Valuation vs growth (PEG proxy). Max 20.

    PEG = fwd_pe / (growth_rate * 100).
    Growth sources (in priority order):
      1. revenue_growth from yfinance (decimal, e.g. 0.25 = 25%)
      2. Implied from fwd_pe vs trailing_pe ratio
      3. Neutral score if neither available
    """
    if fwd_pe is None or fwd_pe <= 0:
        return 10  # neutral

    growth_pct = None

    if revenue_growth is not None and revenue_growth > 0:
        growth_pct = revenue_growth * 100
    elif trailing_pe is not None and trailing_pe > 0 and fwd_pe > 0:
        # If fwd PE < trailing PE, implies earnings growth
        # growth ≈ (trailing / forward - 1) * 100
        implied = (trailing_pe / fwd_pe - 1) * 100
        if implied > 0:
            growth_pct = implied

    if growth_pct is None or growth_pct <= 0:
        return 10  # neutral

    peg = fwd_pe / growth_pct

    if peg < 0.5:
        return 20
    elif peg < 1.0:
        return 15
    elif peg < 1.5:
        return 10
    elif peg < 2.0:
        return 5
    return 0


def score_gap(gap_pct: float | None) -> int:
    """Gap to entry target: below target = opportunity. Max 20."""
    if gap_pct is None:
        return 8  # neutral-ish
    if gap_pct < -20:
        return 20
    elif gap_pct < -10:
        return 15
    elif gap_pct < 0:
        return 12
    elif gap_pct < 10:
        return 8
    elif gap_pct < 20:
        return 4
    return 0


def score_conviction(conviction: float | None) -> int:
    """Conviction score. Max 20."""
    if conviction is None:
        return 0
    if conviction >= 9:
        return 20
    elif conviction >= 8:
        return 16
    elif conviction >= 7:
        return 12
    elif conviction >= 6:
        return 8
    elif conviction >= 5:
        return 4
    return 0


def score_sector_momentum(momentum: str | None) -> int:
    """Sector momentum classification. Max 10."""
    if momentum is None:
        return 5  # neutral
    mapping = {
        "Accelerating Up": 10,
        "Steady Uptrend": 8,
        "Pulling Back in Uptrend": 8,
        "Pulling Back": 8,
        "Sideways": 5,
        "Mixed": 5,
        "Downtrend": 2,
        "Stage 4 (Declining)": 0,
        "Capitulation": 0,
    }
    return mapping.get(momentum, 5)


def score_staleness(stale_days: int | None, conviction: float | None) -> int:
    """Staleness bonus: staler = more urgent to refresh. Max 10."""
    if stale_days is None or stale_days >= 999:
        return 5  # unknown
    cadence = get_cadence(conviction)
    days_over = stale_days - cadence
    if days_over <= 0:
        return 0  # fresh
    elif days_over < 7:
        return 2
    elif days_over < 14:
        return 4
    elif days_over < 30:
        return 7
    return 10


# ---------------------------------------------------------------------------
# Composite scoring
# ---------------------------------------------------------------------------

def compute_composite(stock: dict) -> dict:
    """Compute composite score (0-100) with component breakdown."""
    rsi = stock.get("rsi")
    fwd_pe = stock.get("fwd_pe")
    gap_pct = stock.get("gap_pct")
    conviction = stock.get("conviction")
    momentum = stock.get("sector_momentum")
    stale_days = stock.get("stale_days", 0)

    # Component scores
    s_rsi = score_rsi(rsi)
    s_peg = score_peg(fwd_pe)
    s_gap = score_gap(gap_pct)
    s_conv = score_conviction(conviction)
    s_mom = score_sector_momentum(momentum)
    s_stale = score_staleness(stale_days, conviction)

    total = s_rsi + s_peg + s_gap + s_conv + s_mom + s_stale

    # Derive PEG for display
    peg = None
    if fwd_pe and fwd_pe > 0:
        # Try to estimate growth from thesis patterns or just show fwd_pe
        # For display only; scoring already handled
        pass

    # Verdict
    if total >= 75:
        verdict = "STRONG BUY"
    elif total >= 60:
        verdict = "BUY"
    elif total >= 45:
        verdict = "HOLD"
    elif total >= 30:
        verdict = "WATCH"
    else:
        verdict = "AVOID"

    return {
        "ticker": stock.get("ticker", "???"),
        "score": total,
        "components": {
            "rsi": s_rsi,
            "peg": s_peg,
            "gap": s_gap,
            "conviction": s_conv,
            "sector_momentum": s_mom,
            "staleness": s_stale,
        },
        "verdict": verdict,
        # Pass through useful display data
        "rsi": rsi,
        "fwd_pe": fwd_pe,
        "gap_pct": gap_pct,
        "conviction_raw": conviction,
        "sector": stock.get("sector", ""),
        "sector_momentum": momentum,
        "tier": stock.get("tier", ""),
        "held_in": stock.get("held_in", []),
        "total_held_value": stock.get("total_held_value", 0),
        "price": stock.get("price"),
        "entry_target": stock.get("entry_target"),
        "stale_days": stale_days,
        "earnings_days": stock.get("earnings_days"),
        "thesis": stock.get("thesis", ""),
    }


# ---------------------------------------------------------------------------
# Input: read watchlist JSON
# ---------------------------------------------------------------------------

def read_watchlist_json() -> list[dict]:
    """Read watchlist JSON from stdin or by running watchlist.py internally."""
    # Check if stdin has data (piped)
    if not sys.stdin.isatty():
        try:
            return json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error reading piped JSON: {e}", file=sys.stderr)
            sys.exit(1)

    # Run watchlist.py internally
    print("Running watchlist.py --json --no-save ...", file=sys.stderr)
    try:
        result = subprocess.run(
            [sys.executable, "scripts/watchlist.py", "--json", "--no-save"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            print(f"watchlist.py failed: {result.stderr[:500]}", file=sys.stderr)
            sys.exit(1)
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        print("watchlist.py timed out", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing watchlist.py output: {e}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Output: terminal table
# ---------------------------------------------------------------------------

def verdict_colored(verdict: str) -> str:
    """Color-code verdict for terminal display."""
    if verdict == "STRONG BUY":
        return c("STRONG BUY", BOLD_GREEN)
    elif verdict == "BUY":
        return c("BUY       ", GREEN)
    elif verdict == "HOLD":
        return c("HOLD      ", YELLOW)
    elif verdict == "WATCH":
        return c("WATCH     ", DIM)
    elif verdict == "AVOID":
        return c("AVOID     ", BOLD_RED)
    return verdict


def rsi_str(rsi: float | None) -> str:
    if rsi is None:
        return "  --"
    val = f"{rsi:4.0f}"
    if rsi < 30:
        return c(val, GREEN)
    elif rsi > 70:
        return c(val, RED)
    return val


def gap_str(gap_pct: float | None) -> str:
    if gap_pct is None:
        return "     --"
    s = f"{gap_pct:+6.1f}%"
    if gap_pct < -10:
        return c(s, GREEN)
    elif gap_pct > 20:
        return c(s, RED)
    return s


def pe_str(fwd_pe: float | None) -> str:
    if fwd_pe is None:
        return "    --"
    if fwd_pe > 999:
        return f"  999+"
    return f"{fwd_pe:6.1f}"


def print_screener(scored: list[dict]):
    """Print ranked screener table to terminal."""
    today = datetime.now().strftime("%Y-%m-%d")
    width = 105

    print()
    print(c("=" * width, BOLD))
    print(c(f"  SCREENER — {today}", BOLD_WHITE))
    print(c("=" * width, BOLD))
    print()

    # Header
    hdr = (
        f"  {'Rank':>4s}  {'Ticker':<6s}  {'Score':>5s}  "
        f"{'RSI':>4s}  {'FwdPE':>6s}  {'Gap%':>7s}  "
        f"{'Conv':>4s}  {'Sector Mom':<20s}  {'Verdict':<10s}"
    )
    print(c(hdr, DIM))
    print(c(
        f"  {'----':>4s}  {'------':<6s}  {'-----':>5s}  "
        f"{'---':>4s}  {'-----':>6s}  {'-----':>7s}  "
        f"{'----':>4s}  {'----------':<20s}  {'-------':<10s}", DIM
    ))

    for i, s in enumerate(scored, 1):
        conv = f"{s['conviction_raw']:.1f}" if s['conviction_raw'] else "  --"
        mom = s.get("sector_momentum") or "--"
        if len(mom) > 20:
            mom = mom[:18] + ".."

        # Score color
        score_val = s["score"]
        if score_val >= 75:
            score_s = c(f"{score_val:5d}", BOLD_GREEN)
        elif score_val >= 60:
            score_s = c(f"{score_val:5d}", GREEN)
        elif score_val >= 45:
            score_s = c(f"{score_val:5d}", YELLOW)
        elif score_val >= 30:
            score_s = f"{score_val:5d}"
        else:
            score_s = c(f"{score_val:5d}", RED)

        line = (
            f"  {i:4d}  {s['ticker']:<6s}  {score_s}  "
            f"{rsi_str(s['rsi'])}  {pe_str(s['fwd_pe'])}  {gap_str(s['gap_pct'])}  "
            f"{conv:>4s}  {mom:<20s}  {verdict_colored(s['verdict'])}"
        )
        print(line)

    print()
    print(c(
        f"  Verdicts: >=75 STRONG BUY | 60-74 BUY | 45-59 HOLD | 30-44 WATCH | <30 AVOID",
        DIM,
    ))
    print(c("=" * width, BOLD))
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Composite stock screener — scores and ranks watchlist stocks"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--held", action="store_true", help="Only show held positions")
    parser.add_argument("--top", type=int, default=None, help="Show top N only")
    parser.add_argument("--min-score", type=int, default=None, help="Minimum score threshold")
    args = parser.parse_args()

    # Read input
    stocks = read_watchlist_json()

    if not stocks:
        print("No watchlist data found.", file=sys.stderr)
        sys.exit(1)

    # Score all stocks
    scored = [compute_composite(s) for s in stocks]

    # Sort by score descending, then by ticker for ties
    scored.sort(key=lambda s: (-s["score"], s["ticker"]))

    # Apply filters
    if args.held:
        scored = [s for s in scored if s.get("held_in")]

    if args.min_score is not None:
        scored = [s for s in scored if s["score"] >= args.min_score]

    if args.top is not None:
        scored = scored[:args.top]

    if not scored:
        print("No stocks match the given filters.", file=sys.stderr)
        sys.exit(0)

    # Output
    if args.json:
        print(json.dumps(scored, indent=2))
    else:
        print_screener(scored)


if __name__ == "__main__":
    main()
