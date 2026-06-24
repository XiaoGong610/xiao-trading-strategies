#!/usr/bin/env python3
"""Macro data dashboard — FRED economic data + Polymarket predictions.

FRED requires a free API key: https://fred.stlouisfed.org/docs/api/api_key.html
Set FRED_API_KEY env var. Without it, FRED data is skipped.

Polymarket requires no API key.

Adapted from TauricResearch/TradingAgents (MIT license).

Usage:
  .venv/bin/python3 scripts/macro.py                    # full dashboard (terminal)
  .venv/bin/python3 scripts/macro.py --json              # JSON output
  .venv/bin/python3 scripts/macro.py --fred              # FRED only
  .venv/bin/python3 scripts/macro.py --polymarket        # Polymarket only
  .venv/bin/python3 scripts/macro.py --polymarket "Fed rate cut"  # specific topic
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone

import requests

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

FRED_API_BASE = "https://api.stlouisfed.org/fred"
GAMMA_BASE = "https://gamma-api.polymarket.com"
TIMEOUT = 30

# --- FRED ---

MACRO_SERIES = {
    "fed_funds_rate": "FEDFUNDS",
    "10y_treasury": "DGS10",
    "2y_treasury": "DGS2",
    "yield_curve": "T10Y2Y",
    "cpi": "CPIAUCSL",
    "core_pce": "PCEPILFE",
    "unemployment": "UNRATE",
    "initial_claims": "ICSA",
    "m2": "M2SL",
    "vix": "VIXCLS",
    "consumer_sentiment": "UMCSENT",
    "inflation_expectations": "T10YIE",
}

# The dashboard series — most important macro indicators
DASHBOARD_SERIES = [
    "fed_funds_rate", "10y_treasury", "2y_treasury", "yield_curve",
    "cpi", "core_pce", "unemployment", "vix",
]


def fred_fetch(series_id: str, api_key: str, lookback_days: int = 365) -> dict | None:
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    try:
        # Get metadata
        meta_resp = requests.get(
            f"{FRED_API_BASE}/series",
            params={"series_id": series_id, "api_key": api_key, "file_type": "json"},
            timeout=TIMEOUT,
        )
        meta_resp.raise_for_status()
        meta = meta_resp.json().get("seriess", [{}])[0]

        # Get observations
        obs_resp = requests.get(
            f"{FRED_API_BASE}/series/observations",
            params={
                "series_id": series_id, "api_key": api_key, "file_type": "json",
                "observation_start": start_date, "observation_end": end_date,
                "sort_order": "desc",
            },
            timeout=TIMEOUT,
        )
        obs_resp.raise_for_status()
        observations = obs_resp.json().get("observations", [])

        # Get latest non-missing value
        points = [(o["date"], o["value"]) for o in observations if o.get("value") not in (".", None, "")]
        if not points:
            return None

        latest_date, latest_val = points[0]
        # Get value from ~1 year ago for change calculation
        oldest_date, oldest_val = points[-1] if len(points) > 1 else (latest_date, latest_val)

        try:
            change = float(latest_val) - float(oldest_val)
            base = float(oldest_val)
            change_pct = (change / base * 100) if base != 0 else 0
        except ValueError:
            change = 0
            change_pct = 0

        return {
            "series_id": series_id,
            "title": meta.get("title", series_id),
            "units": meta.get("units_short", ""),
            "frequency": meta.get("frequency", ""),
            "latest_value": latest_val,
            "latest_date": latest_date,
            "change_1y": round(change, 4),
            "change_1y_pct": round(change_pct, 2),
        }
    except Exception as exc:
        logger.warning("FRED fetch failed for %s: %s", series_id, exc)
        return None


def fetch_fred_dashboard(api_key: str) -> list[dict]:
    results = []
    for alias in DASHBOARD_SERIES:
        series_id = MACRO_SERIES[alias]
        data = fred_fetch(series_id, api_key)
        if data:
            data["alias"] = alias
            results.append(data)
    return results


# --- Polymarket ---

DEFAULT_TOPICS = ["Federal Reserve rate", "US recession", "inflation", "tariff"]


def fetch_polymarket(topic: str, limit: int = 4) -> dict:
    try:
        resp = requests.get(
            f"{GAMMA_BASE}/public-search",
            params={"q": topic, "limit_per_type": 20},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("Polymarket fetch failed for %r: %s", topic, exc)
        return {"topic": topic, "available": False, "error": str(exc)}

    now = datetime.now(timezone.utc)
    markets = []
    for event in data.get("events", []):
        for m in event.get("markets", []):
            if m.get("closed"):
                continue
            # Parse outcome prices
            try:
                prices = json.loads(m["outcomePrices"]) if isinstance(m.get("outcomePrices"), str) else m.get("outcomePrices", [])
                outcomes = json.loads(m["outcomes"]) if isinstance(m.get("outcomes"), str) else m.get("outcomes", [])
            except (json.JSONDecodeError, TypeError):
                continue
            if not prices or not outcomes:
                continue
            try:
                prob = float(prices[0])
            except (ValueError, IndexError):
                continue

            volume = m.get("volumeNum") or 0
            end_date = (m.get("endDate") or "")[:10]
            wk_change = m.get("oneWeekPriceChange")

            markets.append({
                "question": m.get("question", ""),
                "outcome": outcomes[0],
                "probability": round(prob * 100, 1),
                "volume": volume,
                "end_date": end_date,
                "week_change_pp": round(wk_change * 100, 1) if isinstance(wk_change, (int, float)) and wk_change else None,
            })

    markets.sort(key=lambda x: x["volume"], reverse=True)
    return {
        "topic": topic,
        "available": len(markets) > 0,
        "markets": markets[:limit],
    }


# --- Output ---

def to_terminal(fred_data: list[dict], poly_data: list[dict]) -> str:
    lines = ["=" * 70, "  MACRO DASHBOARD", "=" * 70, ""]

    if fred_data:
        lines.append("  FRED ECONOMIC DATA")
        lines.append("  " + "-" * 66)
        lines.append(f"  {'Indicator':<30} {'Latest':>10} {'Date':>12} {'1Y Δ':>10}")
        lines.append("  " + "-" * 66)
        for d in fred_data:
            alias = d.get("alias", d["series_id"])
            val = d["latest_value"]
            date = d["latest_date"]
            change = d["change_1y"]
            sign = "+" if change >= 0 else ""
            lines.append(f"  {alias:<30} {val:>10} {date:>12} {sign}{change:>9}")
        lines.append("")

    if poly_data:
        lines.append("  POLYMARKET PREDICTIONS")
        lines.append("  " + "-" * 66)
        for topic_data in poly_data:
            if not topic_data.get("available"):
                continue
            lines.append(f"  Topic: {topic_data['topic']}")
            for m in topic_data.get("markets", []):
                wk = f" ({m['week_change_pp']:+.1f}pp 1W)" if m.get("week_change_pp") else ""
                lines.append(f"    {m['probability']:>5.1f}%  {m['question'][:55]}{wk}")
            lines.append("")

    lines.extend(["=" * 70, ""])
    return "\n".join(lines)


def to_json(fred_data: list[dict], poly_data: list[dict]) -> str:
    return json.dumps({
        "timestamp": datetime.now().isoformat(),
        "fred": fred_data,
        "polymarket": poly_data,
    }, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Macro data dashboard (FRED + Polymarket)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--fred", action="store_true", help="FRED only")
    parser.add_argument("--polymarket", nargs="?", const="__default__", help="Polymarket only (optional topic)")
    args = parser.parse_args()

    both = not args.fred and args.polymarket is None

    fred_data = []
    poly_data = []

    if both or args.fred:
        api_key = os.getenv("FRED_API_KEY")
        if api_key:
            fred_data = fetch_fred_dashboard(api_key)
        else:
            print("⚠️  FRED_API_KEY not set — skipping FRED data. Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html", file=sys.stderr)

    if both or args.polymarket is not None:
        if args.polymarket and args.polymarket != "__default__":
            topics = [args.polymarket]
        else:
            topics = DEFAULT_TOPICS
        for topic in topics:
            poly_data.append(fetch_polymarket(topic))

    if args.json:
        print(to_json(fred_data, poly_data))
    else:
        print(to_terminal(fred_data, poly_data))


if __name__ == "__main__":
    main()
