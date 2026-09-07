#!/usr/bin/env python3
"""
Cash check — validate trading plan orders against account cash balances.

Parses the latest (or specified) PLAN-*.md and all portfolio/accounts/*.md files,
aggregates planned deployments per account, and checks feasibility.

Usage:
    .venv/bin/python3 scripts/cash-check.py                        # latest plan, terminal
    .venv/bin/python3 scripts/cash-check.py --json                  # JSON output
    .venv/bin/python3 scripts/cash-check.py --plan PLAN-2026-09-06.md  # specific plan
"""

import argparse
import json
import re
import sys
from pathlib import Path

ACCOUNTS_DIR = Path("portfolio/accounts")
PLANS_DIR = Path("portfolio/plans")

# Canonical account name mapping — maps various plan references to account file names.
# Keys are lowercase; values are the canonical account_name from frontmatter.
ACCOUNT_ALIASES = {
    "roth ira": "ROTH IRA",
    "roth": "ROTH IRA",
    "hold": "HOLD",
    "thetagang": "THETAGANG",
    "theta gang": "THETAGANG",
    "tg": "THETAGANG",
    "gobig": "GOBIG",
    "go big": "GOBIG",
    "gb": "GOBIG",
    "brokeragelink": "BROKERAGELINK",
    "brokerage link": "BROKERAGELINK",
    "bl": "BROKERAGELINK",
}


def parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter values using regex (no pyyaml dependency)."""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if line.startswith("-") or line.startswith("#") or not line:
            continue
        parts = line.split(":", 1)
        if len(parts) == 2:
            key = parts[0].strip()
            val = parts[1].strip().strip('"').strip("'")
            # Try numeric conversion
            try:
                if "." in val:
                    fm[key] = float(val)
                else:
                    fm[key] = int(val)
            except ValueError:
                fm[key] = val
    return fm


def load_accounts() -> dict:
    """Load all account files, return {canonical_name: {cash, total_value, ...}}."""
    accounts = {}
    for f in ACCOUNTS_DIR.glob("*.md"):
        text = f.read_text()
        fm = parse_frontmatter(text)
        name = fm.get("account_name", f.stem.upper())
        accounts[name] = {
            "cash": fm.get("cash", 0),
            "total_value": fm.get("total_value", 0),
            "file": str(f),
        }
    return accounts


def resolve_account(raw: str) -> str:
    """Resolve a raw account name string to canonical account name."""
    cleaned = raw.strip()
    key = cleaned.lower()
    if key in ACCOUNT_ALIASES:
        return ACCOUNT_ALIASES[key]
    # Try substring match
    for alias, canonical in ACCOUNT_ALIASES.items():
        if alias in key or key in alias:
            return canonical
    return cleaned.upper()


def parse_dollar_amounts(text: str) -> list:
    """Extract all dollar amounts from text. Returns list of (value, position) tuples.

    Handles: $X, ~$X, $X,XXX, $X.XX, $XK, $X-YK (range with K suffix).
    """
    amounts = []
    for m in re.finditer(r"~?\$([\d,]+(?:\.\d+)?)\s*([Kk])?", text):
        num_str = m.group(1).replace(",", "")
        try:
            val = float(num_str)
        except ValueError:
            continue
        if m.group(2):  # K suffix
            val *= 1000
        amounts.append((val, m.start()))
    return amounts


def parse_total_cost(detail: str) -> float:
    """Parse total cost from an order Detail column.

    Priority:
    1. Explicit "Total ~$X" pattern
    2. "Collateral ~$XK" pattern (for CSPs)
    3. "Est. cost ~$X-$YK" range (take midpoint)
    4. "N shares ~$X" or "N share ~$X" (single item cost)
    5. Fallback: largest dollar amount
    """
    # 1. Look for explicit total pattern
    total_m = re.search(r"[Tt]otal\s*~?\$([\d,]+(?:\.\d+)?)\s*([Kk])?", detail)
    if total_m:
        val = float(total_m.group(1).replace(",", ""))
        if total_m.group(2):
            val *= 1000
        return val

    # 2. Look for collateral pattern (for CSPs)
    coll_m = re.search(r"[Cc]ollateral\s*~?\$([\d,]+(?:\.\d+)?)\s*([Kk])?", detail)
    if coll_m:
        val = float(coll_m.group(1).replace(",", ""))
        if coll_m.group(2):
            val *= 1000
        return val

    # 3. Look for "Est. cost ~$X-$YK" or "~$X-$Y cost" range — take midpoint
    est_m = re.search(
        r"(?:[Ee]st\.?\s*(?:cost|premium)\s*~?\$([\d,]+(?:\.\d+)?)\s*-\s*\$?([\d,]+(?:\.\d+)?)\s*([Kk])?)"
        r"|(?:~\$([\d,]+(?:\.\d+)?)\s*-\s*\$?([\d,]+(?:\.\d+)?)\s*([Kk])?\s*(?:cost|premium))",
        detail
    )
    if est_m:
        if est_m.group(1):
            lo = float(est_m.group(1).replace(",", ""))
            hi = float(est_m.group(2).replace(",", ""))
            k = est_m.group(3)
        else:
            lo = float(est_m.group(4).replace(",", ""))
            hi = float(est_m.group(5).replace(",", ""))
            k = est_m.group(6)
        if k:
            lo *= 1000
            hi *= 1000
        return (lo + hi) / 2

    # 4. Look for "N share(s) ~$X" or "N share(s) @ $X" (single item with price)
    share_m = re.search(r"(\d+)\s+shares?\s*(?:~|at\s*(?:or\s*below\s*)?)\$?([\d,]+(?:\.\d+)?)", detail)
    if share_m:
        count = int(share_m.group(1))
        price = float(share_m.group(2).replace(",", ""))
        return count * price

    # 5. Fallback: largest dollar amount that looks like a cost (not a strike price / other ref)
    amounts = parse_dollar_amounts(detail)
    if amounts:
        return max(a[0] for a in amounts)

    return 0


def classify_order(order_text: str, type_text: str, detail: str) -> str:
    """Classify an order as 'limit', 'csp', 'leap', 'cc', 'dca', 'stop', or 'other'."""
    combined = (order_text + " " + type_text + " " + detail).lower()

    # Non-cash-deployment actions first
    if "trailing stop" in combined or "stop loss" in combined or "set trailing" in combined:
        return "stop"
    if "let assign" in combined or "let expire" in combined or "let ride" in combined:
        return "assignment"
    if "modify dca" in combined or ("slow" in combined and "dca" in combined):
        return "dca_modify"
    if "pause" in combined and "dca" in combined:
        return "dca_modify"
    if "dca" in combined or "recurring" in combined:
        return "dca"
    if ("csp" in combined or
            ("sell to open" in combined and ("put" in combined or re.search(r"\d+p\b", combined)))):
        return "csp"
    if "cc" in combined or "covered call" in combined:
        return "cc"
    if "sell" in order_text.lower() and "to open" not in type_text.lower():
        # Selling shares (e.g., "Sell GLD", "Trim U") — generates cash, not a deployment
        return "sell"
    if "trim" in order_text.lower():
        return "sell"
    if "leap" in combined or "buy to open" in combined:
        return "leap"
    if "limit" in combined or "gtc" in combined:
        return "limit"
    if "market" in type_text.lower() or "buy" in order_text.lower():
        return "limit"  # Market buys treated as limit for cash purposes
    return "other"


def is_deferred(order_text: str, detail: str) -> bool:
    """Check if an order is deferred / struck through / contingent."""
    combined = order_text + " " + detail
    if "~~" in combined:
        return True
    if re.search(r"DEFERRED|CONTINGENT|After\s+(Oct|Nov|Dec|Jan|Feb|Mar|Sep)", combined, re.IGNORECASE):
        return True
    return False


def parse_one_time_orders(plan_text: str) -> list:
    """Parse the One-Time Orders table from a plan file."""
    orders = []

    # Find the One-Time Orders section
    section_m = re.search(r"##\s*One-Time Orders.*?\n(.*?)(?=\n##\s|\n---|\Z)", plan_text, re.DOTALL)
    if not section_m:
        return orders

    section = section_m.group(1)

    # Find table rows (skip header and separator)
    lines = section.strip().splitlines()
    in_table = False
    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            in_table = False
            continue
        # Skip header separator
        if re.match(r"\|[\s\-|]+\|", line):
            in_table = True
            continue
        if not in_table:
            # Could be the header row
            if "#" in line.split("|")[1] if len(line.split("|")) > 1 else False:
                continue
            in_table = True
            continue

        cols = [c.strip() for c in line.split("|")]
        # Remove empty first/last from split
        cols = [c for c in cols if c != ""]

        if len(cols) < 6:
            continue

        # Columns: #, Order, Type, Account, Detail, Rationale, [Deadline]
        order_num = cols[0]
        order_text = cols[1]
        order_type = cols[2]
        account_raw = cols[3]
        detail = cols[4]
        rationale = cols[5] if len(cols) > 5 else ""

        # Skip deferred/struck-through orders
        if is_deferred(order_text, detail):
            continue

        account = resolve_account(account_raw)
        cost = parse_total_cost(detail)
        kind = classify_order(order_text, order_type, detail)

        # Skip non-deployment order types
        # CCs: premium is income, not a cost
        # DCA: handled in DCA schedule section
        # Stops: trailing/stop-loss orders don't deploy cash
        # DCA modifications: pace changes, not new cash
        # Sells: selling shares generates cash, not a deployment
        # Assignments: letting options expire/assign — no new cash needed
        if kind in ("cc", "dca", "stop", "dca_modify", "sell", "assignment"):
            continue

        orders.append({
            "num": order_num,
            "description": re.sub(r"\*\*", "", order_text).strip(),
            "type": order_type,
            "account": account,
            "detail": detail,
            "cost": cost,
            "kind": kind,
        })

    return orders


def parse_dca_schedule(plan_text: str) -> list:
    """Parse DCA schedule sections from a plan file.

    Handles two formats:
    - "### Account Name — $X/day" (multiple sub-sections)
    - "## DCA Schedule (Account — $X/day)" (single section with parenthesized account)

    Returns list of {account, ticker, daily, description}.
    """
    dcas = []

    # Pattern 1: ### Account Name — $X/day (or — PAUSED)
    sections = list(re.finditer(
        r"###\s+(.*?)\s*[—–-]\s*(?:PAUSED|\$(\d+)/day).*?\n(.*?)(?=\n###\s|\n---|\n##\s|\Z)",
        plan_text, re.DOTALL
    ))

    # Pattern 2: ## DCA Schedule (Account — $X/day)
    alt_sections = re.finditer(
        r"##\s+DCA Schedule\s*\(([^)]*?)\s*[—–-]\s*\$(\d+)/day\).*?\n(.*?)(?=\n---|\n##\s|\Z)",
        plan_text, re.DOTALL
    )
    for alt in alt_sections:
        sections.append(alt)

    for sec in sections:
        account_raw = sec.group(1).strip()
        daily_total = int(sec.group(2)) if sec.group(2) else 0
        body = sec.group(3)

        if daily_total == 0:
            continue

        account = resolve_account(account_raw)

        # Parse the table within this section
        lines = body.strip().splitlines()
        in_table = False
        for line in lines:
            line = line.strip()
            if not line.startswith("|"):
                continue
            if re.match(r"\|[\s\-|]+\|", line):
                in_table = True
                continue
            if not in_table:
                in_table = True
                continue

            cols = [c.strip() for c in line.split("|")]
            cols = [c for c in cols if c != ""]

            if len(cols) < 4:
                continue

            ticker = re.sub(r"\*\*", "", cols[0]).strip()

            # Skip totals row
            if ticker.lower() in ("total", ""):
                continue

            # Skip struck-through / paused entries
            if ticker.startswith("~~") or "PAUSED" in line.upper() or "$0" in cols[3]:
                continue

            # Parse proposed $/day column (usually col index 3)
            daily_match = re.search(r"\$(\d+)", cols[3])
            daily = int(daily_match.group(1)) if daily_match else 0

            if daily > 0:
                dcas.append({
                    "account": account,
                    "ticker": ticker,
                    "daily": daily,
                    "description": f"{ticker} ${daily}/d",
                })

    return dcas


def parse_leap_orders(orders: list) -> list:
    """Filter LEAP orders from one-time orders."""
    return [o for o in orders if o["kind"] == "leap"]


def find_latest_plan() -> Path:
    """Find the most recent PLAN-*.md file."""
    plans = sorted(PLANS_DIR.glob("PLAN-*.md"))
    if not plans:
        print("ERROR: No PLAN-*.md files found in portfolio/plans/", file=sys.stderr)
        sys.exit(1)
    return plans[-1]


def build_account_summary(accounts: dict, orders: list, dcas: list) -> list:
    """Build per-account deployment summary."""
    summaries = {}

    # Initialize from accounts
    for name, acct in accounts.items():
        summaries[name] = {
            "name": name,
            "cash": acct["cash"],
            "total_value": acct["total_value"],
            "dca_items": [],
            "dca_daily": 0,
            "dca_monthly": 0,
            "limit_orders": [],
            "limit_total": 0,
            "leap_orders": [],
            "leap_total": 0,
            "csp_collateral": 0,
            "csp_items": [],
        }

    # Aggregate DCA
    for dca in dcas:
        acct = dca["account"]
        if acct not in summaries:
            continue
        summaries[acct]["dca_items"].append(dca["description"])
        summaries[acct]["dca_daily"] += dca["daily"]

    # Calculate monthly DCA (5 days/week × 4 weeks)
    for s in summaries.values():
        s["dca_monthly"] = s["dca_daily"] * 5 * 4  # 20 trading days

    # Aggregate orders
    for order in orders:
        acct = order["account"]
        if acct not in summaries:
            continue

        if order["kind"] == "csp":
            summaries[acct]["csp_collateral"] += order["cost"]
            summaries[acct]["csp_items"].append(order["description"])
        elif order["kind"] == "leap":
            summaries[acct]["leap_orders"].append(order)
            summaries[acct]["leap_total"] += order["cost"]
        else:
            summaries[acct]["limit_orders"].append(order)
            summaries[acct]["limit_total"] += order["cost"]

    # Calculate remaining and status
    for s in summaries.values():
        total_committed = s["dca_monthly"] + s["limit_total"] + s["leap_total"]
        # CSP collateral is reserved but not consumed — show separately
        remaining = s["cash"] - total_committed
        remaining_pct = (remaining / s["cash"] * 100) if s["cash"] > 0 else 0

        s["total_committed"] = total_committed
        s["remaining"] = remaining
        s["remaining_pct"] = round(remaining_pct, 1)

        # DCA runway
        weekly_dca = s["dca_daily"] * 5
        if weekly_dca > 0:
            s["dca_runway_weeks"] = int(remaining / weekly_dca) if remaining > 0 else 0
        else:
            s["dca_runway_weeks"] = None

        # Status
        if remaining < 0:
            s["status"] = "OVER-COMMITTED"
        elif remaining_pct < 15:
            s["status"] = "TIGHT"
        else:
            s["status"] = "OK"

    return list(summaries.values())


def format_money(amount: float) -> str:
    """Format a number as $X,XXX."""
    if amount < 0:
        return f"-${abs(amount):,.0f}"
    return f"${amount:,.0f}"


def status_icon(status: str) -> str:
    """Return status indicator."""
    if status == "OK":
        return "\u2705 OK"
    elif status == "TIGHT":
        return "\u26a0\ufe0f  TIGHT"
    else:
        return "\U0001f534 OVER-COMMITTED"


def print_terminal(plan_name: str, summaries: list):
    """Print terminal dashboard."""
    W = 70

    print()
    print("=" * W)
    print(f"  CASH CHECK \u2014 {plan_name}")
    print("=" * W)

    total_cash = 0
    total_committed = 0
    over_committed = 0

    # Sort: accounts with activity first, then alphabetical
    active = [s for s in summaries if s["total_committed"] > 0 or s["csp_collateral"] > 0]
    inactive = [s for s in summaries if s["total_committed"] == 0 and s["csp_collateral"] == 0]
    display = sorted(active, key=lambda x: -x["total_committed"]) + sorted(inactive, key=lambda x: x["name"])

    for s in display:
        total_cash += s["cash"]
        total_committed += s["total_committed"]
        if s["status"] == "OVER-COMMITTED":
            over_committed += 1

        print()
        print(f"  {s['name']}")
        print(f"  {'-' * (W - 4)}")

        print(f"    {'Available cash:':<26} {format_money(s['cash']):>10}")

        if s["dca_monthly"] > 0:
            dca_desc = " + ".join(s["dca_items"])
            print(f"    {'DCA (1 month):':<26} {format_money(-s['dca_monthly']):>10}  ({dca_desc})")

        if s["limit_total"] > 0:
            limit_descs = []
            for o in s["limit_orders"]:
                limit_descs.append(f"{o['description']} {format_money(o['cost'])}")
            desc_str = " + ".join(limit_descs) if len(limit_descs) <= 3 else f"{len(limit_descs)} orders"
            print(f"    {'Limit orders (if fill):':<26} {format_money(-s['limit_total']):>10}  ({desc_str})")

        if s["leap_total"] > 0:
            leap_descs = []
            for o in s["leap_orders"]:
                leap_descs.append(f"{o['description']} {format_money(o['cost'])}")
            desc_str = " + ".join(leap_descs)
            print(f"    {'LEAP purchases:':<26} {format_money(-s['leap_total']):>10}  ({desc_str})")

        if s["csp_collateral"] > 0:
            csp_desc = " + ".join(s["csp_items"])
            print(f"    {'CSP collateral:':<26} {format_money(s['csp_collateral']):>10}  ({csp_desc}) [reserved, not consumed]")
        elif s["total_committed"] > 0:
            print(f"    {'CSP collateral:':<26} {'$0':>10}  (none active)")

        if s["total_committed"] > 0 or s["csp_collateral"] > 0:
            print(f"  {'-' * (W - 4)}")
            pct_str = f"({s['remaining_pct']}%)"
            print(f"    {'Remaining:':<26} {format_money(s['remaining']):>10}  {pct_str:<12} {status_icon(s['status'])}")

            if s["dca_runway_weeks"] is not None:
                print(f"    {'DCA runway:':<26} {s['dca_runway_weeks']} weeks")

            # Warn about CSP collateral impact
            if s["csp_collateral"] > 0:
                remaining_with_csp = s["remaining"] - s["csp_collateral"]
                pct_with_csp = (remaining_with_csp / s["cash"] * 100) if s["cash"] > 0 else 0
                if remaining_with_csp < 0:
                    print(f"    {'If CSPs assigned:':<26} {format_money(remaining_with_csp):>10}  ({pct_with_csp:.1f}%)   \U0001f534 NEGATIVE")
                elif pct_with_csp < 15:
                    print(f"    {'If CSPs assigned:':<26} {format_money(remaining_with_csp):>10}  ({pct_with_csp:.1f}%)   \u26a0\ufe0f  TIGHT")
        else:
            print(f"    {'Planned deployment:':<26} {'$0':>10}  (no orders this plan)")

    # Summary
    total_remaining = total_cash - total_committed
    total_pct = (total_remaining / total_cash * 100) if total_cash > 0 else 0

    print()
    print(f"  SUMMARY")
    print(f"  {'-' * (W - 4)}")
    print(f"    {'Total cash:':<26} {format_money(total_cash):>10}")
    print(f"    {'Total committed:':<26} {format_money(total_committed):>10}")
    print(f"    {'Total remaining:':<26} {format_money(total_remaining):>10}  ({total_pct:.1f}%)")
    print(f"    {'Over-committed accounts:':<26} {over_committed}")
    print("=" * W)
    print()


def build_json(plan_name: str, summaries: list) -> dict:
    """Build JSON output."""
    total_cash = sum(s["cash"] for s in summaries)
    total_committed = sum(s["total_committed"] for s in summaries)
    total_remaining = total_cash - total_committed

    accounts_json = []
    for s in summaries:
        entry = {
            "name": s["name"],
            "cash": s["cash"],
            "dca_monthly": s["dca_monthly"],
            "limit_orders": s["limit_total"],
            "leap_purchases": s["leap_total"],
            "csp_collateral": s["csp_collateral"],
            "total_committed": s["total_committed"],
            "remaining": s["remaining"],
            "remaining_pct": s["remaining_pct"],
            "status": s["status"],
        }
        if s["dca_runway_weeks"] is not None:
            entry["dca_runway_weeks"] = s["dca_runway_weeks"]
        if s["dca_items"]:
            entry["dca_detail"] = s["dca_items"]
        if s["limit_orders"]:
            entry["limit_detail"] = [
                {"description": o["description"], "cost": o["cost"]}
                for o in s["limit_orders"]
            ]
        if s["leap_orders"]:
            entry["leap_detail"] = [
                {"description": o["description"], "cost": o["cost"]}
                for o in s["leap_orders"]
            ]
        if s["csp_items"]:
            entry["csp_detail"] = s["csp_items"]
        accounts_json.append(entry)

    over_committed = sum(1 for s in summaries if s["status"] == "OVER-COMMITTED")

    return {
        "plan_file": plan_name,
        "accounts": sorted(accounts_json, key=lambda x: -x["total_committed"]),
        "summary": {
            "total_cash": total_cash,
            "total_committed": total_committed,
            "total_remaining": total_remaining,
            "remaining_pct": round(total_remaining / total_cash * 100, 1) if total_cash > 0 else 0,
            "over_committed": over_committed,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Cash check — validate plan orders against account cash")
    parser.add_argument("--plan", help="Specific plan file (e.g., PLAN-2026-09-06.md)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    # Find plan file
    if args.plan:
        plan_path = PLANS_DIR / args.plan
        if not plan_path.exists():
            # Try without directory
            plan_path = Path(args.plan)
        if not plan_path.exists():
            print(f"ERROR: Plan file not found: {args.plan}", file=sys.stderr)
            sys.exit(1)
    else:
        plan_path = find_latest_plan()

    plan_name = plan_path.stem
    plan_text = plan_path.read_text()

    # Load accounts
    accounts = load_accounts()
    if not accounts:
        print("ERROR: No account files found in portfolio/accounts/", file=sys.stderr)
        sys.exit(1)

    # Parse plan
    orders = parse_one_time_orders(plan_text)
    dcas = parse_dca_schedule(plan_text)

    # Build summaries
    summaries = build_account_summary(accounts, orders, dcas)

    # Output
    if args.json:
        result = build_json(plan_name, summaries)
        print(json.dumps(result, indent=2))
    else:
        print_terminal(plan_name, summaries)


if __name__ == "__main__":
    main()
