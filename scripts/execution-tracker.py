#!/usr/bin/env python3
"""
Execution tracker — compare a trading plan's orders against current account state.

Reads PLAN-*.md and portfolio/accounts/*.md, determines which orders were executed,
tracks carry-forwards across plans, and calculates execution rate.

Usage:
    .venv/bin/python3 scripts/execution-tracker.py                          # latest plan vs accounts
    .venv/bin/python3 scripts/execution-tracker.py --plan PLAN-2026-09-06.md  # specific plan
    .venv/bin/python3 scripts/execution-tracker.py --json                    # JSON output
"""

import argparse
import json
import re
import sys
from pathlib import Path

PLANS_DIR = Path("portfolio/plans")
ACCOUNTS_DIR = Path("portfolio/accounts")

# Canonical account name mapping (case-insensitive, handles variations)
ACCOUNT_ALIASES = {
    "hold": "HOLD",
    "thetagang": "THETAGANG",
    "theta gang": "THETAGANG",
    "tg": "THETAGANG",
    "roth ira": "ROTH IRA",
    "roth": "ROTH IRA",
    "brokeragelink": "BROKERAGELINK",
    "brokerage link": "BROKERAGELINK",
    "bl": "BROKERAGELINK",
    "gobig": "GOBIG",
    "go big": "GOBIG",
    "gb": "GOBIG",
}

# Account file mapping (canonical name → filename)
ACCOUNT_FILES = {
    "HOLD": "hold.md",
    "THETAGANG": "thetagang.md",
    "ROTH IRA": "roth-ira.md",
    "BROKERAGELINK": "brokeragelink.md",
    "GOBIG": "gobig.md",
}

# Status constants
DONE = "DONE"
NOT_DONE = "NOT DONE"
PARTIAL = "PARTIAL"
CARRY_FORWARD = "CARRY-FORWARD"
DEFERRED = "DEFERRED"
UNVERIFIABLE = "UNVERIFIABLE"

STATUS_EMOJI = {
    DONE: "\u2705",
    NOT_DONE: "\u274c",
    PARTIAL: "\u26a0\ufe0f",
    CARRY_FORWARD: "\U0001f504",
    DEFERRED: "\u23ed\ufe0f",
    UNVERIFIABLE: "\u2753",
}


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def normalize_account(name: str) -> str:
    """Map any account name variation to canonical form."""
    if not name:
        return ""
    key = name.strip().lower()
    return ACCOUNT_ALIASES.get(key, name.strip().upper())


def get_plan_files() -> list[Path]:
    """Return PLAN-*.md files sorted by date (oldest first)."""
    plans = sorted(PLANS_DIR.glob("PLAN-*.md"))
    return plans


def parse_plan_date(path: Path) -> str:
    """Extract date string from PLAN-YYYY-MM-DD.md filename."""
    m = re.search(r"PLAN-(\d{4}-\d{2}-\d{2})", path.name)
    return m.group(1) if m else ""


def parse_markdown_table(text: str) -> list[dict]:
    """Parse a markdown table into a list of dicts.

    Handles standard | col1 | col2 | format. Skips the separator row (---|---).
    """
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    if len(lines) < 2:
        return []

    # Find header row (first line with pipes)
    header_line = None
    data_start = 0
    for i, line in enumerate(lines):
        if "|" in line:
            header_line = line
            data_start = i + 1
            break
    if not header_line:
        return []

    headers = [h.strip() for h in header_line.split("|") if h.strip()]

    rows = []
    for line in lines[data_start:]:
        if not line.strip() or not "|" in line:
            continue
        # Skip separator rows
        if re.match(r"^[\s|:-]+$", line):
            continue
        cells = [c.strip() for c in line.split("|") if c.strip() != ""]
        # If row has fewer cells than headers, pad with empty strings
        while len(cells) < len(headers):
            cells.append("")
        row = {}
        for j, h in enumerate(headers):
            row[h] = cells[j] if j < len(cells) else ""
        rows.append(row)
    return rows


def extract_one_time_orders_section(text: str) -> str:
    """Extract the One-Time Orders table section from a plan."""
    # Look for "## One-Time Orders" heading
    pattern = r"##\s+One-Time Orders.*?\n(.*?)(?=\n---|\n##|\Z)"
    m = re.search(pattern, text, re.DOTALL)
    return m.group(1).strip() if m else ""


def extract_one_time_orders_table(text: str) -> str:
    """Extract just the markdown table from the One-Time Orders section."""
    section = extract_one_time_orders_section(text)
    if not section:
        return ""
    # Find the table (starts with | # | or similar)
    lines = section.split("\n")
    table_lines = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and not in_table:
            in_table = True
        if in_table:
            if stripped.startswith("|"):
                table_lines.append(stripped)
            elif stripped == "":
                continue  # skip blank lines within table area
            else:
                break  # end of table
    return "\n".join(table_lines)


def parse_order(row: dict) -> dict | None:
    """Parse a single order row into a structured order dict.

    Returns None for deferred/cancelled orders.
    """
    # Get the order description — try common column names
    order_text = ""
    for key in ["Order", "order"]:
        if key in row:
            order_text = row[key]
            break
    if not order_text:
        # Try first non-# column
        for k, v in row.items():
            if k.strip() != "#":
                order_text = v
                break

    # Get order number
    num = row.get("#", "").strip()

    # Get account
    account_text = row.get("Account", row.get("account", "")).strip()
    account = normalize_account(account_text)

    # Get type
    order_type = row.get("Type", row.get("type", "")).strip()

    # Get detail
    detail = row.get("Detail", row.get("detail", "")).strip()

    # Get rationale
    rationale = row.get("Rationale", row.get("rationale", "")).strip()

    # Check if deferred/cancelled (strikethrough or DEFERRED keyword or CONTINGENT)
    is_deferred = False
    raw_order = order_text
    if "~~" in order_text or "DEFERRED" in order_text.upper() or "DEFERRED" in detail.upper():
        is_deferred = True
    if "CONTINGENT" in detail.upper() or "CONTINGENT" in order_text.upper():
        is_deferred = True
    if "~~" in order_type or "~~" in account_text:
        is_deferred = True
    # Also check if the # column is struck through
    if "~~" in num:
        is_deferred = True

    # Clean strikethrough markers for display
    clean_order = re.sub(r"~~(.*?)~~", r"\1", order_text)
    clean_order = re.sub(r"\*\*(.*?)\*\*", r"\1", clean_order).strip()

    # Classify the order type
    order_class = classify_order(clean_order, order_type, detail)

    # Extract ticker(s) — prefer order text only; use detail as fallback
    tickers = extract_tickers(clean_order, "")
    if not tickers:
        tickers = extract_tickers(clean_order, detail)

    # Extract option details if applicable
    option_info = extract_option_info(clean_order, detail)

    return {
        "num": num.replace("~~", "").strip(),
        "raw": raw_order,
        "order": clean_order,
        "type": order_type,
        "account": account,
        "detail": detail,
        "rationale": rationale,
        "deferred": is_deferred,
        "order_class": order_class,
        "tickers": tickers,
        "option_info": option_info,
    }


def classify_order(order: str, order_type: str, detail: str) -> str:
    """Classify order into a category for execution checking."""
    text = f"{order} {order_type} {detail}".lower()

    if "sell to open" in text or "sell cc" in text or "sell ccs" in text:
        if "put" in text or " p " in text or re.search(r"\$\d+p\b", text):
            return "sell_csp"
        return "sell_cc"
    if "csp" in text or "sell.*put" in re.sub(r"\s+", " ", text):
        return "sell_csp"
    if "buy to open" in text or "leap" in text.lower():
        return "buy_leap"
    if "buy to close" in text or "close" in text:
        return "close_option"
    if "let assign" in text or "let expire" in text or "accept assignment" in text:
        return "let_expire"
    if "trailing stop" in text or "stop" in text:
        return "set_stop"
    if "start" in text and "dca" in text:
        return "start_dca"
    if ("modify" in text or "slow" in text or "reduce" in text or "pause" in text
            or "cut" in text or "adjust" in text or "increase" in text) and "dca" in text:
        return "modify_dca"
    if "dca" in text and "recurring" in order_type.lower():
        return "start_dca"
    if "recurring buy" in text or "recurring" in order_type.lower():
        return "start_dca"
    if "sell" in text and ("share" in text or "market" in text or "trim" in text):
        return "sell_shares"
    if "buy" in text and ("share" in text or "market" in text):
        return "buy_shares"
    if "limit" in text and "buy" in text:
        return "buy_shares"
    if "limit" in text and "sell" in text:
        return "sell_shares"
    if "place" in text and "limit" in text:
        return "buy_shares"
    if "gtc" in order_type.lower() and "limit" in order_type.lower():
        return "buy_shares"
    if "set" in text and "limit" in text and "order" in text:
        return "buy_shares"

    # Fallback — try to guess from order text
    if "sell" in order.lower():
        return "sell_shares"
    if "buy" in order.lower() or "place" in order.lower() or "set" in order.lower():
        return "buy_shares"

    return "unknown"


def extract_tickers(order: str, detail: str) -> list[str]:
    """Extract stock tickers from order text."""
    tickers = []
    text = f"{order} {detail}"
    # Exclude common abbreviations that aren't tickers
    exclude = {
        "DCA", "CC", "CCS", "CSP", "GTC", "RSI", "OTM", "ITM", "ATR", "SMA",
        "DTE", "EST", "OB", "NEW", "SELL", "BUY", "SET", "START", "HOLD",
        "SKIP", "CARRY", "FORWARD", "DEAD", "DONE", "NOT", "STILL", "THE",
        "ALL", "BOTH", "MORE", "CLOSE", "OPEN", "PLACE", "LIMIT", "MARKET",
        "SLOW", "STOP", "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN",
        "MODIFY", "PAUSE", "REDUCE", "TRIM", "TOTAL", "WEEKS", "DAYS",
        "DEFERRED", "CONTINGENT", "SHARES", "SHARE", "LEAP", "LEAPS",
        "IV", "PE", "ATH", "EPS", "YOY", "WOW", "QOQ", "FOMC", "CPI",
        "SEC", "DOJ", "IPO", "ETF", "BPR", "FIFO", "MS", "VS", "OK",
        "IF", "OR", "ON", "AT", "TO", "IN", "OF", "BE", "DO", "IS",
        "IT", "NO", "SO", "UP", "BY", "FOR", "AND", "THE", "THIS",
        "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP",
        "OCT", "NOV", "DEC",
    }
    # Known single-letter tickers
    single_letter_tickers = {"U", "X", "F", "T", "V"}

    # Look for single-letter tickers explicitly (they need special handling)
    # Match "N U shares" or "SELL U" or similar patterns
    for ticker in single_letter_tickers:
        if re.search(rf"\b{ticker}\b", text):
            # Check it's used as a ticker (near "shares", "sell", "buy", etc.)
            if re.search(rf"(?:sell|buy|trim|add|start)\s+(?:\d+\s+)?{ticker}\b", text, re.IGNORECASE):
                tickers.append(ticker)
            elif re.search(rf"\b{ticker}\s+(?:shares|stock)", text, re.IGNORECASE):
                tickers.append(ticker)

    # Look for multi-letter ticker symbols (2-5 uppercase letters)
    matches = re.findall(r"\b([A-Z]{2,5})\b", text)
    for m in matches:
        if m not in exclude and m not in tickers:
            tickers.append(m)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for t in tickers:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique


def extract_option_info(order: str, detail: str) -> dict | None:
    """Extract option strike, expiry, and type from order text."""
    text = f"{order} {detail}"

    info = {}

    # Look for strike price pattern: $NNN or $NNN.NN followed by C or P
    strike_match = re.search(r"\$(\d+(?:\.\d+)?)\s*([CP])\b", text)
    if strike_match:
        info["strike"] = float(strike_match.group(1))
        info["type"] = "call" if strike_match.group(2) == "C" else "put"

    # Also look for patterns like "$390C" or "$250P"
    if not strike_match:
        strike_match2 = re.search(r"\$(\d+(?:\.\d+)?)([CP])", text)
        if strike_match2:
            info["strike"] = float(strike_match2.group(1))
            info["type"] = "call" if strike_match2.group(2) == "C" else "put"

    # Look for expiry: "Oct 16", "Sep 18", "Jan 2028", etc.
    expiry_match = re.search(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}(?:,?\s*\d{4})?)",
        text
    )
    if expiry_match:
        info["expiry_str"] = expiry_match.group(0).strip()

    # Look for contract count: "3x", "2x", "1x", "1 contract"
    count_match = re.search(r"(\d+)\s*x\b", text)
    if count_match:
        info["contracts"] = int(count_match.group(1))
    else:
        count_match2 = re.search(r"(\d+)\s+contract", text)
        if count_match2:
            info["contracts"] = int(count_match2.group(1))

    return info if info else None


# ---------------------------------------------------------------------------
# Account parsing
# ---------------------------------------------------------------------------

def parse_account_file(path: Path) -> dict:
    """Parse an account .md file into a structured dict."""
    text = path.read_text()

    account = {
        "name": "",
        "cash": 0,
        "total_value": 0,
        "positions": {},      # ticker → {shares, cost_basis, current_value, ...}
        "options": [],        # list of option positions
        "constraints": "",    # raw constraints text
        "raw": text,
    }

    # Parse frontmatter
    fm_match = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        for line in fm.split("\n"):
            line = line.strip()
            if line.startswith("account_name:"):
                account["name"] = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("cash:"):
                try:
                    account["cash"] = float(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith("total_value:"):
                try:
                    account["total_value"] = float(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
        # Get constraints block
        constraints_match = re.search(r"constraints:\s*\n((?:\s+-.*\n)*)", fm)
        if constraints_match:
            account["constraints"] = constraints_match.group(1)

    # Parse position tables — find all markdown tables with Ticker/Option column
    # Split into sections by ## headers
    sections = re.split(r"\n(?=##)", text)

    for section in sections:
        header = section.split("\n")[0].strip()

        # Skip non-position sections
        if any(skip in header.lower() for skip in ["flag", "review", "cadence", "rotation", "lesson", "closed"]):
            continue

        # Find tables in this section
        table_text = extract_tables_from_section(section)
        for table in table_text:
            rows = parse_markdown_table(table)
            for row in rows:
                # Position rows (shares)
                if "Ticker" in row and "Shares" in row:
                    ticker = clean_ticker(row.get("Ticker", ""))
                    if not ticker:
                        continue
                    shares = parse_number(row.get("Shares", "0"))
                    cost = parse_number(row.get("Cost Basis", row.get("Cost/Share", "0")))
                    value = parse_number(row.get("Current Value", "0"))

                    if ticker in account["positions"]:
                        # Merge (e.g., same ticker in multiple tables)
                        account["positions"][ticker]["shares"] += shares
                        account["positions"][ticker]["current_value"] += value
                    else:
                        account["positions"][ticker] = {
                            "shares": shares,
                            "cost_basis": cost,
                            "current_value": value,
                            "notes": row.get("Notes", ""),
                            "dca": row.get("DCA Amount", ""),
                        }

                # Options rows
                if "Option" in row or "Strike" in row:
                    opt = parse_option_row(row)
                    if opt:
                        account["options"].append(opt)

    return account


def extract_tables_from_section(section: str) -> list[str]:
    """Extract markdown table blocks from a section."""
    tables = []
    lines = section.split("\n")
    current_table = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and "|" in stripped[1:]:
            in_table = True
            current_table.append(stripped)
        else:
            if in_table and current_table:
                tables.append("\n".join(current_table))
                current_table = []
                in_table = False
    if current_table:
        tables.append("\n".join(current_table))
    return tables


def clean_ticker(text: str) -> str:
    """Clean a ticker cell value."""
    # Remove bold markers, links, etc.
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"~~(.*?)~~", r"\1", text)
    text = text.strip()
    # Extract just the ticker symbol
    m = re.match(r"([A-Z]{1,5})", text)
    return m.group(1) if m else ""


def parse_number(text: str) -> float:
    """Parse a number from text, handling $, commas, ~, etc."""
    if not text:
        return 0.0
    text = re.sub(r"[~$,]", "", text)
    text = text.strip()
    # Handle fractional shares like "90.15"
    m = re.match(r"(-?[\d.]+)", text)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return 0.0
    return 0.0


def parse_option_row(row: dict) -> dict | None:
    """Parse an option position row."""
    # Handle rows with "Option" column (e.g., "NOW $150 Call (bought)")
    option_text = row.get("Option", "")
    if not option_text:
        # Try Strike-based format
        strike = row.get("Strike", "")
        if not strike:
            return None
        expiry = row.get("Expiry", "")
        contracts = row.get("Contracts", "")
        status = row.get("Status", "")
        return {
            "raw": f"{strike} {expiry}",
            "strike": parse_number(strike),
            "expiry": expiry,
            "contracts": contracts,
            "status": status,
            "ticker": clean_ticker(strike) if re.search(r"[A-Z]", strike) else "",
            "type": "put" if "P" in strike or "put" in status.lower() else "call",
            "direction": "short" if contracts.startswith("-") else "long",
        }

    # Parse "NOW $150 Call (bought)" or "IGV $110 Call" format
    m = re.match(r"([A-Z]{1,5})\s+\$(\d+(?:\.\d+)?)\s+(Call|Put)(?:\s+\((bought|sold)\))?", option_text)
    if m:
        return {
            "raw": option_text,
            "ticker": m.group(1),
            "strike": float(m.group(2)),
            "type": "call" if m.group(3) == "Call" else "put",
            "direction": "long" if m.group(4) == "bought" else ("short" if m.group(4) == "sold" else "long"),
            "expiry": row.get("Expiry", ""),
            "contracts": row.get("Contracts", ""),
            "status": row.get("Status", ""),
            "current_value": row.get("Current Value", row.get("Current value", "")),
        }

    # Try to parse "CRCL $83" style (from CSP tables)
    m2 = re.match(r"([A-Z]{1,5})\s+\$(\d+(?:\.\d+)?)", option_text)
    if m2:
        return {
            "raw": option_text,
            "ticker": m2.group(1),
            "strike": float(m2.group(2)),
            "type": "put" if "P" in row.get("Status", "") or "put" in option_text.lower() else "call",
            "direction": "short",
            "expiry": row.get("Expiry", ""),
            "contracts": row.get("Contracts", ""),
            "status": row.get("Status", ""),
        }

    return None


def load_accounts() -> dict[str, dict]:
    """Load all account files. Returns {canonical_name: parsed_account}."""
    accounts = {}
    for name, filename in ACCOUNT_FILES.items():
        path = ACCOUNTS_DIR / filename
        if path.exists():
            accounts[name] = parse_account_file(path)
    return accounts


# ---------------------------------------------------------------------------
# Execution checking
# ---------------------------------------------------------------------------

def check_order_execution(order: dict, accounts: dict) -> tuple[str, str]:
    """Check if an order was executed.

    Returns (status, notes).
    """
    if order["deferred"]:
        return DEFERRED, ""

    acct_name = order["account"]
    acct = accounts.get(acct_name)

    order_class = order["order_class"]
    tickers = order["tickers"]
    option_info = order["option_info"]

    if order_class == "sell_cc":
        return check_sell_cc(order, acct, accounts)
    elif order_class == "sell_csp":
        return check_sell_csp(order, acct, accounts)
    elif order_class == "buy_leap":
        return check_buy_leap(order, acct, accounts)
    elif order_class == "close_option":
        return check_close_option(order, acct, accounts)
    elif order_class == "let_expire":
        return check_let_expire(order, acct, accounts)
    elif order_class == "set_stop":
        return UNVERIFIABLE, "Can't verify stop orders from account file"
    elif order_class == "start_dca":
        return check_start_dca(order, acct, accounts)
    elif order_class == "modify_dca":
        return check_modify_dca(order, acct, accounts)
    elif order_class == "sell_shares":
        return check_sell_shares(order, acct, accounts)
    elif order_class == "buy_shares":
        return check_buy_shares(order, acct, accounts)
    else:
        return UNVERIFIABLE, f"Unknown order class: {order_class}"


def check_sell_cc(order: dict, acct: dict | None, accounts: dict) -> tuple[str, str]:
    """Check if a CC was sold — look for matching active CC in account."""
    if not acct:
        return NOT_DONE, f"Account {order['account']} not found"

    tickers = order["tickers"]
    opt_info = order["option_info"]

    for opt in acct.get("options", []):
        # Match: same ticker, call type, short direction
        if opt.get("ticker") in tickers and opt.get("type") == "call":
            # Check direction — short CCs have negative contracts
            contracts = str(opt.get("contracts", ""))
            if contracts.startswith("-") or opt.get("direction") == "short":
                # Found a matching short call
                if opt_info and opt_info.get("strike"):
                    if abs(opt.get("strike", 0) - opt_info["strike"]) < 1:
                        return DONE, f"Found {opt['raw']} in {order['account']}"
                    else:
                        return PARTIAL, f"CC found but different strike: {opt.get('strike')} vs planned {opt_info['strike']}"
                return DONE, f"Found CC on {tickers[0]} in {order['account']}"

    # Check if the "NO ACTIVE OPTIONS" note exists
    if "NO ACTIVE OPTIONS" in acct.get("raw", ""):
        return NOT_DONE, "No active options in account"

    return NOT_DONE, f"No matching CC found in {order['account']}"


def check_sell_csp(order: dict, acct: dict | None, accounts: dict) -> tuple[str, str]:
    """Check if a CSP was sold — look for matching active put in account."""
    if not acct:
        return NOT_DONE, f"Account {order['account']} not found"

    tickers = order["tickers"]
    opt_info = order["option_info"]

    for opt in acct.get("options", []):
        if opt.get("ticker") in tickers and opt.get("type") == "put":
            contracts = str(opt.get("contracts", ""))
            if contracts.startswith("-") or opt.get("direction") == "short":
                if opt_info and opt_info.get("strike"):
                    if abs(opt.get("strike", 0) - opt_info["strike"]) < 1:
                        return DONE, f"Found {opt['raw']} in {order['account']}"
                return DONE, f"Found CSP on {tickers[0]} in {order['account']}"

    return NOT_DONE, f"No matching CSP found in {order['account']}"


def check_buy_leap(order: dict, acct: dict | None, accounts: dict) -> tuple[str, str]:
    """Check if a LEAP was purchased — look for matching long call in account."""
    if not acct:
        return NOT_DONE, f"Account {order['account']} not found"

    tickers = order["tickers"]
    opt_info = order["option_info"]

    for opt in acct.get("options", []):
        if opt.get("ticker") in tickers and opt.get("direction") == "long":
            if opt_info and opt_info.get("strike"):
                if abs(opt.get("strike", 0) - opt_info["strike"]) < 1:
                    return DONE, f"Found {opt['raw']} in {order['account']}"
            # Check if this is an existing LEAP vs a newly purchased one
            # We can't perfectly distinguish, but if it exists, it's likely done
            if opt.get("type") == (opt_info or {}).get("type", "call"):
                return DONE, f"Found matching LEAP in {order['account']}"

    return NOT_DONE, f"No matching LEAP found in {order['account']}"


def check_close_option(order: dict, acct: dict | None, accounts: dict) -> tuple[str, str]:
    """Check if an option was closed — it should NOT be in the account anymore."""
    if not acct:
        return UNVERIFIABLE, f"Account {order['account']} not found"

    tickers = order["tickers"]
    opt_info = order["option_info"]

    for opt in acct.get("options", []):
        if opt.get("ticker") in tickers:
            if opt_info and opt_info.get("strike"):
                if abs(opt.get("strike", 0) - opt_info["strike"]) < 1:
                    return NOT_DONE, f"Option still active: {opt['raw']}"
            else:
                return NOT_DONE, f"Option still active: {opt['raw']}"

    # Check "Closed since last update" section
    if tickers:
        for ticker in tickers:
            if f"{ticker}" in acct.get("raw", "") and "closed" in acct.get("raw", "").lower():
                # Found mention of ticker in closed section
                pass
    return DONE, "Option no longer in active positions"


def check_let_expire(order: dict, acct: dict | None, accounts: dict) -> tuple[str, str]:
    """Check if an option was let to expire — it should NOT be active."""
    if not acct:
        return UNVERIFIABLE, f"Account {order['account']} not found"

    tickers = order["tickers"]
    opt_info = order["option_info"]

    for opt in acct.get("options", []):
        if opt.get("ticker") in tickers:
            if opt_info and opt_info.get("strike"):
                if abs(opt.get("strike", 0) - opt_info["strike"]) < 1:
                    return NOT_DONE, f"Option still active: {opt['raw']}"

    return DONE, "Option no longer in active positions (expired or closed)"


def check_start_dca(order: dict, acct: dict | None, accounts: dict) -> tuple[str, str]:
    """Check if DCA was started — look in constraints or positions."""
    if not acct:
        return UNVERIFIABLE, f"Account {order['account']} not found"

    tickers = order["tickers"]
    constraints = acct.get("constraints", "").lower()
    raw = acct.get("raw", "")

    # Check if "Active DCA" mention exists in constraints or body
    for ticker in tickers:
        # Check if ticker appears in a DCA context
        if re.search(rf"(?:active\s+)?dca.*{ticker}", raw, re.IGNORECASE):
            return DONE, f"DCA reference found for {ticker}"
        if re.search(rf"{ticker}.*\$\d+/day", raw, re.IGNORECASE):
            return DONE, f"DCA rate found for {ticker}"
        # Check if ticker exists in positions (sign of DCA starting)
        if ticker in acct.get("positions", {}):
            shares = acct["positions"][ticker].get("shares", 0)
            if shares > 0:
                return PARTIAL, f"{ticker} held ({shares} shares) — DCA may be active but can't confirm rate"

    return UNVERIFIABLE, "Can't verify DCA setup from account file alone"


def check_modify_dca(order: dict, acct: dict | None, accounts: dict) -> tuple[str, str]:
    """Check if DCA was modified — mostly unverifiable."""
    return UNVERIFIABLE, "DCA rate changes can't be verified from account snapshots"


def check_sell_shares(order: dict, acct: dict | None, accounts: dict) -> tuple[str, str]:
    """Check if shares were sold — ticker should have fewer shares or be gone."""
    if not acct:
        return UNVERIFIABLE, f"Account {order['account']} not found"

    tickers = order["tickers"]

    # Try to extract target share count from order text
    order_text = f"{order['order']} {order['detail']}"
    sell_qty_match = re.search(r"(\d+)\s+(?:of\s+\d+\s+)?shares?", order_text, re.IGNORECASE)
    sell_qty = int(sell_qty_match.group(1)) if sell_qty_match else None

    for ticker in tickers:
        pos = acct.get("positions", {}).get(ticker)
        if not pos:
            # Ticker not in account — it was fully sold
            return DONE, f"{ticker} no longer in {order['account']}"

        shares = pos.get("shares", 0)
        shares_str = f"{shares:g}"

        # If we know the expected sell quantity, check if shares decreased
        # We can look for "N of M shares" pattern to see if the original was M
        orig_match = re.search(r"(\d+)\s+of\s+(\d+)\s+shares?", order_text, re.IGNORECASE)
        if orig_match:
            expected_remaining = int(orig_match.group(2)) - int(orig_match.group(1))
            if shares <= expected_remaining:
                return DONE, f"{ticker} reduced to {shares_str} shares (expected {expected_remaining})"
            elif shares < int(orig_match.group(2)):
                sold = int(orig_match.group(2)) - int(shares)
                return PARTIAL, f"{ticker} partially sold: {sold} of {orig_match.group(1)} shares"
            else:
                return NOT_DONE, f"{ticker} still {shares_str} shares (expected to sell {orig_match.group(1)})"

        # Generic case: still there, likely not done
        return NOT_DONE, f"{ticker} still held: {shares_str} shares in {order['account']}"

    return UNVERIFIABLE, "Could not determine sell status"


def check_buy_shares(order: dict, acct: dict | None, accounts: dict) -> tuple[str, str]:
    """Check if shares were bought — ticker should appear in account."""
    if not acct:
        return UNVERIFIABLE, f"Account {order['account']} not found"

    tickers = order["tickers"]
    order_text = f"{order['order']} {order['detail']}"

    # For limit orders ("Place X limit buys"), we check if the ticker is held
    # and whether the share count suggests fills
    is_limit_order = "limit" in order_text.lower() or "gtc" in order_text.lower()

    # Try to extract expected buy quantity
    buy_qty_match = re.search(r"(\d+)\s+shares?\s+@", order_text, re.IGNORECASE)
    if not buy_qty_match:
        # "2 shares @ $1,145 / 2 @ $1,108 ..." — sum all quantities
        qty_matches = re.findall(r"(\d+)\s+(?:shares?\s+)?@\s*\$", order_text)
        expected_qty = sum(int(q) for q in qty_matches) if qty_matches else None
    else:
        expected_qty = int(buy_qty_match.group(1))

    for ticker in tickers:
        pos = acct.get("positions", {}).get(ticker)
        if pos and pos.get("shares", 0) > 0:
            shares = pos["shares"]
            shares_str = f"{shares:g}"
            if expected_qty and is_limit_order:
                # For limit orders, having the same small position as before = not filled
                if shares <= 1 and expected_qty > 1:
                    return NOT_DONE, f"{ticker} still only {shares_str} share(s) in {order['account']}"
                return PARTIAL, f"{ticker} has {shares_str} shares — can't confirm if limit fills added"
            return PARTIAL, f"{ticker} held ({shares_str} shares) — can't verify if new buys filled"
        elif pos:
            return PARTIAL, f"{ticker} in account but shares unclear"

    # Ticker not found in account at all
    if tickers:
        primary = tickers[0]
        return NOT_DONE, f"{primary} not found in {order['account']}"

    return UNVERIFIABLE, "Could not determine buy status"


# ---------------------------------------------------------------------------
# Carry-forward detection
# ---------------------------------------------------------------------------

def normalize_for_comparison(text: str) -> str:
    """Normalize order text for carry-forward comparison."""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"~~(.*?)~~", r"\1", text)
    text = re.sub(r"\$\d+[CP]\s+\w+\s+\d+", "", text)  # Remove specific strikes/dates
    text = re.sub(r"\d+x\b", "", text)                   # Remove contract counts
    text = re.sub(r"\$[\d,.]+", "", text)                 # Remove dollar amounts
    text = re.sub(r"#\d+", "", text)                      # Remove carry-forward counts
    text = re.sub(r"CARRY.?FORWARD", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def find_matching_order(order: dict, other_orders: list[dict]) -> dict | None:
    """Find a matching order in another plan's order list.

    Requires both ticker overlap AND same order class for a match.
    Fuzzy text matching is only used as a fallback when tickers can't be extracted.
    """
    order_tickers = set(order["tickers"])

    for other in other_orders:
        if other["deferred"]:
            continue
        other_tickers = set(other["tickers"])

        # Primary match: same ticker(s) + same order class
        if order_tickers and other_tickers:
            if order_tickers & other_tickers and order["order_class"] == other["order_class"]:
                return other

    # Fallback: fuzzy text match only if we have no tickers
    if not order_tickers:
        norm_order = normalize_for_comparison(order["order"])
        for other in other_orders:
            if other["deferred"]:
                continue
            norm_other = normalize_for_comparison(other["order"])
            if norm_order and norm_other:
                words1 = set(norm_order.split())
                words2 = set(norm_other.split())
                common = words1 & words2
                if len(common) >= 3 and len(common) / max(len(words1), len(words2)) > 0.5:
                    return other

    return None


def extract_carry_forward_count(text: str) -> int:
    """Extract existing carry-forward count from order text."""
    # Look for "CARRY-FORWARD #N" or "carry-forward #N"
    m = re.search(r"CARRY[- ]?FORWARD\s*#(\d+)", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    # Look for "Nth consecutive plan"
    m2 = re.search(r"(\d+)(?:st|nd|rd|th)\s+(?:consecutive\s+)?plan", text, re.IGNORECASE)
    if m2:
        return int(m2.group(1))
    # Look for "N weeks" patterns
    m3 = re.search(r"(\d+)\+?\s+weeks?\s+(?:uncovered|overdue)", text, re.IGNORECASE)
    if m3:
        # Approximate: each plan is ~1 week, so N weeks overdue ≈ N carry-forwards
        weeks = int(m3.group(1))
        return max(1, weeks // 2)  # rough approximation
    return 0


def detect_carry_forwards(current_orders: list[dict], prior_orders: list[dict],
                          all_plans: list[tuple[str, list[dict]]]) -> dict[int, dict]:
    """Detect carry-forward orders and their count.

    Returns {order_index: {"count": N, "first_seen": plan_date}}.
    """
    carry_forwards = {}

    for i, order in enumerate(current_orders):
        if order["deferred"]:
            continue

        # First check if the current plan already labels it as carry-forward
        existing_count = extract_carry_forward_count(
            f"{order['raw']} {order.get('rationale', '')}"
        )

        if existing_count > 0:
            carry_forwards[i] = {
                "count": existing_count,
                "source": "labeled in plan",
            }
            continue

        # Check against prior plan
        if prior_orders:
            match = find_matching_order(order, prior_orders)
            if match:
                # Found in prior plan — this is a carry-forward
                prior_count = extract_carry_forward_count(
                    f"{match['raw']} {match.get('rationale', '')}"
                )
                carry_forwards[i] = {
                    "count": prior_count + 1 if prior_count else 2,
                    "source": "appeared in prior plan",
                }
                continue

        # Check across all available historical plans
        appearances = 0
        for plan_date, plan_orders in all_plans:
            match = find_matching_order(order, plan_orders)
            if match:
                appearances += 1

        if appearances > 1:  # appeared in multiple plans
            carry_forwards[i] = {
                "count": appearances,
                "source": f"appeared in {appearances} plans",
            }

    return carry_forwards


# ---------------------------------------------------------------------------
# Plan parsing
# ---------------------------------------------------------------------------

def parse_plan_orders(plan_path: Path) -> list[dict]:
    """Parse all one-time orders from a plan file."""
    text = plan_path.read_text()
    table_text = extract_one_time_orders_table(text)
    if not table_text:
        return []

    rows = parse_markdown_table(table_text)
    orders = []
    for row in rows:
        order = parse_order(row)
        if order:
            orders.append(order)
    return orders


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_status(status: str, carry_info: dict | None = None) -> str:
    """Format a status with emoji."""
    emoji = STATUS_EMOJI.get(status, "?")
    return f"{emoji} {status}"


def format_carry_tag(carry_info: dict | None) -> str:
    """Format carry-forward tag."""
    if not carry_info:
        return ""
    count = carry_info["count"]
    tag = f"\U0001f504 CF#{count}"
    if count >= 4:
        tag += " CHRONIC"
    return tag


def truncate(text: str, max_len: int = 32) -> str:
    """Truncate text to max_len, adding ... if needed."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def print_terminal_report(plan_name: str, plan_date: str, orders: list[dict],
                          results: list[tuple[str, str]],
                          carry_forwards: dict[int, dict]):
    """Print the execution tracker report to terminal."""
    width = 80
    print()
    print("=" * width)
    print(f"  EXECUTION TRACKER \u2014 {plan_name} vs Accounts ({plan_date})")
    print("=" * width)
    print()

    total = 0
    done_count = 0
    deferred_count = 0
    unverifiable_count = 0
    partial_count = 0
    not_done_count = 0
    carry_items = []

    for i, (order, (status, notes)) in enumerate(zip(orders, results)):
        total += 1
        cf = carry_forwards.get(i)

        if status == DEFERRED:
            deferred_count += 1
        elif status == UNVERIFIABLE:
            unverifiable_count += 1
        elif status == DONE:
            done_count += 1
        elif status == PARTIAL:
            partial_count += 1
        else:  # NOT_DONE
            not_done_count += 1

        if cf:
            carry_items.append((order, cf))

        # Format the line
        num = order["num"] or str(i + 1)
        order_text = truncate(order["order"], 34)
        status_text = format_status(status)
        carry_tag = format_carry_tag(cf)

        # Build status + carry tag
        full_status = status_text
        if carry_tag:
            full_status += f"  {carry_tag}"

        print(f"  {num:<3} {order_text:<36} {full_status}")
        if notes:
            print(f"      {truncate(notes, 70)}")

    print()

    # Execution rate — partials count as 0.5
    scoreable = total - deferred_count - unverifiable_count
    effective_done = done_count + (partial_count * 0.5)

    if scoreable > 0:
        rate = effective_done / scoreable
        done_display = f"{effective_done:g}" if effective_done != int(effective_done) else f"{int(effective_done)}"
        rate_str = f"{done_display}/{scoreable} = {rate:.0%}"
    else:
        rate_str = "N/A (all deferred or unverifiable)"

    print(f"  EXECUTION RATE: {rate_str}", end="")
    exclusions = []
    if deferred_count:
        exclusions.append(f"{deferred_count} deferred")
    if unverifiable_count:
        exclusions.append(f"{unverifiable_count} unverifiable")
    if exclusions:
        print(f" (excluding {', '.join(exclusions)})")
    else:
        print()

    # Carry-forwards
    if carry_items:
        print()
        print("  CARRY-FORWARDS (appeared in prior plan too):")
        for order, cf in carry_items:
            count = cf["count"]
            chronic = " CHRONIC." if count >= 4 else ""
            ticker_str = ", ".join(order["tickers"][:2]) if order["tickers"] else truncate(order["order"], 25)
            print(f"    - {ticker_str}: #{count} consecutive.{chronic}")

    print()
    print("=" * width)
    print()


def build_json_report(plan_name: str, plan_date: str, orders: list[dict],
                      results: list[tuple[str, str]],
                      carry_forwards: dict[int, dict]) -> dict:
    """Build JSON report."""
    items = []
    total = 0
    done_count = 0
    deferred_count = 0
    unverifiable_count = 0
    partial_count = 0

    for i, (order, (status, notes)) in enumerate(zip(orders, results)):
        total += 1
        cf = carry_forwards.get(i)

        if status == DEFERRED:
            deferred_count += 1
        elif status == UNVERIFIABLE:
            unverifiable_count += 1
        elif status == DONE:
            done_count += 1
        elif status == PARTIAL:
            partial_count += 1

        item = {
            "num": order["num"],
            "order": order["order"],
            "account": order["account"],
            "order_class": order["order_class"],
            "tickers": order["tickers"],
            "status": status,
            "notes": notes,
            "deferred": order["deferred"],
        }
        if cf:
            item["carry_forward"] = {
                "count": cf["count"],
                "chronic": cf["count"] >= 4,
            }
        items.append(item)

    scoreable = total - deferred_count - unverifiable_count
    effective_done = done_count + (partial_count * 0.5)
    rate = effective_done / scoreable if scoreable > 0 else None
    done_display = f"{effective_done:g}" if rate is not None else "N/A"

    return {
        "plan": plan_name,
        "plan_date": plan_date,
        "orders": items,
        "summary": {
            "total": total,
            "done": done_count,
            "partial": partial_count,
            "not_done": total - done_count - deferred_count - unverifiable_count - partial_count,
            "deferred": deferred_count,
            "unverifiable": unverifiable_count,
            "execution_rate": round(rate, 3) if rate is not None else None,
            "execution_rate_display": f"{done_display}/{scoreable}" if scoreable > 0 else "N/A",
        },
        "carry_forwards": [
            {
                "order": orders[i]["order"],
                "tickers": orders[i]["tickers"],
                "count": cf["count"],
                "chronic": cf["count"] >= 4,
            }
            for i, cf in carry_forwards.items()
        ],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Compare a trading plan's orders against current account state."
    )
    parser.add_argument(
        "--plan", type=str, default=None,
        help="Specific plan file (e.g., PLAN-2026-09-06.md). Default: latest."
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON."
    )
    args = parser.parse_args()

    # Find plan files
    plan_files = get_plan_files()
    if not plan_files:
        print("Error: No PLAN-*.md files found in portfolio/plans/", file=sys.stderr)
        sys.exit(1)

    # Select target plan
    if args.plan:
        plan_name = args.plan
        # Handle both "PLAN-2026-09-06.md" and "PLAN-2026-09-06"
        if not plan_name.endswith(".md"):
            plan_name += ".md"
        target_plan = PLANS_DIR / plan_name
        if not target_plan.exists():
            print(f"Error: {target_plan} not found.", file=sys.stderr)
            sys.exit(1)
    else:
        target_plan = plan_files[-1]  # latest

    plan_date = parse_plan_date(target_plan)

    # Load accounts
    accounts = load_accounts()
    if not accounts:
        print("Error: No account files found in portfolio/accounts/", file=sys.stderr)
        sys.exit(1)

    # Parse current plan orders
    current_orders = parse_plan_orders(target_plan)
    if not current_orders:
        print(f"No orders found in {target_plan.name}.", file=sys.stderr)
        sys.exit(1)

    # Parse prior plan orders (for carry-forward detection)
    prior_orders = []
    target_idx = None
    for idx, pf in enumerate(plan_files):
        if pf.name == target_plan.name:
            target_idx = idx
            break
    if target_idx is not None and target_idx > 0:
        prior_plan = plan_files[target_idx - 1]
        prior_orders = parse_plan_orders(prior_plan)

    # Parse all historical plans for deeper carry-forward detection
    all_plans = []
    for pf in plan_files:
        if pf.name == target_plan.name:
            continue
        pdate = parse_plan_date(pf)
        porders = parse_plan_orders(pf)
        if porders:
            all_plans.append((pdate, porders))

    # Check execution of each order
    results = []
    for order in current_orders:
        status, notes = check_order_execution(order, accounts)
        results.append((status, notes))

    # Detect carry-forwards
    carry_forwards = detect_carry_forwards(current_orders, prior_orders, all_plans)

    # Override status for carry-forward items that are NOT_DONE
    for i, cf in carry_forwards.items():
        status, notes = results[i]
        if status == NOT_DONE:
            cf_note = f"\U0001f504 CARRY-FORWARD #{cf['count']}"
            if cf['count'] >= 4:
                cf_note += " CHRONIC"
            notes = f"{cf_note}. {notes}" if notes else cf_note
            results[i] = (NOT_DONE, notes)

    # Output
    if args.json:
        report = build_json_report(target_plan.name, plan_date, current_orders,
                                   results, carry_forwards)
        print(json.dumps(report, indent=2))
    else:
        print_terminal_report(target_plan.name, plan_date, current_orders,
                              results, carry_forwards)


if __name__ == "__main__":
    main()
