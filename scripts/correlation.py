#!/usr/bin/env python3
"""
correlation.py — Cross-position correlation analysis for portfolio risk.

Identifies correlated positions that compound concentration risk.
Uses yfinance 6-month daily returns and pairwise Pearson correlation.

Usage:
    .venv/bin/python3 scripts/correlation.py                    # all held positions
    .venv/bin/python3 scripts/correlation.py --top 15           # top 15 by position size
    .venv/bin/python3 scripts/correlation.py --threshold 0.70   # only show pairs above threshold
    .venv/bin/python3 scripts/correlation.py --json             # JSON output
    .venv/bin/python3 scripts/watchlist.py --json --no-save | .venv/bin/python3 scripts/correlation.py
"""

import argparse
import json
import re
import sys
from datetime import datetime
from itertools import combinations
from pathlib import Path

import pandas as pd
import yfinance as yf

ACCOUNTS_DIR = Path("portfolio/accounts")

# Leveraged ETF mappings — note relationship in output
LEVERAGED_MAP = {
    "TSLL": ("TSLA", "2x"),
    "CONL": ("COIN", "2x"),
}

# ANSI colors
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# Correlation thresholds
EXTREME_THRESHOLD = 0.85
HIGH_THRESHOLD = 0.70
MODERATE_THRESHOLD = 0.50

# Cluster detection threshold
CLUSTER_THRESHOLD = 0.65


# ---------------------------------------------------------------------------
# Portfolio parsing (reuses logic from watchlist.py)
# ---------------------------------------------------------------------------

def _parse_number(s: str) -> float | None:
    try:
        return float(s.strip().replace(',', '').replace('~', ''))
    except (ValueError, AttributeError):
        return None


def _parse_dollar(s: str) -> float | None:
    if '$' not in str(s):
        return None
    try:
        return float(str(s).strip().replace('$', '').replace(',', '').replace('~', '').strip())
    except (ValueError, AttributeError):
        return None


def _parse_pct(s: str) -> float | None:
    m = re.search(r'([\d.]+)%', str(s))
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return None


def parse_frontmatter(filepath: Path) -> dict:
    content = filepath.read_text(encoding="utf-8")
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).strip().split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            fm[key] = value
    return fm


def parse_portfolio_holdings() -> dict[str, dict]:
    """Parse all portfolio account files and extract holdings.

    Returns: {TICKER: {accounts: [...], total_value: float, sector: str}}
    """
    if not ACCOUNTS_DIR.exists():
        return {}

    holdings: dict[str, dict] = {}

    for filepath in ACCOUNTS_DIR.glob("*.md"):
        content = filepath.read_text(encoding="utf-8")
        fm = parse_frontmatter(filepath)
        account = fm.get('account_name', filepath.stem.upper())

        in_sold = False

        for line in content.split('\n'):
            if re.match(r'^#{1,4}\s+', line):
                in_sold = bool(re.search(r'[Ss]old', line))

                # Parse headers like "### AMZN — 801 shares ($219,858 — 97.26%)"
                hdr = re.match(
                    r'^#{1,4}\s+([A-Z]{1,5})\s+[—–-]\s+([\d,.]+)\s+shares?\s*\(\$([\d,.]+)',
                    line,
                )
                if hdr and not in_sold:
                    ticker = hdr.group(1)
                    value = float(hdr.group(3).replace(',', ''))
                    if ticker not in holdings:
                        holdings[ticker] = {'accounts': [], 'total_value': 0}
                    holdings[ticker]['accounts'].append(account)
                    holdings[ticker]['total_value'] += value
                continue

            if in_sold:
                continue

            if not line.startswith('|') or '---' in line:
                continue

            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) < 3:
                continue

            first = cells[0].strip('*').strip()

            if first.lower() in ('ticker', 'option', 'strike', 'trade',
                                  'acquired', '#', 'detail'):
                continue

            if re.match(r'^[A-Z]{1,5}$', first):
                ticker = first
                value = _parse_dollar(cells[3]) if len(cells) > 3 else None
                if value is None:
                    # Try other columns — some tables have different layouts
                    for i in range(2, min(len(cells), 6)):
                        value = _parse_dollar(cells[i])
                        if value is not None:
                            break
                if ticker not in holdings:
                    holdings[ticker] = {'accounts': [], 'total_value': 0}
                if account not in holdings[ticker]['accounts']:
                    holdings[ticker]['accounts'].append(account)
                    holdings[ticker]['total_value'] += (value or 0)

    return holdings


def get_holdings_from_stdin_raw(raw: str) -> dict[str, dict]:
    """Parse piped watchlist JSON from raw string."""
    data = json.loads(raw)
    holdings = {}
    for entry in data:
        held_in = entry.get('held_in', [])
        if not held_in:
            continue
        ticker = entry['ticker']
        total_value = entry.get('total_held_value', 0)
        accounts = [h.get('account', '?') for h in held_in]
        sector = entry.get('sector', '')
        holdings[ticker] = {
            'accounts': accounts,
            'total_value': total_value,
            'sector': sector,
        }
    return holdings


# ---------------------------------------------------------------------------
# Correlation engine
# ---------------------------------------------------------------------------

def fetch_returns(tickers: list[str], period: str = "6mo") -> pd.DataFrame:
    """Fetch daily returns for all tickers. Returns DataFrame of pct changes."""
    if not tickers:
        return pd.DataFrame()

    print(f"Fetching 6-month price history for {len(tickers)} tickers...", file=sys.stderr)
    data = yf.download(tickers, period=period, progress=False, group_by="ticker")

    returns = {}
    for ticker in tickers:
        try:
            if len(tickers) == 1:
                close = data['Close']
            else:
                close = data[ticker]['Close']
            close = close.dropna()
            if len(close) > 10:
                returns[ticker] = close.pct_change().dropna()
            else:
                print(f"  Skipping {ticker}: insufficient data ({len(close)} days)",
                      file=sys.stderr)
        except (KeyError, TypeError):
            print(f"  Skipping {ticker}: no data available", file=sys.stderr)

    if not returns:
        return pd.DataFrame()

    df = pd.DataFrame(returns)
    return df


def calculate_correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Calculate pairwise Pearson correlation matrix."""
    return returns.corr(method='pearson')


def get_correlated_pairs(corr_matrix: pd.DataFrame,
                         threshold: float = 0.0) -> list[dict]:
    """Extract all unique pairs with their correlation, sorted descending."""
    pairs = []
    tickers = corr_matrix.columns.tolist()
    for i, t1 in enumerate(tickers):
        for j, t2 in enumerate(tickers):
            if i >= j:
                continue
            corr = corr_matrix.loc[t1, t2]
            if pd.isna(corr):
                continue
            pairs.append({
                'ticker1': t1,
                'ticker2': t2,
                'correlation': round(corr, 4),
            })

    pairs.sort(key=lambda p: -abs(p['correlation']))
    if threshold > 0:
        pairs = [p for p in pairs if abs(p['correlation']) >= threshold]
    return pairs


def classify_correlation(corr: float) -> tuple[str, str]:
    """Return (label, color) for a correlation value."""
    abs_corr = abs(corr)
    if abs_corr >= EXTREME_THRESHOLD:
        return "EXTREME", RED
    elif abs_corr >= HIGH_THRESHOLD:
        return "HIGH", YELLOW
    elif abs_corr >= MODERATE_THRESHOLD:
        return "MODERATE", DIM
    else:
        return "LOW", GREEN


def leveraged_note(t1: str, t2: str) -> str:
    """Return a note if one ticker is a leveraged version of the other."""
    for lev, (underlying, mult) in LEVERAGED_MAP.items():
        if (t1 == lev and t2 == underlying) or (t2 == lev and t1 == underlying):
            return f"{lev} is {mult} leveraged {underlying}"
    return ""


# ---------------------------------------------------------------------------
# Cluster detection
# ---------------------------------------------------------------------------

def detect_clusters(corr_matrix: pd.DataFrame,
                    threshold: float = CLUSTER_THRESHOLD) -> list[dict]:
    """Find groups of tickers with high average intra-group correlation.

    Uses simple agglomerative approach: start with highest-correlated pair,
    grow cluster by adding tickers that have avg correlation > threshold
    with all existing members.
    """
    tickers = corr_matrix.columns.tolist()
    if len(tickers) < 2:
        return []

    used = set()
    clusters = []

    # Get all pairs sorted by correlation
    pairs = []
    for i, t1 in enumerate(tickers):
        for j, t2 in enumerate(tickers):
            if i >= j:
                continue
            corr = corr_matrix.loc[t1, t2]
            if not pd.isna(corr) and corr >= threshold:
                pairs.append((t1, t2, corr))
    pairs.sort(key=lambda x: -x[2])

    for t1, t2, corr in pairs:
        if t1 in used and t2 in used:
            continue

        # Seed a cluster
        cluster = set()
        if t1 not in used:
            cluster.add(t1)
        if t2 not in used:
            cluster.add(t2)
        # If one is already used, skip (don't split clusters)
        if len(cluster) < 2:
            continue

        # Try to grow the cluster
        for candidate in tickers:
            if candidate in used or candidate in cluster:
                continue
            # Check avg correlation with all current members
            corrs_with = [corr_matrix.loc[candidate, m]
                          for m in cluster
                          if not pd.isna(corr_matrix.loc[candidate, m])]
            if corrs_with and sum(corrs_with) / len(corrs_with) >= threshold:
                cluster.add(candidate)

        # Calculate average intra-cluster correlation
        members = sorted(cluster)
        intra_corrs = []
        for i, m1 in enumerate(members):
            for j, m2 in enumerate(members):
                if i >= j:
                    continue
                c = corr_matrix.loc[m1, m2]
                if not pd.isna(c):
                    intra_corrs.append(c)

        if intra_corrs:
            avg_corr = sum(intra_corrs) / len(intra_corrs)
            clusters.append({
                'members': members,
                'avg_correlation': round(avg_corr, 2),
            })
            used.update(cluster)

    # Sort by avg correlation descending
    clusters.sort(key=lambda c: -c['avg_correlation'])
    return clusters


def label_cluster(members: list[str], holdings: dict) -> str:
    """Try to auto-label a cluster based on known sector/theme patterns."""
    member_set = set(members)

    # Known groupings
    labels = {
        frozenset({"TSLA", "TSLL"}): "TSLA Exposure",
        frozenset({"COIN", "CONL"}): "Crypto",
    }

    for known, label in labels.items():
        if known.issubset(member_set):
            return label

    # Check if members share sectors
    sectors = set()
    for m in members:
        h = holdings.get(m, {})
        s = h.get('sector', '')
        if s:
            sectors.add(s)

    if len(sectors) == 1:
        return list(sectors)[0]

    # Check for common themes
    ai_semi = {"NVDA", "AMD", "MU", "AVGO", "MRVL", "SMTC", "LITE", "AXTI",
               "MPWR", "SNDK", "AEHR", "TSM", "ASML", "LRCX", "KLAC", "AMAT"}
    crypto = {"COIN", "CRCL", "MSTR", "CONL", "MARA", "RIOT", "BITF"}
    software = {"NOW", "DDOG", "META", "GOOG", "APP", "IGV", "U"}

    overlap_ai = member_set & ai_semi
    overlap_crypto = member_set & crypto
    overlap_sw = member_set & software

    if len(overlap_ai) >= 2 and len(overlap_ai) / len(member_set) >= 0.5:
        return "AI Semis"
    if len(overlap_crypto) >= 2 and len(overlap_crypto) / len(member_set) >= 0.5:
        return "Crypto"
    if len(overlap_sw) >= 2 and len(overlap_sw) / len(member_set) >= 0.5:
        return "Software"

    return "Correlated Group"


# ---------------------------------------------------------------------------
# Portfolio metrics
# ---------------------------------------------------------------------------

def portfolio_metrics(corr_matrix: pd.DataFrame,
                      holdings: dict) -> dict:
    """Calculate portfolio-level diversification metrics."""
    tickers = corr_matrix.columns.tolist()
    n = len(tickers)

    if n < 2:
        return {
            'n_positions': n,
            'avg_correlation': 0,
            'effective_positions': n,
            'verdict': 'N/A (need at least 2 positions)',
        }

    # Average pairwise correlation (upper triangle only)
    corr_vals = []
    for i in range(n):
        for j in range(i + 1, n):
            c = corr_matrix.iloc[i, j]
            if not pd.isna(c):
                corr_vals.append(c)

    avg_corr = sum(corr_vals) / len(corr_vals) if corr_vals else 0

    # Effective number of independent positions
    # Formula: N / (1 + (N-1) * avg_corr) — from portfolio theory
    if avg_corr > 0:
        effective = n / (1 + (n - 1) * avg_corr)
    else:
        effective = n

    # Verdict
    if avg_corr >= 0.65:
        verdict = "POOR diversification — positions move together"
    elif avg_corr >= 0.45:
        verdict = "MODERATE diversification"
    elif avg_corr >= 0.30:
        verdict = "GOOD diversification"
    else:
        verdict = "EXCELLENT diversification"

    return {
        'n_positions': n,
        'avg_correlation': round(avg_corr, 2),
        'effective_positions': round(effective, 1),
        'verdict': verdict,
    }


# ---------------------------------------------------------------------------
# Output: terminal
# ---------------------------------------------------------------------------

def format_dollar(val: float) -> str:
    if val >= 1_000_000:
        return f"${val / 1_000_000:.1f}M"
    elif val >= 1_000:
        return f"${val / 1_000:.0f}K"
    else:
        return f"${val:.0f}"


def print_terminal(corr_matrix: pd.DataFrame,
                   pairs: list[dict],
                   clusters: list[dict],
                   metrics: dict,
                   holdings: dict,
                   threshold: float,
                   top_n: int | None):
    """Print the full terminal dashboard."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    width = 70

    print()
    print("=" * width)
    print(f"  CORRELATION MATRIX — Portfolio ({date_str})".center(width))
    print("=" * width)

    # Top correlated pairs
    high_pairs = [p for p in pairs if abs(p['correlation']) >= threshold]
    if high_pairs:
        print()
        print(f"  {BOLD}TOP CORRELATED PAIRS (>={threshold:.2f}):{RESET}")
        print("  " + "-" * (width - 4))

        for p in high_pairs[:20]:
            t1, t2 = p['ticker1'], p['ticker2']
            corr = p['correlation']
            label, color = classify_correlation(corr)
            emoji = "\U0001f534" if label == "EXTREME" else "\u26a0\ufe0f " if label == "HIGH" else ""

            # Combined value
            v1 = holdings.get(t1, {}).get('total_value', 0)
            v2 = holdings.get(t2, {}).get('total_value', 0)
            combined = v1 + v2
            val_str = f"({format_dollar(combined)} combined)" if combined > 0 else ""

            # Leveraged note
            note = leveraged_note(t1, t2)
            note_str = f" — {note}" if note else ""

            line = f"    {t1:>5s} / {t2:<5s}  {color}{corr:6.2f}  {emoji}{label:<8s}{RESET}  {val_str}{note_str}"
            print(line)
    else:
        print()
        print(f"  {GREEN}No pairs above {threshold:.2f} threshold.{RESET}")

    # Diversification score
    print()
    print(f"  {BOLD}DIVERSIFICATION SCORE:{RESET}")
    print("  " + "-" * (width - 4))
    print(f"    Held positions:           {metrics['n_positions']}")
    print(f"    Avg pairwise correlation: {metrics['avg_correlation']:.2f}")
    print(f"    Effective independent:    ~{metrics['effective_positions']:.0f} (of {metrics['n_positions']})")

    verdict = metrics['verdict']
    if "POOR" in verdict:
        vcolor = RED
    elif "MODERATE" in verdict:
        vcolor = YELLOW
    elif "GOOD" in verdict:
        vcolor = GREEN
    else:
        vcolor = GREEN
    print(f"    Verdict:                  {vcolor}{verdict}{RESET}")

    # Cluster analysis
    if clusters:
        print()
        print(f"  {BOLD}CLUSTER ANALYSIS:{RESET}")
        print("  " + "-" * (width - 4))
        for i, cl in enumerate(clusters, 1):
            members = cl['members']
            avg = cl['avg_correlation']
            label = cl.get('label', 'Correlated Group')
            members_str = ", ".join(members)
            total = sum(holdings.get(m, {}).get('total_value', 0) for m in members)
            val_str = f"  {format_dollar(total)}" if total > 0 else ""
            print(f"    Cluster {i} ({label}):  {members_str}  "
                  f"avg corr {avg:.2f}{val_str}")

    # Full matrix (top N by position size)
    display_tickers = corr_matrix.columns.tolist()
    if top_n and len(display_tickers) > top_n:
        # Sort by position size, take top N
        sized = [(t, holdings.get(t, {}).get('total_value', 0)) for t in display_tickers]
        sized.sort(key=lambda x: -x[1])
        display_tickers = [t for t, _ in sized[:top_n]]

    if len(display_tickers) >= 2:
        print()
        label_str = f" (top {top_n} by position size)" if top_n and len(corr_matrix.columns) > top_n else ""
        print(f"  {BOLD}FULL MATRIX{label_str}:{RESET}")
        print("  " + "-" * (width - 4))

        # Header
        col_w = 6
        header = "    " + " " * 6
        for t in display_tickers:
            header += f"{t:>{col_w}s}"
        print(header)

        # Rows
        for row_t in display_tickers:
            row = f"    {row_t:>5s} "
            for col_t in display_tickers:
                if row_t == col_t:
                    row += f"{DIM}  1.00{RESET}"
                else:
                    corr = corr_matrix.loc[row_t, col_t] if col_t in corr_matrix.columns and row_t in corr_matrix.index else float('nan')
                    if pd.isna(corr):
                        row += "     —"
                    else:
                        _, color = classify_correlation(corr)
                        row += f"{color}{corr:6.2f}{RESET}"
            print(row)

    print()
    print("=" * width)
    print()


# ---------------------------------------------------------------------------
# Output: JSON
# ---------------------------------------------------------------------------

def build_json(corr_matrix: pd.DataFrame,
               pairs: list[dict],
               clusters: list[dict],
               metrics: dict,
               holdings: dict,
               threshold: float) -> dict:
    """Build JSON output structure."""
    high_pairs = [p for p in pairs if abs(p['correlation']) >= threshold]
    for p in high_pairs:
        t1, t2 = p['ticker1'], p['ticker2']
        label, _ = classify_correlation(p['correlation'])
        p['severity'] = label
        v1 = holdings.get(t1, {}).get('total_value', 0)
        v2 = holdings.get(t2, {}).get('total_value', 0)
        p['combined_value'] = round(v1 + v2, 2)
        note = leveraged_note(t1, t2)
        if note:
            p['note'] = note

    # Full matrix as dict-of-dicts
    matrix_dict = {}
    for t1 in corr_matrix.columns:
        matrix_dict[t1] = {}
        for t2 in corr_matrix.columns:
            val = corr_matrix.loc[t1, t2]
            matrix_dict[t1][t2] = round(val, 4) if not pd.isna(val) else None

    return {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'metrics': metrics,
        'high_pairs': high_pairs,
        'clusters': clusters,
        'matrix': matrix_dict,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Cross-position correlation analysis for portfolio risk.")
    parser.add_argument("--top", type=int, default=None,
                        help="Limit matrix display to top N positions by size")
    parser.add_argument("--threshold", type=float, default=HIGH_THRESHOLD,
                        help=f"Show pairs above this correlation (default: {HIGH_THRESHOLD})")
    parser.add_argument("--json", action="store_true",
                        help="JSON output")
    parser.add_argument("--period", type=str, default="6mo",
                        help="Price history period (default: 6mo)")
    args = parser.parse_args()

    # Get holdings: piped stdin or parse account files
    stdin_piped = False
    try:
        stdin_piped = not sys.stdin.isatty()
    except Exception:
        pass

    if stdin_piped:
        print("Reading holdings from stdin (watchlist JSON)...", file=sys.stderr)
        raw = sys.stdin.read().strip()
        if raw:
            holdings = get_holdings_from_stdin_raw(raw)
        else:
            print("Empty stdin, falling back to account files...", file=sys.stderr)
            holdings = parse_portfolio_holdings()
    else:
        print("Parsing portfolio account files...", file=sys.stderr)
        holdings = parse_portfolio_holdings()

    if not holdings:
        print("No held positions found.", file=sys.stderr)
        sys.exit(1)

    tickers = sorted(holdings.keys())
    print(f"Found {len(tickers)} held tickers: {', '.join(tickers)}", file=sys.stderr)

    # Fetch returns
    returns = fetch_returns(tickers, period=args.period)

    if returns.empty or len(returns.columns) < 2:
        print("Not enough tickers with valid price data for correlation.", file=sys.stderr)
        sys.exit(1)

    # Calculate correlation
    corr_matrix = calculate_correlation_matrix(returns)

    # Get pairs
    all_pairs = get_correlated_pairs(corr_matrix, threshold=0.0)

    # Detect clusters
    clusters = detect_clusters(corr_matrix, threshold=CLUSTER_THRESHOLD)
    for cl in clusters:
        cl['label'] = label_cluster(cl['members'], holdings)

    # Portfolio metrics
    metrics = portfolio_metrics(corr_matrix, holdings)

    # Output
    if args.json:
        output = build_json(corr_matrix, all_pairs, clusters, metrics,
                            holdings, args.threshold)
        print(json.dumps(output, indent=2))
    else:
        print_terminal(corr_matrix, all_pairs, clusters, metrics,
                       holdings, args.threshold, args.top)


if __name__ == "__main__":
    main()
