#!/usr/bin/env python3
"""
Watchlist manager — single source of truth for watchlist status.

Consolidates: triage, priority refresh queue, live market data (price, RSI, fwd P/E),
sector momentum, earnings calendar, and generates 0-WATCHLIST.md.

Replaces: update-index.py (0-INDEX.md) and dashboard.py (1-DASHBOARD.md).

Usage:
    .venv/bin/python3 scripts/watchlist.py              # terminal dashboard + save 0-WATCHLIST.md
    .venv/bin/python3 scripts/watchlist.py --json        # JSON output
    .venv/bin/python3 scripts/watchlist.py --auto        # top N tickers only (for piping)
    .venv/bin/python3 scripts/watchlist.py --top 10      # show top 10 in refresh queue
    .venv/bin/python3 scripts/watchlist.py --update      # update tier field in frontmatter
    .venv/bin/python3 scripts/watchlist.py --add TICKER                    # quick-add a stock
    .venv/bin/python3 scripts/watchlist.py --add TICKER --sector Energy    # with sector
    .venv/bin/python3 scripts/watchlist.py --add TICKER --source "friend"  # with source
    .venv/bin/python3 scripts/watchlist.py --no-save     # skip writing 0-WATCHLIST.md
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

STOCKS_DIR = Path("research/stocks")
WATCHLIST_FILE = STOCKS_DIR / "0-WATCHLIST.md"

# --- Tiered refresh cadence ---
REFRESH_CADENCE = {
    "high": 14,    # conviction 8+
    "medium": 28,  # conviction 6-7.9
    "low": 42,     # conviction 5-5.9
}

VERY_STALE_DAYS = 60

# --- Priority scoring constants ---
DEFAULT_TOP_N = 5
CANDIDATE_BONUS = 35          # new stocks get high priority
STALENESS_SCALE = 3           # +1 point per N days stale
STALENESS_CAP = 20            # max staleness bonus

MOMENTUM_BONUS = {
    "Accelerating Up": 15,
    "Steady Uptrend": 10,
    "Pulling Back in Uptrend": 8,
    "Pulling Back": 8,
    "Sideways": 0,
    "Mixed": 0,
    "Downtrend": -5,
    "Capitulation": -5,
}

# Map stock frontmatter sector names → GICS sector names from sector-momentum.py
SECTOR_TO_GICS = {
    "Semiconductors": "Technology",
    "Semiconductors / Memory": "Technology",
    "Semiconductors / Optical Communications": "Technology",
    "Semiconductor Equipment": "Technology",
    "Technology": "Technology",
    "Technology/Optical Communications": "Technology",
    "Technology/Optical Networking": "Technology",
    "Technology/Photonics": "Technology",
    "Software": "Technology",
    "Software - Infrastructure": "Technology",
    "Software/Gaming": "Technology",
    "Software (ETF)": "Technology",
    "Cybersecurity / Software": "Technology",
    "Communication Services": "Communication",
    "Healthcare": "Healthcare",
    "Financial Services": "Financials",
    "Crypto/Fintech": "Financials",
    "Energy": "Energy",
    "Industrials": "Industrials",
    "Industrials/Data Center Infrastructure": "Industrials",
    "Consumer Cyclical": "Consumer Disc.",
    "EVs/Autonomy": "Consumer Disc.",
    "Real Estate": "Real Estate",
    "Materials": "Materials",
    "Utilities": "Utilities",
    "Consumer Staples": "Consumer Staples",
    "Leveraged ETF / South Korea": None,  # no GICS mapping
}


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
    current_year = datetime.now().year
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            date_str = match.group(1).strip('*')
            for fmt in ['%B %d, %Y', '%B %d', '%b %d, %Y', '%b %d']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    if dt.year < current_year:
                        dt = dt.replace(year=current_year)
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


def get_market_data(tickers: list[str]) -> tuple[dict, dict, dict]:
    """Fetch current prices, RSI, and forward P/E for a list of tickers."""
    prices = {}
    rsi_values = {}
    fwd_pe = {}

    if not HAS_YFINANCE or not tickers:
        return prices, rsi_values, fwd_pe

    us_tickers = [t for t in tickers if not any(c in t for c in ['.', '/', 'IBDNF'])]
    if not us_tickers:
        return prices, rsi_values, fwd_pe

    try:
        # Use 1mo period for RSI calculation (need 14+ trading days)
        data = yf.download(us_tickers, period="1mo", progress=False)
        if len(us_tickers) == 1:
            try:
                closes = data['Close'].dropna().tolist()
                if closes:
                    prices[us_tickers[0]] = round(float(closes[-1]), 2)
                    rsi = compute_rsi(closes)
                    if rsi is not None:
                        rsi_values[us_tickers[0]] = rsi
            except (KeyError, IndexError):
                pass
        else:
            for t in us_tickers:
                try:
                    closes = data['Close'][t].dropna().tolist()
                    if closes:
                        prices[t] = round(float(closes[-1]), 2)
                        rsi = compute_rsi(closes)
                        if rsi is not None:
                            rsi_values[t] = rsi
                except (KeyError, IndexError):
                    pass

        # Fetch forward P/E for each ticker
        print("Fetching fundamentals...", file=sys.stderr)
        for t in us_tickers:
            try:
                info = yf.Ticker(t).info
                pe = info.get('forwardPE')
                if pe and pe > 0:
                    fwd_pe[t] = round(float(pe), 1)
            except Exception:
                pass

    except Exception:
        pass

    return prices, rsi_values, fwd_pe


def fetch_sector_momentum() -> dict[str, str]:
    """Run sector-momentum.py --json and return {gics_sector: momentum_classification}."""
    try:
        result = subprocess.run(
            [sys.executable, "scripts/sector-momentum.py", "--json"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            print("  ⚠ sector-momentum.py failed, skipping sector bonus", file=sys.stderr)
            return {}
        data = json.loads(result.stdout)
        return {entry["sector"]: entry["momentum"] for entry in data}
    except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, Exception) as e:
        print(f"  ⚠ sector momentum unavailable: {e}", file=sys.stderr)
        return {}


def get_refresh_cadence(conv_f: float | None) -> int:
    """Return stale threshold in days based on conviction tier."""
    if conv_f is not None and conv_f >= 8:
        return REFRESH_CADENCE["high"]     # 14 days
    elif conv_f is not None and conv_f >= 6:
        return REFRESH_CADENCE["medium"]   # 28 days
    else:
        return REFRESH_CADENCE["low"]      # 42 days


def compute_priority_score(stock: dict, gap_pct: float | None,
                           sector_momentum: str | None,
                           is_candidate: bool = False) -> tuple[int, list[str]]:
    """Compute numeric priority score and breakdown for refresh ordering."""
    score = 0
    breakdown = []

    # Candidate bonus — new stocks need first research
    if is_candidate:
        score += CANDIDATE_BONUS
        breakdown.append(f"NEW candidate (+{CANDIDATE_BONUS})")

    # Earnings proximity (highest weight)
    earnings_days = stock.get('earnings_days')
    if earnings_days is not None and earnings_days > 0:
        if earnings_days < 7:
            score += 40
            breakdown.append(f"earnings <7d (+40)")
        elif earnings_days < 14:
            score += 25
            breakdown.append(f"earnings <14d (+25)")
        elif earnings_days < 30:
            score += 10
            breakdown.append(f"earnings <30d (+10)")

    # Sector momentum bonus
    if sector_momentum:
        bonus = MOMENTUM_BONUS.get(sector_momentum, 0)
        if bonus != 0:
            score += bonus
            breakdown.append(f"sector {sector_momentum} ({bonus:+d})")

    # Gap to target
    if gap_pct is not None:
        if abs(gap_pct) <= 5:
            score += 25
            breakdown.append(f"within 5% of target (+25)")
        elif abs(gap_pct) <= 10:
            score += 15
            breakdown.append(f"within 10% of target (+15)")
        elif abs(gap_pct) <= 15:
            score += 5
            breakdown.append(f"within 15% of target (+5)")

    # Staleness
    stale_days = stock.get('stale_days', 0)
    if stale_days > 0 and not is_candidate:
        stale_pts = min(stale_days // STALENESS_SCALE, STALENESS_CAP)
        if stale_pts > 0:
            score += stale_pts
            breakdown.append(f"stale {stale_days}d (+{stale_pts})")

    # Conviction (lighter weight — may be stale)
    conviction = stock.get('conviction')
    if conviction:
        try:
            conv_f = float(conviction)
            conv_pts = round(conv_f * 2)
            score += conv_pts
            breakdown.append(f"conv {conv_f} (+{conv_pts})")
        except (ValueError, TypeError):
            pass

    return score, breakdown


def classify_stock(stock: dict, price: float | None, sector_momentum: str | None,
                   rsi: float | None = None, fwd_pe: float | None = None) -> dict:
    """Classify a stock into a tier with reasons and priority score."""
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
    is_candidate = stock.get('status') == 'candidate'

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

    # --- CANDIDATE: always needs research ---
    if is_candidate:
        tier = 'candidate'
        reasons.append("new — needs first research")
        priority_score, score_breakdown = compute_priority_score(
            stock, gap_pct, sector_momentum, is_candidate=True)
        return {
            'ticker': ticker,
            'tier': tier,
            'conviction': conv_f,
            'sector': stock.get('sector', ''),
            'thesis': stock.get('thesis', ''),
            'strategies': stock.get('strategies', []),
            'stale_days': stale_days,
            'gap_pct': gap_pct,
            'price': price,
            'rsi': rsi,
            'fwd_pe': fwd_pe,
            'entry_target': entry_target,
            'earnings': earnings_date,
            'earnings_days': earnings_days,
            'reasons': reasons,
            'priority_score': priority_score,
            'score_breakdown': score_breakdown,
            'sector_momentum': sector_momentum,
            'needs_refresh': True,
        }

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
        if stale_days > 90:
            remove_reasons.append(f"very stale ({stale_days}d)")
        if gap_pct is not None and gap_pct > 50:
            remove_reasons.append(f"far above target ({gap_pct:+.0f}%)")

        if remove_reasons:
            tier = 'remove'
            reasons = remove_reasons
        elif not reasons:
            reasons.append("no active triggers")

    # --- Tiered refresh check ---
    cadence = get_refresh_cadence(conv_f)
    needs_refresh = tier == 'active' and stale_days > cadence

    if needs_refresh and stale_days > cadence:
        reasons.append(f"stale {stale_days}d (cadence {cadence}d)")

    # --- Priority scoring ---
    priority_score, score_breakdown = compute_priority_score(
        stock, gap_pct, sector_momentum)

    return {
        'ticker': ticker,
        'tier': tier,
        'conviction': conv_f,
        'sector': stock.get('sector', ''),
        'thesis': stock.get('thesis', ''),
        'strategies': stock.get('strategies', []),
        'stale_days': stale_days,
        'gap_pct': gap_pct,
        'price': price,
        'rsi': rsi,
        'fwd_pe': fwd_pe,
        'entry_target': entry_target,
        'earnings': earnings_date,
        'earnings_days': earnings_days,
        'reasons': reasons,
        'priority_score': priority_score,
        'score_breakdown': score_breakdown,
        'sector_momentum': sector_momentum,
        'needs_refresh': needs_refresh,
    }


def load_and_classify() -> list[dict]:
    """Load all watching/candidate stocks and classify them."""
    if not STOCKS_DIR.exists():
        return []

    # Start sector momentum fetch early (runs in parallel with market data fetch)
    momentum_proc = None
    try:
        momentum_proc = subprocess.Popen(
            [sys.executable, "scripts/sector-momentum.py", "--json"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
    except Exception:
        pass

    stocks_raw = []
    for f in STOCKS_DIR.glob("*.md"):
        if f.name.startswith(('0-', '1-')):
            continue
        fm = parse_frontmatter(f)
        if not fm.get('ticker') or fm.get('status') not in ('watching', 'candidate'):
            continue

        last_update = find_last_update(f)
        earnings_date, earnings_days = find_earnings_date(f)

        stocks_raw.append({
            'ticker': fm['ticker'],
            'status': fm.get('status', ''),
            'sector': fm.get('sector', ''),
            'thesis': fm.get('thesis', ''),
            'conviction': fm.get('conviction'),
            'entry_target': fm.get('entry_target'),
            'strategies': fm.get('strategies', []),
            'stale_days': days_since(last_update) if last_update else 999,
            'last_update': last_update,
            'earnings_date': earnings_date,
            'earnings_days': earnings_days,
            'filepath': f,
        })

    # Fetch market data (prices, RSI, fwd P/E)
    tickers = [s['ticker'] for s in stocks_raw]
    print("Fetching market data...", file=sys.stderr)
    prices, rsi_values, fwd_pe_values = get_market_data(tickers)

    # Collect sector momentum (should be done by now)
    sector_momentum_map = {}
    if momentum_proc:
        try:
            stdout, _ = momentum_proc.communicate(timeout=45)
            if momentum_proc.returncode == 0:
                data = json.loads(stdout)
                sector_momentum_map = {entry["sector"]: entry["momentum"] for entry in data}
            else:
                print("  ⚠ sector-momentum.py failed, skipping sector bonus", file=sys.stderr)
        except Exception as e:
            print(f"  ⚠ sector momentum unavailable: {e}", file=sys.stderr)
            if momentum_proc.poll() is None:
                momentum_proc.kill()

    # Classify
    classified = []
    for s in stocks_raw:
        ticker = s['ticker']
        price = prices.get(ticker)
        rsi = rsi_values.get(ticker)
        pe = fwd_pe_values.get(ticker)
        # Map stock sector → GICS sector → momentum
        gics_sector = SECTOR_TO_GICS.get(s.get('sector', ''))
        momentum = sector_momentum_map.get(gics_sector) if gics_sector else None
        # Warn on unmapped sectors (for maintenance)
        if s.get('sector') and s['sector'] not in SECTOR_TO_GICS:
            print(f"  ⚠ unmapped sector '{s['sector']}' for {ticker}", file=sys.stderr)
        result = classify_stock(s, price, momentum, rsi=rsi, fwd_pe=pe)
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


def add_stock(ticker: str, sector: str | None = None, source: str | None = None):
    """Create a candidate stub file for a new stock."""
    ticker = ticker.upper()
    filepath = STOCKS_DIR / f"{ticker}.md"

    if filepath.exists():
        fm = parse_frontmatter(filepath)
        print(f"  {ticker} already exists (status: {fm.get('status', 'unknown')})")
        return

    STOCKS_DIR.mkdir(parents=True, exist_ok=True)

    # Try to look up sector from yfinance if not provided
    if not sector and HAS_YFINANCE:
        try:
            info = yf.Ticker(ticker).info
            sector = info.get('sector', None)
        except Exception:
            pass

    date_str = datetime.now().strftime("%Y-%m-%d")
    source_line = f'\nsource: "{source}"' if source else ""

    content = f"""---
ticker: {ticker}
status: candidate
added_date: {date_str}
sector: {sector or "null"}{source_line}
---
"""
    filepath.write_text(content, encoding="utf-8")
    print(f"  ✅ Added {ticker} as candidate → research/stocks/{ticker}.md")
    if sector:
        print(f"     Sector: {sector}")
    if source:
        print(f"     Source: {source}")
    print(f"     Run /research-stock {ticker} to complete the profile.")


# --- Terminal dashboard ---

def rsi_flag(rsi_val):
    if rsi_val is None:
        return "  —"
    if rsi_val < 30:
        return f"{rsi_val:4.0f} OS"
    elif rsi_val > 70:
        return f"{rsi_val:4.0f} OB"
    return f"{rsi_val:4.0f}   "


def pe_flag(pe_val):
    if pe_val is None:
        return "     —"
    if pe_val < 15:
        return f"{pe_val:5.1f}x$"
    elif pe_val > 100:
        return f"{pe_val:5.0f}x!"
    return f"{pe_val:5.1f}x "


def print_dashboard(classified: list[dict], top_n: int = DEFAULT_TOP_N):
    """Print tiered watchlist to terminal."""
    candidates = sorted(
        [s for s in classified if s['tier'] == 'candidate'],
        key=lambda s: -s['priority_score'],
    )
    active = sorted(
        [s for s in classified if s['tier'] == 'active'],
        key=lambda s: (-s['priority_score'], -(s['conviction'] or 0)),
    )
    passive = sorted(
        [s for s in classified if s['tier'] == 'passive'],
        key=lambda s: s['ticker'],
    )
    remove = sorted(
        [s for s in classified if s['tier'] == 'remove'],
        key=lambda s: s['ticker'],
    )

    needs_refresh = sorted(
        [s for s in classified if s['needs_refresh']],
        key=lambda s: -s['priority_score'],
    )

    width = 120
    print("=" * width)
    print(f"  WATCHLIST — {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * width)

    # Summary
    n_active = len(active)
    n_cand = len(candidates)
    n_passive = len(passive)
    n_remove = len(remove)
    n_refresh = len(needs_refresh)
    print(f"\n  {n_active} active | {n_cand} candidate | {n_passive} passive | {n_remove} remove | {n_refresh} need refresh\n")

    # Candidates
    if candidates:
        print(f"  CANDIDATES ({len(candidates)} — need first /research-stock)")
        print(f"  {'-' * (width - 4)}")
        for s in candidates:
            sector_str = s['sector'] or '?'
            mom = f" [{s['sector_momentum']}]" if s.get('sector_momentum') else ""
            price_str = f"${s['price']:.2f}" if s['price'] else "—"
            rsi_str = rsi_flag(s.get('rsi'))
            pe_str = pe_flag(s.get('fwd_pe'))
            print(f"    {s['ticker']:6s} | score {s['priority_score']:3d} | {price_str:>9s} | RSI {rsi_str} | PE {pe_str} | {sector_str}{mom}")
        print()

    # Active — full table with market data
    cadence_note = "conv 8+: 14d, 6-7: 28d, <6: 42d"
    print(f"  ACTIVE ({len(active)} — cadence: {cadence_note})")
    print(f"  {'-' * (width - 4)}")
    print(f"    {'TICKER':6s} | {'CONV':>4s} | {'PRICE':>9s} | {'RSI':>6s} | {'FwdPE':>6s} | {'GAP':>7s} | {'EARN':>5s} | {'STATUS':8s} | REASONS")
    print(f"    {'-'*6} | {'-'*4} | {'-'*9} | {'-'*6} | {'-'*6} | {'-'*7} | {'-'*5} | {'-'*8} | {'-'*20}")
    for s in active:
        conv = f"{s['conviction']:.1f}" if s['conviction'] else "  ?"
        price_str = f"${s['price']:.2f}" if s['price'] else "      —"
        rsi_str = rsi_flag(s.get('rsi'))
        pe_str = pe_flag(s.get('fwd_pe'))
        gap = f"{s['gap_pct']:+.1f}%" if s['gap_pct'] is not None else "    —"
        earn = f"{s['earnings_days']:3d}d" if s.get('earnings_days') and s['earnings_days'] > 0 else "   —"
        if s['needs_refresh']:
            status = f"🔄 {s['priority_score']:3d}"
        else:
            status = "  ✅    "
        reasons_str = ", ".join(s['reasons'][:2])
        print(f"    {s['ticker']:6s} | {conv:>4s} | {price_str:>9s} | {rsi_str} | {pe_str} | {gap:>7s} | {earn:>5s} | {status} | {reasons_str}")

    print()

    # Passive
    if passive:
        print(f"  PASSIVE ({len(passive)} — check monthly)")
        print(f"  {'-' * (width - 4)}")
        for s in passive:
            conv = f"{s['conviction']:.1f}" if s['conviction'] else "  ?"
            price_str = f"${s['price']:.2f}" if s['price'] else "—"
            rsi_str = rsi_flag(s.get('rsi'))
            pe_str = pe_flag(s.get('fwd_pe'))
            stale = f"{s['stale_days']}d" if s['stale_days'] < 999 else "never"
            reasons_str = ", ".join(s['reasons'][:2])
            print(f"    {s['ticker']:6s} | conv {conv} | {price_str:>9s} | RSI {rsi_str} | PE {pe_str} | stale {stale:>5s} | {reasons_str}")
        print()

    # Remove candidates
    if remove:
        print(f"  REMOVE? ({len(remove)} — review for removal)")
        print(f"  {'-' * (width - 4)}")
        for s in remove:
            conv = f"{s['conviction']:.1f}" if s['conviction'] else "  ?"
            reasons_str = ", ".join(s['reasons'][:2])
            print(f"    {s['ticker']:6s} | conv {conv} | {reasons_str}")
        print()

    # Priority refresh queue
    print(f"  REFRESH QUEUE — top {min(top_n, len(needs_refresh))} of {len(needs_refresh)}:")
    print(f"  {'-' * (width - 4)}")
    if needs_refresh:
        for i, s in enumerate(needs_refresh[:top_n], 1):
            conv = f"{s['conviction']:.1f}" if s['conviction'] else " ?"
            top_reasons = " | ".join(s['score_breakdown'][:3])
            print(f"    {i:2d}. {s['ticker']:6s}  score {s['priority_score']:3d}  conv {conv}  — {top_reasons}")
        if len(needs_refresh) > top_n:
            print(f"\n    ... and {len(needs_refresh) - top_n} more (use --top N to see more)")
    else:
        print(f"    All stocks are fresh!")

    print()
    print("=" * width)


# --- Markdown generation for 0-WATCHLIST.md ---

def rsi_md(rsi_val):
    if rsi_val is None:
        return "—"
    if rsi_val < 30:
        return f"**{rsi_val:.0f}** 🔻"
    elif rsi_val > 70:
        return f"**{rsi_val:.0f}** 🔺"
    return f"{rsi_val:.0f}"


def pe_md(pe_val):
    if pe_val is None:
        return "—"
    if pe_val < 15:
        return f"**{pe_val:.1f}x** 💰"
    elif pe_val > 100:
        return f"**{pe_val:.0f}x** ⚠️"
    return f"{pe_val:.1f}x"


def generate_watchlist_md(classified: list[dict], top_n: int = DEFAULT_TOP_N) -> str:
    """Generate 0-WATCHLIST.md content."""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = []

    lines.append(f"# Watchlist")
    lines.append(f"")
    lines.append(f"*Auto-generated on {today} by `scripts/watchlist.py`*")
    lines.append(f"")

    # Separate by tier
    candidates = sorted(
        [s for s in classified if s['tier'] == 'candidate'],
        key=lambda s: -s['priority_score'],
    )
    active = sorted(
        [s for s in classified if s['tier'] == 'active'],
        key=lambda s: (-s['priority_score'], -(s['conviction'] or 0)),
    )
    passive = sorted(
        [s for s in classified if s['tier'] == 'passive'],
        key=lambda s: s['ticker'],
    )
    remove = sorted(
        [s for s in classified if s['tier'] == 'remove'],
        key=lambda s: s['ticker'],
    )
    needs_refresh = sorted(
        [s for s in classified if s['needs_refresh']],
        key=lambda s: -s['priority_score'],
    )

    n_active = len(active)
    n_cand = len(candidates)
    n_passive = len(passive)
    n_remove = len(remove)
    n_refresh = len(needs_refresh)

    lines.append(f"**{n_active}** active | **{n_cand}** candidate | **{n_passive}** passive | **{n_remove}** remove | **{n_refresh}** need refresh")
    lines.append(f"")

    # Refresh queue
    lines.append(f"## Refresh Queue (top {min(top_n, len(needs_refresh))} of {len(needs_refresh)})")
    lines.append(f"")
    if needs_refresh:
        lines.append(f"| # | Ticker | Score | Conv | Why |")
        lines.append(f"|---|--------|-------|------|-----|")
        for i, s in enumerate(needs_refresh[:top_n], 1):
            conv = f"{s['conviction']:.1f}" if s['conviction'] else "?"
            why = ", ".join(s['score_breakdown'][:3])
            lines.append(f"| {i} | [{s['ticker']}]({s['ticker']}.md) | {s['priority_score']} | {conv} | {why} |")
    else:
        lines.append(f"All stocks are fresh!")
    lines.append(f"")

    # Candidates
    if candidates:
        lines.append(f"## Candidates ({len(candidates)} — need /research-stock)")
        lines.append(f"")
        lines.append(f"| Ticker | Score | Price | RSI | Fwd P/E | Sector | Momentum |")
        lines.append(f"|--------|-------|-------|-----|---------|--------|----------|")
        for s in candidates:
            price_str = f"${s['price']:.2f}" if s['price'] else "—"
            mom = s.get('sector_momentum', '—') or '—'
            lines.append(f"| [{s['ticker']}]({s['ticker']}.md) | {s['priority_score']} | {price_str} | {rsi_md(s.get('rsi'))} | {pe_md(s.get('fwd_pe'))} | {s['sector'] or '?'} | {mom} |")
        lines.append(f"")

    # Active — grouped by sector
    lines.append(f"## Active ({len(active)} stocks)")
    lines.append(f"")
    lines.append(f"*Refresh cadence: conv 8+ = 14d, conv 6-7 = 28d, conv <6 = 42d*")
    lines.append(f"")

    # Group by sector
    sectors = {}
    for s in active:
        sector = s['sector'] or 'Other'
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(s)

    for sector in sorted(sectors.keys()):
        lines.append(f"### {sector}")
        lines.append(f"")
        lines.append(f"| Ticker | Conv | Price | RSI | Fwd P/E | Target | Gap | Earn | Status | Thesis |")
        lines.append(f"|--------|------|-------|-----|---------|--------|-----|------|--------|--------|")
        for s in sectors[sector]:
            conv = f"{s['conviction']:.1f}" if s['conviction'] else "?"
            price_str = f"${s['price']:.2f}" if s['price'] else "—"
            target_str = f"${s['entry_target']}" if s['entry_target'] else "—"
            gap_str = f"{s['gap_pct']:+.1f}%" if s['gap_pct'] is not None else "—"
            earn_str = f"{s['earnings_days']}d" if s.get('earnings_days') and s['earnings_days'] > 0 else "—"
            status = f"🔄 {s['priority_score']}" if s['needs_refresh'] else "✅"
            thesis = s.get('thesis', '')[:80]
            strategies = ", ".join(s['strategies']) if isinstance(s['strategies'], list) else s.get('strategies', '')
            lines.append(f"| [{s['ticker']}]({s['ticker']}.md) | {conv} | {price_str} | {rsi_md(s.get('rsi'))} | {pe_md(s.get('fwd_pe'))} | {target_str} | {gap_str} | {earn_str} | {status} | {thesis} |")
        lines.append(f"")

    # Passive
    if passive:
        lines.append(f"## Passive ({len(passive)} stocks)")
        lines.append(f"")
        lines.append(f"| Ticker | Conv | Price | RSI | Fwd P/E | Sector | Reason |")
        lines.append(f"|--------|------|-------|-----|---------|--------|--------|")
        for s in passive:
            conv = f"{s['conviction']:.1f}" if s['conviction'] else "?"
            price_str = f"${s['price']:.2f}" if s['price'] else "—"
            reasons_str = ", ".join(s['reasons'][:2])
            lines.append(f"| [{s['ticker']}]({s['ticker']}.md) | {conv} | {price_str} | {rsi_md(s.get('rsi'))} | {pe_md(s.get('fwd_pe'))} | {s['sector'] or '?'} | {reasons_str} |")
        lines.append(f"")

    # Remove
    if remove:
        lines.append(f"## Remove Candidates ({len(remove)} stocks)")
        lines.append(f"")
        lines.append(f"| Ticker | Conv | Reason |")
        lines.append(f"|--------|------|--------|")
        for s in remove:
            conv = f"{s['conviction']:.1f}" if s['conviction'] else "?"
            reasons_str = ", ".join(s['reasons'][:2])
            lines.append(f"| [{s['ticker']}]({s['ticker']}.md) | {conv} | {reasons_str} |")
        lines.append(f"")

    # Earnings calendar
    earnings_stocks = [(s['ticker'], s['earnings'], s['earnings_days'])
                       for s in classified
                       if s.get('earnings_days') and s['earnings_days'] > 0]
    if earnings_stocks:
        earnings_stocks.sort(key=lambda x: x[2])
        lines.append(f"## Earnings Calendar")
        lines.append(f"")
        lines.append(f"| Ticker | Earnings | Days |")
        lines.append(f"|--------|----------|------|")
        for ticker, date, days in earnings_stocks:
            urgency = " ⚡" if days < 7 else ""
            lines.append(f"| [{ticker}]({ticker}.md) | {date} | {days}d{urgency} |")
        lines.append(f"")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Watchlist manager")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--update", action="store_true", help="Update tier in frontmatter")
    parser.add_argument("--auto", action="store_true", help="Output top N tickers only, one per line")
    parser.add_argument("--top", type=int, default=DEFAULT_TOP_N, help=f"Number of stocks in refresh queue (default {DEFAULT_TOP_N})")
    parser.add_argument("--add", metavar="TICKER", help="Quick-add a stock as candidate")
    parser.add_argument("--sector", help="Sector for --add (auto-detected if omitted)")
    parser.add_argument("--source", help="Source for --add (e.g., 'sector-scan', 'friend', 'news')")
    parser.add_argument("--no-save", action="store_true", help="Skip writing 0-WATCHLIST.md")
    args = parser.parse_args()

    # Quick-add mode
    if args.add:
        add_stock(args.add, sector=args.sector, source=args.source)
        return

    classified = load_and_classify()

    if args.update:
        for s in classified:
            if s.get('filepath'):
                update_frontmatter_tier(s['filepath'], s['tier'])
        print(f"Updated tier for {len(classified)} stocks.")
        return

    if args.auto:
        needs_refresh = sorted(
            [s for s in classified if s['needs_refresh']],
            key=lambda s: -s['priority_score'],
        )
        for s in needs_refresh[:args.top]:
            print(s['ticker'])
        return

    if args.json:
        output = []
        for s in classified:
            entry = {k: v for k, v in s.items() if k != 'filepath'}
            output.append(entry)
        print(json.dumps(output, indent=2))
        return

    # Terminal dashboard
    print_dashboard(classified, top_n=args.top)

    # Save 0-WATCHLIST.md and generate charts
    if not args.no_save:
        md = generate_watchlist_md(classified, top_n=max(args.top, 10))
        WATCHLIST_FILE.write_text(md, encoding="utf-8")
        print(f"\nSaved to {WATCHLIST_FILE}")

        # Regenerate interactive dashboard chart
        generate_dashboard_html(classified)


from datetime import date as _date
DASHBOARD_HTML_PATH = Path("research/stocks") / f"0-watchlist-dashboard-{_date.today().isoformat()}.html"

# Sector color palette for scatter plot
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
}


def generate_dashboard_html(classified: list[dict]):
    """Generate a single interactive HTML dashboard with tabbed charts."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        print("  ⚠ plotly not installed, skipping dashboard chart", file=sys.stderr)
        return

    date_str = datetime.now().strftime("%Y-%m-%d")
    all_stocks = [s for s in classified if s['tier'] in ('active', 'candidate', 'passive')]

    # --- Tab 1: RSI vs Fwd P/E Scatter ---
    scatter_fig = _build_scatter(all_stocks, date_str)

    # --- Tab 2: Earnings Calendar ---
    earnings_fig = _build_earnings(all_stocks, date_str)

    # --- Combine into tabbed HTML ---
    DASHBOARD_HTML_PATH.parent.mkdir(parents=True, exist_ok=True)

    scatter_html = scatter_fig.to_html(include_plotlyjs=False, full_html=False, div_id="scatter")
    earnings_html = earnings_fig.to_html(include_plotlyjs=False, full_html=False, div_id="earnings") if earnings_fig else "<p style='color:#888;padding:40px;'>No upcoming earnings found.</p>"

    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>Watchlist Dashboard — {date_str}</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
  body {{ margin:0; background:#1a1a1a; color:#fff; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }}
  .tabs {{ display:flex; gap:0; background:#111; border-bottom:2px solid #333; padding:0 20px; }}
  .tab {{ padding:12px 24px; cursor:pointer; color:#888; font-size:14px; font-weight:600;
           border-bottom:3px solid transparent; transition: all 0.2s; }}
  .tab:hover {{ color:#ccc; }}
  .tab.active {{ color:#fff; border-bottom-color:#4a9eff; }}
  .panel {{ display:none; padding:10px 20px; }}
  .panel.active {{ display:block; }}
  .guide {{ background:#111; padding:12px 20px; font-size:13px; color:#999; line-height:1.6; border-top:1px solid #333; }}
  h1 {{ margin:0; padding:16px 20px 0; font-size:22px; color:#eee; }}
  .subtitle {{ padding:0 20px 8px; font-size:13px; color:#666; }}
</style>
</head><body>
<h1>Watchlist Dashboard</h1>
<p class="subtitle">Generated {date_str} &middot; {len(all_stocks)} stocks</p>
<div class="tabs">
  <div class="tab active" onclick="showTab('scatter')">RSI vs P/E</div>
  <div class="tab" onclick="showTab('earnings')">Earnings Calendar</div>
</div>
<div id="panel-scatter" class="panel active">
  {scatter_html}
  <div class="guide">
    <b>How to read:</b> Each dot = one stock.
    <b>X-axis:</b> RSI (momentum) — left is oversold, right is overbought.
    <b>Y-axis:</b> Forward P/E (valuation) — bottom is cheap, top is expensive.
    <span style="color:#66bb6a"><b>Bottom-left</b></span> = best opportunities (oversold + cheap).
    <span style="color:#ef5350"><b>Top-right</b></span> = most stretched.
    Dot color = sector. Bigger dot = closer to entry target. Hover for details.
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
<script>
function showTab(name) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('panel-' + name).classList.add('active');
  window.dispatchEvent(new Event('resize'));  // fix plotly sizing
}}
</script>
</body></html>"""

    DASHBOARD_HTML_PATH.write_text(html, encoding="utf-8")
    print(f"Dashboard saved to {DASHBOARD_HTML_PATH}")


def _build_scatter(stocks: list[dict], date_str: str):
    """Build RSI vs Forward P/E scatter plot from classified data."""
    import plotly.graph_objects as go

    # Filter to stocks with both RSI and fwd_pe
    plottable = [s for s in stocks if s.get('rsi') is not None and s.get('fwd_pe') is not None]

    fig = go.Figure()

    # Group by GICS sector
    sector_groups = {}
    for s in plottable:
        gics = SECTOR_TO_GICS.get(s['sector'], 'Other') or 'Other'
        if gics not in sector_groups:
            sector_groups[gics] = []
        sector_groups[gics].append(s)

    for sector in sorted(sector_groups.keys()):
        ss = sector_groups[sector]
        color = SECTOR_COLORS.get(sector, "#888888")

        sizes = []
        for s in ss:
            gap = s.get('gap_pct')
            if gap is not None:
                sizes.append(max(8, min(22, 22 - abs(gap) * 0.5)))
            else:
                sizes.append(12)

        hover_texts = []
        for s in ss:
            target_str = f"${s['entry_target']}" if s.get('entry_target') else "—"
            gap_str = f"{s['gap_pct']:+.1f}%" if s.get('gap_pct') is not None else "—"
            price_str = f"${s['price']:.2f}" if s.get('price') else "—"
            conv_str = f"{s['conviction']:.1f}" if s.get('conviction') else "?"
            earn_str = f"{s['earnings_days']}d" if s.get('earnings_days') and s['earnings_days'] > 0 else "—"
            hover_texts.append(
                f"<b>{s['ticker']}</b><br>"
                f"Price: {price_str}<br>"
                f"RSI: {s['rsi']}<br>"
                f"Fwd P/E: {s['fwd_pe']:.1f}x<br>"
                f"Sector: {s['sector']}<br>"
                f"Conv: {conv_str} | Target: {target_str} | Gap: {gap_str}<br>"
                f"Earnings: {earn_str}"
            )

        fig.add_trace(go.Scatter(
            x=[s['rsi'] for s in ss],
            y=[s['fwd_pe'] for s in ss],
            mode="markers+text",
            name=sector,
            text=[s['ticker'] for s in ss],
            textposition="top center",
            textfont=dict(size=11, color="#cccccc"),
            hovertext=hover_texts,
            hoverinfo="text",
            marker=dict(size=sizes, color=color, opacity=0.85,
                        line=dict(width=1, color="#ffffff")),
        ))

    # Reference lines
    fig.add_vline(x=30, line_dash="dash", line_color="#66bb6a", line_width=1)
    fig.add_vline(x=70, line_dash="dash", line_color="#ef5350", line_width=1)
    fig.add_hline(y=25, line_dash="dash", line_color="#888888", line_width=1)

    # Quadrant labels
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
        paper_bgcolor="#1a1a1a", plot_bgcolor="#1a1a1a", font=dict(color="white"),
        hoverlabel=dict(bgcolor="#2a2a2a", bordercolor="#555555", font_size=13, font_color="white"),
    )

    return fig


def _build_earnings(stocks: list[dict], date_str: str):
    """Build earnings calendar horizontal bar chart from classified data."""
    import plotly.graph_objects as go

    today = datetime.now().date()

    # Parse earnings dates from the classified data
    entries = []
    for s in stocks:
        days = s.get('earnings_days')
        earn_str = s.get('earnings')
        if days is None or days <= 0 or earn_str is None:
            continue
        # Parse earnings string back to date
        current_year = datetime.now().year
        for fmt in ['%B %d, %Y', '%B %d', '%b %d, %Y', '%b %d']:
            try:
                dt = datetime.strptime(earn_str.strip('*'), fmt)
                if dt.year < current_year:
                    dt = dt.replace(year=current_year)
                entries.append({
                    'ticker': s['ticker'],
                    'earnings_date': dt.date(),
                    'days_until': days,
                    'sector': s.get('sector', ''),
                    'conviction': s.get('conviction'),
                })
                break
            except ValueError:
                continue

    if not entries:
        return None

    entries.sort(key=lambda e: e['earnings_date'], reverse=True)

    fig = go.Figure()

    def urgency_color(d):
        if d < 7: return "#ef5350"
        elif d < 14: return "#ffa726"
        elif d < 30: return "#ffee58"
        return "#66bb6a"

    def urgency_label(d):
        if d < 7: return "IMMINENT"
        elif d < 14: return "SOON"
        elif d < 30: return "UPCOMING"
        return "SAFE"

    for e in entries:
        earn_date = e['earnings_date']
        color = urgency_color(e['days_until'])
        conv_str = f"{e['conviction']:.1f}" if e.get('conviction') else "?"

        fig.add_trace(go.Bar(
            y=[e['ticker']], x=[(earn_date - today).days],
            base=[today.isoformat()], orientation="h",
            marker=dict(color=color, opacity=0.85, line=dict(width=0)),
            hovertemplate=(
                f"<b>{e['ticker']}</b><br>"
                f"Earnings: {earn_date.strftime('%b %d, %Y')}<br>"
                f"Days: {e['days_until']}<br>"
                f"Sector: {e['sector']}<br>"
                f"Conviction: {conv_str}<br>"
                f"Urgency: {urgency_label(e['days_until'])}"
                "<extra></extra>"
            ),
            showlegend=False,
        ))

        mid_date = today + (earn_date - today) / 2
        fig.add_annotation(
            x=mid_date.isoformat(), y=e['ticker'],
            text=f"<b>{e['days_until']}d</b>", showarrow=False,
            font=dict(color="white", size=12),
        )

    # Today line
    fig.add_shape(type="line", x0=today.isoformat(), x1=today.isoformat(),
                  y0=0, y1=1, yref="paper",
                  line=dict(color="white", width=2, dash="dash"))
    fig.add_annotation(x=today.isoformat(), y=1, yref="paper",
                       text="TODAY", showarrow=False,
                       font=dict(color="white", size=12), yshift=10)

    chart_height = max(400, len(entries) * 35 + 120)

    fig.update_layout(
        title=dict(text=f"Earnings Calendar | {date_str}", font=dict(size=18)),
        xaxis=dict(title="Date", type="date", gridcolor="#333333", tickfont=dict(color="#cccccc")),
        yaxis=dict(title="", tickfont=dict(color="#cccccc", size=13), automargin=True),
        barmode="overlay", height=chart_height,
        margin=dict(t=60, l=10, r=30, b=60),
        paper_bgcolor="#1a1a1a", plot_bgcolor="#1a1a1a", font=dict(color="white"),
    )

    return fig


if __name__ == "__main__":
    main()
