#!/usr/bin/env python3
"""
Watchlist manager — tier stocks, identify refresh priorities, flag removals.

Reads research/stocks/ frontmatter and live prices to auto-classify:
  ACTIVE  — refresh weekly (conviction ≥7, near target, earnings <30d)
  PASSIVE — refresh monthly (conviction 5-6, no catalyst)
  REMOVE? — review for removal (no conviction, stale >30d, thesis unclear)

Usage:
    .venv/bin/python3 scripts/watchlist.py              # terminal dashboard
    .venv/bin/python3 scripts/watchlist.py --json        # JSON output
    .venv/bin/python3 scripts/watchlist.py --update      # update tier field in frontmatter
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

STOCKS_DIR = Path("research/stocks")
STALE_DAYS = 7
VERY_STALE_DAYS = 30


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
            if value.startswith('[') and value.endswith(']'):
                value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(',')]
            fm[key] = value
    return fm


def find_last_update(filepath: Path) -> str | None:
    content = filepath.read_text(encoding="utf-8")
    dates = re.findall(r'\|\s*(\d{4}-\d{2}-\d{2})', content)
    if not dates:
        dates = re.findall(r'(\d{4}-\d{2}-\d{2})', content[:2000])
    return max(dates) if dates else None


def find_earnings_date(filepath: Path) -> tuple[str | None, int | None]:
    """Find earnings date and days until it."""
    content = filepath.read_text(encoding="utf-8")
    patterns = [
        r'[Ee]arnings\s*(?:\*\*)?(?:date)?:?\s*(?:\*\*)?\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2}(?:,?\s*\d{4})?)',
        r'[Nn]ext\s+earnings[:\s]+(?:\*\*)?((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2}(?:,?\s*\d{4})?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            date_str = match.group(1).strip('*')
            for fmt in ['%B %d, %Y', '%B %d', '%b %d, %Y', '%b %d']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    if dt.year < 2026:
                        dt = dt.replace(year=2026)
                    days_until = (dt - datetime.now()).days
                    return date_str, days_until
                except ValueError:
                    continue
    return None, None


def days_since(date_str: str) -> int:
    try:
        return (datetime.now() - datetime.strptime(date_str, "%Y-%m-%d")).days
    except (ValueError, TypeError):
        return 999


def get_prices(tickers: list[str]) -> dict:
    if not HAS_YFINANCE or not tickers:
        return {}
    us_tickers = [t for t in tickers if not any(c in t for c in ['.', '/', 'IBDNF'])]
    if not us_tickers:
        return {}
    try:
        data = yf.download(us_tickers, period="5d", progress=False)
        prices = {}
        if len(us_tickers) == 1:
            try:
                closes = data['Close'].dropna().tolist()
                if closes:
                    prices[us_tickers[0]] = round(float(closes[-1]), 2)
            except (KeyError, IndexError):
                pass
        else:
            for t in us_tickers:
                try:
                    closes = data['Close'][t].dropna().tolist()
                    if closes:
                        prices[t] = round(float(closes[-1]), 2)
                except (KeyError, IndexError):
                    pass
        return prices
    except Exception:
        return {}


def classify_stock(stock: dict, price: float | None) -> dict:
    """Classify a stock into a tier with reasons."""
    ticker = stock['ticker']
    conviction = stock.get('conviction')
    conv_f = None
    if conviction:
        try:
            conv_f = float(conviction)
        except (ValueError, TypeError):
            pass

    stale_days = stock['stale_days']
    earnings_date = stock.get('earnings_date')
    earnings_days = stock.get('earnings_days')
    entry_target = stock.get('entry_target')

    # Calculate gap to target
    gap_pct = None
    if price and entry_target:
        try:
            target_f = float(entry_target)
            if target_f > 0:
                gap_pct = ((price / target_f) - 1) * 100
        except (ValueError, TypeError):
            pass

    reasons = []
    tier = 'passive'

    # --- ACTIVE triggers ---
    if conv_f and conv_f >= 7:
        tier = 'active'
        reasons.append(f"conviction {conv_f}")

    if gap_pct is not None and -15 < gap_pct < 5:
        tier = 'active'
        reasons.append(f"near target ({gap_pct:+.1f}%)")

    if earnings_days is not None and 0 < earnings_days <= 30:
        tier = 'active'
        reasons.append(f"earnings in {earnings_days}d")

    # --- REMOVE triggers (override to remove if no active reasons) ---
    if tier != 'active':
        remove_reasons = []
        if conv_f is not None and conv_f < 5:
            remove_reasons.append(f"low conviction ({conv_f})")
        if conv_f is None and stale_days > VERY_STALE_DAYS:
            remove_reasons.append(f"no conviction + stale {stale_days}d")
        if stale_days > 60:
            remove_reasons.append(f"very stale ({stale_days}d)")
        if gap_pct is not None and gap_pct > 50:
            remove_reasons.append(f"far above target ({gap_pct:+.0f}%)")

        if remove_reasons:
            tier = 'remove'
            reasons = remove_reasons
        elif not reasons:
            reasons.append("no active triggers")

    # --- Refresh priority within active ---
    refresh_priority = 0
    if tier == 'active':
        if stale_days > STALE_DAYS:
            refresh_priority += 3
            reasons.append(f"stale {stale_days}d")
        if earnings_days is not None and 0 < earnings_days <= 14:
            refresh_priority += 2
        if gap_pct is not None and abs(gap_pct) < 5:
            refresh_priority += 1

    return {
        'ticker': ticker,
        'tier': tier,
        'conviction': conv_f,
        'sector': stock.get('sector', ''),
        'stale_days': stale_days,
        'gap_pct': gap_pct,
        'price': price,
        'entry_target': entry_target,
        'earnings': earnings_date,
        'earnings_days': earnings_days,
        'reasons': reasons,
        'refresh_priority': refresh_priority,
        'needs_refresh': tier == 'active' and stale_days > STALE_DAYS,
    }


def load_and_classify() -> list[dict]:
    """Load all watching stocks and classify them."""
    if not STOCKS_DIR.exists():
        return []

    stocks_raw = []
    for f in STOCKS_DIR.glob("*.md"):
        if f.name.startswith(('0-', '1-')):
            continue
        fm = parse_frontmatter(f)
        if not fm.get('ticker') or fm.get('status') != 'watching':
            continue

        last_update = find_last_update(f)
        earnings_date, earnings_days = find_earnings_date(f)

        stocks_raw.append({
            'ticker': fm['ticker'],
            'status': fm.get('status', ''),
            'sector': fm.get('sector', ''),
            'conviction': fm.get('conviction'),
            'entry_target': fm.get('entry_target'),
            'stale_days': days_since(last_update) if last_update else 999,
            'last_update': last_update,
            'earnings_date': earnings_date,
            'earnings_days': earnings_days,
            'filepath': f,
        })

    # Fetch prices
    tickers = [s['ticker'] for s in stocks_raw]
    print("Fetching prices...", file=sys.stderr)
    prices = get_prices(tickers)

    # Classify
    classified = []
    for s in stocks_raw:
        price = prices.get(s['ticker'])
        result = classify_stock(s, price)
        result['filepath'] = s.get('filepath')
        result['last_update'] = s.get('last_update')
        classified.append(result)

    return classified


def update_frontmatter_tier(filepath: Path, tier: str):
    """Update or add tier field in frontmatter."""
    content = filepath.read_text(encoding="utf-8")
    match = re.match(r'^(---\s*\n)(.*?)(\n---)', content, re.DOTALL)
    if not match:
        return

    fm_block = match.group(2)

    # Update or add tier
    if re.search(r'^tier:', fm_block, re.MULTILINE):
        fm_block = re.sub(r'^tier:.*$', f'tier: {tier}', fm_block, flags=re.MULTILINE)
    else:
        fm_block += f'\ntier: {tier}'

    new_content = match.group(1) + fm_block + match.group(3) + content[match.end():]
    filepath.write_text(new_content, encoding="utf-8")


def print_dashboard(classified: list[dict]):
    """Print tiered watchlist to terminal."""
    active = sorted(
        [s for s in classified if s['tier'] == 'active'],
        key=lambda s: (-s['refresh_priority'], -(s['conviction'] or 0)),
    )
    passive = sorted(
        [s for s in classified if s['tier'] == 'passive'],
        key=lambda s: s['ticker'],
    )
    remove = sorted(
        [s for s in classified if s['tier'] == 'remove'],
        key=lambda s: s['ticker'],
    )

    needs_refresh = [s for s in active if s['needs_refresh']]

    width = 90
    print("=" * width)
    print(f"  WATCHLIST MANAGER — {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * width)

    # Summary
    print(f"\n  {len(active)} active | {len(passive)} passive | {len(remove)} remove candidates | {len(needs_refresh)} need refresh\n")

    # Active
    print(f"  {'ACTIVE':} ({len(active)} stocks — refresh weekly)")
    print(f"  {'-' * (width - 4)}")
    for s in active:
        conv = f"{s['conviction']:.1f}" if s['conviction'] else "  ?"
        gap = f"{s['gap_pct']:+.1f}%" if s['gap_pct'] is not None else "    —"
        refresh = "🔄 REFRESH" if s['needs_refresh'] else "  ✅ fresh"
        reasons_str = ", ".join(s['reasons'][:3])
        print(f"    {s['ticker']:6s} | conv {conv} | gap {gap:>7s} | {refresh} | {reasons_str}")

    print()

    # Passive
    print(f"  {'PASSIVE':} ({len(passive)} stocks — check monthly)")
    print(f"  {'-' * (width - 4)}")
    for s in passive:
        conv = f"{s['conviction']:.1f}" if s['conviction'] else "  ?"
        stale = f"{s['stale_days']}d" if s['stale_days'] < 999 else "never"
        reasons_str = ", ".join(s['reasons'][:2])
        print(f"    {s['ticker']:6s} | conv {conv} | stale {stale:>5s} | {reasons_str}")

    print()

    # Remove candidates
    if remove:
        print(f"  {'REMOVE?':} ({len(remove)} stocks — review for removal)")
        print(f"  {'-' * (width - 4)}")
        for s in remove:
            conv = f"{s['conviction']:.1f}" if s['conviction'] else "  ?"
            reasons_str = ", ".join(s['reasons'][:2])
            print(f"    {s['ticker']:6s} | conv {conv} | {reasons_str}")

    print()

    # Refresh list
    if needs_refresh:
        print(f"  REFRESH QUEUE (run /research-stock on these):")
        print(f"  {'-' * (width - 4)}")
        tickers = [s['ticker'] for s in needs_refresh]
        print(f"    {', '.join(tickers)}")

    print()
    print("=" * width)


def main():
    parser = argparse.ArgumentParser(description="Watchlist manager")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--update", action="store_true", help="Update tier in frontmatter")
    args = parser.parse_args()

    classified = load_and_classify()

    if args.update:
        for s in classified:
            if s.get('filepath'):
                update_frontmatter_tier(s['filepath'], s['tier'])
        print(f"Updated tier for {len(classified)} stocks.")
        return

    if args.json:
        output = []
        for s in classified:
            entry = {k: v for k, v in s.items() if k != 'filepath'}
            output.append(entry)
        print(json.dumps(output, indent=2))
        return

    print_dashboard(classified)


if __name__ == "__main__":
    main()
